from __future__ import annotations

from typing import Optional, List, Union, Annotated

from pydantic import BaseModel, Field, StringConstraints

from scripts.models.shortevent.cats import Cats


class HistoryText(BaseModel):
    cats: Optional[
        List[Union[Cats, Annotated[str, StringConstraints(pattern=r"^n_c:[0-9]+$")]]]
    ] = Field(None, description="List of cats for whom the history will be assigned.")
    reg_death: Optional[str] = Field(
        None,
        description="Death history text for non-leaders. Whole sentence. Must be included if the cat is dead or injured.",
    )
    lead_death: Optional[str] = Field(
        None,
        description="Death history text for leaders. Sentence fragment. Must be included if the dead or injured cat could be the leader.",
    )
    scar: Optional[str] = Field(
        None,
        description="Scar history. Whole sentence. Must be included if cat gets injured.",
    )
