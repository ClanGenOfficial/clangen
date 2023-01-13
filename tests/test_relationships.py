import unittest
import ujson

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship

class TestRelationshipInteraction(unittest.TestCase):

    def test_love_action_possibilities_sibling(self):
        # given
        parent = Cat()
        cat1 = Cat(parent1=parent.ID)
        cat2 = Cat(parent1=parent.ID)
        cat1.siblings = [cat2.ID]
        cat2.siblings = [cat1.ID]
        cat1.trait = "charismatic"
        cat2.trait = "charismatic"

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        resource_directory = "resources/dicts/relationship_events/DE_IN_CREASE/"
        INCREASE_LOW = None
        INCREASE_HIGH = None
        with open(f"{resource_directory}INCREASE_HIGH.json", 'r') as read_file:
            INCREASE_HIGH = ujson.loads(read_file.read())
        with open(f"{resource_directory}INCREASE_LOW.json", 'r') as read_file:
            INCREASE_LOW = ujson.loads(read_file.read())

        # when
        relationship1.platonic_like = 60
        relationship2.platonic_like = 60

        # then
        possibilities1 = relationship1.get_action_possibilities()
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['to']['romantic_love']))
        possibilities2 = relationship2.get_action_possibilities()
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['to']['romantic_love']))

    def test_love_action_possibilities_parent(self):
        # given
        cat1 = Cat()
        cat2 = Cat(parent1=cat1.ID)
        cat1.trait = "charismatic"
        cat2.trait = "charismatic"


        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        resource_directory = "resources/dicts/relationship_events/DE_IN_CREASE/"
        INCREASE_LOW = None
        INCREASE_HIGH = None
        with open(f"{resource_directory}INCREASE_HIGH.json", 'r') as read_file:
            INCREASE_HIGH = ujson.loads(read_file.read())
        with open(f"{resource_directory}INCREASE_LOW.json", 'r') as read_file:
            INCREASE_LOW = ujson.loads(read_file.read())

        # when
        relationship1.platonic_like = 60
        relationship2.platonic_like = 60

        # then
        possibilities1 = relationship1.get_action_possibilities()
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['to']['romantic_love']))
        possibilities2 = relationship2.get_action_possibilities()
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['to']['romantic_love']))

    def test_love_action_possibilities_uncle(self):
        # given
        parent = Cat()
        cat1 = Cat()
        parent.siblings.append(cat1.ID)
        cat1.siblings.append(parent.ID)
        cat2 = Cat(parent1=parent.ID)
        
        cat1.trait = "charismatic"
        cat2.trait = "charismatic"

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        resource_directory = "resources/dicts/relationship_events/DE_IN_CREASE/"
        INCREASE_LOW = None
        INCREASE_HIGH = None
        with open(f"{resource_directory}INCREASE_HIGH.json", 'r') as read_file:
            INCREASE_HIGH = ujson.loads(read_file.read())
        with open(f"{resource_directory}INCREASE_LOW.json", 'r') as read_file:
            INCREASE_LOW = ujson.loads(read_file.read())

        # when
        relationship1.platonic_like = 60
        relationship2.platonic_like = 60

        # then
        possibilities1 = relationship1.get_action_possibilities()
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['to']['romantic_love']))
        possibilities2 = relationship2.get_action_possibilities()
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['to']['romantic_love']))

    def test_love_action_possibilities_grandparents(self):
        # given
        grand_parent = Cat()
        cat1 = Cat(parent1=grand_parent.ID)
        cat2 = Cat(parent1=cat1.ID)
        cat1.trait = "charismatic"
        cat2.trait = "charismatic"

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        resource_directory = "resources/dicts/relationship_events/DE_IN_CREASE/"
        INCREASE_LOW = None
        INCREASE_HIGH = None
        with open(f"{resource_directory}INCREASE_HIGH.json", 'r') as read_file:
            INCREASE_HIGH = ujson.loads(read_file.read())
        with open(f"{resource_directory}INCREASE_LOW.json", 'r') as read_file:
            INCREASE_LOW = ujson.loads(read_file.read())

        # when
        relationship1.platonic_like = 60
        relationship2.platonic_like = 60

        # then
        possibilities1 = relationship1.get_action_possibilities()
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['to']['romantic_love']))
        possibilities2 = relationship2.get_action_possibilities()
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['to']['romantic_love']))

    def test_love_action_possibilities_apprentice_warrior(self):
        # given
        cat1 = Cat(moons=6)
        cat2 = Cat(moons=15)
        cat1.trait = "charismatic"
        cat2.trait = "charismatic"

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        resource_directory = "resources/dicts/relationship_events/DE_IN_CREASE/"
        INCREASE_LOW = None
        INCREASE_HIGH = None
        with open(f"{resource_directory}INCREASE_HIGH.json", 'r') as read_file:
            INCREASE_HIGH = ujson.loads(read_file.read())
        with open(f"{resource_directory}INCREASE_LOW.json", 'r') as read_file:
            INCREASE_LOW = ujson.loads(read_file.read())

        # when
        relationship1.platonic_like = 60
        relationship2.platonic_like = 60

        # then
        possibilities1 = relationship1.get_action_possibilities()
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['to']['romantic_love']))
        possibilities2 = relationship2.get_action_possibilities()
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['to']['romantic_love']))

    def test_love_action_possibilities_mentor_apprentice(self):
        # given
        cat1 = Cat(moons=6)
        cat2 = Cat(moons=15)
        cat1.trait = "charismatic"
        cat2.trait = "charismatic"
        cat1.mentor = cat2

        relationship1 = Relationship(cat1,cat2)
        relationship2 = Relationship(cat2,cat1)
        relationship1.opposite_relationship = relationship2
        relationship2.opposite_relationship = relationship1
        cat1.relationships[cat2.ID] = relationship1
        cat2.relationships[cat1.ID] = relationship2

        resource_directory = "resources/dicts/relationship_events/DE_IN_CREASE/"
        INCREASE_LOW = None
        INCREASE_HIGH = None
        with open(f"{resource_directory}INCREASE_HIGH.json", 'r') as read_file:
            INCREASE_HIGH = ujson.loads(read_file.read())
        with open(f"{resource_directory}INCREASE_LOW.json", 'r') as read_file:
            INCREASE_LOW = ujson.loads(read_file.read())

        # when
        relationship1.platonic_like = 60
        relationship2.platonic_like = 60

        # then
        possibilities1 = relationship1.get_action_possibilities()
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities1 for action in INCREASE_HIGH['to']['romantic_love']))
        possibilities2 = relationship2.get_action_possibilities()
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_LOW['to']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['from']['romantic_love']))
        self.assertFalse(any(action in possibilities2 for action in INCREASE_HIGH['to']['romantic_love']))