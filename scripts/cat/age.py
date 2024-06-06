from enum import IntEnum


class Age(IntEnum):
    NONE = 0
    NEWBORN = 1
    KITTEN = 2
    ADOLESCENT = 3
    YOUNGADULT = 4
    ADULT = 5
    SENIORADULT = 6
    SENIOR = 7

    def __str__(self):
        if self == Age.YOUNGADULT:
            return "young adult"
        elif self == Age.SENIORADULT:
            return "senior adult"
        else:
            return self.name.lower()
