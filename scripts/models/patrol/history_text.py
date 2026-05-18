from __future__ import annotations

from typing import Union

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import MISSING


class HistoryText(BaseModel):
    model_config = ConfigDict(extra="forbid")
    death: Union[str, MISSING] = Field(
        MISSING, description="Death history. Whole sentence."
    )
    scar: Union[str, MISSING] = Field(
        MISSING, description="Scar history. Whole sentence."
    )
