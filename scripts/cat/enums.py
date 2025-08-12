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
        return self in (
            self.APPRENTICE,
            self.MEDIATOR_APPRENTICE,
            self.MEDICINE_APPRENTICE,
        )

    def is_any_adult_warrior_like_rank(self) -> bool:
        return self in (self.WARRIOR, self.DEPUTY, self.LEADER)

    def is_allowed_to_patrol(self) -> bool:
        # newborn is not included in this because the constants.CONFIG["fun"] needs extra checks
        if self.is_any_clancat_rank() and self not in (
            self.ELDER,
            self.KITTEN,
            self.NEWBORN,
            self.MEDIATOR,
            self.MEDIATOR_APPRENTICE,
        ):
            return True
        return False

    def is_active_clan_rank(self):
        if self.is_any_clancat_rank() and self not in (
            self.ELDER,
            self.KITTEN,
            self.NEWBORN,
        ):
            return True
        return False

    def is_any_clancat_rank(self) -> bool:
        return self not in (self.ROGUE, self.LONER, self.KITTYPET)

    @staticmethod
    def get_num_of_clan_ranks() -> int:
        return len([enum for enum in CatRank if enum.is_any_clancat_rank()])


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
    STARCLAN = "starclan"
    UNKNOWN_RESIDENCE = "unknown_residence"

    def is_afterlife(self) -> bool:
        return self in (self.DARK_FOREST, self.STARCLAN, self.UNKNOWN_RESIDENCE)

    def is_any_clan_group(self) -> bool:
        return self in (
            self.PLAYER_CLAN,
            self.OTHER_CLAN1,
            self.OTHER_CLAN2,
            self.OTHER_CLAN3,
            self.OTHER_CLAN4,
            self.OTHER_CLAN5,
        )

    def is_other_clan_group(self) -> bool:
        return self.is_any_clan_group() and self != self.PLAYER_CLAN
