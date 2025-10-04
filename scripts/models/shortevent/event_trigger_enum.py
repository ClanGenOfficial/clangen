from __future__ import annotations

from enum import Enum


class EventTriggerEnum(Enum):
    always = "always"
    low = "low"
    adequate = "adequate"
    full = "full"
    excess = "excess"
