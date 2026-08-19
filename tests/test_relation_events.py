import os
import unittest
from unittest.mock import patch

from scripts.cat.enums import CatGroup
from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.clan_package.settings import (
    load_clan_settings,
    set_clan_setting,
)
from scripts.cat.microservices.conditions import get_injured
from scripts.game_structure import game

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan
from scripts.events_module.pregnancy import pregnancy_events

cat_factory = TestCatFactory()


class TestPregnancySettings(unittest.TestCase):
    def setUp(self):
        load_clan_settings()

    def test_single_parent(self):
        parent1 = cat_factory.create_cat(moons=50, gender="male")
        parent2 = cat_factory.create_cat(moons=50, gender="female")

        # our parents are unmated, thus this would be single parenthood
        # allowed
        set_clan_setting("single parentage", True)
        self.assertTrue(pregnancy_events.check_if_can_have_kits(parent1))
        # not allowed
        set_clan_setting("single parentage", False)
        self.assertFalse(pregnancy_events.check_if_can_have_kits(parent1))

        # set mate
        parent1.mate = [parent2.ID]
        # single parentage setting shouldn't prevent these cats from having kits
        self.assertTrue(pregnancy_events.check_if_can_have_kits(parent1))

    def test_ignore_biology(self):
        parent1 = cat_factory.create_cat(moons=50, gender="male")
        parent2 = cat_factory.create_cat(moons=50, gender="male")
        set_clan_setting("same sex birth", False)

        self.assertEqual(
            pregnancy_events.check_second_parent(parent1, parent2), (False, False)
        )

    def test_unmated(self):
        parent1 = cat_factory.create_cat(moons=50, gender="male")
        parent2 = cat_factory.create_cat(moons=50, gender="female")

        # parent1 is unmated
        # allow
        set_clan_setting("unmated parentage", True)
        self.assertTrue(pregnancy_events.check_if_can_have_kits(parent1))
        # don't allow
        set_clan_setting("unmated parentage", False)
        self.assertFalse(pregnancy_events.check_if_can_have_kits(parent1))

        # set mate
        parent1.mate = [parent2.ID]
        # unmated parentage setting shouldn't prevent these cats from having kits
        self.assertTrue(pregnancy_events.check_if_can_have_kits(parent1))
        self.assertTrue(pregnancy_events.check_if_can_have_kits(parent1))

    def test_affair(self):
        parent1 = cat_factory.create_cat(moons=50, gender="male")
        parent2 = cat_factory.create_cat(moons=50, gender="female")

        # our parents are unmated and so an affair isn't allowed (only mated cats have affairs)
        # allowed
        self.assertFalse(pregnancy_events.check_if_can_have_kits(parent1))
        # set mate
        parent1.mate = [parent2.ID]
        affair_cat = cat_factory.create_cat(moons=50, gender="female")
        parent1.relationships[affair_cat.ID] = Relationship(
            cat_from=parent1, cat_to=affair_cat, romance=100
        )
        # our parents ARE mated and so an affair is allowed
        # TODO: would love to test this, but the way affairs are set up does not allow it
        # self.assertEqual(
        #    pregnancy_events.get_second_parent(parent1), (affair_cat, True)
        # )

        # turn affairs off
        set_clan_setting("affair", False)
        # now an affair isn't allowed
        self.assertEqual(pregnancy_events.get_second_parent(parent1), (parent2, False))


class CanHaveKits(unittest.TestCase):
    def test_other_clan_pregnancy(self):
        test_clan = Clan(save_id="clan")
        test_clan.pregnancy_data = {}
        cat = cat_factory.create_cat(gender="female", moons=50)
        game.used_group_IDs["5"] = CatGroup.OTHER_CLAN
        cat.status.add_to_group("5")

        self.assertFalse(pregnancy_events.handle_having_kits(cat))

    def test_cat_not_working_pregnancy(self):
        test_clan = Clan(save_id="clan")
        test_clan.pregnancy_data = {}
        cat = cat_factory.create_cat(gender="female", moons=50)
        get_injured(cat, "broken bone")

        self.assertFalse(pregnancy_events.handle_having_kits(cat))

    def test_prevent_kits(self):
        # given
        cat = cat_factory.create_cat(disable_random=True)
        cat.no_kits = True

        # then
        self.assertFalse(pregnancy_events.check_if_can_have_kits(cat))

    @patch("scripts.events_module.pregnancy.check_parents.check_if_can_have_kits")
    def test_no_kit_setting(self, check_if_can_have_kits):
        # given
        test_clan = Clan(save_id="clan")
        test_clan.pregnancy_data = {}
        cat1 = cat_factory.create_cat(gender="female", disable_random=True)
        cat1.no_kits = True
        cat2 = cat_factory.create_cat(gender="male", disable_random=True)

        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        relation1 = Relationship(cat1, cat2, family=False, romance=100)
        relation2 = Relationship(cat2, cat1, family=False, romance=100)
        cat1.relationships[cat2.ID] = relation1
        cat2.relationships[cat1.ID] = relation2

        # when
        check_if_can_have_kits.return_value = True
        pregnancy_events.handle_having_kits(cat=cat1)

        # then
        self.assertNotIn(cat1.ID, test_clan.pregnancy_data.keys())


class SameSexAdoptions(unittest.TestCase):
    def test_kits_are_adopted(self):
        # given

        cat1 = cat_factory.create_cat(
            gender="female", age="adult", moons=40, disable_random=True
        )
        cat2 = cat_factory.create_cat(
            gender="female", age="adult", moons=40, disable_random=True
        )
        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        set_clan_setting("same sex adoption", True)
        # when
        self.assertTrue(pregnancy_events.check_if_can_have_kits(cat1))
        self.assertTrue(pregnancy_events.check_if_can_have_kits(cat2))

        can_have_kits, kits_are_adopted = pregnancy_events.check_second_parent(
            cat=cat1, second_parent=cat2
        )
        self.assertTrue(can_have_kits)
        self.assertTrue(kits_are_adopted)


class Pregnancy(unittest.TestCase):
    @patch("scripts.events_module.pregnancy.check_parents.check_if_can_have_kits")
    def test_single_cat_female(self, check_if_can_have_kits):
        # given
        clan = Clan(save_id="clan")
        cat = cat_factory.create_cat(
            gender="female", age="adult", moons=40, disable_random=True
        )
        clan.pregnancy_data = {}

        # when
        check_if_can_have_kits.return_value = True
        pregnancy_events.handle_zero_moon_pregnant(cat, None)

        # then
        self.assertIn(cat.ID, clan.pregnancy_data.keys())

    @patch("scripts.events_module.pregnancy.check_parents.check_if_can_have_kits")
    def test_pair(self, check_if_can_have_kits):
        # given
        clan = Clan(save_id="clan")
        cat1 = cat_factory.create_cat(
            gender="female", age="adult", moons=40, disable_random=True
        )
        cat2 = cat_factory.create_cat(
            gender="male", age="adult", moons=40, disable_random=True
        )

        clan.pregnancy_data = {}

        # when
        check_if_can_have_kits.return_value = True
        pregnancy_events.handle_zero_moon_pregnant(cat1, cat2)

        # then
        self.assertIn(cat1.ID, clan.pregnancy_data.keys())
        self.assertEqual(clan.pregnancy_data[cat1.ID]["second_parent"], cat2.ID)
