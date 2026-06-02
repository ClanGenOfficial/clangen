from typing import List, Union

from pydantic import BaseModel
from pydantic_core import MISSING

from scripts.models.common.skill import Skill
from scripts.models.common.trait import Trait


class StatDict(BaseModel):
    skill: Union[List[Skill], MISSING] = MISSING
    trait: Union[List[Trait], MISSING] = MISSING
    must_have_both: Union[bool, MISSING] = MISSING
