from __future__ import annotations

import random

from scripts.cat.factories.enums import CatType
from scripts.cat.factories.load_cat_factory import LoadCatFactory
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.factories.test_cat_factory import TestCatFactory


class CatFactory:
    rng = random.Random()

    __factories = {
        CatType.NEW: NewCatFactory,
        CatType.LOAD_JSON: LoadCatFactory,
        CatType.LOAD_CSV: LoadCatFactory,
        CatType.FADED: LoadCatFactory,
        CatType.TEST: TestCatFactory,
    }

    @classmethod
    def set_rng(cls, rng):
        cls.rng = rng

    @classmethod
    def create_cat(cls, cat_type: CatType, **kwargs):
        return cls.__factories[cat_type](rng=cls.rng).create_cat(**kwargs)
