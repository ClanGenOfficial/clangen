import unittest

try:
    import ujson
except ImportError:
    import json as ujson

from scripts.patrol import Patrol
from scripts.cat.cats import Cat

class TestLeafPatrols(unittest.TestCase):

    def load_resources(self):
        resource_directory = "resources/dicts/patrols/leaves/"

        NEWLEAF = None
        with open(f"{resource_directory}newleaf.json", 'r') as read_file:
            NEWLEAF = ujson.loads(read_file.read())
        
        GREENLEAF = None
        with open(f"{resource_directory}greenleaf.json", 'r') as read_file:
            GREENLEAF = ujson.loads(read_file.read())
        
        LEAF_FALL = None
        with open(f"{resource_directory}leaf-fall.json", 'r') as read_file:
            LEAF_FALL = ujson.loads(read_file.read())

        LEAF_BARE = None
        with open(f"{resource_directory}leaf-bare.json", 'r') as read_file:
            LEAF_BARE = ujson.loads(read_file.read())
        
        return [NEWLEAF,GREENLEAF,LEAF_FALL,LEAF_BARE]

    def test_newleaf_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        NEWLEAF,GREENLEAF,LEAF_FALL,LEAF_BARE = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Newleaf", "Forest", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in NEWLEAF))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in GREENLEAF))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in LEAF_FALL))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in LEAF_BARE))

    def test_greenleaf_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        NEWLEAF,GREENLEAF,LEAF_FALL,LEAF_BARE = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Greenleaf", "Forest", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in NEWLEAF))
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in GREENLEAF))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in LEAF_FALL))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in LEAF_BARE))

    def test_leaffall_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        NEWLEAF,GREENLEAF,LEAF_FALL,LEAF_BARE = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Leaf-fall", "Forest", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in NEWLEAF))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in GREENLEAF))
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in LEAF_FALL))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in LEAF_BARE))

    def test_leafbare_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        NEWLEAF,GREENLEAF,LEAF_FALL,LEAF_BARE = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Leaf-bare", "Forest", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in NEWLEAF))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in GREENLEAF))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in LEAF_FALL))
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in LEAF_BARE))


class TestBiomePatrols(unittest.TestCase):

    def load_resources(self):
        resource_directory = "resources/dicts/patrols/biomes/"
        FOREST = None
        with open(f"{resource_directory}forest.json", 'r') as read_file:
            FOREST = ujson.loads(read_file.read())

        PLAINS = None
        with open(f"{resource_directory}plains.json", 'r') as read_file:
            PLAINS = ujson.loads(read_file.read())

        MOUNTAINOUS = None
        with open(f"{resource_directory}mountainous.json", 'r') as read_file:
            MOUNTAINOUS = ujson.loads(read_file.read())

        SWAMP = None
        with open(f"{resource_directory}swamp.json", 'r') as read_file:
            SWAMP = ujson.loads(read_file.read())

        BEACH = None
        with open(f"{resource_directory}beach.json", 'r') as read_file:
            BEACH = ujson.loads(read_file.read())

        return [FOREST,PLAINS,MOUNTAINOUS,SWAMP,BEACH]

    def test_forest_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        FOREST,PLAINS,MOUNTAINOUS,SWAMP,BEACH = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Newleaf", "Forest", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in FOREST))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in PLAINS))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in MOUNTAINOUS))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in SWAMP))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in BEACH))

    def test_plains_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        FOREST,PLAINS,MOUNTAINOUS,SWAMP,BEACH = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Newleaf", "Plains", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in FOREST))
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in PLAINS))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in MOUNTAINOUS))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in SWAMP))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in BEACH))

    def test_mountainous_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        FOREST,PLAINS,MOUNTAINOUS,SWAMP,BEACH = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Newleaf", "Mountainous", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in FOREST))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in PLAINS))
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in MOUNTAINOUS))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in SWAMP))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in BEACH))

    def test_swamp_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        FOREST,PLAINS,MOUNTAINOUS,SWAMP,BEACH = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Newleaf", "Swamp", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in FOREST))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in PLAINS))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in MOUNTAINOUS))
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in SWAMP))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in BEACH))

    def test_beach_patrol_generation(self):
        # given
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        FOREST,PLAINS,MOUNTAINOUS,SWAMP,BEACH = self.load_resources()

        # then
        patrol_events = patrol.get_possible_patrols("Newleaf", "Beach", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in FOREST))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in PLAINS))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in MOUNTAINOUS))
        self.assertFalse(all(action["patrol_id"] in possibilities_id for action in SWAMP))
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in BEACH))

class TestSpecificPatrols(unittest.TestCase):
    def test_disaster(self):
        # given
        disaster_patrol_ids = [900,901,902]
        patrol = Patrol()
        random_cat = Cat()
        patrol.patrol_random_cat = random_cat

        # when
        patrol_events = patrol.get_possible_patrols("Newleaf", "Forest", [], True)
        possibilities_id = [p.patrol_id for p in patrol_events]

        # then
        self.assertTrue(all(id in possibilities_id for id in disaster_patrol_ids))
        

class TestCatAmount(unittest.TestCase):

    def test_apprentice_warrior(self):
        # given
        warrior_apprentice_patrol_ids = [150,116]
        patrol = Patrol()
        warrior = Cat(moons=20, status="warrior")
        apprentice = Cat(moons=8, status="apprentice")

        # when
        patrol.add_cat(warrior)
        patrol.add_cat(apprentice)
        patrol.patrol_random_cat = apprentice
        patrol.patrol_leader = warrior
        patrol_events = patrol.get_possible_patrols("Newleaf", "Beach", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]

        # then
        self.assertTrue(all(id in possibilities_id for id in warrior_apprentice_patrol_ids))

    def test_two_warriors(self):
        # given
        warrior_apprentice_patrol_ids = [150,116]
        single_cat_patrol_ids = [400,401,402]
        patrol = Patrol()
        warrior1 = Cat(moons=20, status="warrior")
        warrior2 = Cat(moons=8, status="warrior")

        # when
        patrol.add_cat(warrior1)
        patrol.add_cat(warrior2)
        patrol.patrol_random_cat = warrior2
        patrol.patrol_leader = warrior1
        patrol_events = patrol.get_possible_patrols("Newleaf", "Beach", [], False)
        possibilities_id = [p.patrol_id for p in patrol_events]

        # then
        self.assertFalse(all(id in possibilities_id for id in warrior_apprentice_patrol_ids))
        self.assertFalse(all(id in possibilities_id for id in single_cat_patrol_ids))
