import unittest
from unittest.mock import patch

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts import events
from scripts.cat_relations.relationship import Relationship
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.events_module.relationship.romantic_events import Romantic_Events
from scripts.cat.cats import Cat
from scripts.clan import Clan

class CanHaveKits(unittest.TestCase):
    def test_prevent_kits(self):
        # given
        relation_events = Pregnancy_Events()
        cat = Cat()
        cat.no_kits = True

        # then
        self.assertFalse(relation_events.check_if_can_have_kits(cat,unknown_parent_setting=True, affair_setting=True))


class Pregnancy(unittest.TestCase):
    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits')
    def test_single_cat_female(self, check_if_can_have_kits):
        # given
        relation_events = Pregnancy_Events()
        clan = Clan(name="clan")
        cat = Cat(gender = 'female')
        clan.pregnancy_data = {}

        # when
        check_if_can_have_kits.return_value = True
        relation_events.handle_zero_moon_pregnant(cat,None,None,clan)

        # then
        self.assertIn(cat.ID, clan.pregnancy_data.keys())

    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits')
    def test_pair(self, check_if_can_have_kits):
        # given
        relation_events = Pregnancy_Events()
        clan = Clan(name="clan")
        cat1 = Cat(gender = 'female')
        cat2 = Cat(gender = 'male')

        relation = Relationship(cat1, cat2,mates=True,family=False,romantic_love=100)
        clan.pregnancy_data = {}

        # when
        check_if_can_have_kits.return_value = True
        relation_events.handle_zero_moon_pregnant(cat1,cat2,relation,clan)

        # then
        self.assertIn(cat1.ID, clan.pregnancy_data.keys())
        self.assertEqual(clan.pregnancy_data[cat1.ID]["second_parent"], cat2.ID)

    @patch('scripts.events_module.relationship.pregnancy_events.Pregnancy_Events.check_if_can_have_kits')
    def test_single_cat_male(self, check_if_can_have_kits):
        # given
        relation_events = Pregnancy_Events()
        clan = Clan(name="clan")
        cat = Cat(gender = 'male', moons=40)
        clan.pregnancy_data = {}
        number_before = len(cat.all_cats)

        # when
        check_if_can_have_kits.return_value = True
        relation_events.handle_zero_moon_pregnant(cat,None,None,clan)

        # then
        # a single male cat is not pregnant, event with the setting,
        # but should bring kits back to the clan
        self.assertNotEqual(number_before, len(cat.all_cats))

        # given
        relation_events = Pregnancy_Events()
        test_clan = Clan(name="clan")
        test_clan.pregnancy_data = {}
        cat1 = Cat(gender = 'female')
        cat1.no_kits = True
        cat2 = Cat(gender = 'male')

        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        relation1 = Relationship(cat1, cat2,mates=True,family=False,romantic_love=100)
        relation2 = Relationship(cat2, cat1,mates=True,family=False,romantic_love=100)
        cat1.relationships[cat2.ID] = relation1
        cat2.relationships[cat1.ID] = relation2

        # when
        check_if_can_have_kits.return_value = True
        relation_events.handle_having_kits(cat=cat1,clan=test_clan)

        # then
        self.assertNotIn(cat1.ID, test_clan.pregnancy_data.keys())


class Mates(unittest.TestCase):
    def test_platonic_kitten_mating(self):
        # given
        relation_events = Romantic_Events()
        cat1 = Cat(moons=3)
        cat2 = Cat(moons=3)

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.platonic_like = 100
        relationship2.platonic_like = 100

        # then
        self.assertFalse(relation_events.check_if_new_mate(relationship1,relationship2,cat1,cat2)[0])

    def test_platonic_apprentice_mating(self):
        # given
        relation_events = Romantic_Events()
        cat1 = Cat(moons=6)
        cat2 = Cat(moons=6)

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.platonic_like = 100
        relationship2.platonic_like = 100

        # then
        self.assertFalse(relation_events.check_if_new_mate(relationship1,relationship2,cat1,cat2)[0])

    def test_romantic_kitten_mating(self):
        # given
        relation_events = Romantic_Events()
        cat1 = Cat(moons=3)
        cat2 = Cat(moons=3)

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.romantic_love = 100
        relationship2.romantic_love = 100

        # then
        self.assertFalse(relation_events.check_if_new_mate(relationship1,relationship2,cat1,cat2)[0])

    def test_romantic_apprentice_mating(self):
        # given
        relation_events = Romantic_Events()
        cat1 = Cat(moons=6)
        cat2 = Cat(moons=6)

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        # when
        relationship1.romantic_love = 100
        relationship2.romantic_love = 100

        # then
        self.assertFalse(relation_events.check_if_new_mate(relationship1,relationship2,cat1,cat2)[0])
