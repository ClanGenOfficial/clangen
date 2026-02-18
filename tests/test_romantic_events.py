import os
import unittest

from scripts.cat.factories.cat_factory import CatFactory
from scripts.cat.factories.enums import CatType

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship
from scripts.events_module.relationship.romantic_events import RomanticEvents


class RelationshipConditions(unittest.TestCase):
    def test_main_cat_status_one(self):
        # given
        cat1 = CatFactory.create_cat(CatType.TEST, disable_random=True)
        cat2 = CatFactory.create_cat(CatType.TEST, disable_random=True)

        condition = {
            "romance": 0,
            "like": 0,
            "respect": 0,
            "comfort": 15,
            "trust": 20,
        }

        # when
        rel_fulfill = Relationship(cat1, cat2)
        rel_fulfill.romance = 50
        rel_fulfill.like = 50
        rel_fulfill.comfort = 50
        rel_fulfill.respect = 50
        rel_fulfill.trust = 50

        # then
        self.assertTrue(
            RomanticEvents.relationship_fulfill_condition(rel_fulfill, condition)
        )
