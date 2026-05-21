from __future__ import annotations

from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.shortevent.outsider_rep import OutsiderRep


class Outsider(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current_rep: Union[List[OutsiderRep], MISSING] = Field(
        MISSING,
        description="The reputation the Clan must have in order for this event to be possible.",
    )
    changed: Union[int, MISSING] = Field(
        MISSING,
        description="How the reputation of the Clan changes as a result of this event",
    )
