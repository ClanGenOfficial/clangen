from __future__ import annotations

from typing import List

from pydantic import RootModel, Field

from scripts.models.relationship_pair_event.relationship_pair_schema_item import (
    RelationshipPairEventSchemaItem,
)


class RelationshipPairEvent(RootModel):
    root: List[RelationshipPairEventSchemaItem] = Field(
        ...,
        description="Pair relationship event in Clan Generator.",
        title="Clangen Pair Relationship Event Schema",
    )
