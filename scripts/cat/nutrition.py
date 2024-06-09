from scripts.game_structure.game_essentials import game


class Nutrition:
    """All the information about nutrition from one cat."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.max_score = 1
        self.current_score = 0

    def __str__(self):
        this_is_a_dict_not_a_string = {
            "max_score": self.max_score,
            "current_score": self.current_score,
            "percentage": self.percentage,
            "nutrition_text": self.nutrition_text,
        }
        return str(this_is_a_dict_not_a_string)

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
        return self._current_score / self.max_score * 100

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
