# Installation

## From a wheel

The recommended way to install `cyhighs` is from a prebuilt wheel with pip.

```bash
pip install cyhighs
```

The wheels bundle HiGHS, as described in
[How HiGHS is bundled](bundling.md), so this single command gives you a working
solver with no further setup. The only runtime dependencies are NumPy and SciPy,
which pip installs for you.

Wheels are published for CPython 3.11 through 3.14 on:

- **Linux** x86_64 and aarch64, as `manylinux_2_28` (glibc 2.28 or newer, for
  example CentOS/RHEL 8, Debian 10+, Ubuntu 18.10+) and `musllinux_1_2` (Alpine
  and other musl distros).
- **macOS** on Apple Silicon (arm64).
- **Windows** on x86_64.

If a matching wheel exists for your platform, pip uses it and no compiler is
needed.

### Using Intel MKL instead of the bundled OpenBLAS

By default, on Linux and Windows, the wheel's HiPO interior-point solver runs
on a bundled OpenBLAS, so there is nothing further to install. On macOS, HiPO
always uses Apple's Accelerate framework instead, and the rest of this section
does not apply there.

If you have Intel MKL available on Linux or Windows and want HiGHS to use it
instead of the bundled OpenBLAS, install the optional extra:

```bash
pip install cyhighs[mkl]
```

This takes effect automatically the next time `cyhighs` is imported, with no
rebuild. See [How HiGHS is bundled](bundling.md) for how the switch works.

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
for a platform without a published wheel, you need a C compiler. Meson and
Ninja are pulled in automatically as build dependencies, so you do not have to
install them yourself.

The build never compiles HiGHS or HiPO. It links prebuilt HiGHS, libblastrampoline,
and OpenBLAS binaries instead, and needs network access to fetch them (see
[How HiGHS is bundled](bundling.md)).

The project uses [uv](https://docs.astral.sh/uv/) for development. Cloning the
repository and running a sync builds the extension.

```bash
git clone https://github.com/nardi/cyhighs
cd cyhighs
uv sync
```
