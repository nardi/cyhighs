# cython: language_level=3
"""Low level Cython binding to the HiGHS C API.

This module exposes a single solving entry point, `solve_linear_problem_core`,
that maps almost directly onto the `Highs_passLp` and `Highs_passMip` C
functions. It performs no validation of its own. The pure Python layer in
`cyhighs` is responsible for coercing array dtypes, checking shapes, merging
the inequality and equality constraint matrices, and translating the raw integer
results into the public enumerations. Keeping this module thin makes the mapping
between Python and the C API easy to audit.

The extension deliberately avoids the NumPy C API. Input arrays arrive as typed
memory views and output arrays are allocated with plain `numpy.empty` and
accessed through the buffer protocol, so the compiled module is not tied to any
particular NumPy binary version.
"""

import numpy as np

from ._highs_c_api cimport (
    Highs_create,
    Highs_destroy,
    Highs_getInfinity,
    Highs_getIntInfoValue,
    Highs_getModelStatus,
    Highs_getObjectiveValue,
    Highs_getPresolvedNumCol,
    Highs_getPresolvedNumNz,
    Highs_getPresolvedNumRow,
    Highs_getSolution,
    Highs_passLp,
    Highs_passMip,
    Highs_run,
    Highs_setBoolOptionValue,
    Highs_setDoubleOptionValue,
    Highs_setIntOptionValue,
    Highs_setSolution,
    Highs_setStringOptionValue,
    Highs_version,
    HighsInt,
    kHighsMatrixFormatColwise,
    kHighsObjSenseMaximize,
    kHighsObjSenseMinimize,
    kHighsStatusError,
    kHighsVarTypeContinuous,
    kHighsVarTypeImplicitInteger,
    kHighsVarTypeInteger,
    kHighsVarTypeSemiContinuous,
    kHighsVarTypeSemiInteger,
)


# Mapping from a short kind label to the matching option setter. The Python layer
# tags every option with one of these labels so that the correct typed C setter
# is chosen without inspecting Python value types (which cannot tell a bool
# option from an int option, since bool is a subclass of int in Python).
_OPTION_KIND_BOOL = "bool"
_OPTION_KIND_INT = "int"
_OPTION_KIND_DOUBLE = "double"
_OPTION_KIND_STRING = "string"


# The integer values of the HiGHS C constants, re exported so that the Python
# enumerations can assert that they stay in sync with the compiled library.
HIGHS_CONSTANTS = {
    "kHighsMatrixFormatColwise": kHighsMatrixFormatColwise,
    "kHighsObjSenseMinimize": kHighsObjSenseMinimize,
    "kHighsObjSenseMaximize": kHighsObjSenseMaximize,
    "kHighsVarTypeContinuous": kHighsVarTypeContinuous,
    "kHighsVarTypeInteger": kHighsVarTypeInteger,
    "kHighsVarTypeSemiContinuous": kHighsVarTypeSemiContinuous,
    "kHighsVarTypeSemiInteger": kHighsVarTypeSemiInteger,
    "kHighsVarTypeImplicitInteger": kHighsVarTypeImplicitInteger,
}


def highs_version():
    """Return the version string of the linked HiGHS library.

    Returns:
        The HiGHS version, for example `"1.15.1"`.
    """
    return Highs_version().decode("ascii")


def highs_infinity():
    """Return the value HiGHS uses to represent infinity.

    Any bound whose magnitude is greater than or equal to this value is treated
    by HiGHS as unbounded.

    Returns:
        The infinity threshold, typically `1e30`.
    """
    cdef void* highs = Highs_create()
    try:
        return Highs_getInfinity(highs)
    finally:
        Highs_destroy(highs)


