"""Integration tests that drive real HiGHS solves through the array interface."""

import numpy as np
import pytest

from cyhighs import (
    HighsOption,
    ModelStatus,
    ObjectiveSense,
    VariableType,
    solve_linear_problem,
)


def _classic_two_variable_inequalities():
    """Return CSC arrays for the constraint matrix [[1, 1], [1, 3]].

    Used with b_ub = [4, 6] this is a standard small linear program.
    """
    values = np.array([1.0, 1.0, 1.0, 3.0])
    row_indices = np.array([0, 1, 0, 1])
    column_pointers = np.array([0, 2, 4])
    return values, row_indices, column_pointers


def test_linear_program_reaches_known_optimum():
    values, row_indices, column_pointers = _classic_two_variable_inequalities()
    # Minimize -(x0 + 2 x1), which maximizes x0 + 2 x1.
    solution = solve_linear_problem(
        objective_coefficients=np.array([-1.0, -2.0]),
        inequality_matrix_values=values,
        inequality_matrix_row_indices=row_indices,
        inequality_matrix_column_pointers=column_pointers,
        inequality_upper_bounds=np.array([4.0, 6.0]),
        variable_lower_bounds=np.array([0.0, 0.0]),
        variable_upper_bounds=np.array([np.inf, np.inf]),
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    assert solution.is_optimal
    np.testing.assert_allclose(solution.column_values, [3.0, 1.0], atol=1e-6)
    assert solution.objective_value == pytest.approx(-5.0, abs=1e-6)
    # Dual and row information is available for a pure linear program.
    assert solution.row_values is not None
    np.testing.assert_allclose(solution.row_values, [4.0, 6.0], atol=1e-6)


def test_maximize_sense():
    values, row_indices, column_pointers = _classic_two_variable_inequalities()
    solution = solve_linear_problem(
        objective_coefficients=np.array([1.0, 2.0]),
        inequality_matrix_values=values,
        inequality_matrix_row_indices=row_indices,
        inequality_matrix_column_pointers=column_pointers,
        inequality_upper_bounds=np.array([4.0, 6.0]),
        variable_lower_bounds=np.array([0.0, 0.0]),
        variable_upper_bounds=np.array([np.inf, np.inf]),
        objective_sense=ObjectiveSense.MAXIMIZE,
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    assert solution.objective_value == pytest.approx(5.0, abs=1e-6)


def test_equality_constraint_is_respected():
    # Minimize x0 + x1 subject to x0 + x1 == 3, both nonnegative.
    solution = solve_linear_problem(
        objective_coefficients=np.array([1.0, 1.0]),
        equality_matrix_values=np.array([1.0, 1.0]),
        equality_matrix_row_indices=np.array([0, 0]),
        equality_matrix_column_pointers=np.array([0, 1, 2]),
        equality_right_hand_sides=np.array([3.0]),
        variable_lower_bounds=np.array([0.0, 0.0]),
        variable_upper_bounds=np.array([np.inf, np.inf]),
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    assert solution.objective_value == pytest.approx(3.0, abs=1e-6)
    assert solution.column_values.sum() == pytest.approx(3.0, abs=1e-6)


def test_mixed_and_equality_together():
    # Minimize -(x0 + 2 x1) with x0 + x1 <= 4 and x0 == 1.
    solution = solve_linear_problem(
        objective_coefficients=np.array([-1.0, -2.0]),
        inequality_matrix_values=np.array([1.0, 1.0]),
        inequality_matrix_row_indices=np.array([0, 0]),
        inequality_matrix_column_pointers=np.array([0, 1, 2]),
        inequality_upper_bounds=np.array([4.0]),
        equality_matrix_values=np.array([1.0]),
        equality_matrix_row_indices=np.array([0]),
        equality_matrix_column_pointers=np.array([0, 1, 1]),
        equality_right_hand_sides=np.array([1.0]),
        variable_lower_bounds=np.array([0.0, 0.0]),
        variable_upper_bounds=np.array([np.inf, np.inf]),
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    np.testing.assert_allclose(solution.column_values, [1.0, 3.0], atol=1e-6)


def test_integer_constraint_changes_optimum():
    # Maximize x subject to 2 x <= 3. Continuous optimum is 1.5, integer is 1.
    integer_solution = solve_linear_problem(
        objective_coefficients=np.array([-1.0]),
        inequality_matrix_values=np.array([2.0]),
        inequality_matrix_row_indices=np.array([0]),
        inequality_matrix_column_pointers=np.array([0, 1]),
        inequality_upper_bounds=np.array([3.0]),
        variable_lower_bounds=np.array([0.0]),
        variable_upper_bounds=np.array([10.0]),
        integrality=np.array([VariableType.INTEGER]),
    )
    assert integer_solution.model_status == ModelStatus.OPTIMAL
    np.testing.assert_allclose(integer_solution.column_values, [1.0], atol=1e-6)
    # Dual information is not defined for a mixed integer problem.
    assert integer_solution.row_dual_values is None
    assert integer_solution.column_dual_values is None


def test_semi_continuous_variable_can_take_zero():
    # Minimize x where x is either 0 or between 2 and 10. The optimum is 0.
    solution = solve_linear_problem(
        objective_coefficients=np.array([1.0]),
        variable_lower_bounds=np.array([2.0]),
        variable_upper_bounds=np.array([10.0]),
        integrality=np.array([VariableType.SEMI_CONTINUOUS]),
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    np.testing.assert_allclose(solution.column_values, [0.0], atol=1e-6)


def test_infeasible_problem():
    # Constraint x <= 1 conflicts with the lower bound of 5.
    solution = solve_linear_problem(
        objective_coefficients=np.array([1.0]),
        inequality_matrix_values=np.array([1.0]),
        inequality_matrix_row_indices=np.array([0]),
        inequality_matrix_column_pointers=np.array([0, 1]),
        inequality_upper_bounds=np.array([1.0]),
        variable_lower_bounds=np.array([5.0]),
        variable_upper_bounds=np.array([10.0]),
    )
    assert solution.model_status == ModelStatus.INFEASIBLE


def test_unbounded_problem():
    # Minimize -x with x unbounded above.
    solution = solve_linear_problem(
        objective_coefficients=np.array([-1.0]),
        variable_lower_bounds=np.array([0.0]),
        variable_upper_bounds=np.array([np.inf]),
    )
    assert solution.model_status in (
        ModelStatus.UNBOUNDED,
        ModelStatus.UNBOUNDED_OR_INFEASIBLE,
    )


def test_warm_start_still_reaches_optimum():
    values, row_indices, column_pointers = _classic_two_variable_inequalities()
    solution = solve_linear_problem(
        objective_coefficients=np.array([-1.0, -2.0]),
        inequality_matrix_values=values,
        inequality_matrix_row_indices=row_indices,
        inequality_matrix_column_pointers=column_pointers,
        inequality_upper_bounds=np.array([4.0, 6.0]),
        variable_lower_bounds=np.array([0.0, 0.0]),
        variable_upper_bounds=np.array([np.inf, np.inf]),
        initial_column_values=np.array([3.0, 1.0]),
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    np.testing.assert_allclose(solution.column_values, [3.0, 1.0], atol=1e-6)


def test_options_are_applied():
    # Silence output and set a generous time limit. The solve should still work.
    values, row_indices, column_pointers = _classic_two_variable_inequalities()
    solution = solve_linear_problem(
        objective_coefficients=np.array([-1.0, -2.0]),
        inequality_matrix_values=values,
        inequality_matrix_row_indices=row_indices,
        inequality_matrix_column_pointers=column_pointers,
        inequality_upper_bounds=np.array([4.0, 6.0]),
        variable_lower_bounds=np.array([0.0, 0.0]),
        variable_upper_bounds=np.array([np.inf, np.inf]),
        options={HighsOption.OUTPUT_FLAG: False, HighsOption.TIME_LIMIT: 30.0},
    )
    assert solution.model_status == ModelStatus.OPTIMAL


def test_hipo_solver_option_solves_linear_program():
    # The HiPO interior point solver is compiled in. Selecting it should solve
    # the linear program to the same optimum.
    values, row_indices, column_pointers = _classic_two_variable_inequalities()
    solution = solve_linear_problem(
        objective_coefficients=np.array([-1.0, -2.0]),
        inequality_matrix_values=values,
        inequality_matrix_row_indices=row_indices,
        inequality_matrix_column_pointers=column_pointers,
        inequality_upper_bounds=np.array([4.0, 6.0]),
        variable_lower_bounds=np.array([0.0, 0.0]),
        variable_upper_bounds=np.array([np.inf, np.inf]),
        options={HighsOption.SOLVER: "hipo", HighsOption.OUTPUT_FLAG: False},
    )
    assert solution.model_status == ModelStatus.OPTIMAL
    assert solution.objective_value == pytest.approx(-5.0, abs=1e-5)
