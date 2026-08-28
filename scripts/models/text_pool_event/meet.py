from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.status import Status


class Meet(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: list[GatherCat] = Field(
        ..., description="List of cats who will meet the Clan"
    )
