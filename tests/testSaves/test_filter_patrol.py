import unittest

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
        cat1.siblings = [cat2.ID]
        cat2.siblings = [cat1.ID]

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraint.append("siblings")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, parent], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

    def test_mates_patrol(self):
        # given
        mate1 = Cat()
        mate2 = Cat()
        cat1 = Cat()

        mate1.mate = mate2.ID
        mate2.mate =mate1.ID

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraint.append("mates")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        test_clan = Clan(name="test")

        # then
        patrol_all_events = Patrol()
        patrol_all_events.add_patrol_cats([mate1, mate2], test_clan)
        all_filtered = patrol_all_events.filter_relationship(possible_patrols)
        self.assertEqual(len(all_filtered), len(possible_patrols))

        patrol_not_all_events = Patrol()
        patrol_not_all_events.add_patrol_cats([mate1, cat1], test_clan)
        not_all_filtered = patrol_not_all_events.filter_relationship(possible_patrols)
        self.assertNotEqual(len(not_all_filtered), len(possible_patrols))

        patrol_not_all_events2 = Patrol()
        patrol_not_all_events2.add_patrol_cats([mate1, mate2, cat1], test_clan)
        not_all_filtered2 = patrol_not_all_events2.filter_relationship(possible_patrols)
        self.assertNotEqual(len(not_all_filtered2), len(possible_patrols))

    def test_parent_child_patrol(self):
        # given
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)
        cat1.siblings = [cat2.ID]
        cat2.siblings = [cat1.ID]

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraint.append("parent/child")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = parent
        patrol.patrol_random_cat = cat1
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = cat1
        patrol.patrol_random_cat = parent
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

        patrol = Patrol()
        cat_list = [cat1, cat2, parent]
        patrol.add_patrol_cats(cat_list, test_clan)
        patrol.patrol_leader = parent
        patrol.patrol_random_cat = cat2
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

    def test_child_parent_patrol(self):
        # given
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)
        cat1.siblings = [cat2.ID]
        cat2.siblings = [cat1.ID]

        # when
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraint.append("child/parent")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        test_clan = Clan(name="test")

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = cat1
        patrol.patrol_random_cat = parent
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        patrol = Patrol()
        patrol.add_patrol_cats([parent, cat1], test_clan)
        patrol.patrol_leader = parent
        patrol.patrol_random_cat = cat1
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

        patrol = Patrol()
        cat_list = [cat1, cat2, parent]
        patrol.add_patrol_cats(cat_list, test_clan)
        patrol.patrol_leader = parent
        patrol.patrol_random_cat = cat2
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

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
        con_patrol_event.relationship_constraint.append("romantic_10")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraint.append("romantic_30")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

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
        con_patrol_event.relationship_constraint.append("platonic_10")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraint.append("platonic_30")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

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
        con_patrol_event.relationship_constraint.append("dislike_10")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraint.append("dislike_30")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

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
        con_patrol_event.relationship_constraint.append("comfortable_10")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraint.append("comfortable_30")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

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
        con_patrol_event.relationship_constraint.append("jealousy_10")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraint.append("jealousy_30")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

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
        con_patrol_event.relationship_constraint.append("trust_10")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraint.append("trust_30")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

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
        con_patrol_event.relationship_constraint.append("romantic_10")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        # when - to high limit
        con_patrol_event = PatrolEvent(patrol_id="test3")
        con_patrol_event.relationship_constraint.append("romantic_30")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))


        # when - different relationship values
        cat3.relationships[cat2.ID].romantic_love = 5
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraint.append("romantic_10")
        no_con_patrol_event = PatrolEvent(patrol_id="test2")
        possible_patrols = [con_patrol_event, no_con_patrol_event]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2, cat3], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))

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
        con_patrol_event.relationship_constraint.append("romantic_10")
        con_patrol_event2 = PatrolEvent(patrol_id="test2")
        con_patrol_event2.relationship_constraint.append("platonic_10")
        possible_patrols = [con_patrol_event, con_patrol_event2]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        # when - to high
        con_patrol_event = PatrolEvent(patrol_id="test1")
        con_patrol_event.relationship_constraint.append("romantic_10")
        con_patrol_event2 = PatrolEvent(patrol_id="test2")
        con_patrol_event2.relationship_constraint.append("platonic_30")
        possible_patrols = [con_patrol_event, con_patrol_event2]

        # then
        patrol = Patrol()
        patrol.add_patrol_cats([cat1, cat2], test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertNotEqual(len(filtered), len(possible_patrols))
