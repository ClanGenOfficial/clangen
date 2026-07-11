#!/usr/bin/env python3
# -*- coding: ascii -*-
import logging
import random
from copy import deepcopy
from itertools import combinations
from os.path import exists as path_exists
from random import choice, randint, choices
from typing import List, Tuple, Optional, Union, Literal, TypedDict

import pygame

from scripts.cat.cats import Cat
from scripts.cat_relations.enums import RelType
from scripts.cat.enums import CatAge, CatRank, CatCompatibility
from scripts.clan import Clan
from scripts.clan_package.settings import get_clan_setting
from scripts.config import get_config
from scripts.events_module.event_filters import (
    event_for_tags,
    get_frequency,
    find_new_frequency,
    filter_relationship_type,
    check_relationship_value,
    get_personality_compatibility,
    event_for_location,
    event_for_season,
    event_for_poi,
    event_for_required_cat_types,
    event_for_cat,
    check_rel_constraint_groups,
)
from scripts.events_module.patrol.generate_patrol_list import (
    get_patrol_list,
    will_allow_outsider_patrols,
)
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.patrol.patrol_outcome import PatrolOutcome
from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure import game
from scripts.events_module.text_adjust import (
    event_text_adjust,
)
from scripts.game_structure.game.settings.settings import values
from scripts.special_dates import SpecialDate, is_today


logger = logging.getLogger(__name__)


