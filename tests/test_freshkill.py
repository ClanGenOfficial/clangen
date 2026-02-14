import os
import shutil
from pathlib import Path

from scripts.game_structure.game.save_load import read_clans
from scripts.housekeeping.datadir import get_save_dir

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import unittest
from uuid import uuid4

import ujson

from scripts.cat import save_load
from scripts.cat.enums import CatRank
from scripts.cat.sprites.load_sprites import sprites
from scripts.clan_package.settings import switch_clan_setting, set_clan_setting
from scripts.game_structure import game

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, create_cat
from scripts.cat.skills import Skill, SkillPath
from scripts.clan import Clan, Afterlife
from scripts.clan_resources.freshkill import FreshkillPile
from scripts.clan_package.get_clan_cats import get_alive_clan_queens


class FreshkillPileTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clanlist = read_clans()
        cls.previously_loaded_clan = cls.clanlist[0] if cls.clanlist else None

    def setUp(self) -> None:
        self.prey_config = None
        with open("resources/prey_config.toml", "r") as read_file:
            self.prey_config = tomllib.loads(read_file.read())
        self.amount = self.prey_config["start_amount"]
        self.prey_requirement = self.prey_config["prey_requirement"]
        self.condition_increase = self.prey_config["condition_increase"]

        # load in the spritesheets
        # we have to do this to prevent a crash, even though we won't be displaying anything
        sprites.load_all()

        game.starclan = Afterlife()
        game.dark_forest = Afterlife()

        # set up clan members and some helpful lists for us to use later
        self.warriors = [
            create_cat(CatRank.WARRIOR),
            create_cat(CatRank.WARRIOR),
            create_cat(CatRank.WARRIOR),
        ]
        self.apprentices = [
            create_cat(CatRank.APPRENTICE),
            create_cat(CatRank.APPRENTICE),
        ]
        self.elder = create_cat(CatRank.ELDER)
        self.kitten = create_cat(CatRank.KITTEN)

        members = [self.elder, self.kitten]
        members.extend(self.warriors)
        members.extend(self.apprentices)

        self.test_clan_name = f"Test_{uuid4()}"

        game.clan = Clan(
            name=self.test_clan_name,
            displayname="Test",
            leader=create_cat(CatRank.LEADER),
            deputy=create_cat(CatRank.DEPUTY),
            medicine_cat=create_cat(CatRank.MEDICINE_CAT),
            biome="Forest",
            camp_bg="camp1",
            symbol="symbolADDER0",
            game_mode="expanded",
            starting_members=members,
            starting_season="Newleaf",
        )
        save_load.cat_to_fade.clear()
        game.clan.create_clan()

        for _c in Cat.all_cats_list:
            if _c == game.clan.leader:
                # set leader as a hunter skill for later testing
                game.clan.leader.skills.primary = Skill(SkillPath.HUNTER, 25)
            else:
                _c.skills.primary = Skill(SkillPath.CLIMBER, 20)

        # set dep as injured for later testing
        game.clan.deputy.injuries["test_injury"] = {"severity": "major"}

        self.freshkill_pile = game.clan.freshkill_pile
        # fills all cat's nutrition so we have steady baseline
        self.freshkill_pile.update_nutrition(Cat.all_cats_list)

    def tearDown(self):
        rempath = get_save_dir() + "/" + self.test_clan_name
        shutil.rmtree(rempath)
        if os.path.exists(rempath + "clan.json"):
            os.remove(rempath + "clan.json")

    @classmethod
    def tearDownClass(cls):
        if cls.previously_loaded_clan:
            with open(Path(get_save_dir()) / "currentclan.txt", "w") as currentclanfile:
                currentclanfile.write(str(cls.previously_loaded_clan))

    def test_add_freshkill(self) -> None:
        """
        Tests the addition of freshkill
        """
        # given
        freshkill_pile = FreshkillPile()
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

        # then
        freshkill_pile.add_freshkill(1)
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.amount + 1)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

    def test_remove_freshkill(self) -> None:
        """
        Tests freshkill removal
        """
        # given
        freshkill_pile1 = FreshkillPile()
        freshkill_pile1.pile["expires_in_1"] = 10
        self.assertEqual(freshkill_pile1.pile["expires_in_1"], 10)
        freshkill_pile1.remove_freshkill(5)

        freshkill_pile2 = FreshkillPile()
        freshkill_pile2.remove_freshkill(5, True)

        # then
        self.assertEqual(freshkill_pile1.pile["expires_in_4"], self.amount)
        self.assertEqual(freshkill_pile1.pile["expires_in_1"], 5)
        self.assertEqual(freshkill_pile2.total_amount, self.amount - 5)

    def test_time_skip(self) -> None:
        """
        Tests freshkill expiration over time
        """
        # given
        freshkill_pile = FreshkillPile()
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

        # then
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], self.amount)
        freshkill_pile.time_skip([], [])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

    def test_tactic_low_rank(self):
        """
        Tests low rank first tactic. This is also the default tactic, so we'll test this first before changing any clan settings.
        """
        # we'll set the freshkill pile up with enough to feed the kitten and that's all
        current_amount = self.prey_requirement["kitten"]
        self.freshkill_pile.pile["expires_in_4"] = current_amount
        self.freshkill_pile.total_amount = current_amount

        # feed them
        self.freshkill_pile.feed_cats(Cat.all_cats_list)

        # check that kitten is full
        self.assertEqual(
            self.freshkill_pile.nutrition_info[self.kitten.ID].percentage, 100
        )
        # check that everyone else is hungry
        for cat in Cat.all_cats_list:
            if cat == self.kitten:
                continue
            self.assertNotEqual(
                self.freshkill_pile.nutrition_info[cat.ID].percentage, 100
            )

    def test_tactic_high_rank(self):
        """
        Tests high rank first tactic.
        """
        # first we'll reset everyone's nutrition
        for key in self.freshkill_pile.nutrition_info.keys():
            self.freshkill_pile.nutrition_info[key].percentage = 100

        # then set up the pile with enough to feed the leader and that's all
        current_amount = self.prey_requirement["leader"]
        self.freshkill_pile.pile["expires_in_4"] = current_amount
        self.freshkill_pile.total_amount = current_amount

        # set the tactic to high rank
        set_clan_setting("low_rank", False)
        switch_clan_setting("high_rank")

        # feed them
        self.freshkill_pile.feed_cats(Cat.all_cats_list)

        nutrition_status = {
            Cat.fetch_cat(x).status.rank: y.percentage
            for x, y in self.freshkill_pile.nutrition_info.items()
        }

        # check that leader is full
        self.assertEqual(
            self.freshkill_pile.nutrition_info[game.clan.leader.ID].percentage,
            100,
            f"nutrition status: {nutrition_status}",
        )
        # check that everyone else is hungry
        for cat in Cat.all_cats_list:
            if cat == game.clan.leader:
                continue
            self.assertNotEqual(
                self.freshkill_pile.nutrition_info[cat.ID].percentage, 100
            )

    def test_tactic_youngest(self):
        """
        Tests youngest first tactic.
        """
        # first we'll reset everyone's nutrition
        for key in self.freshkill_pile.nutrition_info.keys():
            self.freshkill_pile.nutrition_info[key].percentage = 100

        # then set up the pile with enough to feed the kitten and that's all
        current_amount = self.prey_requirement["kitten"]
        self.freshkill_pile.pile["expires_in_4"] = current_amount
        self.freshkill_pile.total_amount = current_amount

        # set the tactic to youngest
        set_clan_setting("low_rank", False)
        switch_clan_setting("youngest_first")

        # feed them
        self.freshkill_pile.feed_cats(Cat.all_cats_list)

        # check that kitten is full
        self.assertEqual(
            self.freshkill_pile.nutrition_info[self.kitten.ID].percentage, 100
        )
        # check that everyone else is hungry
        for cat in Cat.all_cats_list:
            if cat == self.kitten:
                continue
            self.assertNotEqual(
                self.freshkill_pile.nutrition_info[cat.ID].percentage, 100
            )

    def test_tactic_oldest(self):
        """
        Tests oldest first tactic.
        """
        # first we'll reset everyone's nutrition
        for key in self.freshkill_pile.nutrition_info.keys():
            self.freshkill_pile.nutrition_info[key].percentage = 100

        # then set up the pile with enough to feed the oldest and that's all
        oldest = sorted(Cat.all_cats_list, key=lambda x: x.moons, reverse=True)[0]
        current_amount = self.prey_requirement[oldest.status.rank]
        self.freshkill_pile.pile["expires_in_4"] = current_amount
        self.freshkill_pile.total_amount = current_amount

        # set the tactic to youngest
        set_clan_setting("low_rank", False)
        switch_clan_setting("oldest_first")

        # feed them
        self.freshkill_pile.feed_cats(Cat.all_cats_list)

        # check that elder is full
        self.assertEqual(self.freshkill_pile.nutrition_info[oldest.ID].percentage, 100)
        # check that everyone else is hungry
        for cat in Cat.all_cats_list:
            if cat == oldest:
                continue
            self.assertNotEqual(
                self.freshkill_pile.nutrition_info[cat.ID].percentage, 100
            )

    def test_tactic_experienced(self):
        """
        Tests experienced first tactic.
        """
        # first we'll reset everyone's nutrition
        for key in self.freshkill_pile.nutrition_info.keys():
            self.freshkill_pile.nutrition_info[key].percentage = 100

        # sorting the cats by experience
        list_of_cats = sorted(
            Cat.all_cats_list, key=lambda x: x.experience, reverse=True
        )
        most_exp = list_of_cats[0]
        # then set up the pile with enough to feed the most experienced and that's all
        current_amount = self.prey_requirement[most_exp.status.rank]
        self.freshkill_pile.pile["expires_in_4"] = current_amount
        self.freshkill_pile.total_amount = current_amount

        # set the tactic to experienced
        set_clan_setting("low_rank", False)
        switch_clan_setting("experience_first")

        # feed them
        self.freshkill_pile.feed_cats(Cat.all_cats_list)

        # check that experienced is full
        self.assertEqual(
            self.freshkill_pile.nutrition_info[most_exp.ID].percentage, 100
        )
        # check that everyone else is hungry
        for cat in Cat.all_cats_list:
            if cat == most_exp:
                continue
            self.assertNotEqual(
                self.freshkill_pile.nutrition_info[cat.ID].percentage, 100
            )

    def test_tactic_hungry(self):
        """
        Tests hungry first tactic.
        """
        # first we'll reset everyone's nutrition
        for key in self.freshkill_pile.nutrition_info.keys():
            self.freshkill_pile.nutrition_info[key].percentage = 100

        # then set certain cat's nutrition lower
        self.freshkill_pile.nutrition_info[game.clan.deputy.ID].percentage = 90

        # then set up the pile with enough to feed the deputy and that's all
        current_amount = self.prey_requirement["deputy"]
        self.freshkill_pile.pile["expires_in_4"] = current_amount
        self.freshkill_pile.total_amount = current_amount

        # set the tactic to hungry
        set_clan_setting("low_rank", False)
        switch_clan_setting("hungriest_first")

        # feed them
        self.freshkill_pile.feed_cats(Cat.all_cats_list)

        # check that deputy has eaten (it won't be 100, since we lowered the starting nutrition, but it'll still be higher than we began with
        self.assertGreater(
            self.freshkill_pile.nutrition_info[game.clan.deputy.ID].percentage, 90
        )
        # check that everyone else is hungry
        for cat in Cat.all_cats_list:
            if cat == game.clan.deputy:
                continue
            self.assertNotEqual(
                self.freshkill_pile.nutrition_info[cat.ID].percentage, 100
            )

    def test_priority_hunter(self):
        """
        Tests hunter first priority.
        """
        # first we'll reset everyone's nutrition
        for key in self.freshkill_pile.nutrition_info.keys():
            self.freshkill_pile.nutrition_info[key].percentage = 100

        hunter = game.clan.leader

        # then set up the pile with enough to feed the hunter and that's all
        current_amount = self.prey_requirement["leader"]
        self.freshkill_pile.pile["expires_in_4"] = current_amount
        self.freshkill_pile.total_amount = current_amount

        # set priority to hunter
        switch_clan_setting("hunter_first")
        # what we SHOULD see is the hunter being fed before the low rank (so leader before kitten)

        # feed them
        self.freshkill_pile.feed_cats(Cat.all_cats_list)

        # check that leader is full
        self.assertEqual(self.freshkill_pile.nutrition_info[hunter.ID].percentage, 100)
        # check that everyone else is hungry
        for cat in Cat.all_cats_list:
            if cat == hunter:
                continue
            self.assertNotEqual(
                self.freshkill_pile.nutrition_info[cat.ID].percentage, 100
            )

    def test_priority_injured(self):
        """
        Tests injured first priority.
        """
        # first we'll reset everyone's nutrition
        for key in self.freshkill_pile.nutrition_info.keys():
            self.freshkill_pile.nutrition_info[key].percentage = 100

        injured = game.clan.deputy

        # then set up the pile with enough to feed the injured and that's all
        current_amount = self.prey_requirement["deputy"]
        self.freshkill_pile.pile["expires_in_4"] = current_amount
        self.freshkill_pile.total_amount = current_amount

        # set priority to injured
        switch_clan_setting("sick_injured_first")
        # what we SHOULD see is the injured being fed before the low rank (so dep before kitten)

        # feed them
        self.freshkill_pile.feed_cats(Cat.all_cats_list)

        # check that injured is full
        self.assertEqual(self.freshkill_pile.nutrition_info[injured.ID].percentage, 100)
        # check that everyone else is hungry
        for cat in Cat.all_cats_list:
            if cat == injured:
                continue
            self.assertNotEqual(
                self.freshkill_pile.nutrition_info[cat.ID].percentage, 100
            )

    def test_queen_handling(self) -> None:
        # given
        # young enough kid
        mother = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        mother.gender = "female"
        father = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        father.gender = "male"
        kid = Cat(status_dict={"rank": CatRank.KITTEN}, moons=1, disable_random=True)
        kid.moons = 2
        kid.parent1 = father
        kid.parent2 = mother

        no_parent = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the warrior
        current_amount = self.prey_requirement["queen/pregnant"] + (
            self.prey_requirement["warrior"] / 2
        )
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        freshkill_pile.add_cat_to_nutrition(mother)
        freshkill_pile.add_cat_to_nutrition(father)
        freshkill_pile.add_cat_to_nutrition(kid)
        freshkill_pile.add_cat_to_nutrition(no_parent)
        self.assertEqual(freshkill_pile.nutrition_info[kid.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[mother.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[father.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[no_parent.ID].percentage, 100)

        # when
        living_cats = [no_parent, father, kid, mother]
        self.assertEqual(
            [mother.ID], list(get_alive_clan_queens(living_cats)[0].keys())
        )
        freshkill_pile.feed_cats(living_cats)

        # then
        self.assertEqual(freshkill_pile.nutrition_info[kid.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[mother.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[no_parent.ID].percentage, 90)
        self.assertGreater(freshkill_pile.nutrition_info[no_parent.ID].percentage, 70)
        self.assertLess(freshkill_pile.nutrition_info[father.ID].percentage, 70)

    def test_pregnant_handling(self) -> None:
        # given
        # young enough kid
        pregnant_cat = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        pregnant_cat.injuries["pregnant"] = {"severity": "minor"}
        cat2 = Cat(status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True)
        cat3 = Cat(status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True)

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some of the warrior
        current_amount = self.prey_requirement["queen/pregnant"]
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        freshkill_pile.add_cat_to_nutrition(pregnant_cat)
        freshkill_pile.add_cat_to_nutrition(cat2)
        freshkill_pile.add_cat_to_nutrition(cat3)
        self.assertEqual(freshkill_pile.nutrition_info[pregnant_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[cat2.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[cat3.ID].percentage, 100)

        # when
        freshkill_pile.feed_cats([cat2, cat3, pregnant_cat])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[pregnant_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[cat2.ID].percentage, 70)
        self.assertLess(freshkill_pile.nutrition_info[cat3.ID].percentage, 70)
