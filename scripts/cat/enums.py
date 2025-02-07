from __future__ import annotations

from strenum import StrEnum


class CatAgeEnum(StrEnum):
    NEWBORN = "newborn"
    KITTEN = "kitten"
    ADOLESCENT = "adolescent"
    YOUNG_ADULT = "young adult"
    ADULT = "adult"
    SENIOR_ADULT = "senior adult"
    SENIOR = "senior"

    def is_baby(self):
        return self in (CatAgeEnum.KITTEN, CatAgeEnum.NEWBORN)

    def can_have_mate(self):
        return self not in (CatAgeEnum.KITTEN, CatAgeEnum.NEWBORN, CatAgeEnum.ADOLESCENT)