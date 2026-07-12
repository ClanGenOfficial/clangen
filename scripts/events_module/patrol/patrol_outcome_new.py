import logging
from dataclasses import field, dataclass
from html import escape
from random import choice, randint
from typing import Union

import i18n

from scripts.cat.cats import Cat, ILLNESSES, PERMANENT
from scripts.cat.constants import INJURIES
from scripts.clan import OtherClan
from scripts.events_module.consequences import check_stolen_vitality
from scripts.events_module.parameter_dicts import (
    RelationshipConstraintDict,
    RelationshipChangeDict,
    InvolvedCatDict,
    RequiredReputationDict,
    ReputationChangesDict,
    DeathDict,
    ConditionDict,
    LostDict,
    SupplyDict,
    FutureEventDict,
    JoinDict,
)
from scripts.events_module.text_adjust import event_text_adjust, adjust_list_text
from scripts.game_structure import constants, game


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
        # TODO: rel logs too

        results = [
            self._handle_joining(patrol_involved_cats),
            self._handle_death(patrol_involved_cats, other_clan),
            self._handle_lost(patrol_involved_cats),
        ]

        # handle injuries

        # apply rel effects (append result text)

        # handle rep changes (outsider and other clan)

        # handle supply changes (prey and herbs)

        # handle exp

        # handle mentor/app stuff

        # handle future event

        # return all the bullshit

    def _handle_joining(self, patrol_involved_cats) -> str:
        """
        Handles cats joining the Clan
        """
        if not self.join:
            return ""

        joined = []
        cat_names = []
        for block in self.join:
            # gather up the kitties
            cat_list = []
            for abbr, cat in patrol_involved_cats.items():
                if abbr in block["cats"]:
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

            joined.extend(cat_list)
            for c in joined:
                cat_names.append(self._profile_link(c))

        return i18n.t("screens.patrol.new_outsider", cats=adjust_list_text(cat_names))

    def _handle_death(self, patrol_involved_cats, other_clan: OtherClan) -> str:
        """
        Handles cats dying on patrol
        """
        if not self.death:
            return ""

        death_tags = [t for t in self.tags if t in ("all_lives", "some_lives")]

        results = []
        player_cat_names = []
        other_cat_names = []

        dead_cats = []

        for block in self.death:
            for abbr, cat in patrol_involved_cats.items():
                if abbr in block["cats"]:
                    if isinstance(patrol_involved_cats[abbr], list):
                        dead_cats.extend(patrol_involved_cats[abbr])
                    else:
                        dead_cats.append(patrol_involved_cats[abbr])

            # we default to a body being present
            body = block.get("body", True)

            for c in dead_cats:
                # LEADER
                if c.status.is_leader:
                    if "all_lives" in death_tags:
                        lives_lost = game.clan.leader_lives
                        game.clan.leader_lives = 0
                        results.append(
                            event_text_adjust(
                                Cat,
                                i18n.t("cat.history.n_leader_death_all"),
                                main_cat=c,
                            )
                        )
                    elif "some_lives" in death_tags:
                        lives_lost = randint(2, max(1, game.clan.leader_lives - 1))
                        game.clan.leader_lives -= lives_lost
                        for i in range(lives_lost - 1):
                            c.history.add_death("multi_lives")
                        results.append(
                            event_text_adjust(
                                Cat,
                                i18n.t(
                                    "cat.history.n_leader_lost_lives", count=lives_lost
                                ),
                                main_cat=c,
                            )
                        )
                    else:
                        lives_lost = 1
                        game.clan.leader_lives -= 1
                        results.append(
                            event_text_adjust(
                                Cat,
                                i18n.t("cat.history.n_leader_lost_lives", count=1),
                                main_cat=c,
                            )
                        )
                    if extra_result := check_stolen_vitality(c, lives_lost):
                        results.append(extra_result)

                # OUTSIDER
                if c.status.is_outsider:
                    other_cat_names.append(self._profile_link(c))

                # NORMAL PLAYER CAT
                else:
                    player_cat_names.append(self._profile_link(c))

                # KILL
                self.__handle_death_history(c, block["history"], other_clan)
                c.die(body)

            # CREATE RESULTS
            if player_cat_names:
                results.append(
                    i18n.t(
                        "cat.history.regular_death",
                        cats=adjust_list_text(player_cat_names),
                        count=len(player_cat_names),
                    )
                )
            # other cats get special text
            if other_cat_names:
                results.append(
                    i18n.t(
                        "screens.patrol.dead_outsider",
                        cats=adjust_list_text(other_cat_names),
                        count=len(other_cat_names),
                    )
                )

        return " ".join(results)

    @staticmethod
    def __handle_death_history(
        cat: Cat, death_text: str, other_clan: OtherClan
    ) -> None:
        """Handles adding death history for dead cats."""

        if not death_text:
            print("WARNING: Death occurred, but some death history is missing.")

        if not death_text:
            death_text = i18n.t("defaults.patrol_regular_death")

        final_death_history = death_text.replace("o_c_n", other_clan.name)

        cat.history.add_death(death_text=final_death_history)

    def _handle_lost(self, patrol_involved_cats: dict) -> str:
        """
        Handles cats being lost
        """
        if not self.lost:
            return ""

        results = []

        for block in self.lost:
            # gather up the kitties
            cat_list = []
            for abbr, cat in patrol_involved_cats.items():
                if abbr in block["cats"]:
                    if isinstance(patrol_involved_cats[abbr], list):
                        cat_list.extend(patrol_involved_cats[abbr])
                    else:
                        cat_list.append(patrol_involved_cats[abbr])

            for c in cat_list:
                c.become_lost()

            results.append(
                i18n.t(
                    "screens.patrol.lost_cats",
                    count=len(cat_list),
                    cats=adjust_list_text(
                        [self._profile_link(cat) for cat in cat_list]
                    ),
                )
            )

        return " ".join(results)

    def _handle_conditions(
        self, patrol_involved_cats: dict, other_clan: OtherClan
    ) -> "":
        if not self.condition:
            return ""

        results = []
        condition_groups = constants.INJURY_GROUPS

        cats_and_conditions: dict[Cat, list[str]] = {}

        for block in self.condition:
            # gather up the kitties
            cat_list = []
            for abbr, cat in patrol_involved_cats.items():
                if abbr in block["cats"]:
                    if isinstance(patrol_involved_cats[abbr], list):
                        cat_list.extend(patrol_involved_cats[abbr])
                    else:
                        cat_list.append(patrol_involved_cats[abbr])

            possible_conditions = []
            for tag in block["condition"]:
                if tag in condition_groups:
                    possible_conditions.extend(condition_groups[tag])
                elif tag in INJURIES or tag in ILLNESSES or tag in PERMANENT:
                    possible_conditions.append(tag)

            if not possible_conditions:
                logging.warning(
                    f"Something went wrong with outcome: {self}. None of the given conditions were valid."
                )

            lethal = block.get("non_lethal", False)
            scars = block.get("scar_pool_override", [])

            for c in cat_list:
                current_conditions = (
                    list(c.injuries.keys())
                    + list(c.illnesses.keys())
                    + list(c.permanent_condition.keys())
                )

                if set(possible_conditions).issubset(current_conditions):
                    print(
                        "WARNING: All possible conditions are already on this cat! (poor kitty)"
                    )
                    continue

                conditions_for_cat = set(possible_conditions).difference(
                    set(current_conditions)
                )
                chosen_condition = choice(list(conditions_for_cat))

                if chosen_condition in INJURIES:
                    c.get_injured(
                        chosen_condition, lethal=lethal, potential_scars=scars
                    )
                elif chosen_condition in ILLNESSES:
                    c.get_ill(chosen_condition, lethal=lethal)
                else:
                    c.get_permanent_condition(chosen_condition)

                if block.get("no_results", False):
                    pass
                else:
                    if c not in cats_and_conditions:
                        cats_and_conditions[c] = [chosen_condition]
                    else:
                        cats_and_conditions[c].append(chosen_condition)

        for c, conditions in cats_and_conditions.items():
            # TODO: localize
            results.append(f"{self._profile_link(c)} got: {' '.join(conditions)}.")

        return results

    def __handle_condition_history(self, cat):

        

    @staticmethod
    def _profile_link(cat: Cat) -> str:
        """Create a hyperlink to a cat profile from patrol results."""
        return f'<a href="cat://{cat.ID}"><b>{escape(str(cat.name))}</b></a>'
