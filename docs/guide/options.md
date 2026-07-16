# Options

[`HighsOption`][cyhighs.HighsOption] covers every user-settable HiGHS option.
See [Solver options](array-interface.md#solver-options) for how options are
actually passed to a solve, and the [API reference][cyhighs.HighsOption] for
each option's full description, type and default.

HiGHS itself splits its options into two tiers. **Basic** options are the ones
most users need day to day. **Advanced** options tune solver internals:
numerical tolerances, algorithm strategy selection, and similar knobs. They
are safe to set, but rarely necessary. If you are not sure whether you need
one, you probably do not. This page indexes every option, grouped by topic and
then by tier, as a map into the reference.

## General

Run control, tolerances, scaling, and other options that apply across
solvers.

### Basic

| Option | Description |
|---|---|
| [`SOLVER`][cyhighs.HighsOption.SOLVER] | Which algorithm to use. |
| [`PARALLEL`][cyhighs.HighsOption.PARALLEL] | Parallelism control. |
| [`THREADS`][cyhighs.HighsOption.THREADS] | Number of threads to use. |
| [`TIME_LIMIT`][cyhighs.HighsOption.TIME_LIMIT] | Wall clock time limit for the solve. |
| [`RUN_CROSSOVER`][cyhighs.HighsOption.RUN_CROSSOVER] | Whether to run crossover after an interior point solve. |
| [`RANGING`][cyhighs.HighsOption.RANGING] | Compute cost, bound, RHS and basic solution ranging. |
| [`RANDOM_SEED`][cyhighs.HighsOption.RANDOM_SEED] | Seed for the random number generator. |
| [`OBJECTIVE_BOUND`][cyhighs.HighsOption.OBJECTIVE_BOUND] | Objective bound that stops the solve when reached. |
| [`OBJECTIVE_TARGET`][cyhighs.HighsOption.OBJECTIVE_TARGET] | Objective target that stops the solve when reached. |
| [`USER_OBJECTIVE_SCALE`][cyhighs.HighsOption.USER_OBJECTIVE_SCALE] | Exponent of power-of-two objective scaling. |
| [`USER_BOUND_SCALE`][cyhighs.HighsOption.USER_BOUND_SCALE] | Exponent of power-of-two bound scaling. |
| [`INFINITE_COST`][cyhighs.HighsOption.INFINITE_COST] | Limit above which a cost coefficient is treated as infinite. |
| [`INFINITE_BOUND`][cyhighs.HighsOption.INFINITE_BOUND] | Limit above which a bound is treated as infinite. |
| [`SMALL_MATRIX_VALUE`][cyhighs.HighsOption.SMALL_MATRIX_VALUE] | Limit below which a matrix entry is treated as zero. |
| [`LARGE_MATRIX_VALUE`][cyhighs.HighsOption.LARGE_MATRIX_VALUE] | Limit above which a matrix entry is treated as infinite. |
| [`KKT_TOLERANCE`][cyhighs.HighsOption.KKT_TOLERANCE] | Combined tolerance for all feasibility and optimality measures. |
| [`PRIMAL_FEASIBILITY_TOLERANCE`][cyhighs.HighsOption.PRIMAL_FEASIBILITY_TOLERANCE] | Tolerance for primal feasibility. |
| [`DUAL_FEASIBILITY_TOLERANCE`][cyhighs.HighsOption.DUAL_FEASIBILITY_TOLERANCE] | Tolerance for dual feasibility. |
| [`PRIMAL_RESIDUAL_TOLERANCE`][cyhighs.HighsOption.PRIMAL_RESIDUAL_TOLERANCE] | Primal residual tolerance. |
| [`DUAL_RESIDUAL_TOLERANCE`][cyhighs.HighsOption.DUAL_RESIDUAL_TOLERANCE] | Dual residual tolerance. |
| [`OPTIMALITY_TOLERANCE`][cyhighs.HighsOption.OPTIMALITY_TOLERANCE] | Optimality tolerance. |
| [`HIGHS_DEBUG_LEVEL`][cyhighs.HighsOption.HIGHS_DEBUG_LEVEL] | Internal debugging verbosity. |
| [`HIGHS_ANALYSIS_LEVEL`][cyhighs.HighsOption.HIGHS_ANALYSIS_LEVEL] | Analysis level in HiGHS. |

### Advanced

| Option | Description |
|---|---|
| [`ALLOW_UNBOUNDED_OR_INFEASIBLE`][cyhighs.HighsOption.ALLOW_UNBOUNDED_OR_INFEASIBLE] | Whether the ambiguous unbounded-or-infeasible status may be reported. |
| [`COST_SCALE_FACTOR`][cyhighs.HighsOption.COST_SCALE_FACTOR] | Scaling factor for costs. |
| [`ALLOWED_MATRIX_SCALE_FACTOR`][cyhighs.HighsOption.ALLOWED_MATRIX_SCALE_FACTOR] | Largest power-of-two factor permitted when scaling the constraint matrix. |
| [`ALLOWED_COST_SCALE_FACTOR`][cyhighs.HighsOption.ALLOWED_COST_SCALE_FACTOR] | Largest power-of-two factor permitted when scaling the costs. |

## Presolve

### Basic

| Option | Description |
|---|---|
| [`PRESOLVE`][cyhighs.HighsOption.PRESOLVE] | Presolve control: off, choose, or on. |
| [`WRITE_PRESOLVED_MODEL_TO_FILE`][cyhighs.HighsOption.WRITE_PRESOLVED_MODEL_TO_FILE] | Write the presolved model to a file. |
| [`WRITE_PRESOLVED_MODEL_FILE`][cyhighs.HighsOption.WRITE_PRESOLVED_MODEL_FILE] | Presolved model file path. |
| [`MIP_ROOT_PRESOLVE_ONLY`][cyhighs.HighsOption.MIP_ROOT_PRESOLVE_ONLY] | Whether MIP presolve is only applied at the root node. |

### Advanced

| Option | Description |
|---|---|
| [`USE_IMPLIED_BOUNDS_FROM_PRESOLVE`][cyhighs.HighsOption.USE_IMPLIED_BOUNDS_FROM_PRESOLVE] | Use relaxed implied bounds from presolve. |
| [`LP_PRESOLVE_REQUIRES_BASIS_POSTSOLVE`][cyhighs.HighsOption.LP_PRESOLVE_REQUIRES_BASIS_POSTSOLVE] | Prevents LP presolve steps for which postsolve cannot maintain a basis. |
| [`PRESOLVE_PIVOT_THRESHOLD`][cyhighs.HighsOption.PRESOLVE_PIVOT_THRESHOLD] | Matrix factorization pivot threshold for substitutions in presolve. |
| [`PRESOLVE_REDUCTION_LIMIT`][cyhighs.HighsOption.PRESOLVE_REDUCTION_LIMIT] | Limit on the number of presolve reductions. |
| [`RESTART_PRESOLVE_REDUCTION_LIMIT`][cyhighs.HighsOption.RESTART_PRESOLVE_REDUCTION_LIMIT] | Limit on further presolve reductions on MIP restart. |
| [`PRESOLVE_RULE_OFF`][cyhighs.HighsOption.PRESOLVE_RULE_OFF] | Bit mask of presolve rules that are not allowed, see [`PresolveRule`][cyhighs.PresolveRule]. |
| [`PRESOLVE_RULE_TEST`][cyhighs.HighsOption.PRESOLVE_RULE_TEST] | A single [`PresolveRule`][cyhighs.PresolveRule] to test in isolation. Development use only. |
| [`PRESOLVE_RULE_LOGGING`][cyhighs.HighsOption.PRESOLVE_RULE_LOGGING] | Log the effectiveness of presolve rules for LP. |
| [`PRESOLVE_REMOVE_SLACKS`][cyhighs.HighsOption.PRESOLVE_REMOVE_SLACKS] | Remove slacks after presolve. |
| [`PRESOLVE_SUBSTITUTION_MAXFILLIN`][cyhighs.HighsOption.PRESOLVE_SUBSTITUTION_MAXFILLIN] | Maximal fillin allowed for substitutions in presolve. |

[`PresolveRule`][cyhighs.PresolveRule] names each individual presolve
reduction so that `PRESOLVE_RULE_OFF` and `PRESOLVE_RULE_TEST` do not have to
be set with raw bit positions:

```python
from cyhighs import HighsOption, PresolveRule

options = {
    HighsOption.PRESOLVE_RULE_OFF: PresolveRule.mask(PresolveRule.PROBING, PresolveRule.SPARSIFY),
}
```

## Simplex

### Basic

| Option | Description |
|---|---|
| [`SIMPLEX_STRATEGY`][cyhighs.HighsOption.SIMPLEX_STRATEGY] | Strategy for the simplex solver. |
| [`SIMPLEX_SCALE_STRATEGY`][cyhighs.HighsOption.SIMPLEX_SCALE_STRATEGY] | Simplex scaling strategy. |
| [`SIMPLEX_CRASH_STRATEGY`][cyhighs.HighsOption.SIMPLEX_CRASH_STRATEGY] | Strategy for simplex crash. |
| [`SIMPLEX_DUAL_EDGE_WEIGHT_STRATEGY`][cyhighs.HighsOption.SIMPLEX_DUAL_EDGE_WEIGHT_STRATEGY] | Strategy for simplex dual edge weights. |
| [`SIMPLEX_PRIMAL_EDGE_WEIGHT_STRATEGY`][cyhighs.HighsOption.SIMPLEX_PRIMAL_EDGE_WEIGHT_STRATEGY] | Strategy for simplex primal edge weights. |
| [`SIMPLEX_ITERATION_LIMIT`][cyhighs.HighsOption.SIMPLEX_ITERATION_LIMIT] | Iteration limit for the simplex solver. |
| [`SIMPLEX_UPDATE_LIMIT`][cyhighs.HighsOption.SIMPLEX_UPDATE_LIMIT] | Limit on the number of simplex UPDATE operations. |
| [`SIMPLEX_MIN_CONCURRENCY`][cyhighs.HighsOption.SIMPLEX_MIN_CONCURRENCY] | Minimum level of concurrency in parallel simplex. |
| [`SIMPLEX_MAX_CONCURRENCY`][cyhighs.HighsOption.SIMPLEX_MAX_CONCURRENCY] | Maximum level of concurrency in parallel simplex. |

### Advanced

| Option | Description |
|---|---|
| [`SIMPLEX_DUALIZE_STRATEGY`][cyhighs.HighsOption.SIMPLEX_DUALIZE_STRATEGY] | Strategy for dualizing before simplex. |
| [`SIMPLEX_PERMUTE_STRATEGY`][cyhighs.HighsOption.SIMPLEX_PERMUTE_STRATEGY] | Strategy for permuting before simplex. |
| [`MAX_DUAL_SIMPLEX_CLEANUP_LEVEL`][cyhighs.HighsOption.MAX_DUAL_SIMPLEX_CLEANUP_LEVEL] | Max level of dual simplex cleanup. |
| [`MAX_DUAL_SIMPLEX_PHASE1_CLEANUP_LEVEL`][cyhighs.HighsOption.MAX_DUAL_SIMPLEX_PHASE1_CLEANUP_LEVEL] | Max level of dual simplex phase 1 cleanup. |
| [`SIMPLEX_PRICE_STRATEGY`][cyhighs.HighsOption.SIMPLEX_PRICE_STRATEGY] | Strategy for PRICE in simplex. |
| [`SIMPLEX_UNSCALED_SOLUTION_STRATEGY`][cyhighs.HighsOption.SIMPLEX_UNSCALED_SOLUTION_STRATEGY] | Strategy for solving the unscaled LP in simplex. |
| [`NO_UNNECESSARY_REBUILD_REFACTOR`][cyhighs.HighsOption.NO_UNNECESSARY_REBUILD_REFACTOR] | No unnecessary refactorization on simplex rebuild. |
| [`REBUILD_REFACTOR_SOLUTION_ERROR_TOLERANCE`][cyhighs.HighsOption.REBUILD_REFACTOR_SOLUTION_ERROR_TOLERANCE] | Tolerance on solution error before refactorizing on simplex rebuild. |
| [`DUAL_STEEPEST_EDGE_WEIGHT_ERROR_TOLERANCE`][cyhighs.HighsOption.DUAL_STEEPEST_EDGE_WEIGHT_ERROR_TOLERANCE] | Tolerance on dual steepest edge weight errors. |
| [`DUAL_STEEPEST_EDGE_WEIGHT_LOG_ERROR_THRESHOLD`][cyhighs.HighsOption.DUAL_STEEPEST_EDGE_WEIGHT_LOG_ERROR_THRESHOLD] | Threshold on dual steepest edge weight errors for the Devex switch. |
| [`DUAL_SIMPLEX_COST_PERTURBATION_MULTIPLIER`][cyhighs.HighsOption.DUAL_SIMPLEX_COST_PERTURBATION_MULTIPLIER] | Dual simplex cost perturbation multiplier. |
| [`PRIMAL_SIMPLEX_BOUND_PERTURBATION_MULTIPLIER`][cyhighs.HighsOption.PRIMAL_SIMPLEX_BOUND_PERTURBATION_MULTIPLIER] | Primal simplex bound perturbation multiplier. |
| [`DUAL_SIMPLEX_PIVOT_GROWTH_TOLERANCE`][cyhighs.HighsOption.DUAL_SIMPLEX_PIVOT_GROWTH_TOLERANCE] | Dual simplex pivot growth tolerance. |
| [`FACTOR_PIVOT_THRESHOLD`][cyhighs.HighsOption.FACTOR_PIVOT_THRESHOLD] | Matrix factorization pivot threshold. |
| [`FACTOR_PIVOT_TOLERANCE`][cyhighs.HighsOption.FACTOR_PIVOT_TOLERANCE] | Matrix factorization pivot tolerance. |
| [`USE_ORIGINAL_HFACTOR_LOGIC`][cyhighs.HighsOption.USE_ORIGINAL_HFACTOR_LOGIC] | Use original HFactor logic for sparse vs hyper-sparse TRANs. |
| [`LESS_INFEASIBLE_DSE_CHECK`][cyhighs.HighsOption.LESS_INFEASIBLE_DSE_CHECK] | Check whether the LP is a candidate for less infeasible dual steepest edge. |
| [`LESS_INFEASIBLE_DSE_CHOOSE_ROW`][cyhighs.HighsOption.LESS_INFEASIBLE_DSE_CHOOSE_ROW] | Use less infeasible dual steepest edge if the LP has the right properties. |

## LP solvers (interior point, HiPO, PDLP, QP)

### Basic

| Option | Description |
|---|---|
| [`IPM_OPTIMALITY_TOLERANCE`][cyhighs.HighsOption.IPM_OPTIMALITY_TOLERANCE] | IPM optimality tolerance. |
| [`IPM_ITERATION_LIMIT`][cyhighs.HighsOption.IPM_ITERATION_LIMIT] | Iteration limit for the IPM solver. |
| [`HIPO_SYSTEM`][cyhighs.HighsOption.HIPO_SYSTEM] | HiPO Newton system. |
| [`HIPO_PARALLEL_TYPE`][cyhighs.HighsOption.HIPO_PARALLEL_TYPE] | HiPO parallelism. |
| [`HIPO_ORDERING`][cyhighs.HighsOption.HIPO_ORDERING] | HiPO matrix reordering. |
| [`HIPO_BLOCK_SIZE`][cyhighs.HighsOption.HIPO_BLOCK_SIZE] | Block size for dense linear algebra within HiPO. |
| [`PDLP_ITERATION_LIMIT`][cyhighs.HighsOption.PDLP_ITERATION_LIMIT] | Iteration limit for the PDLP solver. |
| [`PDLP_SCALING_MODE`][cyhighs.HighsOption.PDLP_SCALING_MODE] | Scaling mode for the PDLP solver. |
| [`PDLP_RUIZ_ITERATIONS`][cyhighs.HighsOption.PDLP_RUIZ_ITERATIONS] | Number of Ruiz scaling iterations for the PDLP solver. |
| [`PDLP_RESTART_STRATEGY`][cyhighs.HighsOption.PDLP_RESTART_STRATEGY] | Restart strategy for the PDLP solver. |
| [`PDLP_CUPDLPC_RESTART_METHOD`][cyhighs.HighsOption.PDLP_CUPDLPC_RESTART_METHOD] | Restart mode for the cuPDLP-C solver. |
| [`PDLP_STEP_SIZE_STRATEGY`][cyhighs.HighsOption.PDLP_STEP_SIZE_STRATEGY] | Step size strategy for the PDLP solver. |
| [`PDLP_OPTIMALITY_TOLERANCE`][cyhighs.HighsOption.PDLP_OPTIMALITY_TOLERANCE] | PDLP optimality tolerance. |
| [`QP_ALLOW_HOT_START`][cyhighs.HighsOption.QP_ALLOW_HOT_START] | Allow the active set QP solver to hot start. |
| [`QP_ITERATION_LIMIT`][cyhighs.HighsOption.QP_ITERATION_LIMIT] | Iteration limit for the active set QP solver. |
| [`QP_NULLSPACE_LIMIT`][cyhighs.HighsOption.QP_NULLSPACE_LIMIT] | Nullspace limit for the active set QP solver. |
| [`QP_REGULARIZATION_VALUE`][cyhighs.HighsOption.QP_REGULARIZATION_VALUE] | Regularization value added to the Hessian in the active set QP solver. |

### Advanced

| Option | Description |
|---|---|
| [`IPX_DUALIZE_STRATEGY`][cyhighs.HighsOption.IPX_DUALIZE_STRATEGY] | Strategy for dualizing before IPX. |
| [`START_CROSSOVER_TOLERANCE`][cyhighs.HighsOption.START_CROSSOVER_TOLERANCE] | Tolerance to be satisfied before IPM crossover will start. |
| [`RUN_CENTRING`][cyhighs.HighsOption.RUN_CENTRING] | Perform centring steps to compute the analytic centre before crossover. |
| [`MAX_CENTRING_STEPS`][cyhighs.HighsOption.MAX_CENTRING_STEPS] | Maximum number of steps used when computing the analytic centre. |
| [`CENTRING_RATIO_TOLERANCE`][cyhighs.HighsOption.CENTRING_RATIO_TOLERANCE] | Tolerance at which centring stops. |

## MIP

### Basic

| Option | Description |
|---|---|
| [`MIP_REL_GAP`][cyhighs.HighsOption.MIP_REL_GAP] | Relative optimality gap at which a MIP solve stops. |
| [`MIP_ABS_GAP`][cyhighs.HighsOption.MIP_ABS_GAP] | Absolute optimality gap at which a MIP solve stops. |
| [`MIP_FEASIBILITY_TOLERANCE`][cyhighs.HighsOption.MIP_FEASIBILITY_TOLERANCE] | Feasibility tolerance for integer variables. |
| [`MIP_MAX_NODES`][cyhighs.HighsOption.MIP_MAX_NODES] | Maximum number of branch and bound nodes. |
| [`MIP_DETECT_SYMMETRY`][cyhighs.HighsOption.MIP_DETECT_SYMMETRY] | Whether MIP symmetry should be detected. |
| [`MIP_ALLOW_RESTART`][cyhighs.HighsOption.MIP_ALLOW_RESTART] | Whether MIP restart is permitted. |
| [`MIP_MAX_STALL_NODES`][cyhighs.HighsOption.MIP_MAX_STALL_NODES] | Max number of nodes where the estimate is above the cutoff bound. |
| [`MIP_MAX_START_NODES`][cyhighs.HighsOption.MIP_MAX_START_NODES] | Max number of nodes when completing a partial MIP start. |
| [`MIP_IMPROVING_SOLUTION_SAVE`][cyhighs.HighsOption.MIP_IMPROVING_SOLUTION_SAVE] | Whether improving MIP solutions should be saved. |
| [`MIP_IMPROVING_SOLUTION_REPORT_SPARSE`][cyhighs.HighsOption.MIP_IMPROVING_SOLUTION_REPORT_SPARSE] | Whether improving MIP solutions should be reported in sparse format. |
| [`MIP_IMPROVING_SOLUTION_FILE`][cyhighs.HighsOption.MIP_IMPROVING_SOLUTION_FILE] | File for reporting improving MIP solutions. |
| [`MIP_LIFTING_FOR_PROBING`][cyhighs.HighsOption.MIP_LIFTING_FOR_PROBING] | Level of lifting for probing that is used. |
| [`MIP_MAX_LEAVES`][cyhighs.HighsOption.MIP_MAX_LEAVES] | Max number of leaf nodes. |
| [`MIP_MAX_IMPROVING_SOLS`][cyhighs.HighsOption.MIP_MAX_IMPROVING_SOLS] | Limit on the number of improving solutions found. |
| [`MIP_LP_AGE_LIMIT`][cyhighs.HighsOption.MIP_LP_AGE_LIMIT] | Maximal age of dynamic LP rows before removal from the LP relaxation. |
| [`MIP_POOL_AGE_LIMIT`][cyhighs.HighsOption.MIP_POOL_AGE_LIMIT] | Maximal age of rows in the cutpool before they are deleted. |
| [`MIP_POOL_SOFT_LIMIT`][cyhighs.HighsOption.MIP_POOL_SOFT_LIMIT] | Soft limit on the number of rows in the cutpool. |
| [`MIP_PSCOST_MINRELIABLE`][cyhighs.HighsOption.MIP_PSCOST_MINRELIABLE] | Minimal observations before pseudo costs are considered reliable. |
| [`MIP_MIN_CLIQUETABLE_ENTRIES_FOR_PARALLELISM`][cyhighs.HighsOption.MIP_MIN_CLIQUETABLE_ENTRIES_FOR_PARALLELISM] | Cliquetable size threshold for parallel conflict graph queries. |
| [`MIP_REPORT_LEVEL`][cyhighs.HighsOption.MIP_REPORT_LEVEL] | MIP solver reporting level. |
| [`MIP_HEURISTIC_EFFORT`][cyhighs.HighsOption.MIP_HEURISTIC_EFFORT] | Effort spent for MIP heuristics. |
| [`MIP_HEURISTIC_RUN_FEASIBILITY_JUMP`][cyhighs.HighsOption.MIP_HEURISTIC_RUN_FEASIBILITY_JUMP] | Use the feasibility jump heuristic. |
| [`MIP_HEURISTIC_RUN_RINS`][cyhighs.HighsOption.MIP_HEURISTIC_RUN_RINS] | Use the RINS heuristic. |
| [`MIP_HEURISTIC_RUN_RENS`][cyhighs.HighsOption.MIP_HEURISTIC_RUN_RENS] | Use the RENS heuristic. |
| [`MIP_HEURISTIC_RUN_ROOT_REDUCED_COST`][cyhighs.HighsOption.MIP_HEURISTIC_RUN_ROOT_REDUCED_COST] | Use the rootReducedCost heuristic. |
| [`MIP_HEURISTIC_RUN_ZI_ROUND`][cyhighs.HighsOption.MIP_HEURISTIC_RUN_ZI_ROUND] | Use the ZI Round heuristic. |
| [`MIP_HEURISTIC_RUN_SHIFTING`][cyhighs.HighsOption.MIP_HEURISTIC_RUN_SHIFTING] | Use the Shifting heuristic. |
| [`MIP_ALLOW_CUT_SEPARATION_AT_NODES`][cyhighs.HighsOption.MIP_ALLOW_CUT_SEPARATION_AT_NODES] | Whether cut separation is permitted away from the root node. |
| [`MIP_MIN_LOGGING_INTERVAL`][cyhighs.HighsOption.MIP_MIN_LOGGING_INTERVAL] | MIP minimum logging interval. |
| [`MIP_LP_SOLVER`][cyhighs.HighsOption.MIP_LP_SOLVER] | MIP LP solver choice. |
| [`MIP_IPM_SOLVER`][cyhighs.HighsOption.MIP_IPM_SOLVER] | MIP IPM solver choice. |
| [`MIP_SEARCH_SIMULATE_CONCURRENCY`][cyhighs.HighsOption.MIP_SEARCH_SIMULATE_CONCURRENCY] | Simulate MIP search concurrency on a single thread. |

### Advanced

| Option | Description |
|---|---|
| [`SOLVE_RELAXATION`][cyhighs.HighsOption.SOLVE_RELAXATION] | Solve the relaxation of discrete model components instead of the discrete model. |

## Logging & file I/O

### Basic

| Option | Description |
|---|---|
| [`OUTPUT_FLAG`][cyhighs.HighsOption.OUTPUT_FLAG] | Master switch for all HiGHS logging. |
| [`LOG_TO_CONSOLE`][cyhighs.HighsOption.LOG_TO_CONSOLE] | Whether log messages are written to the console. |
| [`TIMELESS_LOG`][cyhighs.HighsOption.TIMELESS_LOG] | Suppression of time-based data in logging. |
| [`LOG_FILE`][cyhighs.HighsOption.LOG_FILE] | Log file path. |
| [`WRITE_MODEL_TO_FILE`][cyhighs.HighsOption.WRITE_MODEL_TO_FILE] | Write the model to a file. |
| [`WRITE_SOLUTION_TO_FILE`][cyhighs.HighsOption.WRITE_SOLUTION_TO_FILE] | Write the primal and dual solution to a file. |
| [`WRITE_SOLUTION_STYLE`][cyhighs.HighsOption.WRITE_SOLUTION_STYLE] | Style of the solution file. |
| [`GLPSOL_COST_ROW_LOCATION`][cyhighs.HighsOption.GLPSOL_COST_ROW_LOCATION] | Location of the cost row for a Glpsol file. |
| [`ICRASH`][cyhighs.HighsOption.ICRASH] | Run iCrash. |
| [`ICRASH_DUALIZE`][cyhighs.HighsOption.ICRASH_DUALIZE] | Dualize strategy for iCrash. |
| [`ICRASH_STRATEGY`][cyhighs.HighsOption.ICRASH_STRATEGY] | Strategy for iCrash. |
| [`ICRASH_STARTING_WEIGHT`][cyhighs.HighsOption.ICRASH_STARTING_WEIGHT] | iCrash starting weight. |
| [`ICRASH_ITERATIONS`][cyhighs.HighsOption.ICRASH_ITERATIONS] | iCrash iterations. |
| [`ICRASH_APPROX_ITER`][cyhighs.HighsOption.ICRASH_APPROX_ITER] | iCrash approximate minimization iterations. |
| [`ICRASH_EXACT`][cyhighs.HighsOption.ICRASH_EXACT] | Exact subproblem solution for iCrash. |
| [`ICRASH_BREAKPOINTS`][cyhighs.HighsOption.ICRASH_BREAKPOINTS] | iCrash breakpoints setting. |
| [`READ_SOLUTION_FILE`][cyhighs.HighsOption.READ_SOLUTION_FILE] | Read solution file path. |
| [`READ_BASIS_FILE`][cyhighs.HighsOption.READ_BASIS_FILE] | Read basis file path. |
| [`WRITE_MODEL_FILE`][cyhighs.HighsOption.WRITE_MODEL_FILE] | Write model file path. |
| [`SOLUTION_FILE`][cyhighs.HighsOption.SOLUTION_FILE] | Write solution file path. |
| [`WRITE_BASIS_FILE`][cyhighs.HighsOption.WRITE_BASIS_FILE] | Write basis file path. |
| [`WRITE_IIS_MODEL_FILE`][cyhighs.HighsOption.WRITE_IIS_MODEL_FILE] | Write IIS model file path. |

### Advanced

| Option | Description |
|---|---|
| [`LOG_DEV_LEVEL`][cyhighs.HighsOption.LOG_DEV_LEVEL] | Output development messages. |
| [`LOG_GITHASH`][cyhighs.HighsOption.LOG_GITHASH] | Log the githash. |
| [`WRITE_MATRIX_IMAGE`][cyhighs.HighsOption.WRITE_MATRIX_IMAGE] | Write an image of the constraint matrix to a file. |
| [`WRITE_HESSIAN_IMAGE`][cyhighs.HighsOption.WRITE_HESSIAN_IMAGE] | Write an image of the Hessian to a file. |
| [`MPS_PARSER_TYPE_FREE`][cyhighs.HighsOption.MPS_PARSER_TYPE_FREE] | Use the free format MPS file reader. |
| [`KEEP_N_ROWS`][cyhighs.HighsOption.KEEP_N_ROWS] | How to handle multiple N-rows in MPS files. |
| [`USE_WARM_START`][cyhighs.HighsOption.USE_WARM_START] | Use any warm start that is available. |

## IIS

Options for computing an irreducible infeasible subsystem (IIS) on an
infeasible model. There is no advanced tier for these options.

| Option | Description |
|---|---|
| [`IIS_STRATEGY`][cyhighs.HighsOption.IIS_STRATEGY] | Strategy for computing an IIS. |
| [`IIS_TIME_LIMIT`][cyhighs.HighsOption.IIS_TIME_LIMIT] | Time limit for computing an IIS. |

## Multi-objective

| Option | Description |
|---|---|
| [`BLEND_MULTI_OBJECTIVES`][cyhighs.HighsOption.BLEND_MULTI_OBJECTIVES] | Blend multiple objectives or apply lexicographically. |

There is no advanced tier for multi-objective options.
