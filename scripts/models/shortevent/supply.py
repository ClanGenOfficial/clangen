from __future__ import annotations

from typing import Optional, Union, List, Annotated

from pydantic import BaseModel, Field, StringConstraints

from scripts.models.shortevent.supply_adjust import SupplyAdjust
from scripts.models.common.herb import Herb
from scripts.models.shortevent.event_trigger_enum import EventTriggerEnum
from scripts.models.shortevent.supply_type import SupplyType


class Supply(BaseModel):
    type: Optional[Union[Herb, SupplyType]] = Field(
        None, description="Indicates the supply being affected."
    )
    trigger: Optional[List[EventTriggerEnum]] = Field(
        None,
        description="Indicates when the event can trigger. Must include all possible trigger times.",
    )
    adjust: Optional[
        Union[
            SupplyAdjust,
            Annotated[str, StringConstraints(pattern=r"^increase_[0-9]+$")],
        ]
    ] = Field(None, description="Indicates how the supply should be adjusted.")
