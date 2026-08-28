from __future__ import annotations

from enum import Enum
from typing import Union, Annotated

from pydantic import AfterValidator, RootModel, StringConstraints
from scripts.models.common.rank import validate_clan_ranks_with_min


class TagEnum(Enum):
    classic = "classic"
    high_lives = "high_lives"
    mid_lives = "mid_lives"
    low_lives = "low_lives"
    some_lives = "some_lives"
    all_lives = "all_lives"
    clan_apps = "clan:apps"
    clan_warrior_like = "clan:warrior-like"
    romance = "romance"
    halloween = "halloween"
    april_fools = "april_fools"
    new_years = "new_years"
    disaster = "disaster"


class Tag(RootModel):
    root: Union[
        TagEnum,
        Annotated[
            str,
            StringConstraints(pattern=r"^-?clan:(.+)$"),
            AfterValidator(validate_clan_ranks_with_min),
        ],
    ]
