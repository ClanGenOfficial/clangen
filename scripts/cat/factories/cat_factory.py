import random

from scripts.cat.factories.enums import CatType
from scripts.cat.factories.new_cat_factory import NewCatFactory


class CatFactory:
    __factories = {
        CatType.NEW: NewCatFactory,
        CatType.LOAD: "TODO ADD",
        CatType.FADED: "TODO ADD",
    }

    def __init__(self, rng=None):
        self.rng = rng if rng else random.Random()

    def create_cat(self, cat_type: CatType, **kwargs):
        return self.__factories[cat_type](**kwargs)
