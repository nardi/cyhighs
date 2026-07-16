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
CMake build behind the standard Python packaging interface. By default, instead
of compiling HiGHS from source, CMake downloads the official prebuilt
**`static-apache`** release archive for the target platform at a pinned version,
currently 1.15.1, verifies it against a pinned checksum, extracts it, and links
the static libraries it ships directly into the extension. Because the version
is pinned, every wheel is built against a known solver, and the Python
enumerations in `cyhighs` are transcribed from that same release.

The one exception is the portable Linux wheels (`manylinux_2_28` and
`musllinux_1_2`). The prebuilt archive is built against a recent glibc and
cannot link inside the older manylinux/musllinux build containers, so for those
wheels CMake compiles HiGHS and HiPO from source at the same pinned version
(`-DCYHIGHS_HIGHS_FROM_SOURCE=ON`), linking a prebuilt OpenBLAS installed in the
container. The result is the same statically bundled solver, just built in place.

The `static-apache` archive already contains the HiPO interior point solver and
its bundled OpenBLAS linear algebra kernels, so the wheels carry their own linear
algebra and still need nothing from the host system. The Cython source is
transpiled to C and compiled against the prebuilt HiGHS headers. The binding
deliberately avoids the NumPy C API. It moves array data across the boundary
using typed memoryviews and the buffer protocol only, which keeps the compiled
surface small and the dependency on NumPy loose.

## Platform coverage

Wheels are published for Linux x86_64 and aarch64, macOS on Apple Silicon, and
Windows on x86_64. On Linux both a `manylinux_2_39` wheel (from the prebuilt
archive, requiring **glibc 2.39 or newer**) and the more portable
`manylinux_2_28` (**glibc 2.28 or newer**) and `musllinux_1_2` (Alpine and other
musl distros) wheels are shipped; pip installs whichever best matches the host.
There are no 32-bit wheels; that platform builds from source instead.

## Licensing

Because the bundled build includes HiPO, which carries Apache-licensed
dependencies, the `static-apache` archive is distributed under the Apache License
2.0, and `cyhighs` is released under the same license. The upstream HiGHS license
and notices are included in the wheels for attribution.

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
