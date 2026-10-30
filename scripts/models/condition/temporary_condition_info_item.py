from __future__ import annotations

from typing import Dict, List

from pydantic import Field, ConfigDict
from pydantic.v1 import PositiveInt
from pydantic_core import MISSING

from scripts.models.common.condition import ConditionEnum
from scripts.models.common.scar import Scar
from scripts.models.condition.base_condition_info_item import (
    BaseConditionInfoSchemaItem,
)


class TemporaryConditionInfoSchemaItem(BaseConditionInfoSchemaItem):
    model_config = ConfigDict(extra="forbid")
    duration: int = Field(
        description="How many moons the cat will have this condition."
    )
    infectiousness: float = Field(
        description="Percentage chance that the cat will infect others with this condition. Can be set to 0.0 if the condition cannot infect others."
    )
    side_effect: Dict[ConditionEnum, float] = Field(
        description="Extra conditions that can also be applied as a 'bonus' when this condition is given to the cat. Float is the percentage chance that the condition will be applied."
    )
    is_complication: bool | MISSING = Field(
        MISSING,
        description="If condition is a complication of another condition (i.e. infection is a complication) and cannot be given on it's own.",
    )
    possible_scars: List[Scar] | MISSING = Field(
        MISSING, description="List of scars this condition can give upon healing."
    )
