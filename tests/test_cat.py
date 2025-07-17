import os
import unittest
from copy import deepcopy

from scripts.game_structure.game_essentials import game

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat.enums import CatAge, CatRank, CatGroup, CatSocial
from scripts.cat_relations.relationship import Relationship


class TestCreationAge(unittest.TestCase):
    # test that a cat with 1-5 moons has the age of a kitten
    def test_kitten(self):
        test_cat = Cat(moons=5)
        self.assertEqual(test_cat.age, CatAge.KITTEN)

    # test that a cat with 6-11 moons has the age of an adolescent
    def test_adolescent(self):
        test_cat = Cat(moons=6)
        self.assertEqual(test_cat.age, CatAge.ADOLESCENT)

    # test that a cat with 12-47 moons has the age of a young adult
    def test_young_adult(self):
        test_cat = Cat(moons=12)
        self.assertEqual(test_cat.age, CatAge.YOUNG_ADULT)

    # test that a cat with 48-95 moons has the age of an adult
    def test_adult(self):
        test_cat = Cat(moons=48)
        self.assertEqual(test_cat.age, CatAge.ADULT)

    # test that a cat with 96-119 moons has the age of a senior adult
    def test_senior_adult(self):
        test_cat = Cat(moons=96)
        self.assertEqual(test_cat.age, CatAge.SENIOR_ADULT)

    # test that a cat with 120-300 moons has the age of a senior
    def test_elder(self):
        test_cat = Cat(moons=120)
        self.assertEqual(test_cat.age, CatAge.SENIOR)


