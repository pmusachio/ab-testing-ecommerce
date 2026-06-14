"""Transformation layer: clean the experiment log so each user appears once with a
consistent group/page assignment, the precondition for a valid A/B comparison.
"""
from __future__ import annotations

import logging

import pandas as pd

from src import config

logger = logging.getLogger(__name__)


class Preprocessor:
    def __init__(self, processed_path=config.PROCESSED_PATH) -> None:
        self.processed_path = processed_path

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drops rows where the assigned group and the page shown disagree, then
        removes users with more than one record, leaving one clean row per user."""
        aligned = (
            ((df[config.GROUP_COL] == config.TREATMENT) & (df[config.PAGE_COL] == config.NEW_PAGE))
            | ((df[config.GROUP_COL] == config.CONTROL) & (df[config.PAGE_COL] == config.OLD_PAGE))
        )
        clean = df[aligned].copy()
        dup_users = clean[config.USER_COL].value_counts()
        clean = clean[clean[config.USER_COL].isin(dup_users[dup_users == 1].index)]
        logger.info("Cleaned experiment: %d -> %d rows (%d misaligned, dedup applied)",
                    len(df), len(clean), int((~aligned).sum()))
        self.processed_path.parent.mkdir(parents=True, exist_ok=True)
        clean[[config.USER_COL, config.GROUP_COL, config.CONVERT_COL]].to_parquet(self.processed_path, index=False)
        return clean
