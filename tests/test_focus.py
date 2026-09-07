import os
import shutil
import unittest
from pathlib import Path
from uuid import uuid4

from scripts.cat import save_load
from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.cat.sprites.load_sprites import sprites
from scripts.clan import Clan, Afterlife
from scripts.clan_package.settings import set_clan_setting
from scripts.config import get_config
from scripts.events_module import focus
from scripts.game_structure import game
from scripts.game_structure.game.save_load import read_clans
from scripts.housekeeping.datadir import get_save_dir
from tests.test_cat import cat_factory


class TestFocus(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # load in the spritesheets
        # we have to do this to prevent a crash, even though we won't be displaying anything
        sprites.load_all()
        focus.disable_random = True
        cls.test_clan_name = f"Test_{uuid4()}"
        cls.clanlist = read_clans()
        cls.previously_loaded_clan = cls.clanlist[0] if cls.clanlist else None

    def setUp(self):
        Cat.all_cats.clear()
        Cat.all_cats_list.clear()

        game.starclan = Afterlife()
        game.dark_forest = Afterlife()
        self.leader = cat_factory.create_cat(rank=CatRank.LEADER)
        self.deputy = cat_factory.create_cat(rank=CatRank.DEPUTY)
        self.medicine_cat = cat_factory.create_cat(rank=CatRank.MEDICINE_CAT)
        game.clan = Clan(
            save_id=self.test_clan_name,
            display_name="Test",
            leader=self.leader,
            deputy=self.deputy,
            medicine_cat=self.medicine_cat,
            biome="Forest",
            camp_bg="camp1",
            symbol="symbolADDER0",
            game_mode="expanded",
            starting_members=[],
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

    @classmethod
    def tearDownClass(cls):
        focus.disable_random = False

        rempath = get_save_dir() + "/" + cls.test_clan_name
        shutil.rmtree(rempath)
        if os.path.exists(rempath + "/clan.json"):
            os.remove(rempath + "/clan.json")

        if cls.previously_loaded_clan:
            with open(Path(get_save_dir()) / "currentclan.txt", "w") as currentclanfile:
                currentclanfile.write(str(cls.previously_loaded_clan))

    @staticmethod
    def change_setting(setting: str):
        for s in (
            "business_as_usual",
            "hunting",
            "herb_gathering",
            "threaten_outsiders",
            "seek_outsiders",
            "sabotage_other_clans",
            "aid_other_clan",
            "raid_other_clans",
            "hoarding",
        ):
            set_clan_setting(s, False)

        set_clan_setting(setting, True)

    def test_hunting(self):
        self.change_setting("hunting")

        beginning_supply = game.clan.freshkill_pile.total_amount
        amount_should_gather = 2 * get_config(f"focus.hunting.{CatRank.WARRIOR}")

        focus.handle_focus()

        self.assertEqual(
            amount_should_gather + beginning_supply,
            game.clan.freshkill_pile.total_amount,
        )

    def test_herb_gathering(self):
        self.change_setting("herb_gathering")

        game.clan.herb_supply.disable_random = True
        beginning_supply = game.clan.herb_supply.total

        focus.handle_focus()

        # 12 is the amount that should be gathered in total by a single med cat with 2 helpers
        self.assertEqual(beginning_supply + 12, game.clan.herb_supply.total)

        game.clan.herb_supply.disable_random = False

    def test_threaten_outsiders(self):
        self.change_setting("threaten_outsiders")

        starting_relation = game.clan.reputation
        amount = get_config("focus.outsiders.reputation")

        focus.handle_focus()

        self.assertEqual(starting_relation - amount, game.clan.reputation)

    def test_seek_outsiders(self):
        self.change_setting("seek_outsiders")

        starting_relation = game.clan.reputation
        amount = get_config("focus.outsiders.reputation")

        focus.handle_focus()

        self.assertEqual(starting_relation + amount, game.clan.reputation)

    def test_sabotage_other_clans(self):
        self.change_setting("sabotage_other_clans")

        game.clan.clans_in_focus = [game.clan.all_other_clans[0].name]
        starting_relation = game.clan.all_other_clans[0].relations
        amount = get_config("focus.other_clans.relation")
        focus.handle_focus()

        self.assertEqual(
            starting_relation - amount, game.clan.all_other_clans[0].relations
        )

    def test_aid_other_clans(self):
        self.change_setting("aid_other_clans")

        game.clan.clans_in_focus = [game.clan.all_other_clans[0].name]
        starting_relation = game.clan.all_other_clans[0].relations
        amount = get_config("focus.other_clans.relation")
        focus.handle_focus()

        self.assertEqual(
            starting_relation + amount, game.clan.all_other_clans[0].relations
        )

    def test_raid_other_clans(self):
        self.change_setting("raid_other_clans")
        game.clan.clans_in_focus = [game.clan.all_other_clans[0].name]

        starting_relation = game.clan.all_other_clans[0].relations
        amount_rel = get_config("focus.raid_other_clans.relation")

        beginning_herbs = game.clan.herb_supply.total
        amount_herbs = 2
        beginning_prey = game.clan.freshkill_pile.total_amount
        amount_prey = 2

        focus.handle_focus()

        self.assertEqual(
            starting_relation + amount_rel,
            game.clan.all_other_clans[0].relations,
            msg=f"Clan relationship did not change as expected",
        )
        self.assertEqual(
            beginning_herbs + amount_herbs,
            game.clan.herb_supply.total,
            msg=f"Herb supply did not change as expected.",
        )
        self.assertEqual(
            beginning_prey + amount_prey,
            game.clan.freshkill_pile.total_amount,
            msg=f"Prey supply did not change as expected.",
        )
        self.assertTrue(self.leader.is_injured())
        self.assertTrue(self.deputy.is_injured())

    def test_hoarding(self):
        self.change_setting("hoarding")
        game.clan.herb_supply.disable_random = True
        beginning_herbs = game.clan.herb_supply.total
        amount_herbs = 6
        beginning_prey = game.clan.freshkill_pile.total_amount
        amount_prey = get_config("focus.hoarding.prey_warrior") * 2

        focus.handle_focus()

        self.assertEqual(
            beginning_herbs + amount_herbs,
            game.clan.herb_supply.total,
            msg=f"Herb supply did not change as expected.",
        )
        self.assertEqual(
            beginning_prey + amount_prey,
            game.clan.freshkill_pile.total_amount,
            msg=f"Prey supply did not change as expected.",
        )
        self.assertTrue(
            all(
                [
                    self.leader.is_injured(),
                    self.deputy.is_injured(),
                    self.medicine_cat.is_injured(),
                ]
            )
        )
        game.clan.herb_supply.disable_random = False
