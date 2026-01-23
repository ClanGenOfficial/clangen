import os
import unittest

from scripts.events_module.short.short_event import ShortEvent

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat.pelts import Pelt


class TestHandleEvent(unittest.TestCase):
    def setUp(self):
        self.chosen_event = ShortEvent(event_id="test")
        self.chosen_event.main_cat = Cat()
        self.chosen_event.random_cat = Cat()

    def test_mc_presence(self):
        # event should always use m_c by default
        self.chosen_event.execute_event()
        self.assertTrue(
            self.chosen_event.main_cat.ID in self.chosen_event.all_involved_cat_ids
        )

    def test_mc_exclusion(self):
        # remove if excluded
        self.chosen_event.exclude_involved = ["m_c"]
        self.chosen_event.execute_event()
        self.assertFalse(
            self.chosen_event.main_cat.ID in self.chosen_event.all_involved_cat_ids
        )

    def test_rc_presence(self):
        # no r_c specified
        self.chosen_event.execute_event()
        self.assertFalse(
            self.chosen_event.random_cat.ID in self.chosen_event.all_involved_cat_ids
        )

        # r_c specified
        self.chosen_event.r_c = {"age": "any"}
        self.chosen_event.execute_event()
        self.assertTrue(
            self.chosen_event.random_cat.ID in self.chosen_event.all_involved_cat_ids
        )

    def test_rc_exclusion(self):
        # remove if excluded
        self.chosen_event.r_c = {"age": "any"}
        self.chosen_event.exclude_involved = ["r_c"]
        self.chosen_event.execute_event()
        self.assertFalse(
            self.chosen_event.random_cat.ID in self.chosen_event.all_involved_cat_ids
        )


class TestHandleNewCats(unittest.TestCase):
    pass


class TestHandleAccessories(unittest.TestCase):
    def setUp(self):
        self.chosen_event = ShortEvent(event_id="test", new_accessory=["TEST"])
        self.chosen_event.main_cat = Cat(disable_random=True)
        self.pelts = Pelt

    def assert_intersection(self, a, b):
        """assert that the intersection of iterables a and b is non-empty"""

        self.assertTrue(set(a) & set(b))

    def test_misc_appended_to_types(self):
        self.chosen_event.types = []

        self.chosen_event.execute_event()
        self.assertIn("misc", self.chosen_event.types)

    def test_cat_gets_test_accessory(self):
        self.chosen_event.execute_event()
        self.assertEqual(self.chosen_event.main_cat.pelt.accessory, ["TEST"])

    def test_cat_gets_random_wild_accessory(self):
        self.chosen_event.new_accessory = ["WILD"]

        self.chosen_event.execute_event()
        self.assert_intersection(
            self.chosen_event.main_cat.pelt.accessory, self.pelts.wild_accessories
        )

    def test_cat_gets_random_plant_accessory(self):
        self.chosen_event.new_accessory = ["PLANT"]

        self.chosen_event.execute_event()
        self.assert_intersection(
            self.chosen_event.main_cat.pelt.accessory, self.pelts.plant_accessories
        )

    def test_cat_gets_random_collar_accessory(self):
        self.chosen_event.new_accessory = ["COLLAR"]

        self.chosen_event.execute_event()
        self.assert_intersection(
            self.chosen_event.main_cat.pelt.accessory, self.pelts.collar_accessories
        )

    def test_notail_cats_do_not_get_tail_accessories(self):
        self.chosen_event.new_accessory = self.pelts.tail_accessories
        self.chosen_event.main_cat.pelt.scars = ["NOTAIL"]

        self.chosen_event.execute_event()
        self.assertFalse(self.chosen_event.main_cat.pelt.accessory)

    def test_halftail_cats_do_not_get_tail_accessories(self):
        self.chosen_event.new_accessory = self.pelts.tail_accessories
        self.chosen_event.main_cat.pelt.scars = ["HALFTAIL"]

        self.chosen_event.execute_event()
        self.assertFalse(self.chosen_event.main_cat.pelt.accessory)


class TestHandleTransition(unittest.TestCase):
    def setUp(self):
        self.chosen_event = ShortEvent(
            event_id="test",
            sub_type=["transition"],
            new_gender=["trans male", "nonbinary"],
        )
        self.chosen_event.main_cat = Cat(gender="female", disable_random=True)

    def test_cat_transitions(self):
        self.chosen_event.execute_event()

        self.assertTrue(
            self.chosen_event.main_cat.genderalign != self.chosen_event.main_cat.gender
        )


class TestHandleDeath(unittest.TestCase):
    pass


class TestHandleMassDeath(unittest.TestCase):
    pass


class TestHandleDeathHistory(unittest.TestCase):
    pass


class TestHandleInjury(unittest.TestCase):
    def setUp(self):
        self.chosen_event = ShortEvent(
            event_id="test",
            r_c={"age": "any"},
            injury=[{"cats": ["m_c"], "injuries": ["scrapes"]}],
        )
        self.chosen_event.main_cat = Cat()
        self.chosen_event.random_cat = Cat()

    def test_types(self):
        self.chosen_event.execute_event()

        self.assertTrue("health" in self.chosen_event.types)

    def test_mc_injured(self):
        self.chosen_event.execute_event()

        self.assertTrue("scrapes" in self.chosen_event.main_cat.injuries)
        self.assertFalse("scrapes" in self.chosen_event.random_cat.injuries)

    def test_rc_injured(self):
        self.chosen_event.injury[0]["cats"] = ["r_c"]
        self.chosen_event.execute_event()

        self.assertTrue("scrapes" in self.chosen_event.random_cat.injuries)
        self.assertFalse("scrapes" in self.chosen_event.main_cat.injuries)

    def test_both_injured(self):
        self.chosen_event.injury[0]["cats"].append("r_c")
        self.chosen_event.execute_event()

        self.assertTrue("scrapes" in self.chosen_event.random_cat.injuries)
        self.assertTrue("scrapes" in self.chosen_event.main_cat.injuries)


class TestHandleInjuryHistory(unittest.TestCase):
    pass


class TestHandleFreshkillSupply(unittest.TestCase):
    pass


class TestHandleHerbSupply(unittest.TestCase):
    pass
