"""Unit tests for option validation and dispatch."""

import pytest

from cyhighs import HighsOption
from cyhighs.options import (
    OPTION_KIND_BOOL,
    OPTION_KIND_DOUBLE,
    OPTION_KIND_INT,
    OPTION_KIND_STRING,
    build_option_settings,
)


def test_build_option_settings_returns_none_for_none():
    assert build_option_settings(None) is None


def test_build_option_settings_produces_name_kind_value_tuples():
    settings = build_option_settings(
        {
            HighsOption.TIME_LIMIT: 12.5,
            HighsOption.OUTPUT_FLAG: False,
            HighsOption.THREADS: 4,
            HighsOption.SOLVER: "simplex",
        }
    )
    assert settings is not None
    settings_by_name = {name: (kind, value) for name, kind, value in settings}
    assert settings_by_name["time_limit"] == (OPTION_KIND_DOUBLE, 12.5)
    assert settings_by_name["output_flag"] == (OPTION_KIND_BOOL, False)
    assert settings_by_name["threads"] == (OPTION_KIND_INT, 4)
    assert settings_by_name["solver"] == (OPTION_KIND_STRING, "simplex")


def test_integer_option_accepts_python_int():
    settings = build_option_settings({HighsOption.THREADS: 2})
    assert settings == [("threads", OPTION_KIND_INT, 2)]


def test_double_option_accepts_int_value():
    # An int is an acceptable double value.
    settings = build_option_settings({HighsOption.TIME_LIMIT: 5})
    assert settings == [("time_limit", OPTION_KIND_DOUBLE, 5)]


def test_bool_option_rejects_int():
    with pytest.raises(TypeError):
        build_option_settings({HighsOption.OUTPUT_FLAG: 1})


def test_int_option_rejects_bool():
    with pytest.raises(TypeError):
        build_option_settings({HighsOption.THREADS: True})


def test_string_option_rejects_number():
    with pytest.raises(TypeError):
        build_option_settings({HighsOption.SOLVER: 3})


def test_non_option_key_is_rejected():
    with pytest.raises(TypeError):
        # A plain string key is deliberately the wrong type here, so the static
        # type check is suppressed for this negative test.
        build_option_settings({"time_limit": 10.0})  # ty: ignore[invalid-argument-type]
