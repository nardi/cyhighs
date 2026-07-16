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

The set of options declared here is a curated subset of the full HiGHS option
list, chosen to cover the most common needs. The value kinds match the four
typed setters in the HiGHS C API.
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
    """Master switch for all HiGHS logging. Set to False to silence the solver.
    Boolean, default True."""

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
