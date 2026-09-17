"""
Unit tests for Person 2 Scaffolding (paths, directories, and central configuration).
"""

from pathlib import Path
from src.utils.paths import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DIR,
    PROCESSED_DIR,
    SPLITS_DIR,
    METADATA_CSV,
    DOCS_DIR,
    TESTS_DIR,
    SRC_DIR,
    ensure_dir,
)
from src.dataset import config


def test_project_root_exists():
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()


def test_data_subdirectories_exist():
    assert DATA_DIR.exists()
    assert RAW_DIR.exists()
    assert PROCESSED_DIR.exists()
    assert SPLITS_DIR.exists()
    assert DOCS_DIR.exists()
    assert TESTS_DIR.exists()
    assert SRC_DIR.exists()


def test_ensure_dir(tmp_path):
    sub = tmp_path / "nested" / "test_dir"
    res = ensure_dir(sub)
    assert res.exists()
    assert res.is_dir()


def test_config_constants():
    assert config.RANDOM_SEED == 42
    assert config.IMAGE_SIZE == (400, 800)
    assert isinstance(config.TEMPLATE_NAMES, list)
    assert len(config.TEMPLATE_NAMES) == 3
    for name in config.TEMPLATE_NAMES:
        assert name in ["PayLite", "QuickPe", "UniPay"]
    assert "original" in config.LABELS
    assert "synthetic_fake" in config.LABELS
    assert len(config.EDIT_TYPES) == 10
    assert "DEMO" in config.DEMO_WATERMARK_TEXT
