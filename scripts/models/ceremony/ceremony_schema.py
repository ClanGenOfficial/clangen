from __future__ import annotations

from typing import List

from pydantic import Field, RootModel

from scripts.models.patrol.patrol_schema_item import PatrolSchemaItem


class CeremonySchema(RootModel):
    root: List[PatrolSchemaItem] = Field(
        ...,
        description="Ceremonies in Clan Generator.",
        title="Clangen Ceremony Schema",
    )
