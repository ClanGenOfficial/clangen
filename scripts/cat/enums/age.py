from enum import Enum, IntEnum
from random import randint

from scripts.game_structure.game_essentials import game


class Age(IntEnum):
    """Cat age group"""
    NONE = 0
    NEWBORN = 1
    KITTEN = 2
    ADOLESCENT = 3
    YOUNGADULT = 4
    ADULT = 5
    SENIORADULT = 6
    SENIOR = 7

    def __str__(self):
        """ONLY USE FOR JSONING!"""
        if self == Age.YOUNGADULT:
            return "young adult"
        elif self == Age.SENIORADULT:
            return "senior adult"
        else:
            return self.name.lower()

    def is_kit(self):
        """True if cat is newborn or kitten"""
        return self in [Age.NEWBORN, Age.KITTEN]

    def is_underage(self):
        """True if cat is newborn, kitten or adolescent"""
        return self in [Age.NEWBORN, Age.KITTEN, Age.ADOLESCENT]
    def is_adult(self):
        """True is cat is young adult, adult or senior adult"""
        return self in [Age.YOUNGADULT, Age.ADULT, Age.SENIORADULT]

    def is_adult_or_senior(self):
        """True if cat is young adult, adult, senior adult or senior"""
        return self in [Age.YOUNGADULT, Age.ADULT, Age.SENIORADULT, Age.SENIOR]

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

    def get_age_moon_range(self):
        return AgeMoonsRange[self.name]
    @staticmethod
    def get_random_moons_for_age(age) -> int:
        age_moon = AgeMoonsRange[age.name]
        return randint(age_moon.value[0], age_moon.value[1])

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