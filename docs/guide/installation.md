# Installation

## From a wheel

The recommended way to install `cyhighs` is from a prebuilt wheel with pip.

```bash
pip install cyhighs
```

The wheels bundle HiGHS statically, as described in
[How HiGHS is bundled](bundling.md), so this single command gives you a working
solver with no further setup. The only runtime dependencies are NumPy and SciPy,
which pip installs for you.

Wheels are published for CPython 3.11 through 3.14 on:

- **Linux** x86_64 and aarch64 — built against a recent glibc, so they require
  **glibc 2.38 or newer** (for example Ubuntu 24.04+, Debian 13+, Fedora 39+).
  Older distributions and musl-based distributions (such as Alpine) are not
  covered by a wheel and need a source build.
- **macOS** on Apple Silicon (arm64).
- **Windows** on x86_64.

If a matching wheel exists for your platform, pip uses it and no compiler is
needed.

## Verifying the install

After installing, you can check that the extension imports and that the solver
is linked in.

```python
import cyhighs

print(cyhighs.highs_version())
assert cyhighs.highs_version().startswith("1.15")
```

## From source

If you want to build from source, for example to develop the package or to build
for a platform without a published wheel, you need a C and C++ compiler. CMake
and Ninja are pulled in automatically as build dependencies, so you do not have
to install them yourself.

Rather than compiling HiGHS, the build downloads the official prebuilt HiGHS
release archive for your platform and links it in, so it is quick and needs
network access at build time. Because the prebuilt Linux archive targets a
recent glibc, a source build on Linux also requires **glibc 2.38 or newer**.

The project uses [uv](https://docs.astral.sh/uv/) for development. Cloning the
repository and running a sync builds the extension.

```bash
git clone https://github.com/nardi/cyhighs
cd cyhighs
uv sync
```

### Building offline or from a local archive

If you already have the HiGHS `static-apache` archive for your platform (or want
to avoid the download), point the build at it with the `HIGHS_ARCHIVE` CMake
variable and no download happens:

```bash
pip wheel . -C cmake.define.HIGHS_ARCHIVE=/path/to/highs-1.15.1-x86_64-linux-gnu-static-apache.tar.gz
```
