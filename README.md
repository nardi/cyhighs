# cyhighs

Cython bindings to the [HiGHS](https://highs.dev) linear and mixed integer
optimization solver. The solver is compiled from source and statically linked, so
an installed wheel has no external system dependencies beyond NumPy and SciPy.

## Installation

```
uv sync
```

This builds the HiGHS library and the extension module from source. A C and C++
compiler is required. CMake and Ninja are pulled in automatically as build
dependencies.

## Usage

Three interfaces are provided, from lowest to highest level.

The main array interface takes the constraint matrix in compressed sparse column
form:

```python
import numpy as np
from cyhighs import solve_linear_problem

solution = solve_linear_problem(
    objective_coefficients=np.array([-1.0, -2.0]),
    inequality_matrix_values=np.array([1.0, 1.0]),
    inequality_matrix_row_indices=np.array([0, 0]),
    inequality_matrix_column_pointers=np.array([0, 1, 2]),
    inequality_upper_bounds=np.array([4.0]),
    variable_lower_bounds=np.array([0.0, 0.0]),
    variable_upper_bounds=np.array([10.0, 10.0]),
)
print(solution.column_values, solution.objective_value)
```

The sparse wrapper accepts any SciPy sparse matrix:

```python
from scipy.sparse import csr_matrix
from cyhighs import solve_linear_problem_sparse

solution = solve_linear_problem_sparse(
    objective_coefficients=[-1.0, -2.0],
    inequality_constraint_matrix=csr_matrix([[1.0, 1.0]]),
    inequality_upper_bounds=[4.0],
    variable_lower_bounds=[0.0, 0.0],
    variable_upper_bounds=[10.0, 10.0],
)
```

The linprog wrapper is a drop in replacement for `scipy.optimize.linprog`:

```python
from cyhighs import linprog

result = linprog(c=[-1.0, -2.0], A_ub=[[1.0, 1.0]], b_ub=[4.0], bounds=(0, 10))
print(result.x, result.fun)
```
