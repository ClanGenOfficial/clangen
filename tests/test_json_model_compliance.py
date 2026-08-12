import os

from itertools import chain

from pathlib import Path

import pytest

from scripts.models.relationship_group_event.relationship_group_schema import (
    RelationshipGroupEvent,
)
from scripts.models.relationship_pair_event.relationship_pair_schema import (
    RelationshipPairEvent,
)

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.models.patrol.patrol_schema import PatrolSchema
from scripts.models.shortevent.short_event_schema import ShortEventSchema
from scripts.models.thought.thought_schema import ThoughtSchema
from scripts.models.points_of_interest.points_of_interest_schema import (
    PointsOfInterestSchema,
)


ROOT_DIR = Path(__file__).parent.parent
RESOURCES_DIR = ROOT_DIR / "resources"


def format_file_context_string(path: Path) -> str:
    return f'"{path.relative_to(Path.cwd())}"'


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


def pair_relationship_files():
    """
    Iterator for Paths for all relationship files
    """

    INCLUSION_GLOBS = [
        "joining_interactions/*/*/*.json",
        "normal_interactions/*/*/*.json",
    ]

    yield from chain.from_iterable(
        RESOURCES_DIR.glob("lang/*/events/relationship_events/" + glob)
        for glob in INCLUSION_GLOBS
    )


def group_relationship_files():
    """
    Iterator for Paths for all relationship files
    """
    yield from RESOURCES_DIR.glob(
        "lang/*/events/relationship_events/group_interactions/*/*.json"
    )


@pytest.mark.parametrize(
    "thought_file",
    all_thought_files(),
    ids=format_file_context_string,
)
def test_thoughts(thought_file: Path):
    """Test that all thought JSONs are correct according to the Pydantic models"""
    ThoughtSchema.model_validate_json(thought_file.read_text())


@pytest.mark.parametrize(
    "patrol_file",
    all_patrol_files(),
    ids=format_file_context_string,
)
def test_patrols(patrol_file: Path):
    """Test that all patrol JSONs are correct according to the Pydantic models"""
    PatrolSchema.model_validate_json(patrol_file.read_text())


@pytest.mark.parametrize(
    "shortevent_file",
    all_shortevent_files(),
    ids=format_file_context_string,
)
def test_shortevents(shortevent_file: Path):
    """Test that all shortevent JSONs are correct according to the Pydantic models"""
    ShortEventSchema.model_validate_json(shortevent_file.read_text())


@pytest.mark.parametrize(
    "group_relationship_file",
    group_relationship_files(),
    ids=format_file_context_string,
)
def test_group_relationship_events(group_relationship_file: Path):
    """Test that all group_relationship_file JSONs are correct according to the Pydantic models"""
    RelationshipGroupEvent.model_validate_json(group_relationship_file.read_text())


@pytest.mark.parametrize(
    "pair_relationship_file",
    pair_relationship_files(),
    ids=format_file_context_string,
)
def test_pair_relationship_file_events(pair_relationship_file: Path):
    """Test that all pair_relationship_file JSONs are correct according to the Pydantic models"""
    RelationshipPairEvent.model_validate_json(pair_relationship_file.read_text())


def test_points_of_interest():
    """Test that the Points of Interest JSON is correct according to the Pydantic models"""
    poi_file = RESOURCES_DIR / "dicts/points_of_interest.json"
    PointsOfInterestSchema.model_validate_json(poi_file.read_text())
