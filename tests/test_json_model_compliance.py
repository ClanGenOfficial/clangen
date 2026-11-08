from itertools import chain

from pathlib import Path

import pytest
import ujson
from pydantic_core import ErrorDetails, ValidationError

from scripts.models.ceremony.ceremony_schema import CeremonySchema
from scripts.models.condition.base_condition_schema import BaseConditionSchema
from scripts.models.condition.death_condition_schema import DeathConditionSchema
from scripts.models.condition.permanent_condition_info_schema import (
    PermanentConditionInfoSchema,
)
from scripts.models.condition.temporary_condition_info_schema import (
    TemporaryConditionInfoSchema,
)
from scripts.models.relationship_group_event.relationship_group_schema import (
    RelationshipGroupEvent,
)
from scripts.models.relationship_pair_event.relationship_pair_schema import (
    RelationshipPairEvent,
)
from scripts.models.transition.transition_schema import TransitionSchema

from scripts.models.patrol.patrol_schema import PatrolSchema
from scripts.models.shortevent.short_event_schema import ShortEventSchema
from scripts.models.thought.thought_schema import ThoughtSchema
from scripts.models.points_of_interest.points_of_interest_schema import (
    PointsOfInterestSchema,
)
from scripts.models.pelt_recipe.pelt_recipe_schema import PeltRecipe


ROOT_DIR = Path(__file__).parent.parent
RESOURCES_DIR = ROOT_DIR / "resources"

CUSTOM_MESSAGES = {
    "extra_forbidden": '"{last_loc}" either is not a valid parameter or is incorrectly placed. Check that the parameter is contained within the correct brackets and that it is a valid parameter for this format.',
    "missing_sentinel_error": "A parameter should have had an empty value, but did not.",
    "enum": 'The input "{input}" isn\'t valid. Valid options are: {expected}.',
    "model_type": 'It appears "{second_last_loc}" has an item of the incorrect type. Did you add a list where you should have added a dictionary?',
    "string_pattern_mismatch": "Checked if {input} could match with the valid tag pattern: {pattern}, but it couldn't. Are you certain this is a valid input?",
}


def convert_errors(e: ValidationError, tested_file: dict) -> list[ErrorDetails]:
    new_errors: list[ErrorDetails] = []
    for error in e.errors():
        if new_errors and error["type"] == "missing_sentinel_error":
            # skip this guy if other errors already present
            # it's usually cleared up by clearing the prior errors
            # so only worry about it if it's on its own
            continue
        location_message = (
            f"Error is in the {tested_file[error['loc'][0]]['event_id']} event."
        )
        custom_message = CUSTOM_MESSAGES.get(error["type"])
        ctx = error.get("ctx", {})
        if error.get("input"):
            ctx["input"] = error["input"]

        ctx["last_loc"] = error["loc"][-1]
        ctx["second_last_loc"] = error["loc"][-2]

        if custom_message:
            error[
                "msg"
            ] = f"{location_message} {custom_message.format(**ctx) if ctx else custom_message}"
        else:
            error[
                "msg"
            ] = f"{location_message} {error['msg'].format(**ctx) if ctx else error['msg']}"

        new_errors.append(error)
    return new_errors


def format_file_context_string(path: Path) -> str:
    return f'"{path.relative_to(Path.cwd())}"'


def all_pelt_recipe_files():
    """
    Iterator for Paths for all pelt recipe files
    """
    yield from ROOT_DIR.glob("sprites/dicts/pelt_recipes/*.json")


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


def ceremony_files():
    """
    Iterator for Paths for all ceremony files
    """
    EXCLUSIONS = [
        "ceremony_traits.json",
    ]

    yield from (
        file
        for file in RESOURCES_DIR.glob("lang/*/events/ceremonies/*.json")
        if file.name not in EXCLUSIONS
    )


def transition_files():
    """
    Iterator for Paths for all transition files
    """
    yield from RESOURCES_DIR.glob("lang/*/events/transition.json")


def base_condition_event_files():
    """
    Iterator for Paths for all base condition events (death not included) files
    """

    INCLUSION_GLOBS = [
        "gain_temporary_condition_strings/*.json",
        "healed_strings/*.json",
        "outbreak_strings/*.json",
        "reveal_condition_strings/*.json",
        "progression_strings/*/*.json",
        "risk_strings/*/*.json",
    ]

    yield from chain.from_iterable(
        RESOURCES_DIR.glob("lang/*/conditions/" + glob) for glob in INCLUSION_GLOBS
    )


def death_condition_event_files():
    """
    Iterator for Paths for all death condition events files
    """
    INCLUSION_GLOBS = [
        "death_strings/*.json",
    ]

    yield from chain.from_iterable(
        RESOURCES_DIR.glob("lang/*/conditions/" + glob) for glob in INCLUSION_GLOBS
    )


def temporary_condition_info_files():
    """
    Iterator for Paths for all temporary condition info files
    """

    yield from RESOURCES_DIR.glob("dicts/conditions/temporary_conditions/*.json")


