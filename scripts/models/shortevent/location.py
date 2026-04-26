from __future__ import annotations

from typing import Annotated, List, Literal, Union

from pydantic import RootModel, StringConstraints

from scripts.models.common.biome import Biome


class Location(RootModel):
    root: List[
        Union[
            Biome,
            Literal["any"],
            Annotated[
                str, StringConstraints(pattern=r"^[a-z]+:(camp[0-9]_)*camp[0-9]$")
            ],
        ]
    ]
