"""The main array based solving interface and its input validation.

This module hosts [`solve_linear_problem`][cyhighs.solve_linear_problem], the
primary Python entry point. It accepts the problem as plain NumPy arrays,
validates and coerces them to the exact dtypes the compiled core requires,
merges the separate inequality and equality constraint matrices into the single
row bounded structure that HiGHS expects, calls the core, and packages the raw
results into a [`LinearProblemSolution`][cyhighs.LinearProblemSolution].

The constraint matrices are supplied in compressed sparse column (CSC) form as
three arrays each: values, row indices, and column pointers. This matches the
memory layout HiGHS consumes, so no transpose or format conversion is needed.
"""

from __future__ import annotations

import numpy as np

from . import _core
from .enumerations import ModelStatus, ObjectiveSense
from .options import build_option_settings
from .result import LinearProblemSolution

# The value HiGHS uses for infinity. Any bound at or beyond this magnitude is
# treated as unbounded. Queried once from the linked library so that it always
# matches the compiled solver.
HIGHS_INFINITY: float = _core.highs_infinity()


def _as_float64_array(array, name: str) -> np.ndarray:
    """Coerce an input to a contiguous one dimensional float64 array.

    Any infinite values are clamped to the HiGHS infinity magnitude so that the
    solver interprets them as unbounded.
    """
    coerced = np.ascontiguousarray(array, dtype=np.float64)
    if coerced.ndim != 1:
        raise ValueError(f"{name} must be one dimensional, got {coerced.ndim} dimensions")
    # Map plus and minus infinity onto the HiGHS sentinel value.
    np.clip(coerced, -HIGHS_INFINITY, HIGHS_INFINITY, out=coerced)
    return coerced


def _as_index_array(array, name: str) -> np.ndarray:
    """Coerce an input to a contiguous one dimensional int32 index array.

    Raises if any value does not fit in a signed 32 bit integer, which is the
    index width of the default HiGHS build.
    """
    coerced = np.ascontiguousarray(array)
    if coerced.ndim != 1:
        raise ValueError(f"{name} must be one dimensional, got {coerced.ndim} dimensions")
    as_int64 = coerced.astype(np.int64, copy=False)
    if as_int64.size and (
        as_int64.min() < np.iinfo(np.int32).min or as_int64.max() > np.iinfo(np.int32).max
    ):
        raise ValueError(f"{name} contains values that do not fit in a 32 bit integer")
    return np.ascontiguousarray(as_int64, dtype=np.int32)


