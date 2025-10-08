from __future__ import annotations

from typing import Union, List

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.models.common.herb import Herb
from scripts.models.shortevent.event_trigger import EventTrigger
from scripts.models.shortevent.supply_adjust import SupplyAdjust
from scripts.models.shortevent.supply_type import SupplyType


class Supply(BaseModel):
    type: Union[Union[Herb, SupplyType], MISSING] = Field(
        MISSING, description="Indicates the supply being affected."
    )
    trigger: Union[List[EventTrigger], MISSING] = Field(
        MISSING,
        description="Indicates when the event can trigger. Must include all possible trigger times.",
    )
    adjust: Union[SupplyAdjust, MISSING] = Field(
        MISSING, description="Indicates how the supply should be adjusted."
    )
