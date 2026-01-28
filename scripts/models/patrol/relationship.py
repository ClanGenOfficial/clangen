from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from scripts.models.common.gather_cat import GatherCat
from scripts.models.patrol.value import Value


class Relationship(BaseModel):
    cats_from: List[GatherCat] = Field(
        ...,
        description='The cat\'s whose relationship values are being edited. You are changing how the "cats_from" feels.',
    )
    cats_to: List[GatherCat] = Field(
        ...,
        description='The target of the relationship. You are changing how "cats_from" feels about "cats_to".',
    )
    mutual: Optional[bool] = Field(
        None,
        description="Controls if the relation effect will be applied in both directions.",
    )
    values: List[Value] = Field(
        ..., description="Controls which relationship values are affected."
    )
    amount: int = Field(
        ...,
        description="Exact amount the relationship value will be affected. Can be positive or negative.",
    )
