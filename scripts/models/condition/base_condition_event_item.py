from __future__ import annotations

from pydantic import Field, ConfigDict
from pydantic_core import MISSING

from scripts.models.condition.involved_cats import InvolvedCatsConditionEvent
from scripts.models.text_pool_event.base_text_pool_event import BaseTextPoolEvent


class BaseConditionSchemaItem(BaseTextPoolEvent):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(
        ...,
        description="Separates the events into their blocks. Generally, the ID is descriptive of the conditions represented and the type of event (i.e. `death_claw_wound0`.",
    )
    involved_cats: InvolvedCatsConditionEvent | MISSING = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
