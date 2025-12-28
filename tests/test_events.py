import unittest
from random import choice
from uuid import uuid4

from scripts.cat.cats import create_cat, Cat
from scripts.cat.enums import CatRank
from scripts.cat.sprites import sprites
from scripts.clan import Clan
from scripts.clan_package.settings import switch_clan_setting, set_clan_setting
from scripts import events
from scripts.game_structure import game
from scripts.utility import get_living_cat_count


class TestEvents(unittest.TestCase):
    def test_bulk_skip(self):
        # load in the spritesheets
        # we have to do this to prevent a crash, even though we won't be displaying anything
        sprites.load_all()

        game.clan = Clan(
            name=f"{'Test'}_{uuid4()}",
            displayname="Test",
            leader=create_cat(CatRank.LEADER),
            deputy=create_cat(CatRank.DEPUTY),
            medicine_cat=create_cat(CatRank.MEDICINE_CAT),
            biome="Forest",
            camp_bg="camp1",
            symbol="ADDER0",
            game_mode="expanded",
            starting_members=[
                create_cat(
                    choice(
                        [
                            CatRank.KITTEN,
                            CatRank.APPRENTICE,
                            CatRank.WARRIOR,
                            CatRank.WARRIOR,
                            CatRank.ELDER,
                        ]
                    )
                )
                for _ in range(10)
            ],
            starting_season="Newleaf",
        )
        game.clan.create_clan()
        game.cur_events_list.clear()
        game.herb_events_list.clear()
        game.clan.herb_supply.start_storage(15)
        game.clan.save_herb_supply(game.clan)
        Cat.grief_strings.clear()
        Cat.sort_cats()
        # prevent them from just dying of starvation
        set_clan_setting("business as usual", False)
        set_clan_setting("hunting", True)

        with self.subTest(
            "Timeskip Failed",
        ):
            for _ in range(500):
                events.one_moon()
                if not _ % 100:
                    print(f"CATS ALIVE: {get_living_cat_count(Cat)}")
