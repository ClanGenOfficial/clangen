from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field
from pydantic_core import MISSING


class HistoryText(BaseModel):
    reg_death: str | MISSING = Field(
        MISSING, description="Death history text for non-leaders. Whole sentence."
    )
    lead_death: str | MISSING = Field(
        MISSING, description="Death history text for leaders. Sentence fragment."
    )
    scar: str | MISSING = Field(MISSING, description="Scar history. Whole sentence.")
