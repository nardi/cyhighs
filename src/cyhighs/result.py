"""The solution record returned by the solving functions."""

from __future__ import annotations

from typing import NamedTuple

import numpy as np

from .enumerations import ModelStatus


class LinearProblemSolution(NamedTuple):
    """The outcome of solving a linear or mixed integer program.

    The field names follow HiGHS terminology. Columns are decision variables and
    rows are constraints. For mixed integer problems the dual value and row value
    fields are set to None, since dual information is not defined there.

    Attributes
    ----------
    model_status : ModelStatus
        The status HiGHS reported for the solve.
    column_values : numpy.ndarray
        The solution vector ``x``, one value per variable.
    objective_value : float
        The objective value at the returned solution.
    column_dual_values : numpy.ndarray or None
        The reduced costs, one per variable. None for mixed integer problems.
    row_dual_values : numpy.ndarray or None
        The dual values of the constraints, one per row. None for mixed integer
        problems.
    row_values : numpy.ndarray or None
        The activity of each constraint row, that is the left hand side value at
        the solution. None for mixed integer problems.
    simplex_iteration_count : int
        The number of simplex iterations performed, or -1 if not available.
    """

    model_status: ModelStatus
    column_values: np.ndarray
    objective_value: float
    column_dual_values: np.ndarray | None
    row_dual_values: np.ndarray | None
    row_values: np.ndarray | None
    simplex_iteration_count: int

    @property
    def is_optimal(self) -> bool:
        """Return True if HiGHS proved the returned solution optimal."""
        return self.model_status == ModelStatus.OPTIMAL
