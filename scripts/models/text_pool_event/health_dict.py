from typing import Union, List, Literal

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.common.illness import Illness
from scripts.models.common.injury import Injury
from scripts.models.common.perm_condition import PermCondition


class HealthDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    working: Union[bool, MISSING] = MISSING
    condition: Union[
        List[Union[Injury, Illness, PermCondition, Literal["any"]]], MISSING
    ] = MISSING
    must_be_congenital: Union[bool, MISSING] = MISSING
    must_be_acquired: Union[bool, MISSING] = MISSING
