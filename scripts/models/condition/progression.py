from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING


class ProgressionDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chance: float = Field(description="Percentage chance to progress to this condition")
    when: Literal["CONTINUING", "FATAL", "HEALED", "REVEALED"] = Field(
        description="The state the condition must be in to allow this progression to occur."
    )
    allow_scar: bool | MISSING = Field(
        MISSING,
        description="If progressing to this condition should be allowed the chance to scar.",
    )
