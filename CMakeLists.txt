# CMake build for the cyhighs Cython extension.
#
# HiGHS + HiPO are always compiled from source (FetchContent) on every platform.
#
# On Linux and Windows, HiPO's BLAS dependency is satisfied by
# libblastrampoline (lbt) rather than by linking OpenBLAS directly: lbt is a
# small MIT-licensed shared library that exports the standard BLAS/LAPACK ABI
# and forwards each call, at runtime, to whichever real BLAS implementation it
# has been pointed at (this is the same mechanism Julia's LinearAlgebra/
# HiGHS.jl use to switch BLAS backends without recompiling). Once the compiled
# extension (and therefore lbt) is loaded, cyhighs's own
# src/cyhighs/_blas_backend.py calls lbt's `lbt_forward` C API to register:
#
#   * by default, a prebuilt OpenBLAS bundled inside the wheel (so the
#     package remains fully self contained with zero configuration, matching
#     the project's historical "no external system dependencies" promise);
#   * Intel MKL instead, if the optional `cyhighs[mkl]` extra is installed
#     and its shared library can be located (Linux x86_64 / Windows x86_64
#     only -- Intel has never published MKL for macOS or for ARM).
#
# CYHIGHS_USE_LBT (below) turns this off, linking the bundled OpenBLAS
# directly with no lbt in the process at all. It exists for local A/B testing
# against the default lbt-forwarded build, not as a shipped configuration.
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
cmake_minimum_required(VERSION 3.28)

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

# Off links the bundled OpenBLAS directly instead of routing it through
# libblastrampoline, with no forwarding layer in between. This exists for
# local A/B testing against the default lbt-forwarded build, not as a shipped
# configuration: with it off, the cyhighs[mkl] extra and the CYHIGHS_LBT_PREFER/
# CYHIGHS_LBT_DEBUG environment variables (see src/cyhighs/_blas_backend.py)
# have no effect, since there is no lbt in the process to configure. Toggle it
# with, for example, `uv sync --config-settings=cmake.define.CYHIGHS_USE_LBT=OFF`,
# in a clean build directory since scikit-build-core otherwise reuses the same
# build directory (see build-dir in pyproject.toml) across runs.
option(CYHIGHS_USE_LBT "Route HiPO's BLAS through libblastrampoline" ON)

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
# *.dll.a import library that MSVC cannot consume directly.
#
# cibuildwheel's Windows build runs in a plain shell, not an MSVC developer
# command prompt, so dumpbin/lib.exe are not on PATH (confirmed by a real CI
# failure: "dumpbin/lib.exe not found"). CMAKE_C_COMPILER is always the
# resolved absolute path to cl.exe once project() has run, though, and MSVC
# always installs dumpbin.exe/lib.exe in that exact same toolset directory
# (.../VC/Tools/MSVC/<version>/bin/Hostx64/x64/), so look there directly
# instead of relying on PATH.
function(cyhighs_generate_msvc_import_lib dll_path def_path out_lib_path)
  get_filename_component(_msvc_bin_dir "${CMAKE_C_COMPILER}" DIRECTORY)
  find_program(_dumpbin dumpbin HINTS "${_msvc_bin_dir}")
  find_program(_implib lib HINTS "${_msvc_bin_dir}")
  if(NOT _dumpbin OR NOT _implib)
    message(FATAL_ERROR
      "dumpbin/lib.exe not found (looked next to the MSVC compiler at "
      "${_msvc_bin_dir} and on PATH); cannot generate an MSVC import library "
      "for ${dll_path}.")
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

