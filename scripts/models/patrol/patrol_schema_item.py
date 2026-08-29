from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, Field, ConfigDict
from pydantic_core import MISSING

from scripts.models.common.location import Location
from scripts.models.common.min_max_status import MinMaxStatusDictKey
from scripts.models.common.points_of_interest import PointsOfInterestGroup
from scripts.models.common.season import Season
from scripts.models.common.tag import Tag
from scripts.models.common.temperament import Temperament
from scripts.models.patrol.involved_cats import InvolvedCatsPatrolEvent
from scripts.models.patrol.outcome import Outcome
from scripts.models.patrol.patrol_type import PatrolType
from scripts.models.text_pool_event.relationship_constraint_dict import (
    RelationshipConstraint,
)


class PatrolSchemaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(..., description="Unique string used to identify the patrol.")
    location: Union[Location, MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if a player chooses a specific biome.",
    )
    season: List[Season] = Field(
        MISSING, description="Controls the season(s) the patrol appears in."
    )
    types: List[PatrolType] = Field(..., description="Controls the type of patrol.")
    tags: List[Tag] = Field(
        MISSING,
        description="Tags are used for some filtering purposes, and some odd-and-ends. Tags never affect outcome.",
    )
    poi: Union[PointsOfInterestGroup, MISSING] = Field(
        MISSING,
        description="The relevant points of interest. Points of Interest never affect outcome.",
    )
    patrol_art: Optional[str] = Field(
        ...,
        description="The name of displayed patrol art file, without any file extension (no .png).",
    )
    patrol_art_clean: Optional[str] = Field(
        None,
        description='If patrol_art contains gore, this line can hold a clean version. The existence of a non-empty string in this parameter marks the patrol art in "patrol_art" as explicit.',
    )
    required_cat_types: Union[
        Dict[MinMaxStatusDictKey, Tuple[int, int]], MISSING
    ] = Field(
        MISSING,
        description="Allows specification of the minimum and maximum number of specific types of cats that are allowed on the patrol.",
    )
    frequency: int = Field(
        ...,
        description="Controls how common a patrol is. 4 is the most common, 1 is the least.",
        json_schema_extra={
            "default": 4
        },  # Necessary so that JSON Schema still shows a default without making the field optional
    )
    chance_of_success: int = Field(
        ...,
        description="Controls chance to succeed. Higher number is higher chance to succeed.",
    )
    involved_cats: Union[InvolvedCatsPatrolEvent, MISSING] = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    relationship_constraint: Union[List[RelationshipConstraint], MISSING] = Field(
        MISSING,
        description="Dictates what relationships cats can have towards each other.",
    )
    patrol_temperament: Union[List[Temperament], MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the patrol has one of these temperaments.",
    )
    other_clan_temperament: Union[List[Temperament], MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the involved other Clan has one of these temperaments.",
    )
    intro_text: str = Field(
        ..., description="The text that displays when the patrol first starts."
    )
    decline_text: str = Field(
        ...,
        description="The text that displays if the patrol is declined (do not proceed)",
    )
    success_outcomes: List[Outcome]
    fail_outcomes: List[Outcome]
    antag_success_outcomes: Union[List[Outcome], MISSING] = MISSING
    antag_fail_outcomes: List[Outcome] = MISSING
