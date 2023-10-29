from typing import List
from scripts.utility import get_alive_clan_queens
from scripts.cat.cats import Cat
from scripts.cat.skills import SkillPath
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
                "expires_in_4": game.prey_config["start_amount"],
                "expires_in_3": 0,
                "expires_in_2": 0,
                "expires_in_1": 0,
            }
            self.total_amount = game.prey_config["start_amount"]
        self.nutrition_info = {}
        self.living_cats = []

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

    def time_skip(self, living_cats: list, event_list: list) -> None:
        """
        Handle the time skip for the freshkill pile, 'age' the prey and feeding the cats.

            Parameters
            ----------
            living_cats : list
                list of living cats which should be feed
        """
        self.living_cats = living_cats
        previous_amount = 0
        # update the freshkill pile
        for key, value in self.pile.items():
            self.pile[key] = previous_amount
            previous_amount = value
            if key == "expires_in_1" and FRESHKILL_ACTIVE and value > 0:
                event_list.append(f"Some prey expired, {value} pieces where removed from the pile.")
        self.total_amount = sum(self.pile.values())
        value_diff = self.total_amount
        self.feed_cats(living_cats)
        value_diff -= sum(self.pile.values())
        event_list.append(f"{value_diff} pieces of prey where consumed.")

    def feed_cats(self, living_cats: list) -> None:
        """
        Handles to feed all living clan cats. This happens before the aging up.

            Parameters
            ----------
            living_cats : list
                list of living cats which should be feed
        """
        self.update_nutrition(living_cats)

        relevant_group = []
        queen_dict, kits = get_alive_clan_queens(living_cats)
        relevant_queens = []
        # kits under 3 months are feed by the queen
        for queen_id, their_kits in queen_dict.items():
            queen = Cat.fetch_cat(queen_id)
            young_kits = [kit for kit in their_kits if kit.moons < 3]
            if len(young_kits) > 0:
                relevant_queens.append(queen)
        
        pregnant_cats = [cat for cat in living_cats if "pregnant" in cat.injuries and cat.ID not in queen_dict.keys()]

        for feeding_status in FEEDING_ORDER:
            if feeding_status == "newborn":
                relevant_group = [
                    cat for cat in living_cats if cat.status == "newborn" and  cat.moons > 2 and\
                    not any(parent_id in queen_dict.keys() for parent_id in cat.get_parents())
                ]
            elif feeding_status == "kitten":
                # kits under 3 months are feed by the queen
                all_kits = [
                    cat for cat in living_cats if cat.status == "kitten" and cat.moons > 2 and\
                    not any(parent_id in queen_dict.keys() for parent_id in cat.get_parents())
                ]
                relevant_group = all_kits
            elif feeding_status == "queen/pregnant":
                relevant_group = relevant_queens + pregnant_cats
            else:
                relevant_group = [cat for cat in living_cats if str(cat.status) == feeding_status]
                # remove all cats, which are also queens / pregnant
                relevant_group = [cat for cat in relevant_group if cat not in relevant_queens and cat not in pregnant_cats]

            if len(relevant_group) == 0:
                continue

            sick_cats = []
            for cat in relevant_group:
                injured_not_pregnant = (cat.is_injured() and "pregnant" not in cat.injuries) or len(cat.injuries) > 1
                if cat.is_ill() or injured_not_pregnant:
                    sick_cats.append(cat)
            
            # check if there is enough food for this group
            needed_prey = len(relevant_group) * PREY_REQUIREMENT[feeding_status] + len(sick_cats) * CONDITION_INCREASE
            enough_prey = needed_prey <= self.total_amount
            if not enough_prey:
                self.handle_not_enough_food(relevant_group, feeding_status)
            else:
                self.feed_group(relevant_group, feeding_status)

    def amount_food_needed(self):
        """
            Returns
            -------
            needed_prey : int|float
                the amount of prey the Clan needs
        """
        living_cats = [i for i in Cat.all_cats.values() if not (i.dead or i.outside or i.exiled)]
        sick_cats = [cat for cat in living_cats if cat.is_injured() or cat.is_ill()]
        queen_dict, living_kits = get_alive_clan_queens(self.living_cats)

        needed_prey = [PREY_REQUIREMENT[cat.status] for cat in living_cats]
        needed_prey = sum(needed_prey) + len(sick_cats) * CONDITION_INCREASE + len(queen_dict) * (PREY_REQUIREMENT["queen/pregnant"] - PREY_REQUIREMENT["warrior"])
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
        # NOTE: this is for testing purposes
        if not game.clan:
            self.feed_group(group, status_)
            return

        # NOTE: the tactics should have a own function for testing purposes
        if game.clan.clan_settings["younger first"]:
            self.tactic_younger_first(group, status_)
        elif game.clan.clan_settings["less nutrition first"]:
            self.tactic_less_nutrition_first(group, status_)
        elif game.clan.clan_settings["more experience first"]:
            self.tactic_more_experience_first(group, status_)
        elif game.clan.clan_settings["hunter first"]:
            self.tactic_hunter_first(group, status_)
        elif game.clan.clan_settings["sick/injured first"]:
            self.tactic_sick_injured_first(group, status_)
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
        ration_prey = game.clan.clan_settings["ration prey"] if game.clan else False

        for cat in group:
            feeding_amount = PREY_REQUIREMENT[status_]
            needed_amount = feeding_amount
            injured_not_pregnant = (cat.is_injured() and "pregnant" not in cat.injuries) or len(cat.injuries) > 1
            if cat.is_ill() or injured_not_pregnant:
                feeding_amount += CONDITION_INCREASE
                needed_amount = feeding_amount
            else:
                if ration_prey and status_ == "warrior":
                    feeding_amount = feeding_amount/2
            # if there is enough prey, and nutrients are low, fill the nutrients up
            lot_more_prey = self.amount_food_needed() < self.total_amount
            if lot_more_prey and self.nutrition_info[cat.ID].percentage < 100:
                feeding_amount += 1
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
        ration = game.clan.clan_settings["ration prey"] if game.clan else False
        remaining_amount = amount
        amount_difference = actual_needed - amount
        order = ["expires_in_1", "expires_in_2", "expires_in_3", "expires_in_4"]
        for key in order:
            remaining_amount = self.take_from_pile(key, remaining_amount)

        if remaining_amount > 0 and amount_difference == 0:
            self.nutrition_info[cat.ID].current_score -= remaining_amount
        elif actual_needed == 0:
            if remaining_amount == 0:
                self.nutrition_info[cat.ID].current_score += amount
            elif amount > remaining_amount:
                self.nutrition_info[cat.ID].current_score += (amount - remaining_amount)
        elif ration and cat.status == "warrior":
            feeding_amount = PREY_REQUIREMENT[cat.status]
            feeding_amount = feeding_amount/2
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
            self.total_amount -= given_amount
            remaining_amount = 0
        elif self.pile[pile_group] > 0:
            remaining_amount = given_amount - self.pile[pile_group]
            self.total_amount -= self.pile[pile_group]
            self.pile[pile_group] = 0

        return remaining_amount

    # ---------------------------------------------------------------------------- #
    #                                    tactics                                   #
    # ---------------------------------------------------------------------------- #

    def tactic_younger_first(self, group: List[Cat], status_: str) -> None:
        """
        With this tactic, the youngest cats will be fed first.

        Parameters
        ----------
            group : list
                the list of cats which should be feed
            status_ : str
                the status of each cat of the group
        """
        sorted_group = sorted(group, key=lambda x: x.moons)
        self.feed_group(sorted_group, status_)

    def tactic_less_nutrition_first(self, group: list, status_: str) -> None:
        """
        With this tactic, the cats with the lowest nutrition will be feed first.

        Parameters
        ----------
            group : list
                the list of cats which should be feed
            status_ : str
                the status of each cat of the group
        """
        group_ids = [cat.ID for cat in group]
        sorted_nutrition = sorted(self.nutrition_info.items(), key=lambda x: x[1].percentage)
        ration_prey = game.clan.clan_settings["ration prey"] if game.clan else False

        for k, v in sorted_nutrition:
            if k not in group_ids:
                continue
            cat = Cat.all_cats[k]
            feeding_amount = PREY_REQUIREMENT[status_]
            needed_amount = feeding_amount
            injured_not_pregnant = (cat.is_injured() and "pregnant" not in cat.injuries) or len(cat.injuries) > 1
            if cat.is_ill() or injured_not_pregnant:
                feeding_amount += CONDITION_INCREASE
                needed_amount = feeding_amount
            else:
                if ration_prey and status_ == "warrior":
                    feeding_amount = feeding_amount/2
            self.feed_cat(cat, feeding_amount, needed_amount)

    def tactic_more_experience_first(self, group: list, status_: str) -> None:
        """
        With this tactic, the cats with the most experience will be fed first.

        Parameters
        ----------
            group : list
                the list of cats which should be feed
            status_ : str
                the status of each cat of the group
        """
        sorted_group = sorted(group, key=lambda x: x.experience, reverse=True)
        self.feed_group(sorted_group, status_)

    def tactic_hunter_first(self, group: list, status_: str) -> None:
        """
        With this tactic, the cats with the skill hunter (depending on rank) will be fed first.

        Parameters
        ----------
            group : list
                the list of cats which should be feed
            status_ : str
                the status of each cat of the group
        """
        best_hunter = []
        search_rank = 3
        for search_rank in range(1,4):
            for cat in group.copy():
                if not cat.skills:
                    continue
                if cat.skills.primary and cat.skills.primary.path == SkillPath.HUNTER and cat.skills.primary.tier == search_rank:
                    best_hunter.insert(0,cat)
                    group.remove(cat)
                elif cat.skills.secondary and cat.skills.secondary.path == SkillPath.HUNTER and cat.skills.secondary.tier == search_rank:
                    best_hunter.insert(0,cat)
                    group.remove(cat)

        sorted_group = best_hunter + group
        self.feed_group(sorted_group, status_)

    def tactic_sick_injured_first(self, group: list, status_: str) -> None:
        """
        With this tactic, the sick or injured cats will be fed first.

        Parameters
        ----------
            group : list
                the list of cats which should be feed
            status_ : str
                the status of each cat of the group
        """
        sick_cats = [cat for cat in group if cat.is_ill() or cat.is_injured()]
        healthy_cats = [cat for cat in group if not cat.is_ill() and not cat.is_injured()]
        sorted_group = sick_cats + healthy_cats
        self.feed_group(sorted_group, status_)


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
        queen_dict, kits = get_alive_clan_queens(self.living_cats)

        for cat in living_cats:
            if str(cat.status) not in PREY_REQUIREMENT:
                continue
            # update the nutrition_info
            if cat.ID in old_nutrition_info:
                self.nutrition_info[cat.ID] = old_nutrition_info[cat.ID]
                factor = 3
                if str(cat.status) in ["newborn", "kitten", "elder"]:
                    factor = 2
                # check if the max_score is correct, otherwise update
                if cat.moons == 6:
                    self.nutrition_info[cat.ID].max_score = PREY_REQUIREMENT[str(cat.status)] * factor
                    self.nutrition_info[cat.ID].current_score += PREY_REQUIREMENT[str(cat.status)]
                elif cat.moons == 12:
                    self.nutrition_info[cat.ID].max_score = PREY_REQUIREMENT[str(cat.status)] * factor
                    self.nutrition_info[cat.ID].current_score += PREY_REQUIREMENT[str(cat.status)]
                elif cat.moons >= 120 and str(cat.status) == "elder":
                    self.nutrition_info[cat.ID].max_score = PREY_REQUIREMENT[str(cat.status)] * factor
                elif cat.ID in queen_dict.keys() or "pregnant" in cat.injuries:
                    if old_nutrition_info[cat.ID].current_score == PREY_REQUIREMENT[str(cat.status)] * factor:
                        self.nutrition_info[cat.ID].max_score = PREY_REQUIREMENT["queen/pregnant"] * factor
                        old_nutrition_info[cat.ID].current_score= PREY_REQUIREMENT["queen/pregnant"] * factor
                    else:
                        self.nutrition_info[cat.ID].max_score = PREY_REQUIREMENT["queen/pregnant"] * factor
                        new_score = old_nutrition_info[cat.ID].current_score / PREY_REQUIREMENT[str(cat.status)] * PREY_REQUIREMENT["queen/pregnant"]
                        self.nutrition_info[cat.ID].current_score = new_score
                
                # adapt sickness (increase needed amount)
                injured_not_pregnant = (cat.is_injured() and "pregnant" not in cat.injuries) or len(cat.injuries) > 1
                ill_not_starving = (cat.is_ill() and "malnourished" not in cat.illnesses and "starving" not in cat.illnesses)
                if ill_not_starving or injured_not_pregnant:
                    self.nutrition_info[cat.ID].max_score += CONDITION_INCREASE * factor
                    curr_score = self.nutrition_info[cat.ID].current_score
                    if curr_score == PREY_REQUIREMENT[str(cat.status)] * factor:
                        self.nutrition_info[cat.ID].current_score = self.nutrition_info[cat.ID].max_score
                    else: 
                        # increase the current score relevant to the existing one
                        new_score = curr_score / PREY_REQUIREMENT[str(cat.status)] * (PREY_REQUIREMENT[str(cat.status)] + CONDITION_INCREASE * factor)
                        self.nutrition_info[cat.ID].current_score = new_score
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
        nutrition.percentage = 100

        # adapt sickness (increase needed amount)
        injured_not_pregnant = (cat.is_injured() and "pregnant" not in cat.injuries) or len(cat.injuries) > 1
        if cat.is_ill() or injured_not_pregnant:
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
FRESHKILL_EVENT_TRIGGER_FACTOR = game.prey_config["event_trigger_factor"]
MAL_PERCENTAGE = game.prey_config["nutrition_malnourished_percentage"]
STARV_PERCENTAGE = game.prey_config["nutrition_starving_percentage"]

FRESHKILL_ACTIVE = game.prey_config["activate_death"]
FRESHKILL_EVENT_ACTIVE = game.prey_config["activate_events"]