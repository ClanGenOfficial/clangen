import os
from pathlib import Path

import pytest

from scripts.models.patrol.patrol_schema import PatrolSchema

ROOT_DIR = Path(__file__).parent
SCHEMA_DIR = ROOT_DIR / "schemas"
RESOURCES_DIR = ROOT_DIR / "resources"


def all_patrol_files():
    """
    Iterator for Paths for all patrol files
    """
    EXCLUSIONS = [
        "explicit_patrol_art.json",
        "prey_text_replacements.json",
    ]

    yield from (
        file
        for file in RESOURCES_DIR.glob("lang/*/patrols/**/*.json")
        if file.name not in EXCLUSIONS
    )


@pytest.mark.parametrize(
    "patrol_file",
    all_patrol_files(),
    ids=lambda patrol_file: f'"{str(patrol_file.relative_to(os.getcwd()))}"',
)
def test_patrols(patrol_file: Path):
    PatrolSchema.model_validate_json(patrol_file.read_text())
