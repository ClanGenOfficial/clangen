from __future__ import annotations

from enum import Enum
from typing import Union, Annotated

from pydantic import RootModel, StringConstraints


class TagEnum(Enum):
    classic = "classic"
    cruel_season = "cruel_season"
    no_body = "no_body"
    skill_trait_required = "skill_trait_required"
    clan_wide = "clan_wide"
    all_lives = "all_lives"
    some_lives = "some_lives"
    lives_remain = "lives_remain"
    high_lives = "high_lives"
    mid_lives = "mid_lives"
    low_lives = "low_lives"
    clan_apps = "clan:apps"
    lost = "lost"
    kit_manipulated = "kit_manipulated"
    romance = "romance"
    adoption = "adoption"


class Tag(RootModel):
    root: Union[TagEnum, Annotated[str, StringConstraints(pattern=r"^clan:(.+)$")]]
