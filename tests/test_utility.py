import unittest

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.utility import (
	get_highest_romantic_relation, 
	get_personality_compatibility, 
	get_amount_of_cats_with_relation_value_towards,
    get_alive_clan_queens
)

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
        # TODO: the one who updated the personality should update the tests!!
        pass
        cat1 = Cat()
        cat2 = Cat()

        cat1.personality.trait = self.current_traits[0]
        cat2.personality.trait = self.current_traits[1]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

        cat1.personality.trait = self.current_traits[3]
        cat2.personality.trait = self.current_traits[5]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

        cat1.personality.trait = self.current_traits[7]
        cat2.personality.trait = self.current_traits[10]
        self.assertIsNone(get_personality_compatibility(cat1,cat2))
        self.assertIsNone(get_personality_compatibility(cat2,cat1))

    def test_some_positive_combinations(self):
        # TODO: the one who updated the personality should update the tests!!
        pass
        cat1 = Cat()
        cat2 = Cat()

        cat1.personality.trait = self.current_traits[1]
        cat2.personality.trait = self.current_traits[18]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

        cat1.personality.trait = self.current_traits[3]
        cat2.personality.trait = self.current_traits[4]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

        cat1.personality.trait = self.current_traits[5]
        cat2.personality.trait = self.current_traits[17]
        self.assertTrue(get_personality_compatibility(cat1,cat2))
        self.assertTrue(get_personality_compatibility(cat2,cat1))

    def test_some_negative_combinations(self):
        # TODO: the one who updated the personality should update the tests!!
        pass
        cat1 = Cat()
        cat2 = Cat()

        cat1.personality.trait = self.current_traits[1]
        cat2.personality.trait = self.current_traits[2]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

        cat1.personality.trait = self.current_traits[3]
        cat2.personality.trait = self.current_traits[6]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

        cat1.personality.trait = self.current_traits[8]
        cat2.personality.trait = self.current_traits[9]
        self.assertFalse(get_personality_compatibility(cat1,cat2))
        self.assertFalse(get_personality_compatibility(cat2,cat1))

    def test_false_trait(self):
        cat1 = Cat()
        cat2 = Cat()
        cat1.personality.trait = None
        cat2.personality.trait = None
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

