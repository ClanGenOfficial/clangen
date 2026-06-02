from typing import List, Union

from pydantic import BaseModel
from pydantic_core import MISSING

from scripts.models.common.group import Group
from scripts.models.common.standing import Standing


class StandingDict(BaseModel):
    group: Union[List[Group]]
    currently: Union[List[Standing], MISSING] = MISSING
    past: Union[List[Standing], MISSING] = MISSING
