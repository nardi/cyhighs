"""Performance benchmarks for the three cyhighs solving interfaces.

These are run with pytest-benchmark and are intentionally kept out of the
default test paths, so a plain pytest run does not collect them. The benchmark
CI step invokes this directory explicitly. Each benchmark also asserts that the
solve reached an optimal solution, so a broken solve fails rather than silently
reporting a fast but wrong result.
"""

from enum import Enum
from typing import TypeAlias

import pytest

from cyhighs import linprog, solve_linear_problem, solve_linear_problem_sparse

from .problems import make_problem


class ProblemType(Enum):
    """Whether a benchmarked problem is a pure LP or a mixed integer program."""

    LP = "lp"
    MIP = "mip"


ProblemSize: TypeAlias = int

# LPs are exercised up to 10000 variables. MIPs stop at 1000 variables, since a
# larger mixed integer instance risks a branch and bound blowup that would make
# the benchmark slow and noisy.
_LP_SIZES: list[ProblemSize] = [100, 1000, 5000, 10000]
_MIP_SIZES: list[ProblemSize] = [100, 500, 1000]

# Every (ProblemType, ProblemSize) pair the problem fixture below is
# parametrized over, with a matching test id such as "lp-100" or "mip-1000"
# so failures are easy to identify.
_PROBLEM_PARAMS: list[tuple[ProblemType, ProblemSize]] = [
    (ProblemType.LP, n) for n in _LP_SIZES
] + [(ProblemType.MIP, n) for n in _MIP_SIZES]
_PROBLEM_IDS = [f"{problem_type.value}-{n}" for problem_type, n in _PROBLEM_PARAMS]

# Per-problem round counts for benchmark.pedantic below, keyed by the same
# (ProblemType, ProblemSize) pairs as _PROBLEM_PARAMS. A fixed round count
# keeps each benchmark comparable and avoids pytest-benchmark's own
# calibration, which would run a variable number of rounds per test. Larger
# problems, which already take several seconds per solve, use fewer rounds to
# keep the total CI time in check, while lp-100 gets extra rounds since it is
# cheap enough to tighten the statistics further.
_ROUNDS_BY_PROBLEM: dict[tuple[ProblemType, ProblemSize], int] = {
    (ProblemType.LP, 100): 20,
    (ProblemType.LP, 5000): 5,
    (ProblemType.LP, 10000): 5,
    (ProblemType.MIP, 500): 5,
    (ProblemType.MIP, 1000): 5,
}
_DEFAULT_ROUNDS = 10

_PEDANTIC_KWARGS = {"iterations": 1, "warmup_rounds": 1}


@pytest.fixture(params=_PROBLEM_PARAMS, ids=_PROBLEM_IDS)
def problem(request):
    """Build the LP or MIP problem and round count for the requested size.

    Parametrized over every (ProblemType, ProblemSize) pair in
    _PROBLEM_PARAMS, so each test function below runs once per size.
    """
    problem_type, number_of_variables = request.param
    built_problem = make_problem(number_of_variables, mixed_integer=problem_type == ProblemType.MIP)
    rounds = _ROUNDS_BY_PROBLEM.get(request.param, _DEFAULT_ROUNDS)
    return built_problem, rounds


def test_array_solve(benchmark, problem):
    """Benchmark solve_linear_problem, the raw CSC array interface."""
    built_problem, rounds = problem
    kwargs = built_problem.array_kwargs()
    result = benchmark.pedantic(
        solve_linear_problem, kwargs=kwargs, rounds=rounds, **_PEDANTIC_KWARGS
    )
    assert result.is_optimal


def test_sparse_solve(benchmark, problem):
    """Benchmark solve_linear_problem_sparse, the SciPy sparse matrix interface."""
    built_problem, rounds = problem
    kwargs = built_problem.sparse_kwargs()
    result = benchmark.pedantic(
        solve_linear_problem_sparse, kwargs=kwargs, rounds=rounds, **_PEDANTIC_KWARGS
    )
    assert result.is_optimal


def test_linprog_solve(benchmark, problem):
    """Benchmark linprog, the SciPy compatible interface."""
    built_problem, rounds = problem
    kwargs = built_problem.linprog_kwargs()
    result = benchmark.pedantic(linprog, kwargs=kwargs, rounds=rounds, **_PEDANTIC_KWARGS)
    assert result.success
