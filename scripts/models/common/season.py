from __future__ import annotations

from enum import Enum


class Season(Enum):
    greenleaf = "greenleaf"
    not_greenleaf = "-greenleaf"
    leaf_fall = "leaf-fall"
    not_leaf_fall = "-leaf-fall"
    leaf_bare = "leaf-bare"
    not_leaf_bare = "-leaf-bare"
    newleaf = "newleaf"
    not_newleaf = "-newleaf"
    any = "any"
