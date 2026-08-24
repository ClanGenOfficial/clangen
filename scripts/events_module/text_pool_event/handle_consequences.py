import logging
from html import escape
from random import choice, randint
from typing import Union, Literal

import i18n

from scripts.cat.cats import Cat
from scripts.cat.constants import PERMANENT, ILLNESSES, INJURIES
from scripts.cat.enums import CatRank, CatThought
from scripts.cat.microservices.add_to_clan import add_to_clan, add_dependents_to_clan
from scripts.cat.skills import SkillPath
from scripts.clan import OtherClan
from scripts.clan_package.cotc import change_clan_reputation, change_clan_relations
from scripts.clan_resources.freshkill import (
    FRESHKILL_ACTIVE,
    ADDITIONAL_PREY,
    HUNTER_BONUS,
    HUNTER_EXP_BONUS,
)
from scripts.cat.microservices.conditions import (
    get_ill,
    get_injured,
    get_permanent_condition,
)
from scripts.config import get_config
from scripts.events_module.consequences import unpack_rel_block, check_stolen_vitality
from scripts.events_module.future.prep_and_trigger import prep_future_event
from scripts.events_module.parameter_dicts import SupplyDict
from scripts.events_module.relationship import relation_events
from scripts.events_module.text_adjust import event_text_adjust, adjust_list_text
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import game, constants

disable_random: bool = False
logger = logging.getLogger(__name__)


def execute_outcome(
    event: TextPoolEvent,
    event_involved_cats: dict[str, Union[Cat, list[Cat]]],
    other_clan: OtherClan = None,
):
    """
    Executes the outcome, applying any specified consequences.
    :returns: Outcome text, results text, list of created rel logs (might be empty)
    """

    rel_results = {}
    chosen_string = choice(event.strings)
    # process text
    processed_text = event_text_adjust(
        Cat,
        chosen_string,
        involved_cat_dict=event_involved_cats,
        clan=game.clan,
        other_clan=other_clan,
    )

    results = [
        _handle_joining(event, event_involved_cats),
        _handle_death(event, event_involved_cats, other_clan),
        _handle_lost(event, event_involved_cats),
        _handle_conditions(event, event_involved_cats, other_clan),
        _handle_reputation_changes(event, other_clan),
        _handle_supply_changes(event, event_involved_cats),
    ]

    _handle_exp(event, event_involved_cats)
    _handle_mentor_app(event_involved_cats)
    _handle_future_event(event, event_involved_cats)

    # just gonna make this a copy so that we don't accidentally change the base info
    rel_changes = event.relationship_changes.copy()
    for block in rel_changes:
        if "log" in block:
            for group in block["log"]:
                block["log"][group] = event_text_adjust(
                    Cat,
                    block["log"][group],
                    involved_cat_dict=event_involved_cats,
                    clan=game.clan,
                    other_clan=other_clan,
                )

    # apply rel effects (append result text)
    rel_results.update(
        unpack_rel_block(Cat, rel_changes, involved_cats=event_involved_cats)
    )
    if rel_results:
        results.append(i18n.t(f"screens.patrol.relationship_changed"))

    final_results = []
    for r in results:
        if r:
            final_results.append(r)

    # return all the bullshit
    return processed_text, "\n".join(final_results), rel_results


def _handle_joining(
    event: TextPoolEvent, event_involved_cats: dict[str, Union[Cat, list[Cat]]]
) -> str:
    """
    Handles cats joining the Clan
    """
    if not event.join:
        return ""

    joined = []
    cat_names = []
    for block in event.join:
        # gather up the kitties
        cat_list = []
        for abbr, cat in event_involved_cats.items():
            if abbr in block["cats"]:
                if isinstance(event_involved_cats[abbr], list):
                    cat_list.extend(event_involved_cats[abbr])
                else:
                    cat_list.append(event_involved_cats[abbr])

        for cat in cat_list:
            add_to_clan(cat)
            add_dependents_to_clan(cat)
            if block.get("change_name"):
                cat.change_name()

            if block.get("new_status"):
                if cat.status.rank not in block["new_status"]:
                    cat.rank_change(new_rank=choice(block["new_status"]), resort=True)
            if cat.status.rank.is_any_apprentice_rank():
                cat.update_mentor()
                # ensuring that any cats joining as an apprentice will display the correct skills
                cat.skills.primary.interest_only = True
                if cat.skills.secondary:
                    cat.skills.secondary.interest_only = True

        joined.extend(cat_list)

    for c in joined:
        cat_names.append(_profile_link(c))
        c.assign_thought(CatThought.ON_JOIN)

    relation_events.trigger_joining_relationship_events(joined)

    return i18n.t("screens.patrol.new_outsider", cats=adjust_list_text(cat_names))


