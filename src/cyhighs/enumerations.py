"""Enumerations mirroring the HiGHS C API integer constants.

Every enumeration value here corresponds directly to a `kHighs*` constant in
the HiGHS C header. The values are transcribed from HiGHS 1.15.1. The test suite
cross checks a subset of these against the constants exported by the compiled
extension so that a drift between this file and the linked library is caught.
"""

from __future__ import annotations

from enum import IntEnum


class ObjectiveSense(IntEnum):
    """Direction in which the objective function is optimized.

    Mirrors the `kHighsObjSense` constants.
    """

    MINIMIZE = 1
    """Minimize the objective. This is the default and the convention the
    package interface is documented against."""

    MAXIMIZE = -1
    """Maximize the objective."""


class VariableType(IntEnum):
    """Integrality domain of a single decision variable.

    Mirrors the `kHighsVarType` constants. This is what HiGHS calls
    integrality, and the values are used directly in the `integrality` array
    passed to `Highs_passMip`.
    """

    CONTINUOUS = 0
    """The variable may take any real value within its bounds."""

    INTEGER = 1
    """The variable must take an integer value within its bounds."""

    SEMI_CONTINUOUS = 2
    """The variable is either zero or a real value within its bounds. A finite
    upper bound is required by HiGHS for semi continuous variables."""

    SEMI_INTEGER = 3
    """The variable is either zero or an integer value within its bounds. A
    finite upper bound is required by HiGHS for semi integer variables."""

    IMPLICIT_INTEGER = 4
    """The variable is continuous but known to take an integer value at the
    optimum. This is used internally by HiGHS and is rarely set by callers."""


class ModelStatus(IntEnum):
    """Outcome reported by HiGHS after a solve.

    Mirrors the `kHighsModelStatus` constants from HiGHS 1.15.1. The most
    commonly inspected values are [`OPTIMAL`][cyhighs.ModelStatus.OPTIMAL],
    [`INFEASIBLE`][cyhighs.ModelStatus.INFEASIBLE] and
    [`UNBOUNDED`][cyhighs.ModelStatus.UNBOUNDED].
    """

    NOTSET = 0
    """No status has been set. Seen when a solve has not been run."""

    LOAD_ERROR = 1
    """The model could not be loaded."""

    MODEL_ERROR = 2
    """The model is invalid, for example because of inconsistent dimensions."""

    PRESOLVE_ERROR = 3
    """An error occurred during presolve."""

    SOLVE_ERROR = 4
    """An error occurred during the main solve."""

    POSTSOLVE_ERROR = 5
    """An error occurred during postsolve."""

    MODEL_EMPTY = 6
    """The model contains no variables and no constraints."""

    OPTIMAL = 7
    """An optimal solution was found."""

    INFEASIBLE = 8
    """The model has no feasible solution."""

    UNBOUNDED_OR_INFEASIBLE = 9
    """The model is either unbounded or infeasible. HiGHS could not distinguish
    the two, often because presolve detected the condition."""

    UNBOUNDED = 10
    """The objective is unbounded, so no finite optimum exists."""

    OBJECTIVE_BOUND = 11
    """The solve stopped because the objective reached a supplied bound."""

    OBJECTIVE_TARGET = 12
    """The solve stopped because the objective reached a supplied target."""

    TIME_LIMIT = 13
    """The solve stopped because the time limit was reached."""

    ITERATION_LIMIT = 14
    """The solve stopped because the iteration limit was reached."""

    UNKNOWN = 15
    """The status could not be determined."""

    SOLUTION_LIMIT = 16
    """The solve stopped because the solution count limit was reached."""

    INTERRUPT = 17
    """The solve was interrupted by the user."""
