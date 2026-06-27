import os
import unittest
from unittest.mock import patch

from scripts.cat.enums import CatGroup
from scripts.clan_package.settings import (
    load_clan_settings,
    set_clan_setting,
)
from scripts.game_structure import game

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.events_module.relationship.romantic_events import RomanticEvents


class TestPregnancySettings(unittest.TestCase):
    def setUp(self):
        load_clan_settings()
        Cat.disable_random = True

    def test_single_parent(self):
        parent1 = Cat(moons=50, gender="male")
        parent2 = Cat(moons=50, gender="female")

        # our parents are unmated, thus this would be single parenthood
        # allowed
        self.assertTrue(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=True,
                allow_unmated=True,
                allow_affair=True,
            )
        )
        # not allowed
        self.assertFalse(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=False,
                allow_unmated=True,
                allow_affair=True,
            )
        )

        # set mate
        parent1.mate = [parent2.ID]
        # single parentage setting shouldn't prevent these cats from having kits
        self.assertTrue(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=True,
                allow_unmated=True,
                allow_affair=True,
            )
        )
        self.assertTrue(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=False,
                allow_unmated=True,
                allow_affair=True,
            )
        )

    def test_unmated(self):
        parent1 = Cat(moons=50, gender="male")
        parent2 = Cat(moons=50, gender="female")

        # parent1 is unmated
        # allow
        self.assertTrue(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=True,
                allow_unmated=True,
                allow_affair=True,
            )
        )
        # don't allow
        set_clan_setting("unmated parentage", False)
        self.assertFalse(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=True,
                allow_unmated=False,
                allow_affair=True,
            )
        )

        # set mate
        parent1.mate = [parent2.ID]
        # unmated parentage setting shouldn't prevent these cats from having kits
        self.assertTrue(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=True,
                allow_unmated=True,
                allow_affair=True,
            )
        )
        self.assertTrue(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=True,
                allow_unmated=False,
                allow_affair=True,
            )
        )

    def test_affair(self):
        parent1 = Cat(moons=50, gender="male")
        parent2 = Cat(moons=50, gender="female")

        # our parents are unmated and so an affair isn't allowed (only mated cats have affairs)
        # allowed
        self.assertFalse(
            Pregnancy_Events.check_if_can_have_kits(
                parent1,
                allow_single_parent=False,
                allow_unmated=False,
                allow_affair=True,
            )
        )
        # set mate
        parent1.mate = [parent2.ID]
        affair_cat = Cat(moons=50, gender="female")
        parent1.relationships[affair_cat.ID] = Relationship(
            cat_from=parent1, cat_to=affair_cat, romance=100
        )
        # our parents ARE mated and so an affair is allowed
        # TODO: would love to test this, but the way affairs are set up does not allow it
        # self.assertEqual(
        #    Pregnancy_Events.get_second_parent(parent1), (affair_cat, True)
        # )

        # turn affairs off
        set_clan_setting("affair", False)
        # now an affair isn't allowed
        self.assertEqual(Pregnancy_Events.get_second_parent(parent1), (parent2, False))


class CanHaveKits(unittest.TestCase):
    def test_other_clan_pregnancy(self):
        test_clan = Clan(save_id="clan")
        test_clan.pregnancy_data = {}
        cat = Cat(disable_random=True, moons=50)
        game.used_group_IDs["5"] = CatGroup.OTHER_CLAN
        cat.status.add_to_group("5")

        self.assertFalse(Pregnancy_Events.handle_having_kits(cat, test_clan))

    def test_cat_not_working_pregnancy(self):
        test_clan = Clan(save_id="clan")
        test_clan.pregnancy_data = {}
        cat = Cat(disable_random=True, moons=50)
        cat.get_injured("broken bone")

        self.assertFalse(Pregnancy_Events.handle_having_kits(cat, test_clan))

    def test_prevent_kits(self):
        # given
        cat = Cat(disable_random=True)
        cat.no_kits = True

        # then
        self.assertFalse(
            Pregnancy_Events.check_if_can_have_kits(
                cat, allow_single_parent=True, allow_unmated=True, allow_affair=True
            )
        )

    @patch(
        "scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits"
    )
    def test_no_kit_setting(self, check_if_can_have_kits):
        # given
        test_clan = Clan(save_id="clan")
        test_clan.pregnancy_data = {}
        cat1 = Cat(gender="female", disable_random=True)
        cat1.no_kits = True
        cat2 = Cat(gender="male", disable_random=True)

        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        relation1 = Relationship(cat1, cat2, mates=True, family=False, romance=100)
        relation2 = Relationship(cat2, cat1, mates=True, family=False, romance=100)
        cat1.relationships[cat2.ID] = relation1
        cat2.relationships[cat1.ID] = relation2

        # when
        check_if_can_have_kits.return_value = True
        Pregnancy_Events.handle_having_kits(cat=cat1, clan=test_clan)

        # then
        self.assertNotIn(cat1.ID, test_clan.pregnancy_data.keys())


