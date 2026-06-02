from __future__ import annotations

from enum import Enum
from typing import Union, Annotated

from pydantic import RootModel, StringConstraints


class CatEnum(Enum):
    m_c = "m_c"
    r_c = "r_c"


class Cat(RootModel):
    root: Union[CatEnum, Annotated[str, StringConstraints(pattern=r"^n_c:[0-9]+$")]]


def validate_cat_abbr(value: str) -> str:
    abbrs = [r.value for r in CatEnum]
    _, abbr_str = value.split(":")
    if abbr_str not in abbrs:
        raise ValueError(
            f"Abbreviation {abbr_str} in {value} is not a valid abbreviation!"
        )
    return value
