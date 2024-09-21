import os
import unittest
from unittest.mock import patch

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.events_module.relationship.romantic_events import Romantic_Events

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


class CanHaveKits(unittest.TestCase):
    def test_prevent_kits(self):
        # given
        cat = Cat()
        cat.no_kits = True

        # then
        self.assertFalse(Pregnancy_Events.check_if_can_have_kits(cat, single_parentage=True, allow_affair=True))

    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits')
    def test_no_kit_setting(self, check_if_can_have_kits):
        # given
        test_clan = Clan(name="clan")
        test_clan.pregnancy_data = {}
        cat1 = Cat(sex='female')
        cat1.no_kits = True
        cat2 = Cat(sex='male')

        cat1.current_mate.append(cat2.cat_id)
        cat2.current_mate.append(cat1.cat_id)
        relation1 = Relationship(cat1, cat2, mates=True, family=False, romantic_love=100)
        relation2 = Relationship(cat2, cat1, mates=True, family=False, romantic_love=100)
        cat1.relationships[cat2.cat_id] = relation1
        cat2.relationships[cat1.cat_id] = relation2

        # when
        check_if_can_have_kits.return_value = True
        Pregnancy_Events.handle_having_kits(cat=cat1, clan=test_clan)

        # then
        self.assertNotIn(cat1.cat_id, test_clan.pregnancy_data.keys())


class SameSexAdoptions(unittest.TestCase):
    def test_kits_are_adopted(self):
        # given

        cat1 = Cat(sex='female', age="adult", moons=40)
        cat2 = Cat(sex='female', age="adult", moons=40)
        cat1.current_mate.append(cat2.cat_id)
        cat2.current_mate.append(cat1.cat_id)

        # when
        single_parentage = False
        allow_affair = False
        self.assertTrue(Pregnancy_Events.check_if_can_have_kits(cat1, single_parentage, allow_affair))
        self.assertTrue(Pregnancy_Events.check_if_can_have_kits(cat2, single_parentage, allow_affair))

        can_have_kits, kits_are_adopted = Pregnancy_Events.check_second_parent(
            cat=cat1,
            second_parent=cat2,
            single_parentage=single_parentage,
            allow_affair=allow_affair,
            same_sex_birth=False,
            same_sex_adoption=True
        )
        self.assertTrue(can_have_kits)
        self.assertTrue(kits_are_adopted)


class Pregnancy(unittest.TestCase):
    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits')
    def test_single_cat_female(self, check_if_can_have_kits):
        # given
        clan = Clan(name="clan")
        cat = Cat(sex='female', age="adult", moons=40)
        clan.pregnancy_data = {}

        # when
        check_if_can_have_kits.return_value = True
        Pregnancy_Events.handle_zero_moon_pregnant(cat, None, clan)

        # then
        self.assertIn(cat.cat_id, clan.pregnancy_data.keys())

    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits')
    def test_pair(self, check_if_can_have_kits):
        # given
        clan = Clan(name="clan")
        cat1 = Cat(sex='female', age="adult", moons=40)
        cat2 = Cat(sex='male', age="adult", moons=40)

        clan.pregnancy_data = {}

        # when
        check_if_can_have_kits.return_value = True
        Pregnancy_Events.handle_zero_moon_pregnant(cat1, cat2, clan)

        # then
        self.assertIn(cat1.cat_id, clan.pregnancy_data.keys())
        self.assertEqual(clan.pregnancy_data[cat1.cat_id]["second_parent"], cat2.cat_id)


class Mates(unittest.TestCase):
    def test_platonic_kitten_mating(self):
        # given
        cat1 = Cat(moons=3)
        cat2 = Cat(moons=3)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.cat_id] = relationship1
        cat2.relationships[cat1.cat_id] = relationship2

        # when
        relationship1.platonic_like = 100
        relationship2.platonic_like = 100

        # then
        self.assertFalse(Romantic_Events.check_if_new_mate(cat1, cat2)[0])

    def test_platonic_apprentice_mating(self):
        # given
        cat1 = Cat(moons=6)
        cat2 = Cat(moons=6)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.cat_id] = relationship1
        cat2.relationships[cat1.cat_id] = relationship2

        # when
        relationship1.platonic_like = 100
        relationship2.platonic_like = 100

        # then
        self.assertFalse(Romantic_Events.check_if_new_mate(cat1, cat2)[0])

    def test_romantic_kitten_mating(self):
        # given
        cat1 = Cat(moons=3)
        cat2 = Cat(moons=3)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.cat_id] = relationship1
        cat2.relationships[cat1.cat_id] = relationship2

        # when
        relationship1.romantic_love = 100
        relationship2.romantic_love = 100

        # then
        self.assertFalse(Romantic_Events.check_if_new_mate(cat1, cat2)[0])

    def test_romantic_apprentice_mating(self):
        # given
        cat1 = Cat(moons=6)
        cat2 = Cat(moons=6)

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.cat_id] = relationship1
        cat2.relationships[cat1.cat_id] = relationship2

        # when
        relationship1.romantic_love = 100
        relationship2.romantic_love = 100

        # then
        self.assertFalse(Romantic_Events.check_if_new_mate(cat1, cat2)[0])
