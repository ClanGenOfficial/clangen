import unittest

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.thoughts import resource_directory, get_med_thoughts, get_family_thoughts

try:
    import ujson
except ImportError:
    import json as ujson

from scripts.cat.cats import Cat

class TestsGetStatusThought(unittest.TestCase):

    def load_resources(self, status):
        base_path = f"resources/dicts/thoughts/"
        status = "warrior"
        life_dir = "alive"
        spec_dir = ""

        THOUGHTS = []
        with open(f"{base_path}{life_dir}{spec_dir}/{status}.json", 'r') as read_file:
            THOUGHTS = ujson.loads(read_file.read())
        GENTHOUGHTS = []
        with open(f"{base_path}{life_dir}{spec_dir}/general.json", 'r') as read_file:
            GENTHOUGHTS = ujson.loads(read_file.read())

        return [THOUGHTS,
                GENTHOUGHTS]

    def test_medicine_thought(self, status):
        status = "medicine cat"
        [THOUGHTS,
         GENTHOUGHTS] = self.load_resources()

        # given
        medicine = Cat()
        warrior = Cat()
        medicine.status = "medicine cat"
        warrior.status = "warrior"
        medicine.trait = "bold"

class TestFamilyThoughts(unittest.TestCase):
    def load_resources(self):
        base_path = f"resources/dicts/thoughts/"
        status = "warrior"
        life_dir = "alive"
        spec_dir = ""

        THOUGHTS = []
        with open(f"{base_path}{life_dir}{spec_dir}/{status}.json", 'r') as read_file:
            THOUGHTS = ujson.loads(read_file.read())
        GENTHOUGHTS = []
        with open(f"{base_path}{life_dir}{spec_dir}/general.json", 'r') as read_file:
            GENTHOUGHTS = ujson.loads(read_file.read())

        return [THOUGHTS,
                GENTHOUGHTS]

    def test_family_thought_young_children(self):
        # given
        FAMILY = self.load_resources()
        parent = Cat(moons=40)
        kit = Cat(parent1=parent.ID, moons=4)
        parent.children.append(kit.ID)

    
    def test_family_thought_unrelated(self):
        # given
        cat1 = Cat(moons=40)
        cat2 = Cat(moons=40)


