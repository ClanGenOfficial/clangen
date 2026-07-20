from __future__ import annotations

from typing import Annotated, Dict, List, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING
from scripts.models.common.gather_cat import GatherCat, GatherCatEnum
from scripts.models.common.herb import Herb
from scripts.models.common.location import Location
from scripts.models.common.min_max_status import MinMaxStatusDictKey
from scripts.models.common.new_cat import NewCat
from scripts.models.common.future_event import FutureEvent
from scripts.models.common.relationship_status import RelationshipStatus
from scripts.models.common.season import Season
from scripts.models.common.skill import Skill
from scripts.models.common.tag import Tag
from scripts.models.common.trait import Trait
from scripts.models.patrol.can_have_status import CanHaveStat
from scripts.models.patrol.history_text import HistoryText
from scripts.models.patrol.injury_item import InjuryItem
from scripts.models.patrol.leader_lives_lost import LeaderLivesLost
from scripts.models.patrol.patrol_herb import PatrolHerb
from scripts.models.patrol.prey import Prey
from scripts.models.common.relationship import Relationship
from scripts.models.text_pool_event.cat_dict import CatDict


class Outcome(BaseModel):
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
    involved_cats: Union[dict[GatherCatEnum, CatDict], MISSING] = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
    relationship_constraint: Union[
        List[PairEventRelationshipConstraint], MISSING
    ] = Field(
        MISSING,
        description="Used to require specific relationships between the cats",
    )
    relationship_changes: Union[List[PairEventRelationshipChange], MISSING] = Field(
        MISSING,
        description="Used to change specific relationships between the cats",
    )