class TestHighestRomance(unittest.TestCase):
    def test_exclude_mate(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat3 = Cat()
        cat4 = Cat()

        # when
        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        relation_1_2 = Relationship(cat_from=cat1,cat_to=cat2, mates=True)
        relation_1_3 = Relationship(cat_from=cat1,cat_to=cat3)
        relation_1_4 = Relationship(cat_from=cat1,cat_to=cat4)
        relation_1_2.romantic_love = 60
        relation_1_3.romantic_love = 50
        relation_1_4.romantic_love = 40

        relations = [relation_1_2, relation_1_3, relation_1_4]

        #then
        self.assertNotEqual(relation_1_2, get_highest_romantic_relation(relations, exclude_mate=True))
        self.assertEqual(relation_1_3, get_highest_romantic_relation(relations, exclude_mate=True))
        self.assertNotEqual(relation_1_4, get_highest_romantic_relation(relations, exclude_mate=True))

    def test_include_mate(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat3 = Cat()
        cat4 = Cat()

        # when
        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        relation_1_2 = Relationship(cat_from=cat1,cat_to=cat2, mates=True)
        relation_1_3 = Relationship(cat_from=cat1,cat_to=cat3)
        relation_1_4 = Relationship(cat_from=cat1,cat_to=cat4)
        relation_1_2.romantic_love = 60
        relation_1_3.romantic_love = 50
        relation_1_4.romantic_love = 40

        relations = [relation_1_2, relation_1_3, relation_1_4]

        #then
        self.assertEqual(relation_1_2, get_highest_romantic_relation(relations, exclude_mate=False))
        self.assertNotEqual(relation_1_3, get_highest_romantic_relation(relations, exclude_mate=False))
        self.assertNotEqual(relation_1_4, get_highest_romantic_relation(relations, exclude_mate=False))

class TestgetQueens(unittest.TestCase):
    def test_single_mother(self):
        # given
        # young enough kid
        mother1 = Cat()
        mother1.gender = "female"
        mother1.status = "warrior"
        kid1 = Cat()
        kid1.status = "kitten"
        kid1.parent1 = mother1

        # too old kid
        mother2 = Cat()
        mother2.gender = "female"
        mother2.status = "warrior"
        kid2 = Cat()
        kid2.status = "apprentice"
        kid2.parent1 = mother2

        # then
        self.assertEqual([mother1.ID], list(get_alive_clan_queens(Cat)[0].keys()))

    def test_single_father(self):
        # given
        # young enough kid
        father1 = Cat()
        father1.gender = "male"
        father1.status = "warrior"
        kid1 = Cat()
        kid1.status = "kitten"
        kid1.parent1 = father1

        # too old kid
        father2 = Cat()
        father2.gender = "male"
        father2.status = "warrior"
        kid2 = Cat()
        kid2.status = "apprentice"
        kid2.parent1 = father2

        # then
        self.assertEqual([father1.ID], list(get_alive_clan_queens(Cat)[0].keys()))

    def tests_hetero_pair(self):
        # given
        # young enough kid
        mother1 = Cat()
        mother1.gender = "female"
        mother1.status = "warrior"
        father1 = Cat()
        father1.gender = "male"
        father1.status = "warrior"
        kid1 = Cat()
        kid1.status = "kitten"
        kid1.parent1 = father1
        kid1.parent2 = mother1

        # too old kid
        mother2 = Cat()
        mother2.gender = "female"
        mother2.status = "warrior"
        father2 = Cat()
        father2.gender = "male"
        father2.status = "warrior"
        kid2 = Cat()
        kid2.status = "apprentice"
        kid2.parent1 = father2
        kid2.parent2 = mother2

        # then
        self.assertEqual([mother1.ID], list(get_alive_clan_queens(Cat)[0].keys()))

    def test_gay_pair(self):
        # given
        # young enough kid
        father11 = Cat()
        father11.gender = "male"
        father11.status = "warrior"
        father12 = Cat()
        father12.gender = "male"
        father12.status = "warrior"
        kid1 = Cat()
        kid1.status = "kitten"
        kid1.parent1 = father12
        kid1.parent2 = father11

        # too old kid
        father21 = Cat()
        father21.gender = "male"
        father21.status = "warrior"
        father22 = Cat()
        father22.gender = "male"
        father22.status = "warrior"
        kid2 = Cat()
        kid2.status = "apprentice"
        kid2.parent1 = father22
        kid2.parent2 = father21

        # then
        self.assertTrue(
            [father11.ID] == list(get_alive_clan_queens(Cat)[0].keys()) or [father12.ID] == list(get_alive_clan_queens(Cat)[0].keys())
        )

    def test_lesbian_pair(self):
        # given
        # young enough kid
        mother11 = Cat()
        mother11.gender = "female"
        mother11.status = "warrior"
        mother12 = Cat()
        mother12.gender = "female"
        mother12.status = "warrior"
        kid1 = Cat()
        kid1.status = "kitten"
        kid1.parent1 = mother12
        kid1.parent2 = mother11

        # too old kid
        mother21 = Cat()
        mother21.gender = "female"
        mother21.status = "warrior"
        mother22 = Cat()
        mother22.gender = "female"
        mother22.status = "warrior"
        kid2 = Cat()
        kid2.status = "apprentice"
        kid2.parent1 = mother22
        kid2.parent2 = mother21

        # then
        self.assertTrue(
            [mother11.ID] == list(get_alive_clan_queens(Cat)[0].keys()) or [mother12.ID] == list(get_alive_clan_queens(Cat)[0].keys())
        )

    def test_poly_pair(self):
        # given
        # young enough kid
        parent11 = Cat()
        parent11.gender = "female"
        parent11.status = "warrior"
        parent12 = Cat()
        parent12.gender = "female"
        parent12.status = "warrior"
        parent13 = Cat()
        parent13.gender = "male"
        parent13.status = "warrior"
        kid1 = Cat()
        kid1.status = "kitten"
        kid1.parent1 = parent12
        kid1.parent2 = parent11
        kid1.adoptive_parents.append(parent13)

        # too old kid
        parent21 = Cat()
        parent21.gender = "female"
        parent21.status = "warrior"
        parent22 = Cat()
        parent22.gender = "female"
        parent22.status = "warrior"
        parent23 = Cat()
        parent23.gender = "male"
        parent23.status = "warrior"
        kid2 = Cat()
        kid2.status = "apprentice"
        kid2.parent1 = parent22
        kid2.parent2 = parent11
        kid2.adoptive_parents.append(parent23)

        # then
        self.assertEqual([parent12.ID], list(get_alive_clan_queens(Cat)[0].keys()))