class TestRelativesFunction(unittest.TestCase):
    # test that is_parent returns True for a parent1-cat relationship and False otherwise
    def test_is_parent(self):
        parent = Cat()
        kit = Cat(parent1=parent.ID)
        self.assertFalse(kit.is_parent(kit))
        self.assertFalse(kit.is_parent(parent))
        self.assertTrue(parent.is_parent(kit))

    # test that is_sibling returns True for cats with a shared parent1 and False otherwise
    def test_is_sibling(self):
        parent = Cat()
        kit1 = Cat(parent1=parent.ID)
        kit2 = Cat(parent1=parent.ID)
        self.assertFalse(parent.is_sibling(kit1))
        self.assertFalse(kit1.is_sibling(parent))
        self.assertTrue(kit2.is_sibling(kit1))
        self.assertTrue(kit1.is_sibling(kit2))

    # test that is_uncle_aunt returns True for a uncle/aunt-cat relationship and False otherwise
    def test_is_uncle_aunt(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(sibling1.is_uncle_aunt(kit))
        self.assertFalse(sibling1.is_uncle_aunt(sibling2))
        self.assertFalse(kit.is_uncle_aunt(sibling2))
        self.assertTrue(sibling2.is_uncle_aunt(kit))

    # test that is_grandparent returns True for a grandparent-cat relationship and False otherwise
    def test_is_grandparent(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(sibling1.is_grandparent(kit))
        self.assertFalse(sibling1.is_grandparent(sibling2))
        self.assertFalse(kit.is_grandparent(sibling2))
        self.assertFalse(sibling2.is_grandparent(kit))
        self.assertFalse(kit.is_grandparent(grand_parent))
        self.assertTrue(grand_parent.is_grandparent(kit))


class TestPossibleMateFunction(unittest.TestCase):
    # test that is_potential_mate returns False for cats that are related to each other
    def test_relation(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(kit.is_potential_mate(grand_parent))
        self.assertFalse(kit.is_potential_mate(sibling1))
        self.assertFalse(kit.is_potential_mate(sibling2))
        self.assertFalse(kit.is_potential_mate(kit))
        self.assertFalse(sibling1.is_potential_mate(grand_parent))
        self.assertFalse(sibling1.is_potential_mate(sibling1))
        self.assertFalse(sibling1.is_potential_mate(sibling2))
        self.assertFalse(sibling1.is_potential_mate(kit))

    # test that is_potential_mate returns False for cats that are related to each other even if for_love_interest is True
    def test_relation_love_interest(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(kit.is_potential_mate(grand_parent, for_love_interest=True))
        self.assertFalse(kit.is_potential_mate(sibling1, for_love_interest=True))
        self.assertFalse(kit.is_potential_mate(sibling2, for_love_interest=True))
        self.assertFalse(kit.is_potential_mate(kit, for_love_interest=True))
        self.assertFalse(
            sibling1.is_potential_mate(grand_parent, for_love_interest=True)
        )
        self.assertFalse(sibling1.is_potential_mate(sibling1, for_love_interest=True))
        self.assertFalse(sibling1.is_potential_mate(sibling2, for_love_interest=True))
        self.assertFalse(sibling1.is_potential_mate(kit, for_love_interest=True))
        self.assertFalse(sibling2.is_potential_mate(sibling1, for_love_interest=True))

    # test is_potential_mate for age checks
    def test_age_mating(self):
        kitten_cat2 = Cat(moons=1)
        kitten_cat1 = Cat(moons=1)
        adolescent_cat1 = Cat(moons=6)
        adolescent_cat2 = Cat(moons=6)
        too_young_adult_cat1 = Cat(moons=12)
        too_young_adult_cat2 = Cat(moons=12)
        young_adult_cat1 = Cat(moons=20)
        young_adult_cat2 = Cat(moons=20)
        adult_cat_in_range1 = Cat(moons=60)
        adult_cat_in_range2 = Cat(moons=60)
        adult_cat_out_range1 = Cat(moons=65)
        adult_cat_out_range2 = Cat(moons=65)
        senior_adult_cat1 = Cat(moons=96)
        senior_adult_cat2 = Cat(moons=96)
        elder_cat1 = Cat(moons=120)
        elder_cat2 = Cat(moons=120)

        # check for cat mating with itself
        self.assertFalse(kitten_cat1.is_potential_mate(kitten_cat1))

        # check for setting
        self.assertFalse(
            senior_adult_cat1.is_potential_mate(
                young_adult_cat1, for_love_interest=False, age_restriction=True
            )
        )
        self.assertTrue(
            senior_adult_cat1.is_potential_mate(
                young_adult_cat1, for_love_interest=False, age_restriction=False
            )
        )

        # check invalid constellations
        self.assertFalse(kitten_cat1.is_potential_mate(kitten_cat2))
        self.assertFalse(kitten_cat1.is_potential_mate(adolescent_cat1))
        self.assertFalse(kitten_cat1.is_potential_mate(young_adult_cat1))
        self.assertFalse(kitten_cat1.is_potential_mate(adult_cat_in_range1))
        self.assertFalse(kitten_cat1.is_potential_mate(senior_adult_cat1))
        self.assertFalse(kitten_cat1.is_potential_mate(elder_cat1))

        self.assertFalse(adolescent_cat1.is_potential_mate(kitten_cat2))
        self.assertFalse(adolescent_cat1.is_potential_mate(adolescent_cat2))
        self.assertFalse(adolescent_cat1.is_potential_mate(too_young_adult_cat2))
        self.assertFalse(adolescent_cat1.is_potential_mate(young_adult_cat1))
        self.assertFalse(adolescent_cat1.is_potential_mate(adult_cat_in_range1))
        self.assertFalse(adolescent_cat1.is_potential_mate(senior_adult_cat1))
        self.assertFalse(adolescent_cat1.is_potential_mate(elder_cat1))

        self.assertFalse(too_young_adult_cat1.is_potential_mate(too_young_adult_cat2))

        self.assertFalse(young_adult_cat1.is_potential_mate(kitten_cat2))
        self.assertFalse(young_adult_cat1.is_potential_mate(adolescent_cat1))
        self.assertFalse(young_adult_cat1.is_potential_mate(adult_cat_out_range1))
        self.assertFalse(young_adult_cat1.is_potential_mate(senior_adult_cat1))
        self.assertFalse(young_adult_cat1.is_potential_mate(elder_cat1))

        self.assertFalse(adult_cat_out_range1.is_potential_mate(kitten_cat2))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(adolescent_cat1))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(young_adult_cat1))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(elder_cat1))

        self.assertFalse(senior_adult_cat1.is_potential_mate(kitten_cat1))
        self.assertFalse(senior_adult_cat1.is_potential_mate(adolescent_cat1))
        self.assertFalse(senior_adult_cat1.is_potential_mate(young_adult_cat1))

        # check valid constellations
        self.assertTrue(young_adult_cat1.is_potential_mate(young_adult_cat2))
        self.assertTrue(young_adult_cat1.is_potential_mate(adult_cat_in_range1))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(young_adult_cat1))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(adult_cat_in_range2))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(adult_cat_out_range1))
        self.assertTrue(adult_cat_out_range1.is_potential_mate(adult_cat_out_range2))
        self.assertTrue(adult_cat_out_range1.is_potential_mate(senior_adult_cat1))
        self.assertTrue(senior_adult_cat1.is_potential_mate(adult_cat_out_range1))
        self.assertTrue(senior_adult_cat1.is_potential_mate(senior_adult_cat2))
        self.assertTrue(senior_adult_cat1.is_potential_mate(elder_cat1))
        self.assertTrue(elder_cat1.is_potential_mate(senior_adult_cat1))
        self.assertTrue(elder_cat1.is_potential_mate(elder_cat2))

    # test is_potential_mate for age checks with for_love_interest set to True
    def test_age_love_interest(self):
        kitten_cat2 = Cat(moons=1)
        kitten_cat1 = Cat(moons=1)
        adolescent_cat1 = Cat(moons=6)
        adolescent_cat2 = Cat(moons=6)
        young_adult_cat1 = Cat(moons=12)
        young_adult_cat2 = Cat(moons=12)
        adult_cat_in_range1 = Cat(moons=52)
        adult_cat_in_range2 = Cat(moons=52)
        adult_cat_out_range1 = Cat(moons=65)
        adult_cat_out_range2 = Cat(moons=65)
        senior_adult_cat1 = Cat(moons=96)
        senior_adult_cat2 = Cat(moons=96)
        elder_cat1 = Cat(moons=120)
        elder_cat2 = Cat(moons=120)

        # check for cat mating with itself
        self.assertFalse(kitten_cat1.is_potential_mate(kitten_cat1, True))

        # check invalid constellations
        self.assertFalse(kitten_cat1.is_potential_mate(adolescent_cat1, True))
        self.assertFalse(kitten_cat1.is_potential_mate(young_adult_cat1, True))
        self.assertFalse(kitten_cat1.is_potential_mate(adult_cat_in_range1, True))
        self.assertFalse(kitten_cat1.is_potential_mate(senior_adult_cat1, True))
        self.assertFalse(kitten_cat1.is_potential_mate(elder_cat1, True))

        self.assertFalse(adolescent_cat1.is_potential_mate(kitten_cat2, True))
        self.assertFalse(adolescent_cat1.is_potential_mate(young_adult_cat1, True))
        self.assertFalse(adolescent_cat1.is_potential_mate(adult_cat_in_range1, True))
        self.assertFalse(adolescent_cat1.is_potential_mate(senior_adult_cat1, True))
        self.assertFalse(adolescent_cat1.is_potential_mate(elder_cat1, True))

        self.assertFalse(young_adult_cat1.is_potential_mate(kitten_cat2, True))
        self.assertFalse(young_adult_cat1.is_potential_mate(adolescent_cat1, True))
        self.assertFalse(young_adult_cat1.is_potential_mate(adult_cat_out_range1, True))
        self.assertFalse(young_adult_cat1.is_potential_mate(senior_adult_cat1, True))
        self.assertFalse(young_adult_cat1.is_potential_mate(elder_cat1, True))

        self.assertFalse(adult_cat_out_range1.is_potential_mate(kitten_cat2, True))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(adolescent_cat1, True))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(young_adult_cat1, True))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(elder_cat1, True))

        self.assertFalse(senior_adult_cat1.is_potential_mate(kitten_cat1, True))
        self.assertFalse(senior_adult_cat1.is_potential_mate(adolescent_cat1, True))
        self.assertFalse(senior_adult_cat1.is_potential_mate(young_adult_cat1, True))

        # check valid constellations
        self.assertTrue(kitten_cat1.is_potential_mate(kitten_cat2, True))
        self.assertTrue(adolescent_cat1.is_potential_mate(adolescent_cat2, True))
        self.assertTrue(young_adult_cat1.is_potential_mate(young_adult_cat2, True))
        self.assertTrue(young_adult_cat1.is_potential_mate(adult_cat_in_range1, True))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(young_adult_cat1, True))
        self.assertTrue(
            adult_cat_in_range1.is_potential_mate(adult_cat_in_range2, True)
        )
        self.assertTrue(
            adult_cat_in_range1.is_potential_mate(adult_cat_out_range1, True)
        )
        self.assertTrue(
            adult_cat_out_range1.is_potential_mate(adult_cat_out_range2, True)
        )
        self.assertTrue(adult_cat_out_range1.is_potential_mate(senior_adult_cat1, True))
        self.assertTrue(senior_adult_cat1.is_potential_mate(adult_cat_out_range1, True))
        self.assertTrue(senior_adult_cat1.is_potential_mate(senior_adult_cat2, True))
        self.assertTrue(senior_adult_cat1.is_potential_mate(elder_cat1, True))
        self.assertTrue(elder_cat1.is_potential_mate(senior_adult_cat1, True))
        self.assertTrue(elder_cat1.is_potential_mate(elder_cat2, True))

    # test that is_potential_mate returns False for exiled or dead cats
    def test_dead_exiled(self):
        exiled_cat = Cat()
        exiled_cat.status.exile_from_group()
        dead_cat = Cat()
        dead_cat.dead = True
        normal_cat = Cat()
        self.assertFalse(exiled_cat.is_potential_mate(normal_cat))
        self.assertFalse(normal_cat.is_potential_mate(exiled_cat))
        self.assertFalse(dead_cat.is_potential_mate(normal_cat))
        self.assertFalse(normal_cat.is_potential_mate(dead_cat))


