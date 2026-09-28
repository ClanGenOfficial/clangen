from __future__ import annotations

from typing import List

from pydantic import Field, RootModel

from scripts.models.ceremony.ceremony_schema_item import CeremonySchemaItem
from scripts.models.condition.base_condition_event_item import BaseConditionSchemaItem
from scripts.models.patrol.patrol_schema_item import PatrolSchemaItem


class BaseConditionSchema(RootModel):
    root: List[BaseConditionSchemaItem] = Field(
        ...,
        description="Condition events in Clan Generator.",
        title="Clangen Condition Schema",
    )
