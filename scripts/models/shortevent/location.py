from __future__ import annotations

from typing import Annotated, List, Literal, Union

from pydantic import AfterValidator, RootModel, StringConstraints

from scripts.models.common.biome import Biome


def validate_biome_camp(value: str) -> str:
    biomes = [e.value for e in Biome]
    biome, _ = value.split(":")
    if biome not in biomes:
        raise ValueError(f"{biome} in {value} is an invalid biome!")
    return value


class Location(RootModel):
    root: List[
        Union[
            Biome,
            Literal["any"],
            Annotated[
                str,
                StringConstraints(pattern=r"^[a-z]+:(camp[0-9]_)*camp[0-9]$"),
                AfterValidator(validate_biome_camp),
            ],
        ]
    ]
