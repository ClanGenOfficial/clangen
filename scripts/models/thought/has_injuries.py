from __future__ import annotations

from typing import List, Union

from pydantic import BaseModel
from pydantic_core import MISSING

from scripts.models.thought.illness_injury_any import IllnessInjuryAny


class HasInjuries(BaseModel):
    m_c: Union[List[IllnessInjuryAny], MISSING] = MISSING
    r_c: Union[List[IllnessInjuryAny], MISSING] = MISSING
