import random

from scripts.cat.factories.enums import CatType
from scripts.cat.factories.new_cat_factory import NewCatFactory


class CatFactory:
    rng = random.Random()

    __factories = {
        CatType.NEW: NewCatFactory,
        CatType.LOAD: NewCatFactory,
        CatType.FADED: NewCatFactory,
    }

    @classmethod
    def set_rng(cls, rng):
        cls.rng = rng

    @classmethod
    def create_cat(cls, cat_type: CatType, **kwargs):
        return cls.__factories[cat_type](rng=cls.rng).create_cat(**kwargs)
