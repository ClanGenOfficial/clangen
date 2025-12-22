import os
import unittest
import ujson

from scripts.cat.enums import CatRank

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.conditions import medicine_cats_can_cover_clan


class TestsMedCondition(unittest.TestCase):
    def test_fulfilled(self):
        cat1 = Cat(moons=20, status_dict={"rank": CatRank.WARRIOR}, disable_random=True)
        med = Cat(
            moons=20, status_dict={"rank": CatRank.MEDICINE_CAT}, disable_random=True
        )

        all_cats = [cat1, med]
        self.assertTrue(medicine_cats_can_cover_clan(all_cats, 15))

    def test_fulfilled_many_cats(self):
        cat1 = Cat(moons=20, status_dict={"rank": CatRank.WARRIOR}, disable_random=True)
        cat2 = Cat(moons=20, status_dict={"rank": CatRank.WARRIOR}, disable_random=True)
        cat3 = Cat(moons=20, status_dict={"rank": CatRank.WARRIOR}, disable_random=True)
        cat4 = Cat(moons=20, status_dict={"rank": CatRank.WARRIOR}, disable_random=True)

        med1 = Cat(
            moons=20, status_dict={"rank": CatRank.MEDICINE_CAT}, disable_random=True
        )
        med2 = Cat(
            moons=20, status_dict={"rank": CatRank.MEDICINE_CAT}, disable_random=True
        )

        all_cats = [cat1, cat2, cat3, cat4, med1, med2]
        self.assertTrue(medicine_cats_can_cover_clan(all_cats, 2))

    def test_injured_fulfilled(self):
        cat1 = Cat(moons=20, status_dict={"rank": CatRank.WARRIOR}, disable_random=True)

        med = Cat(
            moons=20, status_dict={"rank": CatRank.MEDICINE_CAT}, disable_random=True
        )
        med.injuries["small cut"] = {"severity": "minor"}

        all_cats = [cat1, med]
        self.assertTrue(medicine_cats_can_cover_clan(all_cats, 15))

    def test_illness_fulfilled(self):
        cat1 = Cat(moons=20, status_dict={"rank": CatRank.WARRIOR}, disable_random=True)

        med = Cat(
            moons=20, status_dict={"rank": CatRank.MEDICINE_CAT}, disable_random=True
        )
        med.illnesses["running nose"] = {"severity": "minor"}

        all_cats = [cat1, med]
        self.assertTrue(medicine_cats_can_cover_clan(all_cats, 15))


class TestsIllnesses(unittest.TestCase):
    def load_resources(self):
        resource_directory = "resources/dicts/conditions/"

        with open(f"{resource_directory}Illnesses.json", "r") as read_file:
            illnesses = ujson.loads(read_file.read())
        return illnesses


class TestInjury(unittest.TestCase):
    def load_resources(self):
        resource_directory = "resources/dicts/conditions/"

        with open(f"{resource_directory}Injuries.json", "r") as read_file:
            injuries = ujson.loads(read_file.read())
        return injuries
