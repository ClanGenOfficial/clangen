from enum import Enum, auto


class PatrolChoice(Enum):
    DECLINE = auto()
    ANTAGONIZE = auto()
    PROCEED = auto()


class PatrolOutcome(Enum):
    SUCCESS = auto()
    FAILURE = auto()
