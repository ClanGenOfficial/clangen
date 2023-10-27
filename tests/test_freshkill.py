import unittest
import ujson
from scripts.cat.cats import Cat
from scripts.clan import Clan
from scripts.clan_resources.freshkill import Freshkill_Pile


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
        # check with and without random
        pass

    def test_time_skip(self) -> None:
        # given
        freshkill_pile = Freshkill_Pile()
        self.assertEqual(freshkill_pile.pile["expires_in_4"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)

        # then
        freshkill_pile.time_skip([],[])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)
        freshkill_pile.time_skip([],[])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], self.amount)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], 0)
        freshkill_pile.time_skip([],[])
        self.assertEqual(freshkill_pile.pile["expires_in_4"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_3"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_2"], 0)
        self.assertEqual(freshkill_pile.pile["expires_in_1"], self.amount)
        freshkill_pile.time_skip([],[])
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
                 starting_season='Newleaf'
        )
        test_warrior = Cat()
        test_warrior.status = "warrior"
        test_clan.add_cat(test_warrior)

        # then
        self.assertEqual(test_clan.freshkill_pile.total_amount, self.amount)
        test_clan.freshkill_pile.feed_cats([test_warrior])
        self.assertEqual(test_clan.freshkill_pile.total_amount, self.amount - self.prey_requirement["warrior"])

    def test_amount_food_needed(self) -> None:
        # given
        freshkill_pile = Freshkill_Pile()
        test_warrior = Cat()
        test_warrior.status = "warrior"

        # then
        self.assertEqual(freshkill_pile.amount_food_needed(), self.prey_requirement["warrior"])

    def test_clan_has_enough_food(self) -> None:
        pass

    def test_tactic_younger_first(self) -> None:
        pass

    def test_tactic_less_nutrition_first(self) -> None:
        pass

    def test_more_experience_first(self) -> None:
        pass

    def test_hunter_first(self) -> None:
        # check also different ranks of hunting skill
        pass

    def test_queen_handling(self) -> None:
        pass

    def test_sick_handling(self) -> None:
        pass

    def test_update_nutrition(self) -> None:
        pass

    def test_add_cat_to_nutrition(self) -> None:
        pass
