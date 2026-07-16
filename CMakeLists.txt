# CMake build for the cyhighs Cython extension.
#
# HiGHS + HiPO are always compiled from source (FetchContent) on every platform.
#
# On Linux and Windows, HiPO's BLAS dependency is satisfied by
# libblastrampoline (lbt) rather than by linking OpenBLAS directly: lbt is a
# small MIT-licensed shared library that exports the standard BLAS/LAPACK ABI
# and forwards each call, at runtime, to whichever real BLAS implementation is
# named by the LBT_DEFAULT_LIBS environment variable (this is the same
# mechanism Julia's LinearAlgebra/HiGHS.jl use to switch BLAS backends without
# recompiling). cyhighs's own Python `__init__.py` sets that variable before
# importing the compiled extension:
#
#   * by default, to a prebuilt OpenBLAS bundled inside the wheel (so the
#     package remains fully self contained with zero configuration, matching
#     the project's historical "no external system dependencies" promise);
#   * to Intel MKL instead, if the optional `cyhighs[mkl]` extra is installed
#     and its shared library can be located (Linux x86_64 / Windows x86_64
#     only -- Intel has never published MKL for macOS or for ARM).
#
# On macOS, none of this applies. Reading HiGHS's own cmake/FindHipoDeps.cmake
# shows it unconditionally links Apple's Accelerate framework on Apple
# platforms (in highs_link_blas()), regardless of anything found via
# find_package/find_library, so lbt would have nothing to intercept there.
# cyhighs's macOS wheels use Accelerate directly, the same as before this
# project adopted lbt.
#
# HiGHS's FindHipoDeps.cmake does not call find_library(NAMES openblas)
# directly (also confirmed by reading that file). With no BLAS_LIBRARIES/
# BLA_VENDOR set, it tries find_package(OpenBLAS CONFIG) first (finds nothing,
# since neither lbt nor the bundled OpenBLAS ships a CMake package config),
# then sets BLA_VENDOR=OpenBLAS and calls find_package(BLAS). CMake's own
# FindBLAS.cmake module handles that vendor with an internal
# find_library(NAMES openblas) that does respect CMAKE_LIBRARY_PATH/
# CMAKE_PREFIX_PATH, so this file copies the fetched lbt library into a
# directory prepended to those two variables, under the "openblas" name, so
# that lookup resolves to lbt instead of a real BLAS -- with no upstream
# HiGHS source change needed, just via CMake's own module rather than a
# literal find_library() call in HiGHS's own code.
#
# musllinux (Alpine) wheels are the one exception on Linux: conda-forge only
# ships glibc binaries, so the *default* OpenBLAS backend there comes from
# Alpine's own package (installed via apk in CI, see wheels.yml) instead of
# conda-forge, found via find_library the same way this project found
# OpenBLAS before adopting lbt. lbt itself is still fetched from
# JuliaBinaryWrappers, which does publish musl-tagged assets.
#
# The libblastrampoline release tag/version and the individual asset
# filenames and hashes below are all confirmed against a live release listing
# of JuliaBinaryWrappers/libblastrampoline_jll.jl (as is the MinGW-only
# import library situation handled by cyhighs_generate_msvc_import_lib()).
# The conda-forge OpenBLAS/libgfortran5 coordinates and the Windows/Linux
# package layouts are pinned and confirmed the same way, against real
# repodata.json hashes and real extracted packages.
cmake_minimum_required(VERSION 3.24)

project(cyhighs LANGUAGES C CXX)

# HiGHS is written in C++17. Enforce it here so that our extension agrees with
# the standard the HiGHS libraries were compiled against.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Position independent code is required to link the static HiGHS libraries into
# the shared extension module.
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ---------------------------------------------------------------------------
# Locate Python and the Cython compiler through scikit-build-core.
# ---------------------------------------------------------------------------
find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

# The HiGHS release built from source. Used as the FetchContent git tag
# (v${HIGHS_VERSION}).
set(HIGHS_VERSION 1.15.1)

# The libblastrampoline release fetched as a prebuilt binary. The version,
# the release tag's "+<build>" suffix, and the per-triplet asset hashes below
# are all confirmed real against a live release listing of
# https://github.com/JuliaBinaryWrappers/libblastrampoline_jll.jl
# (tag libblastrampoline-v5.15.0+0).
set(CYHIGHS_LBT_VERSION 5.15.0)
set(CYHIGHS_LBT_BUILD 0)

