from enum import StrEnum, auto  # pylint: disable=no-name-in-module


class Age(StrEnum):
    """An enum representing the possible age groups of a cat"""

    NEWBORN = auto()
    KITTEN = auto()
    ADOLESCENT = auto()
    YOUNG_ADULT = 'young adult'
    ADULT = auto()
    SENIOR_ADULT = 'senior adult'
    SENIOR = auto()
