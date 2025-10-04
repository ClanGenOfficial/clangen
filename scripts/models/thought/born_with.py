from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class BornWith(BaseModel):
    m_c: Optional[bool] = None
    r_c: Optional[bool] = None
