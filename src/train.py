"""Analysis layer: estimate the conversion difference between control and treatment,
run a two-proportion z-test with a confidence interval and observed power, derive
the sample size the experiment would have needed, and serialize the result.

This is an inferential A/B test, not a predictive model: the deliverable is a
decision (ship the new page or not), so there is no train/holdout split.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd
from scipy import stats

from src import config

logger = logging.getLogger(__name__)
SCHEMA_VERSION = "1.0"


def required_sample_size(p1: float, mde: float, alpha: float, power: float) -> int:
    """Per-group sample size to detect an absolute effect `mde` at a baseline `p1`."""
    p2 = min(max(p1 + mde, 1e-6), 1 - 1e-6)
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)
    pooled = (p1 + p2) / 2
    num = (z_alpha * np.sqrt(2 * pooled * (1 - pooled)) + z_beta * np.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return int(np.ceil(num / (mde ** 2)))


def observed_power(p1: float, p2: float, n1: int, n2: int, alpha: float) -> float:
    se = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    if se == 0:
        return 0.0
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z = abs(p2 - p1) / se
    return float(stats.norm.cdf(z - z_alpha) + stats.norm.cdf(-z - z_alpha))


class ABAnalyzer:
    def __init__(self, clean: pd.DataFrame, data_source: Path | None = None) -> None:
        self.df = clean
        self.data_source = data_source
        self.result: Dict[str, Any] = {}

    def analyze(self) -> Dict[str, Any]:
        g = self.df.groupby(config.GROUP_COL)[config.CONVERT_COL]
        n_c, n_t = int(g.count()[config.CONTROL]), int(g.count()[config.TREATMENT])
        x_c, x_t = int(g.sum()[config.CONTROL]), int(g.sum()[config.TREATMENT])
        p_c, p_t = x_c / n_c, x_t / n_t

        pooled = (x_c + x_t) / (n_c + n_t)
        se = np.sqrt(pooled * (1 - pooled) * (1 / n_c + 1 / n_t))
        z = (p_t - p_c) / se
        p_value = float(2 * (1 - stats.norm.cdf(abs(z))))
        diff = p_t - p_c
        se_diff = np.sqrt(p_c * (1 - p_c) / n_c + p_t * (1 - p_t) / n_t)
        ci = [float(diff - 1.96 * se_diff), float(diff + 1.96 * se_diff)]
        power = observed_power(p_c, p_t, n_c, n_t, config.ALPHA)

        decision = (
            "Reject H0: the new page changes conversion."
            if p_value < config.ALPHA else
            "Fail to reject H0: no significant difference; keep the current page."
        )
        self.result = {
            "groups": {
                config.CONTROL: {"n": n_c, "conversions": x_c, "rate": round(p_c, 5)},
                config.TREATMENT: {"n": n_t, "conversions": x_t, "rate": round(p_t, 5)},
            },
            "test": {
                "name": "Two-proportion z-test",
                "z_statistic": float(z), "p_value": p_value,
                "abs_difference": float(diff), "relative_difference": float(diff / p_c) if p_c else 0.0,
                "ci95_difference": ci, "alpha": config.ALPHA,
                "observed_power": round(power, 4), "significant": bool(p_value < config.ALPHA),
                "decision": decision,
            },
            "design": {
                "baseline_rate": round(p_c, 5),
                "required_n_per_group_at_default_mde": required_sample_size(
                    p_c, config.DEFAULT_MDE, config.ALPHA, config.POWER),
                "default_mde": config.DEFAULT_MDE,
            },
        }
        logger.info("A/B: control=%.4f treatment=%.4f p=%.4f power=%.3f -> %s",
                    p_c, p_t, p_value, power, "significant" if p_value < config.ALPHA else "not significant")
        return self.result

    def save(self) -> None:
        config.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump({"schema_version": SCHEMA_VERSION, "result": self.result,
                     "alpha": config.ALPHA, "power": config.POWER}, config.PIPELINE_PATH)
        logger.info("Analysis artifact written to %s", config.PIPELINE_PATH)
        card = {
            "schema_version": SCHEMA_VERSION,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "dataset": config.KAGGLE_DATASET, "data_sha256": self._hash(),
            "problem": "A/B test: does the new landing page change conversion?",
            "result": self.result,
        }
        config.MODEL_CARD_PATH.write_text(json.dumps(card, indent=2))
        logger.info("Model card written to %s", config.MODEL_CARD_PATH)

    def _hash(self) -> str:
        src = self.data_source or config.SAMPLE_PATH
        return hashlib.sha256(Path(src).read_bytes()).hexdigest() if src and Path(src).exists() else "unknown"
