# What is cyhighs

`cyhighs` lets you solve linear programs and mixed integer programs from Python
using the HiGHS solver. A linear program asks for the values of a set of
variables that optimize a linear objective, subject to linear inequality and
equality constraints and simple bounds on the variables. A mixed integer program
adds the requirement that some of those variables take integer values. These
problems appear across scheduling, logistics, finance, and engineering, and
HiGHS is one of the fastest open source solvers available for them.

The package is a thin binding. It does not reimplement any of the solving logic.
Instead it hands your problem to the compiled HiGHS library and returns the
result, so you get the full speed of the C++ solver with a Python interface that
feels natural.

## Three interfaces, one solver

`cyhighs` offers the same solver through three interfaces. They differ only in
how you describe the problem, not in how it is solved.

1. The **array interface**,
   [`solve_linear_problem`][cyhighs.solve_linear_problem], is the lowest level.
   You pass the constraint matrix directly in compressed sparse column form,
   along with per row bounds. This maps almost one to one onto the HiGHS C API,
   so it has the least overhead and the fewest surprises.
2. The **sparse interface**,
   [`solve_linear_problem_sparse`][cyhighs.solve_linear_problem_sparse], accepts
   SciPy sparse matrices for the inequality and equality constraints. It merges
   them into the form the array interface expects. This is the right choice when
   your data already lives in SciPy sparse matrices.
3. The **linprog interface**, [`linprog`][cyhighs.linprog], is a drop in
   replacement for `scipy.optimize.linprog`. It mirrors the SciPy signature and
   return type, so you can switch an existing SciPy call over to HiGHS by
   changing only the import.

## Choosing an interface

If you are porting code that already calls `scipy.optimize.linprog`, start with
[`linprog`][cyhighs.linprog]. It requires the fewest changes.

```python
from cyhighs import linprog

result = linprog(c=[-1.0, -2.0], A_ub=[[1.0, 1.0], [1.0, 3.0]], b_ub=[4.0, 6.0])
assert result.success
```

If you build constraint matrices with SciPy, reach for
[`solve_linear_problem_sparse`][cyhighs.solve_linear_problem_sparse], which keeps
your matrices in their sparse format and avoids a dense conversion.

If you need the tightest control and want to avoid any conversion at all, use the
array interface [`solve_linear_problem`][cyhighs.solve_linear_problem] and supply
the constraint matrix in compressed sparse column form yourself.

Each interface has its own page in this guide with a complete worked example.
