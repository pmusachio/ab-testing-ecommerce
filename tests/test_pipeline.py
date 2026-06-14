"""Smoke tests for the cleaning contract and the analysis serving surface."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import config  # noqa: E402
from src.predict import Predictor  # noqa: E402
from src.preprocessing import Preprocessor  # noqa: E402


@pytest.fixture(scope="module")
def sample():
    return pd.read_csv(config.SAMPLE_PATH)


def test_cleaning_aligns_group_and_page(sample):
    clean = Preprocessor().run(sample)
    aligned = (((clean[config.GROUP_COL] == config.TREATMENT) & (clean[config.PAGE_COL] == config.NEW_PAGE))
               | ((clean[config.GROUP_COL] == config.CONTROL) & (clean[config.PAGE_COL] == config.OLD_PAGE)))
    assert aligned.all()
    assert clean[config.USER_COL].duplicated().sum() == 0


def test_result_contract():
    pred = Predictor()
    groups = pred.groups()
    assert config.CONTROL in groups and config.TREATMENT in groups
    for g in groups.values():
        assert 0.0 <= g["rate"] <= 1.0 and g["n"] > 0
    test = pred.test()
    assert 0.0 <= test["p_value"] <= 1.0
    assert "decision" in test


def test_sample_size_increases_for_smaller_effect():
    pred = Predictor()
    big = pred.sample_size(0.12, 0.02)
    small = pred.sample_size(0.12, 0.005)
    assert small > big > 0


def test_power_in_unit_interval():
    pred = Predictor()
    p = pred.power(0.12, 0.01, 17000)
    assert 0.0 <= p <= 1.0
