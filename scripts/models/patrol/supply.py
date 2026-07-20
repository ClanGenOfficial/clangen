from __future__ import annotations

from typing import Union, Literal

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING


class Supply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: str
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
