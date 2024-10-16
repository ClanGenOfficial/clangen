import os
import unittest

import ujson

from scripts.cat import enums
from scripts.cat.cats import Cat
from scripts.conditions import medical_cats_condition_fulfilled

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


class TestsMedCondition(unittest.TestCase):
    def test_fulfilled(self):
        cat1 = Cat(moons=20, status=enums.Status.WARRIOR)
        med = Cat(moons=20, status=enums.Status.MEDCAT)

        all_cats = [cat1, med]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 15))

    def test_fulfilled_many_cats(self):
        cat1 = Cat(moons=20, status=enums.Status.WARRIOR)
        cat2 = Cat(moons=20, status=enums.Status.WARRIOR)
        cat3 = Cat(moons=20, status=enums.Status.WARRIOR)
        cat4 = Cat(moons=20, status=enums.Status.WARRIOR)

        med1 = Cat(moons=20, status=enums.Status.MEDCAT)
        med2 = Cat(moons=20, status=enums.Status.MEDCAT)

        all_cats = [cat1, cat2, cat3, cat4, med1, med2]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 2))

    def test_injured_fulfilled(self):
        cat1 = Cat(moons=20, status=enums.Status.WARRIOR)

        med = Cat(moons=20, status=enums.Status.MEDCAT)
        med.injuries["small cut"] = {"severity": "minor"}

        all_cats = [cat1, med]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 15))

    def test_illness_fulfilled(self):
        cat1 = Cat(moons=20, status=enums.Status.WARRIOR)

        med = Cat(moons=20, status=enums.Status.MEDCAT)
        med.illnesses["running nose"] = {"severity": "minor"}

        all_cats = [cat1, med]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 15))


class TestsIllnesses(unittest.TestCase):
    @staticmethod
    def load_resources():
        resource_directory = "resources/dicts/conditions/"

        illnesses = None
        with open(f"{resource_directory}Illnesses.json", 'r') as read_file:
            illnesses = ujson.loads(read_file.read())
        return illnesses


class TestInjury(unittest.TestCase):
    @staticmethod
    def load_resources():
        resource_directory = "resources/dicts/conditions/"

        injuries = None
        with open(f"{resource_directory}Injuries.json", 'r') as read_file:
            injuries = ujson.loads(read_file.read())
        return injuries
    