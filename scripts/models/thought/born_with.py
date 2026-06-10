from __future__ import annotations

from typing import Union

from pydantic import BaseModel
from pydantic_core import MISSING


class BornWith(BaseModel):
    m_c: Union[bool, MISSING] = MISSING
    r_c: Union[bool, MISSING] = MISSING
