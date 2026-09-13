from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING

from scripts.models.common.gather_cat import GatherCat


class Death(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cats: list[GatherCat] = Field(
        ...,
        description="List of cats who will die. patrol_cats can be used to kill the entire patrol",
    )
    body: Union[bool, MISSING] = Field(
        MISSING,
        description="True if the body can be retrieved, False if the body has been lost",
    )
    history: str = Field(
        ...,
        description="String to add to the cat's death history. Use m_c in place of the dead cat's name and pronoun",
    )
    no_results: Union[bool, MISSING] = Field(
        MISSING,
        description="Not required. Set to True to prevent the result text for this death from appearing on the patrol screen. Defaults to False",
    )
