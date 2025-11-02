import os
import unittest
import ujson

from scripts.cat.enums import CatRank

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat
from scripts.cat.skills import Skill, SkillPath
from scripts.clan import Clan
from scripts.clan_resources.freshkill import FreshkillPile
from scripts.utility import get_alive_clan_queens


class FreshkillPileTest(unittest.TestCase):
    def setUp(self) -> None:
        self.prey_config = None
        with open("resources/prey_config.json", "r") as read_file:
            self.prey_config = ujson.loads(read_file.read())
        self.amount = self.prey_config["start_amount"]
        self.prey_requirement = self.prey_config["prey_requirement"]
        self.condition_increase = self.prey_config["condition_increase"]
        Cat.all_cats = {}

    def test_add_freshkill(self) -> None:
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

    def test_feed_cats(self) -> None:
        # given
        test_clan = Clan(
            name="Test",
            leader=None,
            deputy=None,
            medicine_cat=None,
            biome="Forest",
            camp_bg=None,
            game_mode="expanded",
            starting_season="Newleaf",
        )
        test_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        test_clan.add_cat(test_warrior)

        # then
        self.assertEqual(test_clan.freshkill_pile.total_amount, self.amount)
        test_clan.freshkill_pile.feed_cats([test_warrior])
        self.assertEqual(
            test_clan.freshkill_pile.total_amount,
            self.amount - self.prey_requirement["warrior"],
        )

    def test_tactic_younger_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.prey_requirement["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        youngest_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        youngest_warrior.moons = 20
        middle_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        middle_warrior.moons = 30
        oldest_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        oldest_warrior.moons = 40

        freshkill_pile.add_cat_to_nutrition(youngest_warrior)
        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        freshkill_pile.add_cat_to_nutrition(oldest_warrior)
        self.assertEqual(
            freshkill_pile.nutrition_info[youngest_warrior.ID].percentage, 100
        )
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100
        )
        self.assertEqual(
            freshkill_pile.nutrition_info[oldest_warrior.ID].percentage, 100
        )

        # when
        freshkill_pile.tactic_younger_first(
            [oldest_warrior, middle_warrior, youngest_warrior]
        )

        # then
        self.assertEqual(
            freshkill_pile.nutrition_info[youngest_warrior.ID].percentage, 100
        )
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100
        )
        self.assertNotEqual(
            freshkill_pile.nutrition_info[oldest_warrior.ID].percentage, 100
        )

    def test_tactic_less_nutrition_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.prey_requirement["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        lowest_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        lowest_warrior.moons = 20
        middle_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        middle_warrior.moons = 30
        highest_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        highest_warrior.moons = 40

        freshkill_pile.add_cat_to_nutrition(lowest_warrior)
        max_score = freshkill_pile.nutrition_info[lowest_warrior.ID].max_score
        give_score = max_score - self.prey_requirement["warrior"]
        freshkill_pile.nutrition_info[lowest_warrior.ID].current_score = give_score

        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        give_score = max_score - (self.prey_requirement["warrior"] / 2)
        freshkill_pile.nutrition_info[middle_warrior.ID].current_score = give_score

        freshkill_pile.add_cat_to_nutrition(highest_warrior)
        self.assertLessEqual(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 70
        )
        self.assertLessEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 90
        )
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100
        )

        # when
        living_cats = [highest_warrior, middle_warrior, lowest_warrior]
        freshkill_pile.living_cats = living_cats
        freshkill_pile.tactic_less_nutrition_first(living_cats)

        # then
        self.assertEqual(freshkill_pile.total_amount, 0)
        self.assertGreaterEqual(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 60
        )
        self.assertGreaterEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 80
        )
        self.assertLess(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 70
        )

    def test_tactic_sick_injured_first(self) -> None:
        # given
        # young enough kid
        injured_cat = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        injured_cat.injuries["test_injury"] = {"severity": "major"}
        sick_cat = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        sick_cat.illnesses["test_illness"] = {"severity": "major"}
        healthy_cat = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some warriors
        current_amount = self.prey_requirement["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        freshkill_pile.add_cat_to_nutrition(injured_cat)
        freshkill_pile.add_cat_to_nutrition(sick_cat)
        freshkill_pile.add_cat_to_nutrition(healthy_cat)
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 100)

        # when
        freshkill_pile.tactic_sick_injured_first([healthy_cat, sick_cat, injured_cat])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 70)

    def test_more_experience_first(self) -> None:
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.prey_requirement["warrior"]
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        lowest_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        lowest_warrior.experience = 20
        middle_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        middle_warrior.experience = 30
        highest_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        highest_warrior.experience = 40

        freshkill_pile.add_cat_to_nutrition(lowest_warrior)
        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        freshkill_pile.add_cat_to_nutrition(highest_warrior)
        self.assertEqual(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 100
        )
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100
        )
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100
        )

        # when
        freshkill_pile.tactic_more_experience_first(
            [lowest_warrior, middle_warrior, highest_warrior]
        )

        # then
        # self.assertEqual(freshkill_pile.total_amount,0)
        self.assertLess(freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 70)
        self.assertLess(freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 90)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100
        )

    def test_hunter_first(self) -> None:
        # check also different ranks of hunting skill
        # given
        freshkill_pile = FreshkillPile()
        current_amount = self.prey_requirement["warrior"] + (
            self.prey_requirement["warrior"] / 2
        )
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        best_hunter_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        best_hunter_warrior.skills.primary = Skill(SkillPath.HUNTER, 25)
        self.assertEqual(best_hunter_warrior.skills.primary.tier, 3)
        hunter_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        hunter_warrior.skills.primary = Skill(SkillPath.HUNTER, 0)
        self.assertEqual(hunter_warrior.skills.primary.tier, 1)
        no_hunter_warrior = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        no_hunter_warrior.skills.primary = Skill(SkillPath.MEDIATOR, 0, True)

        freshkill_pile.add_cat_to_nutrition(best_hunter_warrior)
        freshkill_pile.add_cat_to_nutrition(hunter_warrior)
        freshkill_pile.add_cat_to_nutrition(no_hunter_warrior)
        self.assertEqual(
            freshkill_pile.nutrition_info[best_hunter_warrior.ID].percentage, 100
        )
        self.assertEqual(
            freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 100
        )
        self.assertEqual(
            freshkill_pile.nutrition_info[no_hunter_warrior.ID].percentage, 100
        )

        # when
        living_cats = [hunter_warrior, no_hunter_warrior, best_hunter_warrior]
        freshkill_pile.tactic_hunter_first(living_cats)

        # then
        # this hunter should be fed completely
        self.assertEqual(
            freshkill_pile.nutrition_info[best_hunter_warrior.ID].percentage, 100
        )
        # this hunter should be fed partially
        self.assertLess(freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 90)
        self.assertGreater(
            freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 70
        )
        # this cat should not be fed
        self.assertLess(
            freshkill_pile.nutrition_info[no_hunter_warrior.ID].percentage, 70
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
        freshkill_pile.tactic_status(living_cats)

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

    def test_sick_handling(self) -> None:
        # given
        # young enough kid
        injured_cat = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        injured_cat.injuries["claw-wound"] = {"severity": "major"}
        sick_cat = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )
        sick_cat.illnesses["diarrhea"] = {"severity": "major"}
        healthy_cat = Cat(
            status_dict={"rank": CatRank.WARRIOR}, moons=1, disable_random=True
        )

        freshkill_pile = FreshkillPile()
        # be able to feed one queen and some warriors
        current_amount = self.prey_requirement["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        freshkill_pile.add_cat_to_nutrition(injured_cat)
        freshkill_pile.add_cat_to_nutrition(sick_cat)
        freshkill_pile.add_cat_to_nutrition(healthy_cat)
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 100)

        # when
        freshkill_pile.tactic_sick_injured_first([sick_cat, injured_cat, healthy_cat])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[injured_cat.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[sick_cat.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[healthy_cat.ID].percentage, 70)
