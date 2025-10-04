import os
from itertools import chain
from pathlib import Path

import pytest

from scripts.models.shortevent.short_event_schema import ShortEventSchema

ROOT_DIR = Path(__file__).parent
SCHEMA_DIR = ROOT_DIR / "schemas"
RESOURCES_DIR = ROOT_DIR / "resources"


def all_shortevent_files():
    """
    Iterator for Paths for all shortevent files
    """

    INCLUSION_GLOBS = ["death/*.json", "injury/*.json", "misc/*.json", "new_cat/*.json"]

    yield from chain.from_iterable(
        RESOURCES_DIR.glob("lang/*/events/" + glob) for glob in INCLUSION_GLOBS
    )


@pytest.mark.parametrize(
    "shortevent_file",
    all_shortevent_files(),
    ids=lambda shortevent_file: f'"{str(shortevent_file.relative_to(os.getcwd()))}"',
)
def test_shortevents(shortevent_file: Path):
    ShortEventSchema.model_validate_json(shortevent_file.read_text())
