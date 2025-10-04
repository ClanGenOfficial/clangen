from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class HistoryText(BaseModel):
    reg_death: Optional[str] = Field(
        None, description="Death history text for non-leaders. Whole sentence."
    )
    lead_death: Optional[str] = Field(
        None, description="Death history text for leaders. Sentence fragment."
    )
    scar: Optional[str] = Field(None, description="Scar history. Whole sentence.")
