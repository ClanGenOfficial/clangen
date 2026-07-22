from __future__ import annotations

from typing import Dict, List, Tuple, Union, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING
from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.location import Location
from scripts.models.common.min_max_status import MinMaxStatusDictKey
from scripts.models.common.future_event import FutureEvent
from scripts.models.common.season import Season
from scripts.models.common.tag import Tag
from scripts.models.patrol.condition import Condition
from scripts.models.patrol.death import Death
from scripts.models.patrol.involved_cats import InvolvedCatsPatrolEvent
from scripts.models.patrol.join import Join
from scripts.models.patrol.supply import Supply
from scripts.models.text_pool_event.relationship_change_dict import RelationshipChange
from scripts.models.text_pool_event.relationship_constraint_dict import (
    RelationshipConstraint,
)


class Outcome(BaseModel):
    model_config = ConfigDict(extra="forbid")
    frequency: int = Field(
        ...,
        description="Controls how common an outcome is. 4 is the most common, 1 is the least.",
        json_schema_extra={
            "default": 4
        },  # Necessary so that JSON Schema still shows a default without making the field optional
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

    outcome_art: Union[str, MISSING] = Field(
        MISSING,
        description="The name of displayed patrol art file, without any file extension (no .png).",
    )
    outcome_art_clean: Union[str, MISSING] = Field(
        MISSING,
        description='If patrol_art contains gore, this line can hold a clean version. The existence of a non-empty string in this parameter marks the patrol art in "patrol_art" as explicit.',
    )
    strings: List[str] = Field(
        ..., description="List of the text that will be displayed in-game as events."
    )
    required_cat_types: Union[
        Dict[MinMaxStatusDictKey, Tuple[int, int]], MISSING
    ] = Field(
        MISSING,
        description="Allows specification of the minimum and maximum number of specific types of cats that are allowed on the patrol.",
    )
    involved_cats: Union[InvolvedCatsPatrolEvent, MISSING] = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    required_reputation: Union[
        dict[Literal["outsider", "other_clan"], list], MISSING
    ] = MISSING
    relationship_constraint: Union[List[RelationshipConstraint], MISSING] = Field(
        MISSING,
        description="Used to require specific relationships between the cats",
    )
    exp_gained: int
    reputation_changes: Union[
        dict[Literal["outsider", "other_clan"], int], MISSING
    ] = MISSING
    relationship_changes: Union[List[RelationshipChange], MISSING] = Field(
        MISSING,
        description="Used to change specific relationships between the cats",
    )
    supply: Union[List[Supply], MISSING] = MISSING
    death: Union[List[Death], MISSING] = MISSING
    condition: Union[List[Condition], MISSING] = MISSING
    lost: Union[List[Dict[Literal["cats"], list[GatherCat]]], MISSING] = MISSING
    join: Union[List[Join], MISSING] = MISSING
    future_event: Union[List[FutureEvent], MISSING] = Field(
        MISSING, description="Schedules another event to happen in the future."
    )
