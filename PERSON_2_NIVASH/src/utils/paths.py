"""
Path resolution and directory management for Person 2 Subsystem.
Centralizes all directory paths to prevent hard-coded string concatenation or cwd dependencies.
"""

from pathlib import Path
from typing import Union


# Project Root resolves to the root of the Person 2 workspace (or repo root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Data Directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SPLITS_DIR = DATA_DIR / "splits"
METADATA_CSV = DATA_DIR / "metadata.csv"

# Documentation & Tests
DOCS_DIR = PROJECT_ROOT / "docs"
TESTS_DIR = PROJECT_ROOT / "tests"
SRC_DIR = PROJECT_ROOT / "src"


def ensure_dir(path: Union[str, Path]) -> Path:
    """
    Ensure that a target directory exists, creating parent directories if needed.
    
    Args:
        path: Directory path as str or Path.
        
    Returns:
        Path object of the verified/created directory.
    """
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


# Initialize required subdirectories automatically
ensure_dir(RAW_DIR)
ensure_dir(PROCESSED_DIR)
ensure_dir(SPLITS_DIR)
ensure_dir(DOCS_DIR)
ensure_dir(TESTS_DIR)
