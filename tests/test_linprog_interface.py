"""Tests for the scipy.optimize.linprog compatible wrapper.

Where practical the results are compared directly against SciPy's own linprog so
that the drop in replacement is verified to agree.
"""

import numpy as np
import pytest
from scipy.optimize import linprog as scipy_linprog

from cyhighs import LinearProblemSolution, linprog


def test_matches_scipy_on_a_small_problem():
    c = [-1.0, -2.0]
    A_ub = [[1.0, 1.0], [1.0, 3.0]]
    b_ub = [4.0, 6.0]
    bounds = (0, None)

    ours = linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds)
    theirs = scipy_linprog(c=c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    assert ours.success
    assert theirs.success
    np.testing.assert_allclose(ours.x, theirs.x, atol=1e-6)
    assert ours.fun == pytest.approx(theirs.fun, abs=1e-6)


def test_returns_optimize_result_fields():
    result = linprog(
        c=[-1.0, -2.0],
        A_ub=[[1.0, 1.0], [1.0, 3.0]],
        b_ub=[4.0, 6.0],
        bounds=(0, None),
    )
    assert result.status == 0
    assert result.success is True
    assert result.message
    # slack is b_ub - A_ub @ x and should be nonnegative at optimum.
    assert np.all(result.slack >= -1e-6)
    assert result.con.size == 0


def test_highs_solution_field_carries_full_result():
    result = linprog(
        c=[-1.0, -2.0],
        A_ub=[[1.0, 1.0], [1.0, 3.0]],
        b_ub=[4.0, 6.0],
        bounds=(0, None),
    )
    assert isinstance(result.highs_solution, LinearProblemSolution)
    assert 0 <= result.highs_solution.presolved_num_columns <= 2
    assert 0 <= result.highs_solution.presolved_num_rows <= 2


def test_equality_constraints_produce_zero_residual():
    result = linprog(
        c=[1.0, 1.0],
        A_eq=[[1.0, 1.0]],
        b_eq=[3.0],
        bounds=(0, None),
    )
    assert result.success
    np.testing.assert_allclose(result.con, [0.0], atol=1e-6)


def test_per_variable_bounds():
    # Force x0 into [1, 2] and x1 into [0, 5].
    result = linprog(
        c=[-1.0, -1.0],
        A_ub=[[1.0, 1.0]],
        b_ub=[4.0],
        bounds=[(1, 2), (0, 5)],
    )
    assert result.success
    # Maximizing x0 + x1 with x0 + x1 <= 4 fills the constraint, so the objective
    # is -4. The exact vertex is not unique, so check the bounds and the sum.
    assert result.fun == pytest.approx(-4.0, abs=1e-6)
    assert 1.0 - 1e-6 <= result.x[0] <= 2.0 + 1e-6
    assert result.x.sum() == pytest.approx(4.0, abs=1e-6)


def test_integrality_argument():
    # Maximize x subject to 2 x <= 3 with x integer gives x = 1.
    result = linprog(
        c=[-1.0],
        A_ub=[[2.0]],
        b_ub=[3.0],
        bounds=(0, 10),
        integrality=[1],
    )
    assert result.success
    np.testing.assert_allclose(result.x, [1.0], atol=1e-6)


def test_infeasible_reports_status_two():
    result = linprog(
        c=[1.0],
        A_ub=[[1.0]],
        b_ub=[1.0],
        bounds=[(5, 10)],
    )
    assert result.status == 2
    assert not result.success


def test_unbounded_reports_status_three():
    result = linprog(c=[-1.0], bounds=[(0, None)])
    assert result.status == 3
    assert not result.success


def test_warm_start_argument_is_accepted():
    result = linprog(
        c=[-1.0, -2.0],
        A_ub=[[1.0, 1.0], [1.0, 3.0]],
        b_ub=[4.0, 6.0],
        bounds=(0, None),
        x0=[3.0, 1.0],
    )
    assert result.success
    np.testing.assert_allclose(result.x, [3.0, 1.0], atol=1e-6)
