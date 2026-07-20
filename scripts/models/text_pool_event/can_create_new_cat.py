from typing import Union, List, Literal

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING

from scripts.events_module.parameter_dicts import CanCreateNewCatDict
from scripts.models.common.age import Age
from scripts.models.common.backstory import Backstory
from scripts.models.common.group import Group
from scripts.models.text_pool_event.health_dict import HealthDict
from scripts.models.text_pool_event.standing_dict import StandingDict
from scripts.models.text_pool_event.stat_dict import StatDict
from scripts.models.text_pool_event.status_any import StatusAny


class CanCreateNewCat(BaseModel):
    model_config = ConfigDict(extra="forbid")
    become_litter: Union[bool, MISSING] = MISSING
    assign_blood_parent: Union[list[str], MISSING] = MISSING
    assign_adoptive_parent: Union[list[str], MISSING] = MISSING
    assign_mate: Union[list[str], MISSING] = MISSING
