"""Tests for the initial OmniPulse AI repository layout."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

IMPORTANT_DIRECTORIES = (
    "data/raw",
    "data/processed",
    "data/sample",
    "src/ingestion",
    "src/processing",
    "src/analytics",
    "src/ml",
    "src/genai",
    "src/utils",
    "notebooks",
    "dashboards",
    "api",
    "tests",
    "docs",
    "docker",
    "architecture",
)


def test_important_directories_exist() -> None:
    """Every directory required for Phase 1 should be present."""
    missing_directories = [
        directory
        for directory in IMPORTANT_DIRECTORIES
        if not (PROJECT_ROOT / directory).is_dir()
    ]

    assert not missing_directories, (
        "Missing required project directories: " + ", ".join(missing_directories)
    )
