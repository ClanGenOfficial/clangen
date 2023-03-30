import unittest

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.thoughts import Thoughts

try:
    import ujson
except ImportError:
    import json as ujson

from scripts.cat.cats import Cat

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



class TestFamilyThoughts(unittest.TestCase):

    def test_family_thought_young_children(self):
        # given
        parent = Cat(moons=40)
        kit = Cat(parent1=parent.ID, moons=4)
        parent.children.append(kit.ID)
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

