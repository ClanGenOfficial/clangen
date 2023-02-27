from copy import deepcopy
import unittest

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship


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

    def test_senior_adult(self):
        test_cat = Cat(moons=96)
        self.assertEqual(test_cat.age,"senior adult")

    def test_elder(self):
        test_cat = Cat(moons=120)
        self.assertEqual(test_cat.age,"elder")

class TestRelativesFunction(unittest.TestCase):

    def test_is_parent(self):
        parent = Cat()
        kit = Cat(parent1=parent.ID)
        self.assertFalse(kit.is_parent(kit))
        self.assertFalse(kit.is_parent(parent))
        self.assertTrue(parent.is_parent(kit))

    def test_is_sibling(self):
        parent = Cat()
        kit1 = Cat(parent1=parent.ID)
        kit2 = Cat(parent1=parent.ID)
        self.assertFalse(parent.is_sibling(kit1))
        self.assertFalse(kit1.is_sibling(parent))
        # Cats don't need to be their own siblings, do they?
        #self.assertTrue(kit1.is_sibling(kit1))
        self.assertTrue(kit2.is_sibling(kit1))
        self.assertTrue(kit1.is_sibling(kit2))

    def test_is_uncle_aunt(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        sibling1.siblings.append(sibling2.ID)
        sibling2.siblings.append(sibling1.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(sibling1.is_uncle_aunt(kit))
        self.assertFalse(sibling1.is_uncle_aunt(sibling2))
        self.assertFalse(kit.is_uncle_aunt(sibling2))
        self.assertTrue(sibling2.is_uncle_aunt(kit))

    def test_is_grandparent(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        sibling1.siblings.append(sibling2.ID)
        sibling2.siblings.append(sibling1.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(sibling1.is_grandparent(kit))
        #self.assertFalse(sibling1.is_grandparent(sibling2))
        #self.assertFalse(kit.is_grandparent(sibling2))
        #self.assertFalse(sibling2.is_grandparent(kit))
        #self.assertFalse(kit.is_grandparent(grand_parent))
        #self.assertTrue(grand_parent.is_grandparent(kit))

class TestPossibleMateFunction(unittest.TestCase):

    def test_relation(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        sibling1.siblings.append(sibling2.ID)
        sibling2.siblings.append(sibling1.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(kit.is_potential_mate(grand_parent))
        self.assertFalse(kit.is_potential_mate(sibling1))
        self.assertFalse(kit.is_potential_mate(sibling2))
        self.assertFalse(kit.is_potential_mate(kit))
        self.assertFalse(sibling1.is_potential_mate(grand_parent))
        self.assertFalse(sibling1.is_potential_mate(sibling1))
        self.assertFalse(sibling1.is_potential_mate(sibling2))
        self.assertFalse(sibling1.is_potential_mate(kit))

    def test_relation_love_interest(self):
        grand_parent = Cat()
        sibling1 = Cat(parent1=grand_parent.ID)
        sibling2 = Cat(parent1=grand_parent.ID)
        sibling1.siblings.append(sibling2.ID)
        sibling2.siblings.append(sibling1.ID)
        kit = Cat(parent1=sibling1.ID)
        self.assertFalse(kit.is_potential_mate(grand_parent,for_love_interest = True))
        self.assertFalse(kit.is_potential_mate(sibling1,for_love_interest = True))
        self.assertFalse(kit.is_potential_mate(sibling2,for_love_interest = True))
        self.assertFalse(kit.is_potential_mate(kit,for_love_interest = True))
        self.assertFalse(sibling1.is_potential_mate(grand_parent,for_love_interest = True))
        self.assertFalse(sibling1.is_potential_mate(sibling1,for_love_interest = True))
        self.assertFalse(sibling1.is_potential_mate(sibling2,for_love_interest = True))
        self.assertFalse(sibling1.is_potential_mate(kit,for_love_interest = True))
        self.assertFalse(sibling2.is_potential_mate(sibling1,for_love_interest = True))

    def test_age_mating(self):
        kitten_cat2 = Cat(moons=1)
        kitten_cat1 = Cat(moons=1)
        adolescent_cat1 = Cat(moons=6)
        adolescent_cat2 = Cat(moons=6)
        too_young_adult_cat1 = Cat(moons=12)
        too_young_adult_cat2 = Cat(moons=12)
        young_adult_cat1 = Cat(moons=20)
        young_adult_cat2 = Cat(moons=20)
        adult_cat_in_range1 = Cat(moons=60)
        adult_cat_in_range2 = Cat(moons=60)
        adult_cat_out_range1 = Cat(moons=65)
        adult_cat_out_range2 = Cat(moons=65)
        senior_adult_cat1 = Cat(moons=96)
        senior_adult_cat2 = Cat(moons=96)
        elder_cat1 = Cat(moons=120)
        elder_cat2 = Cat(moons=120)

        self.assertFalse(kitten_cat1.is_potential_mate(kitten_cat1))

        # check invalid constellations
        self.assertFalse(kitten_cat1.is_potential_mate(kitten_cat2))
        self.assertFalse(kitten_cat1.is_potential_mate(adolescent_cat1))
        self.assertFalse(kitten_cat1.is_potential_mate(young_adult_cat1))
        self.assertFalse(kitten_cat1.is_potential_mate(adult_cat_in_range1))
        self.assertFalse(kitten_cat1.is_potential_mate(senior_adult_cat1))
        self.assertFalse(kitten_cat1.is_potential_mate(elder_cat1))

        self.assertFalse(adolescent_cat1.is_potential_mate(kitten_cat2))
        self.assertFalse(adolescent_cat1.is_potential_mate(adolescent_cat2))
        self.assertFalse(adolescent_cat1.is_potential_mate(too_young_adult_cat2))
        self.assertFalse(adolescent_cat1.is_potential_mate(young_adult_cat1))
        self.assertFalse(adolescent_cat1.is_potential_mate(adult_cat_in_range1))
        self.assertFalse(adolescent_cat1.is_potential_mate(senior_adult_cat1))
        self.assertFalse(adolescent_cat1.is_potential_mate(elder_cat1))

        self.assertFalse(too_young_adult_cat1.is_potential_mate(too_young_adult_cat2))

        self.assertFalse(young_adult_cat1.is_potential_mate(kitten_cat2))
        self.assertFalse(young_adult_cat1.is_potential_mate(adolescent_cat1))
        self.assertFalse(young_adult_cat1.is_potential_mate(adult_cat_out_range1))
        self.assertFalse(young_adult_cat1.is_potential_mate(senior_adult_cat1))
        self.assertFalse(young_adult_cat1.is_potential_mate(elder_cat1))

        self.assertFalse(adult_cat_out_range1.is_potential_mate(kitten_cat2))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(adolescent_cat1))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(young_adult_cat1))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(elder_cat1))

        self.assertFalse(senior_adult_cat1.is_potential_mate(kitten_cat1))
        self.assertFalse(senior_adult_cat1.is_potential_mate(adolescent_cat1))
        self.assertFalse(senior_adult_cat1.is_potential_mate(young_adult_cat1))

        # check valid constellations
        self.assertTrue(young_adult_cat1.is_potential_mate(young_adult_cat2))
        self.assertTrue(young_adult_cat1.is_potential_mate(adult_cat_in_range1))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(young_adult_cat1))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(adult_cat_in_range2))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(adult_cat_out_range1))
        self.assertTrue(adult_cat_out_range1.is_potential_mate(adult_cat_out_range2))
        self.assertTrue(adult_cat_out_range1.is_potential_mate(senior_adult_cat1))
        self.assertTrue(senior_adult_cat1.is_potential_mate(adult_cat_out_range1))
        self.assertTrue(senior_adult_cat1.is_potential_mate(senior_adult_cat2))
        self.assertTrue(senior_adult_cat1.is_potential_mate(elder_cat1))
        self.assertTrue(elder_cat1.is_potential_mate(senior_adult_cat1))
        self.assertTrue(elder_cat1.is_potential_mate(elder_cat2))

    def test_age_love_interest(self):
        kitten_cat2 = Cat(moons=1)
        kitten_cat1 = Cat(moons=1)
        adolescent_cat1 = Cat(moons=6)
        adolescent_cat2 = Cat(moons=6)
        young_adult_cat1 = Cat(moons=12)
        young_adult_cat2 = Cat(moons=12)
        adult_cat_in_range1 = Cat(moons=52)
        adult_cat_in_range2 = Cat(moons=52)
        adult_cat_out_range1 = Cat(moons=65)
        adult_cat_out_range2 = Cat(moons=65)
        senior_adult_cat1 = Cat(moons=96)
        senior_adult_cat2 = Cat(moons=96)
        elder_cat1 = Cat(moons=120)
        elder_cat2 = Cat(moons=120)

        self.assertFalse(kitten_cat1.is_potential_mate(kitten_cat1,True))

        # check invalid constellations
        self.assertFalse(kitten_cat1.is_potential_mate(adolescent_cat1,True))
        self.assertFalse(kitten_cat1.is_potential_mate(young_adult_cat1,True))
        self.assertFalse(kitten_cat1.is_potential_mate(adult_cat_in_range1,True))
        self.assertFalse(kitten_cat1.is_potential_mate(senior_adult_cat1,True))
        self.assertFalse(kitten_cat1.is_potential_mate(elder_cat1,True))

        self.assertFalse(adolescent_cat1.is_potential_mate(kitten_cat2,True))
        self.assertFalse(adolescent_cat1.is_potential_mate(young_adult_cat1,True))
        self.assertFalse(adolescent_cat1.is_potential_mate(adult_cat_in_range1,True))
        self.assertFalse(adolescent_cat1.is_potential_mate(senior_adult_cat1,True))
        self.assertFalse(adolescent_cat1.is_potential_mate(elder_cat1,True))

        self.assertFalse(young_adult_cat1.is_potential_mate(kitten_cat2,True))
        self.assertFalse(young_adult_cat1.is_potential_mate(adolescent_cat1,True))
        self.assertFalse(young_adult_cat1.is_potential_mate(adult_cat_out_range1,True))
        self.assertFalse(young_adult_cat1.is_potential_mate(senior_adult_cat1,True))
        self.assertFalse(young_adult_cat1.is_potential_mate(elder_cat1,True))

        self.assertFalse(adult_cat_out_range1.is_potential_mate(kitten_cat2,True))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(adolescent_cat1,True))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(young_adult_cat1,True))
        self.assertFalse(adult_cat_out_range1.is_potential_mate(elder_cat1,True))

        self.assertFalse(senior_adult_cat1.is_potential_mate(kitten_cat1,True))
        self.assertFalse(senior_adult_cat1.is_potential_mate(adolescent_cat1,True))
        self.assertFalse(senior_adult_cat1.is_potential_mate(young_adult_cat1,True))

        # check valid constellations
        self.assertTrue(kitten_cat1.is_potential_mate(kitten_cat2,True))
        self.assertTrue(adolescent_cat1.is_potential_mate(adolescent_cat2,True))
        self.assertTrue(young_adult_cat1.is_potential_mate(young_adult_cat2,True))
        self.assertTrue(young_adult_cat1.is_potential_mate(adult_cat_in_range1,True))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(young_adult_cat1,True))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(adult_cat_in_range2,True))
        self.assertTrue(adult_cat_in_range1.is_potential_mate(adult_cat_out_range1,True))
        self.assertTrue(adult_cat_out_range1.is_potential_mate(adult_cat_out_range2,True))
        self.assertTrue(adult_cat_out_range1.is_potential_mate(senior_adult_cat1,True))
        self.assertTrue(senior_adult_cat1.is_potential_mate(adult_cat_out_range1,True))
        self.assertTrue(senior_adult_cat1.is_potential_mate(senior_adult_cat2,True))
        self.assertTrue(senior_adult_cat1.is_potential_mate(elder_cat1,True))
        self.assertTrue(elder_cat1.is_potential_mate(senior_adult_cat1,True))
        self.assertTrue(elder_cat1.is_potential_mate(elder_cat2,True))

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

    def test_possible_setting(self):
        mentor = Cat(moons=50)
        former_appr = Cat(moons=20)
        mentor.former_apprentices.append(former_appr.ID)

        self.assertFalse(mentor._intern_potential_mate(former_appr,False,False))
        self.assertFalse(former_appr._intern_potential_mate(mentor,False,False))
        self.assertTrue(mentor._intern_potential_mate(former_appr,False,True))
        self.assertTrue(former_appr._intern_potential_mate(mentor,False,True))

        self.assertFalse(mentor._intern_potential_mate(former_appr,True,False))
        self.assertFalse(former_appr._intern_potential_mate(mentor,True,False))
        self.assertTrue(mentor._intern_potential_mate(former_appr,True,True))
        self.assertTrue(former_appr._intern_potential_mate(mentor,True,True))

