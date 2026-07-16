# Sparse interface

[`solve_linear_problem_sparse`][cyhighs.solve_linear_problem_sparse] accepts
SciPy sparse matrices for the constraints. It keeps the inequality and equality
matrices separate, the way you usually build them, and merges them for you into
the single row bounded form the array interface needs. Each code block on this
page continues from the previous one.

## An inequality only problem

You give the inequality matrix as `A_ub` with its right hand side `b_ub`. The
matrix may be in any SciPy sparse format. Here it is a compressed sparse row
matrix. We solve the same problem as on the array interface page, minimizing
`-x - 2y` subject to `x + y <= 4` and `x + 3y <= 6`.

```python
import numpy as np
from scipy.sparse import csr_matrix

from cyhighs import ModelStatus, solve_linear_problem_sparse

inequality = csr_matrix([[1.0, 1.0], [1.0, 3.0]])

solution = solve_linear_problem_sparse(
    objective_coefficients=[-1.0, -2.0],
    inequality_constraint_matrix=inequality,
    inequality_upper_bounds=[4.0, 6.0],
    variable_lower_bounds=[0.0, 0.0],
    variable_upper_bounds=[np.inf, np.inf],
)

assert solution.model_status == ModelStatus.OPTIMAL
np.testing.assert_allclose(solution.column_values, [3.0, 1.0])
```

Notice that the interface takes plain lists for the vectors. Anything array like
is accepted and converted internally.

## Adding equality constraints

To add equality constraints, pass `A_eq` and `b_eq`. When you supply both an
inequality and an equality matrix, they must share the same sparse format, so the
merge can stay in that format and avoid a conversion. Here both are in coordinate
format. The equality row `[1, 0]` with right hand side `1` pins `x` to 1.

```{.python continuation}
from scipy.sparse import coo_matrix

solution = solve_linear_problem_sparse(
    objective_coefficients=[-1.0, -2.0],
    inequality_constraint_matrix=coo_matrix([[1.0, 1.0], [1.0, 3.0]]),
    inequality_upper_bounds=[4.0, 6.0],
    equality_constraint_matrix=coo_matrix([[1.0, 0.0]]),
    equality_right_hand_sides=[1.0],
    variable_lower_bounds=[0.0, 0.0],
    variable_upper_bounds=[np.inf, np.inf],
)

assert solution.is_optimal
assert solution.column_values[0] == 1.0
```

## Mixing formats is rejected

Because a mixed pairing would force a hidden conversion, it is refused. If you
pass one matrix as compressed sparse row and the other as compressed sparse
column, the call raises a `ValueError`, so the layout decision stays in your
hands.

```{.python continuation}
from scipy.sparse import csc_matrix

try:
    solve_linear_problem_sparse(
        objective_coefficients=[-1.0, -2.0],
        inequality_constraint_matrix=csr_matrix([[1.0, 1.0]]),
        inequality_upper_bounds=[4.0],
        equality_constraint_matrix=csc_matrix([[1.0, 0.0]]),
        equality_right_hand_sides=[1.0],
    )
except ValueError as error:
    print("rejected:", error)
else:
    raise AssertionError("expected a ValueError for the mixed formats")
```

For a fully SciPy compatible calling convention, see the
[linprog interface](linprog-interface.md), which builds on this layer.
