from __future__ import annotations

from typing import Optional, List, Union, Annotated

from pydantic import BaseModel, Field, StringConstraints
from pydantic_core import MISSING

from scripts.models.shortevent.cat import Cat


class HistoryText(BaseModel):
    cats: List[
        Union[Cat, Annotated[str, StringConstraints(pattern=r"^n_c:[0-9]+$")]]
    ] | MISSING = Field(
        MISSING, description="List of cats for whom the history will be assigned."
    )
    reg_death: str | MISSING = Field(
        MISSING,
        description="Death history text for non-leaders. Whole sentence. Must be included if the cat is dead or injured.",
    )
    lead_death: str | MISSING = Field(
        MISSING,
        description="Death history text for leaders. Sentence fragment. Must be included if the dead or injured cat could be the leader.",
    )
    scar: str | MISSING = Field(
        MISSING,
        description="Scar history. Whole sentence. Must be included if cat gets injured.",
    )
