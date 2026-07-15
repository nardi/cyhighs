"""Tests for the SciPy sparse convenience wrapper."""

import numpy as np
import pytest
from scipy.sparse import coo_matrix, csr_matrix

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


def test_sparse_wrapper_accepts_coo_matrix_and_equality():
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


def test_sparse_wrapper_rejects_dense_input():
    with pytest.raises(TypeError, match="sparse"):
        solve_linear_problem_sparse(
            objective_coefficients=[1.0],
            inequality_constraint_matrix=np.array([[1.0]]),
            inequality_upper_bounds=[1.0],
        )
