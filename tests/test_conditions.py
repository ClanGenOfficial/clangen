import ujson
import unittest
from mock import patch

from scripts.cat.cats import Cat
from scripts.conditions import Illness, Injury, medical_cats_condition_fulfilled

class TestsMedCondition(unittest.TestCase):
    def test_medicine_condition_not_fulfilled(self):
        cat1 = Cat(moons=20)
        cat1.status = "warrior"
        cat2 = Cat(moons=20)
        cat2.status = "warrior"

        all_cats = [cat1, cat2]
        self.assertFalse(medical_cats_condition_fulfilled(all_cats, 15))


    def test_medicine_condition_fulfilled(self):
        cat1 = Cat(moons=20)
        cat1.status = "warrior"

        med = Cat(moons=20)
        med.status = "medicine cat"

        all_cats = [cat1, med]
        self.assertTrue(medical_cats_condition_fulfilled(all_cats, 15))

    def test_medicine_condition_fulfilled_many_cats(self):
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

    def test_medicine_condition_not_fulfilled_many_cats(self):
        cat1 = Cat(moons=20)
        cat1.status = "warrior"
        cat2 = Cat(moons=20)
        cat2.status = "warrior"
        cat3 = Cat(moons=20)
        cat3.status = "warrior"
        cat4 = Cat(moons=20)
        cat4.status = "warrior"

        med = Cat(moons=20)
        med.status = "medicine cat"

        all_cats = [cat1, cat2, cat3, cat4, med]
        self.assertFalse(medical_cats_condition_fulfilled(all_cats, 2))

class TestsIllnesses(unittest.TestCase):
    def load_resources(self):
        resource_directory = "resources/dicts/conditions/"

        ILLNESSES = None
        with open(f"{resource_directory}Illnesses.json", 'r') as read_file:
            ILLNESSES = ujson.loads(read_file.read())
        return ILLNESSES

    def test_get_ill_unknown_name(self):
        cat = Cat()
        no_name = "NotExisting"

        try:
            cat.get_ill(no_name)
        except BaseException as exc:
            assert False, f"Unknown illness name raises an exception: {exc}"


class TestInjury(unittest.TestCase):
    def load_resources(self):
        resource_directory = "resources/dicts/conditions/"

        INJURIES = None
        with open(f"{resource_directory}Injuries.json", 'r') as read_file:
            INJURIES = ujson.loads(read_file.read())
        return INJURIES
    
    def test_get_injured_unknown_name(self):
        cat = Cat()
        no_name = "NotExisting"

        try:
            cat.get_injured(no_name)
        except BaseException as exc:
            assert False, f"Unknown injury name raises an exception: {exc}"