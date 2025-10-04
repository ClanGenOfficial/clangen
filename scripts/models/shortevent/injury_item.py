from __future__ import annotations

from typing import Optional, List, Union, Annotated

from pydantic import BaseModel, Field, StringConstraints

from scripts.models.shortevent.cats import Cats
from scripts.models.common.injury import Injury
from scripts.models.common.scar import Scar


class InjuryItem(BaseModel):
    cats: Optional[
        List[Union[Cats, Annotated[str, StringConstraints(pattern=r"^n_c:[0-9]+$")]]]
    ] = Field(None, description="Which cats are injured.")
    injuries: Optional[List[Injury]] = Field(
        None, description="Pool of injuries to draw from."
    )
    scars: Optional[List[Scar]] = Field(
        None,
        description="Pool of scars to draw from. If in classic mode, a scar is chosen from this pool to be given instead of an injury. If in expanded mode, a scar is chosen from this pool to possibly be given upon healing their injury.",
    )
