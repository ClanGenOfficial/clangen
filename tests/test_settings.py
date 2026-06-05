import unittest

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.clan_package.settings import (
    load_clan_settings,
    get_clan_setting,
    set_clan_setting,
)
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events


class TestPregnancySettings(unittest.TestCase):
    def setUp(self):
        load_clan_settings()
        self.pregnancy_class = Pregnancy_Events()
        Cat.disable_random = True

    def test_single_parent(self):
        parent1 = Cat(moons=50, gender="male")
        parent2 = Cat(moons=50, gender="female")

        set_clan_setting("single parentage", True)
        set_clan_setting("unmated parentage", True)
        set_clan_setting("affair", True)
        # our parents are unmated, thus this would be single parenthood
        # allowed
        self.assertTrue(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )
        # not allowed
        set_clan_setting("single parentage", False)
        self.assertFalse(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )

        # set mate
        parent1.mate = [parent2.ID]
        # single parentage setting shouldn't prevent these cats from having kits
        set_clan_setting("single parentage", True)
        self.assertTrue(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )
        set_clan_setting("single parentage", False)
        self.assertTrue(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )

    def test_unmated(self):
        parent1 = Cat(moons=50, gender="male")
        parent2 = Cat(moons=50, gender="female")

        set_clan_setting("single parentage", True)
        set_clan_setting("unmated parentage", True)
        set_clan_setting("affair", True)

        # parent1 is unmated
        # allow
        self.assertTrue(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )
        # don't allow
        set_clan_setting("unmated parentage", False)
        self.assertFalse(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )

        # set mate
        parent1.mate = [parent2.ID]
        # unmated parentage setting shouldn't prevent these cats from having kits
        set_clan_setting("unmated parentage", True)
        self.assertTrue(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )
        set_clan_setting("unmated parentage", False)
        self.assertTrue(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )

    def test_affair(self):
        parent1 = Cat(moons=50, gender="male")
        parent2 = Cat(moons=50, gender="female")

        set_clan_setting("single parentage", False)
        set_clan_setting("unmated parentage", False)
        set_clan_setting("affair", True)
        # our parents are unmated and so an affair isn't allowed (only mated cats have affairs)
        # allowed
        self.assertFalse(
            self.pregnancy_class.check_if_can_have_kits(
                parent1,
                get_clan_setting("single parentage"),
                get_clan_setting("unmated parentage"),
                get_clan_setting("affair"),
            )
        )
        # set mate
        parent1.mate = [parent2.ID]
        affair_cat = Cat(moons=50, gender="female")
        parent1.relationships[affair_cat.ID] = Relationship(
            cat_from=parent1, cat_to=affair_cat, romance=100
        )
        # our parents ARE mated and so an affair is allowed
        # TODO: would love to test this, but the way affair are set up does not allow it
        # self.assertEqual(
        #    self.pregnancy_class.get_second_parent(parent1), (affair_cat, True)
        # )

        # turn affairs off
        set_clan_setting("affair", False)
        # now an affair isn't allowed
        self.assertEqual(
            self.pregnancy_class.get_second_parent(parent1), (parent2, False)
        )
