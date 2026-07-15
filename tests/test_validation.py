"""Unit tests for input validation and the Cython CSC matrix merge."""

import numpy as np
import pytest
from cyhighs._core import merge_constraint_matrices_csc
from scipy.sparse import csc_matrix

from cyhighs.validation import _as_index_array, solve_linear_problem


def test_index_array_rejects_values_too_large_for_int32():
    too_large = np.array([2**40], dtype=np.int64)
    with pytest.raises(ValueError, match="32 bit"):
        _as_index_array(too_large, "test")


def _as_csc_arrays(dense):
    """Return the int32 and float64 CSC component arrays of a dense matrix."""
    compressed = csc_matrix(np.asarray(dense, dtype=np.float64))
    return (
        np.ascontiguousarray(compressed.data, dtype=np.float64),
        np.ascontiguousarray(compressed.indices, dtype=np.int32),
        np.ascontiguousarray(compressed.indptr, dtype=np.int32),
    )


def test_cython_merge_stacks_equality_rows_below_inequality_rows():
    inequality_values, inequality_indices, inequality_pointers = _as_csc_arrays([[1.0, 2.0]])
    equality_values, equality_indices, equality_pointers = _as_csc_arrays([[3.0, 4.0]])

    values, indices, pointers = merge_constraint_matrices_csc(
        2,  # number of columns
        inequality_values,
        inequality_indices,
        inequality_pointers,
        1,  # one inequality row
        equality_values,
        equality_indices,
        equality_pointers,
    )

    dense = csc_matrix((values, indices, pointers), shape=(2, 2)).toarray()
    np.testing.assert_array_equal(dense, np.array([[1.0, 2.0], [3.0, 4.0]]))


def test_cython_merge_with_empty_equality_block():
    inequality_values, inequality_indices, inequality_pointers = _as_csc_arrays([[5.0, 6.0]])
    empty_values = np.empty(0, dtype=np.float64)
    empty_indices = np.empty(0, dtype=np.int32)
    empty_pointers = np.zeros(3, dtype=np.int32)

    values, indices, pointers = merge_constraint_matrices_csc(
        2,
        inequality_values,
        inequality_indices,
        inequality_pointers,
        1,
        empty_values,
        empty_indices,
        empty_pointers,
    )
    np.testing.assert_array_equal(values, np.array([5.0, 6.0]))
    np.testing.assert_array_equal(pointers, np.array([0, 1, 2]))


def test_cython_merge_matches_dense_stack_on_a_larger_case():
    inequality_dense = np.array([[1.0, 0.0, 2.0], [0.0, 3.0, 0.0]])
    equality_dense = np.array([[4.0, 5.0, 0.0]])
    inequality_values, inequality_indices, inequality_pointers = _as_csc_arrays(inequality_dense)
    equality_values, equality_indices, equality_pointers = _as_csc_arrays(equality_dense)

    values, indices, pointers = merge_constraint_matrices_csc(
        3,
        inequality_values,
        inequality_indices,
        inequality_pointers,
        inequality_dense.shape[0],
        equality_values,
        equality_indices,
        equality_pointers,
    )
    merged = csc_matrix((values, indices, pointers), shape=(3, 3)).toarray()
    np.testing.assert_array_equal(merged, np.vstack([inequality_dense, equality_dense]))


def test_partial_matrix_block_is_rejected():
    with pytest.raises(ValueError, match="together"):
        solve_linear_problem(
            objective_coefficients=np.array([1.0]),
            constraint_matrix_values=np.array([1.0]),
            # Missing row indices and column pointers.
        )


def test_row_bounds_required_when_matrix_given():
    with pytest.raises(ValueError, match="constraint_lower_bounds"):
        solve_linear_problem(
            objective_coefficients=np.array([1.0]),
            constraint_matrix_values=np.array([1.0]),
            constraint_matrix_row_indices=np.array([0]),
            constraint_matrix_column_pointers=np.array([0, 1]),
        )


def test_column_pointer_length_is_checked():
    with pytest.raises(ValueError, match="column pointers must have length"):
        solve_linear_problem(
            objective_coefficients=np.array([1.0, 2.0]),
            constraint_matrix_values=np.array([1.0]),
            constraint_matrix_row_indices=np.array([0]),
            constraint_matrix_column_pointers=np.array([0, 1]),  # should have length 3
            constraint_lower_bounds=np.array([-np.inf]),
            constraint_upper_bounds=np.array([1.0]),
        )


def test_mismatched_row_bound_lengths_are_rejected():
    with pytest.raises(ValueError, match="equal length"):
        solve_linear_problem(
            objective_coefficients=np.array([1.0]),
            constraint_matrix_values=np.array([1.0]),
            constraint_matrix_row_indices=np.array([0]),
            constraint_matrix_column_pointers=np.array([0, 1]),
            constraint_lower_bounds=np.array([-np.inf]),
            constraint_upper_bounds=np.array([1.0, 2.0]),
        )
