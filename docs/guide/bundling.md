# How HiGHS is bundled

A binding to a C++ library usually forces a choice on its users. Either they
install the library themselves and hope the version matches, or the binding
ships a copy. `cyhighs` takes the second path and makes it invisible. HiGHS is
bundled alongside the extension, so a `cyhighs` wheel already contains the
solver. There is no separate HiGHS to install and no system package to keep in
sync.

## The build

The build is driven by [meson](https://mesonbuild.com/) through the
[meson-python](https://mesonbuild.com/meson-python/) backend. Rather than
compiling HiGHS from source, `cyhighs` links against
[HiGHS_jll](https://github.com/JuliaBinaryWrappers/HiGHS_jll.jl), a prebuilt
binary of HiGHS published for the Julia ecosystem, brought into the Meson
build through [meson-jll](https://nardi.github.io/meson-jll/meson_jll/index.html).
A plain `dependency('HiGHS')` in `meson.build` resolves, at setup time, to
whichever platform tarball matches the host, and meson-python folds the
resulting shared libraries into the wheel. Because the version is pinned by
the JLL release used, every wheel is built against a known solver, and the
Python enumerations in `cyhighs` are transcribed from that same release.

The Cython source is transpiled to C and compiled against the HiGHS headers
that ship inside the JLL tarball. The binding deliberately avoids the NumPy C
API. It moves array data across the boundary using typed memoryviews and the
buffer protocol only, which keeps the compiled surface small and the
dependency on NumPy loose.

## The BLAS backend: libblastrampoline

HiPO, HiGHS's interior-point solver, needs a BLAS/LAPACK implementation.
HiGHS_jll links
[libblastrampoline](https://github.com/JuliaLinearAlgebra/libblastrampoline)
(lbt) for this on every platform, including macOS. lbt is a small shared
library, originally built for the Julia ecosystem, that implements the
standard BLAS/LAPACK ABI and forwards every call, at runtime, to whichever
real implementation lbt has been pointed at. Once the compiled extension (and
therefore lbt) is loaded, `cyhighs`'s own `__init__.py` calls lbt's
`lbt_forward` C API to register the first available backend from this order of
preference:

- Apple's Accelerate framework, on macOS, which ships with the OS and is
  faster there than a bundled OpenBLAS
- Intel MKL, if the optional `cyhighs[mkl]` extra is installed and MKL's
  runtime library can be found
- otherwise a prebuilt OpenBLAS bundled inside the wheel (from
  [OpenBLAS32_jll](https://github.com/JuliaBinaryWrappers/OpenBLAS32_jll.jl),
  the same LP64 build HiGHS.jl itself depends on, and the same way HiGHS
  itself is bundled), so installing `cyhighs` gives you a fully working solver
  with no configuration and no external dependencies

The bundled OpenBLAS ships on every platform, including macOS, so there is
always a working fallback even where Accelerate is the preferred choice.
Because the switch happens at import time rather than at compile time, going
between backends never requires reinstalling `cyhighs`. If the
`LBT_DEFAULT_LIBS` environment variable is already set when `cyhighs` is
imported, it is left alone, so you can also point HiGHS at any other
lbt-compatible BLAS build yourself.

Neither HiGHS, lbt, nor OpenBLAS is compiled by this project. All three are
fetched as prebuilt JLL binaries, covering Linux (including the portable
`musllinux_1_2`/Alpine target), macOS, and Windows alike.

### Choosing a backend explicitly

Two environment variables override the default preference, read once when
`cyhighs` is imported.

`CYHIGHS_LBT_PREFER` moves one backend to the front of the order above. Set it
to `accelerate`, `mkl`, or `openblas`. If the named backend cannot be found
(for example `mkl` without the `cyhighs[mkl]` extra, or `accelerate` off
macOS), selection falls through to the remaining backends in their normal
order.

`CYHIGHS_LBT_DEBUG` prints diagnostic information to stderr during backend
selection, including which backend was chosen and the result of the
`lbt_forward` call. Set it to any non-empty value to enable it. This is useful
for confirming which backend is active or for diagnosing why HiPO has no
backend at all.

## Platform coverage

Wheels are published for Linux x86_64 and aarch64, macOS on Apple Silicon, and
Windows on x86_64. There are no 32-bit wheels, since HiGHS is not viable on
32-bit targets. The `cyhighs[mkl]` extra is only available on Linux x86_64 and
Windows x86_64, since Intel does not publish MKL for macOS or for any ARM
target.

## Licensing

Because the bundled build includes HiPO, which carries Apache-licensed
dependencies, `cyhighs` is released under the Apache License 2.0.
libblastrampoline is MIT licensed, and OpenBLAS is BSD licensed. HiGHS itself
is Apache 2.0 licensed. All three are dynamically linked, and none imposes
further obligations on `cyhighs` itself beyond preserving attribution.

The upstream HiGHS license text ships inside the HiGHS_jll tarball
(`share/licenses/HiGHS/LICENSE.txt`), but the build does not currently copy it
into the wheel automatically. This is a known gap left by the move away from
building HiGHS from a locally fetched source tree, tracked as follow-up work,
not a deliberate omission.

## What this means for you

Because HiGHS is bundled alongside the extension, installing `cyhighs` gives
you a working solver immediately, with nothing further to install. You can
confirm which HiGHS version you have by asking the library directly.

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
