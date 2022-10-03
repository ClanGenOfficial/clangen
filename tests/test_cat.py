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

class TestRelationFunction(unittest.TestCase):

    def test_parent(self):
        parent = Cat()
        kit = Cat(parent1=parent.ID)
        self.assertTrue(parent.is_parent(kit))

    def test_sibling(self):
        parent = Cat()
        kit1 = Cat(parent1=parent.ID)
        kit2 = Cat(parent1=parent.ID)
        self.assertTrue(kit1.is_sibling(kit2))

    def test_uncle_aunt(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertTrue(sibling2.is_uncle_aunt(kit))

class TestPossibleMateFunction(unittest.TestCase):

    def test_relation(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(kit.is_potential_mate(grand_parent))
        self.assertFalse(kit.is_potential_mate(sibling1))
        self.assertFalse(kit.is_potential_mate(sibling2))
        self.assertFalse(kit.is_potential_mate(kit))

    def test_age(self):
        adolescent_cat = Cat(moons=6)
        young_adult_cat = Cat(moons=20)
        adult_cat_in_range = Cat(moons=40)
        adult_cat_out_range = Cat(moons=65)

        # check invalid constellations
        self.assertFalse(adolescent_cat.is_potential_mate(young_adult_cat))
        self.assertFalse(young_adult_cat.is_potential_mate(adolescent_cat))
        self.assertFalse(young_adult_cat.is_potential_mate(adult_cat_out_range))
        self.assertFalse(adult_cat_out_range.is_potential_mate(young_adult_cat))

        # check valid constellations
        self.assertTrue(young_adult_cat.is_potential_mate(adult_cat_in_range))
        self.assertTrue(adult_cat_in_range.is_potential_mate(young_adult_cat))

    def test_dead_exiled(self):
        exiled_cat = Cat()
        exiled_cat.exiled = True
        dead_cat = Cat()
        dead_cat.dead = True
        normal_cat = Cat()
        self.assertFalse(exiled_cat.is_potential_mate(normal_cat))
        self.assertFalse(normal_cat.is_potential_mate(exiled_cat))
        self.assertFalse(dead_cat.is_potential_mate(normal_cat))
        self.assertFalse(normal_cat.is_potential_mate(dead_cat))