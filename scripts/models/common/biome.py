from __future__ import annotations

from enum import Enum


class Biome(Enum):
    mountainous = "mountainous"
    not_mountainous = "-mountainous"
    plains = "plains"
    not_plains = "-plains"
    forest = "forest"
    not_forest = "-forest"
    beach = "beach"
    not_beach = "-beach"
    wetlands = "wetlands"
    not_wetlands = "-wetlands"
    desert = "desert"
    not_desert = "-desert"


class BiomeNoExclusions(Enum):
    mountainous = "mountainous"
    plains = "plains"
    forest = "forest"
    beach = "beach"
    wetlands = "wetlands"
    desert = "desert"
