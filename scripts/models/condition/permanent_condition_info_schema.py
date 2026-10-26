from __future__ import annotations

from typing import Dict

from pydantic import Field, RootModel

from scripts.models.condition.permanent_condition_info_item import (
    PermanentConditionInfoSchemaItem,
)


class PermanentConditionInfoSchema(RootModel):
    root: Dict[str, PermanentConditionInfoSchemaItem] = Field(
        ...,
        description="Permanent condition info in Clan Generator.",
        title="Clangen Permanent Condition Schema",
    )
