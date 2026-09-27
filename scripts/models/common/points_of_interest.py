from enum import Enum
from typing import List, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel
from pydantic_core import MISSING


class PointsOfInterestTagEnum(Enum):
    CAVE = "cave"
    COVERED = "covered"
    DANGER = "danger"
    DANGER_FALL_RISK = "danger:fall_risk"
    DANGER_UNSTABLE = "danger:unstable"
    DANGER_TAINTED = "danger:tainted"
    HOLE = "hole"
    PREY = "prey"
    PREY_FLYING = "prey:flying"
    PREY_BIRD = "prey:bird"
    PREY_WATER = "prey:water"
    PREY_GROUND = "prey:ground"
    PREY_FISH = "prey:fish"
    ROCKS = "rocks"
    TREES = "trees"
    TWOLEGS = "Twolegs"
    TWOLEGS_ABANDONED = "Twolegs:abandoned"
    TWOLEGS_PRESENT = "Twolegs:present"
    WATER = "water"
    WATER_STILL = "water:still"
    WATER_FLOWING = "water:flowing"
    WATER_OCEAN = "water:ocean"
    NESTS = "nests"


class PointsOfInterestCategoryEnum(Enum):
    GATHERING = "gathering"
    MOONPLACE = "moonplace"
    TERRAIN = "terrain"


class PointsOfInterestTag(RootModel):
    root: Union[str, PointsOfInterestTagEnum]


class PointsOfInterestGroup(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Union[MISSING, List[str]] = Field(
        MISSING,
        description="Points of Interest with these specific IDs will be allowed.",
    )
    tags: Union[MISSING, List[PointsOfInterestTag]] = Field(
        MISSING, description="Points of Interest with these tags will be allowed."
    )
    category: Union[PointsOfInterestCategoryEnum, MISSING] = Field(
        MISSING, description="The category this POI belongs to."
    )
