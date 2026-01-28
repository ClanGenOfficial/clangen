from __future__ import annotations

from enum import Enum


class SupplyType(Enum):
    freshkill = "freshkill"
    all_herb = "all_herb"
    any_herb = "any_herb"
