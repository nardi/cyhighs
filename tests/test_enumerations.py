"""Tests that the Python enumerations stay in sync with the HiGHS C constants."""

import cyhighs
from cyhighs import ModelStatus, ObjectiveSense, VariableType
from cyhighs._core import HIGHS_CONSTANTS


def test_variable_type_values_match_c_constants():
    assert VariableType.CONTINUOUS == HIGHS_CONSTANTS["kHighsVarTypeContinuous"]
    assert VariableType.INTEGER == HIGHS_CONSTANTS["kHighsVarTypeInteger"]
    assert VariableType.SEMI_CONTINUOUS == HIGHS_CONSTANTS["kHighsVarTypeSemiContinuous"]
    assert VariableType.SEMI_INTEGER == HIGHS_CONSTANTS["kHighsVarTypeSemiInteger"]
    assert VariableType.IMPLICIT_INTEGER == HIGHS_CONSTANTS["kHighsVarTypeImplicitInteger"]


def test_objective_sense_values_match_c_constants():
    assert ObjectiveSense.MINIMIZE == HIGHS_CONSTANTS["kHighsObjSenseMinimize"]
    assert ObjectiveSense.MAXIMIZE == HIGHS_CONSTANTS["kHighsObjSenseMaximize"]


def test_model_status_has_expected_core_members():
    # Spot check the statuses users most often inspect.
    assert ModelStatus.OPTIMAL == 7
    assert ModelStatus.INFEASIBLE == 8
    assert ModelStatus.UNBOUNDED == 10


def test_version_is_reported():
    version = cyhighs.highs_version()
    assert version.startswith("1.15")


def test_infinity_is_large():
    assert cyhighs.highs_infinity() >= 1e30