class SameSexAdoptions(unittest.TestCase):
    def test_kits_are_adopted(self):
        # given

        cat1 = Cat(gender="female", age="adult", moons=40, disable_random=True)
        cat2 = Cat(gender="female", age="adult", moons=40, disable_random=True)
        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)

        # when
        single_parentage = False
        unmated_parentage = False
        allow_affair = False
        self.assertTrue(
            Pregnancy_Events.check_if_can_have_kits(
                cat1, single_parentage, unmated_parentage, allow_affair
            )
        )
        self.assertTrue(
            Pregnancy_Events.check_if_can_have_kits(
                cat2, single_parentage, unmated_parentage, allow_affair
            )
        )

        can_have_kits, kits_are_adopted = Pregnancy_Events.check_second_parent(
            cat=cat1,
            second_parent=cat2,
            single_parentage=single_parentage,
            allow_unmated=unmated_parentage,
            allow_affair=allow_affair,
            same_sex_birth=False,
            same_sex_adoption=True,
        )
        self.assertTrue(can_have_kits)
        self.assertTrue(kits_are_adopted)


class Pregnancy(unittest.TestCase):
    @patch(
        "scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits"
    )
    def test_single_cat_female(self, check_if_can_have_kits):
        # given
        clan = Clan(save_id="clan")
        cat = Cat(gender="female", age="adult", moons=40, disable_random=True)
        clan.pregnancy_data = {}

        # when
        check_if_can_have_kits.return_value = True
        Pregnancy_Events.handle_zero_moon_pregnant(cat, None, clan)

        # then
        self.assertIn(cat.ID, clan.pregnancy_data.keys())

    @patch(
        "scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits"
    )
    def test_pair(self, check_if_can_have_kits):
        # given
        clan = Clan(save_id="clan")
        cat1 = Cat(gender="female", age="adult", moons=40, disable_random=True)
        cat2 = Cat(gender="male", age="adult", moons=40, disable_random=True)

        clan.pregnancy_data = {}

        # when
        check_if_can_have_kits.return_value = True
        Pregnancy_Events.handle_zero_moon_pregnant(cat1, cat2, clan)

        # then
        self.assertIn(cat1.ID, clan.pregnancy_data.keys())
        self.assertEqual(clan.pregnancy_data[cat1.ID]["second_parent"], cat2.ID)


class Mates(unittest.TestCase):
    def test_platonic_kitten_mating(self):
        # given
        cat1 = Cat(moons=3, disable_random=True)
        cat2 = Cat(moons=3, disable_random=True)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.like = 100
        relationship2.like = 100

        # then
        self.assertFalse(RomanticEvents.check_if_new_mate(cat1, cat2)[0])

    def test_platonic_apprentice_mating(self):
        # given
        cat1 = Cat(moons=6, disable_random=True)
        cat2 = Cat(moons=6, disable_random=True)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.like = 100
        relationship2.like = 100

        # then
        self.assertFalse(RomanticEvents.check_if_new_mate(cat1, cat2)[0])

    def test_romantic_kitten_mating(self):
        # given
        cat1 = Cat(moons=3, disable_random=True)
        cat2 = Cat(moons=3, disable_random=True)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.romance = 100
        relationship2.romance = 100

        # then
        self.assertFalse(RomanticEvents.check_if_new_mate(cat1, cat2)[0])

    def test_romantic_apprentice_mating(self):
        # given
        cat1 = Cat(moons=6, disable_random=True)
        cat2 = Cat(moons=6, disable_random=True)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.romance = 100
        relationship2.romance = 100

        # then
        self.assertFalse(RomanticEvents.check_if_new_mate(cat1, cat2)[0])
