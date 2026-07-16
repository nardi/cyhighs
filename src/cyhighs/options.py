"""HiGHS solver options exposed as a typed enumeration.

Each [`HighsOption`][cyhighs.HighsOption] member carries the exact option name
string that HiGHS expects together with the value kind that selects the correct
typed C setter. Passing options as enumeration members rather than raw strings
means typos are caught at lookup time and the value type is validated before it
ever reaches the C API.

Options are supplied to the solving functions as a mapping from
[`HighsOption`][cyhighs.HighsOption] to a value, for example:

```python
{HighsOption.TIME_LIMIT: 10.0, HighsOption.OUTPUT_FLAG: False}
```

The options declared here cover every user-settable HiGHS option (the ones
documented in the HiGHS options reference), excluding options that only exist
in debug builds of HiGHS. The value kinds match the four typed setters in the
HiGHS C API.
"""

from __future__ import annotations

from enum import Enum

# Value kind labels. These match the branch labels in the compiled core module
# and select which typed HiGHS setter is used for the option.
OPTION_KIND_BOOL = "bool"
OPTION_KIND_INT = "int"
OPTION_KIND_DOUBLE = "double"
OPTION_KIND_STRING = "string"

# Python types accepted for each value kind. bool is intentionally excluded from
# the integer and double kinds so that a boolean is never silently coerced.
_ACCEPTED_PYTHON_TYPES = {
    OPTION_KIND_BOOL: (bool,),
    OPTION_KIND_INT: (int,),
    OPTION_KIND_DOUBLE: (int, float),
    OPTION_KIND_STRING: (str,),
}


