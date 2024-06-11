from copy import deepcopy

from scripts.game_structure.game_essentials import game
from scripts.utility import get_alive_clan_queens


class Nutrition:
    """All the information about nutrition from one cat."""

    def __init__(self, status="warrior") -> None:
        """Initialize the class."""

        self._max_score = 1
        self._current_score = 1
        self.max_score = status
        self.needed_per_moon = 3

    def __str__(self):
        this_is_a_dict_not_a_string = {
            "max_score": self._max_score,
            "current_score": self.current_score,
            "percentage": self.percentage,
            "nutrition_text": self.nutrition_text,
        }
        return str(this_is_a_dict_not_a_string)

    @property
    def max_score(self):
        return self._max_score

    @max_score.setter
    def max_score(self, status):
        if isinstance(status, float) or isinstance(status, int):
            self._max_score = status
            return

        if status not in PREY_REQUIREMENT:
            self._max_score = 1
            return

        base_size = 3
        if status in ["newborn", "kitten", "elder"]:
            # todo: this is missing the nuance of the original
            #  which specified age in moons as well for elder
            base_size = 2

        required_max = PREY_REQUIREMENT[status] * base_size

        if self.max_score and required_max != self.max_score:
            prev_max = self._max_score
            self._max_score = required_max
            self.current_score = (
                    (self.current_score / prev_max) * required_max
            )

    @property
    def current_score(self):
        return self._current_score

    @current_score.setter
    def current_score(self, value) -> None:
        """Sets the current_score

        :param int|float value: value to set current_score to
        """
        if value > self.max_score:
            value = self.max_score
        if value < 0:
            value = 0
        self._current_score = value

    @property
    def percentage(self):
        return self.current_score / self.max_score * 100

    @percentage.setter
    def percentage(self, val):
        self.current_score = (val / 100) * self.max_score

    @property
    def nutrition_text(self):
        text_config = game.prey_config["text_nutrition"]
        nutrition_text = text_config["text"][0]
        for index in range(len(text_config["lower_range"])):
            if self.percentage >= text_config["lower_range"][index]:
                nutrition_text = text_config["text"][index]
        return nutrition_text

    @property
    def is_low_nutrition(self):
        return self.percentage < 100

    @staticmethod
    def is_pregnant_nursing_or_nursing_kit(cat_id, cat_injuries, cat_list):
        """True if cat is pregnant, nursing or a kit that is nursing"""
        queen_dict, kits = get_alive_clan_queens(cat_list)

        if "pregnant" in cat_injuries:
            return True

        # Nursing queens & associated kits
        for queen_id, their_kits in queen_dict.items():
            young_kits = [kit.ID for kit in their_kits if kit.moons < 3]
            if len(young_kits) == 0 and queen_id == cat_id:
                return False
            elif len(young_kits) == 0:
                continue

            for key in young_kits:
                if key == cat_id:
                    return True
            continue

    @staticmethod
    def update_nutrition(living_cats: list) -> None:
        """
        Handles increasing or decreasing the max score of their nutrition
        depending on their age. Automatically removes irrelevant cats.
        """
        queen_dict, kits = get_alive_clan_queens(living_cats)

        for cat in living_cats:
            if str(cat.status) not in PREY_REQUIREMENT:
                continue
            status_ = deepcopy(cat.status)
            if cat.ID in queen_dict.keys() or "pregnant" in cat.injuries:
                status_ = "queen/pregnant"

            cat.nutrition.max_score = status_
            cat.nutrition.needed_per_moon = PREY_REQUIREMENT[status_]


PREY_REQUIREMENT = game.prey_config["prey_requirement"]
