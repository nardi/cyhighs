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

Wheels are published for CPython 3.11 through 3.14 on Linux, macOS, and Windows.
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

The project uses [uv](https://docs.astral.sh/uv/) for development. Cloning the
repository and running a sync builds the extension from source, including HiGHS.

```bash
git clone https://github.com/nardi/cyhighs
cd cyhighs
uv sync
```

The first build compiles HiGHS and can take several minutes. Later builds reuse
the compiled output and are much faster.
