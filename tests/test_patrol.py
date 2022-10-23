import unittest
import ujson

from scripts.cat.cats import Cat
from scripts.patrol import LEAF_FALL, Patrol

class TestPatrol(unittest.TestCase):

    def test_newleaf_patrol_generation(self):
        # given
        patrol = Patrol()

        NEWLEAF = None
        resource_directory = "resources/dicts/patrols/"
        with open(f"{resource_directory}newleaf.json", 'r') as read_file:
            NEWLEAF = ujson.loads(read_file.read())

        # then
        patrol_events = patrol.get_possible_patrols("Newleaf", "Forest", [])
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in NEWLEAF))

    def test_greenleaf_patrol_generation(self):
        # given
        patrol = Patrol()

        GREENLEAF = None
        resource_directory = "resources/dicts/patrols/"
        with open(f"{resource_directory}greenleaf.json", 'r') as read_file:
            GREENLEAF = ujson.loads(read_file.read())

        # then
        patrol_events = patrol.get_possible_patrols("Greenleaf", "Forest", [])
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in GREENLEAF))

    def test_leaffall_patrol_generation(self):
        # given
        patrol = Patrol()

        LEAF_FALL = None
        resource_directory = "resources/dicts/patrols/"
        with open(f"{resource_directory}leaf-fall.json", 'r') as read_file:
            LEAF_FALL = ujson.loads(read_file.read())

        # then
        patrol_events = patrol.get_possible_patrols("Leaf-fall", "Forest", [])
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in LEAF_FALL))

    def test_leafbare_patrol_generation(self):
        # given
        patrol = Patrol()

        LEAF_BARE = None
        resource_directory = "resources/dicts/patrols/"
        with open(f"{resource_directory}leaf-bare.json", 'r') as read_file:
            LEAF_BARE = ujson.loads(read_file.read())

        # then
        patrol_events = patrol.get_possible_patrols("Leaf-bare", "Forest", [])
        possibilities_id = [p.patrol_id for p in patrol_events]
        self.assertTrue(all(action["patrol_id"] in possibilities_id for action in LEAF_BARE))
