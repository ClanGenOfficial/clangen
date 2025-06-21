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

    def is_baby(self) -> bool:
        return self in (self.NEWBORN, self.KITTEN)

    def is_any_medicine_rank(self) -> bool:
        return self in (self.MEDICINE_CAT, self.MEDICINE_APPRENTICE)

    def is_any_mediator_rank(self) -> bool:
        return self in (self.MEDIATOR, self.MEDIATOR_APPRENTICE)

    def is_any_apprentice_rank(self) -> bool:
        return self in (self.APPRENTICE,
                        self.MEDIATOR_APPRENTICE,
                        self.MEDICINE_APPRENTICE)

    def is_any_warrior_like_rank(self) -> bool:
        return self in (self.WARRIOR,
                        self.DEPUTY,
                        self.LEADER)

    def is_any_clancat_rank(self) -> bool:
        return self in self.all_clancat_ranks()

    def all_clancat_ranks(self) -> tuple:
        return (self.NEWBORN,
                self.KITTEN,
                self.APPRENTICE,
                self.MEDICINE_APPRENTICE,
                self.MEDIATOR_APPRENTICE,
                self.MEDICINE_CAT,
                self.MEDIATOR,
                self.DEPUTY,
                self.LEADER,
                self.ELDER)



class CatStanding(StrEnum):
    MEMBER = "member"
    LEFT = "left"
    LOST = "lost"
    EXILED = "exiled"
    KNOWN = "known"


class CatGroup(StrEnum):
    PLAYER_CLAN = "player_clan"

    OTHER_CLAN1 = "other_clan1"
    OTHER_CLAN2 = "other_clan2"
    OTHER_CLAN3 = "other_clan3"
    OTHER_CLAN4 = "other_clan4"
    OTHER_CLAN5 = "other_clan5"

    DARK_FOREST = "dark_forest"
    STAR_CLAN = "star_clan"
    UNKNOWN_RESIDENCE = "unknown_residence"
