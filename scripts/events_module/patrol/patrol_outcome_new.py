from dataclasses import field, dataclass
from typing import Union

from scripts.events_module.parameter_dicts import (
    RelationshipConstraintDict,
    RelationshipChangeDict,
    InvolvedCatDict,
    RequiredReputationDict,
    ReputationChangesDict,
    DeathDict,
    InjuryDict,
    LostDict,
    SupplyDict,
    FutureEventDict,
)
from scripts.game_structure import constants


# slots increases performance and can be used since we won't be adding new attrs at runtime
@dataclass(slots=True)
class EventOutcome:
    # display
    outcome_art: str

    # constraints
    text: str
    frequency: int
    weight: int = 1
    location: list[str] = field(default_factory=list)
    season: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    required_reputation: RequiredReputationDict = field(default_factory=dict)
    involved_cats: dict[str, Union[InvolvedCatDict, dict]] = field(default_factory=dict)
    relationship_constraint: list[RelationshipConstraintDict] = field(
        default_factory=list[RelationshipConstraintDict]
    )
    relationship_changes: list[RelationshipChangeDict] = field(
        default_factory=list[RelationshipChangeDict]
    )

    # consequences
    exp_gained: int = 0
    reputation_changes: ReputationChangesDict = field(default_factory=dict)
    supply: list[SupplyDict] = field(default_factory=list[dict])
    death: list[DeathDict] = field(default_factory=list[dict])
    injury: list[InjuryDict] = field(default_factory=list[dict])
    lost: list[LostDict] = field(default_factory=list[dict])
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
        # represented by a short text snippet
        return f"{self.text[:30]}..."

    def execute_outcome(self):
        """
        Executes the outcome, applying any specified consequences.
        :returns: Outcome text, results text, list of created rel logs (might be empty)
        """

        rel_results = {}

        # create new cats

        # handle joining

        # process text

        # handle death

        # handle lost

        # handle injuries

        # adjust text for logs

        # apply rel effects (append result text)

        # handle rep changes (outsider and other clan)

        # handle supply changes (prey and herbs)

        # handle exp

        # handle mentor/app stuff

        # handle future event

        # return all the bullshit
