from __future__ import annotations

from enum import Enum
from typing import Union, Annotated

from pydantic import RootModel, StringConstraints


class CatEnum(Enum):
    m_c = "m_c"
    r_c = "r_c"


class Cat(RootModel):
    root: Union[CatEnum, Annotated[str, StringConstraints(pattern=r"^n_c:[0-9]+$")]]
