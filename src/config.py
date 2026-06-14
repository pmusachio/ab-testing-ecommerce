"""Central configuration: paths, dataset identity, test constants and the Dracula
palette shared by the pipeline, the serving layer and the dashboard.
"""
from __future__ import annotations

from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parents[1]
DATA_DIR: Path = BASE_DIR / "data"
RAW_DIR: Path = DATA_DIR / "raw"
PROCESSED_DIR: Path = DATA_DIR / "processed"
SAMPLE_DIR: Path = DATA_DIR / "sample"
MODELS_DIR: Path = BASE_DIR / "models"

PIPELINE_PATH: Path = MODELS_DIR / "pipeline.joblib"
MODEL_CARD_PATH: Path = MODELS_DIR / "model_card.json"
PROCESSED_PATH: Path = PROCESSED_DIR / "experiment.parquet"

SAMPLE_FILENAME: str = "ab_data_sample.csv"
SAMPLE_PATH: Path = SAMPLE_DIR / SAMPLE_FILENAME

KAGGLE_DATASET: str = "zhangluyuan/ab-testing"
RAW_FILENAME: str = "ab_data.csv"

USER_COL: str = "user_id"
GROUP_COL: str = "group"
PAGE_COL: str = "landing_page"
CONVERT_COL: str = "converted"
CONTROL: str = "control"
TREATMENT: str = "treatment"
OLD_PAGE: str = "old_page"
NEW_PAGE: str = "new_page"

ALPHA: float = 0.05
POWER: float = 0.80
SEED: int = 42

# Calculator defaults (the experiment's own numbers seed the UI).
DEFAULT_MDE: float = 0.01   # absolute minimum detectable effect

DRACULA = {
    "background": "#282a36", "current_line": "#44475a", "foreground": "#f8f8f2",
    "comment": "#6272a4", "cyan": "#8be9fd", "green": "#50fa7b", "orange": "#ffb86c",
    "pink": "#ff79c6", "purple": "#bd93f9", "red": "#ff5555", "yellow": "#f1fa8c",
}
