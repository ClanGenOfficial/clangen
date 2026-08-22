from dataclasses import dataclass, field
from typing import Union, Optional

from scripts.cat.constants import ILLNESSES, PERMANENT, INJURIES
from scripts.cat.enums import CatRank, CatAge, CatGroup, CatStanding
from scripts.cat.personality import Personality
from scripts.cat.skills import SkillPath
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    RelationshipConstraintDict,
    RelationshipChangeDict,
    RequiredReputationDict,
    ReputationChangesDict,
    SupplyDict,
    DeathDict,
    ConditionDict,
    LostDict,
    JoinDict,
    FutureEventDict,
)
from scripts.game_structure import constants


# slots increases performance and can be used since we won't be adding new attrs at runtime
@dataclass(slots=True)
class TextPoolEvent:
    event_id: Optional[str] = None

    # display
    strings: list[str] = field(default_factory=list)
    outcome_art: Optional[str] = None
    outcome_art_clean: Optional[str] = None

    # weighting
    frequency: int = 4
    weight: int = 1  # will be increased via code in post init

    # constraints
    location: list[str] = field(default_factory=list)
    season: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    required_reputation: RequiredReputationDict = field(default_factory=dict)
    required_cat_types: dict[str, list[int]] = field(default_factory=dict)
    involved_cats: dict[str, Union[InvolvedCatDict, dict]] = field(default_factory=dict)
    relationship_constraint: list[RelationshipConstraintDict] = field(
        default_factory=list[RelationshipConstraintDict]
    )
    patrol_temperament: list[str] = field(default_factory=list)
    other_clan_temperament: list[str] = field(default_factory=list)

    # consequences
    relationship_changes: list[RelationshipChangeDict] = field(
        default_factory=list[RelationshipChangeDict]
    )
    exp_gained: int = 0
    reputation_changes: ReputationChangesDict = field(default_factory=dict)
    supply: list[SupplyDict] = field(default_factory=list[dict])
    death: list[DeathDict] = field(default_factory=list[dict])
    condition: list[ConditionDict] = field(default_factory=list[dict])
    lost: list[LostDict] = field(default_factory=list[dict])
    join: list[JoinDict] = field(default_factory=list[dict])
    future_event: list[FutureEventDict] = field(default_factory=list[dict])

    def __post_init__(self):
        self.weight = 1
        if self.location:
            self.weight += 4 * (len(constants.BIOME_TYPES) - len(self.location))
        if self.season:
            self.weight += 4 * (len(constants.SEASONS) - len(self.season))
        if self.tags:
            self.weight += len(self.tags) * 2
        self.weight += self.involved_cat_weight(self.involved_cats)

        if self.relationship_constraint:
            self.weight += 20

        if self.required_cat_types:
            self.weight += len(self.required_cat_types.keys()) * 5

        self.weight = max(1, self.weight)

    @staticmethod
    def involved_cat_weight(involved_cats: dict) -> int:
        weight = 0

        for constraints in involved_cats.values():
            if constraints.get("status"):
                if "-" in constraints["status"][0]:
                    weight += len(CatRank) - len(constraints["status"])
                else:
                    weight += len(constraints["status"])
            if constraints.get("past_status"):
                if "-" in constraints["past_status"][0]:
                    weight += len(CatRank) - len(constraints["past_status"])
                else:
                    weight += len(constraints["past_status"])
            if constraints.get("age"):
                if "-" in constraints["age"][0]:
                    weight += len(CatAge) - len(constraints["age"])
                else:
                    weight += len(constraints["age"])
            if constraints.get("group"):
                if "-" in constraints["group"][0]:
                    weight += len([g for g in [*CatGroup] if not g.is_ID()]) - len(
                        constraints["group"]
                    )
                else:
                    weight += len(constraints["group"])
            if constraints.get("standing"):
                weight += 10
                weight += 10

            if constraints.get("stat"):
                stat_weight = 0
                if constraints["stat"].get("skill"):
                    skill_constraints = constraints["stat"]["skill"]
                    if "-" in skill_constraints[0]:
                        stat_weight += len(SkillPath) - len(skill_constraints)
                    else:
                        stat_weight += len(skill_constraints)
                if constraints["stat"].get("trait"):
                    trait_constraint = constraints["stat"]["trait"]
                    if "-" in trait_constraint[0]:
                        stat_weight += len(
                            Personality.trait_ranges["normal_traits"].keys()
                        ) - len(trait_constraint)
                    else:
                        stat_weight += len(trait_constraint)
                if constraints.get("must_have_both"):
                    stat_weight *= 2
                weight += stat_weight

            if constraints.get("health"):
                if constraints["health"].get("condition"):
                    condition_constraint = constraints["health"]["condition"]
                    if "-" in condition_constraint[0]:
                        weight += len(
                            list(INJURIES.keys())
                            + list(ILLNESSES.keys())
                            + list(PERMANENT.keys())
                        ) - len(condition_constraint)
                    else:
                        weight += len(condition_constraint)

            if constraints.get("backstory"):
                if "-" in constraints["backstory"][0]:
                    weight += len(constraints["backstory"])
                else:
                    # i'm not gonna try and count up all the backstory possibilities, so we'll just do 40
                    weight += max(40 - len(constraints["backstory"]), 1)
                    # I do not expect someone to actually tag 50 backstories, but just in case

            if constraints.get("has_mentor"):
                weight += 10

        return weight

    def __repr__(self):
        return self.event_id if self.event_id else f"string event: {self.strings[0]}"
