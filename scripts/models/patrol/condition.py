from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury
from scripts.models.common.perm_condition import PermCondition
from scripts.models.common.scar import Scar


class Condition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: list[GatherCat]
    no_results: Union[bool, MISSING] = MISSING
    non_lethal: Union[bool, MISSING] = MISSING
    condition: list[Union[Injury, Illness, PermCondition]]
    scar_pool_override: Union[list[Scar], MISSING] = MISSING
    scar_history: Union[str, MISSING] = MISSING
    death_history: Union[str, MISSING] = MISSING
