# Cython declarations for the subset of the HiGHS C API used by this package.
#
# Only the functions and constants that the extension actually calls are declared
# here. The signatures mirror highs/interfaces/highs_c_api.h from HiGHS 1.15.1.
# HighsInt is a 32 bit signed integer in the default HiGHS build.

from libc.stdint cimport int32_t

# Alias matching the HiGHS typedef. The default build compiles with 32 bit
# indices, so HighsInt maps to int32_t.
ctypedef int32_t HighsInt


cdef extern from "interfaces/highs_c_api.h" nogil:
    # ----- Instance lifecycle -----
    void* Highs_create()
    void Highs_destroy(void* highs)

    # ----- Model input -----
    # Pass a pure linear program (all variables continuous).
    HighsInt Highs_passLp(
        void* highs,
        const HighsInt num_col,
        const HighsInt num_row,
        const HighsInt num_nz,
        const HighsInt a_format,
        const HighsInt sense,
        const double offset,
        const double* col_cost,
        const double* col_lower,
        const double* col_upper,
        const double* row_lower,
        const double* row_upper,
        const HighsInt* a_start,
        const HighsInt* a_index,
        const double* a_value,
    )

    # Pass a mixed integer program. Identical to Highs_passLp with an additional
    # per column integrality array using the kHighsVarType encoding.
    HighsInt Highs_passMip(
        void* highs,
        const HighsInt num_col,
        const HighsInt num_row,
        const HighsInt num_nz,
        const HighsInt a_format,
        const HighsInt sense,
        const double offset,
        const double* col_cost,
        const double* col_lower,
        const double* col_upper,
        const double* row_lower,
        const double* row_upper,
        const HighsInt* a_start,
        const HighsInt* a_index,
        const double* a_value,
        const HighsInt* integrality,
    )

    # ----- Option setters, one per value type -----
    HighsInt Highs_setBoolOptionValue(void* highs, const char* option, const HighsInt value)
    HighsInt Highs_setIntOptionValue(void* highs, const char* option, const HighsInt value)
    HighsInt Highs_setDoubleOptionValue(void* highs, const char* option, const double value)
    HighsInt Highs_setStringOptionValue(void* highs, const char* option, const char* value)

    # ----- Warm start -----
    # Provide an initial solution. Any of the pointers may be NULL to leave that
    # component unset.
    HighsInt Highs_setSolution(
        void* highs,
        const double* col_value,
        const double* row_value,
        const double* col_dual,
        const double* row_dual,
    )

    # ----- Solving -----
    HighsInt Highs_run(void* highs)

    # ----- Results -----
    HighsInt Highs_getModelStatus(const void* highs)
    HighsInt Highs_getSolution(
        const void* highs,
        double* col_value,
        double* col_dual,
        double* row_value,
        double* row_dual,
    )
    double Highs_getObjectiveValue(const void* highs)
    HighsInt Highs_getIntInfoValue(const void* highs, const char* info, HighsInt* value)
    HighsInt Highs_getPresolvedNumCol(const void* highs)
    HighsInt Highs_getPresolvedNumRow(const void* highs)
    HighsInt Highs_getPresolvedNumNz(const void* highs)

    # ----- Miscellaneous -----
    double Highs_getInfinity(const void* highs)
    const char* Highs_version()
    HighsInt Highs_versionMajor()
    HighsInt Highs_versionMinor()
    HighsInt Highs_versionPatch()

    # ----- Constants -----
    # Matrix orientation. This package always passes column wise CSC data.
    const HighsInt kHighsMatrixFormatColwise
    const HighsInt kHighsMatrixFormatRowwise

    # Objective sense.
    const HighsInt kHighsObjSenseMinimize
    const HighsInt kHighsObjSenseMaximize

    # Variable integrality types.
    const HighsInt kHighsVarTypeContinuous
    const HighsInt kHighsVarTypeInteger
    const HighsInt kHighsVarTypeSemiContinuous
    const HighsInt kHighsVarTypeSemiInteger
    const HighsInt kHighsVarTypeImplicitInteger

    # Return status codes shared by most C API functions.
    const HighsInt kHighsStatusError
    const HighsInt kHighsStatusOk
    const HighsInt kHighsStatusWarning
