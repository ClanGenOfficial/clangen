from __future__ import annotations

from enum import Enum


class SupplyAdjust(Enum):
    reduce_eighth = "reduce_eighth"
    reduce_quarter = "reduce_quarter"
    reduce_half = "reduce_half"
    reduce_full = "reduce_full"
    field_ = ""
