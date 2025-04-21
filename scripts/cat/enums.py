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


class CatSocialEnum(StrEnum):
    CLANCAT = "clancat"
    ROGUE = "rogue"
    LONER = "loner"
    KITTYPET = "kittypet"


class CatRankEnum(StrEnum):
    # clan ranks
    NEWBORN = "newborn"
    KITTEN = "kitten"
    APPRENTICE = "apprentice"
    MEDICINE_APPRENTICE = "medicine cat apprentice"
    MEDIATOR_APPRENTICE = "mediator apprentice"
    WARRIOR = "warrior"
    MEDICINE_CAT = "medicine cat"
    MEDIATOR = "mediator"
    DEPUTY = "deputy"
    LEADER = "leader"
    ELDER = "elder"

    # outsider ranks
    LONER = "loner"
    ROGUE = "rogue"
    KITTYPET = "kittypet"

    # TODO: look at Flags for these instead??
    @property
    def all_apprentice_ranks(self) -> list:
        return [CatRankEnum.APPRENTICE, CatRankEnum.MEDIATOR_APPRENTICE, CatRankEnum.MEDICINE_APPRENTICE]

    @property
    def all_clancat_ranks(self) -> list:
        return [CatRankEnum.NEWBORN,
                CatRankEnum.KITTEN,
                CatRankEnum.APPRENTICE,
                CatRankEnum.MEDICINE_APPRENTICE,
                CatRankEnum.MEDIATOR_APPRENTICE,
                CatRankEnum.MEDICINE_CAT,
                CatRankEnum.MEDIATOR,
                CatRankEnum.DEPUTY,
                CatRankEnum.LEADER,
                CatRankEnum.ELDER]

    @property
    def all_outsider_ranks(self) -> list:
        return [CatRankEnum.LONER, CatRankEnum.ROGUE, CatRankEnum.KITTYPET]


class CatStandingEnum(StrEnum):
    MEMBER = "member"
    LEFT = "left"
    LOST = "lost"
    EXILED = "exiled"
    KNOWN = "known"
