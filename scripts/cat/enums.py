from __future__ import annotations

from strenum import StrEnum


class CatAge(StrEnum):
    NEWBORN = "newborn"
    KITTEN = "kitten"
    ADOLESCENT = "adolescent"
    YOUNG_ADULT = "young adult"
    ADULT = "adult"
    SENIOR_ADULT = "senior adult"
    SENIOR = "senior"

    def is_baby(self):
        return self in (CatAge.KITTEN, CatAge.NEWBORN)

    def can_have_mate(self):
        return self not in (CatAge.KITTEN, CatAge.NEWBORN, CatAge.ADOLESCENT)


class CatSocial(StrEnum):
    CLANCAT = "clancat"
    ROGUE = "rogue"
    LONER = "loner"
    KITTYPET = "kittypet"


class CatRank(StrEnum):
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

    # TODO: these might be useless tbh? bad practice?
    @property
    def all_apprentice_ranks(self) -> list:
        return [CatRank.APPRENTICE, CatRank.MEDIATOR_APPRENTICE, CatRank.MEDICINE_APPRENTICE]

    @property
    def all_clancat_ranks(self) -> list:
        return [CatRank.NEWBORN,
                CatRank.KITTEN,
                CatRank.APPRENTICE,
                CatRank.MEDICINE_APPRENTICE,
                CatRank.MEDIATOR_APPRENTICE,
                CatRank.MEDICINE_CAT,
                CatRank.MEDIATOR,
                CatRank.DEPUTY,
                CatRank.LEADER,
                CatRank.ELDER]

    @property
    def all_outsider_ranks(self) -> list:
        return [CatRank.LONER, CatRank.ROGUE, CatRank.KITTYPET]


class CatStanding(StrEnum):
    MEMBER = "member"
    LEFT = "left"
    LOST = "lost"
    EXILED = "exiled"
    KNOWN = "known"
