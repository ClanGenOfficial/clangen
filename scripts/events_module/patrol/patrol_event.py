#!/usr/bin/env python3
# -*- coding: ascii -*-
from typing import List, Union

from scripts.events_module.patrol.patrol_outcome import PatrolOutcome
from scripts.game_structure import constants


class PatrolEvent:
    def __init__(
        self,
        patrol_id,
        biome: List[str] = None,
        camp: List[str] = None,
        season: List[str] = None,
        types: List[str] = None,
        tags: List[str] = None,
        frequency: int = 4,
        patrol_art: Union[str, None] = None,
        patrol_art_clean: Union[str, None] = None,
        intro_text: str = "",
        decline_text: str = "",
        chance_of_success=0,
        success_outcomes: List[PatrolOutcome] = None,
        fail_outcomes: List[PatrolOutcome] = None,
        antag_success_outcomes: List[PatrolOutcome] = None,
        antag_fail_outcomes: List[PatrolOutcome] = None,
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
            self.weight += 4
        self.camp = camp if camp is not None else ["any"]
        if "any" not in self.camp:
            self.weight += 4
        self.season = season if season is not None else ["any"]
        if "any" not in self.season:
            self.weight += len(constants.SEASONS) - len(
                self.season
            )  # this increases the weight inversely to the number of season constraints

        self.tags = tags if tags is not None else []
        self.chance_of_success = chance_of_success  # out of 100

        self.min_cats = min_cats
        self.max_cats = max_cats
        self.weight += 6 - (
            self.max_cats - self.min_cats
        )  # the narrower this range, the higher weighted we want it

        self.min_max_status = min_max_status if min_max_status is not None else {}
        self.weight += len(self.min_max_status) * 2

        self.relationship_constraints = (
            relationship_constraints if relationship_constraints is not None else []
        )
        self.weight += len(self.relationship_constraints) * 3
        self.pl_skill_constraints = (
            pl_skill_constraints if pl_skill_constraints is not None else []
        )
        self.weight += len(self.pl_skill_constraints)
        self.pl_trait_constraints = (
            pl_trait_constraints if pl_trait_constraints is not None else []
        )
        self.weight += len(self.pl_trait_constraints)

        self.intro_text = intro_text
        self.decline_text = decline_text

        self.success_outcomes = success_outcomes if success_outcomes is not None else []
        self.fail_outcomes = fail_outcomes if fail_outcomes is not None else []
        self.antag_success_outcomes = (
            antag_success_outcomes if antag_success_outcomes is not None else []
        )
        self.antag_fail_outcomes = (
            antag_fail_outcomes if antag_fail_outcomes is not None else []
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
