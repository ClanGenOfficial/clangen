from scripts.utility import get_queens
from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import *
from copy import deepcopy

PREY_REQUIREMENT = {
    "leader": 3,
    "deputy": 3,
    "medicine cat": 2,
    "medicine cat apprentice": 1.5,
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
    "warrior",
    "deputy",
    "leader"
]


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

    def add_freshkill(self, amount):
        """Add new fresh kill to the pile."""
        self.pile["expires_in_4"] += amount

    def time_skip(self, living_cats):
        """Handle the time skip for the freshkill pile."""
        previous_amount = 0
        # update the freshkill pile
        for key, value in self.pile.items():
            self.pile[key] = previous_amount
            previous_amount = value
        self.total_amount = sum(self.pile.values())

        self.feed_cats(living_cats)
        
    def feed_cats(self, living_cats):
        """Handles to feed all living cats. This happens before the aging up."""
        self.update_nutrition(living_cats)

        relevant_group = []
        queens = get_queens(living_cats, Cat.all_cats)
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

    def update_nutrition(self, living_cats):
        """Update the nutrition information."""
        old_nutrition_info = deepcopy(self.nutrition_info)
        self.nutrition_info = {}

        # TODO: check nutrition information from dead cats are removed
        for cat in living_cats:
            # update the nutrition_info
            if cat.ID in old_nutrition_info:
                self.nutrition_info[cat.ID] = old_nutrition_info[cat.ID] 
                # check if the max_amount is correct, otherwise update
                if cat.moons == 6:
                    self.nutrition_info[cat.ID].max_amount = PREY_REQUIREMENT[str(cat.status)] * 3
                # TODO: maybe find a better way to handle this
                if cat.moons >= 120 and str(cat.status) == "elder":
                    self.nutrition_info[cat.ID].max_amount = PREY_REQUIREMENT[str(cat.status)] * 2
            else:
                self.add_cat_to_nutrition(cat)

    def feed_group(self, group, status_):
        """Handle the feeding of a specific group of cats, the order is already set."""
        for cat in group:
            needed_prey = PREY_REQUIREMENT[status_]
            if cat.is_ill() or cat.is_injured():
                needed_prey += CONDITION_INCREASE
            self.feed_cat(cat, needed_prey)

    def handle_not_enough_food(self, group, status_):
        """Handle the situation where there is not enough food for this group."""
        tactic = None
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

    def tactic_less_nutrition(self, group, status_):
        """With this tactic, the cats with the lowest nutrition will be feed first."""
        sorted_nutrition = sorted(self.nutrition_info.items(), key=lambda x: x[1].percentage)

        for k, v in sorted_nutrition:
            cat = Cat.all_cats[k]
            needed_prey = PREY_REQUIREMENT[status_]
            if cat.is_ill() or cat.is_injured():
                needed_prey += CONDITION_INCREASE
            self.feed_cat(cat,needed_prey)

    def feed_cat(self, cat, amount):
        """Handle the feeding process."""
        previous_amount = amount
        remaining_amount = amount
        order = ["expires_in_1", "expires_in_2", "expires_in_3", "expires_in_4"]
        for key in order:
            remaining_amount = self.take_from_pile(key, remaining_amount)
            self.nutrition_info[cat.ID].current_score += previous_amount - remaining_amount
            previous_amount = remaining_amount

        if remaining_amount > 0:
            self.nutrition_info[cat.ID].current_score -= remaining_amount

    def take_from_pile(self, pile_group, needed_amount):
        """Take the amount from the pile group. Returns the rest of the original needed amount."""
        if needed_amount == 0:
            return needed_amount

        remaining_amount = needed_amount
        if self.pile[pile_group] >= needed_amount:
            self.pile[pile_group] -= needed_amount
            self.total_amount -= needed_amount
            remaining_amount = 0
        elif self.pile[pile_group] > 0:
            remaining_amount = needed_amount - self.pile[pile_group]
            self.total_amount -= self.pile[pile_group]
            self.pile[pile_group] = 0

        return remaining_amount
