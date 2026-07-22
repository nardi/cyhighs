# cyhighs

Cython bindings to the [HiGHS](https://highs.dev) linear and mixed integer
optimization solver. The solver is bundled as a prebuilt binary, so an
installed wheel has no external system dependencies beyond NumPy and SciPy.

`cyhighs` provides three interfaces at increasing levels of convenience. You can
hand the solver raw arrays, pass SciPy sparse matrices, or call a drop in
replacement for `scipy.optimize.linprog`.

## Installation

```bash
pip install cyhighs
```

## Documentation

Full documentation, including a user guide and the API reference, lives at
[nardi.github.io/cyhighs](https://nardi.github.io/cyhighs/).

There you will find a description of what the package is for, how it bundles the
HiGHS solver, an installation guide, and worked examples for each of the three
solver interfaces.
