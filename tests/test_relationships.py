import unittest
import ujson
from scripts.cats import Cat
from scripts.relationship import Relationship

class TestPersonalityCompatibility(unittest.TestCase):

    def test_love_action_possibilities_sibling(self):
        # given
        cat1 = Cat()
        cat2 = Cat()
        cat1.siblings.append(cat2.ID)
        cat2.siblings.append(cat1.ID)

        relationship = Relationship(cat1,cat2)
        relationship.link_relationship()

        LOVE = None
        resource_directory = "scripts/resources/relationship_events/"
        with open(f"{resource_directory}love.json", 'r') as read_file:
            LOVE = ujson.loads(read_file.read())

        # when
        relationship.platonic_like = 60
        relationship.opposite_relationship.platonic_like = 60

        # then
        possibilities = relationship.get_action_possibilities()
        self.assertFalse(any(x in possibilities for x in LOVE['love_interest_only']))
        self.assertFalse(any(x in possibilities for x in LOVE['love_interest']))
        self.assertFalse(any(x in possibilities for x in LOVE['mates']))

    def test_love_action_possibilities_parent(self):
        # given
        cat1 = Cat()
        cat2 = Cat(parent1=cat1.ID)

        relationship = Relationship(cat1,cat2)
        relationship.link_relationship()

        LOVE = None
        resource_directory = "scripts/resources/relationship_events/"
        with open(f"{resource_directory}love.json", 'r') as read_file:
            LOVE = ujson.loads(read_file.read())

        # when
        relationship.platonic_like = 60
        relationship.opposite_relationship.platonic_like = 60

        # then
        possibilities = relationship.get_action_possibilities()
        self.assertFalse(any(x in possibilities for x in LOVE['love_interest_only']))
        self.assertFalse(any(x in possibilities for x in LOVE['love_interest']))
        self.assertFalse(any(x in possibilities for x in LOVE['mates']))

    def test_love_action_possibilities_uncle(self):
        # given
        parent = Cat()
        cat1 = Cat()
        parent.siblings.append(cat1.ID)
        cat1.siblings.append(parent.ID)
        cat2 = Cat(parent1=parent.ID)

        relationship = Relationship(cat1,cat2)
        relationship.link_relationship()

        LOVE = None
        resource_directory = "scripts/resources/relationship_events/"
        with open(f"{resource_directory}love.json", 'r') as read_file:
            LOVE = ujson.loads(read_file.read())

        # when
        relationship.platonic_like = 60
        relationship.opposite_relationship.platonic_like = 60

        # then
        possibilities = relationship.get_action_possibilities()
        self.assertFalse(any(x in possibilities for x in LOVE['love_interest_only']))
        self.assertFalse(any(x in possibilities for x in LOVE['love_interest']))
        self.assertFalse(any(x in possibilities for x in LOVE['mates']))

    def test_love_action_possibilities_grandparents(self):
        # given
        grand_parent = Cat()
        cat1 = Cat(parent1=grand_parent.ID)
        cat2 = Cat(parent1=cat1.ID)

        relationship = Relationship(cat1,cat2)
        relationship.link_relationship()

        LOVE = None
        resource_directory = "scripts/resources/relationship_events/"
        with open(f"{resource_directory}love.json", 'r') as read_file:
            LOVE = ujson.loads(read_file.read())

        # when
        relationship.platonic_like = 60
        relationship.opposite_relationship.platonic_like = 60

        # then
        possibilities = relationship.get_action_possibilities()
        self.assertFalse(any(x in possibilities for x in LOVE['love_interest_only']))
        self.assertFalse(any(x in possibilities for x in LOVE['love_interest']))
        self.assertFalse(any(x in possibilities for x in LOVE['mates']))
