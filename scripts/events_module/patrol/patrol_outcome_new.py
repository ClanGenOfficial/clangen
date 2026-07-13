import logging
from dataclasses import field, dataclass
from html import escape
from random import choice, randint
from typing import Union

import i18n

from scripts.cat.cats import Cat, ILLNESSES, PERMANENT
from scripts.cat.constants import INJURIES
from scripts.cat.enums import CatRank
from scripts.cat.skills import SkillPath
from scripts.clan import OtherClan
from scripts.clan_package.cotc import change_clan_reputation, change_clan_relations
from scripts.clan_resources.freshkill import (
    FRESHKILL_ACTIVE,
    ADDITIONAL_PREY,
    HUNTER_EXP_BONUS,
)
from scripts.config import get_config
from scripts.events_module.consequences import check_stolen_vitality, unpack_rel_block
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
            self._handle_conditions(patrol_involved_cats, other_clan),
            self._handle_reputation_changes(other_clan),
        ]

        # handle supply changes (prey and herbs)

        # handle exp

        # handle mentor/app stuff

        # handle future event

        # apply rel effects (append result text)
        # TODO: gonna have to change how unpack_rel_block works
        rel_results.update(unpack_rel_block(Cat, self.relationship_changes, self))

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
    ) -> str:
        """
        Handles applying conditions to cats.
        """
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

                no_results = block.get("no_results", False)

                self.__handle_condition_history(
                    cat=c,
                    condition=chosen_condition,
                    scar_string=block.get("scar_history"),
                    death_string=block.get("death_history"),
                    other_clan=other_clan,
                    default_override=no_results,
                )

                if not no_results:
                    if c not in cats_and_conditions:
                        cats_and_conditions[c] = [chosen_condition]
                    else:
                        cats_and_conditions[c].append(chosen_condition)

        for c, conditions in cats_and_conditions.items():
            # TODO: localize
            results.append(f"{self._profile_link(c)} got: {' '.join(conditions)}.")

        return " ".join(results)

    def __handle_condition_history(
        self,
        cat: Cat,
        condition: str,
        scar_string: str,
        death_string: str,
        other_clan: OtherClan,
        default_override: bool = False,
    ):
        """
        Handles adding potential history to a cat. default_override will use the default text for the condition.
        """
        if not scar_string and not death_string:
            logging.warning(
                f"WARNING: Condition was added by outcome: {self} but no scar or death history string was given."
            )

        if default_override:
            cat.history.add_possible_history(
                condition=condition, death_text=None, scar_text=None
            )
            return

        if scar_string:
            scar_string = (
                scar_string
                if "o_c_n" not in scar_string
                else scar_string.replace("o_c_n", other_clan.name)
            )
        if death_string:
            death_string = (
                death_string
                if "o_c_n" not in death_string
                else death_string.replace("o_c_n", other_clan.name)
            )

        cat.history.add_possible_history(
            condition=condition, death_text=death_string, scar_text=scar_string
        )

    @staticmethod
    def _profile_link(cat: Cat) -> str:
        """Create a hyperlink to a cat profile from patrol results."""
        return f'<a href="cat://{cat.ID}"><b>{escape(str(cat.name))}</b></a>'

    def _handle_reputation_changes(self, other_clan: OtherClan) -> str:
        if not self.reputation_changes:
            return ""

        outside_change = self.reputation_changes.get("outsider")
        other_clan_change = self.reputation_changes.get("other_clan")

        if outside_change:
            change_clan_reputation(outside_change)
            if outside_change > 0:
                return i18n.t("screens.patrol.outsider_rep_improved")
            elif outside_change == 0:
                return i18n.t("screens.patrol.outsider_rep_neutral")
            else:
                return i18n.t("screens.patrol.outsider_rep_worsened")

        if other_clan_change:
            change_clan_relations(other_clan, other_clan_change)
            if other_clan_change > 0:
                return i18n.t("screens.patrol.clan_rep_improved", clan=other_clan.name)
            elif other_clan_change == 0:
                return i18n.t("screens.patrol.clan_rep_neutral", clan=other_clan.name)
            else:
                return i18n.t("screens.patrol.clan_rep_worsened", clan=other_clan.name)

        return ""

    def _handle_supply_changes(self):
        for block in self.supply:
            if block["type"] == "freshkill":
                self.__handle_prey(block)
            else:
                self.__handle_herbs(block)

    def __handle_prey(self, prey_info: SupplyDict):
        """Handle giving prey"""

        if not FRESHKILL_ACTIVE:
            return ""

        if not prey_info or game.clan.game_mode == "classic":
            return ""

        basic_amount = (
            get_config("prey.prey_requirement")[CatRank.WARRIOR] + ADDITIONAL_PREY
        )

        prey_types = {
            "increase_tiny": basic_amount / 2,
            "increase_small": basic_amount,
            "increase_medium": basic_amount * 1.8,
            "increase_large": basic_amount * 2.4,
            "increase_huge": basic_amount * 3.2,
        }

        basic_amount = prey_types.get(prey_info["adjust"])

        for tag in self.prey:
            basic_amount = prey_types.get(tag)
            if basic_amount is not None:
                used_tag = tag
                break
        else:
            print(f"{self.prey} - no prey amount tags in prey property")
            return ""

        total_amount = 0
        highest_hunter_tier = 0
        for cat in patrol.patrol_cats:
            total_amount += basic_amount
            if (
                cat.skills.primary.path == SkillPath.HUNTER
                and cat.skills.primary.tier > 0
            ):
                level = cat.experience_level
                tier = cat.skills.primary.tier
                if tier > highest_hunter_tier:
                    highest_hunter_tier = tier
                total_amount += int(
                    HUNTER_EXP_BONUS[level] * (HUNTER_BONUS[str(tier)] / 10 + 1)
                )
            elif (
                cat.skills.secondary
                and cat.skills.secondary.path == SkillPath.HUNTER
                and cat.skills.secondary.tier > 0
            ):
                level = cat.experience_level
                tier = cat.skills.secondary.tier
                if tier > highest_hunter_tier:
                    highest_hunter_tier = tier
                total_amount += int(
                    HUNTER_EXP_BONUS[level] * (HUNTER_BONUS[str(tier)] / 10 + 1)
                )

        # additional hunter buff for expanded mode
        if game.clan.game_mode == "expanded" and highest_hunter_tier:
            total_amount = int(
                total_amount * (HUNTER_BONUS[str(highest_hunter_tier)] / 20 + 1)
            )

        results = ""
        if total_amount > 0:
            total_amount = round(total_amount, 2)
            print(f"PREY ADDED: {total_amount}")
            game.freshkill_event_list.append(
                f"{total_amount} pieces of prey were caught on a patrol."
            )
            game.clan.freshkill_pile.add_freshkill(total_amount)
            results = i18n.t(f"screens.patrol.prey_{used_tag}")

        return results

    def __handle_herbs(self):
        pass
