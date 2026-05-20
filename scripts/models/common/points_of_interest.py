from enum import Enum
from typing import List, Union

from pydantic import BaseModel, RootModel


class PointsOfInterestTagEnum(Enum):
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


class PointsOfInterestTag(RootModel):
    root: Union[str, PointsOfInterestTagEnum]


class PointsOfInterestGroupByName(BaseModel):
    name: List[str]


class PointsOfInterestGroupByTags(BaseModel):
    tags: List[PointsOfInterestTag]


class PointsOfInterestGroup(RootModel):
    root: Union[PointsOfInterestGroupByName, PointsOfInterestGroupByTags]
