"""Unit tests for input validation and the CSC matrix merge."""

import numpy as np
import pytest

from cyhighs.validation import (
    _as_index_array,
    _merge_constraint_matrices,
    solve_linear_problem,
)


def test_index_array_rejects_values_too_large_for_int32():
    too_large = np.array([2**40], dtype=np.int64)
    with pytest.raises(ValueError, match="32 bit"):
        _as_index_array(too_large, "test")


def test_merge_stacks_equality_rows_below_inequality_rows():
    # Two variables. Inequality matrix has one row [1, 2]. Equality matrix has
    # one row [3, 4]. In CSC each column holds its own entries.
    number_of_columns = 2
    inequality_values = np.array([1.0, 2.0])
    inequality_indices = np.array([0, 0], dtype=np.int32)
    inequality_pointers = np.array([0, 1, 2], dtype=np.int32)
    equality_values = np.array([3.0, 4.0])
    equality_indices = np.array([0, 0], dtype=np.int32)
    equality_pointers = np.array([0, 1, 2], dtype=np.int32)

    values, indices, pointers = _merge_constraint_matrices(
        number_of_columns,
        inequality_values,
        inequality_indices,
        inequality_pointers,
        1,  # one inequality row
        equality_values,
        equality_indices,
        equality_pointers,
    )

    # Reconstruct the dense stacked matrix to verify correctness.
    from scipy.sparse import csc_matrix

    dense = csc_matrix((values, indices, pointers), shape=(2, 2)).toarray()
    np.testing.assert_array_equal(dense, np.array([[1.0, 2.0], [3.0, 4.0]]))


def test_merge_with_empty_equality_block():
    number_of_columns = 2
    inequality_values = np.array([5.0, 6.0])
    inequality_indices = np.array([0, 0], dtype=np.int32)
    inequality_pointers = np.array([0, 1, 2], dtype=np.int32)
    empty_values = np.empty(0)
    empty_indices = np.empty(0, dtype=np.int32)
    empty_pointers = np.zeros(3, dtype=np.int32)

    values, indices, pointers = _merge_constraint_matrices(
        number_of_columns,
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


def test_partial_inequality_block_is_rejected():
    with pytest.raises(ValueError, match="together"):
        solve_linear_problem(
            objective_coefficients=np.array([1.0]),
            inequality_matrix_values=np.array([1.0]),
            # Missing row indices and column pointers.
        )


def test_inequality_bounds_required_when_matrix_given():
    with pytest.raises(ValueError, match="inequality_upper_bounds is required"):
        solve_linear_problem(
            objective_coefficients=np.array([1.0]),
            inequality_matrix_values=np.array([1.0]),
            inequality_matrix_row_indices=np.array([0]),
            inequality_matrix_column_pointers=np.array([0, 1]),
        )


def test_column_pointer_length_is_checked():
    with pytest.raises(ValueError, match="column pointers must have length"):
        solve_linear_problem(
            objective_coefficients=np.array([1.0, 2.0]),
            inequality_matrix_values=np.array([1.0]),
            inequality_matrix_row_indices=np.array([0]),
            inequality_matrix_column_pointers=np.array([0, 1]),  # should have length 3
            inequality_upper_bounds=np.array([1.0]),
        )
