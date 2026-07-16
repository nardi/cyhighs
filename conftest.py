"""Pytest configuration shared by the test suite and the documentation examples.

HiGHS prints its solver log to stdout by default, and the public API keeps that
default in place. During the test session that output is just noise, so it is
silenced here at the single point where every solve builds its option settings:
the ``build_option_settings`` call inside ``cyhighs.validation``. Only that bound
reference is replaced, so the library default and the unit tests that exercise
``cyhighs.options.build_option_settings`` directly are left untouched. A test or
doc example that explicitly sets ``OUTPUT_FLAG`` still wins, because the default
is only filled in when the flag is absent.
"""

import cyhighs.validation as _validation
from cyhighs.options import HighsOption
from cyhighs.options import build_option_settings as _build_option_settings


def _quiet_build_option_settings(options):
    merged = dict(options) if options else {}
    merged.setdefault(HighsOption.OUTPUT_FLAG, False)
    return _build_option_settings(merged)


_validation.build_option_settings = _quiet_build_option_settings
