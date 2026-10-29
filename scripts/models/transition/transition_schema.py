from __future__ import annotations

from typing import List

from pydantic import Field, RootModel

from scripts.models.patrol.patrol_schema_item import PatrolSchemaItem
from scripts.models.transition.transition_schema_item import TransitionSchemaItem


class TransitionSchema(RootModel):
    root: List[TransitionSchemaItem] = Field(
        ...,
        description="Transition in Clan Generator.",
        title="Clangen Transition Schema",
    )
