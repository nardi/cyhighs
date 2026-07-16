---
icon: lucide/house
---

# cyhighs

`cyhighs` is a Python package that provides Cython bindings to
[HiGHS](https://highs.dev/), the high performance solver for linear programming
and mixed integer programming. It compiles HiGHS from source and links it
statically, so an installed wheel carries the solver with it and needs no
external system libraries.

The package exposes three interfaces at increasing levels of convenience. You
can hand the solver raw arrays, you can pass SciPy sparse matrices, or you can
call a drop in replacement for `scipy.optimize.linprog`. All three run the same
underlying solver, so you can pick the one that fits your code and move between
them as your needs change.

Here is the shortest way to solve a problem. It maximizes `x + 2y` subject to
`x + y <= 4` and `x + 3y <= 6`, with both variables between 0 and 10.

```python
from cyhighs import linprog

result = linprog(
    c=[-1.0, -2.0],
    A_ub=[[1.0, 1.0], [1.0, 3.0]],
    b_ub=[4.0, 6.0],
    bounds=(0, 10),
)

assert result.success
print(result.x, result.fun)
```

The objective is negated because `linprog` minimizes, which is the SciPy
convention. The solver returns `x = [3, 1]` with an objective of `-5`, so the
maximum of `x + 2y` is `5`.

## Where to go next

- [What is cyhighs](guide/what-is-cyhighs.md) explains the problem the package
  solves and how its three interfaces relate.
- [How HiGHS is bundled](guide/bundling.md) describes the build and why wheels
  need no extra dependencies.
- [Installation](guide/installation.md) covers installing from a wheel and
  building from source.
- The [API Reference](reference/index.md) documents every public function and
  enumeration.