class HighsOption(Enum):
    """A HiGHS option together with its name and value kind.

    The enumeration value is a `(name, kind)` pair. `name` is the string the
    HiGHS C API expects and `kind` is one of the `OPTION_KIND_*` labels.
    """

    OUTPUT_FLAG = ("output_flag", OPTION_KIND_BOOL)
    """Master switch for all HiGHS logging. Set to True to let the solver print
    its log. Boolean; HiGHS itself defaults to True, but
    [`solve_linear_problem`][cyhighs.solve_linear_problem] defaults it to False
    so the solver is silent unless requested."""

    LOG_TO_CONSOLE = ("log_to_console", OPTION_KIND_BOOL)
    """Whether log messages are written to the console. Boolean, default True."""

    SOLVER = ("solver", OPTION_KIND_STRING)
    """Which algorithm to use. One of "choose", "simplex", "ipm", "pdlp" or
    "hipo". String, default "choose"."""

    PRESOLVE = ("presolve", OPTION_KIND_STRING)
    """Presolve control. One of "off", "choose" or "on". String, default
    "choose"."""

    PARALLEL = ("parallel", OPTION_KIND_STRING)
    """Parallelism control. One of "off", "choose" or "on". String, default
    "choose"."""

    RUN_CROSSOVER = ("run_crossover", OPTION_KIND_STRING)
    """Whether to run crossover after an interior point solve. One of "off",
    "choose" or "on". String, default "on"."""

    TIME_LIMIT = ("time_limit", OPTION_KIND_DOUBLE)
    """Wall clock time limit for the solve in seconds. Double, default infinity."""

    THREADS = ("threads", OPTION_KIND_INT)
    """Number of threads to use. Zero means let HiGHS choose. Integer, default 0."""

    RANDOM_SEED = ("random_seed", OPTION_KIND_INT)
    """Seed for the random number generator. Integer, default 0."""

    PRIMAL_FEASIBILITY_TOLERANCE = ("primal_feasibility_tolerance", OPTION_KIND_DOUBLE)
    """Tolerance for primal feasibility. Double, default 1e-7."""

    DUAL_FEASIBILITY_TOLERANCE = ("dual_feasibility_tolerance", OPTION_KIND_DOUBLE)
    """Tolerance for dual feasibility. Double, default 1e-7."""

    OBJECTIVE_BOUND = ("objective_bound", OPTION_KIND_DOUBLE)
    """Bound on the objective that stops the solve when reached. Double, default
    infinity."""

    OBJECTIVE_TARGET = ("objective_target", OPTION_KIND_DOUBLE)
    """Target objective value that stops the solve when reached. Double, default
    negative infinity."""

    MIP_REL_GAP = ("mip_rel_gap", OPTION_KIND_DOUBLE)
    """Relative optimality gap at which a mixed integer solve stops. Double,
    default 1e-4."""

    MIP_ABS_GAP = ("mip_abs_gap", OPTION_KIND_DOUBLE)
    """Absolute optimality gap at which a mixed integer solve stops. Double,
    default 1e-6."""

    MIP_FEASIBILITY_TOLERANCE = ("mip_feasibility_tolerance", OPTION_KIND_DOUBLE)
    """Feasibility tolerance for integer variables. Double, default 1e-6."""

    MIP_MAX_NODES = ("mip_max_nodes", OPTION_KIND_INT)
    """Maximum number of branch and bound nodes. Integer, default a very large
    value."""

    HIGHS_DEBUG_LEVEL = ("highs_debug_level", OPTION_KIND_INT)
    """Internal debugging verbosity from 0 to 4. Integer, default 0."""

    RANGING = ("ranging", OPTION_KIND_STRING)
    """Compute cost, bound, RHS and basic solution ranging: "off" or "on". String, default
    "off"."""

    INFINITE_COST = ("infinite_cost", OPTION_KIND_DOUBLE)
    """Limit on |cost coefficient|: values greater than or equal to this will be treated as
    infinite. Double, default 1e20."""

    INFINITE_BOUND = ("infinite_bound", OPTION_KIND_DOUBLE)
    """Limit on |constraint bound|: values greater than or equal to this will be treated as
    infinite. Double, default 1e20."""

    SMALL_MATRIX_VALUE = ("small_matrix_value", OPTION_KIND_DOUBLE)
    """Lower limit on |matrix entries|: values less than or equal to this will be treated
    as zero. Double, default 1e-9."""

    LARGE_MATRIX_VALUE = ("large_matrix_value", OPTION_KIND_DOUBLE)
    """Upper limit on |matrix entries|: values greater than or equal to this will be
    treated as infinite. Double, default 1e15."""

    KKT_TOLERANCE = ("kkt_tolerance", OPTION_KIND_DOUBLE)
    """If changed from its default value, this tolerance is used for all feasibility and
    optimality (KKT) measures. Double, default 1e-7."""

    PRIMAL_RESIDUAL_TOLERANCE = ("primal_residual_tolerance", OPTION_KIND_DOUBLE)
    """Primal residual tolerance. Double, default 1e-7."""

    DUAL_RESIDUAL_TOLERANCE = ("dual_residual_tolerance", OPTION_KIND_DOUBLE)
    """Dual residual tolerance. Double, default 1e-7."""

    OPTIMALITY_TOLERANCE = ("optimality_tolerance", OPTION_KIND_DOUBLE)
    """Optimality tolerance. Double, default 1e-7."""

    USER_OBJECTIVE_SCALE = ("user_objective_scale", OPTION_KIND_INT)
    """Exponent of power-of-two objective scaling for model. Integer, default 0."""

    USER_BOUND_SCALE = ("user_bound_scale", OPTION_KIND_INT)
    """Exponent of power-of-two bound scaling for model. Integer, default 0."""

    HIGHS_ANALYSIS_LEVEL = ("highs_analysis_level", OPTION_KIND_INT)
    """Analysis level in HiGHS. Integer, default 0."""

    SIMPLEX_STRATEGY = ("simplex_strategy", OPTION_KIND_INT)
    """Strategy for simplex solver 0 => Choose; 1 => Dual (serial); 2 => Dual (SIP); 3 =>
    Dual (PAMI); 4 => Primal. Integer, default 1."""

    SIMPLEX_SCALE_STRATEGY = ("simplex_scale_strategy", OPTION_KIND_INT)
    """Simplex scaling strategy: off / choose / equilibration (default) / forced
    equilibration / max value (0/1/2/3/4). Integer, default 2."""

    SIMPLEX_CRASH_STRATEGY = ("simplex_crash_strategy", OPTION_KIND_INT)
    """Strategy for simplex crash: off / LTSSF / Bixby (0/1/2). Integer, default 0."""

    SIMPLEX_DUAL_EDGE_WEIGHT_STRATEGY = ("simplex_dual_edge_weight_strategy", OPTION_KIND_INT)
    """Strategy for simplex dual edge weights: Choose / Dantzig / Devex / Steepest Edge
    (-1/0/1/2). Integer, default -1."""

    SIMPLEX_PRIMAL_EDGE_WEIGHT_STRATEGY = ("simplex_primal_edge_weight_strategy", OPTION_KIND_INT)
    """Strategy for simplex primal edge weights: Choose / Dantzig / Devex / Steepest Edge
    (-1/0/1/2). Integer, default -1."""

    SIMPLEX_ITERATION_LIMIT = ("simplex_iteration_limit", OPTION_KIND_INT)
    """Iteration limit for simplex solver when solving LPs, but not subproblems in the MIP
    solver. Integer, default a very large value."""

    SIMPLEX_UPDATE_LIMIT = ("simplex_update_limit", OPTION_KIND_INT)
    """Limit on the number of simplex UPDATE operations. Integer, default 5000."""

    SIMPLEX_MIN_CONCURRENCY = ("simplex_min_concurrency", OPTION_KIND_INT)
    """Minimum level of concurrency in parallel simplex. Integer, default 1."""

    SIMPLEX_MAX_CONCURRENCY = ("simplex_max_concurrency", OPTION_KIND_INT)
    """Maximum level of concurrency in parallel simplex. Integer, default 8."""

    TIMELESS_LOG = ("timeless_log", OPTION_KIND_BOOL)
    """Suppression of time-based data in logging. Boolean, default False."""

    LOG_FILE = ("log_file", OPTION_KIND_STRING)
    """Log file. String, default ""."""

    WRITE_MODEL_TO_FILE = ("write_model_to_file", OPTION_KIND_BOOL)
    """Write the model to a file. Boolean, default False."""

    WRITE_PRESOLVED_MODEL_TO_FILE = ("write_presolved_model_to_file", OPTION_KIND_BOOL)
    """Write the presolved model to a file. Boolean, default False."""

    WRITE_SOLUTION_TO_FILE = ("write_solution_to_file", OPTION_KIND_BOOL)
    """Write the primal and dual solution to a file. Boolean, default False."""

    WRITE_SOLUTION_STYLE = ("write_solution_style", OPTION_KIND_INT)
    """Style of solution file (raw = computer-readable, pretty = human-readable): -1 =>
    HiGHS old raw (deprecated); 0 => HiGHS raw; 1 => HiGHS pretty; 2 => Glpsol raw; 3 =>
    Glpsol pretty; 4 => HiGHS sparse raw. Integer, default 0."""

    GLPSOL_COST_ROW_LOCATION = ("glpsol_cost_row_location", OPTION_KIND_INT)
    """Location of cost row for Glpsol file: -2 => Last; -1 => None; 0 => None if empty,
    otherwise data file location; 1 <= n <= num_row => Location n; n > num_row => Last.
    Integer, default 0."""

    ICRASH = ("icrash", OPTION_KIND_BOOL)
    """Run iCrash. Boolean, default False."""

    ICRASH_DUALIZE = ("icrash_dualize", OPTION_KIND_BOOL)
    """Dualize strategy for iCrash. Boolean, default False."""

    ICRASH_STRATEGY = ("icrash_strategy", OPTION_KIND_STRING)
    """Strategy for iCrash. String, default "ICA"."""

    ICRASH_STARTING_WEIGHT = ("icrash_starting_weight", OPTION_KIND_DOUBLE)
    """iCrash starting weight. Double, default 1e-3."""

    ICRASH_ITERATIONS = ("icrash_iterations", OPTION_KIND_INT)
    """iCrash iterations. Integer, default 30."""

    ICRASH_APPROX_ITER = ("icrash_approx_iter", OPTION_KIND_INT)
    """iCrash approximate minimization iterations. Integer, default 50."""

    ICRASH_EXACT = ("icrash_exact", OPTION_KIND_BOOL)
    """Exact subproblem solution for iCrash. Boolean, default False."""

    ICRASH_BREAKPOINTS = ("icrash_breakpoints", OPTION_KIND_BOOL)
    """Exact subproblem solution for iCrash. Boolean, default False."""

    READ_SOLUTION_FILE = ("read_solution_file", OPTION_KIND_STRING)
    """Read solution file. String, default ""."""

    READ_BASIS_FILE = ("read_basis_file", OPTION_KIND_STRING)
    """Read basis file. String, default ""."""

    WRITE_MODEL_FILE = ("write_model_file", OPTION_KIND_STRING)
    """Write model file. String, default ""."""

    SOLUTION_FILE = ("solution_file", OPTION_KIND_STRING)
    """Write solution file. String, default ""."""

    WRITE_BASIS_FILE = ("write_basis_file", OPTION_KIND_STRING)
    """Write basis file. String, default ""."""

    WRITE_PRESOLVED_MODEL_FILE = ("write_presolved_model_file", OPTION_KIND_STRING)
    """Write presolved model file. String, default ""."""

    WRITE_IIS_MODEL_FILE = ("write_iis_model_file", OPTION_KIND_STRING)
    """Write IIS model file. String, default ""."""

    MIP_DETECT_SYMMETRY = ("mip_detect_symmetry", OPTION_KIND_BOOL)
    """Whether MIP symmetry should be detected. Boolean, default True."""

    MIP_ALLOW_RESTART = ("mip_allow_restart", OPTION_KIND_BOOL)
    """Whether MIP restart is permitted. Boolean, default True."""

    MIP_MAX_STALL_NODES = ("mip_max_stall_nodes", OPTION_KIND_INT)
    """MIP solver max number of nodes where estimate is above cutoff bound. Integer,
    default a very large value."""

    MIP_MAX_START_NODES = ("mip_max_start_nodes", OPTION_KIND_INT)
    """MIP solver max number of nodes when completing a partial MIP start. Integer, default
    500."""

    MIP_IMPROVING_SOLUTION_SAVE = ("mip_improving_solution_save", OPTION_KIND_BOOL)
    """Whether improving MIP solutions should be saved. Boolean, default False."""

    MIP_IMPROVING_SOLUTION_REPORT_SPARSE = (
        "mip_improving_solution_report_sparse",
        OPTION_KIND_BOOL,
    )
    """Whether improving MIP solutions should be reported in sparse format. Boolean,
    default False."""

    MIP_IMPROVING_SOLUTION_FILE = ("mip_improving_solution_file", OPTION_KIND_STRING)
    """File for reporting improving MIP solutions. Not reported for an empty string.
    String, default ""."""

    MIP_ROOT_PRESOLVE_ONLY = ("mip_root_presolve_only", OPTION_KIND_BOOL)
    """Whether MIP presolve is only applied at the root node. Boolean, default False."""

    MIP_LIFTING_FOR_PROBING = ("mip_lifting_for_probing", OPTION_KIND_INT)
    """Level of lifting for probing that is used. Integer, default -1."""

    MIP_MAX_LEAVES = ("mip_max_leaves", OPTION_KIND_INT)
    """MIP solver max number of leaf nodes. Integer, default a very large value."""

    MIP_MAX_IMPROVING_SOLS = ("mip_max_improving_sols", OPTION_KIND_INT)
    """Limit on the number of improving solutions found to stop the MIP solver prematurely.
    Integer, default a very large value."""

    MIP_LP_AGE_LIMIT = ("mip_lp_age_limit", OPTION_KIND_INT)
    """Maximal age of dynamic LP rows before they are removed from the LP relaxation in the
    MIP solver. Integer, default 10."""

    MIP_POOL_AGE_LIMIT = ("mip_pool_age_limit", OPTION_KIND_INT)
    """Maximal age of rows in the MIP solver cutpool before they are deleted. Integer,
    default 30."""

    MIP_POOL_SOFT_LIMIT = ("mip_pool_soft_limit", OPTION_KIND_INT)
    """Soft limit on the number of rows in the MIP solver cutpool for dynamic age
    adjustment. Integer, default 10000."""

    MIP_PSCOST_MINRELIABLE = ("mip_pscost_minreliable", OPTION_KIND_INT)
    """Minimal number of observations before MIP solver pseudo costs are considered
    reliable. Integer, default 8."""

    MIP_MIN_CLIQUETABLE_ENTRIES_FOR_PARALLELISM = (
        "mip_min_cliquetable_entries_for_parallelism",
        OPTION_KIND_INT,
    )
    """Minimal number of entries in the MIP solver cliquetable before neighbourhood queries
    of the conflict graph use parallel processing. Integer, default 100000."""

    MIP_REPORT_LEVEL = ("mip_report_level", OPTION_KIND_INT)
    """MIP solver reporting level. Integer, default 1."""

    MIP_HEURISTIC_EFFORT = ("mip_heuristic_effort", OPTION_KIND_DOUBLE)
    """Effort spent for MIP heuristics. Double, default 0.05."""

    MIP_HEURISTIC_RUN_FEASIBILITY_JUMP = ("mip_heuristic_run_feasibility_jump", OPTION_KIND_BOOL)
    """Use the feasibility jump heuristic. Boolean, default True."""

    MIP_HEURISTIC_RUN_RINS = ("mip_heuristic_run_rins", OPTION_KIND_BOOL)
    """Use the RINS heuristic. Boolean, default True."""

    MIP_HEURISTIC_RUN_RENS = ("mip_heuristic_run_rens", OPTION_KIND_BOOL)
    """Use the RENS heuristic. Boolean, default True."""

    MIP_HEURISTIC_RUN_ROOT_REDUCED_COST = ("mip_heuristic_run_root_reduced_cost", OPTION_KIND_BOOL)
    """Use the rootReducedCost heuristic. Boolean, default True."""

    MIP_HEURISTIC_RUN_ZI_ROUND = ("mip_heuristic_run_zi_round", OPTION_KIND_BOOL)
    """Use the ZI Round heuristic. Boolean, default False."""

    MIP_HEURISTIC_RUN_SHIFTING = ("mip_heuristic_run_shifting", OPTION_KIND_BOOL)
    """Use the Shifting heuristic. Boolean, default False."""

    MIP_ALLOW_CUT_SEPARATION_AT_NODES = ("mip_allow_cut_separation_at_nodes", OPTION_KIND_BOOL)
    """Whether cut separation at nodes other than the root node is permitted. Boolean,
    default True."""

    MIP_MIN_LOGGING_INTERVAL = ("mip_min_logging_interval", OPTION_KIND_DOUBLE)
    """MIP minimum logging interval. Double, default 5."""

    MIP_LP_SOLVER = ("mip_lp_solver", OPTION_KIND_STRING)
    """MIP LP solver: "choose", "simplex", "ipm", "ipx" or "hipo". String, default
    "choose"."""

    MIP_IPM_SOLVER = ("mip_ipm_solver", OPTION_KIND_STRING)
    """MIP IPM solver: "choose", "ipx" or "hipo". String, default "choose"."""

    IPM_OPTIMALITY_TOLERANCE = ("ipm_optimality_tolerance", OPTION_KIND_DOUBLE)
    """IPM optimality tolerance. Double, default 1e-8."""

    MIP_SEARCH_SIMULATE_CONCURRENCY = ("mip_search_simulate_concurrency", OPTION_KIND_BOOL)
    """Simulate MIP search concurrency on a single thread. Boolean, default False."""

    IPM_ITERATION_LIMIT = ("ipm_iteration_limit", OPTION_KIND_INT)
    """Iteration limit for IPM solver. Integer, default a very large value."""

    HIPO_SYSTEM = ("hipo_system", OPTION_KIND_STRING)
    """HiPO Newton system: "choose", "augmented" or "normaleq". String, default "choose"."""

    HIPO_PARALLEL_TYPE = ("hipo_parallel_type", OPTION_KIND_STRING)
    """HiPO parallelism: "tree", "node" or "both". String, default "both"."""

    HIPO_ORDERING = ("hipo_ordering", OPTION_KIND_STRING)
    """HiPO matrix reordering: "choose", "metis", "amd" or "rcm". String, default "choose"."""

    HIPO_BLOCK_SIZE = ("hipo_block_size", OPTION_KIND_INT)
    """Block size for dense linear algebra within HiPO. Integer, default 128."""

    PDLP_ITERATION_LIMIT = ("pdlp_iteration_limit", OPTION_KIND_INT)
    """Iteration limit for PDLP solver. Integer, default a very large value."""

    PDLP_SCALING_MODE = ("pdlp_scaling_mode", OPTION_KIND_INT)
    """Scaling mode for PDLP solver (default = 5): 1 => Ruiz; 2 => L2; 4 => PC. Integer,
    default 5."""

    PDLP_RUIZ_ITERATIONS = ("pdlp_ruiz_iterations", OPTION_KIND_INT)
    """Number of Ruiz scaling iteraitons for PDLP solver. Integer, default 10."""

    PDLP_RESTART_STRATEGY = ("pdlp_restart_strategy", OPTION_KIND_INT)
    """Restart strategy for PDLP solver: 0 => off; 1 => fixed; 2 => adaptive; 3 => Halpern.
    Integer, default 2."""

    PDLP_CUPDLPC_RESTART_METHOD = ("pdlp_cupdlpc_restart_method", OPTION_KIND_INT)
    """Restart mode for cuPDLP-C solver: 0 => none; 1 => GPU (default); 2 => CPU. Integer,
    default 1."""

    PDLP_STEP_SIZE_STRATEGY = ("pdlp_step_size_strategy", OPTION_KIND_INT)
    """Step size strategy for PDLP solver: 0 => fixed; 1 => adaptive; 2 => Malitsky-Pock; 3
    => PID. Integer, default 1."""

    PDLP_OPTIMALITY_TOLERANCE = ("pdlp_optimality_tolerance", OPTION_KIND_DOUBLE)
    """PDLP optimality tolerance. Double, default 1e-7."""

    QP_ALLOW_HOT_START = ("qp_allow_hot_start", OPTION_KIND_BOOL)
    """Allow the active set QP solver to hot start. Boolean, default False."""

    QP_ITERATION_LIMIT = ("qp_iteration_limit", OPTION_KIND_INT)
    """Iteration limit for the active set QP solver. Integer, default a very large value."""

    QP_NULLSPACE_LIMIT = ("qp_nullspace_limit", OPTION_KIND_INT)
    """Nullspace limit for the active set QP solver. Integer, default 4000."""

    QP_REGULARIZATION_VALUE = ("qp_regularization_value", OPTION_KIND_DOUBLE)
    """Regularization value added to the Hessian in the active set QP solver. Double,
    default 1e-7."""

    IIS_STRATEGY = ("iis_strategy", OPTION_KIND_INT)
    """Strategy for IIS calculation: 0 => Light test; 1 => Try dual ray; 2 => Try elastic
    LP; 4 => Prioritise columns; 8 => Find true IIS; 16 => Find relaxation IIS for MIP.
    Integer, default 0."""

    IIS_TIME_LIMIT = ("iis_time_limit", OPTION_KIND_DOUBLE)
    """Time limit for computing IIS (seconds). Double, default infinity."""

    BLEND_MULTI_OBJECTIVES = ("blend_multi_objectives", OPTION_KIND_BOOL)
    """Blend multiple objectives or apply lexicographically. Boolean, default True."""

    @property
    def option_name(self) -> str:
        """Return the option name string expected by the HiGHS C API."""
        return self.value[0]

    @property
    def value_kind(self) -> str:
        """Return the value kind label for this option."""
        return self.value[1]


