"""Convenience wrapper that accepts SciPy sparse constraint matrices.

This layer takes the inequality and equality constraint matrices as SciPy sparse
matrices, merges them into the single row bounded matrix that the low level
[`solve_linear_problem`][cyhighs.solve_linear_problem] expects, and delegates. The merge picks the
most efficient path for the incoming sparse format. Two matrices already in
compressed sparse column form are merged column wise by a Cython routine, while
matrices in a row oriented format are stacked in that native format and then
converted to CSC once.
"""

from __future__ import annotations

import numpy as np

from . import _core
from .enumerations import ObjectiveSense
from .result import LinearProblemSolution
from .validation import HIGHS_INFINITY, _as_index_array, solve_linear_problem


def _merge_sparse_constraints(inequality_matrix, equality_matrix):
    """Merge the inequality and equality matrices into one CSC matrix.

    Returns a `(values, row_indices, column_pointers, number_of_inequality_rows,
    number_of_equality_rows)` tuple. The row indices place the equality rows
    directly below the inequality rows.

    The merge path depends on the input format. Two CSC matrices are merged by
    the Cython column merge with no format conversion. Two matrices in the same
    row oriented format are stacked natively and converted to CSC once. Two
    matrices in different formats are rejected so that the caller keeps control
    of the layout.
    """
    from scipy.sparse import issparse, vstack

    for matrix, label in (
        (inequality_matrix, "inequality_constraint_matrix"),
        (equality_matrix, "equality_constraint_matrix"),
    ):
        if matrix is not None and not issparse(matrix):
            raise TypeError(f"{label} must be a SciPy sparse matrix, got {type(matrix).__name__}")

    number_of_inequality_rows = 0 if inequality_matrix is None else inequality_matrix.shape[0]
    number_of_equality_rows = 0 if equality_matrix is None else equality_matrix.shape[0]

    # Cases where at most one matrix is present need no merge at all.
    if inequality_matrix is None and equality_matrix is None:
        return None, None, None, 0, 0
    if equality_matrix is None:
        compressed = inequality_matrix.tocsc()
        return (
            compressed.data,
            compressed.indices,
            compressed.indptr,
            number_of_inequality_rows,
            0,
        )
    if inequality_matrix is None:
        compressed = equality_matrix.tocsc()
        return (
            compressed.data,
            compressed.indices,
            compressed.indptr,
            0,
            number_of_equality_rows,
        )

    # Both matrices are present. Reject a mixed format pairing outright.
    if not issparse(inequality_matrix) or not issparse(equality_matrix):
        raise TypeError("Both constraint matrices must be SciPy sparse matrices")
    if inequality_matrix.format != equality_matrix.format:
        raise ValueError(
            "The inequality and equality matrices must share the same sparse "
            f"format, got {inequality_matrix.format!r} and "
            f"{equality_matrix.format!r}"
        )

    if inequality_matrix.format == "csc":
        # Column merge the two CSC matrices directly with the Cython routine.
        # The index and pointer arrays are coerced to the 32 bit width the C API
        # uses before being handed to the compiled merge.
        merged_values, merged_indices, merged_pointers = _core.merge_constraint_matrices_csc(
            inequality_matrix.shape[1],
            np.ascontiguousarray(inequality_matrix.data, dtype=np.float64),
            _as_index_array(inequality_matrix.indices, "inequality matrix row indices"),
            _as_index_array(inequality_matrix.indptr, "inequality matrix column pointers"),
            number_of_inequality_rows,
            np.ascontiguousarray(equality_matrix.data, dtype=np.float64),
            _as_index_array(equality_matrix.indices, "equality matrix row indices"),
            _as_index_array(equality_matrix.indptr, "equality matrix column pointers"),
        )
        return (
            merged_values,
            merged_indices,
            merged_pointers,
            number_of_inequality_rows,
            number_of_equality_rows,
        )

    # Row oriented formats stack cheaply. Keep the native format for the stack,
    # then convert the stacked matrix to CSC a single time.
    stacked = vstack([inequality_matrix, equality_matrix], format=inequality_matrix.format).tocsc()
    return (
        stacked.data,
        stacked.indices,
        stacked.indptr,
        number_of_inequality_rows,
        number_of_equality_rows,
    )


