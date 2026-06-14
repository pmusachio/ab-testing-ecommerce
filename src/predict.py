"""Serving layer: load the analysis artifact and expose the test result plus an
experiment-design calculator (sample size and power). No model is trained here.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

from src import config
from src.train import observed_power, required_sample_size

logger = logging.getLogger(__name__)


class Predictor:
    def __init__(self, artifact_path: Path = config.PIPELINE_PATH) -> None:
        import joblib

        if not Path(artifact_path).exists():
            raise FileNotFoundError(f"No artifact at {artifact_path}. Run `python -m src.pipeline` first.")
        art = joblib.load(artifact_path)
        self.result: Dict[str, Any] = art["result"]

    def groups(self) -> Dict[str, Any]:
        return self.result["groups"]

    def test(self) -> Dict[str, Any]:
        return self.result["test"]

    def sample_size(self, baseline: float, mde: float,
                    alpha: float = config.ALPHA, power: float = config.POWER) -> int:
        return required_sample_size(baseline, mde, alpha, power)

    def power(self, baseline: float, mde: float, n_per_group: int, alpha: float = config.ALPHA) -> float:
        return observed_power(baseline, baseline + mde, n_per_group, n_per_group, alpha)
