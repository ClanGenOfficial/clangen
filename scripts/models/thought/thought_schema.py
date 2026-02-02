from __future__ import annotations

from typing import List

from pydantic import RootModel, Field

from scripts.models.thought.thought_schema_item import ThoughtSchemaItem


class ThoughtSchema(RootModel):
    root: List[ThoughtSchemaItem] = Field(
        ..., description="Thoughts in Clan Generator.", title="Clangen Thought Schema"
    )
