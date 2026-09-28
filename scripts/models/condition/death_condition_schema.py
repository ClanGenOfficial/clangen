from __future__ import annotations

from typing import List

from pydantic import Field, RootModel

from scripts.models.ceremony.ceremony_schema_item import CeremonySchemaItem
from scripts.models.condition.base_condition_event_item import BaseConditionSchemaItem
from scripts.models.condition.death_condition_event_item import DeathConditionSchemaItem
from scripts.models.patrol.patrol_schema_item import PatrolSchemaItem


class DeathConditionSchema(RootModel):
    root: List[DeathConditionSchemaItem] = Field(
        ...,
        description="Condition death events in Clan Generator.",
        title="Clangen Condition Death Schema",
    )
