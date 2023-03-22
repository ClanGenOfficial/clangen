from enum import StrEnum, auto


class Age(StrEnum):
    """An enum representing the possible age groups of a cat"""

    NEWBORN = auto()
    KITTEN = auto()
    ADOLESCENT = auto()
    YOUNG_ADULT = 'young adult'
    ADULT = auto()
    SENIOR_ADULT = 'senior adult'
    SENIOR = auto()
