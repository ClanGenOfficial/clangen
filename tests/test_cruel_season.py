import os
import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from pygame import image

from scripts.cat import save_load
from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.cat.sprites.load_sprites import sprites
from scripts.clan import Afterlife, Clan
from scripts.clan_package.settings import set_clan_setting
from scripts.config import get_config
from scripts.game_structure import game, constants
from scripts.game_structure.game.save_load import read_clans
from scripts.housekeeping.datadir import get_save_dir
from tests.test_cat import cat_factory


class TestEvents(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # load in the spritesheets
        # we have to do this to prevent a crash, even though we won't be displaying anything
        sprites.load_all()

        cls.test_clan_name = f"Test_{uuid4()}"

        cls.clanlist = read_clans()
        cls.previously_loaded_clan = cls.clanlist[0] if cls.clanlist else None

        game.starclan = Afterlife()
        game.dark_forest = Afterlife()
        game.clan = Clan(
            save_id=cls.test_clan_name,
            display_name="Test",
            leader=cat_factory.create_cat(rank=CatRank.LEADER),
            deputy=cat_factory.create_cat(rank=CatRank.DEPUTY),
            medicine_cat=cat_factory.create_cat(rank=CatRank.MEDICINE_CAT),
            biome="Forest",
            camp_bg="camp1",
            symbol="symbolADDER0",
            game_mode="cruel_season",
            starting_members=[
                cat_factory.create_cat(rank=rank)
                for rank in [
                    CatRank.KITTEN,
                    CatRank.APPRENTICE,
                    CatRank.APPRENTICE,
                    CatRank.WARRIOR,
                    CatRank.WARRIOR,
                    CatRank.WARRIOR,
                    CatRank.WARRIOR,
                    CatRank.WARRIOR,
                    CatRank.WARRIOR,
                    CatRank.ELDER,
                ]
            ],
            starting_season="Newleaf",
        )
        save_load.cat_to_fade.clear()
        game.clan.create_clan()
        game.cur_events_list.clear()
        game.herb_events_list.clear()
        game.clan.herb_supply.start_storage(15)
        game.clan.save_herb_supply(game.clan)
        game.clan.grief_strings.clear()
        Cat.sort_cats()
        # prevent them from just dying of starvation
        set_clan_setting("business as usual", False)
        set_clan_setting("hunting", True)

    @classmethod
    def tearDownClass(cls):
        """
        Be a polite bulk test and clean up after yourself
        :return:
        """
        rempath = get_save_dir() + "/" + cls.test_clan_name
        shutil.rmtree(rempath)
        if os.path.exists(rempath + "/clan.json"):
            os.remove(rempath + "/clan.json")

        if cls.previously_loaded_clan:
            with open(Path(get_save_dir()) / "currentclan.txt", "w") as currentclanfile:
                currentclanfile.write(str(cls.previously_loaded_clan))

    def test_card_validity(self):
        for card, info in constants.CRUEL_CARDS_ALL.items():
            modifiers = info["modifiers"]

            for modifier in modifiers:
                with self.subTest(
                    msg=f"{modifier} modifier on {card} could not be loaded"
                ):
                    try:
                        _value = get_config(modifier)
                    except KeyError as e:
                        self.fail(
                            f"ERROR with {modifier} modifier on {card}: {e}. Check that this is a valid modifier path."
                        )

    def test_card_art_load(self):
        for card, info in constants.CRUEL_CARDS_ALL.items():
            art = info["card_art"]
            with self.subTest(msg=f"{art} was an invalid file path for {card}"):
                try:
                    _file = image.load(f"resources/images/cruel_cards/{art}")
                except FileNotFoundError as e:
                    self.fail(
                        f"ERROR with {art} on {card}: {e}. Check that this is a valid file path."
                    )
