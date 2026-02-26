from __future__ import annotations

from typing import List

from pydantic import Field, RootModel

from scripts.models.patrol.patrol_schema_item import PatrolSchemaItem


class PatrolSchema(RootModel):
    root: List[PatrolSchemaItem] = Field(
        ..., description="Patrols in Clan Generator.", title="Clangen Patrol Schema"
    )
