from typing import Union, List

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.models.common.age import Age
from scripts.models.common.backstory import Backstory
from scripts.models.common.group import Group
from scripts.models.text_pool_event.health_dict import HealthDict
from scripts.models.text_pool_event.standing_dict import StandingDict
from scripts.models.text_pool_event.stat_dict import StatDict
from scripts.models.text_pool_event.status_any import StatusAny


class CatDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Union[List[StatusAny], MISSING] = MISSING
    past_status: Union[List[StatusAny], MISSING] = MISSING
    age: Union[List[Age], MISSING] = MISSING
    group: Union[List[Group], MISSING] = MISSING
    standing: Union[StandingDict, MISSING] = MISSING
    stat: Union[StatDict, MISSING] = MISSING
    health: Union[HealthDict, MISSING] = MISSING
    backstory: Union[List[Backstory], MISSING] = MISSING
