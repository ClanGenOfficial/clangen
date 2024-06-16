import unittest

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.cat_relations.relationship import Relationship
from scripts.clan.playerclan import PlayerClan
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
        game.clan = PlayerClan()
        game.clan.instructor = Cat(status="warrior", dead=True, dead_for=20)
        game.clan.all_clans = [PlayerClan(name="Test")]

    def tearDown(self):
        game.clan.leader_lives = 9

    def test_basic_murder(self):
        """Check basic murder is working as intended"""
        victim = create_victim()
        murderer = create_murderer()

        game.config["event_generation"]["debug_ensure_event_id"] = "gen_death_murder_any1"

        # loathing. unadulterated loathing. for their face, their paws, their accessories.
        murderer.relationships[victim.ID] = Relationship(murderer, victim, dislike=100, platonic_like=-100)

        # override the calculations to force their hand
        Events.handle_murder(Events(), murderer, debug_force_murder=True)

        murderer_history = murderer.history.murder["is_murderer"][0]
        victim_history = victim.history.murder["is_victim"][0]

        self.assertTrue(victim.dead)
        self.assertEqual(victim_history["text"],
                         f"m_c was secretly murdered by {murderer.name}.")

        self.assertEqual(murderer_history["victim"],
                         victim.ID)

    def test_leader_murder_some_lives(self):
        """Check leader murder is working as intended."""
        victim = create_victim()
        victim.status = "leader"
        game.clan.leader = victim

        murderer = create_murderer()

        game.config["event_generation"]["debug_ensure_event_id"] = "gen_death_murder_anylead3"  # only takes some lives

        # loathing. unadulterated loathing. for their face, their paws, their accessories.
        murderer.relationships[victim.ID] = Relationship(murderer, victim, dislike=100, platonic_like=-100)

        # override the calculations to force their hand
        Events.handle_murder(Events(), murderer, debug_force_murder=True)

        murderer_history = murderer.history.murder["is_murderer"][0]
        victim_history = victim.history.murder["is_victim"][0]

        self.assertFalse(victim.dead)
        self.assertNotEqual(game.clan.leader_lives, 9)

        # reset for the next test

        game.clan.leader_lives = 9

    def test_leader_murder_all_lives(self):
        """Check leader murder is working as intended."""
        victim = create_victim()
        victim.status = "leader"

        murderer = create_murderer()

        game.config["event_generation"]["debug_ensure_event_id"] = "gen_death_murder_anylead4"

        # loathing. unadulterated loathing. for their face, their paws, their accessories.
        murderer.relationships[victim.ID] = Relationship(murderer, victim, dislike=100, platonic_like=-100)

        # override the calculations to force their hand
        Events.handle_murder(Events(), murderer, debug_force_murder=True)

        murderer_history = murderer.history.murder["is_murderer"][0]
        victim_history = victim.history.murder["is_victim"][0]

    def test_secret_murder(self):
        """check that a secret/unrevealed murder is working as intended"""
        victim = create_victim()
        murderer = create_murderer()

        game.config["event_generation"]["debug_ensure_event_id"] = "gen_death_murder_any1"

        murderer.relationships[victim.ID] = Relationship(murderer, victim, dislike=30, platonic_like=-15)

        Events.handle_murder(Events(), murderer, debug_force_murder=True)

        murderer_history = murderer.history.murder["is_murderer"][0]
        victim_history = victim.history.murder["is_victim"][0]

        self.assertTrue(victim.dead)
        self.assertEqual(victim_history["text"],
                         f"m_c was secretly murdered by {murderer.name}.")

        self.assertEqual(murderer_history["victim"],
                         victim.ID)
        self.assertFalse(murderer_history["revealed"])
