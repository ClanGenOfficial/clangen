#!/usr/bin/env python3
# -*- coding: ascii -*-
import logging
import random
from os.path import exists as path_exists
from random import choice, randint, choices
from typing import List, Tuple, Optional, Union, Literal, TypedDict

import pygame

from scripts.cat.cats import Cat
from scripts.cat_relations.enums import RelType
from scripts.cat.enums import CatAge, CatRank, CatCompatibility
from scripts.clan_package.get_clan_cats import get_living_clan_cat_count
from scripts.clan_resources.freshkill import FRESHKILL_EVENT_TRIGGER_FACTOR
from scripts.config import get_config
from scripts.events_module.event_filters import (
    event_for_tags,
    get_frequency,
    find_new_frequency,
    check_relationship_value,
    get_personality_compatibility,
    event_for_location,
    event_for_season,
    event_for_poi,
    event_for_required_cat_types,
    event_for_cat,
    check_rel_constraint_groups,
    event_for_reputation,
    event_for_clan_relations,
    event_for_freshkill_supply,
    event_for_herb_supply,
    cat_for_event,
)
from scripts.events_module.patrol.create_new_cat import updated_create_new_cat
from scripts.events_module.patrol.generate_patrol_list import (
    get_patrol_list,
    will_allow_outsider_patrols,
)
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event import handle_consequences
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
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
        self.debug_patrol_id: str = ""
        self.other_clan = None

        self.patrol_cats: list[Cat] = []
        """Holds all the cats that are on the patrol"""
        self.patrol_statuses: dict[str, list[Cat]] = {}
        """Keys are cat statuses present on the patrol, values are lists of the cats that hold the status"""
        self.involved_cats: dict[str, Union[list[Cat], Cat]] = {}
        """Cats directly involved and referenced in the event. Keys are their text abbreviation, values are the associated cat objects"""
        self.outcome_cats: TypedDict(
            "outcome_cats", {"success": dict[str, Cat], "failure": dict[str, Cat]}
        ) = {"success": {}, "failure": {}}
        self.new_cats: list[Cat] = []

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

        # Choose other clan
        if game.clan.all_other_clans and len(game.clan.all_other_clans) > 0:
            self.other_clan = choice(game.clan.all_other_clans)
        else:
            self.other_clan = None

        # Find valid patrol
        self.patrol_event = self._get_possible_patrol(patrol_type)

        Patrol.used_patrols.append(self.patrol_event.id)

        # Return text adjusted patrol intro
        return event_text_adjust(
            Cat,
            self.patrol_event.intro_text,
            involved_cat_dict=self.involved_cats,
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
                    f"PATROL ID: {self.patrol_event.id} | SUCCESS: N/A (did not proceed)"
                )
                return (
                    event_text_adjust(
                        Cat,
                        self.patrol_event.intro_text,
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

        return self.determine_outcome(antagonize=(path == "antag"))

    def _add_patrol_cats(self, patrol_cats: List[Cat]) -> None:
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
                set(self.patrol_statuses.keys())
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
            if self._patrol_pass_basic_constraints(
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
        patrol_override: Optional[PatrolEvent],
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
                test_patrol = list(
                    choices([possible_patrols], [x.weight for x in possible_patrols])
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
            if self._patrol_pass_cat_constraints(test_patrol):
                chosen_patrol = test_patrol

        return chosen_patrol

    def _patrol_pass_basic_constraints(
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

    def _patrol_pass_cat_constraints(self, patrol: PatrolEvent) -> bool:
        temp_involved_cats = {}

        outside_cats = [
            c
            for c in Cat.all_cats_list
            if c.status.is_other_clancat or c.status.is_outsider
        ]
        for abbr, constraints in patrol.involved_cats.items():
            # if we need n_c then we pull outside cats
            if "n_c" in abbr:
                potential_cats = [c for c in outside_cats if c not in self.new_cats]
                random.shuffle(potential_cats)
            else:
                potential_cats = [
                    c for c in self.patrol_cats if c not in temp_involved_cats.values()
                ]

            possible_cats = cat_for_event(
                constraint_dict=constraints,
                possible_cats=potential_cats,
                tags=patrol.tags,
                return_list=True,
            )

            if not self._find_involved_cats(
                abbr,
                possible_cats,
                patrol.relationship_constraint,
                cat_constraints=constraints,
                temp_involved_cats=temp_involved_cats,
            ):
                return False

        # if we're here, then we must have filled all the needed cats!
        self.involved_cats = temp_involved_cats
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

        # for success and fail options we'll find what frequency is wanted
        # then pick an outcome of that frequency based on weight
        # then see if that outcome is allowed per constraints
        # if it isn't, then grab the next outcome and try again until we have one that passes.
        # this is the outcome we'll use!

        # we'll get an outcome for both success and failure
        chosen_success = None
        chosen_failure = None

        chosen_frequency = get_frequency()
        used_frequencies = set()

        tested_outcomes = set()
        while not chosen_success or not chosen_failure:
            if not chosen_success:
                possible_outcomes = [
                    x
                    for x in success_outcomes
                    if x.frequency == chosen_frequency and x not in tested_outcomes
                ]
                if not possible_outcomes:
                    used_frequencies.add(chosen_frequency)
                    chosen_frequency = find_new_frequency(used_frequencies)

                test_outcome = choices(
                    possible_outcomes, weights=[x.weight for x in possible_outcomes]
                )[0]

                # try to filter
                if self._check_outcome_constraints(test_outcome, "success"):
                    chosen_success = test_outcome
                else:
                    tested_outcomes.add(test_outcome)

            if not chosen_success:
                continue

            if not chosen_failure:
                possible_outcomes = [
                    x
                    for x in fail_outcomes
                    if x.frequency == chosen_frequency and x not in tested_outcomes
                ]
                if not possible_outcomes:
                    used_frequencies.add(chosen_frequency)
                    chosen_frequency = find_new_frequency(used_frequencies)

                test_outcome = choices(
                    possible_outcomes, weights=[x.weight for x in possible_outcomes]
                )[0]
                # try to filter
                if self._check_outcome_constraints(test_outcome, "failure"):
                    chosen_success = test_outcome
                else:
                    tested_outcomes.add(test_outcome)

            if not chosen_failure:
                continue

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
        if not event_for_location(outcome.location):
            return False

        if not event_for_season(outcome.season):
            return False

        if not event_for_tags(outcome.tags, self.involved_cats["p_l"]):
            return False

        if outcome.required_reputation:
            if not event_for_reputation(outcome.required_reputation.get("outsider")):
                return False

            if not event_for_clan_relations(
                outcome.required_reputation.get("other_clan"), self.other_clan
            ):
                return False

        if outcome.required_cat_types:
            if not event_for_required_cat_types(
                outcome.required_cat_types, self.patrol_statuses
            ):
                return False

        if outcome.supply:
            clan_size = get_living_clan_cat_count(Cat)
            for block in outcome.supply:
                if "freshkill" in block["type"]:
                    if not event_for_freshkill_supply(
                        game.clan.freshkill_pile,
                        trigger=block["trigger"],
                        factor=FRESHKILL_EVENT_TRIGGER_FACTOR,
                        clan_size=clan_size,
                    ):
                        return False
                else:
                    if not event_for_herb_supply(
                        trigger=block["trigger"],
                        supply_type=block["type"],
                        clan_size=clan_size,
                    ):
                        return False

        # CATS
        outside_cats = [
            c
            for c in Cat.all_cats_list
            if c.status.is_other_clancat or c.status.is_outsider
        ]
        temp_involved_cats = self.involved_cats.copy()
        for abbr, constraints in outcome.involved_cats.items():
            possible_injuries = []
            # grab any injuries they might get
            if outcome.condition:
                for block in outcome.condition:
                    if abbr in block["cats"]:
                        possible_injuries.extend(block["condition"])

            # if the abbr is one we've already assigned, then we just test that cat!
            if test_cat := self.involved_cats.get(abbr):
                if not event_for_cat(
                    constraints,
                    test_cat,
                    involved_cat_dict=temp_involved_cats,
                    injuries=possible_injuries,
                    event_id=self.patrol_event.id,
                ):
                    return False

                # check rel constraints
                if outcome.relationship_constraint:
                    for block in outcome.relationship_constraint:
                        if not check_rel_constraint_groups(
                            constraints_dict=block, involved_cats=temp_involved_cats
                        ):
                            return False

            # otherwise, check if this abbr wants to replace an existing one!
            elif constraints.get("prior_abbreviation"):
                possible_cats = [
                    self.involved_cats.get(_a)
                    for _a in constraints["prior_abbreviation"]
                ]

                for c in possible_cats:
                    if not c:
                        continue

                    if not event_for_cat(
                        constraints,
                        c,
                        involved_cat_dict=temp_involved_cats,
                        injuries=possible_injuries,
                        event_id=self.patrol_event.id,
                    ):
                        return False

                    # check rel constraints
                    if outcome.relationship_constraint:
                        for block in outcome.relationship_constraint:
                            if not check_rel_constraint_groups(
                                constraints_dict=block, involved_cats=temp_involved_cats
                            ):
                                return False

            # if neither of those is happening, then we check if any of our uninvolved cats can take this spot!
            else:
                if "n_c" in abbr:
                    potential_cats = [c for c in outside_cats if c not in self.new_cats]
                    random.shuffle(potential_cats)
                else:
                    potential_cats = [
                        c
                        for c in self.patrol_cats
                        if c not in self.involved_cats.values()
                    ]

                possible_cats = cat_for_event(
                    constraint_dict=constraints,
                    possible_cats=potential_cats,
                    tags=outcome.tags,
                    return_list=True,
                )

                if not self._find_involved_cats(
                    abbr,
                    possible_cats,
                    outcome.relationship_constraint,
                    cat_constraints=constraints,
                    temp_involved_cats=temp_involved_cats,
                ):
                    return False

        # if we're here, then we must have found all our cats!
        self.outcome_cats[outcome_type] = temp_involved_cats

        return True

    def _find_involved_cats(
        self,
        abbr: str,
        possible_cats: list[Cat],
        relationship_constraint,
        cat_constraints,
        temp_involved_cats: dict,
    ) -> bool:
        # if relationships aren't required, just grab some cats and go!
        if possible_cats and not relationship_constraint:
            # take first cat
            temp_involved_cats[abbr] = possible_cats[0]
            return False

        # otherwise, let's make sure we fulfill the rel constraints with this cat
        elif possible_cats:
            while not temp_involved_cats.get(abbr):
                # need a temp cat dict that includes our possible kitty
                _temp_cats = temp_involved_cats.copy()
                _temp_cats[abbr] = possible_cats[0]
                # now we check each rel constraint to make sure our new cat is valid
                for block in relationship_constraint:
                    if not check_rel_constraint_groups(block, _temp_cats):
                        # they aren't! so we remove them from the possibilities
                        possible_cats.remove(_temp_cats[abbr])
                        if not possible_cats:
                            # oops! no more cats available! this patrol isn't possible
                            return False
                        else:
                            # still some possibilities, let's try the next!
                            continue

                    # if we got here, then this cat works!
                    temp_involved_cats[abbr] = _temp_cats[abbr]

        # there weren't any possible cats, so we'll create a new one if we're allowed
        else:
            # we don't need to check relationship constraints if we're making a new cat
            if "n_c" in abbr and cat_constraints.get("can_create_new_cat"):
                temp_involved_cats[abbr] = updated_create_new_cat(
                    option_dict=cat_constraints,
                    involved_cats=temp_involved_cats,
                    other_clan=self.other_clan,
                )
                self.new_cats.extend(temp_involved_cats[abbr])
            else:
                # if we aren't allowed to make a new one, then we can't do this patrol
                return False

        return True

    def determine_outcome(
        self, antagonize=False
    ) -> Tuple[str, str, list, Optional[str]]:
        if self.patrol_event is None:
            raise Exception("No patrol event supplied")

        success_outcome, fail_outcome = self._find_allowed_outcomes(antagonize)

        chosen_outcome, success = self.calculate_success(success_outcome, fail_outcome)

        print(f"PATROL ID: {self.patrol_event.id} | SUCCESS: {success}")
        print(
            f"Patrol Frequency: {self.patrol_event.frequency} | Patrol Weight: {self.patrol_event.weight}"
        )
        print(
            f"Outcome Frequency: {chosen_outcome.frequency} | Outcome Weight: {chosen_outcome.weight}"
        )

        # Run the chosen outcome
        return handle_consequences.execute_outcome(
            chosen_outcome, self.involved_cats, self.other_clan
        )

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
            print(f"The outcome of {self.patrol_event.id} was altered to {success}")

        return success_outcome if success else fail_outcome, success

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
        prey_size_random_weights = PATROL_BALANCE[biome][season]

        chosen_prey_size = choices(prey_size, weights=prey_size_random_weights)[0]
        print(f"chosen filter prey size: {chosen_prey_size}")

        # filter all possible patrol depending on the needed prey size
        for patrol in possible_patrols:
            # count the outcomes + prey size
            prey_size_to_outcome_amounts = {}
            for outcome in patrol.success_outcomes:
                # ignore skill or trait outcomes
                if outcome.stat_trait or outcome.stat_skill:
                    continue
                if outcome.prey:
                    outcome_prey_size = outcome.prey[0]
                    if outcome_prey_size not in prey_size_to_outcome_amounts:
                        prey_size_to_outcome_amounts[outcome_prey_size] = 0
                    prey_size_to_outcome_amounts[outcome_prey_size] += 1

            # get the prey size with the most outcomes
            most_prey_size = ""
            max_occurrences = 0
            for size, amount in prey_size_to_outcome_amounts.items():
                if amount >= max_occurrences:
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