def merge_constraint_matrices_csc(
    HighsInt number_of_columns,
    double[::1] inequality_values not None,
    HighsInt[::1] inequality_indices not None,
    HighsInt[::1] inequality_pointers not None,
    HighsInt number_of_inequality_rows,
    double[::1] equality_values not None,
    HighsInt[::1] equality_indices not None,
    HighsInt[::1] equality_pointers not None,
):
    """Column merge two CSC matrices that share the same set of columns.

    The two matrices are stacked vertically, with the equality rows placed below
    the inequality rows. Because both matrices are in compressed sparse column
    form, the merge walks the columns and, for each column, copies the
    inequality entries followed by the equality entries. The equality row indices
    are shifted down by `number_of_inequality_rows` so that they occupy the
    rows beneath the inequality block.

    All inputs must already have the exact dtype and contiguity used by the C
    API, which the Python caller guarantees. Empty blocks are represented by a
    pointer array of length `number_of_columns + 1` filled with zeros and empty
    value and index arrays.

    Args:
        number_of_columns: The shared number of columns of both matrices.
        inequality_values: The CSC value array of the inequality matrix.
        inequality_indices: The CSC row index array of the inequality matrix.
        inequality_pointers: The CSC column pointer array of the inequality
            matrix.
        number_of_inequality_rows: The number of rows in the inequality matrix,
            used as the offset for the equality row indices.
        equality_values: The CSC value array of the equality matrix.
        equality_indices: The CSC row index array of the equality matrix.
        equality_pointers: The CSC column pointer array of the equality matrix.

    Returns:
        The merged `(values, row_indices, column_pointers)` triple in CSC form.
    """
    cdef HighsInt number_of_inequality_nonzeros = inequality_values.shape[0]
    cdef HighsInt number_of_equality_nonzeros = equality_values.shape[0]
    cdef HighsInt total_nonzeros = (
        number_of_inequality_nonzeros + number_of_equality_nonzeros
    )

    # Allocate the output arrays through NumPy and access them as typed memory
    # views. This keeps the extension free of the NumPy C API.
    merged_values_array = np.empty(total_nonzeros, dtype=np.float64)
    merged_indices_array = np.empty(total_nonzeros, dtype=np.int32)
    merged_pointers_array = np.empty(number_of_columns + 1, dtype=np.int32)

    cdef double[::1] merged_values = merged_values_array
    cdef HighsInt[::1] merged_indices = merged_indices_array
    cdef HighsInt[::1] merged_pointers = merged_pointers_array

    cdef HighsInt column
    cdef HighsInt entry
    cdef HighsInt write_position = 0

    # Walk the columns once, copying both blocks into place and building the
    # merged column pointers as we go. No Python objects are touched here, so the
    # loop can run without the GIL.
    with nogil:
        for column in range(number_of_columns):
            merged_pointers[column] = write_position

            for entry in range(
                inequality_pointers[column], inequality_pointers[column + 1]
            ):
                merged_indices[write_position] = inequality_indices[entry]
                merged_values[write_position] = inequality_values[entry]
                write_position += 1

            for entry in range(
                equality_pointers[column], equality_pointers[column + 1]
            ):
                merged_indices[write_position] = (
                    equality_indices[entry] + number_of_inequality_rows
                )
                merged_values[write_position] = equality_values[entry]
                write_position += 1

        merged_pointers[number_of_columns] = write_position

    return merged_values_array, merged_indices_array, merged_pointers_array


cdef int _apply_options(void* highs, object option_settings) except -1:
    """Apply a sequence of option settings to a HiGHS instance.

    Each entry of `option_settings` is a `(name, kind, value)` tuple where
    `kind` selects the typed C setter to call. Raises `RuntimeError` if HiGHS
    rejects a setting.
    """
    cdef bytes name_bytes
    cdef bytes value_bytes
    cdef HighsInt status
    for name, kind, value in option_settings:
        name_bytes = name.encode("ascii")
        if kind == _OPTION_KIND_BOOL:
            status = Highs_setBoolOptionValue(highs, name_bytes, 1 if value else 0)
        elif kind == _OPTION_KIND_INT:
            status = Highs_setIntOptionValue(highs, name_bytes, <HighsInt>value)
        elif kind == _OPTION_KIND_DOUBLE:
            status = Highs_setDoubleOptionValue(highs, name_bytes, <double>value)
        elif kind == _OPTION_KIND_STRING:
            value_bytes = str(value).encode("ascii")
            status = Highs_setStringOptionValue(highs, name_bytes, value_bytes)
        else:
            raise ValueError(f"Unknown option kind: {kind!r}")
        if status == kHighsStatusError:
            raise RuntimeError(f"HiGHS rejected option {name!r} with value {value!r}")
    return 0


