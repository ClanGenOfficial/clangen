import random
from copy import deepcopy, copy
from typing import List

from scripts.cat.cats import Cat
from scripts.cat.nutrition import Nutrition
from scripts.cat.skills import SkillPath
from scripts.game_structure.game_essentials import game
from scripts.utility import get_alive_clan_queens


class FreshkillPile:
    """Handle everything related to the freshkill pile of the clan."""

    def __init__(self, pile: dict = None) -> None:
        """
        Initialize the class.

            Parameters
            ----------
            pile : dict
                the dictionary of the loaded pile from files
        """
        # the pile could be handled as a list but this makes it more readable
        if pile:
            self.pile = pile
        else:
            self.pile = {
                "expires_in_4": game.prey_config["start_amount"],
                "expires_in_3": 0,
                "expires_in_2": 0,
                "expires_in_1": 0,
            }
        self.living_cats = []
        self.already_fed = []
        self.needed_prey = 0

    def add_freshkill(self, amount) -> None:
        """
        Add new fresh kill to the pile.

            Parameters
            ----------
            amount : int|float
                the amount which should be added to the pile
        """
        self.pile["expires_in_4"] += amount

    def remove_freshkill(self, amount, take_random: bool = False) -> int:
        """
        Remove a certain amount of fresh kill from the pile.

            Parameters
            ----------
            amount : int|float
                the amount which should be removed from the pile
            take_random : bool
                if it should be taken from the different sub-piles or not
        """
        if amount == 0:
            return 0
        order = ["expires_in_1", "expires_in_2", "expires_in_3", "expires_in_4"]
        if take_random:
            random.shuffle(order)
        for key in order:
            amount = self.take_from_pile(key, amount)
        return amount

    @property
    def total_amount(self):
        return round(sum(self.pile.values()), 2)

    def _update_needed_food(self, living_cats: List[Cat]) -> None:
        # handle kits and queens
        clan_cats = self.handle_kits_and_queens(living_cats)

        # all normal status cats calculation
        needed_prey = sum(
            [
                PREY_REQUIREMENT[cat.status]
                for cat in living_cats
                if cat.status
                not in ["kittypet", "rogue", "loner", "exiled", "former Clancat"]
                and not cat.outside
            ]
        )
        # increase the number for sick cats
        if game.clan and game.clan.game_mode == "cruel season":
            sick_cats = [
                cat
                for cat in living_cats
                if cat.not_working() and "pregnant" not in cat.injuries
            ]
            needed_prey += len(sick_cats) * CONDITION_INCREASE
        # increase the number of prey which are missing for relevant queens and pregnant cats
        pregnancy_bonus_prey = (
            PREY_REQUIREMENT["queen/pregnant"] - PREY_REQUIREMENT["warrior"]
        )
        needed_prey += (
            len([cat for cat in clan_cats.values() if cat.status == "queen/pregnant"])
        ) * pregnancy_bonus_prey

        # increase the number of prey for kits, which are not taken care by a queen
        needed_prey += sum(
            [
                PREY_REQUIREMENT[cat.status]
                for cat in living_cats
                if not cat.outside
                and (cat.status == "kitten" or cat.status == "newborn")
                and cat.ID not in clan_cats
            ]
        )

        self.needed_prey = needed_prey

    def time_skip(self, hungry_cats: list, event_list: list) -> None:
        """Handles the time skip for the freshkill pile. Decrements the timers on prey items and feeds listed cats

        :param list hungry_cats: living cats which should be fed
        :param list event_list: the current freshkill moonskip event list
        """

        if (
            not FRESHKILL_ACTIVE
        ):  # we aren't running freshkill things this game, we leave immediately
            return

        self.living_cats = hungry_cats
        previous_amount = 0

        # update the freshkill pile - move every piece forward one moon & discard any excess
        for key, value in self.pile.items():
            self.pile[key] = previous_amount
            previous_amount = value
            if key == "expires_in_1" and value > 0:
                amount = round(value, 2)
                event_list.append(
                    f"Some prey expired, {amount} pieces were removed from the pile."
                )

        value_diff = self.total_amount
        self.prepare_feed_cats(self.living_cats)
        self.already_fed = []
        value_diff -= self.total_amount
        event_list.append(f"{value_diff} pieces of prey were consumed.")
        self._update_needed_food(hungry_cats)

    def prepare_feed_cats(self, living_cats: list, additional_food_round=False) -> None:
        """Feed all living clan cats. This runs before aging up.

        Parameters
        ----------
        :param list living_cats: list of living cats which should be fed
        :param additional_food_round: Whether this is a manual feeding from the freshkill pile, default False
        """
        Nutrition.update_nutrition(living_cats)

        # NOTE: this is for testing purposes
        if not game.clan:
            clan_cats = self.sort_cats(living_cats, ["status", "id"])
            self.feed_group(clan_cats, additional_food_round)
            return

        if game.clan.clan_settings["younger first"]:
            clan_cats = self.sort_cats(living_cats, ["moons", "id"])
        elif game.clan.clan_settings["less nutrition first"]:
            clan_cats = self.sort_cats(
                living_cats, ["nutrition", "status", "moons", "id"]
            )
        elif game.clan.clan_settings["more experience first"]:
            clan_cats = self.sort_cats(
                living_cats, ["experience", "status", "moons", "id"]
            )
        elif game.clan.clan_settings["hunter first"]:
            clan_cats = self.sort_cats(living_cats, ["hunter", "status", "moons", "id"])
        elif game.clan.clan_settings["sick/injured first"]:
            clan_cats = self.sort_cats(living_cats, ["sick", "status", "moons", "id"])
        elif game.clan.clan_settings["by-status"]:
            clan_cats = self.sort_cats(living_cats, ["status", "moons", "id"])
        else:
            clan_cats = self.sort_cats(living_cats, ["status", "moons", "id"])

        self.feed_group(clan_cats, additional_food_round)

    def amount_food_needed(self):
        """Get the amount of freshkill the clan needs.

        :return int|float needed_prey: The amount of prey the Clan needs
        """
        living_cats = [
            cat
            for cat in Cat.all_cats.values()
            if not (cat.dead or cat.outside or cat.exiled)
        ]
        self._update_needed_food(living_cats)
        return self.needed_prey

    def clan_has_enough_food(self) -> bool:
        """Check if the amount of the prey is enough for one moon

        :return bool: True if there is enough food
        """
        return self.amount_food_needed() <= self.total_amount

    # ---------------------------------------------------------------------------- #
    #                               helper functions                               #
    # ---------------------------------------------------------------------------- #

    def feed_group(self, group: list, additional_food_round=False) -> None:
        """Feed a group of cats.

        :param list group: Cats to feed
        :param bool additional_food_round: Determines if not player-initiated, default False
        """
        if len(group) == 0:
            return

        # first split nutrition information into low nutrition and satisfied
        ration_prey = game.clan.clan_settings["ration prey"] if game.clan else False

        # Feed according to hierarchy
        for cat in group:
            if cat in self.already_fed:
                continue

            feeding_amount, needed_amount = self.determine_portion(
                cat, ration_prey, additional_food_round
            )
            self.feed_one_cat(cat, feeding_amount, needed_amount)

    def feed_one_cat(self, cat: Cat, feeding_amount, needed_amount) -> None:
        """
        Handle the feeding process.

            Parameters
            ----------
            cat : Cat
                the cat to feed
            feeding_amount : int|float
                Allocated amount of food
            needed_amount : int|float
                Amount cat needs to maintain nutrition level for this moon
        """

        ration = game.clan.clan_settings["ration prey"] if game.clan else False
        remaining_amount = copy(feeding_amount)
        amount_difference = needed_amount - feeding_amount

        remaining_amount = self.remove_freshkill(remaining_amount)
        self.already_fed.append(cat)

        couldnt_get_full_portion = remaining_amount > 0 and amount_difference == 0
        able_to_eat_full_portion = remaining_amount == 0
        extra_portion = needed_amount == 0
        given_more_than_needed = feeding_amount > needed_amount

        if couldnt_get_full_portion:
            # decrement current_score by the amount of prey they missed out on
            cat.nutrition.current_score -= remaining_amount
        elif able_to_eat_full_portion:
            if extra_portion:  # if this is a top-up feeding
                cat.nutrition.current_score += feeding_amount
            elif given_more_than_needed:
                cat.nutrition.current_score += feeding_amount - needed_amount
            # If neither of these are true, then the satiety stays the same
        elif ration and cat.status == "warrior" and needed_amount != 0:
            feeding_amount = PREY_REQUIREMENT[cat.status] / 2
            cat.nutrition.current_score -= feeding_amount

    def take_from_pile(self, pile_group: str, given_amount):
        """
        Take the amount from a specific pile group and returns the rest of the original needed amount.

            Parameters
            ----------
            pile_group : str
                the name of the pile group
            given_amount : int|float
                the amount which should be consumed

            Returns
            ----------
            remaining_amount : int|float
                the amount which could not be consumed from the given pile group
        """
        if given_amount == 0:
            return given_amount

        remaining_amount = given_amount
        if self.pile[pile_group] >= given_amount:
            self.pile[pile_group] -= given_amount
            remaining_amount = 0
        elif self.pile[pile_group] > 0:
            remaining_amount = given_amount - self.pile[pile_group]
            self.pile[pile_group] = 0

        return remaining_amount

    def determine_portion(self, cat, ration_prey=False, additional_food_round=False):
        feeding_amount = cat.nutrition.needed_per_moon
        needed_amount = copy(feeding_amount)

        # check for condition
        if "pregnant" not in cat.injuries and cat.not_working():
            if game.clan and game.clan.game_mode == "cruel season":
                feeding_amount += CONDITION_INCREASE
                needed_amount = feeding_amount
        else:
            if ration_prey and cat.status == "warrior":
                feeding_amount = feeding_amount / 2

        if cat.nutrition.percentage == 100:
            if additional_food_round:
                needed_amount = 0
            return feeding_amount, needed_amount

        if self.total_amount * 2 > self.amount_food_needed():
            feeding_amount += 2

        elif self.total_amount * 1.8 > self.amount_food_needed():
            feeding_amount += 1.5

        elif self.total_amount * 1.2 > self.amount_food_needed():
            feeding_amount += 1

        elif self.total_amount > self.amount_food_needed():
            feeding_amount += 0.5

        if additional_food_round:
            needed_amount = 0
        return feeding_amount, needed_amount

    @staticmethod
    def handle_kits_and_queens(living_cats):
        clan_cats = {cat.ID: cat for cat in deepcopy(living_cats)}
        """Dict with key : value of cat.ID : cat"""

        # find queens & pregnant cats IDs to set their status to queen/pregnant
        queen_dict, kits = get_alive_clan_queens(living_cats)
        # kits under 3 months are fed by the queen
        for queen_id, their_kits in queen_dict.items():
            young_kits = [kit.ID for kit in their_kits if kit.moons < 3]
            if (
                len(young_kits) != 0
            ):  # if kits exist, set the family's food requirements appropriately
                for key in young_kits:
                    clan_cats.pop(
                        key
                    )  # remove the kits from the list, we don't need them where we're going
                clan_cats[queen_id].status = "queen/pregnant"
        # doing the same for the catermelons
        catermelons = [cat.ID for cat in living_cats if "pregnant" in cat.injuries]
        if len(catermelons) != 0:
            for sliced_catermelon in catermelons:
                clan_cats[sliced_catermelon].status = "queen/pregnant"

        return clan_cats

    @staticmethod
    def sort_cats(clan_cats: list, sort_order: list) -> list:
        if sort_order is None:
            sort_order = ["status", "moons"]

        # invert the order of filters, so we can apply them in the right order
        sort_order.reverse()

        # To ensure the cats are in a guaranteed, repeatable order
        output = clan_cats.copy()
        output.sort(key=lambda cat: int(cat.ID))

        for sort in sort_order:
            if sort == "status":
                output.sort(key=lambda cat: FEEDING_ORDER.index(cat.status))
            elif sort == "moons":
                output.sort(key=lambda cat: cat.moons)
            elif sort == "nutrition":
                output.sort(key=lambda cat: cat.nutrition.percentage)
                continue
            elif sort == "experience":
                output.sort(key=lambda cat: cat.experience, reverse=True)
                continue
            elif sort == "hunter":
                output.sort(
                    key=lambda cat: FreshkillPile.sort_hunter(cat), reverse=True
                )
                continue
            elif sort == "sick":
                output.sort(key=lambda cat: FreshkillPile.sort_sick(cat), reverse=True)
                continue
            elif sort == "id":
                output.sort(key=lambda cat: int(cat.ID))
                continue
            else:
                continue
        return output

    @staticmethod
    def sort_hunter(cat):
        if not cat.skills:
            return 0
        if cat.skills.primary and cat.skills.primary.path == SkillPath.HUNTER:
            return cat.skills.primary.tier
        elif cat.skills.secondary and cat.skills.secondary.path == SkillPath.HUNTER:
            return cat.skills.secondary.tier
        else:
            return 0

    @classmethod
    def sort_sick(cls, cat):
        """If a cat is unfortunate enough to be riddled with multiple things, their priority will be higher."""
        priority = 0
        if len(cat.injuries) > 0:
            for injury in cat.injuries.values():
                priority += cls.sick_priority(injury)
        # elif len(cat.injuries) == 1:
        #     priority += cls.sick_priority(cat.injuries)

        if len(cat.illnesses) > 0:
            for illness in cat.illnesses.values():
                priority += cls.sick_priority(illness)
        # elif len(cat.illnesses) == 1:
        #     priority += cls.sick_priority(cat.illnesses[1])

        return priority

    @staticmethod
    def sick_priority(ailment) -> int:
        if ailment["severity"] == "major":
            priority = 2
        elif ailment["severity"] == "minor":
            priority = 1
        else:
            priority = 0
        return priority


# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #


ADDITIONAL_PREY = game.prey_config["additional_prey"]
PREY_REQUIREMENT = game.prey_config["prey_requirement"]
CONDITION_INCREASE = game.prey_config["condition_increase"]
FEEDING_ORDER = game.prey_config["feeding_order"]
HUNTER_BONUS = game.prey_config["hunter_bonus"]
HUNTER_EXP_BONUS = game.prey_config["hunter_exp_bonus"]
FRESHKILL_EVENT_TRIGGER_FACTOR = game.prey_config["base_event_trigger_factor"]
EVENT_WEIGHT_TYPE = game.prey_config["events_weights"]
MAL_PERCENTAGE = game.prey_config["nutrition_malnourished_percentage"]
STARV_PERCENTAGE = game.prey_config["nutrition_starving_percentage"]

FRESHKILL_ACTIVE = game.prey_config["activate_death"]
FRESHKILL_EVENT_ACTIVE = game.prey_config["activate_events"]