# Stage a single shared library into the runtime bundle under its real SONAME,
# as one plain file with no symlinks. The prebuilt lbt/OpenBLAS/libgfortran
# archives ship each library as a dev-symlink -> SONAME-symlink -> real-file
# chain (e.g. libopenblas.so -> libopenblas.so.0 -> libopenblasp-r0.3.33.so).
# _core's NEEDED entry only ever refers to the SONAME (confirmed with
# objdump/readelf against a real built wheel), so the other chain members are
# never loaded and don't need to ship at all. A real CI-built wheel showed the
# wheel-packaging step does not preserve symlinks (each chain member was
# expanded into its own full-size copy), roughly tripling the wheel size;
# writing exactly one real file under the SONAME sidesteps that regardless of
# how the packaging step handles symlinks, since there is none left to expand.
function(cyhighs_stage_runtime_lib candidate_paths dest_dir)
  list(GET candidate_paths 0 _first)
  file(REAL_PATH "${_first}" _real_file)
  execute_process(
    COMMAND "${CMAKE_OBJDUMP}" -p "${_real_file}"
    OUTPUT_VARIABLE _objdump_output
    RESULT_VARIABLE _objdump_result)
  if(NOT _objdump_result EQUAL 0)
    message(FATAL_ERROR "cyhighs_stage_runtime_lib: objdump failed on ${_real_file}")
  endif()
  string(REGEX MATCH "SONAME[ \t]+([^ \t\r\n]+)" _ "${_objdump_output}")
  if(NOT CMAKE_MATCH_1)
    message(FATAL_ERROR "cyhighs_stage_runtime_lib: no SONAME found in ${_real_file}")
  endif()
  set(_dest_file "${dest_dir}/${CMAKE_MATCH_1}")
  file(COPY_FILE "${_real_file}" "${_dest_file}")
  # These are prebuilt binaries from conda-forge/JuliaBinaryWrappers, shipped
  # with full DWARF debug info still attached (confirmed against a real built
  # wheel: stripping libgfortran alone cut it from 11.4 MB to 3.6 MB). None of
  # it is reachable from Python, so strip it here rather than relying on
  # auditwheel, which does not strip by default.
  execute_process(COMMAND "${CMAKE_STRIP}" --strip-unneeded "${_dest_file}")
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
set(_needs_openblas_extension_stub FALSE)
if(NOT APPLE)
  # The *default* backend: real OpenBLAS, forwarded to by lbt at runtime when
  # CYHIGHS_USE_LBT is on (the default), or linked directly when it is off.
  # Fetched either way. Compiling OpenBLAS ourselves is deliberately avoided:
  # it's what caused the AVX2/AVX512 build breakage this project hit and
  # moved away from previously. conda-forge provides a prebuilt, plain-symbol
  # OpenBLAS for every platform reached here except musl Linux (conda-forge
  # is glibc-only); musllinux instead uses the Alpine package installed via
  # apk in CI (see wheels.yml), discovered via find_library the same way
  # this project found OpenBLAS before adopting lbt.
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

    if(NOT WIN32)
      list(APPEND _bundled_backend_libs "${_openblas_backend}")
    endif()

    if(_libgfortran_conda)
      set(_libgfortran_url "https://conda.anaconda.org/conda-forge/${_conda_subdir}/${_libgfortran_conda}")
      set(_libgfortran_root "${CMAKE_BINARY_DIR}/libgfortran-prebuilt")
      cyhighs_fetch_conda_package("${_libgfortran_url}" "${_libgfortran_sha256}" "${_libgfortran_root}")
      file(GLOB _libgfortran_lib "${_libgfortran_root}/lib/libgfortran*.so*")
      if(_libgfortran_lib)
        list(GET _libgfortran_lib 0 _libgfortran_backend)
        list(APPEND _bundled_backend_libs "${_libgfortran_backend}")
      endif()
    endif()
  endif()

  # The directory the find_package(BLAS)/BLA_VENDOR=OpenBLAS lookup below is
  # pointed at, via CMAKE_LIBRARY_PATH/CMAKE_PREFIX_PATH (prepended below).
  # HiGHS's FindHipoDeps.cmake does not call find_library(NAMES openblas)
  # directly (confirmed by reading that file). With BLAS_LIBRARIES/BLA_VENDOR
  # unset, it tries find_package(OpenBLAS CONFIG) first (finds nothing here,
  # since neither lbt nor the bundled OpenBLAS ships a CMake package config),
  # then sets BLA_VENDOR=OpenBLAS and calls find_package(BLAS). CMake's own
  # FindBLAS.cmake module handles that vendor with an internal
  # find_library(NAMES openblas) that does respect
  # CMAKE_LIBRARY_PATH/CMAKE_PREFIX_PATH, so whatever is staged here under the
  # "openblas" name is what HiGHS links, with no upstream HiGHS source change.
  set(_blas_shim_dir "${CMAKE_BINARY_DIR}/blas-shim")
  file(REMOVE_RECURSE "${_blas_shim_dir}")
  file(MAKE_DIRECTORY "${_blas_shim_dir}")

  if(CYHIGHS_USE_LBT)
    set(_needs_openblas_extension_stub TRUE)
    # Fetch libblastrampoline (lbt): the BLAS/LAPACK ABI HiPO links against,
    # staged here under the "openblas" name so it is what find_package(BLAS)
    # above resolves to, instead of the real backend fetched above.
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
      # The JLL release is MinGW-built and ships with DWARF debug sections
      # still attached (confirmed against a real built wheel: stripping it
      # cut the DLL from 2.8 MB to 1.2 MB). cibuildwheel's Windows build runs
      # outside an MSYS/MinGW shell (the same reason
      # cyhighs_generate_msvc_import_lib above cannot assume dumpbin/lib.exe
      # are on PATH), so a MinGW strip.exe is not guaranteed to be present;
      # skip stripping rather than fail the build if none is found.
      find_program(_mingw_strip strip)
      if(_mingw_strip)
        execute_process(COMMAND "${_mingw_strip}" --strip-unneeded "${_blas_shim_dir}/blastrampoline.dll")
      endif()
      # A separate import library for the real backend, purely so delvewheel
      # treats it as a normal dependency to vendor (see the
      # target_link_libraries comment below). openblas.lib above points at
      # blastrampoline.dll instead, for HiGHS's own BLAS resolution.
      cyhighs_generate_msvc_import_lib(
        "${_openblas_backend}"
        "${_blas_shim_dir}/openblas-backend.def"
        "${_blas_shim_dir}/openblas-backend.lib")
      list(APPEND _bundled_backend_libs "${_blas_shim_dir}/openblas-backend.lib")
    else()
      file(GLOB _lbt_shared "${_lbt_root}/lib/libblastrampoline.*")
      if(NOT _lbt_shared)
        message(FATAL_ERROR "No libblastrampoline shared library found in ${_lbt_root}/lib")
      endif()
      # Preserve the whole libblastrampoline.so -> .so.N -> .so.N.N.N chain
      # under its own names, not just one file renamed to "libopenblas.so".
      # The linker embeds whatever SONAME is baked into the real versioned
      # file (e.g. libblastrampoline.so.5) as _core's NEEDED entry, regardless
      # of what name/path we link it under -- confirmed by a real CI failure
      # at import time: "libblastrampoline.so.5: cannot open shared object
      # file". Renaming only the copy find_package(BLAS) is pointed at left
      # that actual SONAME target missing from the shim directory entirely.
      file(COPY ${_lbt_shared} DESTINATION "${_blas_shim_dir}")
      list(GET _lbt_shared 0 _lbt_shared_one)
      file(COPY_FILE "${_lbt_shared_one}" "${_blas_shim_dir}/libopenblas.so")
    endif()
  else()
    # No lbt: point find_package(BLAS) straight at the real backend fetched
    # above, so HiGHS links it directly with no forwarding layer in between.
    # This exists for local A/B testing (see the CYHIGHS_USE_LBT docstring
    # near the top of this file), not as a shipped configuration.
    if(WIN32)
      cyhighs_generate_msvc_import_lib(
        "${_openblas_backend}"
        "${_blas_shim_dir}/openblas.def"
        "${_blas_shim_dir}/openblas.lib")
      list(APPEND _bundled_backend_libs "${_blas_shim_dir}/openblas.lib")
    else()
      # Stage the real SONAME (for _core's BUILD_RPATH to resolve it in the
      # editable/build-tree case, using cyhighs_stage_runtime_lib defined
      # above) and the "libopenblas.so" alias find_package(BLAS) looks for.
      cyhighs_stage_runtime_lib("${_openblas_backend}" "${_blas_shim_dir}")
      file(COPY_FILE "${_openblas_backend}" "${_blas_shim_dir}/libopenblas.so")
      if(_libgfortran_backend)
        # Unlike lbt (which only depends on libdl/libc), real OpenBLAS's
        # Fortran-compiled kernels need libgfortran resolvable at link time,
        # not just at runtime -- confirmed by a real link failure here
        # ("undefined reference to `_gfortran_etime'") when it was missing
        # from this directory, since HiGHS's own BLAS detection performs a
        # real link check, not just a file-existence check.
        cyhighs_stage_runtime_lib("${_libgfortran_backend}" "${_blas_shim_dir}")
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

