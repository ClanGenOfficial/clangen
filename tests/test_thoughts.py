import unittest

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.thoughts import Thoughts

import ujson

from scripts.cat.cats import Cat

class TestNotWorkingThoughts(unittest.TestCase):
    def setUp(self):
        self.main = Cat(status="warrior")
        self.other = Cat(status="warrior")
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
        possible = [thought for thought in self.thoughts if
                    Thoughts.cats_fulfill_thought_constraints(
                        self.main,
                        self.other,
                        thought,
                        "expanded",
                        self.biome,
                        self.season,
                        self.camp)]

        return {thought["id"] for thought in possible}

    def test_not_working_thought_null(self):
        self.assertEqual({"test_not_working_false", "test_not_working_any"}, self.available_thought_ids())

    def test_not_working_thought_injury_minor(self):
        # given
        self.main.injuries["test-injury-1"] = {"severity": "minor"}

        # then
        self.assertEqual({"test_not_working_false", "test_not_working_any"}, self.available_thought_ids())

    def test_not_working_thought_injury_major(self):
        # given
        self.main.injuries["test-injury-1"] = {"severity": "major"}

        # then
        self.assertEqual({"test_not_working_any", "test_not_working_true"}, self.available_thought_ids())

    def test_not_working_thought_illness_minor(self):
        # given
        self.main.illnesses["test-illness-1"] = {"severity": "minor"}

        # then
        self.assertEqual({"test_not_working_false", "test_not_working_any"}, self.available_thought_ids())

    def test_not_working_thought_illness_major(self):
        # given
        self.main.illnesses["test-illness-1"] = {"severity": "major"}

        # then
        self.assertEqual({"test_not_working_any", "test_not_working_true"}, self.available_thought_ids())



class TestsGetStatusThought(unittest.TestCase):

    def test_medicine_thought(self):
        # given
        medicine = Cat()
        warrior = Cat()
        medicine.status = "medicine cat"
        warrior.status = "warrior"
        medicine.trait = "bold"
        biome = "Forest"
        season = "Newleaf"
        camp = "camp2"

        # load thoughts
        thoughts = Thoughts.load_thoughts(medicine, warrior, "expanded", biome, season, camp)

        # when
        function_thoughts = thoughts

    def test_exiled_thoughts(self):
        # given
        cat = Cat(status="exiled", moons=40)
        cat.exiled = True
        cat.outside = True
        biome = "Forest"
        season = "Newleaf"
        camp = "camp2"

        # load thoughts
        thoughts = Thoughts.load_thoughts(cat, None, "expanded", biome, season, camp)
        """Prints can be turned back on if testing is needed"""
        #print("Exiled Thoughts: " + str(thoughts))

    def test_lost_thoughts(self):
        # given
        cat = Cat(status="warrior", moons=40)
        cat.outside = True
        biome = "Forest"
        season = "Newleaf"
        camp = "camp2"

        # load thoughts
        thoughts = Thoughts.load_thoughts(cat, None, "expanded", biome, season, camp)
        """Prints can be turned back on if testing is needed"""
        #print("Lost Thoughts: " + str(thoughts))

class TestFamilyThoughts(unittest.TestCase):

    def test_family_thought_young_children(self):
        # given
        parent = Cat(moons=40)
        kit = Cat(parent1=parent.ID, moons=4)
        biome = "Forest"
        season = "Newleaf"
        camp = "camp2"

        # when
        function_thoughts1 = Thoughts.load_thoughts(parent, kit, "expanded", biome, season, camp)
        function_thoughts2 = Thoughts.load_thoughts(kit, parent, "expanded", biome, season, camp)

        # then
        '''
        self.assertTrue(all(t in own_collection_thoughts for t in function_thoughts1))
        self.assertFalse(all(t in not_collection_thoughts for t in function_thoughts1))
        self.assertEqual(function_thoughts2,[])
        '''
    
    def test_family_thought_unrelated(self):
        # given
        cat1 = Cat(moons=40)
        cat2 = Cat(moons=40)

        # when

        # then

