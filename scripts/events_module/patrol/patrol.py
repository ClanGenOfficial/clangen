#!/usr/bin/env python3
# -*- coding: ascii -*-
import logging
import random
from copy import deepcopy
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
)
from scripts.events_module.patrol.get_possible_patrols import (
    get_possible_patrols,
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
from scripts.special_dates import SpecialDate, is_today


logger = logging.getLogger(__name__)


class Patrol:
    used_patrols = []

    def __init__(self):
        self.patrol_event: Optional[PatrolEvent] = None

        # TODO: old attributes, might not need them all anymore
        self.patrol_leader = None
        self.random_cat = None
        self.patrol_cats = []
        self.patrol_apprentices = []
        self.other_clan = None
        self.intro_text = ""

        self.patrol_statuses = {}
        self.patrol_status_list = []

        # Holds new cats for easy access
        self.new_cats: List[List[Cat]] = []

        # False if no debug patrol set, value if one is set
        self.debug_patrol: Union[bool, str] = False

    def setup_patrol(self, patrol_cats: List[Cat], patrol_type: str) -> str:
        # Add cats

        print("PATROL START ---------------------------------------------------")

        self.add_patrol_cats(patrol_cats, game.clan)

        self.debug_patrol = (
            constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]
            if constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]
            else False
        )

        final_patrols, final_romance_patrols = self.get_possible_patrols(patrol_type)

        print(
            f"Total Number of Possible Patrols | normal: {len(final_patrols)}, romantic: {len(final_romance_patrols)} "
        )

        if final_patrols:
            normal_event_choice = choices(
                final_patrols, weights=[x.weight for x in final_patrols]
            )[0]
        else:
            print("ERROR: NO POSSIBLE NORMAL PATROLS FOUND for: ", self.patrol_statuses)
            raise RuntimeError

        romantic_event_choice = None
        if final_romance_patrols:
            romantic_event_choice = choices(
                final_romance_patrols, [x.weight for x in final_romance_patrols]
            )[0]

        if romantic_event_choice and Patrol.decide_if_romantic(
            romantic_event_choice,
            self.patrol_leader,
            self.random_cat,
            self.patrol_apprentices,
        ):
            print("did the romance")
            self.patrol_event = romantic_event_choice
        else:
            self.patrol_event = normal_event_choice

        Patrol.used_patrols.append(self.patrol_event.patrol_id)

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

    def add_patrol_cats(self, patrol_cats: List[Cat], clan: Clan) -> None:
        """Add the list of cats to the patrol class and handles to set all needed values.

        Parameters
        ----------
        patrol_cats : list
            list of cats which are on the patrol

        clan: Clan
            the Clan class of the game, this parameter is needed to make tests possible

        Returns
        ----------
        """
        for cat in patrol_cats:
            self.patrol_cats.append(cat)

            if cat.status.rank.is_any_apprentice_rank():
                self.patrol_apprentices.append(cat)

            self.patrol_status_list.append(cat.status.rank)

            if cat.status.rank in self.patrol_statuses:
                self.patrol_statuses[cat.status.rank] += 1
            else:
                self.patrol_statuses[cat.status.rank] = 1

            # Combined patrol_statuses categories
            if cat.status.rank.is_any_medicine_rank():
                if "healer cats" in self.patrol_statuses:
                    self.patrol_statuses["healer cats"] += 1
                else:
                    self.patrol_statuses["healer cats"] = 1

            if cat.status.rank.is_any_apprentice_rank():
                if "all apprentices" in self.patrol_statuses:
                    self.patrol_statuses["all apprentices"] += 1
                else:
                    self.patrol_statuses["all apprentices"] = 1

            if (
                cat.status.rank.is_any_adult_warrior_like_rank()
                and cat.age != CatAge.ADOLESCENT
            ):
                if "normal adult" in self.patrol_statuses:
                    self.patrol_statuses["normal adult"] += 1
                else:
                    self.patrol_statuses["normal adult"] = 1

            game.patrolled.append(cat.ID)

        # PATROL LEADER AND RANDOM CAT CAN NOT CHANGE AFTER SET-UP

        # DETERMINE PATROL LEADER
        # sets medcat as patrol leader if they're in the patrol
        if CatRank.MEDICINE_CAT in self.patrol_status_list:
            index = self.patrol_status_list.index(CatRank.MEDICINE_CAT)
            self.patrol_leader = self.patrol_cats[index]
        # If there is no medicine cat, but there is a medicine cat apprentice, set them as the patrol leader.
        # This prevents warriors from being treated as medicine cats in medicine cat patrols.
        elif CatRank.MEDICINE_APPRENTICE in self.patrol_status_list:
            index = self.patrol_status_list.index(CatRank.MEDICINE_APPRENTICE)
            self.patrol_leader = self.patrol_cats[index]
            # then we just make sure that this app will also be app1
            self.patrol_apprentices.remove(self.patrol_leader)
            self.patrol_apprentices = [self.patrol_leader] + self.patrol_apprentices
        # if no meddies set leader as patrol leader
        elif CatRank.LEADER in self.patrol_status_list:
            index = self.patrol_status_list.index(CatRank.LEADER)
            self.patrol_leader = self.patrol_cats[index]
        # if no leader set the deputy as patrol leader
        elif CatRank.DEPUTY in self.patrol_status_list:
            index = self.patrol_status_list.index(CatRank.DEPUTY)
            self.patrol_leader = self.patrol_cats[index]
        # if no deputy, set oldest or most experienced as patrol leader
        else:
            # Flip a coin to pick the most experience, or oldest.
            if randint(0, 1):
                self.patrol_cats.sort(key=lambda x: x.moons)
            else:
                self.patrol_cats.sort(key=lambda x: x.experience)
            self.involved_cats["p_l"] = self.patrol_cats[-1]

        if clan.all_other_clans and len(clan.all_other_clans) > 0:
            self.other_clan = choice(clan.all_other_clans)
        else:
            self.other_clan = None

        # DETERMINE RANDOM CAT
        # Find random cat
        if len(patrol_cats) > 1:
            # prioritize grabbing an adult as the random cat
            if self.patrol_statuses.get("normal adult", 0) > 1:
                self.random_cat = choice(
                    [
                        i
                        for i in self.patrol_cats
                        if i != self.patrol_leader and i not in self.patrol_apprentices
                    ]
                )
            # if no adults, grab anyone
            else:
                self.random_cat = choice(
                    [i for i in patrol_cats if i != self.patrol_leader]
                )
        else:
            self.random_cat = choice(patrol_cats)

        print("Patrol Leader:", str(self.patrol_leader.name))
        print("Random Cat:", str(self.random_cat.name))

    def get_possible_patrols(
        self,
        patrol_type: str,
    ) -> Tuple[list[PatrolEvent], list[PatrolEvent]]:
        # ---------------------------------------------------------------------------- #
        #                                LOAD RESOURCES                                #
        # ---------------------------------------------------------------------------- #

        # GATHER INFO
        reputation = game.clan.reputation  # reputation with outsiders
        other_clan = self.other_clan
        other_clan_standing = other_clan.get_standing()
        clan_size = int(len(game.clan.clan_cats))
        if clan_size < 20:
            small_clan = True
        else:
            small_clan = False
        # this next one is needed for Classic specifically
        # Classic doesn't let you pick patrol type, so instead we specify herb_gathering if meddies are present
        patrol_type = (
            "herb_gathering"
            if [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE]
            in self.patrol_status_list
            else patrol_type
        )

        # GET POSSIBLE PATROLS
        possible_patrols = get_possible_patrols(
            patrol_type,
            outsider_rep=will_allow_outsider_patrols(reputation, small_clan),
            other_clan_rep=other_clan_standing,
        )

        # INFORM -NOT PRESENT-
        patrol_ids = [patrol.id for patrol in possible_patrols]
        if self.debug_patrol and self.debug_patrol not in patrol_ids:
            print(
                "DEBUG: requested patrol not present (check spelling/mismatched season, biome, patrol type, new cat flag, other clan relations, disaster setting)"
            )

        final_normal_patrols, final_romance_patrols = self.get_filtered_patrols(
            possible_patrols, patrol_type
        )

        # This is a debug option, this allows you to remove any constraints of a patrol regarding location, session, biomes, etc.
        if constants.CONFIG["patrol_generation"][
            "debug_override_patrol_stat_requirements"
        ]:
            final_normal_patrols = final_romance_patrols = possible_patrols
            # Logging
            print(
                "All patrol filters regarding location, session, etc. have been removed."
            )

        # This is a debug option. If the patrol_id set in "debug_ensure_patrol" is possible,
        # make it the *only* possible patrol
        if self.debug_patrol:
            for _pat in final_normal_patrols + final_romance_patrols:
                if _pat.id == self.debug_patrol:
                    patrol_type = choice(_pat.types) if _pat.types != [] else "general"
                    rom = "non-romance"
                    if _pat in final_normal_patrols:
                        final_normal_patrols = [_pat]
                    elif _pat in final_romance_patrols:
                        final_romance_patrols = [_pat]
                        rom = "romance"
                    print(
                        f"debug_ensure_patrol_id: "
                        f'"{constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]}" '
                        f"is a possible {patrol_type} patrol, and was set as the only "
                        f"{patrol_type} {rom} patrol option"
                    )
                    break
            else:
                print(
                    f"debug_ensure_patrol_id: "
                    f'"{constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]}" '
                    f"is not found. Check output for reason."
                )
        return final_normal_patrols, final_romance_patrols

    @staticmethod
    def decide_if_romantic(
        romantic_event, patrol_leader, random_cat, patrol_apprentices: list
    ) -> bool:
        # if no romance was available or the patrol lead and random cat aren't potential mates then use the normal event

        if not romantic_event:
            print("No romantic event")
            return False

        if "rom_two_apps" in romantic_event.tags:
            if len(patrol_apprentices) < 2:
                print("somehow, there are not enough apprentices for romantic patrol")
                return False
            love1 = patrol_apprentices[0]
            love2 = patrol_apprentices[1]
        else:
            love1 = patrol_leader
            love2 = random_cat

        if (
            not love1.is_potential_mate(love2, for_love_interest=True)
            and love1.ID not in love2.mate
        ):
            print("not a potential mate or current mate")
            return False

        print("attempted romance between:", love1.name, love2.name)
        chance_of_romance_patrol = constants.CONFIG["patrol_generation"][
            "chance_of_romance_patrol"
        ]

        if (
            get_personality_compatibility(love1, love2) == CatCompatibility.POSITIVE
            or love1.ID in love2.mate
        ):
            chance_of_romance_patrol -= 10
        else:
            chance_of_romance_patrol += 10

        values = [*RelType]
        for val in values:
            value_check = check_relationship_value(love1, love2, val)
            if value_check < 0:
                chance_of_romance_patrol -= 1
            elif value_check > 0:
                chance_of_romance_patrol += 2

        if (
            romantic_event.patrol_id
            == game.constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]
        ):
            chance_of_romance_patrol = 1

        if chance_of_romance_patrol <= 0:
            chance_of_romance_patrol = 1
        print("final romance chance:", chance_of_romance_patrol)
        return not int(random.random() * chance_of_romance_patrol)

    def _filter_patrols(
        self,
        possible_patrols: List[PatrolEvent],
        patrol_type: str,
    ):
        normal_patrols = []
        romantic_patrols = []

        # This make sure general only gets hunting, border, or training patrols
        if patrol_type == "general":
            # choosing a type now means that the type of patrol later chosen isn't influenced
            # by the amount of patrols available of that type
            patrol_type = random.choice(["hunting", "border", "training"])

        # MENTOR CHECKS
        # this is looking to see if an app has a mentor, regardless of that mentor being present on the patrol
        app_number_mentor_checks = {}
        for i in range(1, 7):
            app_number_mentor_checks[f"app{i}_mentored"] = (
                len(self.patrol_apprentices) >= i
                and self.patrol_apprentices[i - 1].mentor is not None
            )
        general_mentor_checks = (
            all(app.mentor for app in self.patrol_apprentices)
            if self.patrol_apprentices
            else False
        )
        has_mentor = {"general": general_mentor_checks, **app_number_mentor_checks}

        # GET FREQUENCY
        chosen_frequency = get_frequency()
        used_frequencies = set()
        # makes sure that it grabs patrols in the correct biomes, season, with the correct number of cats
        while not normal_patrols:
            for patrol in possible_patrols:
                # CHECK FREQUENCY AND ENSURE ID
                if (
                    patrol.frequency != chosen_frequency
                    and patrol.id
                    != constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]
                ):
                    continue

                if not self._check_constraints(patrol):
                    continue

                # Don't check for repeat patrols if ensure_patrol_id is being used.
                if (
                    constants.CONFIG["patrol_generation"]["debug_ensure_patrol_id"]
                    == ""
                    and patrol.id in self.used_patrols
                ):
                    continue

                # CHECK PATROL TYPE
                if "hunting" not in patrol.types and patrol_type == "hunting":
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (patrol type)"
                        )
                    continue
                elif "border" not in patrol.types and patrol_type == "border":
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (patrol type)"
                        )
                    continue
                elif "training" not in patrol.types and patrol_type == "training":
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (patrol type)"
                        )
                    continue
                elif (
                    "herb_gathering" not in patrol.types
                    and patrol_type == "herb_gathering"
                ):
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (patrol type)"
                        )
                    continue

                if not (patrol.min_cats <= len(self.patrol_cats) <= patrol.max_cats):
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (min or max cats range)"
                        )
                    continue

                flag = False
                for sta, num in patrol.min_max_status.items():
                    if len(num) != 2:
                        print(f"Issue with status limits: {patrol.id}")
                        continue

                    if not (num[0] <= self.patrol_statuses.get(sta, -1) <= num[1]):
                        flag = True
                        break
                if flag:
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (min max status)"
                        )
                    continue

                # CHECK TAGS
                if not event_for_tags(
                    patrol.tags, Cat, mentor_tags_fulfilled=has_mentor
                ):
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (tags)"
                        )
                    continue

                # CHECK LOCATION
                if not event_for_location(patrol.location):
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (biome)"
                        )
                    continue

                # CHECK SEASON
                if not event_for_season(patrol.season):
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print(
                            "DEBUG: requested patrol does not meet constraints (season)"
                        )
                    continue

                # CHECK POI
                if not event_for_poi(patrol.poi):
                    if self.debug_patrol and self.debug_patrol == patrol.id:
                        print("DEBUG: requested patrol does not meet constraints (PoI)")
                    continue

                # romance events are put in their own list
                # this lets us better control the distribution of romantic and nonromantic patrols
                if "romance" in patrol.tags:
                    romantic_patrols.append(patrol)
                else:
                    normal_patrols.append(patrol)

            if not normal_patrols:
                # if we've circled back around to 4 then we need to reset the used patrols
                if 4 in used_frequencies and chosen_frequency == 4:
                    self.used_patrols.clear()
                    used_frequencies.clear()
                else:
                    used_frequencies.add(chosen_frequency)
                    chosen_frequency = find_new_frequency(used_frequencies)

        # make sure the hunting patrols are balanced
        if patrol_type == "hunting":
            normal_patrols = self.balance_hunting(normal_patrols)

        return normal_patrols, romantic_patrols

    def get_filtered_patrols(self, possible_patrols, patrol_type):
        # FILTER
        normal_patrols, romantic_patrols = self._filter_patrols(
            possible_patrols, patrol_type
        )

        # DOUBLE CHECK PATROL PRESENCE
        if not normal_patrols:
            print(
                "No normal patrols possible. Repeating filter with used patrols cleared."
            )
            self.used_patrols.clear()
            print("used patrols cleared", self.used_patrols)
            normal_patrols, romantic_patrols = self._filter_patrols(
                possible_patrols, patrol_type
            )

            if not normal_patrols:
                raise Exception(
                    "No matching patrols found! This may be a localization issue."
                )

        # FIND PATROL FOR WANTED HERBS
        if patrol_type == "herb_gathering":
            target_herbs = game.clan.herb_supply.sorted_by_need
            herb_filtered_patrols = []
            herb_romance_patrols = []

            i = 0
            while not herb_filtered_patrols and i <= len(target_herbs):
                i += 1
                herb_filtered_patrols = [
                    patrol
                    for patrol in normal_patrols
                    if target_herbs[i] in patrol.herbs_given
                    or "random_herbs" in patrol.herbs_given
                ]
                herb_romance_patrols = [
                    patrol
                    for patrol in romantic_patrols
                    if target_herbs[i] in patrol.herbs_given
                    or "random_herbs" in patrol.herbs_given
                ]
            # if we want patrols that get the herbs the meddies want, then we use those
            # otherwise we just use the original patrol lists
            if herb_filtered_patrols:
                normal_patrols = herb_filtered_patrols
                romantic_patrols = herb_romance_patrols

                if self.debug_patrol and self.debug_patrol not in [
                    patrol.id for patrol in normal_patrols + romantic_patrols
                ]:
                    print(
                        "DEBUG: requested patrol removed during herb filtering (not target herb)"
                    )

        # RETURN FOUND PATROLS
        return normal_patrols, romantic_patrols

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
            elif self.debug_patrol and self.debug_patrol == patrol.patrol_id:
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
