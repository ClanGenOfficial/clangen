from scripts.utility import get_alive_clan_queens
from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import *
from copy import deepcopy
import random

PREY_REQUIREMENT = {
    "leader": 3,
    "deputy": 3,
    "medicine cat": 2,
    "medicine cat apprentice": 1.5,
    "mediator apprentice": 1.5,
    "mediator": 2,
    "warrior": 3,
    "apprentice": 1.5,
    "elder": 1.5,
    "queen": 4,
    "kitten": 0.5,
}

CONDITION_INCREASE = 0.5

FEEDING_ORDER = [
    "kitten",
    "queen",
    "elder",
    "medicine cat",
    "medicine cat apprentice",
    "apprentice",
    "mediator apprentice",
    "warrior",
    "mediator",
    "deputy",
    "leader"
]

HUNTER_BONUS = {"fantastic_hunter": 3, "great_hunter": 2, "good_hunter": 1}
HUNTER_EXP_BONUS = {
    "very_low": 1,
    "low": 2,
    "average": 3,
    "high": 4,
    "master": 5,
    "max": 7
}

class Nutrition():
    """All the information about nutrition from one cat."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.max_score = 1
        self.current_score = 0
        self.percentage = 0

    def __str__(self):
        return {
            "max_score": self.max_score,
            "current_score": self.current_score,
            "percentage": self.percentage,
        }

    @property
    def current_score(self):
        return self._current_score

    @current_score.setter
    def current_score(self, value):
        if value > self.max_score:
            value = self.max_score
        if value < 0:
            value = 0
        self._current_score = value
        self.percentage = self._current_score / self.max_score * 100


class Freshkill_Pile():
    """Handle everything related to the freshkill pile of the clan."""

    def __init__(self, pile = None) -> None:
        """Initialize the class."""
        # the pile could be handled as a list but this makes it more readable

        if pile:
            self.pile = pile
            total = 0
            for k,v in pile.items():
                total += v
            self.total_amount = total
        else:
            self.pile = {
                "expires_in_4": 0,
                "expires_in_3": 0,
                "expires_in_2": 0,
                "expires_in_1": 0,
            }
            self.total_amount = 0
        self.nutrition_info = {}

    def add_freshkill(self, amount):
        """Add new fresh kill to the pile."""
        self.pile["expires_in_4"] += amount
        self.total_amount += amount

    def remove_freshkill(self, amount, take_random=False):
        """Remove a certain amount of fresh kill from the pile."""
        if amount == 0:
            return
        order = ["expires_in_1", "expires_in_2", "expires_in_3", "expires_in_4"]
        if take_random:
            random.shuffle(order)       
        for key in order:
            amount = self.take_from_pile(key, amount)
        

    def time_skip(self, living_cats):
        """Handle the time skip for the freshkill pile, including feeding the cats."""
        previous_amount = 0
        # update the freshkill pile
        for key, value in self.pile.items():
            self.pile[key] = previous_amount
            previous_amount = value
        self.total_amount = sum(self.pile.values())

        self.feed_cats(living_cats)
        print(f"REMAINING AMOUNT: {self.total_amount} (needed: {self.amount_food_needed()})")

    def feed_cats(self, living_cats):
        """Handles to feed all living cats. This happens before the aging up."""
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
        """Returns the amount of prey which the clan needs."""
        living_cats = list(filter(lambda cat_: not cat_.dead and not cat_.outside , Cat.all_cats.values()))
        sick_cats = [cat for cat in living_cats if cat.is_injured() or cat.is_ill()]
        queens = get_alive_clan_queens(Cat.all_cats)

        needed_prey = [PREY_REQUIREMENT[cat.status] for cat in living_cats]
        needed_prey = sum(needed_prey) + len(sick_cats) * CONDITION_INCREASE + len(queens) * (PREY_REQUIREMENT["queen"] - PREY_REQUIREMENT["warrior"])
        return needed_prey

    def clan_has_enough_food(self):
        """Check if the amount of the prey is enough for one moon."""
        return self.amount_food_needed() <= self.total_amount

    # ---------------------------------------------------------------------------- #
    #                               helper functions                               #
    # ---------------------------------------------------------------------------- #

    def handle_not_enough_food(self, group, status_):
        """Handle the situation where there is not enough food for this group."""
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

    def feed_group(self, group, status_):
        """Handle the feeding of a specific group of cats, the order is already set."""
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
            self.feed_cat(cat, feeding_amount, needed_amount)

    def tactic_less_nutrition(self, group, status_):
        """With this tactic, the cats with the lowest nutrition will be feed first."""
        group_ids = [cat.id for cat in group]
        sorted_nutrition = sorted(self.nutrition_info.items(), key=lambda x: x[1].percentage)
        # ration_prey < warrior will only eat half of the food they need
        ration_prey = True # TODO: handled with a setting

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

    def feed_cat(self, cat, amount, actual_needed):
        """Handle the feeding process."""
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

    def take_from_pile(self, pile_group, given_amount):
        """Take the amount from the pile group. Returns the rest of the original needed amount."""
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

    def update_nutrition(self, living_cats):
        """Update the nutrition information."""
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

    def add_cat_to_nutrition(self, cat):
        """Add a cat to the nutrition info"""
        nutrition = Nutrition()
        factor = 3
        if str(cat.status) in ["kitten", "elder"]:
            factor = 2

        max_score = PREY_REQUIREMENT[str(cat.status)] * factor
        nutrition.max_score = max_score
        nutrition.current_score = max_score
        nutrition.percentage = 100

        self.nutrition_info[cat.ID] = nutrition
