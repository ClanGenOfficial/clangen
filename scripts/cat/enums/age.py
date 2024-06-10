from enum import Enum
from random import randint

from strenum import StrEnum

from scripts.game_structure.game_essentials import game


class Age(StrEnum):
    """Cat age group"""
    NONE = "ERROR"
    NEWBORN = "newborn"
    KITTEN = "kitten"
    ADOLESCENT = "adolescent"
    YOUNGADULT = "young adult"
    ADULT = "adult"
    SENIORADULT = "senior adult"
    SENIOR = "senior"

    def __str__(self):
        return self.value

    def is_kit(self):
        """True if cat is newborn or kitten"""
        return self in [Age.NEWBORN, Age.KITTEN]

    def is_underage(self):
        """True if cat is newborn, kitten or adolescent"""
        return self in [Age.NEWBORN, Age.KITTEN, Age.ADOLESCENT]

    def is_adult_any(self):
        """True is cat is young adult, adult or senior adult"""
        return self in [Age.YOUNGADULT, Age.ADULT, Age.SENIORADULT]

    def is_adult_any_or_senior(self):
        """True if cat is young adult, adult, senior adult or senior"""
        return self in [Age.YOUNGADULT, Age.ADULT, Age.SENIORADULT, Age.SENIOR]

    def is_newborn(self):
        return self == Age.NEWBORN

    def is_kitten(self):
        return self == Age.KITTEN

    def is_adolescent(self):
        return self == Age.ADOLESCENT

    def is_young_adult(self):
        return self == Age.YOUNGADULT

    def is_adult(self):
        return self == Age.ADULT

    def is_senior_adult(self):
        return self == Age.SENIORADULT

    def is_senior(self):
        return self == Age.SENIOR

    @staticmethod
    def get_age_from_moons(moons):
        """
        Gets the correct life stage for associated moons

        :param int moons: Age in moons
        :return: Matching age group (Age)
        """
        if moons > 300:
            # Out of range, always senior
            return Age.SENIOR
        elif moons == 0:
            return Age.NEWBORN
        else:
            # In range
            for key_age in AgeMoonsRange:
                if moons in range(
                        key_age[0], key_age[1] + 1
                ):
                    return Age[key_age.name]

    @staticmethod
    def get_random_moons_for_age(age, end_age=None) -> int:
        """Returns a random moons value for the given age.

        If just `age` is supplied, the range is that age range.
        If both are supplied, the range is `age`'s min and `end_age`'s max

        :param Age age: The age whose range to get (max overridden by end_age if applicable)
        :param Age end_age: The age whose maximum value to take, default None"""
        start = AgeMoonsRange[age.name].value[0]
        if end_age is not None:
            end = AgeMoonsRange[end_age.name]
        else:
            end = AgeMoonsRange[age.name].value[1]

        return randint(start, end)

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class AgeMoonsRange(Enum):
    """Relationship between life stage & moons. DO NOT CALL THIS"""
    NEWBORN = game.config["cat_ages"]["newborn"]
    KITTEN = game.config["cat_ages"]["kitten"]
    ADOLESCENT = game.config["cat_ages"]["adolescent"]
    YOUNGADULT = game.config["cat_ages"]["young adult"]
    ADULT = game.config["cat_ages"]["adult"]
    SENIORADULT = game.config["cat_ages"]["senior adult"]
    SENIOR = game.config["cat_ages"]["senior"]

    def __getitem__(self, item):
        return self.value[item]

    @staticmethod
    def breeding_age_range():
        return [AgeMoonsRange.ADOLESCENT[0], AgeMoonsRange.SENIOR[1]]
