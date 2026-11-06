from __future__ import annotations

from typing import List

from pydantic import Field, ConfigDict

from scripts.models.condition.base_condition_event_item import BaseConditionSchemaItem
from scripts.models.text_pool_event.death import Death


class DeathConditionSchemaItem(BaseConditionSchemaItem):
    model_config = ConfigDict(extra="forbid")
    death: List[Death] = Field(
        description="Must at least include the death information for m_c.",
    )
