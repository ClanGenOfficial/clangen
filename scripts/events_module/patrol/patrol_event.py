#!/usr/bin/env python3
# -*- coding: ascii -*-
from dataclasses import dataclass, field
from typing import Union, Literal, Optional

from scripts.cat.personality import Personality
from scripts.cat.skills import SkillPath
from scripts.clan_resources.herb.herb import HERBS
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    RelationshipConstraintDict,
)
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import constants

NUM_OF_TRAITS = len(Personality.trait_ranges["normal_traits"].keys()) + len(
    Personality.trait_ranges["kit_traits"].keys()
)
NUM_OF_SKILLS = len(SkillPath)


# slots increases performance and can be used since we won't be adding new attrs at runtime
@dataclass(slots=True)
class PatrolEvent:
    event_id: str

    intro_text: str
    decline_text: str
    success_outcomes: list[Union[dict, TextPoolEvent]]
    fail_outcomes: list[Union[dict, TextPoolEvent]]
    antag_success_outcomes: list[Union[dict, TextPoolEvent]] = field(
        default_factory=list
    )
    antag_fail_outcomes: list[Union[dict, TextPoolEvent]] = field(default_factory=list)

    types: list[Literal["hunting", "herb_gathering", "border", "training"]] = "border"
    frequency: int = 4
    weight: int = 1  # will be increased via code
    chance_of_success: int = 0  # out of 100
    location: list[str] = field(default_factory=list)
    season: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    poi: Optional[dict[str, list]] = field(default_factory=dict)
    required_cat_types: dict[str, list[int]] = field(default_factory=dict)
    involved_cats: dict[str, Union[InvolvedCatDict, dict]] = field(default_factory=dict)
    relationship_constraint: list[RelationshipConstraintDict] = field(
        default_factory=list[RelationshipConstraintDict]
    )
    patrol_temperament: list[str] = field(default_factory=list)
    other_clan_temperament: list[str] = field(default_factory=list)

    herbs_given: list = field(default_factory=list)
    new_cat: bool = False
    other_clan: bool = False

    # art
    patrol_art: Optional[str] = None
    patrol_art_clean: Optional[str] = None

    def __post_init__(self):
        self.weight = 1

        if self.location and "any" not in self.location:
            # add 4 for every biome not listed
            self.weight += 2 * (len(constants.BIOME_TYPES) - len(self.location))

        if self.season and "any" not in self.season:
            # add 4 for every season not listed
            self.weight += 2 * (len(constants.SEASONS) - len(self.season))

        if self.tags:
            self.weight += len(self.tags) * 2

        # add 8, 6, 4 or 2 if there are between 1-4 specific named locations
        # todo: check for balancing
        if self.poi.get("name") and not 1 > len(self.poi["name"]) > 5:
            self.weight += 8 - 2 * len(self.poi["name"])
        elif self.poi.get("tags"):
            # add 4-1 depending on how many specific points of interest are included
            # but only if specific ones are not already requested
            self.weight += min(4, len(self.poi.get("tags", [])))

        self.weight += TextPoolEvent.involved_cat_weight(self.involved_cats)

        # - 1 is for the patrol_cats that they all have
        self.weight += (len(self.required_cat_types.keys()) - 1) * 2

        # LOTS of weight on rel constraints
        self.weight += len(self.relationship_constraint) * 20

        self.weight = max(1, self.weight)

        self._generate_outcomes()

        self.new_cat = self._get_new_cat()
        self.other_clan = self._get_other_clan()
        self.herbs_given = self._get_herbs_given()

    def _get_new_cat(self) -> bool:
        """Returns boolean if there are any outcomes that results in
        a new cat joining (not just meeting)"""

        for outcome in (
            self.success_outcomes
            + self.fail_outcomes
            + self.antag_fail_outcomes
            + self.antag_success_outcomes
        ):
            if outcome.join:
                return True

        return False

    def _get_other_clan(self) -> bool:
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

    def _get_herbs_given(self) -> list:
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
                if supply_change["type"] == "freshkill":
                    continue
                if supply_change["type"] in herb_list:
                    continue
                herb_list.append(supply_change["type"])

        return herb_list

    def _generate_outcomes(self):
        """
        Generates outcome objects for each outcome in the patrol
        """
        success = self.success_outcomes.copy()
        fail = self.fail_outcomes.copy()
        antag_success = self.antag_success_outcomes.copy()
        antag_fail = self.antag_fail_outcomes.copy()

        # clear old dicts so we can replace them
        self.success_outcomes.clear()
        self.fail_outcomes.clear()
        self.antag_success_outcomes.clear()
        self.antag_fail_outcomes.clear()

        for outcome in success:
            self.success_outcomes.append(
                TextPoolEvent(
                    event_id=f"{self.event_id}_success{success.index(outcome)}",
                    **outcome,
                )
            )
        for outcome in fail:
            self.fail_outcomes.append(
                TextPoolEvent(
                    event_id=f"{self.event_id}_fail{fail.index(outcome)}", **outcome
                )
            )
        for outcome in antag_success:
            self.antag_success_outcomes.append(
                TextPoolEvent(
                    event_id=f"{self.event_id}_antag_success{antag_success.index(outcome)}",
                    **outcome,
                )
            )
        for outcome in antag_fail:
            self.antag_fail_outcomes.append(
                TextPoolEvent(
                    event_id=f"{self.event_id}_antag_fail{antag_fail.index(outcome)}",
                    **outcome,
                )
            )
