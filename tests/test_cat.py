import unittest
from scripts.cats import Cat


class TestCreationAge(unittest.TestCase):

    def test_kitten(self):
        test_cat = Cat(moons=5)
        self.assertEqual(test_cat.age,"kitten")

    def test_adolescent(self):
        test_cat = Cat(moons=6)
        self.assertEqual(test_cat.age,"adolescent")

    def test_young_adult(self):
        test_cat = Cat(moons=12)
        self.assertEqual(test_cat.age,"young adult")
    
    def test_adult(self):
        test_cat = Cat(moons=48)
        self.assertEqual(test_cat.age,"adult")

    def test_adult(self):
        test_cat = Cat(moons=96)
        self.assertEqual(test_cat.age,"senior adult")

    def test_elder(self):
        test_cat = Cat(moons=120)
        self.assertEqual(test_cat.age,"elder")