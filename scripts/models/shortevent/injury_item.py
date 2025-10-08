from __future__ import annotations

from typing import List, Union

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.models.common.injury import Injury
from scripts.models.common.scar import Scar
from scripts.models.shortevent.cat import Cat


class InjuryItem(BaseModel):
    cats: Union[
        List[Cat],
        MISSING,
    ] = Field(MISSING, description="Which cats are injured.")
    injuries: Union[List[Injury], MISSING] = Field(
        MISSING, description="Pool of injuries to draw from."
    )
    scars: Union[List[Scar], MISSING] = Field(
        MISSING,
        description="Pool of scars to draw from. If in classic mode, a scar is chosen from this pool to be given instead of an injury. If in expanded mode, a scar is chosen from this pool to possibly be given upon healing their injury.",
    )
