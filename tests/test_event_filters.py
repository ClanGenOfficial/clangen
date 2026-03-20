import unittest

from scripts.cat.cats import Cat, create_cat
from scripts.cat.enums import CatRank
from scripts.clan import Clan
from scripts.events_module.event_filters import (
    event_for_location,
    event_for_season,
    event_for_tags,
    event_for_cat,
)
from scripts.game_structure import game


class TestEventFilters(unittest.TestCase):
    def setUp(self):
        game.clan = Clan()
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        game.clan.game_mode = "classic"

        self.test_cat = create_cat(CatRank.LEADER, moons=50)
        game.clan.leader = self.test_cat

    def test_location(self):
        """
        Tests a variety of location tag combinations
        """

        self.assertTrue(
            event_for_location(locations=["forest"]),
            "Assert single biome match.",
        )
        self.assertTrue(
            event_for_location(locations=["forest:camp1"]),
            "Assert single camp match.",
        )
        self.assertFalse(
            event_for_location(locations=["desert"]),
            "Assert single biome mismatch.",
        )
        self.assertFalse(
            event_for_location(locations=["forest:camp2"]),
            "Assert single camp mismatch.",
        )
        self.assertTrue(
            event_for_location(locations=["desert:camp2", "forest"]),
            "Assert mixed location match.",
        )
        self.assertFalse(
            event_for_location(locations=["desert:camp2", "plains", "forest:camp2"]),
            "Assert mixed location mismatch.",
        )
        self.assertTrue(
            event_for_location(locations=["-plains"]),
            "Assert single location excluded.",
        )
        self.assertTrue(
            event_for_location(locations=["-plains", "-forest:camp2"]),
            "Assert mixed locations excluded.",
        )
        self.assertFalse(
            event_for_location(locations=["-plains", "-forest"]),
            "Assert mixed locations, including current biome, excluded.",
        )
        self.assertFalse(
            event_for_location(locations=["-plains", "-forest:camp1"]),
            "Assert mixed locations, including current camp, excluded.",
        )

    def test_season(self):
        self.assertTrue(event_for_season(["newleaf"]), "Assert single season match.")
        self.assertFalse(
            event_for_season(["greenleaf"]), "Assert single season mismatch."
        )
        self.assertTrue(
            event_for_season(["newleaf", "greenleaf"]),
            "Assert mixed season match.",
        )
        self.assertFalse(
            event_for_season(["greenleaf", "leaf-bare"]),
            "Assert mixed season mismatch.",
        )
        self.assertTrue(
            event_for_season(["-greenleaf"]),
            "Assert single season excluded.",
        )
        self.assertFalse(
            event_for_season(["-newleaf"]),
            "Assert current season excluded.",
        )
        self.assertTrue(
            event_for_season(["-greenleaf", "-leaf-bare"]),
            "Assert mixed season excluded.",
        )
        self.assertFalse(
            event_for_season(["-greenleaf", "-newleaf"]),
            "Assert mixed season, including current, excluded.",
        )

    def test_game_mode_tags(self):
        self.assertTrue(
            event_for_tags(["classic"], self.test_cat),
            "Assert correct game mode tag.",
        )
        self.assertFalse(
            event_for_tags(["expanded"], self.test_cat),
            "Assert incorrect game mode tag",
        )

    def test_leader_life_tags(self):
        game.clan.leader_lives = 9
        self.assertTrue(
            event_for_tags(["some_lives", "lives_remain", "high_lives"], self.test_cat),
            "Assert 9-life leader passes some_lives, lives_remain, and high_lives.",
        )
        self.assertFalse(
            event_for_tags(["mid_lives", "low_lives"], self.test_cat),
            "Assert 9-lives leader does not pass mid_lives and low_lives.",
        )
        self.assertFalse(
            event_for_tags(["mid_lives", "low_lives", "some_lives"], self.test_cat),
            "Assert 9-lives leader does not pass mixed tag list where they qualify for 1 tag, but not others.",
        )

        game.clan.leader_lives = 5
        self.assertTrue(
            event_for_tags(["some_lives", "mid_lives", "lives_remain"], self.test_cat),
            "Assert 5-lives leader passes some_lives, mid_lives, and lives_remain.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "low_lives"], self.test_cat),
            "Assert 5-lives leader does not pass mid_lives and low_lives.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "low_lives", "some_lives"], self.test_cat),
            "Assert 5-lives leader does not pass mixed tag list where they qualify for 1 tag, but not others.",
        )

        game.clan.leader_lives = 3
        self.assertTrue(
            event_for_tags(["low_lives", "lives_remain"], self.test_cat),
            "Assert 3-lives leader passes low_lives and lives_remain.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "mid_lives", "some_lives"], self.test_cat),
            "Assert 3-lives leader does not pass mid_lives, high_lives, and some_lives.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "low_lives", "some_lives"], self.test_cat),
            "Assert 3-lives leader does not pass mixed tag list where they qualify for 1 tag, but not others.",
        )

        game.clan.leader_lives = 1
        self.assertTrue(
            event_for_tags(["low_lives"], self.test_cat),
            "Assert 1-life leader passes low_lives.",
        )
        self.assertFalse(
            event_for_tags(
                ["high_lives", "mid_lives", "some_lives", "lives_remain"], self.test_cat
            ),
            "Assert 1-life leader does not pass mid_lives, high_lives, some_lives, and lives_remain.",
        )
        self.assertFalse(
            event_for_tags(["high_lives", "low_lives", "some_lives"], self.test_cat),
            "Assert 1-life leader does not pass mixed tag list where they qualify for 1 tag, but not others.",
        )
