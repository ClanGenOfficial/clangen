import unittest

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.utility import get_personality_compatibility, get_amount_of_cats_with_relation_value_towards

class TestPersonalityCompatibility(unittest.TestCase):

    current_traits = [
        'adventurous', 'altruistic', 'ambitious', 'bloodthirsty', 'bold',
        'calm', 'careful', 'charismatic', 'childish', 'cold', 'compassionate',
        'confident', 'daring', 'empathetic', 'faithful', 'fierce', 'insecure',
        'lonesome', 'loving', 'loyal', 'nervous', 'patient', 'playful',
        'responsible', 'righteous', 'shameless', 'sneaky', 'strange', 'strict',
        'thoughtful', 'troublesome', 'vengeful', 'wise'
    ]

    def test_some_neutral_combinations(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.trait = self.current_traits[0]
        cat2.trait = self.current_traits[1]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[3]
        cat2.trait = self.current_traits[5]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[7]
        cat2.trait = self.current_traits[10]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

    def test_some_positive_combinations(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.trait = self.current_traits[1]
        cat2.trait = self.current_traits[18]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[3]
        cat2.trait = self.current_traits[4]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[5]
        cat2.trait = self.current_traits[17]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

    def test_some_negative_combinations(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.trait = self.current_traits[1]
        cat2.trait = self.current_traits[2]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[3]
        cat2.trait = self.current_traits[6]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

        cat1.trait = self.current_traits[8]
        cat2.trait = self.current_traits[9]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

    def test_not_existing_trait(self):
        cat1 = Cat()
        cat2 = Cat()

        cat1.trait = 'testing'
        cat2.trait = 'testing'
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

    def test_false_trait(self):
        cat1 = Cat()
        cat2 = Cat()
        cat1.trait = None
        cat2.trait = None
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

class TestCountRelation(unittest.TestCase):
    def test_2_cats_jealousy(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat3 = Cat()
        cat4 = Cat()

        relation_1_2 = Relationship(cat_from=cat1,cat_to=cat2)
        relation_3_2 = Relationship(cat_from=cat3,cat_to=cat2)
        relation_4_2 = Relationship(cat_from=cat4,cat_to=cat2)
        cat1.relationships[cat2.ID] = relation_1_2
        cat3.relationships[cat2.ID] = relation_3_2
        cat4.relationships[cat2.ID] = relation_4_2
        relation_1_2.link_relationship()
        relation_3_2.link_relationship()
        relation_4_2.link_relationship()

        # when
        relation_1_2.jealousy += 20
        relation_3_2.jealousy += 20
        relation_4_2.jealousy += 10

        #then
        relation_dict = get_amount_of_cats_with_relation_value_towards(cat2,20,[cat1,cat2,cat3,cat4])

        self.assertEqual(relation_dict["romantic_love"],0)
        self.assertEqual(relation_dict["platonic_like"],0)
        self.assertEqual(relation_dict["dislike"],0)
        self.assertEqual(relation_dict["admiration"],0)
        self.assertEqual(relation_dict["comfortable"],0)
        self.assertEqual(relation_dict["jealousy"],2)
        self.assertEqual(relation_dict["trust"],0)
