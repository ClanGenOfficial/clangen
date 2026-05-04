from __future__ import annotations

from typing import List, Union, Literal

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat
from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury
from scripts.models.common.perm_condition import PermCondition
from scripts.models.common.scar import Scar


class InjuryItem(BaseModel):
    cats: Union[List[GatherCat], MISSING] = Field(
        MISSING, description="Which cats are injured."
    )
    injuries: Union[
        List[Union[Injury, Illness, PermCondition, Literal["non_lethal"]]], MISSING
    ] = Field(MISSING, description="Pool of injuries to draw from.")
    scars: Union[List[Scar], MISSING] = Field(
        MISSING,
        description="Pool of scars to draw from in Classic. Currently non-functional.",
    )
    no_results: Union[bool, MISSING] = Field(
        MISSING,
        description='True if the injury "got" message does not show up in patrol summary.',
    )
