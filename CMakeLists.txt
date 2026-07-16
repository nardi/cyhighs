# CMake build for the cyhighs Cython extension.
#
# This file fetches the HiGHS solver at a pinned release tag, builds it as a
# static library so that the resulting wheel is fully self contained, transpiles
# the Cython source to C, and links everything into a single extension module.
cmake_minimum_required(VERSION 3.24)

project(cyhighs LANGUAGES C CXX)

# HiGHS is written in C++17. Enforce it here so that every fetched target and our
# own extension agree on the standard.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Position independent code is required to link the static HiGHS library into the
# shared extension module.
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ---------------------------------------------------------------------------
# Locate Python and the Cython compiler through scikit-build-core.
# ---------------------------------------------------------------------------
find_package(
  Python
  COMPONENTS Interpreter Development.Module
  REQUIRED)

# ---------------------------------------------------------------------------
# Fetch and configure HiGHS.
# ---------------------------------------------------------------------------
include(FetchContent)

# Build settings applied to the HiGHS subproject. These are set as cache
# variables before the fetch so that HiGHS picks them up during configuration.
set(BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(FAST_BUILD ON CACHE BOOL "" FORCE)
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(ZLIB OFF CACHE BOOL "" FORCE)

# HiPO is the interior point solver added in HiGHS 1.15. It requires FAST_BUILD
# and its own OpenBLAS build. NO_AVX512 and NO_AVX2 keep the OpenBLAS kernels
# portable across the range of CPUs that the prebuilt wheels will run on.
# NO_AVX2 also works around a manylinux GCC 14 compile failure: its AVX2/FMA
# kernels fail with "inlining failed in call to 'always_inline'
# '_mm256_fmadd_ps': target specific option mismatch" when OpenBLAS's x86_64
# generic kernel is built under that compiler.
#
# BUILD_SHARED_EXTRAS_LIB must be OFF. HiGHS places the HiPO numerical
# dependencies (AMD, BLAS, METIS, RCM) in a separate highs_extras library. When
# that library is shared, HiGHS loads it at runtime from a highs_extras.dll that
# would have to be shipped alongside the wheel. Building it static instead links
# the HiPO code directly into our extension, so HiGHS uses its built in path and
# the wheel stays fully self contained.
set(HIPO ON CACHE BOOL "" FORCE)
set(BUILD_OPENBLAS ON CACHE BOOL "" FORCE)
set(NO_AVX512 ON CACHE BOOL "" FORCE)
set(NO_AVX2 ON CACHE BOOL "" FORCE)
set(BUILD_SHARED_EXTRAS_LIB OFF CACHE BOOL "" FORCE)

FetchContent_Declare(
  highs
  GIT_REPOSITORY https://github.com/ERGO-Code/HiGHS.git
  GIT_TAG v1.15.1
  GIT_SHALLOW ON)
FetchContent_MakeAvailable(highs)

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

# The C API header lives in the highs/interfaces directory of the source tree.
target_include_directories(_core PRIVATE "${highs_SOURCE_DIR}/highs")

# Link against the HiGHS static library target exported by the subproject.
target_link_libraries(_core PRIVATE highs::highs)

# Install the compiled module next to the Python sources inside the package.
install(TARGETS _core DESTINATION cyhighs)
