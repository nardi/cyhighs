# Meson build for the cyhighs Cython extension.
#
# HiGHS + HiPO are consumed as a prebuilt binary via the HiGHS_jll Julia
# package, resolved through meson-jll's generated subprojects/*.wrap files
# (see subprojects/ and meson-jll.lock, committed alongside this file). No
# HiGHS source is compiled: dependency('HiGHS_jll') resolves, at meson setup
# time, to whichever platform tarball matches the host, and returns the
# include directory plus a find_library('highs') result for that platform.
#
# HiPO's BLAS dependency is satisfied the same way libblastrampoline (lbt)
# was before: dependency('HiGHS') pulls libblastrampoline in transitively
# on every platform the JLL publishes, including macOS. Once the compiled
# extension (and therefore lbt) is loaded, cyhighs's own
# src/cyhighs/_blas_backend.py calls lbt's `lbt_forward` C API to register
# a backend, in this order of preference:
#
#   * Apple's Accelerate framework, on macOS, since it ships with the OS and
#     is faster there than a bundled OpenBLAS,
#   * Intel MKL, if the optional `cyhighs[mkl]` extra is installed and its
#     shared library can be located (Linux x86_64 / Windows x86_64 only,
#     Intel has never published MKL for macOS or for ARM),
#   * otherwise the OpenBLAS32_jll bundled below, so cyhighs keeps working
#     with zero configuration and no external dependencies by default.
#
# OpenBLAS32_jll is bundled on every platform so there is always a working
# fallback. It is used in preference to the plain OpenBLAS_jll deliberately:
# it is the same LP64 dependency HiGHS.jl itself uses, and it is what
# HiGHS_jll's own build was tested against.

project(
  'cyhighs',
  'c',
  'cython',
  version: '0.2.2'
)

py = import('python').find_installation(pure: false)

py.extension_module(
  '_core',
  'src/cyhighs/_core.pyx',
  dependencies: [dependency('HiGHS_jll'), dependency('OpenBLAS32_jll')],
  cython_args: ['--3str'],
  subdir: 'cyhighs',
  install: true,
)

py.install_sources(
  [
    'src/cyhighs/__init__.py',
    'src/cyhighs/_blas_backend.py',
    'src/cyhighs/_core.pyi',
    'src/cyhighs/_highs_c_api.pyi',
    'src/cyhighs/enumerations.py',
    'src/cyhighs/linprog_interface.py',
    'src/cyhighs/options.py',
    'src/cyhighs/result.py',
    'src/cyhighs/sparse_interface.py',
    'src/cyhighs/validation.py',
  ],
  subdir: 'cyhighs',
)
