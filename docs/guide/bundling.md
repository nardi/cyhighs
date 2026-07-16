# How HiGHS is bundled

A binding to a C++ library usually forces a choice on its users. Either they
install the library themselves and hope the version matches, or the binding
ships a copy. `cyhighs` takes the second path and makes it invisible. HiGHS is
compiled from source and linked statically into the extension, so a `cyhighs`
wheel already contains the solver. There is no separate HiGHS to install and no
system package to keep in sync.

## The build

The build is driven by
[scikit-build-core](https://scikit-build-core.readthedocs.io/), which runs a
CMake build behind the standard Python packaging interface. CMake uses its
`FetchContent` feature to download HiGHS at a pinned version, currently 1.15.1,
and compiles it as part of building the extension. Because the version is
pinned, every wheel is built against a known solver, and the Python enumerations
in `cyhighs` are transcribed from that same release.

The Cython source is transpiled to C and compiled against the freshly built
HiGHS. The binding deliberately avoids the NumPy C API. It moves array data
across the boundary using typed memoryviews and the buffer protocol only, which
keeps the compiled surface small and the dependency on NumPy loose.

The HiPO interior point solver is compiled in as well. That pulls in a bundled
OpenBLAS build, which is why the wheels carry their own linear algebra kernels
and still need nothing from the host system.

## What this means for you

Because everything is static, installing `cyhighs` gives you a working solver
immediately. You can confirm which HiGHS version you have by asking the library
directly.

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
