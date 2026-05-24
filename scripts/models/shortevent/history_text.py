from __future__ import annotations

from typing import List, Union, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.shortevent.cat import Cat


class HistoryText(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: List[Union[Cat, Literal["multi_cat"]]] = Field(
        MISSING, description="List of cats for whom the history will be assigned."
    )
    death: Union[str, MISSING] = Field(
        MISSING,
        description="Death history text. Whole sentence. Must be included if the cat is dead or injured. If the cat is being injured, write this as though they have died from the injuries.",
    )
    scar: Union[str, MISSING] = Field(
        MISSING,
        description="Scar history. Whole sentence. Must be included if cat gets injured.",
    )