class Patrol:
    used_patrols = []

    def __init__(self):
        self.patrol_event: Optional[PatrolEvent] = None

        self.patrol_cats: list[Cat] = []
        """Holds all the cats that are on the patrol"""
        self.patrol_statuses: dict[str, list[Cat]] = {}
        """Keys are cat statuses present on the patrol, values are lists of the cats that hold the status"""
        self.involved_cats: dict[str, Cat] = {}
        """Cats directly involved and referenced in the event. Keys are their text abbreviation, values are the associated cat objects"""

        # TODO: old attributes, might not need them all anymore
        self.random_cat = None
        self.other_clan = None
        self.intro_text = ""

        # Holds new cats for easy access
        self.new_cats: List[List[Cat]] = []

        # False if no debug patrol set, value if one is set
        self.debug_patrol_id: Union[bool, str] = False

    def begin_patrol(self, patrol_cats: List[Cat], patrol_type: str) -> str:
        """
        Handles all the initial patrol setup, returns the prepared patrol intro text.
        :param patrol_cats: All cats that have been chosen for this patrol
        :param patrol_type: Type of patrol
        """
        self.debug_patrol_id = get_config("patrol_generation.debug_ensure_patrol_id")

        print("PATROL START ---------------------------------------------------")

        # Add cats
        self.add_patrol_cats(patrol_cats)

        # Choose other clan
        if game.clan.all_other_clans and len(game.clan.all_other_clans) > 0:
            self.other_clan = choice(game.clan.all_other_clans)
        else:
            self.other_clan = None

        # Find valid patrol
        self.patrol_event = self.get_possible_patrol(patrol_type)

        Patrol.used_patrols.append(self.patrol_event.id)

        # Return text adjusted patrol intro
        return event_text_adjust(
            Cat,
            self.patrol_event.intro_text,
            patrol_leader=self.patrol_leader,
            random_cat=self.random_cat,
            patrol_cats=self.patrol_cats,
            patrol_apprentices=self.patrol_apprentices,
            new_cats=self.new_cats,
            clan=game.clan,
            other_clan=self.other_clan,
        )

    def proceed_patrol(
        self, path: Literal["proceed", "antag", "decline"] = "proceed"
    ) -> Tuple[str, str, list, Optional[str]]:
        """Proceed the patrol to the next step.
        path can be: "proceed", "antag", or "decline" """

        if path == "decline":
            if self.patrol_event:
                print(
                    f"PATROL ID: {self.patrol_event.patrol_id} | SUCCESS: N/A (did not proceed)"
                )
                return (
                    event_text_adjust(
                        Cat,
                        self.patrol_event.decline_text,
                        patrol_leader=self.patrol_leader,
                        random_cat=self.random_cat,
                        patrol_cats=self.patrol_cats,
                        patrol_apprentices=self.patrol_apprentices,
                        new_cats=self.new_cats,
                        clan=game.clan,
                        other_clan=self.other_clan,
                    ),
                    "",
                    [],
                    None,
                )
            else:
                return "Error - no event chosen", "", None

        return self.determine_outcome(antagonize=(path == "antag"))

    def add_patrol_cats(self, patrol_cats: List[Cat]) -> None:
        """
        Sorts and categorizes patrol cats, then determines a patrol leader.
        :param patrol_cats: list of cats which are on the patrol
        """
        # ADD TO PATROL_CATS

        self.patrol_cats = patrol_cats
        self.patrol_statuses["all_cats"] = patrol_cats
        for cat in patrol_cats:
            # ADD TO STATUS LIST
            if cat.status.rank in self.patrol_statuses:
                self.patrol_statuses[cat.status.rank].append(cat)
            else:
                self.patrol_statuses[cat.status.rank] = [cat]

            # Combined patrol_statuses categories
            if cat.status.rank.is_any_medicine_rank():
                if "healer cats" in self.patrol_statuses:
                    self.patrol_statuses["healer cats"].append(cat)
                else:
                    self.patrol_statuses["healer cats"] = [cat]

            if cat.status.rank.is_any_apprentice_rank():
                if "all apprentices" in self.patrol_statuses:
                    self.patrol_statuses["all apprentices"].append(cat)
                else:
                    self.patrol_statuses["all apprentices"] = [cat]

            if (
                cat.status.rank.is_any_adult_warrior_like_rank()
                and cat.age != CatAge.ADOLESCENT
            ):
                if "normal adult" in self.patrol_statuses:
                    self.patrol_statuses["normal adult"].append(cat)
                else:
                    self.patrol_statuses["normal adult"] = [cat]

            game.patrolled.append(cat.ID)

        # DETERMINE PATROL LEADER
        # THIS CANNOT CHANGE AFTER SET-UP
        # sets medcat as patrol leader if they're in the patrol
        if CatRank.MEDICINE_CAT in self.patrol_statuses.keys():
            possible_leads = self.patrol_statuses[CatRank.MEDICINE_CAT]

        # If there is no medicine cat, but there is a medicine cat apprentice, set them as the patrol leader.
        # This prevents warriors from being treated as medicine cats in medicine cat patrols.
        elif CatRank.MEDICINE_APPRENTICE in self.patrol_statuses.keys():
            possible_leads = self.patrol_statuses[CatRank.MEDICINE_APPRENTICE]

        # if no meddies set leader as patrol leader
        elif CatRank.LEADER in self.patrol_statuses.keys():
            possible_leads = self.patrol_statuses[CatRank.LEADER]

        # if no leader set the deputy as patrol leader
        elif CatRank.DEPUTY in self.patrol_statuses.keys():
            possible_leads = self.patrol_statuses[CatRank.DEPUTY]

        # if no deputy, set oldest or most experienced as patrol leader
        else:
            possible_leads = self.patrol_cats

        # Flip a coin to pick the most experienced or the oldest.
        if randint(0, 1):
            possible_leads.sort(key=lambda x: x.moons)
        else:
            possible_leads.sort(key=lambda x: x.experience)
        self.involved_cats["p_l"] = possible_leads[-1]

        print("Patrol Leader:", str(self.involved_cats["p_l"].name))

    def get_possible_patrol(
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
            if [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE]
            in self.patrol_statuses.keys()
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
                small_clan=int(len(game.clan.clan_cats)) < 20
            ),
            other_clan_rep=self.other_clan.get_standing(),
        )

        # INFORM -NOT PRESENT-
        patrol_ids = [patrol.id for patrol in patrol_list]
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
                    p for p in patrol_list if p.id == self.debug_patrol_id
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
                cats_from = [
                    c for a, c in self.involved_cats.items() if a in block["cats_from"]
                ]
                cats_to = [
                    c for a, c in self.involved_cats.items() if a in block["cats_to"]
                ]
                # now affect the chance depending on the compatibility
                for c in cats_from:
                    compatibility = [
                        get_personality_compatibility(c, love_cat)
                        for love_cat in cats_to
                    ]
                    for compat in compatibility:
                        if compat == CatCompatibility.POSITIVE:
                            chance_of_romance_patrol -= 10
                        elif compat == CatCompatibility.NEGATIVE:
                            chance_of_romance_patrol += 10

                    rel_values = [
                        check_relationship_value(c, love_cat, val)
                        for val in [*RelType]
                        for love_cat in cats_to
                    ]
                    for v in rel_values:
                        if v < 0:
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
            if self._pass_basic_constraints(
                p, patrol_type, is_debug_patrol=p.id == self.debug_patrol_id
            )
        ]
        # make sure the hunting patrols are balanced
        if patrol_type == "hunting":
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

        # GET FREQUENCY
        chosen_frequency = get_frequency()

        # always try to do the debugged ID first
        if self.debug_patrol_id:
            patrol_override = [
                p for p in possible_patrols if p.id == self.debug_patrol_id
            ][0]
            chosen_frequency = patrol_override.frequency
        else:
            patrol_override = None

        # GET PATROL
        chosen_patrol: Optional[PatrolEvent] = None

        # first we see if we can get a romantic patrol
        if romantic_patrols:
            chosen_patrol = self._get_valid_patrol(
                romantic_patrols.copy(), chosen_frequency, patrol_override
            )

        if not self._decide_if_romantic(chosen_patrol):
            chosen_patrol = None

        # if no romantic patrol possible, we get a normal one!
        if not chosen_patrol:
            chosen_patrol = self._get_valid_patrol(
                normal_patrols.copy(), chosen_frequency, patrol_override
            )

        return chosen_patrol

    def _get_valid_patrol(
        self,
        possible_patrols: List[PatrolEvent],
        chosen_frequency: int,
        patrol_override: Optional[int],
    ) -> PatrolEvent:
        chosen_patrol = None
        used_frequencies = set()

        while not chosen_patrol:
            # make sure we still have possible patrols
            if not possible_patrols:
                # if we've circled back around to 4 then we need to reset the used patrols
                if 4 in used_frequencies and chosen_frequency == 4:
                    self.used_patrols.clear()
                    used_frequencies.clear()
                else:
                    used_frequencies.add(chosen_frequency)
                    chosen_frequency = find_new_frequency(used_frequencies)

            if not patrol_override:
                test_patrol = choices(
                    [possible_patrols], [x.weight for x in possible_patrols]
                )[0]
            else:
                test_patrol = patrol_override
                patrol_override = None

            # CHECK FREQUENCY AND ENSURE ID
            if test_patrol.frequency != chosen_frequency:
                possible_patrols.remove(test_patrol)
                continue

            # CHECK REPEAT
            if (
                test_patrol.id in self.used_patrols
                and not self.debug_patrol_id == test_patrol.id
            ):
                possible_patrols.remove(test_patrol)
                continue

            # CHECK IF CATS FIT
            if self._pass_cat_constraints(test_patrol):
                chosen_patrol = test_patrol

        return chosen_patrol

    def _pass_basic_constraints(
        self, patrol: PatrolEvent, patrol_type: str, is_debug_patrol: bool
    ) -> bool:
        # CHECK PATROL TYPE
        if "hunting" not in patrol.types and patrol_type == "hunting":
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (patrol type)")
            return False
        elif "border" not in patrol.types and patrol_type == "border":
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (patrol type)")
            return False
        elif "training" not in patrol.types and patrol_type == "training":
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (patrol type)")
            return False
        elif "herb_gathering" not in patrol.types and patrol_type == "herb_gathering":
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (patrol type)")
            return False

        # CHECK CAT TYPES
        if not event_for_required_cat_types(
            patrol.required_cat_types, self.patrol_statuses
        ):
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet cat type requirements.")
            return False

        # CHECK TAGS
        if not event_for_tags(patrol.tags, self.involved_cats["p_l"]):
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (tags)")
            return False

        # CHECK LOCATION
        if not event_for_location(patrol.location):
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (biome)")
            return False

        # CHECK SEASON
        if not event_for_season(patrol.season):
            if is_debug_patrol:
                print("DEBUG: requested patrol does not meet constraints (season)")
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

    def _pass_cat_constraints(self, patrol: PatrolEvent) -> bool:
        temp_involved_cats = {}

        for abbr, constraints in patrol.involved_cats.items():
            potential_cats = [
                c for c in self.patrol_cats if c not in temp_involved_cats.values()
            ]
            while not temp_involved_cats[abbr] and potential_cats:
                if abbr in self.involved_cats:
                    cat_to_check = self.involved_cats[abbr]
                else:
                    cat_to_check = potential_cats[0]

                # check cat constraints
                if not event_for_cat(
                    cat_info=constraints,
                    cat=cat_to_check,
                    involved_cat_dict=temp_involved_cats,
                    event_id=patrol.id,
                    p_l=temp_involved_cats["p_l"],
                    other_involved_clan_id=self.other_clan.id,
                ):
                    potential_cats.remove(cat_to_check)
                    continue

                # check rel constraints
                if patrol.relationship_constraint:
                    failed = False
                    for block in patrol.relationship_constraint:
                        if not check_rel_constraint_groups(
                            constraints_dict=block, involved_cats=temp_involved_cats
                        ):
                            potential_cats.remove(cat_to_check)
                            failed = True
                            break
                    if failed:
                        continue

                # if we're here, then the cat passed!
                temp_involved_cats[abbr] = cat_to_check

            if not temp_involved_cats.get(abbr):
                # we've failed to find an appropriate cat
                return False

        # if we're here, then we must have filled all the needed cats!
        self.involved_cats = temp_involved_cats
        return True

    def determine_outcome(
        self, antagonize=False
    ) -> Tuple[str, str, list, Optional[str]]:
        if self.patrol_event is None:
            raise Exception("No patrol event supplied")

        # First Step - Filter outcomes and pick a fail and success outcome
        success_outcomes = (
            self.patrol_event.antag_success_outcomes
            if antagonize
            else self.patrol_event.success_outcomes
        )
        fail_outcomes = (
            self.patrol_event.antag_fail_outcomes
            if antagonize
            else self.patrol_event.fail_outcomes
        )

        # Filter the outcomes. Do this only once - this is also where stat cats are determined
        success_outcomes = PatrolOutcome.prepare_allowed_outcomes(
            success_outcomes, self
        )
        fail_outcomes = PatrolOutcome.prepare_allowed_outcomes(fail_outcomes, self)

        chosen_success = None
        chosen_failure = None

        # Choose a success and fail outcome
        chosen_frequency = get_frequency()
        used_frequencies = set()
        while not chosen_success or not chosen_failure:
            if not chosen_success:
                possible_successes = [
                    x for x in success_outcomes if x.frequency == chosen_frequency
                ]
                if possible_successes:
                    chosen_success = choices(
                        possible_successes,
                        weights=[x.weight for x in possible_successes],
                    )[0]
            if not chosen_failure:
                possible_failures = [
                    x for x in fail_outcomes if x.frequency == chosen_frequency
                ]
                if possible_failures:
                    chosen_failure = choices(
                        possible_failures, weights=[x.weight for x in possible_failures]
                    )[0]
            if not chosen_success or not chosen_failure:
                used_frequencies.add(chosen_frequency)
                chosen_frequency = find_new_frequency(used_frequencies)

        final_event, success = self.calculate_success(chosen_success, chosen_failure)

        print(f"PATROL ID: {self.patrol_event.patrol_id} | SUCCESS: {success}")
        print(
            f"Patrol Frequency: {self.patrol_event.frequency} | Patrol Weight: {self.patrol_event.weight}"
        )
        if success:
            print(
                f"Outcome Frequency: {chosen_success.frequency} | Outcome Weight: {chosen_success.weight}"
            )
        else:
            print(
                f"Outcome Frequency: {chosen_failure.frequency} | Outcome Weight: {chosen_failure.weight}"
            )

        # Run the chosen outcome
        return final_event.execute_outcome(self)

    def calculate_success(
        self, success_outcome: PatrolOutcome, fail_outcome: PatrolOutcome
    ) -> Tuple[PatrolOutcome, bool]:
        """Returns both the chosen event, and a boolean that's True if success, and False is fail."""

        patrol_size = len(self.patrol_cats)
        total_exp = sum([x.experience for x in self.patrol_cats])
        path = (
            "patrol_generation.classic_difficulty_modifier"
            if game.clan.game_mode == "classic"
            else "patrol_generation.difficulty_modifier"
        )

        gm_modifier = get_config(path)

        exp_adustment = (
            (1 + 0.10 * patrol_size) * total_exp / (patrol_size * gm_modifier * 2)
        )

        success_chance = self.patrol_event.chance_of_success + int(exp_adustment)
        success_chance = min(success_chance, 90)

        # Now, apply success and fail skill
        print(
            "starting chance:",
            self.patrol_event.chance_of_success,
            "| EX_updated chance:",
            success_chance,
        )
        skill_updates = ""

        # Skill and trait stuff
        for kitty in self.patrol_cats:
            # SUCCESS OUTCOME
            is_exclusionary = any(
                value.find("-") == 0 for value in success_outcome.stat_skill
            )
            if is_exclusionary:
                skills_to_check = [
                    x.replace("-", "") for x in success_outcome.stat_skill
                ]
            else:
                skills_to_check = success_outcome.stat_skill

            hits = kitty.skills.check_skill_requirement_list(skills_to_check)

            if is_exclusionary and not hits:
                # if they don't have a disallowed skill, we increase the chance
                success_chance += (
                    1 * constants.CONFIG["patrol_generation"]["win_stat_cat_modifier"]
                )
            else:
                # if they had a required skill, we increase
                success_chance += (
                    hits
                    * constants.CONFIG["patrol_generation"]["win_stat_cat_modifier"]
                )

            # FAIL OUTCOME
            is_exclusionary = any(
                value.find("-") == 0 for value in fail_outcome.stat_skill
            )
            if is_exclusionary:
                skills_to_check = [x.replace("-", "") for x in fail_outcome.stat_skill]
            else:
                skills_to_check = fail_outcome.stat_skill
            hits = kitty.skills.check_skill_requirement_list(skills_to_check)

            if is_exclusionary and not hits:
                # if they don't have a disallowed skill, we decrease chance (fail mod is a negative)
                success_chance += (
                    1 * constants.CONFIG["patrol_generation"]["fail_stat_cat_modifier"]
                )
            else:
                # if they had the required skill, we decrease chance (fail mod is a negative)
                success_chance += (
                    hits
                    * constants.CONFIG["patrol_generation"]["fail_stat_cat_modifier"]
                )

            # SUCCESS OUTCOME
            is_exclusionary = any(
                value.find("-") == 0 for value in success_outcome.stat_trait
            )
            if is_exclusionary:
                trait_to_check = [
                    x.replace("-", "") for x in success_outcome.stat_trait
                ]
            else:
                trait_to_check = success_outcome.stat_trait

            if (is_exclusionary and kitty.personality.trait not in trait_to_check) or (
                kitty.personality.trait in trait_to_check
            ):
                success_chance += constants.CONFIG["patrol_generation"][
                    "win_stat_cat_modifier"
                ]

            # FAIL OUTCOME
            is_exclusionary = any(
                value.find("-") == 0 for value in fail_outcome.stat_trait
            )
            if is_exclusionary:
                trait_to_check = [x.replace("-", "") for x in fail_outcome.stat_trait]
            else:
                trait_to_check = fail_outcome.stat_trait

            if (is_exclusionary and kitty.personality.trait not in trait_to_check) or (
                kitty.personality.trait in trait_to_check
            ):
                success_chance += constants.CONFIG["patrol_generation"][
                    "fail_stat_cat_modifier"
                ]

            skill_updates += f"{kitty.name} updated chance to {success_chance} | "

        if success_chance >= 120:
            success_chance = 115
            skill_updates += "success chance over 120, updated to 115"

        print(skill_updates)

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
                f"The outcome of {self.patrol_event.patrol_id} was altered to {success}"
            )

        return (success_outcome if success else fail_outcome, success)

    def balance_hunting(self, possible_patrols: list):
        """Filter the incoming hunting patrol list to balance the different kinds of hunting patrols.
        With this filtering, there should be more prey possible patrols.

            Parameters
            ----------
            possible_patrols : list
                list of patrols which should be filtered

            Returns
            ----------
            filtered_patrols : list
                list of patrols which is filtered
        """
        filtered_patrols = []

        # get first what kind of prey size which will be chosen
        biome = (
            game.clan.biome
            if not game.clan.override_biome
            else game.clan.override_biome
        )
        season = game.clan.current_season
        prey_size = ["very_small", "small", "medium", "large", "huge"]

        chosen_prey_size = choices(prey_size, weights=PATROL_BALANCE[biome][season])[0]
        print(f"chosen filter prey size: {chosen_prey_size}")

        # filter all possible patrol depending on the needed prey size
        for patrol in possible_patrols:
            for adaption, needed_weight in PATROL_WEIGHT_ADAPTION.items():
                if needed_weight == patrol.frequency:
                    # get the amount of class sizes which can be increased
                    increment = int(adaption.split("_")[0])
                    new_idx = prey_size.index(chosen_prey_size) + increment
                    # check that the increment does not lead to an overflow
                    new_idx = (
                        new_idx if new_idx < len(prey_size) else len(prey_size) - 1
                    )
                    chosen_prey_size = deepcopy(prey_size[new_idx])
                    break

            # now count the outcomes + prey size
            prey_types = {}
            for outcome in patrol.success_outcomes:
                # ignore skill or trait outcomes
                if outcome.stat_trait or outcome.stat_skill:
                    continue
                if outcome.prey:
                    if outcome.prey[0] in prey_types:
                        prey_types[outcome.prey[0]] += 1
                    else:
                        prey_types[outcome.prey[0]] = 1

            # get the prey size with the most outcomes
            most_prey_size = ""
            max_occurrences = 0
            for size, amount in prey_types.items():
                if amount >= max_occurrences and most_prey_size != chosen_prey_size:
                    most_prey_size = size

            if chosen_prey_size == most_prey_size:
                filtered_patrols.append(patrol)
            elif self.debug_patrol_id and self.debug_patrol_id == patrol.patrol_id:
                print(
                    "DEBUG: requested patrol does not meet constraints (failed prey balancing)"
                )
        # if the filtering results in an empty list, don't filter and return whole possible patrols
        if len(filtered_patrols) <= 0:
            print(
                "---- WARNING ---- filtering to balance out the hunting, didn't work."
            )
            filtered_patrols = possible_patrols
        return filtered_patrols

    def get_patrol_art(self) -> pygame.Surface:
        """Return's patrol art surface"""
        if not self.patrol_event or not isinstance(self.patrol_event.patrol_art, str):
            return pygame.Surface((600, 600), flags=pygame.SRCALPHA)

        root_dir = "resources/images/patrol_art/"

        if not game_setting_get("gore") and self.patrol_event.patrol_art_clean:
            file_name = self.patrol_event.patrol_art_clean
        else:
            file_name = self.patrol_event.patrol_art

        if not isinstance(file_name, str) or not path_exists(
            f"{root_dir}{file_name}.png"
        ):
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


# ---------------------------------------------------------------------------- #
#                               PATROL CLASS END                               #
# ---------------------------------------------------------------------------- #

PATROL_WEIGHT_ADAPTION = constants.CONFIG["prey"]["patrol_weight_adaption"]
PATROL_BALANCE = constants.CONFIG["prey"]["patrol_balance"]
