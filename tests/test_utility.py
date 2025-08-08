import os
import unittest

from scripts.cat.enums import CatRank

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.utility import (
    get_highest_romantic_relation,
    get_personality_compatibility,
    get_num_of_cats_with_relation_amount_towards,
    get_alive_clan_queens,
)


class TestPersonalityCompatibility(unittest.TestCase):
    current_traits = [
        "adventurous",
        "altruistic",
        "ambitious",
        "bloodthirsty",
        "bold",
        "calm",
        "careful",
        "charismatic",
        "childish",
        "cold",
        "compassionate",
        "confident",
        "daring",
        "empathetic",
        "faithful",
        "fierce",
        "insecure",
        "lonesome",
        "loving",
        "loyal",
        "nervous",
        "patient",
        "playful",
        "responsible",
        "righteous",
        "shameless",
        "sneaky",
        "strange",
        "strict",
        "thoughtful",
        "troublesome",
        "vengeful",
        "wise",
    ]

    def test_some_neutral_combinations(self):
        # TODO: the one who updated the personality should update the tests!!
        pass
        # cat1 = Cat()
        # cat2 = Cat()

    #
    # cat1.personality.trait = self.current_traits[0]
    # cat2.personality.trait = self.current_traits[1]
    # self.assertIsNone(get_personality_compatibility(cat1,cat2))
    # self.assertIsNone(get_personality_compatibility(cat2,cat1))
    #
    # cat1.personality.trait = self.current_traits[3]
    # cat2.personality.trait = self.current_traits[5]
    # self.assertIsNone(get_personality_compatibility(cat1,cat2))
    # self.assertIsNone(get_personality_compatibility(cat2,cat1))
    #
    # cat1.personality.trait = self.current_traits[7]
    # cat2.personality.trait = self.current_traits[10]
    # self.assertIsNone(get_personality_compatibility(cat1,cat2))
    # self.assertIsNone(get_personality_compatibility(cat2,cat1))

    def test_some_positive_combinations(self):
        # TODO: the one who updated the personality should update the tests!!
        pass
        # cat1 = Cat()
        # cat2 = Cat()

    #
    # cat1.personality.trait = self.current_traits[1]
    # cat2.personality.trait = self.current_traits[18]
    # self.assertTrue(get_personality_compatibility(cat1,cat2))
    # self.assertTrue(get_personality_compatibility(cat2,cat1))
    #
    # cat1.personality.trait = self.current_traits[3]
    # cat2.personality.trait = self.current_traits[4]
    # self.assertTrue(get_personality_compatibility(cat1,cat2))
    # self.assertTrue(get_personality_compatibility(cat2,cat1))
    #
    # cat1.personality.trait = self.current_traits[5]
    # cat2.personality.trait = self.current_traits[17]
    # self.assertTrue(get_personality_compatibility(cat1,cat2))
    # self.assertTrue(get_personality_compatibility(cat2,cat1))

    def test_some_negative_combinations(self):
        # TODO: the one who updated the personality should update the tests!!
        pass
        # cat1 = Cat()
        # cat2 = Cat()

    #
    # cat1.personality.trait = self.current_traits[1]
    # cat2.personality.trait = self.current_traits[2]
    # self.assertFalse(get_personality_compatibility(cat1,cat2))
    # self.assertFalse(get_personality_compatibility(cat2,cat1))
    #
    # cat1.personality.trait = self.current_traits[3]
    # cat2.personality.trait = self.current_traits[6]
    # self.assertFalse(get_personality_compatibility(cat1,cat2))
    # self.assertFalse(get_personality_compatibility(cat2,cat1))
    #
    # cat1.personality.trait = self.current_traits[8]
    # cat2.personality.trait = self.current_traits[9]
    # self.assertFalse(get_personality_compatibility(cat1,cat2))
    # self.assertFalse(get_personality_compatibility(cat2,cat1))

    def test_false_trait(self):
        cat1 = Cat()
        cat2 = Cat()
        cat1.personality.trait = None
        cat2.personality.trait = None
        self.assertIsNone(get_personality_compatibility(cat1, cat2))
        self.assertIsNone(get_personality_compatibility(cat2, cat1))


