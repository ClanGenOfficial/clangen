"""
Tests that JSON files are correct according to schemas.

 Please do not put the *unittest* in the tests/unittest GitHub action.
 It is only for local use.
HOWEVER,
 Please keep the raw python script, so it can be run by the GitHub action.
"""
import os
from itertools import chain

from pathlib import Path

import pytest

from scripts.models.patrol.patrol_schema import PatrolSchema
from scripts.models.shortevent.short_event_schema import ShortEventSchema
from scripts.models.thought.thought_schema import ThoughtSchema

ROOT_DIR = Path(__file__).parent.parent
RESOURCES_DIR = ROOT_DIR / "resources"


def all_thought_files():
    """
    Iterator for Paths for all thought files
    """
    yield from RESOURCES_DIR.glob("lang/*/thoughts/**/*.json")


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


def all_shortevent_files():
    """
    Iterator for Paths for all shortevent files
    """

    INCLUSION_GLOBS = ["death/*.json", "injury/*.json", "misc/*.json", "new_cat/*.json"]

    yield from chain.from_iterable(
        RESOURCES_DIR.glob("lang/*/events/" + glob) for glob in INCLUSION_GLOBS
    )


@pytest.mark.parametrize(
    "thought_file",
    all_thought_files(),
    ids=lambda thought_file: f'"{str(thought_file.relative_to(os.getcwd()))}"',
)
def test_thoughts(thought_file: Path):
    """Test that all thought JSONs are correct according to the Pydantic models"""
    ThoughtSchema.model_validate_json(thought_file.read_text())


@pytest.mark.parametrize(
    "patrol_file",
    all_patrol_files(),
    ids=lambda patrol_file: f'"{str(patrol_file.relative_to(os.getcwd()))}"',
)
def test_patrols(patrol_file: Path):
    """Test that all patrol JSONs are correct according to the Pydantic models"""
    PatrolSchema.model_validate_json(patrol_file.read_text())


@pytest.mark.parametrize(
    "shortevent_file",
    all_shortevent_files(),
    ids=lambda shortevent_file: f'"{str(shortevent_file.relative_to(os.getcwd()))}"',
)
def test_shortevents(shortevent_file: Path):
    """Test that all shortevent JSONs are correct according to the Pydantic models"""
    ShortEventSchema.model_validate_json(shortevent_file.read_text())
