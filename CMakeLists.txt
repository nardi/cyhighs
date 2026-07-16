# CMake build for the cyhighs Cython extension.
#
# There are two ways to acquire HiGHS, selected by CYHIGHS_HIGHS_FROM_SOURCE:
#
#   * OFF (default): download a prebuilt HiGHS "static-apache" release archive
#     for the target platform, extract it, and link the static libraries it
#     ships (libhighs, libhighs_extras and the bundled OpenBLAS). The Linux
#     archives are built against glibc >= 2.38, so this path is used on the
#     native runners (producing manylinux_2_39) and on macOS/Windows.
#
#   * ON: compile the HiGHS solver and HiPO from source with FetchContent,
#     linking a prebuilt OpenBLAS already installed in the build environment
#     (HiGHS's default BUILD_OPENBLAS=OFF). This path is used inside the
#     manylinux_2_28 / musllinux_1_2 containers, where the prebuilt archive
#     cannot link, to produce the more portable manylinux_2_28 / musllinux
#     wheels.
#
# Either way the result is a single self contained extension module.
cmake_minimum_required(VERSION 3.28)

project(cyhighs LANGUAGES C CXX)

# HiGHS is written in C++17. Enforce it here so that our extension agrees with
# the standard the HiGHS libraries were compiled against.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Position independent code is required to link the static HiGHS libraries into
# the shared extension module. The release archives are already built PIC.
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ---------------------------------------------------------------------------
# Locate Python and the Cython compiler through scikit-build-core.
# ---------------------------------------------------------------------------
find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

# The HiGHS release the wheel is built against. Used as the prebuilt archive
# version and as the FetchContent git tag (v${HIGHS_VERSION}).
set(HIGHS_VERSION 1.15.1)

# Build HiGHS from source instead of using the prebuilt static-apache archive.
# Enabled inside the manylinux_2_28 / musllinux containers so that the resulting
# wheel links against the container glibc/musl and carries the portable
# manylinux_2_28 / musllinux tag.
option(CYHIGHS_HIGHS_FROM_SOURCE
  "Build HiGHS from source (manylinux_2_28 / musllinux) instead of the prebuilt static-apache archive"
  OFF)

# These are filled in by whichever acquisition path runs below and consumed by
# the common extension-build section that follows.
set(_highs_include_dir "")
set(_highs_link_libraries "")
set(_highs_license_file "")

if(CYHIGHS_HIGHS_FROM_SOURCE)
  # -------------------------------------------------------------------------
  # Compile HiGHS + HiPO from source, linking a prebuilt OpenBLAS.
  # -------------------------------------------------------------------------
  include(FetchContent)

  # Build settings applied to the HiGHS subproject. These are set as cache
  # variables before the fetch so that HiGHS picks them up during configuration.
  set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
  set(FAST_BUILD ON CACHE BOOL "" FORCE)
  set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
  set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
  set(ZLIB OFF CACHE BOOL "" FORCE)

  # HiPO is the interior point solver added in HiGHS 1.15. It requires FAST_BUILD
  # and a BLAS. BUILD_OPENBLAS is deliberately left at HiGHS's default of OFF: we
  # link the prebuilt OpenBLAS installed in the build environment (openblas-devel
  # on manylinux, openblas-dev on musllinux). HiGHS's cmake/FindHipoDeps.cmake
  # discovers it with find_library(NAMES openblas) on the default system paths,
  # so no BLAS source compile and no NO_AVX2/NO_AVX512 workaround are needed here.
  #
  # BUILD_SHARED_EXTRAS_LIB must be OFF. HiGHS places the HiPO numerical
  # dependencies (AMD, BLAS, METIS, RCM) in a separate highs_extras library. When
  # that library is shared, HiGHS loads it at runtime from a highs_extras.so that
  # would have to be shipped alongside the wheel. Building it static instead links
  # the HiPO code directly into our extension, so the wheel stays self contained.
  set(HIPO ON CACHE BOOL "" FORCE)
  set(BUILD_SHARED_EXTRAS_LIB OFF CACHE BOOL "" FORCE)

  # EXCLUDE_FROM_ALL keeps HiGHS's own install() rules (its static libs, the
  # standalone highs CLI binary, headers, and CMake package config) out of our
  # wheel. Without it, cmake --install would copy all of that in alongside
  # _core.so even though nothing in cyhighs needs it at runtime.
  FetchContent_Declare(
    highs
    GIT_REPOSITORY https://github.com/ERGO-Code/HiGHS.git
    GIT_TAG v${HIGHS_VERSION}
    GIT_SHALLOW ON
    EXCLUDE_FROM_ALL)
  FetchContent_MakeAvailable(highs)

  # The C API header lives in the highs/interfaces directory of the source tree.
  set(_highs_include_dir "${highs_SOURCE_DIR}/highs")
  # The exported target transitively pulls highs_extras and the discovered
  # OpenBLAS. The prebuilt libopenblas.so becomes a NEEDED entry on the
  # extension, which auditwheel then vendors into the wheel.
  set(_highs_link_libraries "highs::highs")

  # Bundle the upstream HiGHS license from the fetched source tree.
  foreach(_candidate LICENSE.txt LICENSE)
    if(EXISTS "${highs_SOURCE_DIR}/${_candidate}")
      set(_highs_license_file "${highs_SOURCE_DIR}/${_candidate}")
      break()
    endif()
  endforeach()
