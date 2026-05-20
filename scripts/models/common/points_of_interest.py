from enum import Enum


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


class PointsOfInterestGroup(Enum):
    name = "name"
    tags = "tags"
