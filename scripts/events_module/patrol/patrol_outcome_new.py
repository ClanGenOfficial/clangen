from dataclasses import field, dataclass
from random import choice
from typing import Union

from scripts.cat.cats import Cat
from scripts.clan import OtherClan
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
    JoinDict,
)
from scripts.events_module.text_adjust import event_text_adjust
from scripts.game_structure import constants


# slots increases performance and can be used since we won't be adding new attrs at runtime
@dataclass(slots=True)
class EventOutcome:
    # display
    outcome_art: str
    text: str

    # constraints
    frequency: int = 4
    weight: int = 1  # will be increased via code
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
    injury: list[InjuryDict] = field(default_factory=list[dict])
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
        # represented by a short text snippet
        return f"{self.text[:30]}..."

    def execute_outcome(
        self,
        patrol_involved_cats: dict[str, Cat],
        new_cats: list[str],
        other_clan: OtherClan,
    ):
        """
        Executes the outcome, applying any specified consequences.
        :returns: Outcome text, results text, list of created rel logs (might be empty)
        """

        rel_results = {}

        # process text
        processed_text = event_text_adjust(
            Cat,
            self.text,
            patrol_leader=patrol.patrol_leader,
            random_cat=patrol.random_cat,
            stat_cat=self.stat_cat,
            patrol_cats=patrol.patrol_cats,
            patrol_apprentices=patrol.patrol_apprentices,
            new_cats=patrol.new_cats,
            clan=game.clan,
            other_clan=patrol.other_clan,
        )

        # handle joining
        self.handle_joining(patrol_involved_cats)

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

    def handle_joining(self, patrol_involved_cats):
        for block in self.join:
            # gather up the kitties
            cat_list = []
            for abbr, cat in patrol_involved_cats.items():
                if abbr in block:
                    if isinstance(patrol_involved_cats[abbr], list):
                        cat_list.extend(patrol_involved_cats[abbr])
                    else:
                        cat_list.append(patrol_involved_cats[abbr])

            for cat in cat_list:
                cat.add_to_clan()
                if block.get("change_name"):
                    cat.change_name()

                if block.get("new_status"):
                    if cat.status.rank not in block["new_status"]:
                        cat.rank_change(
                            new_rank=choice(block["new_status"]), resort=True
                        )
                if cat.status.rank.is_any_apprentice_rank():
                    cat.update_mentor()
                    # ensuring that any cats joining as an apprentice will display the correct skills
                    cat.skills.primary.interest_only = True
                    if cat.skills.secondary:
                        cat.skills.secondary.interest_only = True

