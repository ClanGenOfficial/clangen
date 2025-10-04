from __future__ import annotations

from typing import Optional, List, Union

from pydantic import BaseModel, Field

from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury
from scripts.models.common.perm_condition import PermCondition
from scripts.models.common.scar import Scar


class InjuryItem(BaseModel):
    cats: Optional[List[GatherCat]] = Field(None, description="Which cats are injured.")
    injuries: Optional[List[Union[Injury, Illness, PermCondition, str]]] = Field(
        None, description="Pool of injuries to draw from."
    )
    scars: Optional[List[Scar]] = Field(
        None,
        description="Pool of scars to draw from in Classic. Currently non-functional.",
    )
    no_results: Optional[bool] = Field(
        None,
        description='True if the injury "got" message does not show up in patrol summary.',
    )
