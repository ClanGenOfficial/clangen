import os
import unittest

from scripts.cat.enums import CatRank, CatGroup

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat.thoughts import Thoughts


class TestNotWorkingThoughts(unittest.TestCase):
    def setUp(self):
        self.main = Cat(status_dict={"rank": CatRank.WARRIOR}, disable_random=True)
        self.other = Cat(status_dict={"rank": CatRank.WARRIOR}, disable_random=True)
        self.biome = "Forest"
        self.season = "Newleaf"
        self.camp = "camp2"

        self.thoughts = [
            {"id": "test_not_working_true", "thoughts": [], "not_working": True},
            {"id": "test_not_working_false", "thoughts": [], "not_working": False},
            {"id": "test_not_working_any", "thoughts": []},
        ]

    def available_thought_ids(self):
        """Return a list of id's for available thoughts"""
        possible = [
            thought
            for thought in self.thoughts
            if Thoughts.cats_fulfill_thought_constraints(
                self.main,
                self.other,
                thought,
                "expanded",
                self.biome,
                self.season,
                self.camp,
            )
        ]

        return {thought["id"] for thought in possible}

    def test_not_working_thought_null(self):
        self.assertEqual(
            {"test_not_working_false", "test_not_working_any"},
            self.available_thought_ids(),
        )

    def test_not_working_thought_injury_minor(self):
        # given
        self.main.injuries["test-injury-1"] = {"severity": "minor"}

        # then
        self.assertEqual(
            {"test_not_working_false", "test_not_working_any"},
            self.available_thought_ids(),
        )

    def test_not_working_thought_injury_major(self):
        # given
        self.main.injuries["test-injury-1"] = {"severity": "major"}

        # then
        self.assertEqual(
            {"test_not_working_any", "test_not_working_true"},
            self.available_thought_ids(),
        )

    def test_not_working_thought_illness_minor(self):
        # given
        self.main.illnesses["test-illness-1"] = {"severity": "minor"}

        # then
        self.assertEqual(
            {"test_not_working_false", "test_not_working_any"},
            self.available_thought_ids(),
        )

    def test_not_working_thought_illness_major(self):
        # given
        self.main.illnesses["test-illness-1"] = {"severity": "major"}

        # then
        self.assertEqual(
            {"test_not_working_any", "test_not_working_true"},
            self.available_thought_ids(),
        )


class TestsGetStatusThought(unittest.TestCase):
    def test_medicine_thought(self):
        # given
        medicine = Cat(status_dict={"rank": CatRank.MEDICINE_CAT})
        warrior = Cat(status_dict={"rank": CatRank.WARRIOR})
        medicine.trait = "bold"
        biome = "Forest"
        season = "Newleaf"
        camp = "camp2"

        # load thoughts
        thoughts = Thoughts.load_thoughts(
            medicine, warrior, "expanded", biome, season, camp
        )

        # when
        function_thoughts = thoughts

    def test_exiled_thoughts(self):
        # given
        exiled_status = {
            "group_history": [
                {"group": CatGroup.PLAYER_CLAN, "rank": CatRank.WARRIOR, "moons_as": 1},
                {"group": None, "rank": CatRank.LONER, "moons_as": 1},
            ],
            "standing_history": [
                {"group": CatGroup.PLAYER_CLAN, "standing": ["member", "exiled"]}
            ],
        }
        cat = Cat(status_dict=exiled_status, moons=40, disable_random=True)
        biome = "Forest"
        season = "Newleaf"
        camp = "camp2"

        # load thoughts
        thoughts = Thoughts.load_thoughts(cat, None, "expanded", biome, season, camp)

    def test_lost_thoughts(self):
        # given
        cat = Cat(status_dict={"rank": CatRank.WARRIOR}, moons=40, disable_random=True)
        cat.status.become_lost()
        biome = "Forest"
        season = "Newleaf"
        camp = "camp2"

        # load thoughts
        thoughts = Thoughts.load_thoughts(cat, None, "expanded", biome, season, camp)


class TestFamilyThoughts(unittest.TestCase):
    def test_family_thought_young_children(self):
        # given
        parent = Cat(moons=40, disable_random=True)
        kit = Cat(parent1=parent.ID, moons=4, disable_random=True)
        biome = "Forest"
        season = "Newleaf"
        camp = "camp2"

        # when
        function_thoughts1 = Thoughts.load_thoughts(
            parent, kit, "expanded", biome, season, camp
        )
        function_thoughts2 = Thoughts.load_thoughts(
            kit, parent, "expanded", biome, season, camp
        )

        # then
        """
        self.assertTrue(all(t in own_collection_thoughts for t in function_thoughts1))
        self.assertFalse(all(t in not_collection_thoughts for t in function_thoughts1))
        self.assertEqual(function_thoughts2,[])
        """

    def test_family_thought_unrelated(self):
        # given
        cat1 = Cat(moons=40, disable_random=True)
        cat2 = Cat(moons=40, disable_random=True)

        # when

        # then
