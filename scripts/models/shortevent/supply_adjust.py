from __future__ import annotations

from enum import Enum
from typing import Union, Annotated

from pydantic import RootModel, StringConstraints


class SupplyAdjustEnum(Enum):
    reduce_eighth = "reduce_eighth"
    reduce_quarter = "reduce_quarter"
    reduce_half = "reduce_half"
    reduce_full = "reduce_full"
    field_ = ""


class SupplyAdjust(RootModel):
    root: Union[
        SupplyAdjustEnum,
        Annotated[str, StringConstraints(pattern=r"^increase_[0-9]+$")],
    ]
