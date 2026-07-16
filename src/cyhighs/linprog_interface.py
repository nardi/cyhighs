"""A near drop in replacement for `scipy.optimize.linprog`.

This wrapper mirrors the SciPy `linprog` signature. It accepts dense or sparse
constraint matrices, translates the SciPy bounds and integrality conventions,
solves through HiGHS, and returns an [`OptimizeResult`][cyhighs.OptimizeResult]
carrying the same field names SciPy callers expect (`x`, `fun`, `slack`, `con`,
`status`, `success`, `message`, `nit`) plus a `highs_solution` field with the
full HiGHS solve result.

The signature adds nothing beyond SciPy except that the standard `x0` argument
is wired to the HiGHS warm start, so an initial solution is actually used.
"""

from __future__ import annotations

import numpy as np

from .enumerations import ModelStatus
from .result import OptimizeResult
from .sparse_interface import solve_linear_problem_sparse

# Translation from HiGHS model status to the integer status codes SciPy linprog
# reports. SciPy uses 0 optimal, 1 iteration or time limit, 2 infeasible,
# 3 unbounded, 4 numerical or other failure.
_SCIPY_STATUS_BY_MODEL_STATUS = {
    ModelStatus.OPTIMAL: 0,
    ModelStatus.ITERATION_LIMIT: 1,
    ModelStatus.TIME_LIMIT: 1,
    ModelStatus.SOLUTION_LIMIT: 1,
    ModelStatus.INFEASIBLE: 2,
    ModelStatus.UNBOUNDED: 3,
    ModelStatus.UNBOUNDED_OR_INFEASIBLE: 3,
}

_SCIPY_MESSAGE_BY_STATUS = {
    0: "Optimization terminated successfully.",
    1: "The iteration or time limit was reached before a solution was found.",
    2: "The problem is infeasible.",
    3: "The problem is unbounded.",
    4: "The solve failed for numerical or other reasons.",
}


def _is_scalar_or_none(value) -> bool:
    """Return True if a value is a scalar number or None."""
    return value is None or np.isscalar(value)


def _pair_to_floats(pair) -> tuple[float, float]:
    """Convert a single bounds pair to floats, mapping None to infinity."""
    lower, upper = pair
    lower_value = -np.inf if lower is None else float(lower)
    upper_value = np.inf if upper is None else float(upper)
    return lower_value, upper_value


def _process_bounds(bounds, number_of_columns: int) -> tuple[np.ndarray, np.ndarray]:
    """Translate the SciPy bounds argument into lower and upper bound arrays.

    Follows the SciPy convention. `None` means the default of `(0, None)` for
    every variable. A single `(min, max)` pair is broadcast to all variables. A
    sequence of pairs sets each variable individually. A `None` inside a pair
    means unbounded in that direction.
    """
    if bounds is None:
        return np.zeros(number_of_columns), np.full(number_of_columns, np.inf)

    bounds_sequence = list(bounds)
    # A single pair is two scalar or None entries.
    if (
        len(bounds_sequence) == 2
        and _is_scalar_or_none(bounds_sequence[0])
        and _is_scalar_or_none(bounds_sequence[1])
    ):
        lower_value, upper_value = _pair_to_floats(bounds_sequence)
        return (
            np.full(number_of_columns, lower_value),
            np.full(number_of_columns, upper_value),
        )

    if len(bounds_sequence) != number_of_columns:
        raise ValueError(
            f"bounds must be a single pair or a sequence of {number_of_columns} "
            f"pairs, got {len(bounds_sequence)} entries"
        )
    lower_bounds = np.empty(number_of_columns)
    upper_bounds = np.empty(number_of_columns)
    for column_index, pair in enumerate(bounds_sequence):
        lower_bounds[column_index], upper_bounds[column_index] = _pair_to_floats(pair)
    return lower_bounds, upper_bounds


def _process_integrality(integrality, number_of_columns: int):
    """Translate the SciPy integrality argument to a per variable array or None.

    A scalar is broadcast to all variables. When every entry is zero, meaning all
    variables are continuous, None is returned so that the pure linear program
    path is used.
    """
    if integrality is None:
        return None
    integrality_array = np.broadcast_to(
        np.asarray(integrality, dtype=np.int32), (number_of_columns,)
    ).copy()
    if not integrality_array.any():
        return None
    return integrality_array


