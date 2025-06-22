from strenum import StrEnum


class Supply(StrEnum):
    EMPTY = "empty"
    LOW = "low"
    ADEQUATE = "adequate"
    FULL = "full"
    EXCESS = "excess"
