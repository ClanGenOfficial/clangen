from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat


class GainAccessory(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: list[GatherCat] = Field(
        ..., description="List of cats who will gain an accessory"
    )
    accessory: list[str] | MISSING = Field(
        MISSING, description="List possible new accessories here"
    )
