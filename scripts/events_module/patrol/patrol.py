#!/usr/bin/env python3
# -*- coding: ascii -*-
import logging
import random
import statistics
from os.path import exists as path_exists
from random import choice, randint, choices
from typing import List, Tuple, Optional, Union, Literal, TypedDict

import pygame

from scripts.cat.cats import Cat
from scripts.cat_relations.enums import RelType
from scripts.cat.enums import CatAge, CatRank, CatCompatibility
from scripts.clan import get_temper_alignment
from scripts.config import get_config
from scripts.events_module.consequences import gather_cat_objects
from scripts.events_module.event_filters import (
    check_relationship_value,
    get_personality_compatibility,
    event_for_poi,
    check_rel_constraint_groups,
)
from scripts.events_module.patrol.create_new_cat import updated_create_new_cat
from scripts.events_module.patrol.enums import PatrolChoice
from scripts.events_module.patrol.generate_patrol_list import (
    get_patrol_list,
    will_allow_outsider_patrols,
)
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event import handle_consequences
from scripts.events_module.text_pool_event.check_general_constraints import (
    passes_general_constraints,
)
from scripts.events_module.text_pool_event.event_retrieval import get_valid_event
from scripts.events_module.text_pool_event.find_involved_cats import find_cats
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure import game
from scripts.events_module.text_adjust import (
    event_text_adjust,
)
from scripts.special_dates import SpecialDate, is_today


logger = logging.getLogger(__name__)


def get_patrol_temperament(patrol_cats: list, patrol_leader=None) -> tuple[str, str]:
    """
    Determines the temperament of a patrol based on clan rank and patrol_leader
    """
    sociability, aggression, lawfulness, stability = [], [], [], []

    for cat in patrol_cats:
        rank = cat.status.rank
        if rank == CatRank.LEADER:
            weight = 3
        elif rank == CatRank.DEPUTY:
            weight = 2
        else:  # medicine cat and all others
            weight = 1
        if patrol_leader is not None and cat == patrol_leader:
            weight += 1

        sociability += [cat.personality.sociability] * weight
        aggression += [cat.personality.aggression] * weight
        lawfulness += [cat.personality.lawfulness] * weight
        stability += [cat.personality.stability] * weight

    if not sociability:  # empty patrol guard
        return "", ""

    return get_temper_alignment(
        round(statistics.mean(sociability)),
        round(statistics.mean(aggression)),
        round(statistics.mean(lawfulness)),
        round(statistics.mean(stability)),
    )


