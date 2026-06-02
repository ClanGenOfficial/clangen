from __future__ import annotations

from enum import Enum
from typing import Union, Annotated

from pydantic import AfterValidator, RootModel, StringConstraints
from scripts.models.common.rank import validate_clan_rank


class TagEnum(Enum):
    classic = "classic"
    high_lives = "high_lives"
    mid_lives = "mid_lives"
    low_lives = "low_lives"
    clan_apps = "clan:apps"
    romance = "romance"


class Tag(RootModel):
    root: Union[
        TagEnum,
        Annotated[
            str,
            StringConstraints(pattern=r"^clan:(.+)$"),
            AfterValidator(validate_clan_rank),
        ],
    ]