set(_downloads_dir "${CMAKE_BINARY_DIR}/_cyhighs_downloads")
file(MAKE_DIRECTORY "${_downloads_dir}")

# ---------------------------------------------------------------------------
# Small helper: download (with a pinned hash when we have one) and extract an
# archive exactly once per build directory.
# ---------------------------------------------------------------------------
function(cyhighs_fetch_and_extract url sha256 dest_dir)
  if(EXISTS "${dest_dir}/.cyhighs_extracted")
    return()
  endif()
  get_filename_component(_local_name "${url}" NAME)
  set(_local_path "${_downloads_dir}/${_local_name}")
  if(NOT EXISTS "${_local_path}")
    message(STATUS "Downloading ${url}")
    if(sha256 STREQUAL "")
      message(WARNING "No pinned SHA256 for ${_local_name}; downloading without an integrity check.")
      file(DOWNLOAD "${url}" "${_local_path}" TLS_VERIFY ON STATUS _dl)
    else()
      file(DOWNLOAD "${url}" "${_local_path}" EXPECTED_HASH SHA256=${sha256} TLS_VERIFY ON STATUS _dl)
    endif()
    list(GET _dl 0 _dl_code)
    if(NOT _dl_code EQUAL 0)
      list(GET _dl 1 _dl_msg)
      file(REMOVE "${_local_path}")
      message(FATAL_ERROR "Failed to download ${url}: ${_dl_msg}")
    endif()
  endif()
  file(MAKE_DIRECTORY "${dest_dir}")
  file(ARCHIVE_EXTRACT INPUT "${_local_path}" DESTINATION "${dest_dir}")
  file(WRITE "${dest_dir}/.cyhighs_extracted" "")
endfunction()

# A .conda package is a zip container holding pkg-*.tar.zst (the payload) and
# info-*.tar.zst (metadata, discarded here). This unwraps both layers so
# dest_dir ends up with the normal lib/, bin/, Library/ layout.
function(cyhighs_fetch_conda_package url sha256 dest_dir)
  if(EXISTS "${dest_dir}/.cyhighs_extracted")
    return()
  endif()
  set(_conda_layer "${dest_dir}_conda_layer")
  cyhighs_fetch_and_extract("${url}" "${sha256}" "${_conda_layer}")
  file(GLOB _pkg_tarball "${_conda_layer}/pkg-*.tar.zst")
  if(NOT _pkg_tarball)
    message(FATAL_ERROR "No pkg-*.tar.zst payload found after extracting ${url}")
  endif()
  list(GET _pkg_tarball 0 _pkg_tarball)
  file(MAKE_DIRECTORY "${dest_dir}")
  file(ARCHIVE_EXTRACT INPUT "${_pkg_tarball}" DESTINATION "${dest_dir}")
  file(WRITE "${dest_dir}/.cyhighs_extracted" "")
endfunction()

# Generate an MSVC-compatible import library from a DLL's own export table,
# using dumpbin + lib.exe (both ship with MSVC). Needed on Windows because
# BinaryBuilder cross-compiles JLL artifacts with MinGW, which produces a
# *.dll.a import library that MSVC cannot consume directly. This step is
# unverified: it has not been exercised on a real Windows toolchain.
function(cyhighs_generate_msvc_import_lib dll_path def_path out_lib_path)
  find_program(_dumpbin dumpbin)
  find_program(_implib lib)
  if(NOT _dumpbin OR NOT _implib)
    message(FATAL_ERROR
      "dumpbin/lib.exe not found; cannot generate an MSVC import library for "
      "${dll_path}. Build from an MSVC developer command prompt.")
  endif()
  execute_process(COMMAND "${_dumpbin}" /exports "${dll_path}" OUTPUT_VARIABLE _exports_output)
  get_filename_component(_dll_name "${dll_path}" NAME)
  file(WRITE "${def_path}" "LIBRARY ${_dll_name}\nEXPORTS\n")
  string(REGEX MATCHALL "[ \t]+[0-9]+[ \t]+[0-9A-Fa-f]+[ \t]+[0-9A-Fa-f]+[ \t]+([A-Za-z_][A-Za-z0-9_@]*)"
    _export_lines "${_exports_output}")
  foreach(_line IN LISTS _export_lines)
    string(REGEX REPLACE ".*[ \t]([A-Za-z_][A-Za-z0-9_@]*)$" "\\1" _symbol "${_line}")
    file(APPEND "${def_path}" "${_symbol}\n")
  endforeach()
  execute_process(COMMAND "${_implib}" "/def:${def_path}" "/out:${out_lib_path}" /machine:x64)
