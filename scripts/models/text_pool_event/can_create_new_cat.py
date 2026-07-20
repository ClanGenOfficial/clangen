from typing import Union

from pydantic import BaseModel, ConfigDict
from pydantic_core import MISSING


class CanCreateNewCat(BaseModel):
    model_config = ConfigDict(extra="forbid")
    become_litter: Union[bool, MISSING] = MISSING
    assign_blood_parent: Union[list[str], MISSING] = MISSING
    assign_adoptive_parent: Union[list[str], MISSING] = MISSING
    assign_mate: Union[list[str], MISSING] = MISSING
