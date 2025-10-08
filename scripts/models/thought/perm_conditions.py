from __future__ import annotations

from typing import List, Union

from pydantic import BaseModel, Field
from pydantic_core import MISSING

from scripts.models.thought.born_with import BornWith
from scripts.models.thought.perm_condition_any import PermConditionAny


class PermConditions(BaseModel):
    m_c: Union[List[PermConditionAny], MISSING] = MISSING
    r_c: Union[List[PermConditionAny], MISSING] = MISSING
    born_with: Union[BornWith, MISSING] = Field(
        MISSING,
        description="Used to determine whether or not the given cat has this condition from birth. Only use if the cat must have it from birth, or must not have it from birth (omit value if either is suitable).",
    )
