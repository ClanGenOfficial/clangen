from dataclasses import dataclass, field
from typing import Union, Optional

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
    id: Optional[str] = None

    # display
    strings: list[str] = field(default_factory=list)
    outcome_art: Optional[str] = None
    outcome_art_clean: Optional[str] = None

    # weighting
    frequency: Optional[int] = None
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
        # TODO: weighting for cat constraints
        pass

    def __repr__(self):
        return self.id if self.id else f"string event: {self.strings[0]}"
