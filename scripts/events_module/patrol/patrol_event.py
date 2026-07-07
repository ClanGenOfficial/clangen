#!/usr/bin/env python3
# -*- coding: ascii -*-
from dataclasses import dataclass, field
from typing import Union, Literal, Optional

from scripts.cat.cats import Cat
from scripts.cat.personality import Personality
from scripts.cat.skills import SkillPath
from scripts.clan_resources.herb.herb import HERBS
from scripts.events_module.event_filters import (
    get_frequency,
    find_new_frequency,
    event_for_location,
    event_for_season,
    event_for_tags,
    event_for_reputation,
    event_for_clan_relations,
    event_for_freshkill_supply,
    event_for_herb_supply,
    event_for_cat,
)
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    RelationshipConstraintDict,
)
from scripts.events_module.patrol.patrol_outcome_new import EventOutcome
from scripts.game_structure import constants, game

NUM_OF_TRAITS = len(Personality.trait_ranges["normal_traits"].keys()) + len(
    Personality.trait_ranges["kit_traits"].keys()
)
NUM_OF_SKILLS = len(SkillPath)


# slots increases performance and can be used since we won't be adding new attrs at runtime
@dataclass(slots=True)
class PatrolEvent:
    # identification
    id: str
    types: list[Literal["hunting", "herb_gathering", "border", "training"]]

    # text and outcomes
    intro_text: str
    decline_text: str
    success_outcomes: list[Union[dict, EventOutcome]]
    fail_outcomes: list[Union[dict, EventOutcome]]
    antag_success_outcomes: list[Union[dict, EventOutcome]] = field(
        default_factory=list
    )
    antag_fail_outcomes: list[Union[dict, EventOutcome]] = field(default_factory=list)

    # constraints
    frequency: int = 4
    weight: int = 1  # will be increased via code
    chance_of_success: int = 0  # out of 100
    location: list[str] = field(default_factory=list)
    season: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    poi: Optional[dict[str, list]] = None
    required_statuses: dict[str, list[int]] = field(default_factory=dict)
    involved_cats: dict[str, Union[InvolvedCatDict, dict]] = field(default_factory=dict)
    relationship_constraint: list[RelationshipConstraintDict] = field(
        default_factory=list[RelationshipConstraintDict]
    )

    # art
    patrol_art: Optional[str] = None
    patrol_art_clean: Optional[str] = None

    def __post_init__(self):
        self.weight = 1

        if "any" not in self.location:
            # add 4 for every biome not listed
            self.weight += 4 * (len(constants.BIOME_TYPES) - len(self.location))

        if "any" not in self.season:
            # add 4 for every season not listed
            self.weight += 4 * (len(constants.SEASONS) - len(self.season))

        # add 8, 6, 4 or 2 if there are between 1-4 specific named locations
        # todo: check for balancing
        if self.poi.get("name") and not 1 > len(self.poi["name"]) > 5:
            self.weight += 8 - 2 * len(self.poi["name"])
        elif self.poi.get("tags"):
            # add 4-1 depending on how many specific points of interest are included
            # but only if specific ones are not already requested
            self.weight += min(4, len(self.poi.get("tags", [])))

        # LOTS of weight on rel constraints
        self.weight += len(self.relationship_constraint) * 20

    @property
    def new_cat(self) -> bool:
        """Returns boolean if there are any outcomes that results in
        a new cat joining (not just meeting)"""

        for outcome in (
            self.success_outcomes
            + self.fail_outcomes
            + self.antag_fail_outcomes
            + self.antag_success_outcomes
        ):
            for abbr in outcome.involved_cats:
                # if "n_c" is in an abbreviation, then that's a potential new cat
                if "n_c" in abbr:
                    # now we look at any join parameters to see if this specific cat is joining
                    for join_cats in outcome.join:
                        # if the abbr is present, then the cat is joining!
                        if abbr in join_cats["cats"]:
                            return True

        return False

    @property
    def other_clan(self) -> bool:
        """Return boolean indicating if any outcome has any reputation effect"""
        for outcome in (
            self.success_outcomes
            + self.fail_outcomes
            + self.antag_fail_outcomes
            + self.antag_success_outcomes
        ):
            if outcome.reputation_changes.get("other_clan"):
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
            for supply_change in out.supply:
                if supply_change["type"] not in HERBS:
                    continue
                herb_list.extend(
                    [herb for herb in supply_change["type"] if herb not in herb_list]
                )

        return herb_list

    def _generate_outcomes(self):
        """
        Generates outcome objects for each outcome in the patrol
        """
        success = self.success_outcomes.copy()
        fail = self.fail_outcomes.copy()
        antag_success = self.antag_success_outcomes.copy()
        antag_fail = self.antag_fail_outcomes.copy()

        for outcome in success:
            self.success_outcomes.append(EventOutcome(**outcome))
        for outcome in fail:
            self.fail_outcomes.append(EventOutcome(**outcome))
        for outcome in antag_success:
            self.antag_success_outcomes.append(EventOutcome(**outcome))
        for outcome in antag_fail:
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
        # until we have one that passes. this is the outcome we'll use!

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
                test_outcome = choices(
                    possible_outcomes, weights=[x.weight for x in possible_outcomes]
                )[0]

                # try to filter
                if _check_outcome_constraints(test_outcome):
                    chosen_success = test_outcome
                else:
                    tested_outcomes.add(test_outcome)

            if not chosen_failure:
                possible_outcomes = [
                    x
                    for x in fail_outcomes
                    if x.frequency == chosen_frequency and x not in tested_outcomes
                ]
                test_outcome = choices(
                    possible_outcomes, weights=[x.weight for x in possible_outcomes]
                )[0]
                # try to filter
                if _check_outcome_constraints(test_outcome):
                    chosen_success = test_outcome
                else:
                    tested_outcomes.add(test_outcome)

            if not chosen_success or not chosen_failure:
                used_frequencies.add(chosen_frequency)
                chosen_frequency = find_new_frequency(used_frequencies)

        return chosen_success, chosen_failure


def _check_outcome_constraints(
    outcome: EventOutcome, involved_cats: dict[str, Cat]
) -> bool:
    if not event_for_location(outcome.location):
        return False

    if not event_for_season(outcome.season):
        return False

    # TODO: min_max_status stuff for required_statuses

    # TODO: mentoring stuff needs to be included.. and a cat?
    if not event_for_tags(outcome.tags):
        return False

    if not event_for_reputation(outcome.required_reputation.get("outsider")):
        return False

    # TODO: need other_clan
    if not event_for_clan_relations(outcome.required_reputation.get("other_clan")):
        return False

    if outcome.supply:
        if not event_for_freshkill_supply(game.clan.freshkill_pile):
            return False

        if not event_for_herb_supply():
            return False

    for abbr, constraints in outcome.involved_cats.items():
        possible_cats = [involved_cats.get(abbr)]
        if not possible_cats:
            # TODO: grab all cats from patrol that haven't been used yet
            # need to grab apps for app abbrs
            # and sort by age so that we grab older cats for for r_c
            pass

        chosen_cat = None
        while not chosen_cat and possible_cats:
            test_cat = possible_cats[0]
            if event_for_cat(constraints, test_cat):
                chosen_cat = test_cat

        if not chosen_cat:
            return False

        involved_cats[abbr] = chosen_cat

    return True
