from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.status import Status


class Join(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: list[GatherCat]
    change_name: Union[bool, MISSING] = MISSING
    new_status: Union[list[Status], MISSING] = MISSING
