from __future__ import annotations

from typing import Optional, Union, List, Annotated

from pydantic import BaseModel, Field, StringConstraints
from pydantic_core import MISSING

from scripts.models.shortevent.supply_adjust import SupplyAdjust
from scripts.models.common.herb import Herb
from scripts.models.shortevent.event_trigger import EventTrigger
from scripts.models.shortevent.supply_type import SupplyType


class Supply(BaseModel):
    type: Union[Herb, SupplyType] | MISSING = Field(
        MISSING, description="Indicates the supply being affected."
    )
    trigger: List[EventTrigger] | MISSING = Field(
        MISSING,
        description="Indicates when the event can trigger. Must include all possible trigger times.",
    )
    adjust: Union[
        SupplyAdjust,
        Annotated[str, StringConstraints(pattern=r"^increase_[0-9]+$")],
    ] | MISSING = Field(
        MISSING, description="Indicates how the supply should be adjusted."
    )