endfunction()

# ---------------------------------------------------------------------------
# Work out which platform/arch we are building for. Reused below for both the
# lbt asset name and the conda-forge subdir.
# ---------------------------------------------------------------------------
string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" _raw_arch)
if(_raw_arch MATCHES "amd64|x86_64|x64")
  set(_arch "x86_64")
elseif(_raw_arch MATCHES "aarch64|arm64")
  set(_arch "aarch64")
else()
  message(FATAL_ERROR "Unsupported CPU architecture for cyhighs: ${CMAKE_SYSTEM_PROCESSOR}")
endif()

if(APPLE)
  if(_arch STREQUAL "aarch64")
    set(_conda_subdir "osx-arm64")
    set(_lbt_triplet "aarch64-apple-darwin")
  else()
    set(_conda_subdir "osx-64")
    set(_lbt_triplet "x86_64-apple-darwin")
  endif()
elseif(WIN32)
  if(NOT _arch STREQUAL "x86_64")
    message(FATAL_ERROR "cyhighs only supports Windows x86_64.")
  endif()
  set(_conda_subdir "win-64")
  set(_lbt_triplet "x86_64-w64-mingw32")
elseif(UNIX)
  # conda-forge only ships glibc binaries, so musllinux (Alpine) wheels can't
  # use the conda-forge OpenBLAS fetch below and need their own musl-tagged
  # lbt asset. Ask the compiler which libc it targets rather than assuming
  # any particular container, matching the actual triplet suffixes
  # JuliaBinaryWrappers publishes (e.g. x86_64-linux-musl).
  execute_process(
    COMMAND "${CMAKE_C_COMPILER}" -dumpmachine
    OUTPUT_VARIABLE _target_triple
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET)
  set(_libc "gnu")
  if(_target_triple MATCHES "musl")
    set(_libc "musl")
  endif()

  if(_arch STREQUAL "aarch64")
    set(_conda_subdir "linux-aarch64")
    set(_lbt_triplet "aarch64-linux-${_libc}")
  else()
    set(_conda_subdir "linux-64")
    set(_lbt_triplet "x86_64-linux-${_libc}")
  endif()
else()
  message(FATAL_ERROR "Unsupported platform for cyhighs: ${CMAKE_SYSTEM_NAME}/${_arch}")
endif()

