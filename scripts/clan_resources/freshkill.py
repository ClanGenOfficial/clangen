import random
from copy import deepcopy
from typing import List

from scripts.cat.cats import Cat
from scripts.cat.skills import SkillPath
from scripts.game_structure.game_essentials import game
from scripts.utility import get_alive_clan_queens


class Nutrition:
    """All the information about nutrition from one cat."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.max_score = 1
        self.current_score = 0

    def __str__(self):
        this_is_a_dict_not_a_string = {
            "max_score": self.max_score,
            "current_score": self.current_score,
            "percentage": self.percentage,
            "nutrition_text": self.nutrition_text,
        }
        return str(this_is_a_dict_not_a_string)

    @property
    def current_score(self):
        return self._current_score

    @current_score.setter
    def current_score(self, value) -> None:
        """Sets the current_score

        :param int|float value: value to set current_score to
        """
        if value > self.max_score:
            value = self.max_score
        if value < 0:
            value = 0
        self._current_score = value

    @property
    def percentage(self):
        return self._current_score / self.max_score * 100

    @property
    def nutrition_text(self):
        text_config = game.prey_config["text_nutrition"]
        nutrition_text = text_config["text"][0]
        for index in range(len(text_config["lower_range"])):
            if self.percentage >= text_config["lower_range"][index]:
                nutrition_text = text_config["text"][index]
        return nutrition_text

    @property
    def is_low_nutrition(self):
        return self.percentage < 100


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
        self.nutrition_info = {}
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

    def remove_freshkill(self, amount, take_random: bool = False) -> int | None:
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
        queen_dict, living_kits = get_alive_clan_queens(living_cats)
        relevant_queens = []
        # kits under 3 months are feed by the queen
        for queen_id, their_kits in queen_dict.items():
            queen = Cat.fetch_cat(queen_id)
            if queen and (queen.outside or queen.status == "exiled"):
                continue
            young_kits = [kit for kit in their_kits if kit.moons < 3]
            if len(young_kits) > 0:
                relevant_queens.append(queen)
        pregnant_cats = [
            cat
            for cat in living_cats
            if "pregnant" in cat.injuries
               and cat.ID not in queen_dict.keys()
               and not cat.outside
               and cat.status != "exiled"
        ]

        # all normal status cats calculation
        needed_prey = sum(
            [
                PREY_REQUIREMENT[cat.status]
                for cat in living_cats
                if cat.status not in ["newborn", "kitten", "exiled"] and not cat.outside
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
        needed_prey += (len(relevant_queens) + len(pregnant_cats)) * (
                PREY_REQUIREMENT["queen/pregnant"] - PREY_REQUIREMENT["warrior"]
        )
        # increase the number of prey for kits, which are not taken care by a queen
        needed_prey += sum(
            [PREY_REQUIREMENT[cat.status] for cat in living_kits if not cat.outside]
        )

        self.needed_prey = needed_prey

    def time_skip(self, living_cats: list, event_list: list) -> None:
        """Handles the time skip for the freshkill pile. Decrements the timers on prey items and feeds listed cats

        :param list living_cats: living cats which should be fed
        :param list event_list: the current moonskip event list
        """
        self.living_cats = living_cats
        previous_amount = 0
        # update the freshkill pile
        for key, value in self.pile.items():
            self.pile[key] = previous_amount
            previous_amount = value
            if key == "expires_in_1" and FRESHKILL_ACTIVE and value > 0:
                amount = round(value, 2)
                event_list.append(
                    f"Some prey expired, {amount} pieces were removed from the pile."
                )
        value_diff = self.total_amount
        self.already_fed = []
        self.feed_cats(living_cats)
        self.already_fed = []
        value_diff -= self.total_amount
        event_list.append(f"{value_diff} pieces of prey were consumed.")
        self._update_needed_food(living_cats)

    def feed_cats(self, living_cats: list, additional_food_round=False) -> None:
        """
        Handles to feed all living clan cats. This happens before the aging up.

            Parameters
            ----------
            :param list living_cats: list of living cats which should be fed
            :param additional_food_round: Whether this is a manual feeding from the freshkill pile, default False
        """
        self.update_nutrition(living_cats)
        # NOTE: this is for testing purposes
        if not game.clan:
            self.tactic_status(living_cats, additional_food_round)
            return

        # NOTE: the tactics should have their own function for testing purposes
        if game.clan.clan_settings["younger first"]:
            self.tactic_younger_first(living_cats, additional_food_round)
        elif game.clan.clan_settings["less nutrition first"]:
            self.tactic_less_nutrition_first(living_cats, additional_food_round)
        elif game.clan.clan_settings["more experience first"]:
            self.tactic_more_experience_first(living_cats, additional_food_round)
        elif game.clan.clan_settings["hunter first"]:
            self.tactic_hunter_first(living_cats, additional_food_round)
        elif game.clan.clan_settings["sick/injured first"]:
            self.tactic_sick_injured_first(living_cats, additional_food_round)
        elif game.clan.clan_settings["by-status"]:
            self.tactic_status(living_cats, additional_food_round)
        else:
            self.tactic_status(living_cats, additional_food_round)

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
    #                                    tactics                                   #
    # ---------------------------------------------------------------------------- #

    def tactic_status(self, living_cats: List[Cat], additional_food_round=False) -> None:
        """Feed cats in order of status, resolving ties with age.

        :param list living_cats: Cats to feed
        :param bool additional_food_round: Determines if not player-initiated, default False
        """

        # get all live clan cat IDs in a dict with their status
        clan_cats = self.handle_kits_and_queens(living_cats)

        clan_cats = sorted(clan_cats.values(), key=lambda x: x.moons)
        clan_cats = sorted(clan_cats, key=lambda x: FEEDING_ORDER.index(x.status))

        self.feed_group(clan_cats, additional_food_round)

    @staticmethod
    def handle_kits_and_queens(living_cats):
        clan_cats = {cat.ID: cat for cat in living_cats}
        """Dict with key : value of cat.ID : cat"""

        # find queens & pregnant cats IDs to set their status to queen/pregnant
        queen_dict, kits = get_alive_clan_queens(living_cats)
        # kits under 3 months are fed by the queen
        for queen_id, their_kits in queen_dict.items():
            young_kits = [kit.ID for kit in their_kits if kit.moons < 3]
            if len(young_kits) != 0:  # if kits exist, set the family's food requirements appropriately
                for key in young_kits:
                    clan_cats.pop(key)  # remove the kits from the list, we don't need them where we're going
                clan_cats[queen_id].status = "queen/pregnant"
        # doing the same for the catermelons
        catermelons = [cat.ID for cat in living_cats if "pregnant" in cat.injuries]
        if len(catermelons) != 0:
            for sliced_catermelon in catermelons:
                clan_cats[sliced_catermelon].status = "queen/pregnant"

        return clan_cats

    def tactic_younger_first(
            self, living_cats: List[Cat], additional_food_round=False
    ) -> None:
        """Feed cats in order of age, youngest first.

        :param list living_cats: Cats to feed
        :param bool additional_food_round: Determines if not player-initiated, default False
        """
        sorted_cats = sorted(living_cats, key=lambda x: x.moons)
        self.feed_group(sorted_cats, additional_food_round)

    def tactic_less_nutrition_first(
            self, living_cats: List[Cat], additional_food_round=False
    ) -> None:
        """Feed cats in order of nutrition, lowest first.

        :param list living_cats: Cats to feed
        :param bool additional_food_round: Determines if not player-initiated, default False
        """
        if len(living_cats) == 0:
            return

        # first get special groups, which need to be looked out for when feeding
        clan_cats = self.handle_kits_and_queens(living_cats)

        # first split nutrition information into low nutrition and satisfied
        ration_prey = game.clan.clan_settings["ration prey"] if game.clan else False

        low_nutrition = {}
        satisfied = {}
        for cat in clan_cats.values():
            if self.nutrition_info[cat.ID].is_low_nutrition:
                low_nutrition[cat.ID] = self.nutrition_info[cat.ID]
            else:
                satisfied[cat.ID] = self.nutrition_info[cat.ID]
        # if there are no low nutrition cats, go back to status tactic
        if len(low_nutrition) == 0:
            self.tactic_status(living_cats)
            return

        # sort the nutrition after amount
        sorted_nutrition = dict(
            sorted(low_nutrition.items(), key=lambda x: x[1].percentage)
        )
        for cat_id in sorted_nutrition.keys():
            feeding_amount, needed_amount = self.determine_portion(clan_cats[cat_id], ration_prey,
                                                                   additional_food_round)

            self.feed_cat(clan_cats[cat_id], feeding_amount, needed_amount)

        # feed the rest according to their status
        remaining_cats = [Cat.fetch_cat(info[0]) for info in satisfied.items()]
        self.tactic_status(remaining_cats, additional_food_round)
        return

    def determine_portion(self, cat, ration_prey=False, additional_food_round=False):
        feeding_amount = PREY_REQUIREMENT[cat.status]
        needed_amount = feeding_amount

        # check for condition
        if "pregnant" not in cat.injuries and cat.not_working():
            if game.clan and game.clan.game_mode == "cruel season":
                feeding_amount += CONDITION_INCREASE
            needed_amount = feeding_amount
        else:
            if ration_prey and cat.status == "warrior":
                feeding_amount = feeding_amount / 2

        if self.nutrition_info[cat.ID].percentage > 99:
            return feeding_amount, needed_amount

        if self.total_amount * 2 > self.amount_food_needed():
            feeding_amount += 2

        if self.total_amount * 1.8 > self.amount_food_needed():
            feeding_amount += 1.5

        elif self.total_amount * 1.2 > self.amount_food_needed():
            feeding_amount += 1

        elif self.total_amount > self.amount_food_needed():
            feeding_amount += 0.5

        if additional_food_round:
            needed_amount = 0

        return feeding_amount, needed_amount


    def tactic_more_experience_first(
            self, living_cats: List[Cat], additional_food_round=False
    ) -> None:
        """Feed cats in order of experience, highest first.

        :param list living_cats: Cats to feed
        :param bool additional_food_round: Determines if not player-initiated, default False
        """
        sorted_cats = sorted(living_cats, key=lambda x: x.experience, reverse=True)
        self.feed_group(sorted_cats, additional_food_round)

    def tactic_hunter_first(self, living_cats: List[Cat], additional_food_round=False) -> None:
        """Feed cats with the hunter skill first, then everyone else according to status.

        :param list living_cats: Cats to feed
        :param bool additional_food_round: Determines if not player-initiated, default False
        """
        best_hunter = []
        for search_rank in range(1, 4):
            for cat in living_cats.copy():
                if not cat.skills:
                    continue
                if (
                        cat.skills.primary
                        and cat.skills.primary.path == SkillPath.HUNTER
                        and cat.skills.primary.tier == search_rank
                ):
                    best_hunter.insert(0, cat)
                    living_cats.remove(cat)
                elif (
                        cat.skills.secondary
                        and cat.skills.secondary.path == SkillPath.HUNTER
                        and cat.skills.secondary.tier == search_rank
                ):
                    best_hunter.insert(0, cat)
                    living_cats.remove(cat)

        self.feed_group(best_hunter, additional_food_round)
        self.tactic_status(living_cats, additional_food_round)

    def tactic_sick_injured_first(
            self, living_cats: List[Cat], additional_food_round=False
    ) -> None:
        """Feed cats in order of health, with sick/injured first.

        :param list living_cats: Cats to feed
        :param bool additional_food_round: Determines if not player-initiated, default False
        """
        sick_cats = [cat for cat in living_cats if cat.is_ill() or cat.is_injured()]
        healthy_cats = [
            cat for cat in living_cats if not cat.is_ill() and not cat.is_injured()
        ]
        self.feed_group(sick_cats, additional_food_round)
        self.tactic_status(healthy_cats, additional_food_round)

    # ---------------------------------------------------------------------------- #
    #                               helper functions                               #
    # ---------------------------------------------------------------------------- #

    def feed_group(
            self, group: list, additional_food_round=False, queens_only=False, fed_kits=None
    ) -> None:
        """Feed a group of cats.

        :param list group: Cats to feed
        :param bool additional_food_round: Determines if not player-initiated, default False
        :param bool queens_only: if this group is exclusively queens/pregnant cats, default False
        :param list fed_kits: list of kits in the group
        """
        if len(group) == 0:
            return

        # first split nutrition information into low nutrition and satisfied
        ration_prey = game.clan.clan_settings["ration prey"] if game.clan else False

        # Feed according to hierarchy
        for cat in group:
            if cat in self.already_fed:
                continue
            status = str(cat.status)
            # check if this is a kit: if so, check if they are fed by the mother
            if status in ["newborn", "kitten"] and fed_kits and cat in fed_kits:
                continue

            # check for queens / pregnant
            if queens_only:
                status = "queen/pregnant"

            feeding_amount, needed_amount = self.determine_portion(cat, ration_prey, additional_food_round)

            self.feed_cat(cat, feeding_amount, needed_amount)


    def feed_cat(self, cat: Cat, feeding_amount, needed_amount) -> None:
        """
        Handle the feeding process.

            Parameters
            ----------
            cat : Cat
                the cat to feed
            feeding_amount : int|float
                the amount which will be consumed
            needed_amount : int|float
                the amount the cat actually needs for the moon
        """

        ration = game.clan.clan_settings["ration prey"] if game.clan else False
        remaining_amount = feeding_amount
        amount_difference = needed_amount - feeding_amount

        remaining_amount = self.remove_freshkill(remaining_amount)
        self.already_fed.append(cat)

        if remaining_amount > 0 and amount_difference == 0:
            self.nutrition_info[cat.ID].current_score -= remaining_amount
        elif remaining_amount == 0:
            if needed_amount == 0:
                self.nutrition_info[cat.ID].current_score += feeding_amount
            elif feeding_amount > needed_amount:
                self.nutrition_info[cat.ID].current_score += feeding_amount - needed_amount
        elif ration and cat.status == "warrior" and needed_amount != 0:
            feeding_amount = PREY_REQUIREMENT[cat.status]
            feeding_amount = feeding_amount / 2
            self.nutrition_info[cat.ID].current_score -= feeding_amount

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

    # ---------------------------------------------------------------------------- #
    #                              nutrition relevant                              #
    # ---------------------------------------------------------------------------- #

    def update_nutrition(self, living_cats: list) -> None:
        """
        Handles increasing or decreasing the max score of their nutrition
        depending on their age. Automatically removes irrelevant cats.

            Parameters
            ----------
            living_cats : list
                the list of the current living cats, where the nutrition should be stored
        """
        old_nutrition_info = deepcopy(self.nutrition_info)
        self.nutrition_info = {}
        queen_dict, kits = get_alive_clan_queens(living_cats)

        for cat in living_cats:
            if str(cat.status) not in PREY_REQUIREMENT:
                continue
            # update the nutrition_info
            if cat.ID in old_nutrition_info:
                self.nutrition_info[cat.ID] = old_nutrition_info[cat.ID]
                factor = 3
                status_ = str(cat.status)
                if str(cat.status) in ["newborn", "kitten"] or (
                        cat.moons > 114 and str(cat.status) == "elder"
                ):
                    factor = 2
                if cat.ID in queen_dict.keys() or "pregnant" in cat.injuries:
                    status_ = "queen/pregnant"

                # check if the max_score is correct, otherwise update
                required_max = PREY_REQUIREMENT[status_] * factor
                current_score = self.nutrition_info[cat.ID].current_score
                if self.nutrition_info[cat.ID].max_score != required_max:
                    previous_max = self.nutrition_info[cat.ID].max_score
                    self.nutrition_info[cat.ID].max_score = required_max
                    self.nutrition_info[cat.ID].current_score = (
                            current_score / previous_max * required_max
                    )
            else:
                self.add_cat_to_nutrition(cat)

    def add_cat_to_nutrition(self, cat: Cat) -> None:
        """
        Parameters
        ----------
        cat : Cat
            the cat, which should be added to the nutrition info
        """
        nutrition = Nutrition()
        factor = 3
        if str(cat.status) in ["newborn", "kitten", "elder"]:
            factor = 2

        queen_dict, kits = get_alive_clan_queens(self.living_cats)
        prey_status = str(cat.status)
        if cat.ID in queen_dict.keys() or "pregnant" in cat.injuries:
            prey_status = "queen/pregnant"
        max_score = PREY_REQUIREMENT[prey_status] * factor
        nutrition.max_score = max_score
        nutrition.current_score = max_score

        # adapt sickness (increase needed amount)
        if (
                "pregnant" not in cat.injuries
                and cat.not_working()
                and game.clan
                and game.clan.game_mode == "cruel season"
        ):
            nutrition.max_score += CONDITION_INCREASE * factor
            nutrition.current_score = nutrition.max_score

        self.nutrition_info[cat.ID] = nutrition


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