class TestMateFunctions(unittest.TestCase):

    def test_set_mate(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        # when
        cat1.set_mate(cat2)
        cat2.set_mate(cat1)

        # then
        self.assertEqual(cat1.mate,cat2.ID)
        self.assertEqual(cat2.mate,cat1.ID)

    def test_unset_mate(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat1.mate = cat2.ID
        cat2.mate = cat1.ID

        # when
        cat1.unset_mate()
        cat2.unset_mate()

        # then
        self.assertEqual(cat1.mate,None)
        self.assertEqual(cat2.mate,None)

    def test_set_mate_relationship(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        relation1 = Relationship(cat1,cat2)
        old_relation1 = deepcopy(relation1)
        relation2 = Relationship(cat2,cat1)
        old_relation2 = deepcopy(relation1)
        
        cat1.relationships[cat2.ID] = relation1
        cat2.relationships[cat1.ID] = relation2

        # when
        cat1.set_mate(cat2)
        cat2.set_mate(cat1)

        # then
        # TODO: maybe not correct check
        self.assertLess(old_relation1.romantic_love, relation1.romantic_love)
        self.assertLessEqual(old_relation1.platonic_like, relation1.platonic_like)
        self.assertLessEqual(old_relation1.dislike, relation1.dislike)
        self.assertLess(old_relation1.comfortable, relation1.comfortable)
        self.assertLess(old_relation1.trust, relation1.trust)
        self.assertLessEqual(old_relation1.admiration, relation1.admiration)
        self.assertLessEqual(old_relation1.jealousy, relation1.jealousy)

        self.assertLess(old_relation2.romantic_love, relation2.romantic_love)
        self.assertLessEqual(old_relation2.platonic_like, relation2.platonic_like)
        self.assertLessEqual(old_relation2.dislike, relation2.dislike)
        self.assertLess(old_relation2.comfortable, relation2.comfortable)
        self.assertLess(old_relation2.trust, relation2.trust)
        self.assertLessEqual(old_relation2.admiration, relation2.admiration)
        self.assertLessEqual(old_relation2.jealousy, relation2.jealousy)

    def test_unset_mate_relationship(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        relation1 = Relationship(cat1,cat2, family=False, mates=True, romantic_love=40, platonic_like=40, dislike=0, comfortable=40, trust=20, admiration=20,jealousy=20)
        old_relation1 = deepcopy(relation1)
        relation2 = Relationship(cat2,cat1, family=False, mates=True, romantic_love=40, platonic_like=40, dislike=0, comfortable=40, trust=20, admiration=20,jealousy=20)
        old_relation2 = deepcopy(relation2)
        cat1.mate = cat2.ID
        cat2.mate = cat1.ID
        cat1.relationships[cat2.ID] = relation1
        cat2.relationships[cat1.ID] = relation2

        # when
        cat1.unset_mate(breakup=True)
        cat2.unset_mate(breakup=True)

        # then
        # TODO: maybe not correct check
        self.assertGreater(old_relation1.romantic_love, relation1.romantic_love)
        self.assertGreaterEqual(old_relation1.platonic_like, relation1.platonic_like)
        self.assertGreaterEqual(old_relation1.dislike, relation1.dislike)
        self.assertGreater(old_relation1.comfortable, relation1.comfortable)
        self.assertGreater(old_relation1.trust, relation1.trust)
        self.assertGreaterEqual(old_relation1.admiration, relation1.admiration)
        self.assertGreaterEqual(old_relation1.jealousy, relation1.jealousy)

        self.assertGreater(old_relation2.romantic_love, relation2.romantic_love)
        self.assertGreaterEqual(old_relation2.platonic_like, relation2.platonic_like)
        self.assertGreaterEqual(old_relation2.dislike, relation2.dislike)
        self.assertGreater(old_relation2.comfortable, relation2.comfortable)
        self.assertGreater(old_relation2.trust, relation2.trust)
        self.assertGreaterEqual(old_relation2.admiration, relation2.admiration)
        self.assertGreaterEqual(old_relation2.jealousy, relation2.jealousy)

class TestStatusChange(unittest.TestCase):

    def test_apprentice_to_warrior(self):
        # given
        apprentice = Cat()
        mentor = Cat()
        apprentice.status = "apprentice"
        apprentice.skill = "???"
        mentor.apprentice.append(apprentice.ID)
        apprentice.mentor = mentor.ID

        # when
        self.assertNotEqual(apprentice.mentor, None)
        apprentice.status_change("warrior")
        
        # then
        self.assertNotEqual(apprentice.skill, "???")
        self.assertIn(apprentice.skill, apprentice.skills)
        self.assertEqual(apprentice.mentor, None)
        self.assertFalse(mentor.apprentice)

class TestUpdateMentor(unittest.TestCase):
    def test_exile_apprentice(self):
        # given
        app = Cat(moons=7, status="apprentice")
        mentor = Cat(moons=20, status="warrior")
        app.update_mentor(mentor.ID)

        # when
        self.assertTrue(app.ID in mentor.apprentice)
        self.assertFalse(app.ID in mentor.former_apprentices)
        self.assertEqual(app.mentor, mentor.ID)
        app.exiled = True
        app.update_mentor()

        # then
        self.assertFalse(app.ID in mentor.apprentice)
        self.assertTrue(app.ID in mentor.former_apprentices)
        self.assertIsNone(app.mentor)