def _handle_death(
    event: TextPoolEvent,
    event_involved_cats: dict[str, Union[Cat, list[Cat]]],
    other_clan: OtherClan,
) -> str:
    """
    Handles cats dying on patrol
    """
    if not event.death:
        return ""

    death_tags = [t for t in event.tags if t in ("all_lives", "some_lives")]

    results = []
    player_cat_names = []
    other_cat_names = []

    dead_cats = []

    for block in event.death:
        for abbr, cat in event_involved_cats.items():
            if abbr in block["cats"]:
                if isinstance(event_involved_cats[abbr], list):
                    dead_cats.extend(event_involved_cats[abbr])
                else:
                    dead_cats.append(event_involved_cats[abbr])

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
                            i18n.t("cat.history.n_leader_lost_lives", count=lives_lost),
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
                other_cat_names.append(_profile_link(c))

            # NORMAL PLAYER CAT
            else:
                player_cat_names.append(_profile_link(c))

            # KILL
            __handle_death_history(c, block["history"], other_clan)
            c.die(body)

        # CREATE RESULTS
        if block.get("no_results"):
            continue

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


def __handle_death_history(cat: Cat, death_text: str, other_clan: OtherClan) -> None:
    """Handles adding death history for dead cats."""

    if not death_text:
        print("WARNING: Death occurred, but some death history is missing.")
        death_text = i18n.t("defaults.patrol_regular_death")

    if other_clan:
        final_death_history = death_text.replace("o_c_n", other_clan.name)
    else:
        final_death_history = death_text

    cat.history.add_death(death_text=final_death_history)


def _handle_lost(
    event: TextPoolEvent, event_involved_cats: dict[str, Union[Cat, list[Cat]]]
) -> str:
    """
    Handles cats being lost
    """
    if not event.lost:
        return ""

    results = []

    for block in event.lost:
        # gather up the kitties
        cat_list = []
        for abbr, cat in event_involved_cats.items():
            if abbr in block["cats"]:
                if isinstance(event_involved_cats[abbr], list):
                    cat_list.extend(event_involved_cats[abbr])
                else:
                    cat_list.append(event_involved_cats[abbr])

        for c in cat_list:
            c.become_lost()

        results.append(
            i18n.t(
                "screens.patrol.lost_cats",
                count=len(cat_list),
                cats=adjust_list_text([_profile_link(cat) for cat in cat_list]),
            )
        )

    return " ".join(results)