def solve_linear_problem_sparse(
    objective_coefficients,
    *,
    inequality_constraint_matrix=None,
    inequality_upper_bounds=None,
    equality_constraint_matrix=None,
    equality_right_hand_sides=None,
    variable_lower_bounds=None,
    variable_upper_bounds=None,
    integrality=None,
    initial_column_values=None,
    objective_sense: ObjectiveSense | int = ObjectiveSense.MINIMIZE,
    options=None,
) -> LinearProblemSolution:
    """Solve a linear or mixed integer program with SciPy sparse matrices.

    Minimizes `c @ x` subject to `A_ub @ x <= b_ub`, `A_eq @ x == b_eq` and
    the variable bounds. The two constraint matrices are merged internally into
    the row bounded form used by
    [`solve_linear_problem`][cyhighs.solve_linear_problem].

    Args:
        objective_coefficients: The objective coefficient vector `c`.
        inequality_constraint_matrix: The inequality matrix `A_ub` in any sparse
            format.
        inequality_upper_bounds: The right hand side vector `b_ub`. Required when
            `A_ub` is given.
        equality_constraint_matrix: The equality matrix `A_eq` in any sparse
            format. When both matrices are given they must share the same sparse
            format.
        equality_right_hand_sides: The right hand side vector `b_eq`. Required
            when `A_eq` is given.
        variable_lower_bounds: Per variable lower bounds.
        variable_upper_bounds: Per variable upper bounds.
        integrality: Per variable integrality using
            [`VariableType`][cyhighs.VariableType] values.
        initial_column_values: A warm start solution.
        objective_sense: Whether to minimize (default) or maximize.
        options: Solver options as a mapping from
            [`HighsOption`][cyhighs.HighsOption] to a value.

    Returns:
        The [`LinearProblemSolution`][cyhighs.LinearProblemSolution] record.
    """
    if inequality_constraint_matrix is not None and inequality_upper_bounds is None:
        raise ValueError("inequality_upper_bounds is required when the inequality matrix is given")
    if equality_constraint_matrix is not None and equality_right_hand_sides is None:
        raise ValueError("equality_right_hand_sides is required when the equality matrix is given")

    (
        matrix_values,
        matrix_indices,
        matrix_pointers,
        number_of_inequality_rows,
        number_of_equality_rows,
    ) = _merge_sparse_constraints(inequality_constraint_matrix, equality_constraint_matrix)

    # Assemble the per row bounds. Inequality rows are bounded above by b_ub and
    # unbounded below, equality rows are pinned to b_eq on both sides. The
    # inequality rows come first to match the row order the merge produces.
    if number_of_inequality_rows:
        inequality_upper = np.ascontiguousarray(inequality_upper_bounds, dtype=np.float64)
        inequality_lower = np.full(number_of_inequality_rows, -HIGHS_INFINITY, dtype=np.float64)
    else:
        inequality_upper = np.empty(0, dtype=np.float64)
        inequality_lower = np.empty(0, dtype=np.float64)
    if number_of_equality_rows:
        equality_bounds = np.ascontiguousarray(equality_right_hand_sides, dtype=np.float64)
    else:
        equality_bounds = np.empty(0, dtype=np.float64)

    constraint_lower_bounds = np.concatenate([inequality_lower, equality_bounds])
    constraint_upper_bounds = np.concatenate([inequality_upper, equality_bounds])

    return solve_linear_problem(
        objective_coefficients,
        constraint_matrix_values=matrix_values,
        constraint_matrix_row_indices=matrix_indices,
        constraint_matrix_column_pointers=matrix_pointers,
        constraint_lower_bounds=constraint_lower_bounds if matrix_values is not None else None,
        constraint_upper_bounds=constraint_upper_bounds if matrix_values is not None else None,
        variable_lower_bounds=variable_lower_bounds,
        variable_upper_bounds=variable_upper_bounds,
        integrality=integrality,
        initial_column_values=initial_column_values,
        objective_sense=objective_sense,
        options=options,
    )
