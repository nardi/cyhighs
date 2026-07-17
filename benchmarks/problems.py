"""Deterministic LP and MIP generators for the performance benchmarks.

Each generator builds a feasible and bounded random program of a requested size
and returns adapters that produce ready to splat keyword arguments for each of
the three public solving interfaces. Because the generation is seeded, every
benchmark run sees exactly the same problem, which keeps the measured solve
times comparable across commits.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.sparse import csc_matrix, csr_matrix

from cyhighs import HighsOption, VariableType

# A small fixed number of nonzeros per constraint row keeps the matrix sparse,
# so a 10000 variable problem has roughly 160k nonzeros rather than 200 million.
_NONZEROS_PER_ROW = 8

# Options shared by every solve. Output is silenced, a single thread and a fixed
# random seed make the solver deterministic, so timings are not perturbed by
# threading or internal randomness.
_COMMON_OPTIONS = {
    HighsOption.OUTPUT_FLAG: False,
    HighsOption.THREADS: 1,
    HighsOption.RANDOM_SEED: 0,
}

# Extra options for mixed integer solves. The relaxed gap and generous time
# limit are safety caps that should never trigger at the sizes benchmarked here,
# they only guard against a pathological instance running unbounded in CI.
_MIP_OPTIONS = {
    **_COMMON_OPTIONS,
    HighsOption.MIP_REL_GAP: 1e-4,
    HighsOption.TIME_LIMIT: 60.0,
}


@dataclass(frozen=True)
class Problem:
    """A feasible, bounded program in a form independent of any interface.

    Attributes:
        objective: The objective coefficient vector to minimize.
        inequality_matrix: The inequality constraint matrix in CSR form.
        upper_bounds: The right hand side of the inequality rows.
        variable_lower_bounds: Per variable lower bounds.
        variable_upper_bounds: Per variable upper bounds.
        integrality: Per variable integrality, or None for a pure LP.
        options: The solver options mapping to apply.
    """

    objective: np.ndarray
    inequality_matrix: csr_matrix
    upper_bounds: np.ndarray
    variable_lower_bounds: np.ndarray
    variable_upper_bounds: np.ndarray
    integrality: np.ndarray | None
    options: dict

    def array_kwargs(self) -> dict:
        """Return keyword arguments for the array interface solve_linear_problem."""
        matrix = csc_matrix(self.inequality_matrix)
        number_of_rows = matrix.shape[0]
        return {
            "objective_coefficients": self.objective,
            "constraint_matrix_values": matrix.data.astype(np.float64),
            "constraint_matrix_row_indices": matrix.indices.astype(np.int32),
            "constraint_matrix_column_pointers": matrix.indptr.astype(np.int32),
            "constraint_lower_bounds": np.full(number_of_rows, -np.inf),
            "constraint_upper_bounds": self.upper_bounds,
            "variable_lower_bounds": self.variable_lower_bounds,
            "variable_upper_bounds": self.variable_upper_bounds,
            "integrality": self.integrality,
            "options": self.options,
        }

    def sparse_kwargs(self) -> dict:
        """Return keyword arguments for solve_linear_problem_sparse."""
        return {
            "objective_coefficients": self.objective,
            "inequality_constraint_matrix": self.inequality_matrix,
            "inequality_upper_bounds": self.upper_bounds,
            "variable_lower_bounds": self.variable_lower_bounds,
            "variable_upper_bounds": self.variable_upper_bounds,
            "integrality": self.integrality,
            "options": self.options,
        }

    def linprog_kwargs(self) -> dict:
        """Return keyword arguments for the SciPy compatible linprog."""
        bounds = list(
            zip(
                self.variable_lower_bounds.tolist(),
                self.variable_upper_bounds.tolist(),
                strict=True,
            )
        )
        return {
            "c": self.objective,
            "A_ub": self.inequality_matrix,
            "b_ub": self.upper_bounds,
            "bounds": bounds,
            "integrality": self.integrality,
            "options": self.options,
        }


def _random_inequality_matrix(
    number_of_variables: int, number_of_rows: int, rng: np.random.Generator
) -> csr_matrix:
    """Build a sparse inequality matrix with a fixed nonzero count per row."""
    nonzeros_per_row = min(_NONZEROS_PER_ROW, number_of_variables)
    columns = np.empty(number_of_rows * nonzeros_per_row, dtype=np.int64)
    for row in range(number_of_rows):
        start = row * nonzeros_per_row
        columns[start : start + nonzeros_per_row] = rng.choice(
            number_of_variables, size=nonzeros_per_row, replace=False
        )
    row_pointers = np.arange(0, number_of_rows * nonzeros_per_row + 1, nonzeros_per_row)
    # Coefficients in [1, 2) are strictly positive, which combines with the
    # variable box to keep the program bounded and easy to keep feasible.
    values = 1.0 + rng.random(number_of_rows * nonzeros_per_row)
    return csr_matrix((values, columns, row_pointers), shape=(number_of_rows, number_of_variables))


def make_problem(number_of_variables: int, *, mixed_integer: bool, seed: int = 0) -> Problem:
    """Build a feasible, bounded LP or mixed integer program.

    The program has twice as many inequality rows as variables. Feasibility is
    guaranteed by choosing an interior point and setting each right hand side to
    that point's row activity plus a nonnegative slack.

    Args:
        number_of_variables: The number of decision variables.
        mixed_integer: When True about half the variables are made integer and
            the rest stay continuous, producing a genuine mixed integer program.
        seed: The seed for the random generator, so instances are reproducible.

    Returns:
        The generated [Problem][benchmarks.problems.Problem].
    """
    rng = np.random.default_rng(seed)
    number_of_rows = 2 * number_of_variables

    variable_upper_bounds = np.full(number_of_variables, 10.0)
    variable_lower_bounds = np.zeros(number_of_variables)

    matrix = _random_inequality_matrix(number_of_variables, number_of_rows, rng)

    # A feasible interior point drives the right hand sides, so the program is
    # always solvable. The added slack keeps the point strictly interior.
    interior_point = rng.uniform(0.0, variable_upper_bounds)
    upper_bounds = matrix @ interior_point + rng.uniform(0.0, 1.0, size=number_of_rows)

    objective = rng.uniform(-1.0, 1.0, size=number_of_variables)

    integrality = None
    if mixed_integer:
        integrality = np.full(number_of_variables, VariableType.CONTINUOUS, dtype=np.int32)
        is_integer = rng.random(number_of_variables) < 0.5
        integrality[is_integer] = VariableType.INTEGER
        # Small integer ranges keep branch and bound shallow and fast.
        variable_upper_bounds[is_integer] = 5.0

    return Problem(
        objective=objective,
        inequality_matrix=matrix,
        upper_bounds=upper_bounds,
        variable_lower_bounds=variable_lower_bounds,
        variable_upper_bounds=variable_upper_bounds,
        integrality=integrality,
        options=_MIP_OPTIONS if mixed_integer else _COMMON_OPTIONS,
    )
