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

        patrol_all_events = Patrol()
        patrol_all_events.add_patrol_cats([cat1, cat2], test_clan)

        patrol_not_all_events = Patrol()
        patrol_not_all_events.add_patrol_cats([cat1, cat2, parent], test_clan)

        all_filtered = patrol_all_events.filter_relationship(possible_patrols)
        not_all_filtered = patrol_not_all_events.filter_relationship(possible_patrols)

        # then
        self.assertEqual(len(all_filtered), len(possible_patrols))
        self.assertNotEqual(len(not_all_filtered), len(possible_patrols))