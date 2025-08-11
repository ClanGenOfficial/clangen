import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan
from scripts.events_module.patrol.patrol import PatrolEvent, Patrol

from scripts.utility import filter_relationship_type

# TODO: redo them! Filtering is not working like this anymore, but it got removed from .github/workflows/test.yml
# so they are not failing!


class TestRelationshipConstraintPatrols(unittest.TestCase):
    def test_sibling_patrol(self):
        # given
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)
        cat1.create_inheritance_new_cat()
        cat2.create_inheritance_new_cat()

        # when
        self.assertTrue(cat1.is_sibling(cat2))
        self.assertTrue(cat2.is_sibling(cat1))
        self.assertFalse(cat1.is_sibling(parent))
        self.assertFalse(cat2.is_sibling(parent))

        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["siblings"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, parent], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_mates_patrol(self):
        # given
        mate1 = Cat()
        mate2 = Cat()
        cat1 = Cat()

        mate1.mate.append(mate2.ID)
        mate2.mate.append(mate1.ID)

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["mates"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([mate1, mate2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        patrol = Patrol()
        patrol.add_patrol_cats([mate1, cat1], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        patrol = Patrol()
        patrol.add_patrol_cats([mate1, mate2, cat1], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_parent_child_patrol(self):
        # given
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["parent/child"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = parent
        patrol.random_cat = cat1
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = cat1
        patrol.random_cat = parent
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        patrol = Patrol()
        cat_list = [cat1, cat2, parent]
        patrol.add_patrol_cats(cat_list, test_clan)
        patrol.patrol_leader = parent
        patrol.random_cat = cat2
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_child_parent_patrol(self):
        # given
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["child/parent"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = cat1
        patrol.random_cat = parent
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = parent
        patrol.random_cat = cat1
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        patrol = Patrol()
        cat_list = [cat1, cat2, parent]
        patrol.add_patrol_cats(cat_list, test_clan)
        patrol.patrol_leader = parent
        patrol.random_cat = cat2
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_romantic_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)

        relationship1.romance = 20
        relationship2.romance = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["fancies"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraints = ["adores"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_platonic_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)

        relationship1.like = 20
        relationship2.like = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["likes"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraints = ["enjoys"]
        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_dislike_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)

        relationship1.like = -20
        relationship2.like = -20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["dislikes"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraints = ["hates"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_comfort_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)

        relationship1.comfort = 20
        relationship2.comfort = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["relates_to"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraints = ["understands"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_jealousy_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)

        relationship1.respect = -20
        relationship2.respect = -20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["begrudges"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraints = ["envies"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_trust_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)

        relationship1.trust = 20
        relationship2.trust = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["listens_to"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraints = ["trusts"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_multiple_romantic_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat3 = Cat()

        relationship1_2 = Relationship(cat1, cat2)
        relationship1_3 = Relationship(cat1, cat3)
        relationship2_1 = Relationship(cat2, cat1)
        relationship2_3 = Relationship(cat2, cat3)
        relationship3_1 = Relationship(cat3, cat1)
        relationship3_2 = Relationship(cat3, cat2)

        relationship1_2.romance = 20
        relationship1_3.romance = 20
        relationship2_1.romance = 20
        relationship2_3.romance = 20
        relationship3_1.romance = 20
        relationship3_2.romance = 20

        relationship1_2.opposite_relationship = relationship2_1
        relationship1_3.opposite_relationship = relationship3_1
        relationship2_1.opposite_relationship = relationship1_2
        relationship2_3.opposite_relationship = relationship3_2
        relationship3_1.opposite_relationship = relationship3_1
        relationship3_2.opposite_relationship = relationship2_3

        cat1.relationships[cat2.ID] = relationship1_2
        cat1.relationships[cat3.ID] = relationship1_3
        cat2.relationships[cat1.ID] = relationship2_1
        cat2.relationships[cat3.ID] = relationship2_3
        cat3.relationships[cat1.ID] = relationship3_1
        cat3.relationships[cat2.ID] = relationship3_2

        test_clan = Clan(name="test")

        # when - all is correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["fancies"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.relationship_constraints = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        # when - to high limit
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraints = ["adores"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

        # when - different relationship values
        cat3.relationships[cat2.ID].romance = 0
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["fancies"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                no_con_patrol_event.relationship_constraints,
                no_con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )

    def test_multiple_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1, cat2)
        relationship2 = Relationship(cat2, cat1)

        relationship1.romance = 20
        relationship2.romance = 20
        relationship1.like = 20
        relationship2.like = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraints = ["fancies"]
        con_patrol_event2 = PatrolEvent(patrol_id="test2")
        con_patrol_event2.relationship_constraints = ["likes"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event2.relationship_constraints,
                con_patrol_event2.patrol_id,
                patrol.patrol_leader,
            )
        )
        # when - to high
        con_patrol_event2 = PatrolEvent(patrol_id="test2")
        con_patrol_event2.relationship_constraints = ["enjoys"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event.relationship_constraints,
                con_patrol_event.patrol_id,
                patrol.patrol_leader,
            )
        )
        self.assertFalse(
            filter_relationship_type(
                patrol.patrol_cats,
                con_patrol_event2.relationship_constraints,
                con_patrol_event2.patrol_id,
                patrol.patrol_leader,
            )
        )