# ---------------------------------------------------------------------------
# BLAS/LAPACK for HiPO. Skipped entirely on macOS: reading HiGHS's own
# cmake/FindHipoDeps.cmake shows highs_link_blas() unconditionally links
# Apple's Accelerate framework on Apple platforms, regardless of anything
# found via find_package/find_library, so there is nothing here for lbt to
# intercept. cyhighs's macOS wheels use Accelerate directly, the same as
# before this project adopted lbt.
# ---------------------------------------------------------------------------
set(_bundled_backend_libs "")
if(NOT APPLE)
  # Fetch libblastrampoline (lbt): the BLAS/LAPACK ABI HiPO links against.
  # HiGHS's FindHipoDeps.cmake does not call find_library(NAMES openblas)
  # directly (confirmed by reading that file). With BLAS_LIBRARIES/BLA_VENDOR
  # unset, it tries find_package(OpenBLAS CONFIG) first (finds nothing here,
  # since neither lbt nor the bundled OpenBLAS ships a CMake package config),
  # then sets BLA_VENDOR=OpenBLAS and calls find_package(BLAS). CMake's own
  # FindBLAS.cmake module handles that vendor with an internal
  # find_library(NAMES openblas) that does respect
  # CMAKE_LIBRARY_PATH/CMAKE_PREFIX_PATH, so staging lbt under the "openblas"
  # name in a directory prepended to those two variables (below) still works,
  # just through CMake's own module rather than a literal find_library() call
  # in HiGHS's own code as originally assumed.
  set(_lbt_hash "")
  if(_lbt_triplet STREQUAL "aarch64-linux-gnu")
    set(_lbt_hash 9cca820658a7206b3324bf4fb309154bf2427c81ebd0f6a448a761183a553cdb)
  elseif(_lbt_triplet STREQUAL "aarch64-linux-musl")
    set(_lbt_hash a50cd8b2cf54df66c324480e66a563d0a756173914f0399d6b17bd1f627def28)
  elseif(_lbt_triplet STREQUAL "x86_64-linux-gnu")
    set(_lbt_hash 76ddd4223122d9664f827fc940f7696bb4225cfd1cf6bb00b3acbeb524bcc609)
  elseif(_lbt_triplet STREQUAL "x86_64-linux-musl")
    set(_lbt_hash 759c0699e8675b1ca13d3f574dfab339f62825cae168a525549b669535207c92)
  elseif(_lbt_triplet STREQUAL "x86_64-w64-mingw32")
    set(_lbt_hash 4d301c454f1259d50db44a2a0af83cb441d3cbc790963c375ed27686d884624f)
  endif()
  set(_lbt_asset "libblastrampoline.v${CYHIGHS_LBT_VERSION}.${_lbt_triplet}.tar.gz")
  set(_lbt_url
    "https://github.com/JuliaBinaryWrappers/libblastrampoline_jll.jl/releases/download/libblastrampoline-v${CYHIGHS_LBT_VERSION}+${CYHIGHS_LBT_BUILD}/${_lbt_asset}")
  set(_lbt_root "${CMAKE_BINARY_DIR}/lbt-prebuilt")
  cyhighs_fetch_and_extract("${_lbt_url}" "${_lbt_hash}" "${_lbt_root}")

  if(WIN32)
    file(GLOB _lbt_dll "${_lbt_root}/bin/libblastrampoline*.dll")
  else()
    file(GLOB _lbt_shared "${_lbt_root}/lib/libblastrampoline.*")
  endif()

  # The directory the find_package(BLAS)/BLA_VENDOR=OpenBLAS lookup above is
  # pointed at, via CMAKE_LIBRARY_PATH/CMAKE_PREFIX_PATH (prepended below). A
  # copy of lbt lives here under the "openblas" name so that lookup resolves
  # to lbt instead of a real BLAS, with no upstream HiGHS source change.
  set(_blas_shim_dir "${CMAKE_BINARY_DIR}/blas-shim")
  file(MAKE_DIRECTORY "${_blas_shim_dir}")

  if(WIN32)
    if(NOT _lbt_dll)
      message(FATAL_ERROR "No libblastrampoline DLL found in ${_lbt_root}/bin")
    endif()
    list(GET _lbt_dll 0 _lbt_dll)
    file(COPY_FILE "${_lbt_dll}" "${_blas_shim_dir}/blastrampoline.dll")
    # CMake's FindBLAS.cmake looks for an import library (openblas.lib) on
    # Windows, not the DLL itself. The JLL release only ships a MinGW-style
    # *.dll.a import library (confirmed by extracting the real archive),
    # which MSVC cannot consume directly, so generate a fresh one.
    cyhighs_generate_msvc_import_lib(
      "${_blas_shim_dir}/blastrampoline.dll"
      "${_blas_shim_dir}/openblas.def"
      "${_blas_shim_dir}/openblas.lib")
  else()
    if(NOT _lbt_shared)
      message(FATAL_ERROR "No libblastrampoline shared library found in ${_lbt_root}/lib")
    endif()
    list(GET _lbt_shared 0 _lbt_shared)
    file(COPY_FILE "${_lbt_shared}" "${_blas_shim_dir}/libopenblas.so")
  endif()

  # The *default* lbt-forwarded backend (not linked directly -- see
  # LBT_DEFAULT_LIBS in src/cyhighs/_blas_backend.py). Compiling OpenBLAS
  # ourselves is deliberately avoided: it's what caused the AVX2/AVX512 build
  # breakage this project hit and moved away from previously. conda-forge
  # provides a prebuilt, plain-symbol OpenBLAS for every platform reached
  # here except musl Linux (conda-forge is glibc-only); musllinux instead
  # uses the Alpine package installed via apk in CI (see wheels.yml),
  # discovered via find_library the same way this project found OpenBLAS
  # before adopting lbt.
  if(_libc STREQUAL "musl")
    find_library(_openblas_backend NAMES openblas REQUIRED)
    list(APPEND _bundled_backend_libs "${_openblas_backend}")
  else()
    # Hashes pinned against real conda.anaconda.org/conda-forge repodata.json
    # entries. The pthreads (non-OpenMP) build variant avoids an additional
    # OpenMP runtime dependency.
    if(_conda_subdir STREQUAL "linux-64")
      set(_openblas_conda "libopenblas-0.3.33-pthreads_h94d23a6_0.conda")
      set(_openblas_sha256 3d9aa85648e5e18a6d66db98b8c4317cc426721ad7a220aa86330d1ccedc8903)
      set(_libgfortran_conda "libgfortran5-15.2.0-h68bc16d_19.conda")
      set(_libgfortran_sha256 057978bb69fea29ed715a9b98adf71015c31baecc4aeb2bfc20d4fd5d83579d4)
    elseif(_conda_subdir STREQUAL "linux-aarch64")
      set(_openblas_conda "libopenblas-0.3.33-pthreads_h9d3fd7e_0.conda")
      set(_openblas_sha256 b018ecfb05e75a8eea3f21f6b5c5c2a54b5178bdcf19e2e2df2735740214a8c8)
      set(_libgfortran_conda "libgfortran5-15.2.0-h1b7bec0_19.conda")
      set(_libgfortran_sha256 af8e9bdcaa77f133a8ee4c1ef57ef564d9c45aa262abf9f5ef9b50eb99d96407)
    elseif(_conda_subdir STREQUAL "win-64")
      # The Windows build has no libgfortran dependency (statically linked).
      set(_openblas_conda "libopenblas-0.3.33-pthreads_h877e47f_0.conda")
      set(_openblas_sha256 104bba89eaed090ab7dd6de17376ba7c14be7f4d44807346012e50a493f18ec9)
      set(_libgfortran_conda "")
    endif()

    set(_openblas_url "https://conda.anaconda.org/conda-forge/${_conda_subdir}/${_openblas_conda}")
    set(_openblas_root "${CMAKE_BINARY_DIR}/openblas-prebuilt")
    cyhighs_fetch_conda_package("${_openblas_url}" "${_openblas_sha256}" "${_openblas_root}")

    if(WIN32)
      # conda-forge's Windows package ships OpenBLAS as a bare DLL with no
      # "lib" prefix and no import library: Library/bin/openblas.dll.
      # Confirmed by extracting the real package; there is no
      # "libopenblas*.dll" name at all.
      file(GLOB _openblas_lib "${_openblas_root}/Library/bin/openblas.dll")
      if(NOT _openblas_lib)
        file(GLOB _openblas_lib "${_openblas_root}/Library/bin/openblas*.dll")
      endif()
    else()
      # Prefer the canonical libopenblas.so(.N) name over the
      # differently-prefixed internal real filename it's a symlink to (e.g.
      # libopenblas.so.0 -> libopenblasp-r0.3.33.so, confirmed by a real
      # extraction), since file(GLOB) result order is not guaranteed to be
      # deterministic across platforms.
      file(GLOB _openblas_lib "${_openblas_root}/lib/libopenblas.so*")
      if(NOT _openblas_lib)
        file(GLOB _openblas_lib "${_openblas_root}/lib/libopenblas*.so*")
      endif()
    endif()
    if(NOT _openblas_lib)
      message(FATAL_ERROR "No OpenBLAS shared library found after extracting ${_openblas_conda}")
    endif()
    list(GET _openblas_lib 0 _openblas_backend)

    if(WIN32)
      # MSVC's linker needs a .lib import library, not the bare DLL, and
      # conda-forge ships none for OpenBLAS (it's only linked here to force
      # delvewheel to bundle it -- see the target_link_libraries comment
      # below). Generate one the same way as for libblastrampoline above.
      cyhighs_generate_msvc_import_lib(
        "${_openblas_backend}"
        "${_blas_shim_dir}/openblas-backend.def"
        "${_blas_shim_dir}/openblas-backend.lib")
      list(APPEND _bundled_backend_libs "${_blas_shim_dir}/openblas-backend.lib")
    else()
      list(APPEND _bundled_backend_libs "${_openblas_backend}")
    endif()

    if(_libgfortran_conda)
      set(_libgfortran_url "https://conda.anaconda.org/conda-forge/${_conda_subdir}/${_libgfortran_conda}")
      set(_libgfortran_root "${CMAKE_BINARY_DIR}/libgfortran-prebuilt")
      cyhighs_fetch_conda_package("${_libgfortran_url}" "${_libgfortran_sha256}" "${_libgfortran_root}")
      file(GLOB _libgfortran_lib "${_libgfortran_root}/lib/libgfortran*.so*")
      if(_libgfortran_lib)
        list(APPEND _bundled_backend_libs ${_libgfortran_lib})
      endif()
    endif()
  endif()

  list(PREPEND CMAKE_LIBRARY_PATH "${_blas_shim_dir}")
  list(PREPEND CMAKE_PREFIX_PATH "${_blas_shim_dir}")