# EXCLUDE_FROM_ALL (CMake 3.28+, hence the cmake_minimum_required above) keeps
# HiGHS's own standalone "highs" CLI executable out of the default build.
# cyhighs never needs that target, and it cannot link on non-Apple platforms
# anyway: it statically links libhighs_extras.a in full, including
# myblas.cpp's highs_openblas_set_num_threads(), which calls the real
# OpenBLAS-specific (not standard BLAS/LAPACK ABI) openblas_set_num_threads()
# -- undefined against our lbt shim, confirmed by a real CI link failure.
# _core only pulls in the highs/highs_extras static libraries themselves
# (via highs::highs below), which still build normally either way.
FetchContent_Declare(
  highs
  GIT_REPOSITORY https://github.com/ERGO-Code/HiGHS.git
  GIT_TAG v${HIGHS_VERSION}
  GIT_SHALLOW ON
  EXCLUDE_FROM_ALL)
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

set(_core_extra_sources "")
if(_needs_openblas_extension_stub)
  # HiGHS's myblas.cpp calls the real OpenBLAS-specific extension function
  # openblas_set_num_threads() (not part of the standard BLAS/LAPACK ABI lbt
  # forwards), because HiGHS's build believes "openblas" is a real OpenBLAS
  # (see the BLAS/LAPACK section above). A static executable that links
  # libhighs_extras.a in full cannot leave this undefined (confirmed by a
  # real CI failure linking HiGHS's own CLI, excluded from the build above),
  # and a shared library like _core would crash if this ever got called at
  # runtime with no definition at all. Rather than a no-op, forward both
  # openblas_get_num_threads() and openblas_set_num_threads() to lbt's own
  # lbt_get_num_threads()/lbt_set_num_threads(), which lbt already routes to
  # whichever real backend (OpenBLAS or MKL) is currently forwarded to (lbt
  # has built-in knowledge of both libraries' thread-control functions, see
  # lbt_register_thread_interface() in libblastrampoline.h), so HiGHS's
  # thread-count control keeps working regardless of the active backend.
  set(_openblas_stub_c "${CMAKE_BINARY_DIR}/openblas_extension_stub.c")
  file(WRITE "${_openblas_stub_c}" [[
#include <stdint.h>

extern int32_t lbt_get_num_threads(void);
extern void lbt_set_num_threads(int32_t num_threads);

int openblas_get_num_threads(void) {
  return (int)lbt_get_num_threads();
}

void openblas_set_num_threads(int num_threads) {
  lbt_set_num_threads((int32_t)num_threads);
}
]])
  list(APPEND _core_extra_sources "${_openblas_stub_c}")
