#!/usr/bin/env python3
# -*- coding: ascii -*-
from typing import List, Union, Dict

from scripts.cat.personality import Personality
from scripts.cat.skills import SkillPath
from scripts.events_module.event_filters import get_frequency, find_new_frequency
from scripts.events_module.patrol.patrol_outcome import PatrolOutcome
from scripts.events_module.patrol.patrol_outcome_new import EventOutcome
from scripts.game_structure import constants


class PatrolEvent:
    NUM_OF_TRAITS = len(Personality.trait_ranges["normal_traits"].keys()) + len(
        Personality.trait_ranges["kit_traits"].keys()
    )
    NUM_OF_SKILLS = len(SkillPath)

    def __init__(
        self,
        patrol_id,
        biome: List[str] = None,
        camp: List[str] = None,
        season: List[str] = None,
        types: List[str] = None,
        tags: List[str] = None,
        frequency: int = 4,
        poi: Union[Dict[str, List], None] = None,
        patrol_art: Union[str, None] = None,
        patrol_art_clean: Union[str, None] = None,
        intro_text: str = "",
        decline_text: str = "",
        chance_of_success=0,
        success_outcomes: List[dict] = None,
        fail_outcomes: List[dict] = None,
        antag_success_outcomes: List[dict] = None,
        antag_fail_outcomes: List[dict] = None,
        min_cats=1,
        max_cats=6,
        min_max_status: dict = None,
        relationship_constraints: List[str] = None,
        pl_skill_constraints: List[str] = None,
        pl_trait_constraints: List[str] = None,
    ):
        self.weight = 1

        self.patrol_id = patrol_id
        self.frequency = frequency
        self.types = types if types is not None else []

        self.patrol_art = patrol_art
        self.patrol_art_clean = patrol_art_clean

        self.biome = biome if biome is not None else ["any"]
        if "any" not in self.biome:
            # add 4 for every biome not listed
            self.weight += 4 * (len(constants.BIOME_TYPES) - len(self.biome))

        self.camp = camp if camp is not None else ["any"]
        if "any" not in self.camp:
            self.weight += 8

        self.season = season if season is not None else ["any"]
        if "any" not in self.season:
            # add 4 for every season not listed
            self.weight += 4 * (len(constants.SEASONS) - len(self.season))

        self.tags = tags if tags is not None else []

        self.poi = poi if poi else {}
        # add 8, 6, 4 or 2 if there are between 1-4 specific named locations
        # todo: check for balancing
        if self.poi.get("name") and not 1 > len(self.poi["name"]) > 5:
            self.weight += 8 - 2 * len(self.poi["name"])
        elif self.poi.get("tags"):
            # add 4-1 depending on how many specific points of interest are included
            # but only if specific ones are not already requested
            self.weight += min(4, len(self.poi.get("tags", [])))

        self.chance_of_success = chance_of_success  # out of 100

        self.min_cats = min_cats
        self.max_cats = max_cats
        self.weight += 2 * (
            6 - (self.max_cats - self.min_cats)
        )  # the narrower this range, the higher weighted we want it

        self.min_max_status = min_max_status if min_max_status is not None else {}
        self.weight += len(self.min_max_status) * 2

        self.relationship_constraints = (
            relationship_constraints if relationship_constraints is not None else []
        )
        # LOTS of weight on rel constraints
        self.weight += len(self.relationship_constraints) * 20
        self.pl_skill_constraints = (
            pl_skill_constraints if pl_skill_constraints is not None else []
        )
        if self.pl_skill_constraints:
            if "-" in self.pl_skill_constraints[0]:
                # exclusionary values!
                self.weight += len(self.pl_skill_constraints)
            else:
                # inclusionary values get inverse weighting
                self.weight += self.NUM_OF_SKILLS - len(self.pl_skill_constraints)

        self.pl_trait_constraints = (
            pl_trait_constraints if pl_trait_constraints is not None else []
        )
        if self.pl_trait_constraints:
            if "-" in self.pl_trait_constraints[0]:
                # exclusionary values!
                self.weight += len(self.pl_trait_constraints)
            else:
                # inclusionary values get inverse weighting
                self.weight += self.NUM_OF_SKILLS - len(self.pl_trait_constraints)

        self.intro_text = intro_text
        self.decline_text = decline_text

        self.success_outcomes: list[EventOutcome] = []
        self.fail_outcomes: list[EventOutcome] = []
        self.antag_success_outcomes: list[EventOutcome] = []
        self.antag_fail_outcomes: list[EventOutcome] = []

        self._generate_outcomes(
            success_outcomes, fail_outcomes, antag_success_outcomes, antag_fail_outcomes
        )

    @property
    def new_cat(self) -> bool:
        """Returns boolean if there are any outcomes that results in
        a new cat joining (not just meeting)"""

        for out in (
            self.success_outcomes
            + self.fail_outcomes
            + self.antag_fail_outcomes
            + self.antag_success_outcomes
        ):
            for sublist in out.new_cat:
                if "join" in sublist:
                    return True

        return False

    @property
    def other_clan(self) -> bool:
        """Return boolean indicating if any outcome has any reputation effect"""
        for out in (
            self.success_outcomes
            + self.fail_outcomes
            + self.antag_fail_outcomes
            + self.antag_success_outcomes
        ):
            if out.other_clan_rep is not None:
                return True

        return False

    @property
    def herbs_given(self) -> list:
        """
        returns list of herbs available to get from this patrol
        """
        herb_list = []
        for out in (
            self.success_outcomes
            + self.fail_outcomes
            + self.antag_fail_outcomes
            + self.antag_success_outcomes
        ):
            herb_list.extend([herb for herb in out.herbs if herb not in herb_list])

        return herb_list

    def _generate_outcomes(
        self,
        success_outcomes: list[dict],
        fail_outcomes: list[dict],
        antag_success_outcomes: list[dict],
        antag_fail_outcomes: list[dict],
    ):
        """
        Generates outcome objects for each outcome in the patrol
        """
        for outcome in success_outcomes:
            self.success_outcomes.append(EventOutcome(**outcome))
        for outcome in fail_outcomes:
            self.fail_outcomes.append(EventOutcome(**outcome))
        for outcome in antag_success_outcomes:
            self.antag_success_outcomes.append(EventOutcome(**outcome))
        for outcome in antag_fail_outcomes:
            self.antag_fail_outcomes.append(EventOutcome(**outcome))

    def find_allowed_outcomes(
        self, antagonize: bool = False
    ) -> tuple[EventOutcome, EventOutcome]:
        """
        Filters through possible outcomes to find appropriate outcomes for both failure and success
        :param antagonize: set True if the player chose to antagonize
        :return: success outcome, failure outcome
        """

        if antagonize:
            success_outcomes = self.antag_success_outcomes
            fail_outcomes = self.antag_fail_outcomes
        else:
            success_outcomes = self.success_outcomes
            fail_outcomes = self.fail_outcomes

        # for success and fail options we'll find what frequency is wanted
        # then pick an outcome of that frequency based on weight
        # then see if that outcome is allowed per constraints
        # if it isn't, then grab the next outcome and try again
        # until we have one that passes. this is what we'll use!

        chosen_success = None
        chosen_failure = None

        chosen_frequency = get_frequency()
        used_frequencies = set()
        while not chosen_success or not chosen_failure:
            if not chosen_success:
                # try to filter
                pass
            if not chosen_failure:
                # try to filter
                pass

            if not chosen_success or not chosen_failure:
                used_frequencies.add(chosen_frequency)
                chosen_frequency = find_new_frequency(used_frequencies)

        return chosen_success, chosen_failure
