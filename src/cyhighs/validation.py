"""The main array based solving interface and its input validation.

This module hosts :func:`solve_linear_problem`, the primary Python entry point.
It accepts the problem as plain NumPy arrays, validates and coerces them to the
exact dtypes the compiled core requires, merges the separate inequality and
equality constraint matrices into the single row bounded structure that HiGHS
expects, calls the core, and packages the raw results into a
:class:`LinearProblemSolution`.

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

    Returns the coerced ``(values, row_indices, column_pointers)`` triple. The
    column pointer array must have length ``number_of_columns + 1`` and its final
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


def _merge_constraint_matrices(
    number_of_columns: int,
    inequality_values: np.ndarray,
    inequality_indices: np.ndarray,
    inequality_pointers: np.ndarray,
    number_of_inequality_rows: int,
    equality_values: np.ndarray,
    equality_indices: np.ndarray,
    equality_pointers: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Vertically stack two CSC matrices sharing the same columns.

    The equality rows are placed below the inequality rows, so their row indices
    are shifted up by the inequality row count. The merge is fully vectorized.

    Returns the merged ``(values, row_indices, column_pointers)`` triple.
    """
    inequality_counts = np.diff(inequality_pointers)
    equality_counts = np.diff(equality_pointers)
    merged_counts = inequality_counts + equality_counts

    merged_pointers = np.empty(number_of_columns + 1, dtype=np.int32)
    merged_pointers[0] = 0
    np.cumsum(merged_counts, out=merged_pointers[1:])

    total_nonzeros = int(merged_pointers[-1])
    merged_indices = np.empty(total_nonzeros, dtype=np.int32)
    merged_values = np.empty(total_nonzeros, dtype=np.float64)

    # Destination position of every inequality entry. Each entry keeps its
    # position within its column, and columns start at the merged pointer.
    inequality_columns = np.repeat(np.arange(number_of_columns, dtype=np.int64), inequality_counts)
    inequality_destinations = merged_pointers[inequality_columns] + (
        np.arange(inequality_values.shape[0], dtype=np.int64)
        - inequality_pointers[inequality_columns]
    )
    merged_indices[inequality_destinations] = inequality_indices
    merged_values[inequality_destinations] = inequality_values

    # Equality entries follow the inequality entries within each column and have
    # their row indices shifted below the inequality rows.
    equality_columns = np.repeat(np.arange(number_of_columns, dtype=np.int64), equality_counts)
    equality_destinations = (
        merged_pointers[equality_columns]
        + inequality_counts[equality_columns]
        + (
            np.arange(equality_values.shape[0], dtype=np.int64)
            - equality_pointers[equality_columns]
        )
    )
    merged_indices[equality_destinations] = equality_indices + number_of_inequality_rows
    merged_values[equality_destinations] = equality_values

    return merged_values, merged_indices, merged_pointers


