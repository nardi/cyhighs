# linprog interface

[`linprog`][cyhighs.linprog] mirrors `scipy.optimize.linprog`'s signature, so
an existing SciPy call keeps working after you change only the import and
adjust how the result is read (see below). Each code block on this page
continues from the one before it.

## A first solve

You pass the objective `c`, the inequality matrix `A_ub` with its right hand side
`b_ub`, and optionally the equality matrix `A_eq` with `b_eq`. Matrices may be
dense or SciPy sparse. The result is an [`OptimizeResult`][cyhighs.OptimizeResult],
which carries the same field names as SciPy's own `OptimizeResult`.

```python
from cyhighs import linprog

result = linprog(
    c=[-1.0, -2.0],
    A_ub=[[1.0, 1.0], [1.0, 3.0]],
    b_ub=[4.0, 6.0],
    bounds=(0, None),
)

assert result.status == 0
assert result.success
print(result.x, result.fun)
```

The result carries the fields SciPy callers expect. `x` is the solution, `fun`
is the objective value, `slack` is the room left in each inequality, `con` is the
equality residual, and `status`, `success`, `message`, and `nit` describe the
outcome. Unlike SciPy's own `OptimizeResult`, there is also a `highs_solution`
field with the full [`LinearProblemSolution`][cyhighs.LinearProblemSolution]
HiGHS returned, which carries extra detail such as the presolved problem size:

```{.python continuation}
print(result.highs_solution.presolved_num_rows, result.highs_solution.presolved_num_columns)
```

## Matching SciPy

Because the interface matches SciPy, you can compare the two directly. HiGHS is
in fact the default method behind `scipy.optimize.linprog`, so the answers agree.

```{.python continuation}
from scipy.optimize import linprog as scipy_linprog
import numpy as np

reference = scipy_linprog(
    c=[-1.0, -2.0],
    A_ub=[[1.0, 1.0], [1.0, 3.0]],
    b_ub=[4.0, 6.0],
    bounds=(0, None),
)

np.testing.assert_allclose(result.x, reference.x)
np.testing.assert_allclose(result.fun, reference.fun)
```

## Bounds

Bounds follow the SciPy convention. Passing `None` gives the default of `(0, None)`
for every variable. A single `(low, high)` pair applies to all variables. A
sequence of pairs sets each variable individually, and a `None` inside a pair
means unbounded in that direction.

```{.python continuation}
result = linprog(
    c=[-1.0, -2.0],
    A_ub=[[1.0, 1.0], [1.0, 3.0]],
    b_ub=[4.0, 6.0],
    bounds=[(0, 2), (0, 5)],
)

# The first variable is now capped at 2.
assert result.x[0] <= 2.0 + 1e-9
```

## Warm starting

Unlike SciPy, `linprog` here wires the `x0` argument to the HiGHS warm start, so
an initial guess is actually used. Passing a known solution still returns that
solution.

```{.python continuation}
result = linprog(
    c=[-1.0, -2.0],
    A_ub=[[1.0, 1.0], [1.0, 3.0]],
    b_ub=[4.0, 6.0],
    bounds=(0, None),
    x0=[3.0, 1.0],
)

assert result.success
np.testing.assert_allclose(result.x, [3.0, 1.0])
```

## Integer variables and status codes

Pass `integrality` to require integer variables, using the same convention as
SciPy where `1` marks an integer variable. The status codes also follow SciPy,
where `0` is success, `2` is infeasible, and `3` is unbounded. The next example
is infeasible, since it asks for a variable that is at least 5 while also being
at most 4.

```{.python continuation}
result = linprog(
    c=[1.0],
    A_ub=[[1.0]],
    b_ub=[4.0],
    bounds=[(5, None)],
    integrality=[1],
)

assert result.status == 2
assert not result.success
```