def _validate_csc_block(
    values,
    row_indices,
    column_pointers,
    number_of_columns: int,
    number_of_rows: int,
    label: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Validate and coerce one CSC constraint block.

    Returns the coerced `(values, row_indices, column_pointers)` triple. The
    column pointer array must have length `number_of_columns + 1` and its final
    entry must equal the number of stored values.
    """
    coerced_values = _as_float64_array(values, f"{label} values")
    coerced_indices = _as_index_array(row_indices, f"{label} row indices")
    coerced_pointers = _as_index_array(column_pointers, f"{label} column pointers")

    if coerced_pointers.shape[0] != number_of_columns + 1:
        raise ValueError(
            f"{label} column pointers must have length {number_of_columns + 1}, "
            f"got {coerced_pointers.shape[0]}"
        )
    if coerced_values.shape[0] != coerced_indices.shape[0]:
        raise ValueError(
            f"{label} values and row indices must have equal length, got "
            f"{coerced_values.shape[0]} and {coerced_indices.shape[0]}"
        )
    if coerced_pointers[-1] != coerced_values.shape[0]:
        raise ValueError(
            f"{label} column pointers final entry must equal the number of stored values"
        )
    if coerced_indices.size and (
        coerced_indices.min() < 0 or coerced_indices.max() >= number_of_rows
    ):
        raise ValueError(f"{label} row indices must lie in the range [0, {number_of_rows})")
    return coerced_values, coerced_indices, coerced_pointers


def _matrix_block_given(values, row_indices, column_pointers) -> bool:
    """Return whether a CSC matrix block was supplied, checking consistency.

    All three arrays must be given together or all omitted. A partial block is an
    error.
    """
    present = [component is not None for component in (values, row_indices, column_pointers)]
    if all(present):
        return True
    if not any(present):
        return False
    raise ValueError(
        "The constraint matrix requires all of values, row indices and column "
        "pointers to be given together"
    )


def solve_linear_problem(
    objective_coefficients,
    *,
    constraint_matrix_values=None,
    constraint_matrix_row_indices=None,
    constraint_matrix_column_pointers=None,
    constraint_lower_bounds=None,
    constraint_upper_bounds=None,
    variable_lower_bounds=None,
    variable_upper_bounds=None,
    integrality=None,
    initial_column_values=None,
    objective_sense: ObjectiveSense | int = ObjectiveSense.MINIMIZE,
    options=None,
) -> LinearProblemSolution:
    """Solve `minimize c @ x` subject to linear constraints and bounds.

    This is the thin low level interface. It maps almost one to one onto the
    HiGHS C API, so the constraint matrix must already be a single matrix in
    compressed sparse column form together with per row lower and upper bounds.
    The problem solved is:

    ```text
    optimize   objective_coefficients @ x
    subject to constraint_lower_bounds <= A @ x <= constraint_upper_bounds
               variable_lower_bounds <= x <= variable_upper_bounds
    ```

    Inequality and equality constraints are both expressed through the row
    bounds. An inequality row `A_i @ x <= b_i` uses a lower bound of negative
    infinity and an upper bound of `b_i`, while an equality row uses equal
    lower and upper bounds. The convenience wrapper
    [`solve_linear_problem_sparse`][cyhighs.solve_linear_problem_sparse] builds
    this merged form from separate inequality and equality matrices.

    Args:
        objective_coefficients: The objective coefficient vector `c` of length
            `number_of_columns`.
        constraint_matrix_values: The `A` matrix stored values in CSC form.
        constraint_matrix_row_indices: The `A` matrix row indices in CSC form.
        constraint_matrix_column_pointers: The `A` matrix column pointers in CSC
            form. The three constraint matrix arrays must be given together, or
            all omitted for a problem with no constraints.
        constraint_lower_bounds: Per row lower bounds. Required when the
            constraint matrix is given.
        constraint_upper_bounds: Per row upper bounds. Required when the
            constraint matrix is given, and must match the lower bounds length.
        variable_lower_bounds: Per variable lower bounds. Default to negative
            infinity, meaning free below.
        variable_upper_bounds: Per variable upper bounds. Default to positive
            infinity, meaning free above.
        integrality: Per variable integrality using
            [`VariableType`][cyhighs.VariableType] values. When omitted the
            problem is solved as a pure linear program.
        initial_column_values: A warm start solution for the variables.
        objective_sense: Whether to minimize (default) or maximize the objective.
        options: Solver options as a mapping from
            [`HighsOption`][cyhighs.HighsOption] to a value.

    Returns:
        The [`LinearProblemSolution`][cyhighs.LinearProblemSolution] record.
    """
    objective_coefficients = _as_float64_array(objective_coefficients, "objective_coefficients")
    number_of_columns = objective_coefficients.shape[0]

    # ----- Variable bounds -----
    if variable_lower_bounds is None:
        lower_bounds = np.full(number_of_columns, -HIGHS_INFINITY, dtype=np.float64)
    else:
        lower_bounds = _as_float64_array(variable_lower_bounds, "variable_lower_bounds")
    if variable_upper_bounds is None:
        upper_bounds = np.full(number_of_columns, HIGHS_INFINITY, dtype=np.float64)
    else:
        upper_bounds = _as_float64_array(variable_upper_bounds, "variable_upper_bounds")
    for bound_array, bound_name in (
        (lower_bounds, "variable_lower_bounds"),
        (upper_bounds, "variable_upper_bounds"),
    ):
        if bound_array.shape[0] != number_of_columns:
            raise ValueError(f"{bound_name} must have length {number_of_columns}")

    # ----- Constraint matrix and row bounds -----
    matrix_given = _matrix_block_given(
        constraint_matrix_values,
        constraint_matrix_row_indices,
        constraint_matrix_column_pointers,
    )
    if matrix_given:
        if constraint_lower_bounds is None or constraint_upper_bounds is None:
            raise ValueError(
                "constraint_lower_bounds and constraint_upper_bounds are required "
                "when the constraint matrix is given"
            )
        row_lower_bounds = _as_float64_array(constraint_lower_bounds, "constraint_lower_bounds")
        row_upper_bounds = _as_float64_array(constraint_upper_bounds, "constraint_upper_bounds")
        if row_lower_bounds.shape[0] != row_upper_bounds.shape[0]:
            raise ValueError(
                "constraint_lower_bounds and constraint_upper_bounds must have equal length"
            )
        number_of_rows = row_lower_bounds.shape[0]
        matrix_values, matrix_indices, matrix_pointers = _validate_csc_block(
            constraint_matrix_values,
            constraint_matrix_row_indices,
            constraint_matrix_column_pointers,
            number_of_columns,
            number_of_rows,
            "constraint matrix",
        )
    else:
        row_lower_bounds = np.empty(0, dtype=np.float64)
        row_upper_bounds = np.empty(0, dtype=np.float64)
        matrix_values = np.empty(0, dtype=np.float64)
        matrix_indices = np.empty(0, dtype=np.int32)
        matrix_pointers = np.zeros(number_of_columns + 1, dtype=np.int32)

    # ----- Integrality -----
    if integrality is None:
        integrality_array = None
    else:
        integrality_array = _as_index_array(integrality, "integrality")
        if integrality_array.shape[0] != number_of_columns:
            raise ValueError(f"integrality must have length {number_of_columns}")

    # ----- Warm start -----
    if initial_column_values is None:
        warm_start_array = None
    else:
        warm_start_array = _as_float64_array(initial_column_values, "initial_column_values")
        if warm_start_array.shape[0] != number_of_columns:
            raise ValueError(f"initial_column_values must have length {number_of_columns}")

    option_settings = build_option_settings(options)

    (
        raw_status,
        column_values,
        objective_value,
        column_dual_values,
        row_dual_values,
        row_values,
        iteration_count,
    ) = _core.solve_linear_problem_core(
        int(objective_sense),
        0.0,
        objective_coefficients,
        lower_bounds,
        upper_bounds,
        row_lower_bounds,
        row_upper_bounds,
        matrix_pointers,
        matrix_indices,
        matrix_values,
        integrality_array,
        warm_start_array,
        option_settings,
    )

    # Dual and row information is not meaningful for mixed integer problems.
    is_mixed_integer = integrality_array is not None
    return LinearProblemSolution(
        model_status=ModelStatus(raw_status),
        column_values=column_values,
        objective_value=objective_value,
        column_dual_values=None if is_mixed_integer else column_dual_values,
        row_dual_values=None if is_mixed_integer else row_dual_values,
        row_values=None if is_mixed_integer else row_values,
        simplex_iteration_count=iteration_count,
    )
