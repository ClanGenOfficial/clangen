from __future__ import annotations

from typing import Dict, List, Union, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.future_event import FutureEvent
from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.location import Location
from scripts.models.common.season import Season
from scripts.models.common.tag import Tag
from scripts.models.common.temperament import Temperament
from scripts.models.patrol.condition import Condition
from scripts.models.patrol.death import Death
from scripts.models.patrol.join import Join
from scripts.models.patrol.supply import Supply
from scripts.models.text_pool_event.relationship_change_dict import RelationshipChange
from scripts.models.text_pool_event.relationship_constraint_dict import (
    RelationshipConstraint,
)


class RequiredReputation(BaseModel):
    outsider: list[Literal["welcoming", "neutral", "hostile"]] | MISSING = MISSING
    other_clan: list[Literal["ally", "neutral", "hostile"]] | MISSING = MISSING


class BaseTextPoolEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
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
    required_reputation: Union[RequiredReputation, MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the player clan has the required reputation",
    )
    relationship_constraint: Union[List[RelationshipConstraint], MISSING] = Field(
        MISSING,
        description="Used to require specific relationships between the cats",
    )
    other_clan_temperament: Union[List[Temperament], MISSING] = Field(
        MISSING,
        description="Constrains the event to only occur if the involved other Clan has one of these temperaments.",
    )
    reputation_changes: Union[
        dict[Literal["outsider", "other_clan"], int], MISSING
    ] = MISSING
    relationship_changes: Union[List[RelationshipChange], MISSING] = Field(
        MISSING,
        description="Used to change specific relationships between the cats",
    )
    supply: Union[List[Supply], MISSING] = Field(
        MISSING,
        description="Indicates changes to the supply of the Clan. Each supply change block is a new change",
    )
    death: Union[List[Death], MISSING] = Field(
        MISSING,
        description='Indicate which cats should die as a result of this event. You can specify different "types" of death as separate blocks',
    )
    condition: Union[List[Condition], MISSING] = Field(
        MISSING,
        description="Indicate which cats should receive conditions and what conditions they receive. You can add multiple condition blocks",
    )
    lost: Union[List[Dict[Literal["cats"], list[GatherCat]]], MISSING] = Field(
        MISSING,
        description="Indicate which cats should be lost from their Clan. You can add multiple lost blocks",
    )
    join: Union[List[Join], MISSING] = Field(
        MISSING,
        description="Indicate which cats will join the player Clan. You can add multiple join blocks",
    )
    future_event: Union[List[FutureEvent], MISSING] = Field(
        MISSING, description="Schedules another event to happen in the future."
    )