endif()

# ---------------------------------------------------------------------------
# Compile HiGHS + HiPO from source. On non-Apple platforms this links the lbt
# shim staged above in place of OpenBLAS; on Apple it links Accelerate.
# ---------------------------------------------------------------------------
include(FetchContent)

set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(FAST_BUILD ON CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(ZLIB OFF CACHE BOOL "" FORCE)

# HiPO is the interior point solver added in HiGHS 1.15. It requires
# FAST_BUILD and a BLAS. BUILD_OPENBLAS stays OFF: OpenBLAS is never compiled
# by this project (see the BLAS/LAPACK section above, which also prepends
# CMAKE_LIBRARY_PATH/CMAKE_PREFIX_PATH with the lbt shim directory on
# non-Apple platforms before this FetchContent runs).
set(HIPO ON CACHE BOOL "" FORCE)
set(BUILD_SHARED_EXTRAS_LIB OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
  highs
  GIT_REPOSITORY https://github.com/ERGO-Code/HiGHS.git
  GIT_TAG v${HIGHS_VERSION}
  GIT_SHALLOW ON)
FetchContent_MakeAvailable(highs)

set(_highs_include_dir "${highs_SOURCE_DIR}/highs")
set(_highs_link_libraries "highs::highs")

set(_highs_license_file "")
foreach(_candidate LICENSE.txt LICENSE)
  if(EXISTS "${highs_SOURCE_DIR}/${_candidate}")
    set(_highs_license_file "${highs_SOURCE_DIR}/${_candidate}")
    break()
  endif()
endforeach()

find_package(Threads REQUIRED)

# ---------------------------------------------------------------------------
# Transpile the Cython source to C.
# ---------------------------------------------------------------------------
set(cython_source "${CMAKE_CURRENT_SOURCE_DIR}/src/cyhighs/_core.pyx")
set(generated_c "${CMAKE_CURRENT_BINARY_DIR}/_core.c")

add_custom_command(
  OUTPUT "${generated_c}"
  COMMAND
    "${Python_EXECUTABLE}" -m cython --3str -o "${generated_c}"
    "${cython_source}"
  DEPENDS "${cython_source}"
          "${CMAKE_CURRENT_SOURCE_DIR}/src/cyhighs/_highs_c_api.pxd"
  VERBATIM)

# ---------------------------------------------------------------------------
# Build the extension module.
# ---------------------------------------------------------------------------
python_add_library(_core MODULE "${generated_c}" WITH_SOABI)

target_include_directories(_core PRIVATE "${_highs_include_dir}")
target_link_libraries(_core PRIVATE ${_highs_link_libraries} Threads::Threads)
if(CMAKE_DL_LIBS)
  target_link_libraries(_core PRIVATE ${CMAKE_DL_LIBS})
endif()

# The bundled OpenBLAS (+ libgfortran) is only ever dlopen'd indirectly by lbt
# at runtime via LBT_DEFAULT_LIBS (see src/cyhighs/_blas_backend.py) -- it is
# not a real dependency of _core. It is linked here anyway, purely so that
# auditwheel/delvewheel treat it as a normal dependency to relocate and
# vendor into the wheel (with correct RPATHs and its own transitive
# libgfortran dependency pulled in), the same way OpenBLAS was vendored by
# those tools before this change. Because those tools rename/hash-suffix
# vendored libraries, _blas_backend.py globs for the relocated file at import
# time rather than assuming a fixed name. Empty (a no-op) on Apple, where
# HiGHS links Accelerate directly and there is nothing to bundle here.
target_link_libraries(_core PRIVATE ${_bundled_backend_libs})

# The Cython source compiles as C, but the HiGHS libraries are C++. Linking with
# the C++ driver pulls in the C++ runtime (libstdc++ / libc++).
set_target_properties(_core PROPERTIES LINKER_LANGUAGE CXX)

# Install the compiled module next to the Python sources inside the package.
install(TARGETS _core DESTINATION cyhighs)

# Bundle the upstream HiGHS license from the fetched source tree, since the
# solver is statically linked into the extension.
if(_highs_license_file)
  install(FILES "${_highs_license_file}"
          DESTINATION cyhighs RENAME HiGHS-LICENSE.txt)
endif()
