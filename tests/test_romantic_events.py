import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship
from scripts.events_module.relationship.romantic_events import RomanticEvents


class RelationshipConditions(unittest.TestCase):
    def test_main_cat_status_one(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        condition = {
            "romantic": 0,
            "platonic": 0,
            "dislike": 0,
            "admiration": 0,
            "comfortable": 15,
            "jealousy": -10,
            "trust": 20,
        }

        # when
        rel_fulfill = Relationship(cat1, cat2)
        rel_fulfill.romantic_love = 50
        rel_fulfill.platonic_like = 50
        rel_fulfill.dislike = 50
        rel_fulfill.comfortable = 50
        rel_fulfill.jealousy = 0
        rel_fulfill.trust = 50

        # then
        self.assertTrue(
            RomanticEvents.relationship_fulfill_condition(rel_fulfill, condition)
        )
