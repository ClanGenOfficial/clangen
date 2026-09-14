from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.all_trait import AllTrait
from scripts.models.common.skill import Skill


class StatDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    skill: Union[List[Skill], MISSING] = Field(
        MISSING, description="List of allowed skills"
    )
    trait: Union[List[AllTrait], MISSING] = Field(
        MISSING, description="List of allowed traits"
    )
    must_have_both: Union[bool, MISSING] = Field(
        MISSING,
        description=" if set to true, the cat's trait AND skills must BOTH qualify. Otherwise, the cat must have either/or a listed trait or a listed skill",
    )
