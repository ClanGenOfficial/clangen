import ujson
import unittest

from scripts.cat.cats import Cat
from scripts.cat.thoughts import *

class TestsGetStatusThought(unittest.TestCase):

    def load_resources(self):
        resource_directory = "resources/dicts/thoughts/"
        in_depth_path = "alive/"

        KITTEN_GENERAL = None
        with open(f"{resource_directory}{in_depth_path}kitten_to_other.json", 'r') as read_file:
            KITTEN_GENERAL = ujson.loads(read_file.read())

        APPR_GENERAL = None
        with open(f"{resource_directory}{in_depth_path}apprentice_to_other.json", 'r') as read_file:
            APPR_GENERAL = ujson.loads(read_file.read())

        MED_APPR_GENERAL = None
        with open(f"{resource_directory}{in_depth_path}medicine_app_to_other.json", 'r') as read_file:
            MED_APPR_GENERAL = ujson.loads(read_file.read())

        WARRIOR_GENERAL = None
        with open(f"{resource_directory}{in_depth_path}warrior_to_other.json", 'r') as read_file:
            WARRIOR_GENERAL = ujson.loads(read_file.read())

        MEDICINE_GENERAL = None
        with open(f"{resource_directory}{in_depth_path}medicine_to_other.json", 'r') as read_file:
            MEDICINE_GENERAL = ujson.loads(read_file.read())

        DEPUTY_GENERAL = None
        with open(f"{resource_directory}{in_depth_path}deputy_to_other.json", 'r') as read_file:
            DEPUTY_GENERAL = ujson.loads(read_file.read())

        LEADER_GENERAL = None
        with open(f"{resource_directory}{in_depth_path}leader_to_other.json", 'r') as read_file:
            LEADER_GENERAL = ujson.loads(read_file.read())

        ELDER_GENERAL = None
        with open(f"{resource_directory}{in_depth_path}elder_to_other.json", 'r') as read_file:
            ELDER_GENERAL = ujson.loads(read_file.read())

        return [KITTEN_GENERAL, 
            APPR_GENERAL,
            MED_APPR_GENERAL,
            WARRIOR_GENERAL,
            MEDICINE_GENERAL,
            DEPUTY_GENERAL,
            LEADER_GENERAL,
            ELDER_GENERAL]

    def test_medicine_thought(self):
        [KITTEN_GENERAL, 
            APPR_GENERAL,
            MED_APPR_GENERAL,
            WARRIOR_GENERAL,
            MEDICINE_GENERAL,
            DEPUTY_GENERAL,
            LEADER_GENERAL,
            ELDER_GENERAL] = self.load_resources()
        
        resource_directory = "resources/dicts/thoughts/"
        GENERAL_ALIVE = None
        with open(f"{resource_directory}cat_alive_general.json", 'r') as read_file:
            GENERAL_ALIVE = ujson.loads(read_file.read())
        MED_TRAIT = None
        with open(f"{resource_directory}traits/medicine.json", 'r') as read_file:
            MED_TRAIT = ujson.loads(read_file.read())
        # given
        medicine = Cat()
        warrior = Cat()
        medicine.status = "medicine cat"
        warrior.status = "warrior"
        medicine.trait = "bold"

        # when
        function_thoughts = get_med_thoughts(medicine, warrior)
        own_collection_thoughts = GENERAL_ALIVE
        own_collection_thoughts += MEDICINE_GENERAL["all"]
        own_collection_thoughts += MEDICINE_GENERAL["alive"]["all"]
        own_collection_thoughts += MEDICINE_GENERAL["alive"][warrior.status]
        own_collection_thoughts += MED_TRAIT[medicine.trait]

        # then
        self.assertTrue(all(t in own_collection_thoughts for t in function_thoughts))