endif()

# ---------------------------------------------------------------------------
# Build the extension module.
# ---------------------------------------------------------------------------
python_add_library(_core MODULE "${generated_c}" ${_core_extra_sources} WITH_SOABI)

target_include_directories(_core PRIVATE "${_highs_include_dir}")
target_link_libraries(_core PRIVATE ${_highs_link_libraries} Threads::Threads)
if(CMAKE_DL_LIBS)
  target_link_libraries(_core PRIVATE ${CMAKE_DL_LIBS})
endif()

# Link the bundled OpenBLAS (+ libgfortran) into _core. With CYHIGHS_USE_LBT
# on (the default), this is only so auditwheel/delvewheel see it as a normal
# dependency to relocate and vendor, and so its transitive deps
# (libgfortran -> libquadmath) get pulled into the wheel too; the actual BLAS
# calls go through lbt instead. With it off, this is the real, direct BLAS
# link. Empty (a no-op) on Apple, where HiGHS links Accelerate directly.
target_link_libraries(_core PRIVATE ${_bundled_backend_libs})

# Make _core's own runtime dependencies loadable. This has to work in two
# very different situations: the wheel builds (cibuildwheel, where
# auditwheel/delvewheel repair the wheel afterward) and the plain editable
# build that tests.yml / `uv sync` / local development use, which has no
# repair step at all. In both, the bundled libraries are installed into the
# package directory next to _core, and _core is pointed at that directory.
if(NOT APPLE)
  if(WIN32)
    # Windows has no RPATH-equivalent: dependent DLLs are found next to the
    # loading module. Copy them next to _core in the build tree (for the
    # unrepaired build) and install them into the package directory (for the
    # wheel, which a real CI failure showed delvewheel does not otherwise
    # populate from the build-tree shim location on its own).
    if(CYHIGHS_USE_LBT)
      set(_windows_runtime_dlls "${_blas_shim_dir}/blastrampoline.dll" "${_openblas_backend}")
    else()
      set(_windows_runtime_dlls "${_openblas_backend}")
    endif()
    add_custom_command(TARGET _core POST_BUILD
      COMMAND "${CMAKE_COMMAND}" -E copy_if_different
        ${_windows_runtime_dlls} "$<TARGET_FILE_DIR:_core>")
    install(FILES ${_windows_runtime_dlls} DESTINATION cyhighs)
  else()
    # On Linux, _core's NEEDED entries are libblastrampoline.so.5 (via HiGHS's
    # shim link) and the bundled OpenBLAS SONAME. Stage just those SONAME
    # files (via cyhighs_stage_runtime_lib, see above) into a bundle directory
    # and install it next to _core, then give _core an $ORIGIN INSTALL_RPATH
    # so it resolves them as siblings. This is what a real CI failure showed
    # was missing: with an empty install RPATH, the editable build could not
    # import _core (libblastrampoline.so.5 not found) and auditwheel could not
    # locate the same libraries to vendor them into the repaired wheel. The
    # BUILD_RPATH keeps the in-build-tree _core loadable too. On the wheel
    # path, auditwheel still runs afterward and pulls the deeper transitive
    # deps (e.g. libquadmath) into cyhighs.libs; on the editable path those
    # come from the system toolchain.
    set(_runtime_bundle_dir "${CMAKE_BINARY_DIR}/runtime-bundle")
    file(REMOVE_RECURSE "${_runtime_bundle_dir}")
    file(MAKE_DIRECTORY "${_runtime_bundle_dir}")
    if(CYHIGHS_USE_LBT)
      cyhighs_stage_runtime_lib("${_lbt_shared}" "${_runtime_bundle_dir}")
    endif()
    foreach(_backend_lib IN LISTS _bundled_backend_libs)
      cyhighs_stage_runtime_lib("${_backend_lib}" "${_runtime_bundle_dir}")
    endforeach()
    install(DIRECTORY "${_runtime_bundle_dir}/" DESTINATION cyhighs)
    set_target_properties(_core PROPERTIES
      INSTALL_RPATH "$ORIGIN"
      BUILD_RPATH "${_blas_shim_dir}")
  endif()
endif()

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
