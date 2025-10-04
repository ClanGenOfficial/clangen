from __future__ import annotations

from typing import Optional, List, Union

from pydantic import BaseModel, Field

from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.herb import Herb as CommonHerb
from scripts.models.common.new_cat import NewCat
from scripts.models.common.skill import Skill
from scripts.models.common.trait import Trait
from scripts.models.patrol.can_have_status import CanHaveStatEnum
from scripts.models.patrol.dead_cat import DeadCats
from scripts.models.patrol.herb import Herb as PatrolHerb
from scripts.models.patrol.history_text import HistoryText
from scripts.models.patrol.injury_item import InjuryItem
from scripts.models.patrol.prey import PreyEnum
from scripts.models.patrol.relationship import Relationship


class Outcome(BaseModel):
    text: str = Field(..., description="Displayed outcome text.")
    weight: int = Field(..., description="Controls how common an outcome is.")
    exp: int = Field(..., description="Base exp gain.")
    stat_skill: Optional[List[Skill]] = Field(
        None,
        description="Makes this a stat outcome which can occur if a stat cat can be found.",
    )
    stat_trait: Optional[List[Trait]] = Field(
        None,
        description="Makes this a stat outcome which can occur if a stat cat can be found.",
    )
    can_have_stat: Optional[List[CanHaveStatEnum]] = Field(
        None,
        description="Overrides default behavior or adds additional requirements for stat_cat picking.",
    )
    prey: Optional[List[PreyEnum]] = Field(
        None, description="Indicates how much prey each cat brings back."
    )
    herbs: Optional[List[Union[CommonHerb, PatrolHerb]]] = Field(
        None, description="Indicates which herbs will be given."
    )
    lost_cats: Optional[List[GatherCat]] = Field(
        None, description="Indicates which cats will become lost."
    )
    dead_cats: Optional[List[Union[GatherCat, DeadCats]]] = Field(
        None, description="Indicates which cats will die."
    )
    injury: Optional[List[InjuryItem]] = Field(
        None, description="Indicates which cats get injured and how."
    )
    history_text: Optional[HistoryText] = Field(
        None, description="Controls the history-text for scars and death."
    )
    relationships: Optional[List[Relationship]] = Field(
        None, description="Indicates effect on cat relationships."
    )
    new_cat: Optional[List[NewCat]] = Field(
        None,
        description="Adds new cat(s), either joining the clan or as outside cats. The {index} value corresponds to their index value on this list (e.g. n_c:0 refers to the first cat in this list).",
    )
    art: Optional[str] = Field(
        None,
        description="Name of outcome-specific art, without file extension (no .png). If no art is specified, the intro art will be used.",
    )
    art_clean: Optional[str] = Field(
        None,
        description="Name of non-gore outcome-specific art, without file extension (no .png). Adding a clean version of the art marks the normal version as containing gore.",
    )
    outsider_rep: Optional[int] = Field(
        None,
        description="How much outsider reputation will change. Can be positive or negative.",
    )
    other_clan_rep: Optional[int] = Field(
        None,
        description="How much reputation with other Clan will change. Can be positive or negative.",
    )
