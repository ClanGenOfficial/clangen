from __future__ import annotations

from typing import Union, Literal

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.common.herb import Herb


class Supply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Union[Literal["random_herbs", "freshkill"], Herb]
    trigger: Union[
        list[Literal["always", "low", "adequate", "full", "excess"]], MISSING
    ] = MISSING
    adjust: list[
        Literal[
            "increase_tiny",
            "increase_small",
            "increase_medium",
            "increase_large",
            "increase_huge",
        ]
    ]
