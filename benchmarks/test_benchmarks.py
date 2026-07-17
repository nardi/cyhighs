"""Performance benchmarks for the three cyhighs solving interfaces.

These are run with pytest-benchmark and are intentionally kept out of the
default test paths, so a plain pytest run does not collect them. The benchmark
CI step invokes this directory explicitly. Each benchmark also asserts that the
solve reached an optimal solution, so a broken solve fails rather than silently
reporting a fast but wrong result.
"""

import pytest

from cyhighs import linprog, solve_linear_problem, solve_linear_problem_sparse

from .problems import make_problem

# LPs are exercised up to 10000 variables. MIPs stop at 1000 variables, since a
# larger mixed integer instance risks a branch and bound blowup that would make
# the benchmark slow and noisy.
_LP_SIZES = [100, 1000, 10000]
_MIP_SIZES = [100, 1000]

# One params list drives the problem fixture below. Each entry is a
# (mixed_integer, number_of_variables) pair, with a matching test id such as
# "lp-100" or "mip-1000" so failures are easy to identify.
_PROBLEM_PARAMS = [(False, n) for n in _LP_SIZES] + [(True, n) for n in _MIP_SIZES]
_PROBLEM_IDS = [f"mip-{n}" if mixed_integer else f"lp-{n}" for mixed_integer, n in _PROBLEM_PARAMS]

# Keyword arguments passed to every benchmark.pedantic call below. A fixed
# round count keeps every benchmark comparable and avoids pytest-benchmark's
# own calibration, which would run a variable number of rounds per test. Ten
# rounds tightens the statistics without letting the largest problems, which
# already take several seconds per solve, blow up the total CI time.
_PEDANTIC_KWARGS = {"rounds": 10, "iterations": 1, "warmup_rounds": 1}


@pytest.fixture(params=_PROBLEM_PARAMS, ids=_PROBLEM_IDS)
def problem(request):
    """Build the LP or MIP problem for the requested size.

    Parametrized over every (mixed_integer, number_of_variables) pair in
    _PROBLEM_PARAMS, so each test function below runs once per size.
    """
    mixed_integer, number_of_variables = request.param
    return make_problem(number_of_variables, mixed_integer=mixed_integer)


def test_array_solve(benchmark, problem):
    """Benchmark solve_linear_problem, the raw CSC array interface."""
    kwargs = problem.array_kwargs()
    result = benchmark.pedantic(solve_linear_problem, kwargs=kwargs, **_PEDANTIC_KWARGS)
    assert result.is_optimal


def test_sparse_solve(benchmark, problem):
    """Benchmark solve_linear_problem_sparse, the SciPy sparse matrix interface."""
    kwargs = problem.sparse_kwargs()
    result = benchmark.pedantic(solve_linear_problem_sparse, kwargs=kwargs, **_PEDANTIC_KWARGS)
    assert result.is_optimal


def test_linprog_solve(benchmark, problem):
    """Benchmark linprog, the SciPy compatible interface."""
    kwargs = problem.linprog_kwargs()
    result = benchmark.pedantic(linprog, kwargs=kwargs, **_PEDANTIC_KWARGS)
    assert result.success
