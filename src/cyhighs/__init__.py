"""Cython bindings to the HiGHS linear and mixed integer optimization solver.

This package exposes three layers, from lowest to highest level.

- [`solve_linear_problem`][cyhighs.solve_linear_problem] is the main array
  interface. It takes the problem as NumPy arrays, with the constraint matrices
  in compressed sparse column form.
- [`solve_linear_problem_sparse`][cyhighs.solve_linear_problem_sparse] is a thin
  wrapper that accepts SciPy sparse constraint matrices instead of unpacked
  component arrays.
- [`linprog`][cyhighs.linprog] mirrors the `scipy.optimize.linprog` signature,
  for code migrating from SciPy.

Problem statuses are returned as the [`ModelStatus`][cyhighs.ModelStatus]
enumeration, variable integrality is expressed with
[`VariableType`][cyhighs.VariableType], and solver options are set with the
[`HighsOption`][cyhighs.HighsOption] enumeration.
[`PresolveRule`][cyhighs.PresolveRule] names the individual presolve
reductions addressed by
[`HighsOption.PRESOLVE_RULE_OFF`][cyhighs.HighsOption.PRESOLVE_RULE_OFF].
"""

from __future__ import annotations

from ._blas_backend import select_blas_backend

select_blas_backend()

from ._core import highs_infinity, highs_version  # noqa: E402
from .enumerations import ModelStatus, ObjectiveSense, PresolveRule, VariableType  # noqa: E402
from .linprog_interface import linprog  # noqa: E402
from .options import HighsOption  # noqa: E402
from .result import LinearProblemSolution, OptimizeResult  # noqa: E402
from .sparse_interface import solve_linear_problem_sparse  # noqa: E402
from .validation import HIGHS_INFINITY, solve_linear_problem  # noqa: E402

__all__ = [
    "HIGHS_INFINITY",
    "HighsOption",
    "LinearProblemSolution",
    "ModelStatus",
    "ObjectiveSense",
    "OptimizeResult",
    "PresolveRule",
    "VariableType",
    "highs_infinity",
    "highs_version",
    "linprog",
    "solve_linear_problem",
    "solve_linear_problem_sparse",
]
