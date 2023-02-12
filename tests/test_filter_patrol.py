import unittest

try:
    import ujson
except ImportError:
    import json as ujson

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
        cat_list = [cat1, cat2]
        patrol.add_patrol_cats(cat_list, test_clan)
        filtered = patrol.filter_relationship(possible_patrols)
        self.assertEqual(len(filtered), len(possible_patrols))

        patrol = Patrol()
        cat_list = [cat1, cat2, parent]
        patrol.add_patrol_cats(cat_list, test_clan)
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