from __future__ import annotations

from typing import Dict, List, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel

from scripts.models.common.points_of_interest import PointsOfInterestTag
from scripts.models.common.biome import BiomeNoExclusions


class PointOfInterestItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Literal["gathering", "moonplace", "terrain"] = Field(
        ..., description="Category the Point of Interest belongs to."
    )
    biome: List[Union[BiomeNoExclusions, Literal["any"]]] = Field(
        ..., description="Biomes the Point of Interest belongs to."
    )
    tags: List[PointsOfInterestTag] = Field(
        ...,
        description="Points of Interests can use many different tags that denote circumstances around them to help specify how it can be used and what events/patrols it would fit with",
    )


class PointsOfInterestSchema(RootModel):
    root: Dict[str, PointOfInterestItem]
