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

# The three public interfaces, each paired with the adapter that shapes a
# Problem into that interface's keyword arguments.
_INTERFACES = {
    "array": (solve_linear_problem, "array_kwargs"),
    "sparse": (solve_linear_problem_sparse, "sparse_kwargs"),
    "linprog": (linprog, "linprog_kwargs"),
}


def _assert_optimal(interface_name, result):
    """Assert that the solve succeeded for the given interface's result type."""
    if interface_name == "linprog":
        assert result.success
    else:
        assert result.is_optimal


def _run(benchmark, interface_name, problem):
    """Time only the solve, building the problem kwargs outside the timed block."""
    solve, adapter = _INTERFACES[interface_name]
    kwargs = getattr(problem, adapter)()
    result = benchmark.pedantic(solve, kwargs=kwargs, rounds=5, iterations=1, warmup_rounds=1)
    _assert_optimal(interface_name, result)


@pytest.mark.parametrize("interface_name", list(_INTERFACES))
@pytest.mark.parametrize("number_of_variables", _LP_SIZES)
def test_lp_solve(benchmark, interface_name, number_of_variables):
    problem = make_problem(number_of_variables, mixed_integer=False)
    _run(benchmark, interface_name, problem)


@pytest.mark.parametrize("interface_name", list(_INTERFACES))
@pytest.mark.parametrize("number_of_variables", _MIP_SIZES)
def test_mip_solve(benchmark, interface_name, number_of_variables):
    problem = make_problem(number_of_variables, mixed_integer=True)
    _run(benchmark, interface_name, problem)
