"""Tests for the SciPy sparse convenience wrapper and its merge paths."""

import numpy as np
import pytest
from scipy.sparse import coo_matrix, csc_matrix, csr_matrix

from cyhighs import ModelStatus, solve_linear_problem_sparse


def test_sparse_wrapper_accepts_csr_matrix():
    inequality = csr_matrix([[1.0, 1.0], [1.0, 3.0]])
    solution = solve_linear_problem_sparse(
        objective_coefficients=[-1.0, -2.0],
        inequality_constraint_matrix=inequality,
        inequality_upper_bounds=[4.0, 6.0],
        variable_lower_bounds=[0.0, 0.0],
        variable_upper_bounds=[np.inf, np.inf],
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    np.testing.assert_allclose(solution.column_values, [3.0, 1.0], atol=1e-6)


def test_sparse_wrapper_accepts_csc_matrix():
    inequality = csc_matrix([[1.0, 1.0], [1.0, 3.0]])
    solution = solve_linear_problem_sparse(
        objective_coefficients=[-1.0, -2.0],
        inequality_constraint_matrix=inequality,
        inequality_upper_bounds=[4.0, 6.0],
        variable_lower_bounds=[0.0, 0.0],
        variable_upper_bounds=[np.inf, np.inf],
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    np.testing.assert_allclose(solution.column_values, [3.0, 1.0], atol=1e-6)


def test_csc_and_csr_inputs_agree_with_equality_block():
    # A problem with both an inequality block and an equality block, solved from
    # CSC inputs (Cython column merge) and from CSR inputs (native row stack).
    inequality_dense = [[1.0, 1.0], [1.0, 3.0]]
    equality_dense = [[1.0, 0.0]]
    kwargs = dict(
        objective_coefficients=[-1.0, -2.0],
        inequality_upper_bounds=[4.0, 6.0],
        equality_right_hand_sides=[1.0],
        variable_lower_bounds=[0.0, 0.0],
        variable_upper_bounds=[np.inf, np.inf],
    )

    from_csc = solve_linear_problem_sparse(
        inequality_constraint_matrix=csc_matrix(inequality_dense),
        equality_constraint_matrix=csc_matrix(equality_dense),
        **kwargs,  # ty: ignore[invalid-argument-type]
    )
    from_csr = solve_linear_problem_sparse(
        inequality_constraint_matrix=csr_matrix(inequality_dense),
        equality_constraint_matrix=csr_matrix(equality_dense),
        **kwargs,  # ty: ignore[invalid-argument-type]
    )
    assert from_csc.model_status == ModelStatus.OPTIMAL
    assert from_csr.model_status == ModelStatus.OPTIMAL
    # x0 is pinned to 1 by the equality row, then x0 + 3 x1 <= 6 caps x1 at 5/3.
    np.testing.assert_allclose(from_csc.column_values, [1.0, 5.0 / 3.0], atol=1e-6)
    np.testing.assert_allclose(from_csr.column_values, from_csc.column_values, atol=1e-9)


def test_coo_inputs_are_supported():
    solution = solve_linear_problem_sparse(
        objective_coefficients=[-1.0, -2.0],
        inequality_constraint_matrix=coo_matrix([[1.0, 1.0], [1.0, 3.0]]),
        inequality_upper_bounds=[4.0, 6.0],
        equality_constraint_matrix=coo_matrix([[1.0, 0.0]]),
        equality_right_hand_sides=[1.0],
        variable_lower_bounds=[0.0, 0.0],
        variable_upper_bounds=[np.inf, np.inf],
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    # x0 pinned to 1 by the equality row, x0 + 3 x1 <= 6 caps x1 at 5/3.
    np.testing.assert_allclose(solution.column_values, [1.0, 5.0 / 3.0], atol=1e-6)


def test_equality_only_problem():
    equality = coo_matrix([[1.0, 1.0]])
    solution = solve_linear_problem_sparse(
        objective_coefficients=[1.0, 1.0],
        equality_constraint_matrix=equality,
        equality_right_hand_sides=[3.0],
        variable_lower_bounds=[0.0, 0.0],
        variable_upper_bounds=[np.inf, np.inf],
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    assert solution.objective_value == pytest.approx(3.0, abs=1e-6)


def test_dense_input_is_rejected():
    with pytest.raises(TypeError, match="sparse"):
        solve_linear_problem_sparse(
            objective_coefficients=[1.0],
            inequality_constraint_matrix=np.array([[1.0]]),
            inequality_upper_bounds=[1.0],
        )


def test_mixed_formats_are_rejected():
    with pytest.raises(ValueError, match="same sparse format"):
        solve_linear_problem_sparse(
            objective_coefficients=[1.0, 1.0],
            inequality_constraint_matrix=csr_matrix([[1.0, 1.0]]),
            inequality_upper_bounds=[4.0],
            equality_constraint_matrix=csc_matrix([[1.0, 0.0]]),
            equality_right_hand_sides=[1.0],
        )
