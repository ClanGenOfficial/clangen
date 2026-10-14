from __future__ import annotations

from typing import Dict

from pydantic import Field, RootModel

from scripts.models.common.condition import ConditionEnum
from scripts.models.condition.temporary_condition_info_item import (
    TemporaryConditionInfoSchemaItem,
)


class TemporaryConditionInfoSchema(RootModel):
    root: Dict[ConditionEnum, TemporaryConditionInfoSchemaItem] = Field(
        ...,
        description="Temporary condition info in Clan Generator.",
        title="Clangen Temporary Condition Schema",
    )
