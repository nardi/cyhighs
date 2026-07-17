# How HiGHS is bundled

A binding to a C++ library usually forces a choice on its users. Either they
install the library themselves and hope the version matches, or the binding
ships a copy. `cyhighs` takes the second path and makes it invisible. HiGHS is
linked statically into the extension, so a `cyhighs` wheel already contains the
solver. There is no separate HiGHS to install and no system package to keep in
sync.

## The build

The build is driven by
[scikit-build-core](https://scikit-build-core.readthedocs.io/), which runs a
CMake build behind the standard Python packaging interface. CMake compiles
HiGHS and HiPO from source (via `FetchContent`) at a pinned version, currently
1.15.1, on every platform. Because the version is pinned, every wheel is built
against a known solver, and the Python enumerations in `cyhighs` are
transcribed from that same release.

The Cython source is transpiled to C and compiled against the HiGHS headers.
The binding deliberately avoids the NumPy C API. It moves array data across the
boundary using typed memoryviews and the buffer protocol only, which keeps the
compiled surface small and the dependency on NumPy loose.

## The BLAS backend: libblastrampoline

HiPO, HiGHS's interior-point solver, needs a BLAS/LAPACK implementation. On
Linux and Windows, instead of linking one directly, `cyhighs` links HiGHS
against
[libblastrampoline](https://github.com/JuliaLinearAlgebra/libblastrampoline)
(lbt). This is a small shared library, originally built for the Julia
ecosystem, that implements the standard BLAS/LAPACK ABI and forwards every
call, at runtime, to whichever real implementation lbt has been pointed at.
Once the compiled extension (and therefore lbt) is loaded, `cyhighs`'s own
`__init__.py` calls lbt's `lbt_forward` C API to register a backend:

- by default, a prebuilt OpenBLAS bundled inside the wheel, so installing
  `cyhighs` still gives you a fully working solver with no configuration and no
  external dependencies
- Intel MKL instead, if the optional `cyhighs[mkl]` extra is installed and
  MKL's runtime library can be found

Because the switch happens at import time rather than at compile time, going
from the bundled OpenBLAS to MKL (or back) never requires reinstalling
`cyhighs`. If the `LBT_DEFAULT_LIBS` environment variable is already set when
`cyhighs` is imported, it is left alone, so you can also point HiGHS at any
other lbt-compatible BLAS build yourself.

CMake never compiles OpenBLAS itself. Both lbt and the bundled OpenBLAS are
fetched as prebuilt binaries and verified against pinned checksums, the same
way the HiGHS source is fetched at a pinned version. lbt comes from
JuliaBinaryWrappers' releases on every platform. The bundled OpenBLAS comes
from conda-forge, except on the portable `musllinux_1_2` (Alpine) Linux
wheels, where conda-forge has no build to offer and Alpine's own OpenBLAS
package is used instead.

On macOS, none of this applies. HiGHS links directly against Apple's
Accelerate framework there, which ships with every macOS system, so lbt has
nothing to forward and the `cyhighs[mkl]` extra has no effect (Intel has also
never published MKL for macOS anyway).

### Choosing a backend explicitly

By default `cyhighs` prefers MKL when it can find it and falls back to the
bundled OpenBLAS otherwise. Two environment variables let you override this,
read once when `cyhighs` is imported.

`CYHIGHS_LBT_PREFER` picks a backend explicitly instead of relying on the
default preference. Set it to `mkl` to prefer MKL, falling back to OpenBLAS if
MKL cannot be found, the same as the default. Set it to `openblas` to force
the bundled OpenBLAS even if the `cyhighs[mkl]` extra is installed.

`CYHIGHS_LBT_DEBUG` prints diagnostic information to stderr during backend
selection, including which backend was found, whether lbt itself was located,
and the result of the `lbt_forward` call. Set it to any non-empty value to
enable it. This is useful for confirming which backend is active or for
diagnosing why HiPO has no backend at all.

## Platform coverage

Wheels are published for Linux x86_64 and aarch64, macOS on Apple Silicon, and
Windows on x86_64. There are no 32-bit wheels, since HiGHS is not viable on
32-bit targets. The `cyhighs[mkl]` extra is only available on Linux x86_64 and
Windows x86_64, since Intel does not publish MKL for macOS or for any ARM
target.

## Licensing

Because the bundled build includes HiPO, which carries Apache-licensed
dependencies, `cyhighs` is released under the Apache License 2.0. The upstream
HiGHS license and notices are included in the wheels for attribution.
libblastrampoline is MIT licensed, and the bundled OpenBLAS is BSD licensed.
Both are dynamically linked, and neither imposes further obligations on
`cyhighs` itself.

## What this means for you

Because HiGHS is statically linked and the BLAS backend it needs is bundled
alongside it, installing `cyhighs` gives you a working solver immediately, with
nothing further to install. You can confirm which HiGHS version you have by
asking the library directly.

```python
from cyhighs import highs_version

version = highs_version()
print(version)
assert version.startswith("1.15")
```

The same is true of the infinity threshold HiGHS uses to mean unbounded. It is
read from the linked library, so it always matches the compiled solver.

```python
from cyhighs import highs_infinity

assert highs_infinity() >= 1e30
```

Any bound at or beyond this magnitude is treated as unbounded, so you can pass
`float("inf")` for a free bound and the library will map it onto this value for
you.