def _as_sparse(matrix):
    """Return a SciPy sparse matrix, or None.

    An already sparse matrix is passed through unchanged so that its format is
    preserved and the sparse wrapper can pick the efficient merge path. A dense
    array like input is converted to CSR, a single consistent format so that two
    dense inputs do not trip the wrapper's mixed format rejection.
    """
    if matrix is None:
        return None
    from scipy.sparse import csr_matrix, issparse

    if issparse(matrix):
        return matrix
    return csr_matrix(matrix)


def linprog(
    c,
    A_ub=None,
    b_ub=None,
    A_eq=None,
    b_eq=None,
    bounds=None,
    method: str = "highs",
    x0=None,
    integrality=None,
    options=None,
):
    """Solve a linear program with a SciPy `linprog` compatible interface.

    Minimizes `c @ x` subject to `A_ub @ x <= b_ub`, `A_eq @ x == b_eq` and
    the given variable bounds. Constraint matrices may be dense array likes or
    SciPy sparse matrices.

    Args:
        c: Coefficients of the linear objective to minimize.
        A_ub: Inequality constraint matrix.
        b_ub: Inequality right hand side.
        A_eq: Equality constraint matrix.
        b_eq: Equality right hand side.
        bounds: Bounds on the variables following the SciPy convention. Defaults
            to `(0, None)` for every variable.
        method: Present for SciPy compatibility. Only HiGHS is used, so this is
            accepted and otherwise ignored.
        x0: A warm start solution, wired to the HiGHS warm start.
        integrality: Per variable integrality using the SciPy convention, which
            matches the [`VariableType`][cyhighs.VariableType] values.
        options: Solver options as a mapping from
            [`HighsOption`][cyhighs.HighsOption] to a value.

    Returns:
        An [`OptimizeResult`][cyhighs.OptimizeResult] with `x`, `fun`, `slack`,
        `con`, `status`, `success`, `message`, `nit` and `highs_solution`
        fields.
    """
    objective_coefficients = np.ascontiguousarray(c, dtype=np.float64)
    number_of_columns = objective_coefficients.shape[0]

    lower_bounds, upper_bounds = _process_bounds(bounds, number_of_columns)
    integrality_array = _process_integrality(integrality, number_of_columns)

    inequality_matrix = _as_sparse(A_ub)
    equality_matrix = _as_sparse(A_eq)

    inequality_upper_bounds = None if b_ub is None else np.ascontiguousarray(b_ub, dtype=np.float64)
    equality_right_hand_sides = (
        None if b_eq is None else np.ascontiguousarray(b_eq, dtype=np.float64)
    )

    solution = solve_linear_problem_sparse(
        objective_coefficients,
        inequality_constraint_matrix=inequality_matrix,
        inequality_upper_bounds=inequality_upper_bounds,
        equality_constraint_matrix=equality_matrix,
        equality_right_hand_sides=equality_right_hand_sides,
        variable_lower_bounds=lower_bounds,
        variable_upper_bounds=upper_bounds,
        integrality=integrality_array,
        initial_column_values=None if x0 is None else np.ascontiguousarray(x0, dtype=np.float64),
        options=options,
    )

    scipy_status = _SCIPY_STATUS_BY_MODEL_STATUS.get(solution.model_status, 4)
    x = solution.column_values

    # Constraint residuals, computed from the original matrices. slack is the
    # amount of room left in each inequality, con is the equality residual.
    if inequality_matrix is not None:
        slack = inequality_upper_bounds - inequality_matrix.dot(x)
    else:
        slack = np.empty(0, dtype=np.float64)
    if equality_matrix is not None:
        con = equality_matrix.dot(x) - equality_right_hand_sides
    else:
        con = np.empty(0, dtype=np.float64)

    return OptimizeResult(
        x=x,
        fun=solution.objective_value,
        slack=slack,
        con=con,
        status=scipy_status,
        success=scipy_status == 0,
        message=_SCIPY_MESSAGE_BY_STATUS[scipy_status],
        nit=solution.simplex_iteration_count,
        highs_solution=solution,
    )
