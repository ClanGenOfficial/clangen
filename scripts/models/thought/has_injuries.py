from __future__ import annotations

from typing import Optional, List

from pydantic import BaseModel

from scripts.models.thought.illness_injury_any import IllnessInjuryAny


class HasInjuries(BaseModel):
    m_c: Optional[List[IllnessInjuryAny]] = None
    r_c: Optional[List[IllnessInjuryAny]] = None
