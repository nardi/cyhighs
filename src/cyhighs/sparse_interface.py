"""Convenience wrapper that accepts SciPy sparse constraint matrices.

This is a thin layer over :func:`cyhighs.validation.solve_linear_problem`. It
lets callers pass the inequality and equality constraint matrices as any SciPy
sparse matrix rather than as unpacked CSC component arrays. Each matrix is
converted to CSC and its component arrays are extracted before delegating.
"""

from __future__ import annotations

from .enumerations import ObjectiveSense
from .result import LinearProblemSolution
from .validation import solve_linear_problem


def _unpack_sparse_matrix(matrix, label: str):
    """Convert a SciPy sparse matrix to its CSC component arrays.

    Returns a ``(values, row_indices, column_pointers, number_of_rows)`` tuple,
    or ``(None, None, None, 0)`` when the matrix is None.
    """
    if matrix is None:
        return None, None, None, 0
    # scipy.sparse is imported lazily so that importing cyhighs does not require
    # importing scipy until a sparse matrix is actually used.
    from scipy.sparse import issparse

    if not issparse(matrix):
        raise TypeError(f"{label} must be a SciPy sparse matrix, got {type(matrix).__name__}")
    compressed = matrix.tocsc()
    number_of_rows = compressed.shape[0]
    return compressed.data, compressed.indices, compressed.indptr, number_of_rows


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

    This mirrors :func:`cyhighs.solve_linear_problem` but takes the constraint
    matrices as SciPy sparse matrices of any format instead of as unpacked CSC
    arrays.

    Parameters
    ----------
    objective_coefficients : array_like
        The objective coefficient vector ``c``.
    inequality_constraint_matrix : scipy.sparse matrix, optional
        The inequality matrix ``A_ub`` in any sparse format.
    inequality_upper_bounds : array_like, optional
        The right hand side vector ``b_ub``.
    equality_constraint_matrix : scipy.sparse matrix, optional
        The equality matrix ``A_eq`` in any sparse format.
    equality_right_hand_sides : array_like, optional
        The right hand side vector ``b_eq``.
    variable_lower_bounds, variable_upper_bounds : array_like, optional
        Per variable bounds.
    integrality : array_like, optional
        Per variable integrality using :class:`cyhighs.VariableType` values.
    initial_column_values : array_like, optional
        A warm start solution.
    objective_sense : ObjectiveSense or int, optional
        Whether to minimize (default) or maximize.
    options : dict of HighsOption to value, optional
        Solver options.

    Returns
    -------
    LinearProblemSolution
        The solution record.
    """
    (
        inequality_values,
        inequality_indices,
        inequality_pointers,
        _,
    ) = _unpack_sparse_matrix(inequality_constraint_matrix, "inequality_constraint_matrix")
    (
        equality_values,
        equality_indices,
        equality_pointers,
        _,
    ) = _unpack_sparse_matrix(equality_constraint_matrix, "equality_constraint_matrix")

    return solve_linear_problem(
        objective_coefficients,
        inequality_matrix_values=inequality_values,
        inequality_matrix_row_indices=inequality_indices,
        inequality_matrix_column_pointers=inequality_pointers,
        inequality_upper_bounds=inequality_upper_bounds,
        equality_matrix_values=equality_values,
        equality_matrix_row_indices=equality_indices,
        equality_matrix_column_pointers=equality_pointers,
        equality_right_hand_sides=equality_right_hand_sides,
        variable_lower_bounds=variable_lower_bounds,
        variable_upper_bounds=variable_upper_bounds,
        integrality=integrality,
        initial_column_values=initial_column_values,
        objective_sense=objective_sense,
        options=options,
    )
