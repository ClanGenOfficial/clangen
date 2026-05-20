from __future__ import annotations

from enum import Enum
from typing import Dict, List, Literal, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel

from scripts.models.common.biome import BiomeNoExclusions


class Tag(Enum):
    CAVE = "cave"
    COVERED = "covered"
    FALL_RISK = "fall_risk"
    HOLE = "hole"
    PREY = "prey"
    PREY_FLYING = "prey:flying"
    PREY_WATER = "prey:water"
    PREY_GROUND = "prey:ground"
    ROCKS = "rocks"
    TAINTED = "tainted"
    TREES = "trees"
    TWOLEGS = "Twolegs"
    TWOLEGS_ABANDONED = "Twolegs:abandoned"
    TWOLEGS_PRESENT = "Twolegs:present"
    UNSTABLE = "unstable"
    WATER = "water"
    WATER_STILL = "water:still"
    WATER_FLOWING = "water:flowing"
    WATER_OCEAN = "water:ocean"


class PointOfInterestItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Literal["gathering", "moonplace", "terrain"] = Field(
        ..., description="Category the Point of Interest belongs to."
    )
    biome: List[Union[BiomeNoExclusions, Literal["any"]]] = Field(
        ..., description="Biomes the Point of Interest belongs to."
    )
    # tags seem able to be kind of arbitrary, so this is just for autocomplete
    tags: List[Union[Tag, str]]


class PointsOfInterestSchema(RootModel):
    root: Dict[str, PointOfInterestItem]
