from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.status import Status


class Join(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: list[GatherCat] = Field(..., description="List of cats who will join")
    change_name: Union[bool, MISSING] = Field(
        MISSING, description="True if the cat should take on a more Clan-like name"
    )
    new_status: Union[list[Status], MISSING] = Field(
        MISSING,
        description="A list of possible ranks for the cat to take within the Clan. If left blank, the cat will take on a rank appropriate for their age",
    )
