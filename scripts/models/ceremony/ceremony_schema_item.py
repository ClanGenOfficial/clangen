from __future__ import annotations

from typing import Union

from pydantic import Field, ConfigDict
from pydantic_core import MISSING

from scripts.models.ceremony.involved_cats import InvolvedCatsCeremonyEvent
from scripts.models.text_pool_event.base_text_pool_event import BaseTextPoolEvent


class CeremonySchemaItem(BaseTextPoolEvent):
    model_config = ConfigDict(extra="forbid")
    event_id: str = Field(
        ...,
        description="Separates the events into their blocks. Generally, the ID is descriptive of the cats included in the event or the general themes of the event.",
    )
    involved_cats: InvolvedCatsCeremonyEvent | MISSING = Field(
        MISSING,
        description="Used to add constraints for the various involved cats.",
    )
