from __future__ import annotations

from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.season import Season
from scripts.models.relationship_group_event.involved_cats import InvolvedCats
from scripts.models.relationship_group_event.relationship_change_dict import (
    GroupEventRelationshipChange,
)
from scripts.models.relationship_group_event.relationship_constraint_dict import (
    GroupEventRelationshipConstraint,
)
from scripts.models.shortevent.location import Location
from scripts.models.thought.tag import Tag


class RelationshipGroupEventSchemaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(
        ...,
        description="Separates the events into their blocks. Generally, the ID includes the condition, personality, age, and status of the main_cat, as well as the condition, personality, age, and status of any other cat mentioned.",
    )
    location: Union[Location, MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if a player chooses a specific biome.",
    )
    season: Union[List[Season], MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur once the Clan is in a specific season.",
    )
    tags: Union[
        List[Tag],
        MISSING,
    ] = Field(MISSING, description="Used for some filtering purposes")
    strings: List[str] = Field(
        ..., description="List of the text that will be displayed in-game as events."
    )
    involved_cats: Union[InvolvedCats, MISSING] = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    relationship_constraint: Union[
        List[GroupEventRelationshipConstraint], MISSING
    ] = Field(
        MISSING,
        description="Used to require specific relationships between the cats",
    )
    relationship_changes: Union[List[GroupEventRelationshipChange], MISSING] = Field(
        MISSING,
        description="Used to change specific relationships between the cats",
    )
