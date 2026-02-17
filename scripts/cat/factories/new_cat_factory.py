import random

from scripts.cat import save_load
from scripts.cat.cat_registry import registry
from scripts.cat.cats import Cat
from scripts.game_structure import game


class NewCatFactory:
    def __init__(self, rng=None):
        self.rng = rng or random.Random()

    def __call__(self, **overrides):
        cat_id = self.get_free_id()

        gender = overrides.get("gender", self._random_gender())

    def _random_gender(self):
        return self.rng.choice(("male", "female"))

    @staticmethod
    def get_free_id():
        potential_id = str(next(Cat.id_iter))

        if game.clan:
            faded_cats = save_load.get_faded_ids()
        else:
            faded_cats = []

        while potential_id in registry.all_cats or potential_id in faded_cats:
            potential_id = str(next(Cat.id_iter))
        return potential_id
