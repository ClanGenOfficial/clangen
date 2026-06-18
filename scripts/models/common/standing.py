from enum import Enum


class Standing(Enum):
    LEFT = "left"
    LOST = "lost"
    EXILED = "exiled"
    NOT_LEFT = "-left"
    NOT_LOST = "-lost"
    NOT_EXILED = "-exiled"
