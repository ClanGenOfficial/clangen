import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.events_module.short.handle_short_events import HandleShortEvents


class TestHandleEvent(unittest.TestCase):
    pass


class TestHandleNewCats(unittest.TestCase):
    pass


class TestHandleAccessories(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock classes
        cls.event_class = type("EventClass", (), dict(new_accessory=[]))
        cls.pelt_class = type(
            "PeltClass",
            (),
            dict(
                wild_accessories=["WILD1", "WILD2"],
                plant_accessories=["PLANT1", "PLANT2"],
                collars=["COLLAR1", "COLLAR2"],
                head_accessories=["HEAD1", "HEAD2"],
                body_accessories=["BODY1", "BODY2"],
                tail_accessories=["TAIL1", "TAIL2"],
            ),
        )

    def setUp(self):
        self.test = HandleShortEvents()
        self.test.chosen_event = self.event_class()
        self.test.main_cat = Cat(disable_random=True)
        self.pelts = self.pelt_class()

    def assert_intersection(self, a, b):
        """assert that the intersection of iterables a and b is non-empty"""

        self.assertTrue(set(a) & set(b))

    def test_misc_appended_to_types(self):
        self.test.types = []

        self.test.handle_accessories()
        self.assertIn("misc", self.test.types)

    def test_cat_gets_test_accessory(self):
        self.test.chosen_event.new_accessory = ["TEST"]

        self.test.handle_accessories()
        self.assertEqual(self.test.main_cat.pelt.accessory, ["TEST"])

    def test_cat_gets_random_wild_accessory(self):
        self.test.chosen_event.new_accessory = ["WILD"]

        self.test.handle_accessories(pelts=self.pelt_class)
        self.assert_intersection(
            self.test.main_cat.pelt.accessory, self.pelts.wild_accessories
        )

    def test_cat_gets_random_plant_accessory(self):
        self.test.chosen_event.new_accessory = ["PLANT"]

        self.test.handle_accessories(pelts=self.pelt_class)
        self.assert_intersection(
            self.test.main_cat.pelt.accessory, self.pelts.plant_accessories
        )

    def test_cat_gets_random_collar_accessory(self):
        self.test.chosen_event.new_accessory = ["COLLAR"]

        self.test.handle_accessories(pelts=self.pelt_class)
        self.assert_intersection(self.test.main_cat.pelt.accessory, self.pelts.collars)

    def test_notail_cats_do_not_get_tail_accessories(self):
        self.test.chosen_event.new_accessory = self.pelts.tail_accessories
        self.test.main_cat.pelt.scars = "NOTAIL"

        self.test.handle_accessories(pelts=self.pelt_class)
        self.assertFalse(self.test.main_cat.pelt.accessory)

    def test_halftail_cats_do_not_get_tail_accessories(self):
        self.test.chosen_event.new_accessory = self.pelts.tail_accessories
        self.test.main_cat.pelt.scars = "HALFTAIL"

        self.test.handle_accessories(pelts=self.pelt_class)
        self.assertFalse(self.test.main_cat.pelt.accessory)


class TestHandleDeath(unittest.TestCase):
    pass


class TestHandleMassDeath(unittest.TestCase):
    pass


class TestHandleDeathHistory(unittest.TestCase):
    pass


class TestHandleInjury(unittest.TestCase):
    pass


class TestHandleInjuryHistory(unittest.TestCase):
    pass


class TestHandleFreshkillSupply(unittest.TestCase):
    pass


class TestHandleHerbSupply(unittest.TestCase):
    pass


class TestReset(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Mock class
        cls.handle = type(
            "HandleShortEventsClass",
            (),
            dict(
                herb_notice=None,
                types=[],
                sub_types=[],
                text=None,
                involved_cats=[],
                main_cat=None,
                random_cat=None,
                new_cat_objects=[],
                new_cats=[],
                victim_cat=None,
                murder_index=None,
                multi_cat=[],
                dead_cats=[],
                chosen_herb=None,
                other_clan=None,
                other_clan_name=None,
                chosen_event=None,
                additional_event_text="",
            ),
        )

    def test_reset_resets_all_attributes_to_default_values(self):
        default = self.handle()
        test = self.handle()
        # Check these are 2 separate instances
        self.assertNotEqual(test, default)

        # Given
        test.herb_notice = "herb notice"
        test.types = ["type1", "type2"]
        test.sub_types = ["type1", "type2"]
        test.text = "text"
        test.involved_cats = ["cat1", "cat2"]
        test.main_cat = "main cat"
        test.random_cat = "random cat"
        test.new_cat_objects = ["cat1", "cat2"]
        test.new_cats = [[Cat(disable_random=True)]]
        test.victim_cat = "victim cat"
        test.murder_index = "murder index"
        test.multi_cat = ["cat1", "cat2"]
        test.dead_cats = ["cat1", "cat2"]
        test.chosen_herb = "chosen herb"
        test.other_clan = "other clan"
        test.other_clan_name = "other clan name"
        test.chosen_event = "chosen event"
        test.additional_event_text = "additional event text"

        # When
        HandleShortEvents.reset(test)

        # Then
        self.assertEqual(test.herb_notice, default.herb_notice)
        self.assertEqual(test.types, default.types)
        self.assertEqual(test.sub_types, default.sub_types)
        self.assertEqual(test.text, default.text)
        self.assertEqual(test.involved_cats, default.involved_cats)
        self.assertEqual(test.main_cat, default.main_cat)
        self.assertEqual(test.random_cat, default.random_cat)
        self.assertEqual(test.new_cat_objects, default.new_cat_objects)
        self.assertEqual(test.new_cats, default.new_cats)
        self.assertEqual(test.victim_cat, default.victim_cat)
        self.assertEqual(test.murder_index, default.murder_index)
        self.assertEqual(test.multi_cat, default.multi_cat)
        self.assertEqual(test.dead_cats, default.dead_cats)
        self.assertEqual(test.chosen_herb, default.chosen_herb)
        self.assertEqual(test.other_clan, default.other_clan)
        self.assertEqual(test.other_clan_name, default.other_clan_name)
        self.assertEqual(test.chosen_event, default.chosen_event)
        self.assertEqual(test.additional_event_text, default.additional_event_text)