def build_option_settings(
    options: dict[HighsOption, object] | None,
) -> list[tuple[str, str, object]] | None:
    """Validate an option mapping and convert it to core level tuples.

    Args:
        options: The options to apply, as a mapping from
            [`HighsOption`][cyhighs.HighsOption] members to values, or `None`.
            Values must match the value kind declared by each option.

    Returns:
        A list of `(name, kind, value)` tuples ready for the compiled core, or
        `None` if no options were supplied.

    Raises:
        TypeError: If a key is not a [`HighsOption`][cyhighs.HighsOption] member
            or a value has the wrong type.
    """
    if options is None:
        return None

    settings: list[tuple[str, str, object]] = []
    for option, value in options.items():
        if not isinstance(option, HighsOption):
            raise TypeError(f"Option keys must be HighsOption members, got {option!r}")
        accepted_types = _ACCEPTED_PYTHON_TYPES[option.value_kind]
        # bool is a subclass of int, so reject it explicitly for non bool kinds.
        if option.value_kind != OPTION_KIND_BOOL and isinstance(value, bool):
            raise TypeError(f"Option {option.name} expects a {option.value_kind} value, got a bool")
        if not isinstance(value, accepted_types):
            raise TypeError(
                f"Option {option.name} expects a {option.value_kind} value, "
                f"got {type(value).__name__}"
            )
        settings.append((option.option_name, option.value_kind, value))
    return settings
