from __future__ import annotations

from enum import Enum
from typing import Union, Annotated

from pydantic import RootModel, StringConstraints


class PatrolTagEnum(Enum):
    romance = "romance"
    rom_two_apps = "rom_two_apps"
    disaster = "disaster"
    new_cat = "new_cat"
    halloween = "halloween"
    april_fools = "april_fools"
    new_years = "new_years"
    cruel_season = "cruel_season"
    all_mentored = "all_mentored"
    app1_mentored = "app1_mentored"
    app2_mentored = "app2_mentored"
    app3_mentored = "app3_mentored"
    app4_mentored = "app4_mentored"
    app5_mentored = "app5_mentored"
    app6_mentored = "app6_mentored"


class PatrolTag(RootModel):
    root: Union[
        PatrolTagEnum, Annotated[str, StringConstraints(pattern=r"^clan:(.+)$")]
    ]
