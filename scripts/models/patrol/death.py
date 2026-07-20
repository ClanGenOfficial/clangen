from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat


class Death(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: list[GatherCat]
    body: Union[bool, MISSING] = MISSING
    history: str
