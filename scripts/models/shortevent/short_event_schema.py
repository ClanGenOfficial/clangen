from __future__ import annotations

from typing import List

from pydantic import Field, RootModel

from scripts.models.shortevent.short_event_schema_item import ShortEventSchemaItem


class ShortEventSchema(RootModel):
    root: List[ShortEventSchemaItem] = Field(
        ...,
        description="Short moonskip events in Clan Generator.",
        title="Clangen Short Event Schema",
    )
