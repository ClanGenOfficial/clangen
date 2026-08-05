from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury
from scripts.models.common.perm_condition import PermCondition
from scripts.models.common.scar import Scar


class Condition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: list[GatherCat] = Field(
        ...,
        description="List of cats who will receive these conditions. patrol_cats can be used to give the condition to the entire patrol",
    )
    no_results: Union[bool, MISSING] = Field(
        MISSING,
        description="Set to True if there should be no result text about this condition application",
    )
    non_lethal: Union[bool, MISSING] = Field(
        MISSING,
        description="Set to True to prevent this condition from killing the cat. It's not necessary if the condition is already non-lethal (eg. scrapes)",
    )
    condition: list[Union[Injury, Illness, PermCondition]] = Field(
        ...,
        description="List of possible conditions. One condition will be chosen from this list. You can also utilize Injury Pools",
    )
    scar_pool_override: Union[list[Scar], MISSING] = Field(
        MISSING,
        description="Override the default scars given for the assigned condition. Instead, a scar will be chosen from this list",
    )
    scar_history: Union[str, MISSING] = Field(
        MISSING,
        description="String to be added to the cat's history if the condition creates a scar. Use m_c in place of the dead cat's name and pronoun",
    )
    death_history: Union[str, MISSING] = Field(
        MISSING,
        description="String to be added to the cat's history if the condition kills them. Use m_c in place of the dead cat's name and pronoun",
    )
