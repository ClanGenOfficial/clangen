import unittest
from scripts.cat.cats import Cat, Relationship

from scripts.cat_relations.interaction import (
    Group_Interaction,
    Single_Interaction, 
    rel_fulfill_rel_constraints,
    cats_fulfill_single_interaction_constraints
)

class Relationship_Constraints(unittest.TestCase):
    def test_siblings(self):
        # given
        parent = Cat()
        cat_from = Cat(parent1=parent.ID)
        cat_to = Cat(parent1=parent.ID)
        rel = Relationship(cat_from, cat_to, False, True)
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["sibling"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["not_mates"], "test"))

    def test_mates(self):
        # given
        cat_from = Cat()
        cat_to = Cat()
        cat_from.mate = cat_to.ID
        cat_to.mate = cat_from.ID
        rel = Relationship(cat_from, cat_to, True, False)
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["mates"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["not_mates"], "test"))

    def test_parent_child_combo(self):
        # given
        parent = Cat()
        child = Cat(parent1=parent.ID)

        child_parent_rel = Relationship(child, parent, False, True)
        parent_child_rel = Relationship(parent, child, False, True)
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(child_parent_rel, ["child/parent"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(child_parent_rel, ["parent/child"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(parent_child_rel, ["parent/child"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(parent_child_rel, ["child/parent"], "test"))

    def test_rel_values_above(self):
        # given
        cat_from = Cat()
        cat_to = Cat()
        rel = Relationship(cat_from, cat_to)
        rel.romantic_love = 50
        rel.platonic_like = 50
        rel.dislike = 50
        rel.comfortable = 50
        rel.jealousy = 50
        rel.trust = 50
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["romantic_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["romantic_60"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["platonic_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["platonic_60"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["comfortable_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["comfortable_60"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["jealousy_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["jealousy_60"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["trust_50"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["trust_60"], "test"))

    def test_rel_values_under(self):
        # given
        cat_from = Cat()
        cat_to = Cat()
        rel = Relationship(cat_from, cat_to)
        rel.romantic_love = 50
        rel.platonic_like = 50
        rel.dislike = 50
        rel.comfortable = 50
        rel.jealousy = 50
        rel.trust = 50
    
        # then
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["romantic_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["romantic_30_lower"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["platonic_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["platonic_30_lower"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["comfortable_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["comfortable_30_lower"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["jealousy_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["jealousy_30_lower"], "test"))
        self.assertTrue(rel_fulfill_rel_constraints(rel, ["trust_50_lower"], "test"))
        self.assertFalse(rel_fulfill_rel_constraints(rel, ["trust_30_lower"], "test"))