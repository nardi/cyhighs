"""Pytest configuration shared by the test suite and the documentation examples.

HiGHS prints its solver log to stdout by default, and the public API keeps that
default in place. During the test session that output is just noise, so an
autouse fixture silences it at the single point where every solve builds its
option settings: the ``build_option_settings`` reference used inside
``cyhighs.validation``. Only that reference is patched, so the library default
and the unit tests that exercise ``cyhighs.options.build_option_settings``
directly are left untouched. A test or doc example that sets ``OUTPUT_FLAG``
explicitly still wins, because the default is only filled in when it is absent.
"""

from __future__ import annotations

import pytest

import cyhighs.validation as validation
from cyhighs.options import HighsOption, build_option_settings


def _quiet_build_option_settings(
    options: dict[HighsOption, object] | None,
) -> list[tuple[str, str, object]] | None:
    merged: dict[HighsOption, object] = dict(options) if options else {}
    merged.setdefault(HighsOption.OUTPUT_FLAG, False)
    return build_option_settings(merged)


@pytest.fixture(autouse=True)
def _silence_highs_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(validation, "build_option_settings", _quiet_build_option_settings)
