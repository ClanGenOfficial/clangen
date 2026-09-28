from __future__ import annotations

from typing import List

from pydantic import Field, ConfigDict
from pydantic_core import MISSING

from scripts.models.common.scar import Scar
from scripts.models.condition.base_condition_info_item import (
    BaseConditionInfoSchemaItem,
)


class PermanentConditionInfoSchemaItem(BaseConditionInfoSchemaItem):
    model_config = ConfigDict(extra="forbid")
    can_be_congenital: bool = Field(
        description="If this condition can be given at birth."
    )
    can_be_acquired: bool = Field(
        description="If this condition can be acquired later in life."
    )
    requires_scar: bool | MISSING = Field(
        MISSING,
        description="If this cat MUST have one of the scars listed in 'possible_scars' in order to have this condition.",
    )
    remove_on_death: bool | MISSING = Field(
        MISSING,
        description="If this condition should or should not be removed from the cat when they die.",
    )
    moons_until_discovery: int | MISSING = Field(
        MISSING,
        description="ONLY FOR CONGENITAL CONDITIONS. The number of moons a cat can have this condition before it is revealed/discovered.",
    )
    possible_scars: List[Scar] | MISSING = Field(
        MISSING,
        description="Scars that can be given when this permanent condition is acquired.",
    )
