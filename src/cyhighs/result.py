"""The solution record returned by the solving functions."""

from __future__ import annotations

from typing import NamedTuple

import numpy as np

from .enumerations import ModelStatus


class LinearProblemSolution(NamedTuple):
    """The outcome of solving a linear or mixed integer program.

    The field names follow HiGHS terminology. Columns are decision variables and
    rows are constraints. For mixed integer problems the dual value and row value
    fields are set to `None`, since dual information is not defined there.

    Attributes:
        model_status: The status HiGHS reported for the solve, as a
            [`ModelStatus`][cyhighs.ModelStatus] value.
        column_values: The solution vector `x`, one value per variable.
        objective_value: The objective value at the returned solution.
        column_dual_values: The reduced costs, one per variable. `None` for mixed
            integer problems.
        row_dual_values: The dual values of the constraints, one per row. `None`
            for mixed integer problems.
        row_values: The activity of each constraint row, that is the left hand
            side value at the solution. `None` for mixed integer problems.
        simplex_iteration_count: The number of simplex iterations performed, or
            -1 if not available.
        presolved_num_columns: The number of columns in the presolved model.
            Equal to `column_values`'s length if presolve was off or made no
            reductions.
        presolved_num_rows: The number of rows in the presolved model. Equal to
            `row_values`'s length if presolve was off or made no reductions.
        presolved_num_nonzeros: The number of nonzeros in the constraint matrix
            of the presolved model.
    """

    model_status: ModelStatus
    column_values: np.ndarray
    objective_value: float
    column_dual_values: np.ndarray | None
    row_dual_values: np.ndarray | None
    row_values: np.ndarray | None
    simplex_iteration_count: int
    presolved_num_columns: int
    presolved_num_rows: int
    presolved_num_nonzeros: int

    @property
    def is_optimal(self) -> bool:
        """Return True if HiGHS proved the returned solution optimal."""
        return self.model_status == ModelStatus.OPTIMAL


class OptimizeResult(NamedTuple):
    """SciPy `linprog` shaped result, returned by [`linprog`][cyhighs.linprog].

    Carries the same field names `scipy.optimize.OptimizeResult` exposes for a
    `linprog` call, plus a `highs_solution` field with the full HiGHS solve
    result.

    Attributes:
        x: The solution vector.
        fun: The objective value at the returned solution.
        slack: The slack in each inequality constraint, `b_ub - A_ub @ x`.
        con: The residual of each equality constraint, `A_eq @ x - b_eq`.
        status: SciPy convention status code: 0 optimal, 1 iteration or time
            limit, 2 infeasible, 3 unbounded, 4 numerical or other failure.
        success: True if `status` is 0.
        message: Human readable description of `status`.
        nit: The number of solver iterations performed.
        highs_solution: The full
            [`LinearProblemSolution`][cyhighs.LinearProblemSolution] HiGHS
            returned for this solve.
    """

    x: np.ndarray
    fun: float
    slack: np.ndarray
    con: np.ndarray
    status: int
    success: bool
    message: str
    nit: int
    highs_solution: LinearProblemSolution
