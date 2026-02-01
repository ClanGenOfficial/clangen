import random
from typing import List

import i18n

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.cat.skills import SkillPath
from scripts.game_structure import game, constants
from scripts.clan_package.settings import get_clan_setting
from scripts.clan_package.get_clan_cats import get_alive_clan_queens


class Nutrition:
    """All the information about nutrition from one cat."""

    def __init__(self) -> None:
        """Initialize the class."""
        self.max_score = 1
        self.current_score = 0
        self.percentage = 0
        self.nutrition_text = "default text"

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
        self.percentage = self._current_score / self.max_score * 100
        text_config = constants.PREY_CONFIG["text_nutrition"]
        self.nutrition_text = text_config["text"][0]
        for index in range(len(text_config["lower_range"])):
            if self.percentage >= text_config["lower_range"][index]:
                self.nutrition_text = i18n.t(
                    f"conditions.nutrition.{text_config['text'][index]}"
                )


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
            total = 0
            for k, v in pile.items():
                total += v
            self.total_amount = total
        else:
            self.pile = {
                "expires_in_4": constants.PREY_CONFIG["start_amount"],
                "expires_in_3": 0,
                "expires_in_2": 0,
                "expires_in_1": 0,
            }
            self.total_amount = constants.PREY_CONFIG["start_amount"]
        self.timeskip_feed = False
        self.nutrition_info = {}
        self.living_cats = []
        self.already_fed = []
        self.needed_prey = 0

        self.fed_kits = []
        self.queens = []
        self.is_manual_feeding = False

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
        self.total_amount = round(self.total_amount, 2)

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

    def update_total_amount(self):
        """
        Update the total amount of the prey pile
        """
        self.total_amount = sum(self.pile.values())

    def _update_needed_food(self, living_cats: List[Cat]) -> None:
        queen_dict, living_kits = get_alive_clan_queens(self.living_cats)
        relevant_queens = []
        # kits under 3 months are feed by the queen
        for queen_id, their_kits in queen_dict.items():
            queen = Cat.fetch_cat(queen_id)
            if queen and not queen.status.alive_in_player_clan:
                continue
            young_kits = [kit for kit in their_kits if kit.moons < 3]
            if len(young_kits) > 0:
                relevant_queens.append(queen)
        pregnant_cats = [
            cat
            for cat in living_cats
            if "pregnant" in cat.injuries
            and cat.ID not in queen_dict.keys()
            and cat.status.alive_in_player_clan
        ]

        # all normal status cats calculation
        needed_prey = sum(
            [
                PREY_REQUIREMENT[cat.status.rank]
                for cat in living_cats
                if not cat.status.rank.is_baby() and cat.status.alive_in_player_clan
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
            PREY_REQUIREMENT["queen/pregnant"] - PREY_REQUIREMENT[CatRank.WARRIOR]
        )
        # increase the number of prey for kits, which are not taken care by a queen
        needed_prey += sum(
            [
                PREY_REQUIREMENT[cat.status.rank]
                for cat in living_kits
                if cat.status.alive_in_player_clan
            ]
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
                event_list.append(i18n.t("hardcoded.expired_prey", count=amount))
        self.total_amount = sum(self.pile.values())
        value_diff = self.total_amount
        self.timeskip_feed = True
        self.already_fed = []
        self.feed_cats(living_cats)
        self.timeskip_feed = False
        value_diff -= sum(self.pile.values())
        event_list.append(i18n.t("hardcoded.consumed_prey", count=value_diff))
        self._update_needed_food(living_cats)
        self.update_total_amount()

    def feed_cats(self, cats_to_feed: list, is_manual_feeding=False) -> None:
        """
        Takes given cats and feeds them according to chosen tactics.

        :param cats_to_feed: List of cat objects to feed
        :param is_manual_feeding: If True, cats will only have nutrition added, not removed as they would on timeskip
        """
        self.update_nutrition(cats_to_feed)

        self.is_manual_feeding = is_manual_feeding

        self.fed_kits, self.queens = self._find_kitten_and_queen(cats_to_feed)

        # PRIORITIES
        if get_clan_setting("sick_injured_first"):
            self._feed_sick_injured(cats_to_feed)
        elif get_clan_setting("hunter_first"):
            self._feed_hunters(cats_to_feed)

        if get_clan_setting("youngest_first"):
            self._feed_by_age(cats_to_feed)
        elif get_clan_setting("oldest_first"):
            self._feed_by_age(cats_to_feed, feed_oldest_first=True)
        elif get_clan_setting("hungriest_first"):
            self._feed_by_hungry_first(cats_to_feed)
        elif get_clan_setting("experience_first"):
            self._feed_by_experience_first(cats_to_feed)
        elif get_clan_setting("high_rank"):
            self._feed_by_rank(cats_to_feed, feed_high_rank_first=True)
        else:  # only remaining tactic is low_rank, this is our default!
            self._feed_by_rank(cats_to_feed)

        self.is_manual_feeding = False
        self.fed_kits.clear()
        self.queens.clear()

    def amount_food_needed(self):
        """Get the amount of freshkill the clan needs.

        :return int|float needed_prey: The amount of prey the Clan needs
        """
        living_cats = [
            cat for cat in Cat.all_cats.values() if cat.status.alive_in_player_clan
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

    @staticmethod
    def _find_kitten_and_queen(cats_to_feed) -> tuple[list, list]:
        """
        Helper to find queens, fed kittens, and pregnant cats.
        :param cats_to_feed: List of cat objects to search through
        :return: List of kittens who have been fed by a queen and list of queens/pregnant cats
        """
        fed_kits = []
        relevant_queens = []

        # finding queens and their kits
        queen_dict, kits = get_alive_clan_queens(cats_to_feed)
        for queen_id, their_kits in queen_dict.items():
            queen = Cat.fetch_cat(queen_id)
            # kits under 3 months are feed by the queen
            young_kits = [kit for kit in their_kits if kit.moons < 3]
            if len(young_kits) > 0:
                fed_kits.extend(young_kits)
                relevant_queens.append(queen)

        # finding pregnant cats
        pregnant_cats = [
            cat
            for cat in cats_to_feed
            if "pregnant" in cat.injuries and cat.ID not in queen_dict.keys()
        ]
        relevant_queens.extend(pregnant_cats)
        return fed_kits, relevant_queens

    def _feed_by_rank(
        self, cats_to_feed: List[Cat], feed_high_rank_first: bool = False
    ) -> None:
        """Feed cats in order of rank, resolving ties by age.

        :param list cats_to_feed: Cats to feed
        :param feed_high_rank_first: If True, feeds from high rank to low. If False, the reverse.
        """
        feed_order = FEEDING_ORDER.copy()
        if feed_high_rank_first:
            feed_order.reverse()

        for feeding_status in feed_order:
            if feeding_status == "queen/pregnant":
                relevant_group = self.queens

            elif CatRank(feeding_status).is_baby():
                relevant_group = [
                    cat
                    for cat in cats_to_feed
                    if cat.status.rank == feeding_status and cat not in self.fed_kits
                ]

            else:
                relevant_group = [
                    cat
                    for cat in cats_to_feed
                    if cat.status.rank == feeding_status and cat not in self.queens
                ]

            if len(relevant_group) == 0:
                continue

            sorted_group = sorted(relevant_group, key=lambda x: x.moons)
            self._feed_group(sorted_group)

    def _feed_by_age(
        self, cats_to_feed: List[Cat], feed_oldest_first: bool = False
    ) -> None:
        """Feed cats in order of age, youngest first.

        :param list cats_to_feed: Cats to feed
        :param feed_oldest_first: If True, feeds from oldest to youngest. If False, the reverse.
        """
        sorted_cats = sorted(
            cats_to_feed, key=lambda x: x.moons, reverse=feed_oldest_first
        )
        self._feed_group(sorted_cats)

    def _feed_by_hungry_first(self, cats_to_feed: List[Cat]) -> None:
        """Feed cats in order of nutrition, lowest first.

        :param list cats_to_feed: Cats to feed
        """
        if len(cats_to_feed) == 0:
            return

        # find who's hungry and who isn't
        hungry_cats = []
        satisfied_cats = []
        for cat in cats_to_feed:
            if self.nutrition_info[cat.ID].percentage < 100:
                hungry_cats.append(cat)
            else:
                satisfied_cats.append(cat)

        # if there are no low nutrition cats, default to rank tactic
        if not hungry_cats:
            self._feed_by_rank(cats_to_feed)
            return

        # sort the hungry
        hungry_cats_sorted = sorted(
            list(hungry_cats), key=lambda x: self.nutrition_info[x.ID]
        )

        self._feed_group(hungry_cats_sorted)
        # feed the rest according to their status
        self._feed_by_rank(satisfied_cats)

    def _feed_by_experience_first(self, cats_to_feed: List[Cat]) -> None:
        """Feed cats in order of experience, highest first.

        :param list cats_to_feed: Cats to feed
        """
        sorted_cats = sorted(cats_to_feed, key=lambda x: x.experience, reverse=True)
        self._feed_group(sorted_cats)

    def _feed_hunters(self, cats_to_feed: List[Cat]) -> None:
        """Feed cats with the hunter skill.

        :param list cats_to_feed: Cats to feed
        """
        best_hunter = []
        for search_rank in range(1, 4):
            for cat in cats_to_feed.copy():
                if not cat.skills:
                    continue
                if (
                    cat.skills.primary
                    and cat.skills.primary.path == SkillPath.HUNTER
                    and cat.skills.primary.tier == search_rank
                ):
                    best_hunter.insert(0, cat)
                    cats_to_feed.remove(cat)
                elif (
                    cat.skills.secondary
                    and cat.skills.secondary.path == SkillPath.HUNTER
                    and cat.skills.secondary.tier == search_rank
                ):
                    best_hunter.insert(0, cat)
                    cats_to_feed.remove(cat)

        self._feed_group(best_hunter)

    def _feed_sick_injured(self, cats_to_feed: List[Cat]) -> None:
        """Feed injured cats.

        :param list cats_to_feed: Cats to feed
        """
        sick_cats = [cat for cat in cats_to_feed if cat.is_ill() or cat.is_injured()]
        self._feed_group(sick_cats)

    # ---------------------------------------------------------------------------- #
    #                               helper functions                               #
    # ---------------------------------------------------------------------------- #

    def _feed_group(self, group: list) -> None:
        """Feed a group of cats.

        :param list group: Cats to feed
        """
        if len(group) == 0:
            return

        ration_prey = get_clan_setting("ration_prey")

        for cat in group:
            # if already fed, get'em outta here
            if cat in self.already_fed:
                continue

            rank = cat.status.rank

            # check if this is a kit: if so, check if they were fed by the mother
            if rank.is_baby() and cat in self.fed_kits:
                # SKIP they're already fed
                continue

            # check for queens/pregnant
            if cat in self.queens:
                rank = "queen/pregnant"

            prey_required = PREY_REQUIREMENT[rank]
            amount_allowed = prey_required

            total_required_food_for_clan = self.amount_food_needed()

            # if rationing, halve the amount we give them
            if ration_prey and rank != CatRank.NEWBORN:
                amount_allowed = amount_allowed / 2
            # otherwise, they can receive bonus amounts if the current total prey the Clan possesses is more than what they need
            elif (
                self.total_amount > total_required_food_for_clan * 2
                and self.nutrition_info[cat.ID].percentage < 100
            ):
                amount_allowed += 2
            elif (
                self.total_amount > total_required_food_for_clan * 1.8
                and self.nutrition_info[cat.ID].percentage < 100
            ):
                amount_allowed += 1.5
            elif (
                self.total_amount > total_required_food_for_clan * 1.2
                and self.nutrition_info[cat.ID].percentage < 100
            ):
                amount_allowed += 1
            elif (
                self.total_amount > total_required_food_for_clan
                and self.nutrition_info[cat.ID].percentage < 100
            ):
                amount_allowed += 0.5

            self.__feed_individual(cat, amount_allowed, prey_required)

    def __feed_individual(self, cat: Cat, amount_allowed, prey_required) -> None:
        """
        Feeds a single cat

        :param cat: Cat to feed
        :param amount_allowed: Amount allowed for the cat
        :param prey_required: Monthly prey requirement for this cat
        """
        ration_deficit = prey_required - amount_allowed

        # here we feed the cat from the pile! we eat the prey soonest to expire first
        # if we get through all the expiration groups, and we still need prey, then there was no prey left
        order_of_expiration = [
            "expires_in_1",
            "expires_in_2",
            "expires_in_3",
            "expires_in_4",
        ]
        amount_still_needed = amount_allowed
        for pile in order_of_expiration:
            amount_still_needed = self.take_from_pile(pile, amount_still_needed)
        # even if the cat isn't full, they have eaten, so they go in this list!
        self.already_fed.append(cat)

        # if the player is manually feeding, then we won't decrease scores at all
        # instead we just add what was available
        if self.is_manual_feeding:
            self.nutrition_info[cat.ID].current_score += (
                amount_allowed - amount_still_needed
            )
        # if the cat didn't get all the food they were allowed, then we update their nutrition score accordingly
        elif amount_still_needed > 0:
            self.nutrition_info[cat.ID].current_score -= amount_still_needed
            # if they had a ration deficit, then we also remove that from the nutrition score
            if ration_deficit > 0:
                self.nutrition_info[cat.ID].current_score -= ration_deficit

        # otherwise, we add to their score if they were already hungry
        elif self.nutrition_info[cat.ID].percentage < 100:
            # this is amount_allowed - prey_required bc the prey_required is assumed to be eaten just to maintain their current_score.
            # any extra food beyond that prey_required amount will be able to increase the current_score.
            self.nutrition_info[cat.ID].current_score += amount_allowed - prey_required

        # if they ate all they were allowed and were not hungry to begin with, but weren't allowed their full prey requirement
        # then we need to remove the deficit between what they should have had and what they ended up with
        elif ration_deficit > 0:
            self.nutrition_info[cat.ID].current_score -= ration_deficit

        # if they fulfilled their prey requirement and weren't hungry to begin with, then their nutrition score is left alone

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
        if self.timeskip_feed and not get_clan_setting("auto_feed"):
            return given_amount

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
        self.total_amount = round(self.total_amount, 2)

        return remaining_amount

    # ---------------------------------------------------------------------------- #
    #                              nutrition relevant                              #
    # ---------------------------------------------------------------------------- #

    def update_nutrition(self, cats_to_feed: list) -> None:
        """
        Handles increasing or decreasing the max score of their nutrition
        depending on their age. Automatically removes irrelevant cats.

            Parameters
            ----------
            cats_to_feed : list
                the list of the current living cats, where the nutrition should be stored
        """
        queen_dict, kits = get_alive_clan_queens(self.living_cats)

        # removing unnecessary cats
        remove = []
        for cat_id in self.nutrition_info:
            if not Cat.fetch_cat(cat_id).status.alive_in_player_clan:
                remove.append(cat_id)

        for cat_id in remove:
            self.nutrition_info.pop(cat_id)

        # update remaining cat's max scores
        for cat in cats_to_feed:
            if str(cat.status.rank) not in PREY_REQUIREMENT:
                continue
            # update the nutrition_info
            if cat.ID in self.nutrition_info:
                factor = 3
                status_ = str(cat.status.rank)
                if cat.status.rank.is_baby() or (
                    cat.moons > 114 and str(cat.status.rank) == CatRank.ELDER
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
        if cat.status.rank in [CatRank.NEWBORN, CatRank.KITTEN, CatRank.ELDER]:
            factor = 2

        queen_dict, kits = get_alive_clan_queens(self.living_cats)
        prey_status = cat.status.rank
        if cat.ID in queen_dict.keys() or "pregnant" in cat.injuries:
            prey_status = "queen/pregnant"
        max_score = PREY_REQUIREMENT[prey_status] * factor
        nutrition.max_score = max_score
        nutrition.current_score = max_score
        nutrition.percentage = 100

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


ADDITIONAL_PREY = constants.PREY_CONFIG["additional_prey"]
PREY_REQUIREMENT = constants.PREY_CONFIG["prey_requirement"]
CONDITION_INCREASE = constants.PREY_CONFIG["condition_increase"]
FEEDING_ORDER = constants.PREY_CONFIG["feeding_order"]
HUNTER_BONUS = constants.PREY_CONFIG["hunter_bonus"]
HUNTER_EXP_BONUS = constants.PREY_CONFIG["hunter_exp_bonus"]
FRESHKILL_EVENT_TRIGGER_FACTOR = constants.PREY_CONFIG["base_event_trigger_factor"]
MAL_PERCENTAGE = constants.PREY_CONFIG["nutrition_malnourished_percentage"]
STARV_PERCENTAGE = constants.PREY_CONFIG["nutrition_starving_percentage"]

FRESHKILL_ACTIVE = constants.PREY_CONFIG["activate_death"]
FRESHKILL_EVENT_ACTIVE = constants.PREY_CONFIG["activate_events"]
