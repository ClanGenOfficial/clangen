from __future__ import annotations

from typing import Union, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.herb import Herb


class Supply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Union[Literal["random_herbs", "freshkill"], Herb] = Field(
        ..., description="The type of supply changing"
    )
    trigger: Union[
        list[Literal["always", "low", "adequate", "full", "excess"]], MISSING
    ] = Field(
        MISSING,
        description="If the Clan's current level of the specified supply type should be at a certain threshold for this outcome to occur, specify it here. You do NOT have to specify a trigger",
    )
    adjust: Literal[
        "increase_tiny",
        "increase_small",
        "increase_medium",
        "increase_large",
        "increase_huge",
    ] = Field(
        ...,
        description='Keep in mind that this increase is "per" cat on the patrol. A 3 cat patrol being given an increase_medium will take home 3 times as much as a similar 1 cat patrol',
    )
