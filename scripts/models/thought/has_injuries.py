from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel
from pydantic_core import MISSING

from scripts.models.thought.illness_injury_any import IllnessInjuryAny


class HasInjuries(BaseModel):
    m_c: List[IllnessInjuryAny] | MISSING = MISSING
    r_c: List[IllnessInjuryAny] | MISSING = MISSING
