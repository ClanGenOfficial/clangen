import unittest

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.patrol import PatrolEvent, Patrol
from scripts.clan import Clan

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
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["siblings"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, parent], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_mates_patrol(self):
        # given
        mate1 = Cat()
        mate2 = Cat()
        cat1 = Cat()

        mate1.mate.append(mate2.ID)
        mate2.mate.append(mate1.ID)

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["mates"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([mate1, mate2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        patrol = Patrol()
        patrol.add_patrol_cats([mate1, cat1], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        patrol = Patrol()
        patrol.add_patrol_cats([mate1, mate2, cat1], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_parent_child_patrol(self):
        # given
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)
        cat1.siblings = [cat2.ID]
        cat2.siblings = [cat1.ID]

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["parent/child"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = parent
        patrol.patrol_random_cat = cat1
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = cat1
        patrol.patrol_random_cat = parent
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        patrol = Patrol()
        cat_list = [cat1, cat2, parent]
        patrol.add_patrol_cats(cat_list, test_clan)
        patrol.patrol_leader = parent
        patrol.patrol_random_cat = cat2
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_child_parent_patrol(self):
        # given
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)
        cat1.siblings = [cat2.ID]
        cat2.siblings = [cat1.ID]

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["child/parent"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = cat1
        patrol.patrol_random_cat = parent
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = parent
        patrol.patrol_random_cat = cat1
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        patrol = Patrol()
        cat_list = [cat1, cat2, parent]
        patrol.add_patrol_cats(cat_list, test_clan)
        patrol.patrol_leader = parent
        patrol.patrol_random_cat = cat2
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_romantic_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)

        relationship1.romantic_love = 20
        relationship2.romantic_love = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["romantic_10"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.constraints["relationship"] = ["romantic_30"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_platonic_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)

        relationship1.platonic_like = 20
        relationship2.platonic_like = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["platonic_10"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.constraints["relationship"] = ["platonic_30"]
        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_dislike_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)

        relationship1.dislike = 20
        relationship2.dislike = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["dislike_10"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.constraints["relationship"] = ["dislike_30"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_comfortable_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)

        relationship1.comfortable = 20
        relationship2.comfortable = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["comfortable_10"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.constraints["relationship"] = ["comfortable_30"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_jealousy_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)

        relationship1.jealousy = 20
        relationship2.jealousy = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["jealousy_10"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.constraints["relationship"] = ["jealousy_30"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_trust_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)

        relationship1.trust = 20
        relationship2.trust = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["trust_10"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.constraints["relationship"] = ["trust_30"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_multiple_romantic_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat3 = Cat()

        relationship1_2 = Relationship(cat1,cat2)
        relationship1_3 = Relationship(cat1,cat3)
        relationship2_1 = Relationship(cat2,cat1)
        relationship2_3 = Relationship(cat2,cat3)
        relationship3_1 = Relationship(cat3,cat1)
        relationship3_2 = Relationship(cat3,cat2)

        relationship1_2.romantic_love = 20
        relationship1_3.romantic_love = 20
        relationship2_1.romantic_love = 20
        relationship2_3.romantic_love = 20
        relationship3_1.romantic_love = 20
        relationship3_2.romantic_love = 20

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
        con_patrol_event.constraints["relationship"] = ["romantic_10"]
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        no_con_patrol_event.constraints["relationship"] = []

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

        # when - to high limit
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.constraints["relationship"] = ["romantic_30"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))


        # when - different relationship values
        cat3.relationships[cat2.ID].romantic_love = 5
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["romantic_10"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        self.assertFalse(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(no_con_patrol_event))

    def test_multiple_constraint_patrol(self):
        # given
        cat1 = Cat()
        cat2 = Cat()

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)

        relationship1.romantic_love = 20
        relationship2.romantic_love = 20
        relationship1.platonic_like = 20
        relationship2.platonic_like = 20

        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        test_clan = Clan(name="test")

        # when - correct
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.constraints["relationship"] = ["romantic_10"]
        con_patrol_event2 = PatrolEvent(patrol_id="test2")
        con_patrol_event2.constraints["relationship"] = ["platonic_10"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertTrue(patrol.filter_relationship(con_patrol_event2))

        # when - to high
        con_patrol_event2 = PatrolEvent(patrol_id="test2")
        con_patrol_event2.constraints["relationship"] = ["platonic_30"]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        self.assertTrue(patrol.filter_relationship(con_patrol_event))
        self.assertFalse(patrol.filter_relationship(con_patrol_event2))