def _empty_csc_block(number_of_columns: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return an empty CSC block for a matrix with no rows."""
    return (
        np.empty(0, dtype=np.float64),
        np.empty(0, dtype=np.int32),
        np.zeros(number_of_columns + 1, dtype=np.int32),
    )


def solve_linear_problem(
    objective_coefficients,
    *,
    inequality_matrix_values=None,
    inequality_matrix_row_indices=None,
    inequality_matrix_column_pointers=None,
    inequality_upper_bounds=None,
    equality_matrix_values=None,
    equality_matrix_row_indices=None,
    equality_matrix_column_pointers=None,
    equality_right_hand_sides=None,
    variable_lower_bounds=None,
    variable_upper_bounds=None,
    integrality=None,
    initial_column_values=None,
    objective_sense: ObjectiveSense | int = ObjectiveSense.MINIMIZE,
    options=None,
) -> LinearProblemSolution:
    """Solve ``minimize c @ x`` subject to linear constraints and bounds.

    The problem solved is::

        optimize   objective_coefficients @ x
        subject to A_ub @ x <= inequality_upper_bounds
                   A_eq @ x == equality_right_hand_sides
                   variable_lower_bounds <= x <= variable_upper_bounds

    where ``A_ub`` and ``A_eq`` are supplied in compressed sparse column form.
    Both constraint blocks are optional. Either or both may be omitted, in which
    case the corresponding constraints are absent.

    Parameters
    ----------
    objective_coefficients : array_like
        The objective coefficient vector ``c`` of length ``number_of_columns``.
    inequality_matrix_values, inequality_matrix_row_indices, \
inequality_matrix_column_pointers : array_like, optional
        The inequality constraint matrix ``A_ub`` in CSC form. All three must be
        given together, or all omitted.
    inequality_upper_bounds : array_like, optional
        The right hand side vector ``b_ub``. Required when ``A_ub`` is given.
    equality_matrix_values, equality_matrix_row_indices, \
equality_matrix_column_pointers : array_like, optional
        The equality constraint matrix ``A_eq`` in CSC form. All three must be
        given together, or all omitted.
    equality_right_hand_sides : array_like, optional
        The right hand side vector ``b_eq``. Required when ``A_eq`` is given.
    variable_lower_bounds, variable_upper_bounds : array_like, optional
        Per variable bounds. Default to negative and positive infinity, meaning
        free variables.
    integrality : array_like, optional
        Per variable integrality using :class:`VariableType` values. When omitted
        the problem is solved as a pure linear program.
    initial_column_values : array_like, optional
        A warm start solution for the variables.
    objective_sense : ObjectiveSense or int, optional
        Whether to minimize (default) or maximize the objective.
    options : dict of HighsOption to value, optional
        Solver options.

    Returns
    -------
    LinearProblemSolution
        The solution record.
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

    # ----- Inequality block -----
    inequality_given = _matrix_block_given(
        inequality_matrix_values,
        inequality_matrix_row_indices,
        inequality_matrix_column_pointers,
        "inequality",
    )
    if inequality_given:
        if inequality_upper_bounds is None:
            raise ValueError(
                "inequality_upper_bounds is required when the inequality matrix is given"
            )
        inequality_upper_bounds = _as_float64_array(
            inequality_upper_bounds, "inequality_upper_bounds"
        )
        number_of_inequality_rows = inequality_upper_bounds.shape[0]
        inequality_block = _validate_csc_block(
            inequality_matrix_values,
            inequality_matrix_row_indices,
            inequality_matrix_column_pointers,
            number_of_columns,
            number_of_inequality_rows,
            "inequality matrix",
        )
    else:
        number_of_inequality_rows = 0
        inequality_block = _empty_csc_block(number_of_columns)

    # ----- Equality block -----
    equality_given = _matrix_block_given(
        equality_matrix_values,
        equality_matrix_row_indices,
        equality_matrix_column_pointers,
        "equality",
    )
    if equality_given:
        if equality_right_hand_sides is None:
            raise ValueError(
                "equality_right_hand_sides is required when the equality matrix is given"
            )
        equality_right_hand_sides = _as_float64_array(
            equality_right_hand_sides, "equality_right_hand_sides"
        )
        number_of_equality_rows = equality_right_hand_sides.shape[0]
        equality_block = _validate_csc_block(
            equality_matrix_values,
            equality_matrix_row_indices,
            equality_matrix_column_pointers,
            number_of_columns,
            number_of_equality_rows,
            "equality matrix",
        )
    else:
        number_of_equality_rows = 0
        equality_block = _empty_csc_block(number_of_columns)

    # ----- Merge the two blocks and assemble the row bounds -----
    merged_values, merged_indices, merged_pointers = _merge_constraint_matrices(
        number_of_columns,
        inequality_block[0],
        inequality_block[1],
        inequality_block[2],
        number_of_inequality_rows,
        equality_block[0],
        equality_block[1],
        equality_block[2],
    )

    # Inequality rows are bounded above by b_ub and unbounded below. Equality
    # rows are pinned to b_eq on both sides.
    row_lower_bounds = np.concatenate(
        [
            np.full(number_of_inequality_rows, -HIGHS_INFINITY, dtype=np.float64),
            equality_right_hand_sides if equality_given else np.empty(0, dtype=np.float64),
        ]
    )
    row_upper_bounds = np.concatenate(
        [
            inequality_upper_bounds if inequality_given else np.empty(0, dtype=np.float64),
            equality_right_hand_sides if equality_given else np.empty(0, dtype=np.float64),
        ]
    )

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
        merged_pointers,
        merged_indices,
        merged_values,
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


def _matrix_block_given(values, row_indices, column_pointers, label: str) -> bool:
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
        f"The {label} matrix requires all of values, row indices and column "
        f"pointers to be given together"
    )
