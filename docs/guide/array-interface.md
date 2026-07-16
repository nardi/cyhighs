# Array interface

[`solve_linear_problem`][cyhighs.solve_linear_problem] is the lowest level
interface. You give it the problem as NumPy arrays and it maps them almost
directly onto the HiGHS C API. This page builds up a full example. Each code
block continues from the one before it, so you can read the page as a single
script.

## The constraint matrix

The constraint matrix is passed in compressed sparse column form. Instead of a
dense two dimensional array, you supply three one dimensional arrays.

- `constraint_matrix_values` holds the nonzero entries, read column by column.
- `constraint_matrix_row_indices` holds the row index of each of those entries.
- `constraint_matrix_column_pointers` holds, for each column, where that column
  starts in the values array. It has one more entry than there are columns, and
  its last entry is the total number of stored values.

Consider the matrix with rows `[3, 1]` and `[2, 5]`. Reading down its two
columns gives the values `[3, 2, 1, 5]`, the row indices `[0, 1, 0, 1]`, and the
column pointers `[0, 2, 4]`. Reading the same matrix across its rows instead
would give `[3, 1, 2, 5]`, a different order, which is the whole point of the
column form. It records the entries column by column, not row by row.

We will minimize `-x - 2y`, which is the same as maximizing `x + 2y`, subject to
`3x + y <= 5` and `2x + 5y <= 12`, with both variables at least zero.

```python
import numpy as np

from cyhighs import ModelStatus, solve_linear_problem

values = np.array([3.0, 2.0, 1.0, 5.0])
row_indices = np.array([0, 1, 0, 1])
column_pointers = np.array([0, 2, 4])

solution = solve_linear_problem(
    objective_coefficients=np.array([-1.0, -2.0]),
    constraint_matrix_values=values,
    constraint_matrix_row_indices=row_indices,
    constraint_matrix_column_pointers=column_pointers,
    constraint_lower_bounds=np.array([-np.inf, -np.inf]),
    constraint_upper_bounds=np.array([5.0, 12.0]),
    variable_lower_bounds=np.array([0.0, 0.0]),
    variable_upper_bounds=np.array([np.inf, np.inf]),
)
```

## Reading the solution

An inequality row `A_i @ x <= b_i` is written with a lower bound of negative
infinity and an upper bound of `b_i`, which is what the two constraint bound
arrays above express. The result is a
[`LinearProblemSolution`][cyhighs.LinearProblemSolution].

```{.python continuation}
assert solution.model_status == ModelStatus.OPTIMAL
assert solution.is_optimal

np.testing.assert_allclose(solution.column_values, [1.0, 2.0])
assert solution.objective_value == -5.0

# The row values are the left hand sides at the solution, so both constraints
# are tight here.
np.testing.assert_allclose(solution.row_values, [5.0, 12.0])
```

## Equality constraints

An equality row uses the same lower and upper bound. To pin `x` to the value 1,
add a row `[1, 0]` with both bounds set to 1. We extend the matrix with that
third row. Its single nonzero entry sits in column 0, so it appends a `1.0` to
column 0 and nothing to column 1. The values array becomes `[3, 2, 1, 1, 5]`,
where the third `1` is the new equality entry in column 0.

```{.python continuation}
values = np.array([3.0, 2.0, 1.0, 1.0, 5.0])
row_indices = np.array([0, 1, 2, 0, 1])
column_pointers = np.array([0, 3, 5])

solution = solve_linear_problem(
    objective_coefficients=np.array([-1.0, -2.0]),
    constraint_matrix_values=values,
    constraint_matrix_row_indices=row_indices,
    constraint_matrix_column_pointers=column_pointers,
    constraint_lower_bounds=np.array([-np.inf, -np.inf, 1.0]),
    constraint_upper_bounds=np.array([5.0, 12.0, 1.0]),
    variable_lower_bounds=np.array([0.0, 0.0]),
    variable_upper_bounds=np.array([np.inf, np.inf]),
)

np.testing.assert_allclose(solution.column_values, [1.0, 2.0])
```

## Integer variables

To require a variable to be integer, pass an `integrality` array using
[`VariableType`][cyhighs.VariableType] values. When any variable is integer, the
problem is solved as a mixed integer program and the dual and row value fields of
the result are set to `None`.

```{.python continuation}
from cyhighs import VariableType

solution = solve_linear_problem(
    objective_coefficients=np.array([-1.0, -2.0]),
    constraint_matrix_values=np.array([3.0, 2.0, 1.0, 5.0]),
    constraint_matrix_row_indices=np.array([0, 1, 0, 1]),
    constraint_matrix_column_pointers=np.array([0, 2, 4]),
    constraint_lower_bounds=np.array([-np.inf, -np.inf]),
    constraint_upper_bounds=np.array([5.0, 12.0]),
    variable_lower_bounds=np.array([0.0, 0.0]),
    variable_upper_bounds=np.array([np.inf, np.inf]),
    integrality=np.array([VariableType.INTEGER, VariableType.INTEGER]),
)

assert solution.is_optimal
assert solution.row_values is None
```

## Solver options

Options are supplied as a mapping from [`HighsOption`][cyhighs.HighsOption] to a
value. A common one is to silence the solver log.

```{.python continuation}
from cyhighs import HighsOption

solution = solve_linear_problem(
    objective_coefficients=np.array([-1.0, -2.0]),
    variable_lower_bounds=np.array([0.0, 0.0]),
    variable_upper_bounds=np.array([4.0, 2.0]),
    options={HighsOption.OUTPUT_FLAG: False, HighsOption.TIME_LIMIT: 30.0},
)

# With no constraints, each variable goes to the bound that helps the objective.
np.testing.assert_allclose(solution.column_values, [4.0, 2.0])
```

This last example also shows that the constraint matrix is optional. With no
matrix given, the problem is a pure bound constrained optimization.