class TestCountRelation(unittest.TestCase):
    def test_2_cats_jealousy(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat3 = Cat()
        cat4 = Cat()

        relation_1_2 = Relationship(cat_from=cat1, cat_to=cat2)
        relation_3_2 = Relationship(cat_from=cat3, cat_to=cat2)
        relation_4_2 = Relationship(cat_from=cat4, cat_to=cat2)
        cat1.relationships[cat2.ID] = relation_1_2
        cat3.relationships[cat2.ID] = relation_3_2
        cat4.relationships[cat2.ID] = relation_4_2
        relation_1_2.link_relationship()
        relation_3_2.link_relationship()
        relation_4_2.link_relationship()

        # when
        relation_1_2.respect -= 20
        relation_3_2.respect -= 20
        relation_4_2.respect -= 10

        # then
        relation_dict = get_num_of_cats_with_relation_amount_towards(
            cat2, -20, [cat1, cat2, cat3, cat4]
        )

        self.assertEqual(relation_dict["romance"], 0)
        self.assertEqual(relation_dict["like"], 0)
        self.assertEqual(relation_dict["respect"], 2)
        self.assertEqual(relation_dict["comfort"], 0)
        self.assertEqual(relation_dict["trust"], 0)


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
        relation_1_2 = Relationship(cat_from=cat1, cat_to=cat2, mates=True)
        relation_1_3 = Relationship(cat_from=cat1, cat_to=cat3)
        relation_1_4 = Relationship(cat_from=cat1, cat_to=cat4)
        relation_1_2.romance = 60
        relation_1_3.romance = 50
        relation_1_4.romance = 40

        relations = [relation_1_2, relation_1_3, relation_1_4]

        # then
        self.assertNotEqual(
            relation_1_2, get_highest_romantic_relation(relations, exclude_mate=True)
        )
        self.assertEqual(
            relation_1_3, get_highest_romantic_relation(relations, exclude_mate=True)
        )
        self.assertNotEqual(
            relation_1_4, get_highest_romantic_relation(relations, exclude_mate=True)
        )

    def test_include_mate(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat3 = Cat()
        cat4 = Cat()

        # when
        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        relation_1_2 = Relationship(cat_from=cat1, cat_to=cat2, mates=True)
        relation_1_3 = Relationship(cat_from=cat1, cat_to=cat3)
        relation_1_4 = Relationship(cat_from=cat1, cat_to=cat4)
        relation_1_2.romance = 60
        relation_1_3.romance = 50
        relation_1_4.romance = 40

        relations = [relation_1_2, relation_1_3, relation_1_4]

        # then
        self.assertEqual(
            relation_1_2, get_highest_romantic_relation(relations, exclude_mate=False)
        )
        self.assertNotEqual(
            relation_1_3, get_highest_romantic_relation(relations, exclude_mate=False)
        )
        self.assertNotEqual(
            relation_1_4, get_highest_romantic_relation(relations, exclude_mate=False)
        )


class TestGetQueens(unittest.TestCase):
    def setUp(self) -> None:
        self.test_cat1 = Cat(status_dict={"rank": CatRank.WARRIOR})
        self.test_cat2 = Cat(status_dict={"rank": CatRank.WARRIOR})
        self.test_cat3 = Cat(status_dict={"rank": CatRank.WARRIOR})
        self.test_cat4 = Cat(status_dict={"rank": CatRank.WARRIOR})
        self.test_cat5 = Cat(status_dict={"rank": CatRank.WARRIOR})
        self.test_cat6 = Cat(status_dict={"rank": CatRank.WARRIOR})

    def tearDown(self) -> None:
        del self.test_cat1
        del self.test_cat2
        del self.test_cat3
        del self.test_cat4
        del self.test_cat5
        del self.test_cat6

    def test_single_mother(self):
        # given
        # young enough kid
        self.test_cat1.gender = "female"

        self.test_cat2.status._change_rank(CatRank.KITTEN)
        self.test_cat2.parent1 = self.test_cat1.ID

        # too old kid
        self.test_cat3.gender = "female"

        self.test_cat4.status._change_rank(CatRank.APPRENTICE)
        self.test_cat4.parent1 = self.test_cat3.ID

        # then
        living_cats = [self.test_cat1, self.test_cat2, self.test_cat3, self.test_cat4]
        self.assertEqual(
            [self.test_cat1.ID], list(get_alive_clan_queens(living_cats)[0].keys())
        )

    def test_single_father(self):
        # given
        # young enough kid
        self.test_cat1.gender = "male"

        self.test_cat2.status._change_rank(CatRank.KITTEN)
        self.test_cat2.parent1 = self.test_cat1.ID

        # too old kid
        self.test_cat3.gender = "male"

        self.test_cat4.status._change_rank(CatRank.APPRENTICE)
        self.test_cat4.parent1 = self.test_cat3.ID

        # then
        living_cats = [self.test_cat1, self.test_cat2, self.test_cat3, self.test_cat4]
        self.assertEqual(
            [self.test_cat1.ID], list(get_alive_clan_queens(living_cats)[0].keys())
        )

    def tests_hetero_pair(self):
        # given
        # young enough kid
        self.test_cat1.gender = "female"

        self.test_cat2.gender = "male"

        self.test_cat3.status._change_rank(CatRank.KITTEN)
        self.test_cat3.parent1 = self.test_cat2.ID
        self.test_cat3.parent2 = self.test_cat1.ID

        # too old kid
        self.test_cat4.gender = "female"

        self.test_cat5.gender = "male"

        self.test_cat6.status._change_rank(CatRank.APPRENTICE)
        self.test_cat6.parent1 = self.test_cat5.ID
        self.test_cat6.parent2 = self.test_cat4.ID

        # then
        living_cats = [
            self.test_cat1,
            self.test_cat2,
            self.test_cat3,
            self.test_cat4,
            self.test_cat5,
            self.test_cat6,
        ]
        self.assertEqual(
            [self.test_cat1.ID], list(get_alive_clan_queens(living_cats)[0].keys())
        )

    def test_gay_pair(self):
        # given
        # young enough kid
        self.test_cat1.gender = "male"

        self.test_cat2.gender = "male"

        self.test_cat3.status._change_rank(CatRank.KITTEN)
        self.test_cat3.parent1 = self.test_cat2.ID
        self.test_cat3.parent2 = self.test_cat1.ID

        # too old kid
        self.test_cat4.gender = "male"

        self.test_cat5.gender = "male"

        self.test_cat6.status._change_rank(CatRank.APPRENTICE)
        self.test_cat6.parent1 = self.test_cat5.ID
        self.test_cat6.parent2 = self.test_cat4.ID

        # then
        living_cats = [
            self.test_cat1,
            self.test_cat2,
            self.test_cat3,
            self.test_cat4,
            self.test_cat5,
            self.test_cat6,
        ]
        self.assertTrue(
            [self.test_cat1.ID] == list(get_alive_clan_queens(living_cats)[0].keys())
            or [self.test_cat2.ID] == list(get_alive_clan_queens(living_cats)[0].keys())
        )

    def test_lesbian_pair(self):
        # given
        # young enough kid
        self.test_cat1.gender = "female"

        self.test_cat2.gender = "female"

        self.test_cat3.status._change_rank(CatRank.KITTEN)
        self.test_cat3.parent1 = self.test_cat2.ID
        self.test_cat3.parent2 = self.test_cat1.ID

        # too old kid
        self.test_cat4.gender = "female"

        self.test_cat5.gender = "female"

        self.test_cat6.status._change_rank(CatRank.APPRENTICE)
        self.test_cat6.parent1 = self.test_cat5.ID
        self.test_cat6.parent2 = self.test_cat4.ID

        # then
        living_cats = [
            self.test_cat1,
            self.test_cat2,
            self.test_cat3,
            self.test_cat4,
            self.test_cat5,
            self.test_cat6,
        ]
        self.assertTrue(
            [self.test_cat1.ID] == list(get_alive_clan_queens(living_cats)[0].keys())
            or [self.test_cat2.ID] == list(get_alive_clan_queens(living_cats)[0].keys())
        )

    def test_poly_pair(self):
        # given
        # young enough kid
        self.test_cat1.gender = "female"

        self.test_cat2.gender = "female"

        self.test_cat3.gender = "male"

        self.test_cat4.status._change_rank(CatRank.KITTEN)
        self.test_cat4.parent1 = self.test_cat2.ID
        self.test_cat4.parent2 = self.test_cat1.ID
        self.test_cat4.adoptive_parents.append(self.test_cat3.ID)

        # then
        living_cats = [
            self.test_cat1,
            self.test_cat2,
            self.test_cat3,
            self.test_cat4,
            self.test_cat5,
            self.test_cat6,
        ]
        self.assertEqual(
            [self.test_cat2.ID], list(get_alive_clan_queens(living_cats)[0].keys())
        )