def permanent_condition_info_files():
    """
    Iterator for Paths for all permanent condition info files
    """

    yield from RESOURCES_DIR.glob("dicts/conditions/permanent_conditions/*.json")


def validate_event_model(model, path):
    """
    Validates an event file against its model and constructs any errors utilizing our custom error message handler.
    Should only be used by event files that contain lists of event_id marked dictionaries.
    """
    with open(path, "r", encoding="utf-8") as f:
        loaded_file = ujson.load(f)

    try:
        model.model_validate_json(path.read_text())
    except ValidationError as e:
        print(f"ERROR IN {path}")
        errors = [
            f"\nError {count}: {_e['msg']}"
            for count, _e in enumerate(convert_errors(e, loaded_file))
        ]
        print("\n".join(errors))
        raise


@pytest.mark.parametrize(
    "thought_file",
    all_thought_files(),
    ids=format_file_context_string,
)
def test_thoughts(thought_file: Path):
    """Test that all thought JSONs are correct according to the Pydantic models"""
    validate_event_model(ThoughtSchema, thought_file)


@pytest.mark.parametrize(
    "patrol_file",
    all_patrol_files(),
    ids=format_file_context_string,
)
def test_patrols(patrol_file: Path):
    """Test that all patrol JSONs are correct according to the Pydantic models"""
    validate_event_model(PatrolSchema, patrol_file)


@pytest.mark.parametrize(
    "shortevent_file",
    all_shortevent_files(),
    ids=format_file_context_string,
)
def test_shortevents(shortevent_file: Path):
    """Test that all shortevent JSONs are correct according to the Pydantic models"""
    validate_event_model(ShortEventSchema, shortevent_file)


@pytest.mark.parametrize(
    "group_relationship_file",
    group_relationship_files(),
    ids=format_file_context_string,
)
def test_group_relationship_events(group_relationship_file: Path):
    """Test that all group_relationship_file JSONs are correct according to the Pydantic models"""
    validate_event_model(RelationshipGroupEvent, group_relationship_file)


@pytest.mark.parametrize(
    "pair_relationship_file",
    pair_relationship_files(),
    ids=format_file_context_string,
)
def test_pair_relationship_file_events(pair_relationship_file: Path):
    """Test that all pair_relationship_file JSONs are correct according to the Pydantic models"""
    validate_event_model(RelationshipPairEvent, pair_relationship_file)


def test_points_of_interest():
    """Test that the Points of Interest JSON is correct according to the Pydantic models"""
    poi_file = RESOURCES_DIR / "dicts/points_of_interest.json"
    PointsOfInterestSchema.model_validate_json(poi_file.read_text())


@pytest.mark.parametrize(
    "pelt_recipe_file",
    all_pelt_recipe_files(),
    ids=format_file_context_string,
)
def test_pelt_recipes(pelt_recipe_file: Path):
    """Test that all pelt recipe JSONs are correct according to the Pydantic models"""
    PeltRecipe.model_validate_json(pelt_recipe_file.read_text())


@pytest.mark.parametrize(
    "ceremony_file",
    ceremony_files(),
    ids=format_file_context_string,
)
def test_ceremony_file_events(ceremony_file: Path):
    """Test that all ceremony JSONs are correct according to the Pydantic models"""
    validate_event_model(CeremonySchema, ceremony_file)


@pytest.mark.parametrize(
    "transition_file",
    transition_files(),
    ids=format_file_context_string,
)
def test_transition_events(transition_file: Path):
    """Test that all transition_file JSONs are correct according to the Pydantic models"""
    validate_event_model(TransitionSchema, transition_file)


@pytest.mark.parametrize(
    "base_condition_file",
    base_condition_event_files(),
    ids=format_file_context_string,
)
def test_base_condition_events(base_condition_file: Path):
    """Test that all base_condition_file JSONs are correct according to the Pydantic models"""
    validate_event_model(BaseConditionSchema, base_condition_file)


@pytest.mark.parametrize(
    "death_condition_file",
    death_condition_event_files(),
    ids=format_file_context_string,
)
def test_death_condition_events(death_condition_file: Path):
    """Test that all death_condition_file JSONs are correct according to the Pydantic models"""
    validate_event_model(DeathConditionSchema, death_condition_file)


@pytest.mark.parametrize(
    "temporary_condition_file",
    temporary_condition_info_files(),
    ids=format_file_context_string,
)
def test_temporary_condition_info(temporary_condition_file: Path):
    """Test that all temporary_condition_file JSONs are correct according to the Pydantic models"""
    TemporaryConditionInfoSchema.model_validate_json(
        temporary_condition_file.read_text()
    )


@pytest.mark.parametrize(
    "permanent_condition_file",
    permanent_condition_info_files(),
    ids=format_file_context_string,
)
def test_permanent_condition_info(permanent_condition_file: Path):
    """Test that all permanent_condition_file JSONs are correct according to the Pydantic models"""
    PermanentConditionInfoSchema.model_validate_json(
        permanent_condition_file.read_text()
    )