class TestMateFunctions(unittest.TestCase):
    # test that set_mate adds the mate's ID to the cat's mate list
    def test_set_mate(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        # when
        cat1.set_mate(cat2)
        cat2.set_mate(cat1)

        # then
        self.assertEqual(cat1.mate[0], cat2.ID)
        self.assertEqual(cat2.mate[0], cat1.ID)

    # test that unset_mate removes the mate's ID from the cat's mate list
    def test_unset_mate(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)

        # when
        cat1.unset_mate(cat2)
        cat2.unset_mate(cat1)

        # then
        self.assertNotIn(cat2, cat1.mate)
        self.assertNotIn(cat1, cat2.mate)
        self.assertEqual(len(cat1.mate), 0)
        self.assertEqual(len(cat2.mate), 0)

    # test for relationship comparisons
    def test_set_mate_relationship(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        relation1 = Relationship(cat1, cat2)
        old_relation1 = deepcopy(relation1)
        relation2 = Relationship(cat2, cat1)
        old_relation2 = deepcopy(relation1)

        cat1.relationships[cat2.ID] = relation1
        cat2.relationships[cat1.ID] = relation2

        # when
        cat1.set_mate(cat2)
        cat2.set_mate(cat1)

        # then
        # TODO: maybe not correct check
        self.assertLess(old_relation1.romance, relation1.romance)
        self.assertLessEqual(old_relation1.like, relation1.like)
        self.assertLess(old_relation1.comfort, relation1.comfort)
        self.assertLess(old_relation1.trust, relation1.trust)
        self.assertLessEqual(old_relation1.respect, relation1.respect)

        self.assertLess(old_relation2.romance, relation2.romance)
        self.assertLessEqual(old_relation2.like, relation2.like)
        self.assertLess(old_relation2.comfort, relation2.comfort)
        self.assertLess(old_relation2.trust, relation2.trust)
        self.assertLessEqual(old_relation2.respect, relation2.respect)

    # test for relationship comparisons for cats that are broken up
    def test_unset_mate_relationship(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        relation1 = Relationship(
            cat1,
            cat2,
            family=False,
            mates=True,
            romance=40,
            like=40,
            comfort=40,
            trust=20,
            respect=20,
        )
        old_relation1 = deepcopy(relation1)
        relation2 = Relationship(
            cat2,
            cat1,
            family=False,
            mates=True,
            romance=40,
            like=40,
            comfort=40,
            trust=20,
            respect=20,
        )
        old_relation2 = deepcopy(relation2)
        cat1.mate.append(cat2.ID)
        cat2.mate.append(cat1.ID)
        cat1.relationships[cat2.ID] = relation1
        cat2.relationships[cat1.ID] = relation2

        # when
        cat1.unset_mate(cat2, breakup=True)
        cat2.unset_mate(cat2, breakup=True)

        # then
        # TODO: maybe not correct check
        self.assertGreater(old_relation1.romance, relation1.romance)
        self.assertGreaterEqual(old_relation1.like, relation1.like)
        self.assertGreater(old_relation1.comfort, relation1.comfort)
        self.assertGreater(old_relation1.trust, relation1.trust)
        self.assertGreaterEqual(old_relation1.respect, relation1.respect)

        self.assertGreater(old_relation2.romance, relation2.romance)
        self.assertGreaterEqual(old_relation2.like, relation2.like)
        self.assertGreater(old_relation2.comfort, relation2.comfort)
        self.assertGreater(old_relation2.trust, relation2.trust)
        self.assertGreaterEqual(old_relation2.respect, relation2.respect)


class TestUpdateMentor(unittest.TestCase):
    # test that an exiled cat apprentice becomes a former apprentice
    def test_exile_apprentice(self):
        # given

        app = Cat(moons=7, status_dict={"rank": CatRank.APPRENTICE})
        mentor = Cat(moons=20, status_dict={"rank": CatRank.WARRIOR})
        app.update_mentor(mentor.ID)

        # when
        self.assertTrue(app.ID in mentor.apprentice)
        self.assertFalse(app.ID in mentor.former_apprentices)
        self.assertEqual(app.mentor, mentor.ID)

        app.status.exile_from_group()
        app.update_mentor()

        # then
        self.assertFalse(app.ID in mentor.apprentice)
        self.assertTrue(app.ID in mentor.former_apprentices)
        self.assertIsNone(app.mentor)


class TestNameRepr(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        os.environ["SDL_AUDIODRIVER"] = "dummy"

    def test_clancats(self):
        """
        Test that basic clancats return the correct names
        :return:
        """
        statuses = [
            [[{"rank": CatRank.KITTEN}], 0, "kit"],
            [[{"rank": CatRank.KITTEN}], 1, "kit"],
            [
                [
                    {"rank": CatRank.APPRENTICE},
                    {"rank": CatRank.MEDICINE_APPRENTICE},
                    {"rank": CatRank.MEDIATOR_APPRENTICE},
                ],
                6,
                "paw",
            ],
            [
                [
                    {"rank": CatRank.WARRIOR},
                    {"rank": CatRank.MEDICINE_CAT},
                    {"rank": CatRank.MEDIATOR},
                    {"rank": CatRank.ELDER},
                    {"rank": CatRank.DEPUTY},
                ],
                14,
                "test",
            ],
            [[{"rank": CatRank.LEADER}], 14, "star"],
        ]
        for testset, moons, suffix in statuses:
            for status in testset:
                with self.subTest("clancats", status_dict=status):
                    cat = Cat(moons=moons, status_dict=status, suffix="test")
                    self.assertTrue(str(cat.name).endswith(suffix))

    def test_specsuffix_clancats(self):
        """
        Test that clancats with suppressed special suffixes return the correct names
        :return:
        """
        statuses = [
            [[{"rank": CatRank.NEWBORN}], 0, "test"],
            [[{"rank": CatRank.KITTEN}], 1, "test"],
            [
                [
                    {"rank": CatRank.APPRENTICE},
                    {"rank": CatRank.MEDICINE_APPRENTICE},
                    {"rank": CatRank.MEDIATOR_APPRENTICE},
                ],
                6,
                "test",
            ],
            [
                [
                    {"rank": CatRank.WARRIOR},
                    {"rank": CatRank.MEDICINE_CAT},
                    {"rank": CatRank.MEDIATOR},
                    {"rank": CatRank.ELDER},
                    {"rank": CatRank.DEPUTY},
                ],
                14,
                "test",
            ],
            [[{"rank": CatRank.LEADER}], 14, "test"],
        ]
        for testset, moons, suffix in statuses:
            for status in testset:
                with self.subTest("clancats specsuffix", status_dict=status):
                    cat = Cat(moons=moons, status_dict=status, suffix="test")
                    cat.name.specsuffix_hidden = True
                    self.assertTrue(str(cat.name).endswith(suffix))

    def test_outsiders(self):
        """
        Test that basic outsiders return the correct name
        :return:
        """
        outsider_statuses = [
            {"rank": CatRank.LONER},
            {"rank": CatRank.ROGUE},
            {"rank": CatRank.KITTYPET},
        ]

        age_suffix = [[0, "kit"], [1, "kit"], [6, "paw"], [14, "test"]]

        for status in outsider_statuses:
            for moons, suffix in age_suffix:
                with self.subTest("outsiders", status_dict=status, moons=moons):
                    cat = Cat(status_dict=status, moons=moons, suffix="test")
                    self.assertTrue(str(cat.name).endswith("test"))

        exiled_kit = {
            "group_history": [
                {
                    "group": CatGroup.PLAYER_CLAN,
                    "rank": CatRank.KITTEN,
                    "moons_as": 1,
                },
                {"group": None, "rank": CatRank.LONER, "moons_as": 20},
            ],
            "standing_history": [
                {"group": CatGroup.PLAYER_CLAN, "standing": ["member", "exiled"]}
            ],
        }
        exiled_app = {
            "group_history": [
                {
                    "group": CatGroup.PLAYER_CLAN,
                    "rank": CatRank.APPRENTICE,
                    "moons_as": 1,
                },
                {"group": None, "rank": CatRank.LONER, "moons_as": 20},
            ],
            "standing_history": [
                {"group": CatGroup.PLAYER_CLAN, "standing": ["member", "exiled"]}
            ],
        }
        exiled_warrior = {
            "group_history": [
                {"group": CatGroup.PLAYER_CLAN, "rank": CatRank.WARRIOR, "moons_as": 1},
                {"group": None, "rank": CatRank.LONER, "moons_as": 1},
            ],
            "standing_history": [
                {"group": CatGroup.PLAYER_CLAN, "standing": ["member", "exiled"]}
            ],
        }
        ex_clancat_statuses = [
            [exiled_kit, "kit"],
            [exiled_app, "paw"],
            [exiled_warrior, "test"],
        ]

        for status, suffix in ex_clancat_statuses:
            with self.subTest("Exiled cat names", status_dict=status, suffix=suffix):
                cat = Cat(status_dict=status, moons=20, suffix="test")
                self.assertTrue(str(cat.name).endswith(suffix))

    def test_specsuffix_outsiders(self):
        """
        Test that outsiders with hidden special suffixes return the correct name
        :return:
        """
        outsider_statuses = [
            {"rank": CatRank.LONER},
            {"rank": CatRank.ROGUE},
            {"rank": CatRank.KITTYPET},
        ]
        former_clancat_status = {
            "group_history": [
                {"group": CatGroup.OTHER_CLAN1, "rank": CatRank.WARRIOR, "moons_as": 1},
                {"group": None, "rank": CatRank.LONER, "moons_as": 1},
            ],
            "standing_history": [
                {"group": CatGroup.OTHER_CLAN1, "standing": ["member", "known"]}
            ],
        }
        exiled_status = {
            "group_history": [
                {"group": CatGroup.PLAYER_CLAN, "rank": CatRank.WARRIOR, "moons_as": 1},
                {"group": None, "rank": CatRank.LONER, "moons_as": 1},
            ],
            "standing_history": [
                {"group": CatGroup.PLAYER_CLAN, "standing": ["member", "exiled"]}
            ],
        }
        ex_clancat_statuses = [former_clancat_status, exiled_status]

        age_suffix = [[0, "kit"], [1, "kit"], [6, "paw"], [14, "test"]]

        for status in outsider_statuses:
            for moons, suffix in age_suffix:
                with self.subTest("outsiders", status_dict=status, moons=moons):
                    cat = Cat(status_dict=status, moons=moons, suffix="test")
                    cat.outside = True
                    cat.name.specsuffix_hidden = True
                    self.assertTrue(str(cat.name).endswith("test"))

        for status in ex_clancat_statuses:
            for moons, suffix in age_suffix:
                with self.subTest("Clan-like names", status_dict=status, moons=moons):
                    cat = Cat(status_dict=status, moons=moons, suffix="test")
                    cat.name.specsuffix_hidden = True
                    self.assertTrue(str(cat.name).endswith("test"))

    def test_lost(self):
        """
        Test that lost cats return the correct suffix
        :return:
        """
        statuses = [
            [{"rank": CatRank.NEWBORN}, 0, "kit"],
            [{"rank": CatRank.KITTEN}, 1, "kit"],
            [{"rank": CatRank.APPRENTICE}, 6, "paw"],
            [{"rank": CatRank.WARRIOR}, 14, "test"],
        ]
        for status, moons, suffix in statuses:
            with self.subTest("lost clancats", moons=moons):
                cat = Cat(status_dict=status, moons=moons, suffix="test")
                cat.become_lost()
                self.assertTrue(str(cat.name).endswith(suffix))

    def test_specsuffix_lost(self):
        """
        Test that lost cats with specsuffix return the correct suffix
        :return:
        """
        statuses = [
            [{"rank": CatRank.NEWBORN}, 0, "kit"],
            [{"rank": CatRank.KITTEN}, 1, "kit"],
            [{"rank": CatRank.APPRENTICE}, 6, "paw"],
            [{"rank": CatRank.WARRIOR}, 14, "test"],
        ]
        for status, moons, suffix in statuses:
            with self.subTest("lost clancats", status_dict=status):
                cat = Cat(status_dict=status, moons=moons, suffix="test")
                cat.status.become_lost()
                cat.name.specsuffix_hidden = True
                self.assertTrue(str(cat.name).endswith("test"))


class TestSocialAssignment(unittest.TestCase):
    def test_clancat_social(self):
        clancat_ranks = (
            CatRank.NEWBORN,
            CatRank.KITTEN,
            CatRank.APPRENTICE,
            CatRank.MEDIATOR_APPRENTICE,
            CatRank.MEDICINE_APPRENTICE,
            CatRank.MEDICINE_CAT,
            CatRank.MEDIATOR,
            CatRank.DEPUTY,
            CatRank.LEADER,
            CatRank.ELDER,
        )

        for rank in clancat_ranks:
            with self.subTest("clancat social assignment", rank=rank):
                cat = Cat(status_dict={"rank": rank})
                self.assertEqual(cat.status.social, CatSocial.CLANCAT)

    def test_outsider_social(self):
        outsider_ranks = (CatRank.LONER, CatRank.ROGUE, CatRank.KITTYPET)
        outsider_social = (CatSocial.LONER, CatSocial.ROGUE, CatSocial.KITTYPET)

        for rank, social in zip(outsider_ranks, outsider_social):
            with self.subTest("outsider social assignment"):
                cat = Cat(status_dict={"rank": rank})
                self.assertTrue(cat.status.social == social)
