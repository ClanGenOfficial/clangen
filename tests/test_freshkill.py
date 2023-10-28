import unittest
import ujson
from scripts.cat.cats import Cat
from scripts.cat.skills import Skill, SkillPath
from scripts.clan import Clan
from scripts.clan_resources.freshkill import Freshkill_Pile
from scripts.utility import get_alive_clan_queens


class FreshkillPile(unittest.TestCase):

    def setUp(self) -> None:
        self.prey_config = None
        with open("resources/prey_config.json", 'r') as read_file:
            self.prey_config = ujson.loads(read_file.read())
        self.amount = self.prey_config["start_amount"]
        self.prey_requirement = self.prey_config["prey_requirement"]
        return super().setUp()

    def test_add_freshkill(self) -> None:
        # given
        freshkill_pile = Freshkill_Pile()
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
        freshkill_pile1 = Freshkill_Pile()
        freshkill_pile1.pile["expires_in_1"] = 10
        self.assertEqual(freshkill_pile1.pile["expires_in_1"], 10)
        freshkill_pile1.remove_freshkill(5)

        freshkill_pile2 = Freshkill_Pile()
        freshkill_pile2.remove_freshkill(5, True)

        # then
        self.assertEqual(freshkill_pile1.pile["expires_in_4"], self.amount)
        self.assertEqual(freshkill_pile1.pile["expires_in_1"], 5)
        self.assertEqual(freshkill_pile2.total_amount, self.amount - 5)

    def test_time_skip(self) -> None:
        # given
        freshkill_pile = Freshkill_Pile()
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
        test_clan = Clan(name="Test",
                         leader=None,
                         deputy=None,
                         medicine_cat=None,
                         biome='Forest',
                         camp_bg=None,
                         game_mode='expanded',
                         starting_members=[],
                         starting_season='Newleaf')
        test_warrior = Cat()
        test_warrior.status = "warrior"
        test_clan.add_cat(test_warrior)

        # then
        self.assertEqual(test_clan.freshkill_pile.total_amount, self.amount)
        test_clan.freshkill_pile.feed_cats([test_warrior])
        self.assertEqual(test_clan.freshkill_pile.total_amount,
                         self.amount - self.prey_requirement["warrior"])

    def test_amount_food_needed(self) -> None:
        # given
        freshkill_pile = Freshkill_Pile()
        test_warrior = Cat()
        test_warrior.status = "warrior"

        # then
        self.assertEqual(freshkill_pile.amount_food_needed(),
                         self.prey_requirement["warrior"])

    def test_clan_has_enough_food(self) -> None:
        # given
        freshkill_pile1 = Freshkill_Pile()
        freshkill_pile2 = Freshkill_Pile()
        freshkill_pile2.pile["expires_in_4"] = 0
        freshkill_pile2.total_amount = 0
        test_warrior = Cat()
        test_warrior.status = "warrior"

        # then
        self.assertTrue(freshkill_pile1.clan_has_enough_food())
        self.assertFalse(freshkill_pile2.clan_has_enough_food())

    def test_tactic_younger_first(self) -> None:
        # given
        freshkill_pile = Freshkill_Pile()
        current_amount = self.prey_requirement["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        youngest_warrior = Cat()
        youngest_warrior.status = "warrior"
        youngest_warrior.moons = 20
        middle_warrior = Cat()
        middle_warrior.status = "warrior"
        middle_warrior.moons = 30
        oldest_warrior = Cat()
        oldest_warrior.status = "warrior"
        oldest_warrior.moons = 40

        freshkill_pile.add_cat_to_nutrition(youngest_warrior)
        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        freshkill_pile.add_cat_to_nutrition(oldest_warrior)
        self.assertEqual(
            freshkill_pile.nutrition_info[youngest_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[oldest_warrior.ID].percentage, 100)

        # when
        freshkill_pile.tactic_younger_first(
            [oldest_warrior, middle_warrior, youngest_warrior], "warrior")

        # then
        self.assertEqual(
            freshkill_pile.nutrition_info[youngest_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100)
        self.assertNotEqual(
            freshkill_pile.nutrition_info[oldest_warrior.ID].percentage, 100)

    def test_tactic_less_nutrition_first(self) -> None:
        # given
        freshkill_pile = Freshkill_Pile()
        current_amount = self.prey_requirement["warrior"] * 2
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        lowest_warrior = Cat()
        lowest_warrior.status = "warrior"
        lowest_warrior.moons = 20
        middle_warrior = Cat()
        middle_warrior.status = "warrior"
        middle_warrior.moons = 30
        highest_warrior = Cat()
        highest_warrior.status = "warrior"
        highest_warrior.moons = 40

        freshkill_pile.add_cat_to_nutrition(lowest_warrior)
        max_score = freshkill_pile.nutrition_info[lowest_warrior.ID].max_score
        freshkill_pile.nutrition_info[
            lowest_warrior.
            ID].current_score = max_score - self.prey_requirement["warrior"]
        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        freshkill_pile.nutrition_info[
            middle_warrior.ID].current_score = max_score - (
                self.prey_requirement["warrior"] / 2)
        freshkill_pile.add_cat_to_nutrition(highest_warrior)
        self.assertLessEqual(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 70)
        self.assertLessEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 90)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100)

        # when
        freshkill_pile.tactic_less_nutrition_first(
            [highest_warrior, middle_warrior, lowest_warrior], "warrior")

        # then
        #self.assertEqual(freshkill_pile.total_amount,0)
        self.assertGreater(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 70)
        self.assertGreater(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 90)
        self.assertLess(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100)

    def test_more_experience_first(self) -> None:
        # given
        freshkill_pile = Freshkill_Pile()
        current_amount = self.prey_requirement["warrior"]
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        lowest_warrior = Cat()
        lowest_warrior.status = "warrior"
        lowest_warrior.experience = 20
        middle_warrior = Cat()
        middle_warrior.status = "warrior"
        middle_warrior.experience = 30
        highest_warrior = Cat()
        highest_warrior.status = "warrior"
        highest_warrior.experience = 40

        freshkill_pile.add_cat_to_nutrition(lowest_warrior)
        freshkill_pile.add_cat_to_nutrition(middle_warrior)
        freshkill_pile.add_cat_to_nutrition(highest_warrior)
        self.assertEqual(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100)

        # when
        freshkill_pile.tactic_more_experience_first(
            [lowest_warrior, middle_warrior, highest_warrior], "warrior")

        # then
        #self.assertEqual(freshkill_pile.total_amount,0)
        self.assertLess(
            freshkill_pile.nutrition_info[lowest_warrior.ID].percentage, 70)
        self.assertLess(
            freshkill_pile.nutrition_info[middle_warrior.ID].percentage, 90)
        self.assertEqual(
            freshkill_pile.nutrition_info[highest_warrior.ID].percentage, 100)

    def test_hunter_first(self) -> None:
        # check also different ranks of hunting skill
        # given
        freshkill_pile = Freshkill_Pile()
        current_amount = self.prey_requirement["warrior"] * 1.8
        freshkill_pile.pile["expires_in_4"] = current_amount
        freshkill_pile.total_amount = current_amount

        excellent_hunter_warrior = Cat()
        excellent_hunter_warrior.status = "warrior"
        excellent_hunter_warrior.skills.primary = Skill(SkillPath.HUNTER, 25)
        hunter_warrior = Cat()
        hunter_warrior.status = "warrior"
        hunter_warrior.skills.primary = Skill(SkillPath.HUNTER, 0)
        no_hunter_warrior = Cat()
        no_hunter_warrior.status = "warrior"
        hunter_warrior.skills.primary = Skill(SkillPath.MEDIATOR, 0, True)

        freshkill_pile.add_cat_to_nutrition(excellent_hunter_warrior)
        freshkill_pile.add_cat_to_nutrition(hunter_warrior)
        freshkill_pile.add_cat_to_nutrition(no_hunter_warrior)
        self.assertEqual(
            freshkill_pile.nutrition_info[
                excellent_hunter_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 100)
        self.assertEqual(
            freshkill_pile.nutrition_info[no_hunter_warrior.ID].percentage, 100)

        # when
        freshkill_pile.tactic_more_experience_first(
            [excellent_hunter_warrior, hunter_warrior, no_hunter_warrior],
            "warrior")

        # then
        self.assertEqual(
            freshkill_pile.nutrition_info[
                excellent_hunter_warrior.ID].percentage, 100) # this hunter should be fed completely
        self.assertLess(
            freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 90) # this hunter should be fed partially
        self.assertGreater(
            freshkill_pile.nutrition_info[hunter_warrior.ID].percentage, 70)
        self.assertLess(
            freshkill_pile.nutrition_info[no_hunter_warrior.ID].percentage, 70) # this cat should not be fed

    def test_queen_handling(self) -> None:
        # given
        # young enough kid
        mother = Cat()
        mother.gender = "female"
        mother.status = "warrior"
        father = Cat()
        father.gender = "male"
        father.status = "warrior"
        kid = Cat()
        kid.status = "kitten"
        kid.moons = 2
        kid.parent1 = father
        kid.parent2 = mother

        no_parent = Cat()
        no_parent.status = "warrior"

        freshkill_pile = Freshkill_Pile()
        # be able to feed one queen and some of the warrior
        current_amount = self.prey_requirement["queen/pregnant"] + (self.prey_requirement["warrior"] / 2)
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
        self.assertEqual([mother.ID], list(get_alive_clan_queens(Cat)[0].keys()))
        freshkill_pile.feed_cats([no_parent, father, kid, mother])

        # then
        self.assertEqual(freshkill_pile.nutrition_info[kid.ID].percentage, 100)
        self.assertEqual(freshkill_pile.nutrition_info[mother.ID].percentage, 100)
        self.assertLess(freshkill_pile.nutrition_info[no_parent.ID].percentage, 90)
        self.assertLess(freshkill_pile.nutrition_info[father.ID].percentage, 70)

    def test_pregnant_handling(self) -> None:
        pass

    def test_sick_handling(self) -> None:
        pass

    def test_update_nutrition(self) -> None:
        pass

    def test_add_cat_to_nutrition(self) -> None:
        pass
