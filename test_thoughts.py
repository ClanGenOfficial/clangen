import os
from pathlib import Path

import pytest

from scripts.models.thought.thought_schema import ThoughtSchema

ROOT_DIR = Path(__file__).parent
SCHEMA_DIR = ROOT_DIR / "schemas"
RESOURCES_DIR = ROOT_DIR / "resources"


def all_thought_files():
    """
    Iterator for Paths for all thought files
    """
    yield from RESOURCES_DIR.glob("lang/*/thoughts/**/*.json")


@pytest.mark.parametrize(
    "thought_file",
    all_thought_files(),
    ids=lambda thought_file: f'"{str(thought_file.relative_to(os.getcwd()))}"',
)
def test_thoughts(thought_file: Path):
    ThoughtSchema.model_validate_json(thought_file.read_text())
