from __future__ import annotations

from typing import List, Union

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.models.shortevent.cat import Cat


class HistoryText(BaseModel):
    cats: Union[
        List[Cat],
        MISSING,
    ] = Field(
        MISSING, description="List of cats for whom the history will be assigned."
    )
    reg_death: Union[str, MISSING] = Field(
        MISSING,
        description="Death history text for non-leaders. Whole sentence. Must be included if the cat is dead or injured.",
    )
    lead_death: Union[str, MISSING] = Field(
        MISSING,
        description="Death history text for leaders. Sentence fragment. Must be included if the dead or injured cat could be the leader.",
    )
    scar: Union[str, MISSING] = Field(
        MISSING,
        description="Scar history. Whole sentence. Must be included if cat gets injured.",
    )