class Patrol:
    used_patrols = {"romance": [], "normal": []}

    def __init__(self):
        self.patrol_event: Optional[PatrolEvent] = None
        self.debug_patrol_id: str = ""
        self.other_clan = None
        self.temperament: tuple[str, str] = ("", "")
        """Set once the patrol cats are known, in begin_patrol"""

        self.patrol_cats: list[Cat] = []
        """Holds all the cats that are on the patrol"""
        self.involved_cats: dict[str, Union[list[Cat], Cat]] = {}
        """Cats directly involved and referenced in the event. Keys are their text abbreviation, values are the associated cat objects"""
        self.outcome_cats: TypedDict(
            "outcome_cats", {"success": dict[str, Cat], "failure": dict[str, Cat]}
        ) = {"success": {}, "failure": {}}

    def begin_patrol(self, patrol_cats: List[Cat], patrol_type: str) -> str:
        """
        Handles all the initial patrol setup, returns the prepared patrol intro text.
        :param patrol_cats: All cats that have been chosen for this patrol
        :param patrol_type: Type of patrol
        """
        self.debug_patrol_id = get_config("patrol_generation.debug_ensure_patrol_id")

        print("PATROL START ---------------------------------------------------")

        # Add cats
        self._add_patrol_cats(patrol_cats)

        # The patrol group can't change once it's set out, so this is fixed for the rest of the patrol
        self.temperament = get_patrol_temperament(
            self.patrol_cats, self.involved_cats.get("p_l")
        )

        # Choose other clan
        if game.clan.all_other_clans and len(game.clan.all_other_clans) > 0:
            self.other_clan = choice(game.clan.all_other_clans)
        else:
            self.other_clan = None

        # Find valid patrol
        self.patrol_event = self._get_possible_patrol(patrol_type)

        # Return text adjusted patrol intro
        return event_text_adjust(
            Cat,
            self.patrol_event.intro_text,
            involved_cat_dict=self.involved_cats,
            clan=game.clan,
            other_clan=self.other_clan,
        )

    def proceed_patrol(
        self, path: PatrolChoice = PatrolChoice.PROCEED
    ) -> Tuple[str, str, list, pygame.Surface | None]:
        """Proceed the patrol to the next step."""

        if path == PatrolChoice.DECLINE:
            if self.patrol_event:
                print(
                    f"PATROL ID: {self.patrol_event.event_id} | SUCCESS: N/A (did not proceed)"
                )
                return (
                    event_text_adjust(
                        Cat,
                        self.patrol_event.decline_text,
                        involved_cat_dict=self.involved_cats,
                        clan=game.clan,
                        other_clan=self.other_clan,
                    ),
                    "",
                    [],
                    None,
                )
            else:
                return "Error - no event chosen", "", [], None

        return self.determine_outcome(antagonize=(path == PatrolChoice.ANTAGONIZE))

    def _add_patrol_cats(self, patrol_cats: List[Cat]) -> None:
        """
        Sorts and categorizes patrol cats, then determines a patrol leader.
        :param patrol_cats: list of cats which are on the patrol
        """
        # ADD TO PATROL_CATS

        self.patrol_cats = patrol_cats
        for cat in patrol_cats:
            # ADD TO STATUS LIST
            if cat.status.rank in self.involved_cats:
                self.involved_cats[cat.status.rank].append(cat)
            else:
                self.involved_cats[cat.status.rank] = [cat]

            # Combined patrol_statuses categories
            if cat.status.rank.is_any_medicine_rank():
                if "healer cats" in self.involved_cats:
                    self.involved_cats["healer cats"].append(cat)
                else:
                    self.involved_cats["healer cats"] = [cat]

            if cat.status.rank.is_any_apprentice_rank():
                if "all apprentices" in self.involved_cats:
                    self.involved_cats["all apprentices"].append(cat)
                else:
                    self.involved_cats["all apprentices"] = [cat]

            if (
                cat.status.rank.is_any_adult_warrior_like_rank()
                and cat.age != CatAge.ADOLESCENT
            ):
                if "normal adult" in self.involved_cats:
                    self.involved_cats["normal adult"].append(cat)
                else:
                    self.involved_cats["normal adult"] = [cat]

            game.patrolled.append(cat.ID)

        # DETERMINE PATROL LEADER
        # THIS CANNOT CHANGE AFTER SET-UP
        # sets medcat as patrol leader if they're in the patrol
        if CatRank.MEDICINE_CAT in self.involved_cats.keys():
            possible_leads = self.involved_cats[CatRank.MEDICINE_CAT]

        # If there is no medicine cat, but there is a medicine cat apprentice, set them as the patrol leader.
        # This prevents warriors from being treated as medicine cats in medicine cat patrols.
        elif CatRank.MEDICINE_APPRENTICE in self.involved_cats.keys():
            possible_leads = self.involved_cats[CatRank.MEDICINE_APPRENTICE]

        # if no meddies set leader as patrol leader
        elif CatRank.LEADER in self.involved_cats.keys():
            possible_leads = self.involved_cats[CatRank.LEADER]

        # if no leader set the deputy as patrol leader
        elif CatRank.DEPUTY in self.involved_cats.keys():
            possible_leads = self.involved_cats[CatRank.DEPUTY]

        # if not deputy, try warriors
        elif CatRank.WARRIOR in self.involved_cats.keys():
            possible_leads = self.involved_cats[CatRank.WARRIOR]
        # if no warriors, set oldest or most experienced of any cats as patrol lead
        else:
            possible_leads = self.patrol_cats

        # Flip a coin to pick the most experienced or the oldest.
        if randint(0, 1):
            possible_leads.sort(key=lambda x: x.moons)
        else:
            possible_leads.sort(key=lambda x: x.experience)

        self.involved_cats["p_l"] = possible_leads[-1]
        self.involved_cats["patrol_cats"] = patrol_cats

        print("Patrol Leader:", str(self.involved_cats["p_l"].name))

    def _get_possible_patrol(
        self,
        patrol_type: str,
    ) -> PatrolEvent:
        # ---------------------------------------------------------------------------- #
        #                                LOAD RESOURCES                                #
        # ---------------------------------------------------------------------------- #

        # this is needed for Classic specifically
        # Classic doesn't let you pick patrol type, so instead we specify herb_gathering if meddies are present
        patrol_type = (
            "herb_gathering"
            if {CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE}.intersection(
                set(self.involved_cats.keys())
            )
            else patrol_type
        )
        # This make sure general only gets hunting, border, or training patrols
        if patrol_type == "general":
            # choosing a type now means that the type of patrol later chosen isn't influenced
            # by the amount of patrols available of that type
            patrol_type = random.choice(["hunting", "border", "training"])

        # GET PATROL LIST
        patrol_list = get_patrol_list(
            patrol_type,
            outsider_rep=will_allow_outsider_patrols(
                small_clan=int(len(game.clan.clan_cats))
                < get_config("patrol_generation.small_clan_threshold")
            ),
            other_clan_rep=self.other_clan.get_standing(),
        )

        # INFORM -NOT PRESENT-
        patrol_ids = [patrol.event_id for patrol in patrol_list]
        if self.debug_patrol_id and self.debug_patrol_id not in patrol_ids:
            print(
                "DEBUG: requested patrol not present (check spelling/mismatched season, biome, patrol type, new cat flag, other clan relations, disaster setting)"
            )

        # DEBUG - NO FILTER
        # This is a debug option, this allows you to remove any constraints of a patrol regarding location, session, biomes, etc.
        if constants.CONFIG["patrol_generation"][
            "debug_override_patrol_stat_requirements"
        ]:
            if self.debug_patrol_id:
                chosen_patrol = [
                    p for p in patrol_list if p.event_id == self.debug_patrol_id
                ][0]
            else:
                chosen_patrol = choice(patrol_list)
            print(
                "All patrol filters regarding location, session, etc. have been removed."
            )
        # FILTER PATROLS when no debug set
        else:
            chosen_patrol = self._filter_patrols(patrol_list, patrol_type)

        return chosen_patrol

    def _decide_if_romantic(self, romantic_event: Optional[PatrolEvent]) -> bool:
        """
        Finds the chance of this patrol being romantic based on the cats involved and their current relationship with each other
        :return: True if patrol should be romantic, False otherwise
        """

        if not romantic_event:
            print("No romantic event")
            return False

        chance_of_romance_patrol = get_config(
            "patrol_generation.chance_of_romance_patrol"
        )

        for block in romantic_event.relationship_constraint:
            if "can_romance" in block["constraints"]:
                # gather the kitty cats
                cats_from = gather_cat_objects(
                    Cat,
                    block["cats_from"],
                    event=self,
                    involved_cats=self.involved_cats,
                )
                cats_to = gather_cat_objects(
                    Cat, block["cats_to"], event=self, involved_cats=self.involved_cats
                )
                # now affect the chance depending on the compatibility
                for c in cats_from:
                    compatibility = [
                        get_personality_compatibility(c, love_cat)
                        for love_cat in cats_to
                        if love_cat != c
                    ]
                    for compat in compatibility:
                        if compat == CatCompatibility.POSITIVE:
                            chance_of_romance_patrol -= 5
                        elif compat == CatCompatibility.NEGATIVE:
                            chance_of_romance_patrol += 5

                    rel_values = [
                        check_relationship_value(c, love_cat, val)
                        for val in [*RelType]
                        for love_cat in cats_to
                        if love_cat != c
                    ]
                    for v in rel_values:
                        if v > 0:
                            chance_of_romance_patrol -= 1
                        else:
                            chance_of_romance_patrol += 1

        if chance_of_romance_patrol <= 0:
            chance_of_romance_patrol = 1
        print("final romance chance:", chance_of_romance_patrol)
        return not int(random.random() * chance_of_romance_patrol)

    def _filter_patrols(
        self,
        possible_patrols: List[PatrolEvent],
        patrol_type: str,
    ) -> PatrolEvent:
        # GET POSSIBLE PATROLS
        # run the first set of really basic constraint filtering, just to get our base of valid patrols
        possible_patrols = [
            p
            for p in possible_patrols
            if self._patrol_pass_basic_constraints(
                p, patrol_type, is_debug_patrol=p.event_id == self.debug_patrol_id
            )
        ]
        # make sure the hunting patrols are balanced
        if patrol_type == "hunting" and not self.debug_patrol_id:
            possible_patrols = self.balance_hunting(possible_patrols)

        # separate into the two lists
        normal_patrols: list[PatrolEvent] = []
        romantic_patrols: list[PatrolEvent] = []
        for p in possible_patrols:
            if "romance" in p.tags:
                romantic_patrols.append(p)
            else:
                normal_patrols.append(p)

        print(
            f"Total Number of Possible Patrols | normal: {len(normal_patrols)}, romantic: {len(romantic_patrols)} "
        )

        # GET PATROL
        chosen_patrol: Optional[PatrolEvent] = None

        # first we see if we can get a romantic patrol
        if romantic_patrols and not self.debug_patrol_id:
            chosen_patrol = self._get_valid_patrol(
                romantic_patrols.copy(), find_romance=True
            )

        # if no romantic patrol possible, we get a normal one!
        if not chosen_patrol:
            chosen_patrol = self._get_valid_patrol(
                normal_patrols.copy(), find_romance=False
            )
            if not chosen_patrol:
                raise Exception(
                    "ERROR: No patrols could be found, even after resetting the used patrol list."
                )

        return chosen_patrol

    def _clear_used_and_retry(
        self, possible_patrols: List[PatrolEvent], find_romance: bool = False
    ):
        """
        Clears used patrols and attempts to get a new valid patrol
        """
        Patrol.used_patrols["romance" if find_romance else "normal"].clear()

        return self._get_valid_patrol(possible_patrols, find_romance)

    def _get_valid_patrol(
        self, possible_patrols: List[PatrolEvent], find_romance: bool = False
    ) -> Optional[PatrolEvent]:
        chosen_patrol = None
        patrols_to_test = [
            p
            for p in possible_patrols
            if p.event_id
            not in Patrol.used_patrols["romance" if find_romance else "normal"]
        ]
        while not chosen_patrol:
            chosen_patrol, involved_cats = get_valid_event(
                primary_cat=self.involved_cats["p_l"],
                involved_cats=self.involved_cats,
                interactable_cats=[
                    c
                    for c in self.involved_cats["patrol_cats"]
                    if c != self.involved_cats["p_l"]
                ],
                possible_events=patrols_to_test,
                other_clan=self.other_clan,
                ensured_id=self.debug_patrol_id,
                general_constraints_active=False,
            )
            if not chosen_patrol:
                if not Patrol.used_patrols["romance" if find_romance else "normal"]:
                    # No patrols found even after resetting used patrols.
                    # This should only be possible when filtering for romance patrols.
                    return None

                # if we couldn't find a patrol, then we need to clear the used_patrols and try again
                chosen_patrol = self._clear_used_and_retry(
                    possible_patrols, find_romance=find_romance
                )
            else:
                # otherwise, let's set our involved cats and move on with this patrol!
                self.involved_cats = involved_cats

        if find_romance:
            if not self._decide_if_romantic(chosen_patrol):
                return None
            Patrol.used_patrols["romance"].append(chosen_patrol.event_id)
        else:
            Patrol.used_patrols["normal"].append(chosen_patrol.event_id)

        return chosen_patrol

    def _patrol_pass_basic_constraints(
        self, patrol: PatrolEvent, patrol_type: str, is_debug_patrol: bool
    ) -> bool:
        # CHECK PATROL TYPE
        if patrol_type not in patrol.types:
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (patrol type)")
            return False

        # CHECK GENERAL
        if not passes_general_constraints(
            patrol,
            self.involved_cats["p_l"],
            self.involved_cats,
            self.other_clan,
            is_debug_patrol,
        ):
            return False

        # CHECK POI
        if not event_for_poi(patrol.poi):
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (PoI)")
            return False

        # CHECK NEEDED HERBS
        if patrol_type == "herb_gathering":
            # skip this if it's a debug patrol
            if is_debug_patrol:
                return True

            target_herbs = game.clan.herb_supply.sorted_by_need

            # if any herb can happen, then we return True
            if "random_herbs" in patrol.herbs_given:
                return True

            # if the patrol is not able to give herbs we need, we return False
            if not set(patrol.herbs_given).intersection(set(target_herbs)):
                return False

        return True

    def _find_allowed_outcomes(
        self, antagonize: bool = False
    ) -> tuple[TextPoolEvent, TextPoolEvent]:
        """
        Filters through possible outcomes to find appropriate outcomes for both failure and success
        :param antagonize: set True if the player chose to antagonize
        :return: success outcome, failure outcome
        """

        # find which set of outcomes we'll be using based on if the player choose to antagonize
        if antagonize:
            success_outcomes = self.patrol_event.antag_success_outcomes
            fail_outcomes = self.patrol_event.antag_fail_outcomes
        else:
            success_outcomes = self.patrol_event.success_outcomes
            fail_outcomes = self.patrol_event.fail_outcomes

        # we'll get an outcome for both success and failure
        # FIND SUCCESS
        chosen_success, self.outcome_cats["success"] = get_valid_event(
            primary_cat=self.involved_cats["p_l"],
            involved_cats=self.involved_cats,
            interactable_cats=[
                c
                for c in self.involved_cats["patrol_cats"]
                if c != self.involved_cats["p_l"]
            ],
            possible_events=success_outcomes,
            other_clan=self.other_clan,
        )

        if not chosen_success:
            raise Exception(
                f"Valid success outcome could not be found for {self.patrol_event.event_id}"
            )

        # FIND FAILURE
        chosen_failure, self.outcome_cats["failure"] = get_valid_event(
            primary_cat=self.involved_cats["p_l"],
            involved_cats=self.involved_cats,
            interactable_cats=[
                c
                for c in self.involved_cats["patrol_cats"]
                if c != self.involved_cats["p_l"]
            ],
            possible_events=fail_outcomes,
            other_clan=self.other_clan,
        )
        if not chosen_failure:
            raise Exception(
                f"Valid fail outcome could not be found for {self.patrol_event.event_id}"
            )

        return chosen_success, chosen_failure

    def _check_outcome_constraints(
        self, outcome: TextPoolEvent, outcome_type: Literal["success", "failure"]
    ) -> bool:
        """
        Checks the outcome constraints and attempts to find appropriate cats. If the outcome is valid and cats are
        found, the cats will be added to the matching `self.outcome_cats` dict
        :param outcome: outcome to check
        :param outcome_type: the outcome_cats dict that the valid cats should be added to
        """
        # BASICS
        if not passes_general_constraints(
            outcome, self.involved_cats["p_l"], self.involved_cats
        ):
            return False

        # CATS
        outside_cats = [
            c
            for c in Cat.all_cats_list
            if (c.status.is_other_clancat or c.status.is_outsider) and not c.dead
        ]
        temp_involved_cats = self.involved_cats.copy()

        temp_involved_cats = find_cats(
            interactable_cats=temp_involved_cats["patrol_cats"],
            involved_cats=temp_involved_cats,
            outside_cats=outside_cats,
            event=outcome,
            other_clan=self.other_clan,
        )
        if not temp_involved_cats:
            return False

        # if we're here, then we must have found all our cats!
        self.outcome_cats[outcome_type] = temp_involved_cats

        return True

    def determine_outcome(
        self, antagonize=False
    ) -> Tuple[str, str, list, pygame.Surface | None]:
        if self.patrol_event is None:
            raise Exception("No patrol event supplied")

        success_outcome, fail_outcome = self._find_allowed_outcomes(antagonize)

        chosen_outcome, success = self.calculate_success(success_outcome, fail_outcome)

        print(f"PATROL ID: {self.patrol_event.event_id} | SUCCESS: {success}")
        print(
            f"Patrol Frequency: {self.patrol_event.frequency} | Patrol Weight: {self.patrol_event.weight}"
        )
        print(
            f"Outcome Frequency: {chosen_outcome.frequency} | Outcome Weight: {chosen_outcome.weight}"
        )

        # Run the chosen outcome
        return handle_consequences.execute_outcome(
            chosen_outcome,
            self.outcome_cats["success" if success else "failure"],
            self.other_clan,
        ) + (self.get_patrol_art(chosen_outcome),)

    def calculate_success(
        self, success_outcome: TextPoolEvent, fail_outcome: TextPoolEvent
    ) -> Tuple[TextPoolEvent, bool]:
        """Returns both the chosen outcome, and a boolean that's True if success, and False if failure."""

        patrol_size = len(self.patrol_cats)
        total_exp = sum([x.experience for x in self.patrol_cats])
        path = (
            "patrol_generation.classic_difficulty_modifier"
            if game.clan.game_mode == "classic"
            else "patrol_generation.difficulty_modifier"
        )

        gm_modifier = get_config(path)

        exp_adjustment = (
            (1 + 0.10 * patrol_size) * total_exp / (patrol_size * gm_modifier * 2)
        )

        success_chance = self.patrol_event.chance_of_success + int(exp_adjustment)
        success_chance = min(success_chance, 90)

        # Now, apply success and fail skill
        print(
            "starting chance:",
            self.patrol_event.chance_of_success,
            "| EX_updated chance:",
            success_chance,
        )

        # Skill and trait stuff
        for abbr, constraints in success_outcome.involved_cats.items():
            # if this is present, then we know a cat must fulfill it
            if stat_block := constraints.get("stat"):
                cat = self.outcome_cats["success"][abbr]
                if "skill" in stat_block:
                    success_chance += get_config(
                        "patrol_generation.skill_cat_modifier"
                    ) * cat.skills.check_skill_requirement_list(stat_block["skill"])
                    print(f"success chance increase to {success_chance}")
                elif "trait" in stat_block:
                    success_chance += get_config("patrol_generation.trait_cat_modifier")
                    print(f"success chance increase to {success_chance}")

        if success_chance >= 120:
            success_chance = 115
            print("success chance over 120, updated to 115")

        success = int(random.random() * 120) < success_chance

        # This is a debug option, this will forcefully change the outcome of a patrol
        if isinstance(
            constants.CONFIG["patrol_generation"]["debug_ensure_patrol_outcome"], bool
        ):
            success = constants.CONFIG["patrol_generation"][
                "debug_ensure_patrol_outcome"
            ]
            # Logging
            print(
                f"The outcome of {self.patrol_event.event_id} was altered to {success}"
            )

        return success_outcome if success else fail_outcome, success

    def balance_hunting(self, possible_patrols: list[PatrolEvent]) -> list[PatrolEvent]:
        """
        Check which prey amount we want to allow this clan to get and filter the possible_patrols accordingly to ensure
        they only have patrols where that amount is possible.
        :param possible_patrols: The list of possible patrols
        :returns: The list of possible patrols but filtered to only include those patrols which have the chosen prey
        amount. If there were no patrols with the chosen prey amount, then the original list is returned
        """
        filtered_patrols = []

        # get first what kind of prey size which will be chosen
        biome = (
            game.clan.biome
            if not game.clan.override_biome
            else game.clan.override_biome
        )
        prey_sizes = ["tiny", "small", "medium", "large", "huge"]
        prey_size_random_weights = get_config(
            f"prey.patrol_balance.{biome}.{game.clan.current_season}"
        )

        chosen_prey_size = choices(prey_sizes, weights=prey_size_random_weights)[0]
        print(f"chosen filter prey size: {chosen_prey_size}")

        # filter all possible patrols depending on the needed prey size
        for patrol in possible_patrols:
            # count how many outcomes award each prey size
            prey_size_to_outcome_amounts = {}
            for outcome in patrol.success_outcomes:
                if outcome.supply:
                    for block in outcome.supply:
                        if block["type"] != "freshkill":
                            continue
                        outcome_prey_size = block["adjust"].replace("increase_", "")
                        if outcome_prey_size not in prey_size_to_outcome_amounts:
                            prey_size_to_outcome_amounts[outcome_prey_size] = 0
                        prey_size_to_outcome_amounts[outcome_prey_size] += 1

            # get the prey size with the most outcomes
            most_prey_size = ""
            max_occurrences = 0
            for size, amount in prey_size_to_outcome_amounts.items():
                if amount >= max_occurrences:
                    most_prey_size = size
                    max_occurrences = amount

            # if the most often awarded prey size matches the one we want, then we allow this patrol through
            if chosen_prey_size == most_prey_size:
                filtered_patrols.append(patrol)
            elif self.debug_patrol_id and self.debug_patrol_id == patrol.event_id:
                print(
                    f"DEBUG: requested patrol does not meet constraints (did not have the prey amount required for prey balancing)"
                )
        # if the filtering results in an empty list, don't filter and return whole possible patrols
        if len(filtered_patrols) <= 0:
            print(
                "---- WARNING ---- attempted prey balancing filtering, but there were no patrols with the required prey amount."
            )
            return possible_patrols

        return filtered_patrols

    def get_patrol_art(self, outcome: TextPoolEvent = None) -> Optional[pygame.Surface]:
        """Return's patrol art surface"""
        if not self.patrol_event or not isinstance(self.patrol_event.patrol_art, str):
            return pygame.Surface((600, 600), flags=pygame.SRCALPHA)

        root_dir = "resources/images/patrol_art/"

        clean_art = (
            self.patrol_event.patrol_art_clean
            if not outcome
            else outcome.outcome_art_clean
        )
        if not game_setting_get("gore") and clean_art:
            file_name = clean_art
        else:
            file_name = (
                self.patrol_event.patrol_art if not outcome else outcome.outcome_art
            )

        if not isinstance(file_name, str) or not path_exists(
            f"{root_dir}{file_name}.png"
        ):
            if outcome:
                # we return None so that we don't overwrite the patrol's general art.
                # if we got here on an outcome, then the outcome had no attached art and we should just be using
                # the patrol's general art
                return None
            if "herb_gathering" in self.patrol_event.types:
                file_name = "med"
            elif "hunting" in self.patrol_event.types:
                file_name = "hunt"
            elif "border" in self.patrol_event.types:
                file_name = "bord"
            else:
                file_name = "train"

            file_name = f"{file_name}_general_intro"

        if is_today(SpecialDate.APRIL_FOOLS):
            april_fools_root_dir = "resources/images/patrol_art/april_fools/"
            if path_exists(f"{april_fools_root_dir}{file_name}.png"):
                return pygame.image.load(f"{april_fools_root_dir}{file_name}.png")

        return pygame.image.load(f"{root_dir}{file_name}.png")
