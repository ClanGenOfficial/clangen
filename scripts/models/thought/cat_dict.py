from typing import Union, List

from pydantic import BaseModel
from pydantic_core import MISSING

from scripts.models.common.age import Age
from scripts.models.common.backstory import Backstory
from scripts.models.common.group import Group
from scripts.models.thought.health_dict import HealthDict
from scripts.models.thought.standing_dict import StandingDict
from scripts.models.thought.stat_dict import StatDict
from scripts.models.thought.status_any import StatusAny


class CatDict(BaseModel):
    status: Union[List[StatusAny], MISSING] = MISSING
    past_status: Union[List[StatusAny], MISSING] = MISSING
    age: Union[List[Age], MISSING] = MISSING
    group: Union[List[Group], MISSING] = MISSING
    standing: Union[StandingDict, MISSING] = MISSING
    stat: Union[StatDict, MISSING] = MISSING
    health: Union[HealthDict, MISSING] = MISSING
    backstory: Union[Backstory, MISSING] = MISSING
