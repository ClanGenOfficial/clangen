import unittest
from mock import patch

from scripts.cat_relations.relation_events import Relation_Events
from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan

class ChanceOfKits(unittest.TestCase):
    def test_single_cat(self):
        # given
        relation_events = Relation_Events()
        cat = Cat(gender='female')

        # when
        relation_events.living_cats = 1

        # then
        chance = relation_events.get_kits_chance(cat)
        self.assertEqual(chance, 70)

    def test_pair_low_relation(self):
        # given
        relation_events = Relation_Events()
        cat1 = Cat(gender='female')
        cat2 = Cat(gender='female')

        relationship1_2 = Relationship(cat1,cat2)

        # when
        relation_events.living_cats = 2

        # then
        chance = relation_events.get_kits_chance(cat1,cat2,relationship1_2)
        self.assertEqual(chance, 35)

    def test_pair_semi_high_relation_1(self):
        # given
        relation_events = Relation_Events()
        cat1 = Cat(gender='female')
        cat2 = Cat(gender='female')

        relationship1_2 = Relationship(cat1,cat2)
        relationship1_2.romantic_love += 50
    
        # when
        relation_events.living_cats = 2
        
        # then
        chance = relation_events.get_kits_chance(cat1,cat2,relationship1_2)
        self.assertEqual(chance, 30)

    def test_pair_semi_high_relation_2(self):
        # given
        relation_events = Relation_Events()
        cat1 = Cat(gender='female')
        cat2 = Cat(gender='female')

        relationship1_2 = Relationship(cat1,cat2)
        relationship1_2.romantic_love += 70
        relationship1_2.comfortable += 50

        # when
        relation_events.living_cats = 2
        
        # then
        chance = relation_events.get_kits_chance(cat1,cat2,relationship1_2)
        self.assertEqual(chance, 20)

    def test_pair_highest_relation(self):
        # given
        relation_events = Relation_Events()
        cat1 = Cat(gender='female')
        cat2 = Cat(gender='female')

        relationship1_2 = Relationship(cat1,cat2)
        relationship1_2.romantic_love += 100
        relationship1_2.comfortable += 100

        # when
        relation_events.living_cats = 2

        # then
        chance = relation_events.get_kits_chance(cat1,cat2,relationship1_2)
        self.assertEqual(chance, 5)

    def test_pair_old_male(self):
        # given
        relation_events = Relation_Events()
        cat1 = Cat(gender='female')
        cat2 = Cat(gender='male', moons=120)
        
        relationship1_2 = Relationship(cat1,cat2)

        # when
        relation_events.living_cats = 2

        # then
        chance = relation_events.get_kits_chance(cat1,cat2,relationship1_2)
        self.assertEqual(chance, 80)

    def test_pair_highest_relation_many_cats(self):
        # given
        relation_events = Relation_Events()
        cat1 = Cat(gender='female')
        cat2 = Cat(gender='female')

        relationship1_2 = Relationship(cat1,cat2)
        relationship1_2.romantic_love += 100
        relationship1_2.comfortable += 100

        # when
        relation_events.living_cats = 45

        # then
        chance = relation_events.get_kits_chance(cat1,cat2,relationship1_2)
        self.assertEqual(chance, 115)

    def test_pair_single_many_cats(self):
        # given
        relation_events = Relation_Events()
        cat1 = Cat(gender='female')

        # when
        relation_events.living_cats = 45

        # then
        chance = relation_events.get_kits_chance(cat1)
        self.assertEqual(chance, 190)


class Pregnancy(unittest.TestCase):
    @patch('scripts.cat_relations.relation_events.Relation_Events.get_kits_chance')
    def test_single_cat_female(self, get_kits_chance):
        # given
        relation_events = Relation_Events()
        clan = Clan()
        cat = Cat(gender = 'female')
        clan.pregnancy_data = {}

        # when
        get_kits_chance.return_value = 1
        relation_events.handle_zero_moon_pregnant(cat,None,None,clan)

        # then
        self.assertTrue(cat.ID in clan.pregnancy_data.keys())

    @patch('scripts.cat_relations.relation_events.Relation_Events.get_kits_chance')
    def test_pair(self, get_kits_chance):
        # given
        relation_events = Relation_Events()
        clan = Clan()
        cat1 = Cat(gender = 'female')
        cat2 = Cat(gender = 'male')

        relation = Relationship(cat1, cat2,mates=True,family=False,romantic_love=100)
        clan.pregnancy_data = {}

        # when
        get_kits_chance.return_value = 1
        relation_events.handle_zero_moon_pregnant(cat1,cat2,relation,clan)

        # then
        self.assertTrue(cat1.ID in clan.pregnancy_data.keys())

    @patch('scripts.cat_relations.relation_events.Relation_Events.get_kits_chance')
    def test_single_cat_male(self, get_kits_chance):
        # given
        relation_events = Relation_Events()
        clan = Clan()
        cat = Cat(gender = 'male', moons=40)
        clan.pregnancy_data = {}
        number_before = len(cat.all_cats)

        # when
        get_kits_chance.return_value = 1
        relation_events.handle_zero_moon_pregnant(cat,None,None,clan)

        # then
        self.assertNotEqual(number_before, len(cat.all_cats))