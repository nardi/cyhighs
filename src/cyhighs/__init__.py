"""Cython bindings to the HiGHS linear and mixed integer optimization solver.

This package exposes three layers, from lowest to highest level.

- [`solve_linear_problem`][cyhighs.solve_linear_problem] is the main array
  interface. It takes the problem as NumPy arrays, with the constraint matrices
  in compressed sparse column form.
- [`solve_linear_problem_sparse`][cyhighs.solve_linear_problem_sparse] is a thin
  wrapper that accepts SciPy sparse constraint matrices instead of unpacked
  component arrays.
- [`linprog`][cyhighs.linprog] is a drop in replacement for
  `scipy.optimize.linprog`.

Problem statuses are returned as the [`ModelStatus`][cyhighs.ModelStatus]
enumeration, variable integrality is expressed with
[`VariableType`][cyhighs.VariableType], and solver options are set with the
[`HighsOption`][cyhighs.HighsOption] enumeration.
"""

from __future__ import annotations

from ._core import highs_infinity, highs_version
from .enumerations import ModelStatus, ObjectiveSense, VariableType
from .linprog_interface import linprog
from .options import HighsOption
from .result import LinearProblemSolution
from .sparse_interface import solve_linear_problem_sparse
from .validation import HIGHS_INFINITY, solve_linear_problem

__all__ = [
    "HIGHS_INFINITY",
    "HighsOption",
    "LinearProblemSolution",
    "ModelStatus",
    "ObjectiveSense",
    "VariableType",
    "highs_infinity",
    "highs_version",
    "linprog",
    "solve_linear_problem",
    "solve_linear_problem_sparse",
]
