from typing import Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING


class MentorApprenticeDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    has_suffix: Union[bool, MISSING] = Field(
        MISSING,
        description="If True, cat must have a suffix. If False, cat must have no suffix",
    )