def solve_linear_problem_core(
    HighsInt objective_sense,
    double objective_offset,
    double[::1] column_costs not None,
    double[::1] column_lower_bounds not None,
    double[::1] column_upper_bounds not None,
    double[::1] row_lower_bounds not None,
    double[::1] row_upper_bounds not None,
    HighsInt[::1] a_matrix_starts not None,
    HighsInt[::1] a_matrix_indices,
    double[::1] a_matrix_values,
    integrality,
    initial_column_values,
    option_settings,
):
    """Solve a linear or mixed integer program through the HiGHS C API.

    This is a thin translation of `Highs_passLp` and `Highs_passMip`. The
    constraint matrix must already be in a single column wise CSC structure with
    row bounds encoding both inequality and equality rows. All arrays must have
    the exact dtype and contiguity expected here, which the Python layer
    guarantees.

    Args:
        objective_sense: Either the minimize or maximize sense constant from the
            HiGHS C API.
        objective_offset: Constant term added to the objective value.
        column_costs: The objective coefficient vector `c`, one float64 entry per
            variable.
        column_lower_bounds: Lower bound on each variable, as float64.
        column_upper_bounds: Upper bound on each variable, as float64.
        row_lower_bounds: Lower bound on each constraint row, as float64.
            Inequality rows use a lower bound of negative infinity.
        row_upper_bounds: Upper bound on each constraint row, as float64. Equality
            rows use equal lower and upper bounds.
        a_matrix_starts: CSC column pointer array of length `num_columns + 1`, as
            int32.
        a_matrix_indices: CSC row index array of length `num_nonzeros`, as int32
            or `None`. May be `None` only when there are no constraint rows and no
            nonzeros.
        a_matrix_values: CSC value array of length `num_nonzeros`, as float64 or
            `None`. May be `None` only when there are no nonzeros.
        integrality: Per variable integrality using the HiGHS variable type
            encoding, as int32 or `None`. When `None` the problem is passed as a
            pure linear program.
        initial_column_values: Optional warm start values for the variables, as
            float64 or `None`.
        option_settings: Option settings as `(name, kind, value)` tuples, or
            `None`.

    Returns:
        A `(model_status, column_values, objective_value, column_dual_values,
        row_dual_values, row_values, simplex_iteration_count,
        presolved_num_columns, presolved_num_rows, presolved_num_nonzeros)`
        tuple.
    """
    cdef HighsInt num_col = column_costs.shape[0]
    cdef HighsInt num_row = row_lower_bounds.shape[0]
    cdef HighsInt num_nz = a_matrix_values.shape[0] if a_matrix_values is not None else 0

    # Resolve optional input pointers. A memory view over a zero length array is
    # not guaranteed to have a valid element zero, so guard every dereference.
    cdef HighsInt[::1] index_view
    cdef double[::1] value_view
    cdef HighsInt* index_pointer = NULL
    cdef double* value_pointer = NULL
    if num_nz > 0:
        index_view = a_matrix_indices
        value_view = a_matrix_values
        index_pointer = &index_view[0]
        value_pointer = &value_view[0]

    cdef HighsInt[::1] integrality_view
    cdef HighsInt* integrality_pointer = NULL
    cdef bint is_mixed_integer = integrality is not None
    if is_mixed_integer:
        integrality_view = integrality
        integrality_pointer = &integrality_view[0] if num_col > 0 else NULL

    cdef void* highs = Highs_create()
    cdef HighsInt pass_status
    cdef HighsInt run_status
    cdef HighsInt model_status
    cdef HighsInt iteration_count = -1
    cdef double[::1] warm_start_view
    cdef double[::1] column_values_view
    cdef double[::1] column_dual_view
    cdef double[::1] row_values_view
    cdef double[::1] row_dual_view

    try:
        if option_settings is not None:
            _apply_options(highs, option_settings)

        # Hand the model to HiGHS. The row bound arrays carry the distinction
        # between inequality and equality constraints, so the same call serves
        # both. Guard the row bound pointers for the degenerate no row case.
        if is_mixed_integer:
            pass_status = Highs_passMip(
                highs, num_col, num_row, num_nz,
                kHighsMatrixFormatColwise, objective_sense, objective_offset,
                &column_costs[0], &column_lower_bounds[0], &column_upper_bounds[0],
                &row_lower_bounds[0] if num_row > 0 else NULL,
                &row_upper_bounds[0] if num_row > 0 else NULL,
                &a_matrix_starts[0], index_pointer, value_pointer,
                integrality_pointer,
            )
        else:
            pass_status = Highs_passLp(
                highs, num_col, num_row, num_nz,
                kHighsMatrixFormatColwise, objective_sense, objective_offset,
                &column_costs[0], &column_lower_bounds[0], &column_upper_bounds[0],
                &row_lower_bounds[0] if num_row > 0 else NULL,
                &row_upper_bounds[0] if num_row > 0 else NULL,
                &a_matrix_starts[0], index_pointer, value_pointer,
            )
        if pass_status == kHighsStatusError:
            raise RuntimeError("HiGHS failed to load the model")

        # Optionally seed a warm start before solving.
        if initial_column_values is not None:
            warm_start_view = initial_column_values
            if Highs_setSolution(
                highs,
                &warm_start_view[0] if num_col > 0 else NULL,
                NULL, NULL, NULL,
            ) == kHighsStatusError:
                raise RuntimeError("HiGHS rejected the initial solution")

        # Release the GIL for the solve itself, which is where all the time is
        # spent and which does not touch any Python objects.
        with nogil:
            run_status = Highs_run(highs)
        if run_status == kHighsStatusError:
            raise RuntimeError("HiGHS failed during the solve")

        model_status = Highs_getModelStatus(highs)

        # Allocate the output arrays through NumPy and read the solution into
        # them via the buffer protocol.
        column_values = np.empty(num_col, dtype=np.float64)
        column_dual_values = np.empty(num_col, dtype=np.float64)
        row_values = np.empty(num_row, dtype=np.float64)
        row_dual_values = np.empty(num_row, dtype=np.float64)

        column_values_view = column_values
        column_dual_view = column_dual_values
        row_values_view = row_values
        row_dual_view = row_dual_values

        Highs_getSolution(
            highs,
            &column_values_view[0] if num_col > 0 else NULL,
            &column_dual_view[0] if num_col > 0 else NULL,
            &row_values_view[0] if num_row > 0 else NULL,
            &row_dual_view[0] if num_row > 0 else NULL,
        )

        objective_value = Highs_getObjectiveValue(highs)

        # Best effort retrieval of the iteration count for reporting.
        Highs_getIntInfoValue(highs, b"simplex_iteration_count", &iteration_count)

        presolved_num_col = Highs_getPresolvedNumCol(highs)
        presolved_num_row = Highs_getPresolvedNumRow(highs)
        presolved_num_nz = Highs_getPresolvedNumNz(highs)

        return (
            int(model_status),
            column_values,
            float(objective_value),
            column_dual_values,
            row_dual_values,
            row_values,
            int(iteration_count),
            int(presolved_num_col),
            int(presolved_num_row),
            int(presolved_num_nz),
        )
    finally:
        Highs_destroy(highs)
