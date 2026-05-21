from enum import Enum
from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel


class PointsOfInterestTagEnum(Enum):
    CAVE = "cave"
    COVERED = "covered"
    FALL_RISK = "fall_risk"
    HOLE = "hole"
    PREY = "prey"
    PREY_FLYING = "prey:flying"
    PREY_WATER = "prey:water"
    PREY_GROUND = "prey:ground"
    PREY_EGGS = "prey:eggs"
    PREY_FISH = "prey:fish"
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
    NESTS = "nests"


class PointsOfInterestTag(RootModel):
    root: Union[str, PointsOfInterestTagEnum]


class PointsOfInterestGroupByName(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: List[str] = Field(
        ..., description="Points of Interest with these specific IDs will be allowed."
    )


class PointsOfInterestGroupByTags(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tags: List[PointsOfInterestTag] = Field(
        ..., description="Points of Interest with these tags will be allowed."
    )


class PointsOfInterestGroup(RootModel):
    root: Union[PointsOfInterestGroupByName, PointsOfInterestGroupByTags] = Field(
        ...,
        description="Specifies Points of Interest constraints. Must use EITHER names or tags.",
    )
