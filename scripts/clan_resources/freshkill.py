from scripts.utility import get_alive_clan_queens
from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game
from copy import deepcopy
import random

class Nutrition():
    """All the information about nutrition from one cat."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.max_score = 1
        self.current_score = 0
        self.percentage = 0

    def __str__(self):
        this_is_a_dict_not_a_string = {
            "max_score": self.max_score,
            "current_score": self.current_score,
            "percentage": self.percentage,
        }
        return str(this_is_a_dict_not_a_string)

    @property
    def current_score(self):
        return self._current_score

    @current_score.setter
    def current_score(self, value) -> None:
        """
        When the current_score is changed, this will be handled here. It also automatically calculates the percentage of the nutrient.

            Parameters
            ----------
            value : int|float
                the value which should be set to the current score
        """
        if value > self.max_score:
            value = self.max_score
        if value < 0:
            value = 0
        self._current_score = value
        self.percentage = self._current_score / self.max_score * 100


class Freshkill_Pile():
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
            total = 0
            for k,v in pile.items():
                total += v
            self.total_amount = total
        else:
            self.pile = {
                "expires_in_4": game.config["freshkill"]["start_amount"],
                "expires_in_3": 0,
                "expires_in_2": 0,
                "expires_in_1": 0,
            }
            self.total_amount = game.config["freshkill"]["start_amount"]
        self.nutrition_info = {}

    def add_freshkill(self, amount) -> None:
        """
        Add new fresh kill to the pile.

            Parameters
            ----------
            amount : int|float
                the amount which should be added to the pile
        """
        self.pile["expires_in_4"] += amount
        self.total_amount += amount

    def remove_freshkill(self, amount, take_random: bool = False) -> None:
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
            return
        order = ["expires_in_1", "expires_in_2", "expires_in_3", "expires_in_4"]
        if take_random:
            random.shuffle(order)       
        for key in order:
            amount = self.take_from_pile(key, amount)
        
    def time_skip(self, living_cats: list) -> None:
        """
        Handle the time skip for the freshkill pile, 'age' the prey and feeding the cats.

            Parameters
            ----------
            living_cats : list
                list of living cats which should be feed
        """
        previous_amount = 0
        # update the freshkill pile
        for key, value in self.pile.items():
            self.pile[key] = previous_amount
            previous_amount = value
            #if key == "expires_in_1":
                #print(f" -- FRESHKILL: {value} expired prey is removed")
        self.total_amount = sum(self.pile.values())

        self.feed_cats(living_cats)

    def feed_cats(self, living_cats: list) -> None:
        """
        Handles to feed all living cats. This happens before the aging up.

            Parameters
            ----------
            living_cats : list
                list of living cats which should be feed
        """
        self.update_nutrition(living_cats)

        relevant_group = []
        queens = get_alive_clan_queens(Cat.all_cats)
        relevant_queens = []
        for queen in queens:
            kits = queen.get_children()
            kits = [cat for cat in living_cats if cat.ID in kits]
            young_kits = [kit for kit in kits if kit.moons < 3]
            if len(young_kits) > 0:
                relevant_queens.append(queen)

        for status_ in FEEDING_ORDER:
            if status_ == "queen":
                relevant_group = relevant_queens
            elif status_ == "kitten":
                relevant_group = [cat for cat in living_cats if str(cat.status) == status_ and cat.moons >= 2]
            else:
                relevant_group = [cat for cat in living_cats if str(cat.status) == status_]
                # remove all cats, which are also queens
                relevant_group = [cat for cat in relevant_group if cat not in relevant_queens]

            sick_cats = [cat for cat in relevant_group if cat.is_injured() or cat.is_ill()]
            needed_prey = len(relevant_group) * PREY_REQUIREMENT[status_] + len(sick_cats) * CONDITION_INCREASE
            enough_prey = needed_prey <= self.total_amount

            if not enough_prey:
                self.handle_not_enough_food(relevant_group, status_)
            else:
                self.feed_group(relevant_group, status_)

    def amount_food_needed(self):
        """
            Returns
            -------
            needed_prey : int|float
                the amount of prey the clan needs
        """
        living_cats = list(filter(lambda cat_: not cat_.dead and not cat_.outside and not cat_.exiled, Cat.all_cats.values()))
        sick_cats = [cat for cat in living_cats if cat.is_injured() or cat.is_ill()]
        queens = get_alive_clan_queens(Cat.all_cats)

        needed_prey = [PREY_REQUIREMENT[cat.status] for cat in living_cats]
        needed_prey = sum(needed_prey) + len(sick_cats) * CONDITION_INCREASE + len(queens) * (PREY_REQUIREMENT["queen"] - PREY_REQUIREMENT["warrior"])
        return needed_prey

    def clan_has_enough_food(self) -> bool:
        """
            Returns
            -------
            _ : bool
                check if the amount of the prey is enough for one moon
        """
        return self.amount_food_needed() <= self.total_amount

    # ---------------------------------------------------------------------------- #
    #                               helper functions                               #
    # ---------------------------------------------------------------------------- #

    def handle_not_enough_food(self, group: list, status_ : str) -> None:
        """
        Handle the situation where there is not enough food for this group.

            Parameters
            ----------
            group : list
                the list of cats which should be feed
            status_ : str
                the status of each cat of the group
        """
        tactic = None # TODO: handle with a setting
        if tactic == "younger_first":
            sorted_group = sorted(group, key=lambda x: x.moons)
            self.feed_group(sorted_group, status_)

        elif tactic == "less_nutrition_first":
            self.tactic_less_nutrition(group, status_)

        elif tactic == "more_experience_first":
            sorted_group = sorted(group, key=lambda x: x.experience, reverse=True)
            self.feed_group(sorted_group, status_)

        elif tactic == "hunter_first":
            ranking = {
                "fantastic hunter": 0,
                "great hunter": 1,
                "good hunter": 2,
            }
            sorted_group = sorted(group, key=lambda x: ranking[x.skill] if x.skill in ranking else 3)
            self.feed_group(sorted_group, status_)

        else:
            self.feed_group(group, status_)

    def feed_group(self, group: list, status_: str) -> None:
        """
        Handle the feeding of a specific group of cats, the order is already set.

            Parameters
            ----------
            group : list
                the list of cats which should be feed
            status_ : str
                the status of each cat of the group
        """
        # ration_prey < healthy warrior will only eat half of the food they need
        ration_prey = False # TODO: handled with a setting

        for cat in group:
            feeding_amount = PREY_REQUIREMENT[status_]
            needed_amount = feeding_amount
            if cat.is_ill() or cat.is_injured():
                feeding_amount += CONDITION_INCREASE
                needed_amount = feeding_amount
            else:
                if ration_prey and status_ == "warrior":
                    feeding_amount = feeding_amount/2
            lot_more_prey = self.amount_food_needed() < self.total_amount * 1.5
            if lot_more_prey and self.nutrition_info[cat.ID].percentage < 100:
                feeding_amount += 1
            self.feed_cat(cat, feeding_amount, needed_amount)

    def tactic_less_nutrition(self, group: list, status_: str) -> None:
        """
        With this tactic, the cats with the lowest nutrition will be feed first.

            Parameters
            ----------
            group : list
                the list of cats which should be feed
            status_ : str
                the status of each cat of the group
        """
        group_ids = [cat.id for cat in group]
        sorted_nutrition = sorted(self.nutrition_info.items(), key=lambda x: x[1].percentage)
        ration_prey = False # TODO: handled with a setting

        for k, v in sorted_nutrition:
            if k not in group_ids:
                continue
            cat = Cat.all_cats[k]
            feeding_amount = PREY_REQUIREMENT[status_]
            needed_amount = feeding_amount
            if cat.is_ill() or cat.is_injured():
                feeding_amount += CONDITION_INCREASE
                needed_amount = feeding_amount
            else:
                if ration_prey and status_ == "warrior":
                    feeding_amount = feeding_amount/2
            self.feed_cat(cat, feeding_amount, needed_amount)

    def feed_cat(self, cat: Cat, amount, actual_needed) -> None:
        """
        Handle the feeding process.

            Parameters
            ----------
            cat : Cat
                the cat to feed
            amount : int|float
                the amount which will be consumed
            actual_needed : int|float
                the amount the cat actually needs for the moon
        """
        previous_amount = amount
        remaining_amount = amount
        amount_difference = actual_needed - amount
        order = ["expires_in_1", "expires_in_2", "expires_in_3", "expires_in_4"]
        for key in order:
            remaining_amount = self.take_from_pile(key, remaining_amount)
            self.nutrition_info[cat.ID].current_score += previous_amount - remaining_amount
            previous_amount = remaining_amount

        if remaining_amount > 0:
            self.nutrition_info[cat.ID].current_score -= (remaining_amount + amount_difference)

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
            self.total_amount -= given_amount
            remaining_amount = 0
        elif self.pile[pile_group] > 0:
            remaining_amount = given_amount - self.pile[pile_group]
            self.total_amount -= self.pile[pile_group]
            self.pile[pile_group] = 0

        return remaining_amount

    # ---------------------------------------------------------------------------- #
    #                              nutrition relevant                              #
    # ---------------------------------------------------------------------------- #

    def update_nutrition(self, living_cats: list) -> None:
        """
        Handles increasing or decreasing the max score of their nutrition depending on their age and automatically removes irrelevant cats.

            Parameters
            ----------
            living_cats : list
                the list of the current living cats, where the nutrition should be stored
        """
        old_nutrition_info = deepcopy(self.nutrition_info)
        self.nutrition_info = {}

        for cat in living_cats:
            # update the nutrition_info
            if cat.ID in old_nutrition_info:
                self.nutrition_info[cat.ID] = old_nutrition_info[cat.ID]
                # check if the max_score is correct, otherwise update
                if cat.moons == 6:
                    self.nutrition_info[cat.ID].max_score = PREY_REQUIREMENT[str(cat.status)] * 3
                    self.nutrition_info[cat.ID].current_score += PREY_REQUIREMENT[str(cat.status)]
                elif cat.moons == 12:
                    self.nutrition_info[cat.ID].max_score = PREY_REQUIREMENT[str(cat.status)] * 3
                    self.nutrition_info[cat.ID].current_score += PREY_REQUIREMENT[str(cat.status)]
                elif cat.moons >= 120 and str(cat.status) == "elder":
                    self.nutrition_info[cat.ID].max_score = PREY_REQUIREMENT[str(cat.status)] * 2
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
        if str(cat.status) in ["kitten", "elder"]:
            factor = 2

        max_score = PREY_REQUIREMENT[str(cat.status)] * factor
        nutrition.max_score = max_score
        nutrition.current_score = max_score
        nutrition.percentage = 100

        self.nutrition_info[cat.ID] = nutrition



# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #


ADDITIONAL_PREY = game.config["freshkill"]["additional_prey"]
PREY_REQUIREMENT = game.config["freshkill"]["prey_requirement"]
CONDITION_INCREASE = game.config["freshkill"]["condition_increase"]
FEEDING_ORDER = game.config["freshkill"]["feeding_order"]
HUNTER_BONUS = game.config["freshkill"]["hunter_bonus"]
HUNTER_EXP_BONUS = game.config["freshkill"]["hunter_exp_bonus"]
FRESHKILL_EVENT_TRIGGER_FACTOR = game.config["freshkill"]["event_trigger_factor"]
MAL_PERCENTAGE = game.config["freshkill"]["nutrition_malnourished_percentage"]
STARV_PERCENTAGE = game.config["freshkill"]["nutrition_starving_percentage"]

FRESHKILL_ACTIVE = game.config["freshkill"]["activate_death"]
FRESHKILL_EVENT_ACTIVE = game.config["freshkill"]["activate_events"]