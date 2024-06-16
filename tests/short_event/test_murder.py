import unittest

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.cat_relations.relationship import Relationship
from scripts.clan import Clan
from scripts.clan_resources.freshkill import FreshkillPile
from scripts.events import Events
from scripts.game_structure.game_essentials import game


def create_victim():
    victim = Cat()
    victim.status = "warrior"
    victim.age = "adolescent"
    victim.history = History()
    return victim


def create_murderer():
    murderer = Cat()
    murderer.status = "warrior"
    murderer.age = "adolescent"
    murderer.history = History()
    return murderer


class TestShortEventMurder(unittest.TestCase):
    def setUp(self):
        game.clan = Clan()
        game.clan.instructor = Cat(status="warrior", dead=True, dead_for=20)
        game.clan.all_clans = [Clan(name="Test")]

    def testBasicMurder(self):
        victim = create_victim()
        murderer = create_murderer()

        murderer.relationships[victim.ID] = Relationship(murderer, victim, dislike=30, platonic_like=-15)

        Events.handle_murder(Events(), murderer, force_murder=True)

        self.assertTrue(victim.dead)
