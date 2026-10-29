from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING


class MentorApprenticeDict(BaseModel):
    model_config = ConfigDict(extra="forbid")
    current: bool | MISSING = Field(
        MISSING,
        description="If True, cat must currently have mentor/apprentice. If False, cat must not have a current mentor/apprentice",
    )
    former: bool | MISSING = Field(
        MISSING,
        description="If True, cat must have a former mentor/apprentice. If False, cat must have a former mentor/apprentice",
    )