else()
  # -------------------------------------------------------------------------
  # Acquire the prebuilt HiGHS static-apache archive.
  #
  # The static-apache variant bundles the HiPO interior point solver together
  # with its numerical dependencies (AMD, BLAS via OpenBLAS, METIS, RCM), ships
  # headers and a CMake package config, and is distributed under Apache 2.0.
  # -------------------------------------------------------------------------

  # Normalise the architecture name to match the release asset naming.
  string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" _highs_arch)
  if(_highs_arch MATCHES "amd64|x86_64|x64")
    set(_highs_arch "x86_64")
  elseif(_highs_arch MATCHES "aarch64|arm64")
    set(_highs_arch "aarch64")
  endif()

  # Select the release asset and its pinned SHA256 for the target platform. Only
  # the platforms with a published static-apache archive are supported; anything
  # else (musllinux, Intel macOS, 32 bit) must build against a system HiGHS.
  set(_highs_sha "")
  if(APPLE)
    if(NOT _highs_arch STREQUAL "aarch64")
      message(FATAL_ERROR
        "No prebuilt HiGHS static-apache binary is published for Intel macOS. "
        "Only Apple Silicon (arm64) is supported.")
    endif()
    set(_highs_asset "highs-${HIGHS_VERSION}-arm-apple-static-apache.tar.gz")
    # TODO: pin the SHA256 of the arm-apple archive.
  elseif(WIN32)
    if(NOT _highs_arch STREQUAL "x86_64")
      message(FATAL_ERROR "No prebuilt HiGHS static-apache binary for Windows ${_highs_arch}.")
    endif()
    set(_highs_asset "highs-${HIGHS_VERSION}-x86_64-windows-static-apache.zip")
    # TODO: pin the SHA256 of the x86_64-windows archive.
  elseif(UNIX)
    set(_highs_asset "highs-${HIGHS_VERSION}-${_highs_arch}-linux-gnu-static-apache.tar.gz")
    if(_highs_arch STREQUAL "x86_64")
      set(_highs_sha "b5c5d25cfbb66d438a3b40b6919c50c3c82341f74062f5f44371a52e65d6bd2c")
    endif()
    # TODO: pin the SHA256 of the aarch64-linux archive.
  else()
    message(FATAL_ERROR "Unsupported platform for prebuilt HiGHS: ${CMAKE_SYSTEM_NAME}/${_highs_arch}.")
  endif()

  # The extracted tree lands here. HIGHS_ARCHIVE lets a caller point at a local
  # copy of the archive (air gapped builds, CI caches, offline development) so
  # that no download happens.
  set(HIGHS_ARCHIVE "" CACHE FILEPATH "Local HiGHS static-apache archive to use instead of downloading")
  set(_highs_root "${CMAKE_BINARY_DIR}/highs-prebuilt")

  if(NOT EXISTS "${_highs_root}/lib")
    if(HIGHS_ARCHIVE AND EXISTS "${HIGHS_ARCHIVE}")
      set(_highs_local "${HIGHS_ARCHIVE}")
      message(STATUS "Using local HiGHS archive: ${_highs_local}")
    else()
      set(_highs_local "${CMAKE_BINARY_DIR}/${_highs_asset}")
      set(_highs_url
        "https://github.com/ERGO-Code/HiGHS/releases/download/v${HIGHS_VERSION}/${_highs_asset}")
      message(STATUS "Downloading HiGHS: ${_highs_url}")
      if(_highs_sha STREQUAL "")
        message(WARNING
          "No pinned SHA256 for ${_highs_asset}; downloading without an integrity check.")
        file(DOWNLOAD "${_highs_url}" "${_highs_local}" TLS_VERIFY ON STATUS _highs_dl)
      else()
        file(DOWNLOAD "${_highs_url}" "${_highs_local}"
          EXPECTED_HASH SHA256=${_highs_sha} TLS_VERIFY ON STATUS _highs_dl)
      endif()
      list(GET _highs_dl 0 _highs_dl_code)
      if(NOT _highs_dl_code EQUAL 0)
        list(GET _highs_dl 1 _highs_dl_msg)
        message(FATAL_ERROR "Failed to download ${_highs_url}: ${_highs_dl_msg}")
      endif()
    endif()
    file(MAKE_DIRECTORY "${_highs_root}")
    file(ARCHIVE_EXTRACT INPUT "${_highs_local}" DESTINATION "${_highs_root}")
  endif()

  # Collect the static libraries in link order: highs depends on highs_extras,
  # which depends on OpenBLAS. Match both the Unix (lib*.a) and Windows (*.lib)
  # naming so the same logic works everywhere.
  set(_highs_static_libs "")
  foreach(_name highs highs_extras)
    file(GLOB _found
      "${_highs_root}/lib/lib${_name}.a"
      "${_highs_root}/lib/${_name}.lib"
      "${_highs_root}/lib/lib${_name}.lib")
    if(NOT _found)
      message(FATAL_ERROR "Prebuilt HiGHS library '${_name}' not found in ${_highs_root}/lib")
    endif()
    list(GET _found 0 _lib)
    list(APPEND _highs_static_libs "${_lib}")
  endforeach()

  # HiPO needs a BLAS. The Linux and Windows archives bundle OpenBLAS as a static
  # library (its name may carry a target or version suffix, so match with a
  # wildcard). The macOS archive ships no OpenBLAS and instead relies on the system
  # Accelerate framework, so fall back to that there.
  file(GLOB _openblas_found
    "${_highs_root}/lib/libopenblas.a"
    "${_highs_root}/lib/libopenblas*.a"
    "${_highs_root}/lib/openblas.lib"
    "${_highs_root}/lib/openblas*.lib"
    "${_highs_root}/lib/libopenblas*.lib")
  if(_openblas_found)
    list(GET _openblas_found 0 _lib)
    list(APPEND _highs_static_libs "${_lib}")
  elseif(APPLE)
    find_library(_accelerate Accelerate REQUIRED)
    list(APPEND _highs_static_libs "${_accelerate}")
  else()
    file(GLOB _lib_contents "${_highs_root}/lib/*")
    message(FATAL_ERROR
      "No BLAS library found in ${_highs_root}/lib. Contents: ${_lib_contents}")
  endif()

  # The prebuilt libraries reference the system zlib (the archives are built with
  # ZLIB on) and pthreads. On Windows the Windows archive may bundle zlib, so it
  # is looked up but not required there.
  find_package(Threads REQUIRED)
  if(WIN32)
    find_package(ZLIB)
  else()
    find_package(ZLIB REQUIRED)
  endif()

  # The C API header lives at include/highs/interfaces/highs_c_api.h in the
  # archive, so include/highs is the directory to add.
  set(_highs_include_dir "${_highs_root}/include/highs")
  set(_highs_link_libraries ${_highs_static_libs} Threads::Threads)
  if(ZLIB_FOUND)
    list(APPEND _highs_link_libraries ZLIB::ZLIB)
  endif()
  if(CMAKE_DL_LIBS)
    list(APPEND _highs_link_libraries ${CMAKE_DL_LIBS})
  endif()

  if(EXISTS "${_highs_root}/share/doc/HIGHS/LICENSE.txt")
    set(_highs_license_file "${_highs_root}/share/doc/HIGHS/LICENSE.txt")
  endif()
endif()

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
target_link_libraries(_core PRIVATE ${_highs_link_libraries})

# The Cython source compiles as C, but the HiGHS libraries are C++. Linking with
# the C++ driver pulls in the C++ runtime (libstdc++ / libc++).
set_target_properties(_core PROPERTIES LINKER_LANGUAGE CXX)

# Install the compiled module next to the Python sources inside the package.
install(TARGETS _core DESTINATION cyhighs)

# Bundle the upstream HiGHS license into the package for attribution, since the
# solver is statically linked into the extension.
if(_highs_license_file)
  install(FILES "${_highs_license_file}"
          DESTINATION cyhighs RENAME HiGHS-LICENSE.txt)
endif()