def _handle_conditions(
    event: TextPoolEvent,
    event_involved_cats: dict[str, Union[Cat, list[Cat]]],
    other_clan: OtherClan,
) -> str:
    """
    Handles applying conditions to cats.
    """
    if not event.condition:
        return ""

    results = []
    condition_groups = constants.INJURY_GROUPS

    cats_and_conditions: dict[Cat, list[str]] = {}

    for block in event.condition:
        # gather up the kitties
        cat_list = []
        for abbr, cat in event_involved_cats.items():
            if abbr in block["cats"]:
                if isinstance(event_involved_cats[abbr], list):
                    cat_list.extend(event_involved_cats[abbr])
                else:
                    cat_list.append(event_involved_cats[abbr])

        possible_conditions = []
        for tag in block["condition"]:
            if tag in condition_groups:
                possible_conditions.extend(condition_groups[tag])
            elif tag in INJURIES or tag in ILLNESSES or tag in PERMANENT:
                possible_conditions.append(tag)

        if not possible_conditions:
            logging.warning(
                f"Something went wrong with outcome: {event}. None of the given conditions were valid."
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
                get_injured(c, chosen_condition, lethal=lethal, potential_scars=scars)
            elif chosen_condition in ILLNESSES:
                get_ill(c, chosen_condition, lethal=lethal)
            else:
                get_permanent_condition(c, chosen_condition)

            no_results = block.get("no_results", False)

            _handle_condition_history(
                event=event,
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
        results.append(
            i18n.t(
                "general.got_condition",
                cat=_profile_link(c),
                conditions=adjust_list_text(conditions),
            )
        )

    return " ".join(results)


def _handle_condition_history(
    event: TextPoolEvent,
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
        logger.warning(
            f"WARNING: Condition was added by outcome: {event} but no scar or death history string was given. This is okay if {condition} shouldn't kill or scar."
        )

    if default_override:
        cat.history.add_possible_history(
            condition=condition, death_text=None, scar_text=None
        )
        return

    if scar_string:
        scar_string = (
            scar_string
            if "o_c_n" not in scar_string or not other_clan
            else scar_string.replace("o_c_n", other_clan.name)
        )
    if death_string:
        death_string = (
            death_string
            if "o_c_n" not in death_string or not other_clan
            else death_string.replace("o_c_n", other_clan.name)
        )

    cat.history.add_possible_history(
        condition=condition, death_text=death_string, scar_text=scar_string
    )


def _profile_link(cat: Cat) -> str:
    """Create a hyperlink to a cat profile from patrol results."""
    return f'<a href="cat://{cat.ID}"><b>{escape(str(cat.name))}</b></a>'


def _handle_reputation_changes(event: TextPoolEvent, other_clan: OtherClan) -> str:
    if not event.reputation_changes:
        return ""

    results = []

    outside_change = event.reputation_changes.get("outsider")
    other_clan_change = event.reputation_changes.get("other_clan")

    if outside_change:
        change_clan_reputation(outside_change)
        if outside_change > 0:
            results.append(i18n.t("screens.patrol.outsider_rep_improved"))
        elif outside_change == 0:
            results.append(i18n.t("screens.patrol.outsider_rep_neutral"))
        else:
            results.append(i18n.t("screens.patrol.outsider_rep_worsened"))

    if other_clan_change and other_clan:
        change_clan_relations(other_clan, other_clan_change)
        if other_clan_change > 0:
            results.append(
                i18n.t("screens.patrol.clan_rep_improved", clan=other_clan.name)
            )
        elif other_clan_change == 0:
            results.append(
                i18n.t("screens.patrol.clan_rep_neutral", clan=other_clan.name)
            )
        else:
            results.append(
                i18n.t("screens.patrol.clan_rep_worsened", clan=other_clan.name)
            )

    return "\n".join(results)


def _handle_supply_changes(
    event: TextPoolEvent, event_involved_cats: dict[str, Union[Cat, list[Cat]]]
) -> str:
    """
    Handles applying supply increases
    """
    if not event.supply:
        return ""

    results = []
    herb_blocks = []
    prey_blocks = []
    for block in event.supply:
        if block["type"] == "freshkill":
            prey_blocks.append(block)
        else:
            herb_blocks.append(block)

    results.append(_handle_herbs(herb_blocks, event_involved_cats))
    results.append(_handle_prey(prey_blocks, event_involved_cats))
    return " ".join(results)


def _handle_prey(
    prey_info: list[SupplyDict], event_involved_cats: dict[str, Union[Cat, list[Cat]]]
) -> str:
    """Handle giving prey"""

    if (not prey_info or game.clan.game_mode == "classic") or not FRESHKILL_ACTIVE:
        return ""

    basic_amount = (
        get_config("prey.prey_requirement")[CatRank.WARRIOR] + ADDITIONAL_PREY
    )

    prey_types = {
        f"increase_{size}": basic_amount
        * get_config(f"prey.event_increase_modifiers.increase_{size}")
        for size in ("tiny", "small", "medium", "large", "huge")
    }

    results = []
    final_amount = 0
    hunter_bonus = 0
    highest_hunter_tier = 0

    for cat in event_involved_cats.get("patrol_cats"):
        if cat.skills.primary.path == SkillPath.HUNTER and cat.skills.primary.tier > 0:
            level = cat.experience_level
            tier = cat.skills.primary.tier
            if tier > highest_hunter_tier:
                highest_hunter_tier = tier
            hunter_bonus += int(
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
            hunter_bonus += int(
                HUNTER_EXP_BONUS[level] * (HUNTER_BONUS[str(tier)] / 10 + 1)
            )

    for prey in prey_info:
        amount_gained = (
            prey_types.get(prey["adjust"]) * len(event_involved_cats["patrol_cats"])
            + hunter_bonus
        )

        # additional hunter buff for expanded mode
        if game.clan.game_mode == "expanded" and highest_hunter_tier:
            amount_gained = int(
                amount_gained * (HUNTER_BONUS[str(highest_hunter_tier)] / 20 + 1)
            )

        if amount_gained > 0:
            final_amount += round(amount_gained)
            print(f"PREY ADDED: {amount_gained}")
            adjust_type = prey["adjust"].replace("increase_", "")
            results.append(i18n.t(f"screens.patrol.prey_{adjust_type}"))

    # TODO: localize
    game.freshkill_event_list.append(i18n.t("screens.prey_log", count=final_amount))

    game.clan.freshkill_pile.add_freshkill(final_amount)

    return " ".join(results)


def _handle_herbs(
    herb_info: list[SupplyDict], event_involved_cats: dict[str, Union[Cat, list[Cat]]]
) -> str:
    """Handle giving herbs"""

    if not herb_info or game.clan.game_mode == "classic":
        return ""

    # herb names for display message
    list_of_herb_strs = []
    # dict of herbs and amount found, for determining plural/singular count later on
    found_herbs = {}

    for herb in herb_info:
        herb_tag = herb["type"]
        change_type = herb["adjust"]

        quantity_allowed = _get_herb_increase_amount(event_involved_cats, change_type)

        if herb_tag == "random_herbs":
            # we want better control over how many herbs they'll gather in total here
            # get random herbs, add to storage, and get patrol outcome msg
            new_herb_strings, new_found_herbs = game.clan.herb_supply.get_found_herbs(
                med_cat=event_involved_cats["p_l"],
                specific_quantity_allowed=quantity_allowed,
            )
        else:
            # add found_herbs to storage and get patrol outcome msg
            (
                new_herb_strings,
                new_found_herbs,
            ) = game.clan.herb_supply.handle_found_herbs_outcomes(
                {herb_tag: quantity_allowed}
            )

        list_of_herb_strs.extend(new_herb_strings)
        found_herbs.update(new_found_herbs)

    herb_string = adjust_list_text(list_of_herb_strs).capitalize()

    full_amount_count = sum(found_herbs.values())

    game.herb_events_list.append(
        i18n.t("screens.patrol.herb_log", count=full_amount_count, herbs=herb_string)
    )

    return i18n.t(
        "screens.patrol.herbs_gathered", count=full_amount_count, herbs=herb_string
    )


def _get_herb_increase_amount(
    event_involved_cats: dict[str, Union[Cat, list[Cat]]],
    increase_tag: Literal[
        "increase_tiny",
        "increase_small",
        "increase_medium",
        "increase_large",
        "increase_huge",
    ],
) -> int:
    """
    finds out how many herbs can be gathered by given cats with given increase_tag
    """
    # find how many herbs each cat is allowed
    amount_per_cat = get_config(f"clan_resources.herbs.increase_amounts.{increase_tag}")

    # some random variance is also created
    random_variance = get_config("clan_resources.herbs.gathering_variance")

    total_increase = 0
    for c in event_involved_cats.get("patrol_cats"):
        # now we find how much this specific cat found
        amount_gathered = amount_per_cat
        if not disable_random:
            # add that random variation
            amount_gathered += randint(*random_variance)

        # give skill buffs
        cat_skills = c.skills.get_all()
        amount_gathered += cat_skills.get(SkillPath.SENSE, 0)

        # now add it to the total increase
        total_increase += amount_gathered

    return total_increase


def _handle_exp(
    event: TextPoolEvent, event_involved_cats: dict[str, Union[Cat, list[Cat]]]
):
    """
    Awards exp to the patrol cats
    """

    if not event.exp_gained:
        return

    if game.clan.game_mode == "classic":
        mode_modifier = 1
    else:
        mode_modifier = 3

    base_exp = 0
    if "masterful" in (
        x.experience_level for x in event_involved_cats.get("patrol_cats")
    ):
        max_boost = 10
    else:
        max_boost = 0

    patrol_exp = 2 * event.exp_gained
    gained_exp = patrol_exp + base_exp + max_boost
    gained_exp = max(
        gained_exp
        * (1 - 0.1 * len(event_involved_cats.get("patrol_cats")))
        / mode_modifier,
        1,
    )

    # Apprentice exp, does not depend on success
    if game.clan.game_mode == "classic":
        app_exp = 0
    else:
        app_exp = max(
            randint(1, 7) * (1 - 0.1 * len(event_involved_cats.get("patrol_cats"))), 1
        )

    if gained_exp or app_exp:
        for cat in event_involved_cats.get("patrol_cats"):
            if cat.status.rank.is_any_apprentice_rank():
                cat.add_experience(app_exp)
            else:
                cat.add_experience(gained_exp)


def _handle_mentor_app(event_involved_cats: dict[str, Union[Cat, list[Cat]]]):
    """Handles mentors influencing apprentices"""

    for cat in event_involved_cats.get("patrol_cats", []):
        mentor = Cat.fetch_cat(cat.mentor)
        if mentor in event_involved_cats["patrol_cats"]:
            affect_personality = cat.personality.mentor_influence(mentor.personality)
            affect_skills = cat.skills.mentor_influence(mentor)
            if affect_personality:
                cat.history.add_facet_mentor_influence(
                    mentor.ID, affect_personality[0], affect_personality[1]
                )
                print(str(cat.name), affect_personality)
            if affect_skills:
                cat.history.add_skill_mentor_influence(
                    affect_skills[0], affect_skills[1], affect_skills[2]
                )
                print(str(cat.name), affect_skills)


def _handle_future_event(
    event: TextPoolEvent, event_involved_cats: dict[str, Union[Cat, list[Cat]]]
):
    """
    collects required info for the future event and sends it to be prepped
    """
    if not event.future_event:
        return

    prep_future_event(
        event=event,
        event_id=event.event_id,
        possible_cats=event_involved_cats,
    )
