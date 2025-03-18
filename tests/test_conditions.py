import os
import unittest
import ujson

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.conditions import medical_cats_condition_fulfilled



class TestsMedCondition(unittest.TestCase):
    def test_fulfilled(self):
        cat1 = Cat(moons=20)
        cat1.status = "warrior"

        med = Cat(moons=20)
        med.status = "medicine cat"

        all_cats = [cat1, med]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 15))

    def test_fulfilled_many_cats(self):
        cat1 = Cat(moons=20)
        cat1.status = "warrior"
        cat2 = Cat(moons=20)
        cat2.status = "warrior"
        cat3 = Cat(moons=20)
        cat3.status = "warrior"
        cat4 = Cat(moons=20)
        cat4.status = "warrior"

        med1 = Cat(moons=20)
        med1.status = "medicine cat"
        med2 = Cat(moons=20)
        med2.status = "medicine cat"

        all_cats = [cat1, cat2, cat3, cat4, med1, med2]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 2))

    def test_injured_fulfilled(self):
        cat1 = Cat(moons=20)
        cat1.status = "warrior"

        med = Cat(moons=20)
        med.status = "medicine cat"
        med.injuries["small cut"] = {"severity": "minor"}

        all_cats = [cat1, med]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 15))

    def test_illness_fulfilled(self):
        cat1 = Cat(moons=20)
        cat1.status = "warrior"

        med = Cat(moons=20)
        med.status = "medicine cat"
        med.illnesses["running nose"] = {"severity": "minor"}

        all_cats = [cat1, med]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 15))


class TestsIllnesses(unittest.TestCase):
    def load_resources(self):
        resource_directory = "resources/dicts/conditions/"

        illnesses = None
        with open(f"{resource_directory}Illnesses.json", 'r') as read_file:
            illnesses = ujson.loads(read_file.read())
        return illnesses


class TestInjury(unittest.TestCase):
    def load_resources(self):
        resource_directory = "resources/dicts/conditions/"

        injuries = None
        with open(f"{resource_directory}Injuries.json", 'r') as read_file:
            injuries = ujson.loads(read_file.read())
        return injuries
    