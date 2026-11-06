from __future__ import annotations

from typing import List

from pydantic import RootModel, Field

from scripts.models.relationship_group_event.relationship_group_schema_item import (
    RelationshipGroupEventSchemaItem,
)


class RelationshipGroupEvent(RootModel):
    root: List[RelationshipGroupEventSchemaItem] = Field(
        ...,
        description="Group relationship event in Clan Generator.",
        title="Clangen Group Relationship Event Schema",
    )
