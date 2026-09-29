import random
from random import choice
from typing import Literal

import i18n

from scripts.cat.cats import Cat
from scripts.cat.enums import CatCompatibility
from scripts.cat_relations.relationship import Relationship, create_one_relationship
from scripts.events_module.event_information import EventInformation
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource
from scripts.events_module.text_adjust import (
    event_text_adjust,
    relationship_text_adjust,
)
from scripts.events_module.consequences import change_relationship_values
from scripts.events_module.event_filters import (
    get_highest_romantic_relation,
    get_personality_compatibility,
)
from scripts.config import get_config


# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

current_loaded_lang = None

MATE_DICTS = {}
BREAKUP_STRINGS = {}
POLY_MATE_DICTS = {}


def handle_mates_and_breakup(cat: Cat):
    """
    Checks if the given cat should move on from prior mates, breakup current ones, or take on a new one.
    :param cat: Cat to check
    """
    _rebuild_dicts()

    # check setting first
    if cat.no_mates:
        return

    # just ensure relationships exist
    for m in cat.mate:
        mate = Cat.fetch_cat(m)
        if mate.ID not in cat.relationships:
            create_one_relationship(cat, mate)
        if cat.ID not in mate.relationships:
            create_one_relationship(mate, cat)

    _handle_moving_on(cat)
    _handle_breakup_events(cat)
    _handle_new_mate_events(cat)


def _handle_moving_on(cat: Cat, disable_random: bool = False):
    """Handles moving on from dead or outside mates
    :param cat: cat who may try to move on
    :param disable_random: used for testing
    """
    for mate_id in cat.mate:
        # check valid mate
        if mate_id not in Cat.all_cats:
            print(f"WARNING: Cat #{cat} has a invalid mate. It will be removed.")
            cat.mate.remove(mate_id)
            continue

        mate: Cat = Cat.fetch_cat(mate_id)
        # check the mate's setting
        if mate.no_mates:
            continue

        # check if the mate has been gone for at least 4 moons
        dead_or_gone = (
            not mate.status.alive_in_player_clan and mate.status.moons_as >= 4
        )

        # if cat is not grief stricken, then we try to move on
        if "grief stricken" not in cat.illnesses and dead_or_gone:
            chance = get_config("mates.moving_on.chance")
            for threshold_reached in [
                cat.personality.stability > 8,
                cat.personality.sociability < 8,
                cat.personality.aggression < 8,
            ]:
                if threshold_reached:
                    chance += get_config("mates.moving_on.facet_influence")

            if random.random() <= chance or disable_random:
                text = i18n.t("hardcoded.move_on_dead_mate", mate=str(mate.name))
                game.cur_events_list.append(
                    EventInformation(
                        text, ["relation"], cat_dict={"m_c": cat, "r_c": mate}
                    )
                )
                cat.unset_mate(mate)


def _handle_breakup_events(cat: Cat):
    """Triggers and handles any events that results in a breakup"""

    for x in cat.mate:
        mate = Cat.fetch_cat(x)

        # check the mate's setting
        if mate.no_mates:
            continue

        _attempt_breakup(cat, mate)


def _attempt_breakup(cat_from: Cat, cat_to: Cat, disable_random: bool = False):
    """Checks if the cats wish to breakup and handles the ensuing result."""

    if not _check_if_breakup(cat_from, cat_to, disable_random):
        return

    # gather relationships
    relationship_from: Relationship = cat_from.relationships[cat_to.ID]
    relationship_to: Relationship = cat_to.relationships[cat_from.ID]

    # Determine the type of breakup
    possible_breakups = get_config("mates.breakup.default_weights")

    # most of these are determined solely by the cat_from's feelings, except for deciding to be friends
    # CHILL
    if relationship_from.romance < 40:
        possible_breakups["chill_breakup"] += 2
    # LOST FEELING
    if relationship_from.romance < 20:
        possible_breakups["lost_feelings"] += 5
    # FIGHT/BAD
    if relationship_from.total_relationship_value < 80:
        possible_breakups["had_fight"] += 3
        possible_breakups["bad_breakup"] += 2
    # FRIENDLY
    if relationship_from.like > 40 and relationship_to.like > 40:
        possible_breakups["decided_to_be_friends"] += 5

    breakup_type = random.choices(
        list(possible_breakups.keys()), weights=list(possible_breakups.values())
    )[0]

    # GET TEXT
    text = choice(BREAKUP_STRINGS[breakup_type])
    text = event_text_adjust(Cat, text, main_cat=cat_from, random_cat=cat_to)

    breakup_changes = get_config(f"mates.breakup.reactions.{breakup_type}")
    variability = get_config("mates.breakup.reactions.variability")

    # CAT_FROM REACTION
    cat_from_change = breakup_changes.copy()
    for change in cat_from_change:
        cat_from_change[change] += random.randint(variability[0], variability[1])
    cat_from_change["cats_from"] = [cat_from]
    cat_from_change["cats_to"] = [cat_to]
    cat_from_change["log"] = text

    # CAT_TO REACTION
    cat_to_change = breakup_changes.copy()
    for change in cat_to_change:
        cat_to_change[change] += random.randint(variability[0], variability[1])

    cat_to_change["cats_from"] = [cat_to]
    cat_to_change["cats_to"] = [cat_from]
    cat_to_change["log"] = text

    # CHANGE VALUES
    change_relationship_values(
        **cat_from_change,
    )
    change_relationship_values(
        **cat_to_change,
    )

    cat_from.unset_mate(cat_to, user_initiated_breakup=False)

    game.cur_events_list.append(
        EventInformation(
            text,
            ["relation", "misc"],
            [cat_from.ID, cat_to.ID],
            cat_dict={"m_c": cat_from, "r_c": cat_to},
        )
    )


def _check_if_breakup(cat_from: Cat, cat_to: Cat, disable_random: bool = False) -> bool:
    """
    Returns True if the cats should break up
    """
    # Moving on, not breakups, occur when one mate is dead or outside.
    if not cat_to.status.alive_in_player_clan:
        return False

    chance_number = _get_breakup_chance(cat_from, cat_to)

    if chance_number == 0 and not disable_random:
        return False

    return not int(random.random() * chance_number) or disable_random


def _get_breakup_chance(cat_from: Cat, cat_to: Cat) -> int:
    """
    Looks into the current values and calculates the chance of breaking up. The lower, the more likely they will break up.
    :return: chance of breaking up
    """
    # Gather relationships
    relationship: Relationship = cat_from.relationships[cat_to.ID]

    # No breakup chance if the cat is above the breakup threshold.
    threshold = get_config("mates.breakup.initial_chance.threshold")
    if relationship.total_relationship_value > threshold:
        return 0

    chance_number = get_config("mates.breakup.initial_chance.default_chance")
    for value in [
        relationship.romance,
        relationship.like,
        relationship.respect,
        relationship.trust,
        relationship.comfort,
    ]:
        chance_number += int(value / 10)

    # change the change based on the personality
    compatibility = get_personality_compatibility(cat_from, cat_to)
    if compatibility == CatCompatibility.POSITIVE:
        chance_number += get_config(
            "mates.breakup.initial_chance.positive_compatibility"
        )
    if compatibility == CatCompatibility.NEGATIVE:
        chance_number += get_config(
            "mates.breakup.initial_chance.negative_compatibility"
        )

    # Then, at least a 1/5 chance
    chance_number = max(chance_number, 5)

    return chance_number


def _handle_new_mate_events(cat: Cat):
    """Triggers and handles any events that result in a new mate"""

    # no trying to take a new mate if you're sad
    if "grief stricken" in cat.illnesses:
        return

    # First, check high love confession
    if _attempt_confession(cat):
        return

    # Then, handle the mutual interest events
    # Choose some subset of cats that they have relationships with
    if not cat.relationships:
        return
    subset = [
        Cat.fetch_cat(x)
        for x in cat.relationships
        if x not in cat.mate
        and Cat.fetch_cat(x).status.alive_in_player_clan
        and cat.is_potential_mate(Cat.fetch_cat(x))
    ]
    if not subset:
        return

    subset = random.sample(subset, max(int(len(subset) / 3), 1))

    # see if any of them want to pair up
    for other_cat in subset:
        _attempt_mutual_interest_mates(cat, other_cat)


def _attempt_confession(cat_from: Cat) -> bool:
    """
    Check if the cat has a high love for another and attempt to become mates. Handles resulting rejection or acceptance.
    return: bool if event is triggered or not
    """

    # get the highest romantic love relationship
    chosen_relationship = get_highest_romantic_relation(
        cat_from.relationships.values(), exclude_mate=True, potential_mate=True
    )

    if not chosen_relationship:
        return False

    # Config check
    if not get_config("mates.allow_mating"):
        return False

    # check if it meets confession threshold
    condition = get_config("mates.confession.make_confession")
    if not chosen_relationship.relationship_qualifies(condition):
        return False

    cat_to: Cat = chosen_relationship.cat_to

    # need to be in the same "place"
    if cat_to.status.group != cat_from.status.group:
        return False

    # need to be okay to try and approach this cat
    if not _check_against_grief(cat_from, cat_to):
        return False

    # CONFESS
    become_mates, cat_from_change, cat_to_change, mate_string = _try_confession(
        cat_from, cat_to
    )

    if not become_mates:
        return False

    # do the final prep of the rel change dicts
    cat_from_change["cats_from"] = [cat_from]
    cat_from_change["cats_to"] = [cat_to]
    cat_from_change["log"] = mate_string

    cat_to_change["cats_from"] = [cat_to]
    cat_to_change["cats_to"] = [cat_from]
    cat_to_change["log"] = mate_string

    # CHANGE VALUES
    change_relationship_values(
        **cat_from_change,
    )
    change_relationship_values(
        **cat_to_change,
    )

    game.cur_events_list.append(
        EventInformation(
            mate_string,
            ["relation", "misc"],
            cat_dict={"m_c": cat_from, "r_c": cat_to},
        )
    )

    if become_mates:
        cat_from.set_mate(cat_to)

    return True


def _try_confession(cat_from, cat_to) -> tuple[bool, dict, dict, str]:
    # CHECK POLY
    existing_from_cat_mates, existing_to_cat_mates = _get_existing_mates(
        cat_from, cat_to
    )
    poly = any([existing_from_cat_mates, existing_to_cat_mates])

    if poly and not _current_mates_allow_new_mate(
        cat_from, cat_to, existing_from_cat_mates, existing_to_cat_mates
    ):
        return False, {}, {}, ""

    become_mates = False
    # accept confession
    condition = get_config("mates.confession.accept_confession")
    variability = get_config("mates.confession.reactions.variability")
    if cat_to.relationships[cat_from.ID].relationship_qualifies(condition):
        become_mates = True
        if cat_from.ID in cat_to.previous_mates:
            mate_string = _get_mate_string(
                "high_romantic_makeup",
                poly,
                existing_from_cat_mates,
                existing_to_cat_mates,
            )
            confession_changes = get_config("mates.confession.reactions.makeup")
            cat_from_change, cat_to_change = _get_relationship_change_dict(
                confession_changes, variability
            )
        else:
            mate_string = _get_mate_string(
                "high_romantic",
                poly,
                existing_from_cat_mates,
                existing_to_cat_mates,
            )
            confession_changes = get_config("mates.confession.reactions.accepted")
            cat_from_change, cat_to_change = _get_relationship_change_dict(
                confession_changes, variability
            )
    else:
        if cat_from.ID in cat_to.previous_mates:
            mate_string = _get_mate_string(
                "makeup_fail",
                poly,
                existing_from_cat_mates,
                existing_to_cat_mates,
            )
            confession_changes = get_config("mates.confession.reactions.makeup_fail")
            cat_from_change, cat_to_change = _get_relationship_change_dict(
                confession_changes, variability
            )
        else:
            mate_string = _get_mate_string(
                "rejected",
                poly,
                existing_from_cat_mates,
                existing_to_cat_mates,
            )
            confession_changes = get_config("mates.confession.reactions.rejected")
            cat_from_change, cat_to_change = _get_relationship_change_dict(
                confession_changes, variability
            )

    mate_string = relationship_text_adjust(mate_string, cat_from, cat_to)

    return become_mates, cat_from_change, cat_to_change, mate_string


def _attempt_mutual_interest_mates(
    cat_from: Cat, cat_to: Cat, disable_random: bool = False
):
    """Checks if the two cats have a high enough mutual interest to become mates. Handles the ensuing event if so."""

    become_mates = False

    if not _check_against_grief(cat_from, cat_to):
        return

    # Gather relationships
    if cat_to.ID in cat_from.relationships:
        relationship_from = cat_from.relationships[cat_to.ID]
    else:
        relationship_from = create_one_relationship(cat_from, cat_to)

    if cat_from.ID in cat_to.relationships:
        relationship_to = cat_to.relationships[cat_from.ID]
    else:
        relationship_to = create_one_relationship(cat_to, cat_from)

    mate_string = None
    mate_chance = get_config("mates.chance_fulfilled_condition")
    becoming_mates = not int(random.random() * mate_chance) or disable_random

    # has to be high because every moon this will be checked for each relationship in the game
    friends_to_lovers = get_config("mates.chance_friends_to_lovers")
    becoming_friend_to_lover = (
        not int(random.random() * friends_to_lovers) or disable_random
    )

    # already return if there is 'no' hit (everything above 0), other checks are not necessary
    if not becoming_mates and not becoming_friend_to_lover:
        return

    # CHECK POLY
    existing_from_cat_mates, existing_to_cat_mates = _get_existing_mates(
        cat_from, cat_to
    )
    poly = any([existing_from_cat_mates, existing_to_cat_mates])

    if poly and not _current_mates_allow_new_mate(
        cat_from, cat_to, existing_from_cat_mates, existing_to_cat_mates
    ):
        return

    # GET TOGETHER
    if (
        becoming_mates
        and relationship_from.relationship_qualifies(get_config("mates.mate_condition"))
        and relationship_to.relationship_qualifies(get_config("mates.mate_condition"))
    ):
        become_mates = True
        if cat_from.ID in cat_to.previous_mates:
            mate_string = _get_mate_string(
                "low_romantic_makeup",
                poly,
                existing_from_cat_mates,
                existing_to_cat_mates,
            )
        else:
            mate_string = _get_mate_string(
                "low_romantic",
                poly,
                existing_from_cat_mates,
                existing_to_cat_mates,
            )
    elif (
        becoming_friend_to_lover
        and relationship_from.relationship_qualifies(
            get_config("mates.like_to_romance")
        )
        and relationship_to.relationship_qualifies(get_config("mates.like_to_romance"))
    ):
        become_mates = True
        if cat_from.ID in cat_to.previous_mates:
            mate_string = _get_mate_string(
                "low_romantic_makeup",
                poly,
                existing_from_cat_mates,
                existing_to_cat_mates,
            )
        else:
            mate_string = _get_mate_string(
                "like_to_romance",
                poly,
                existing_from_cat_mates,
                existing_to_cat_mates,
            )

    if not become_mates:
        return

    if poly:
        print("----- POLY-POLY-POLY", cat_from.name, cat_to.name)
        print(cat_from.mate)
        print(cat_to.mate)

    mate_string = relationship_text_adjust(mate_string, cat_from, cat_to)

    cat_from_change = {
        "cats_from": [cat_from],
        "cats_to": [cat_to],
        "romance": 10,
        "log": mate_string,
    }
    cat_to_change = {
        "cats_from": [cat_to],
        "cats_to": [cat_from],
        "romance": 10,
        "log": mate_string,
    }
    # CHANGE VALUES
    change_relationship_values(
        **cat_from_change,
    )
    change_relationship_values(
        **cat_to_change,
    )

    cat_from.set_mate(cat_to)
    game.cur_events_list.append(
        EventInformation(
            mate_string,
            ["relation", "misc"],
            cat_dict={"m_c": cat_from, "r_c": cat_to},
        )
    )


def _current_mates_allow_new_mate(
    cat_from: Cat, cat_to: Cat, cat_from_mates: list[str], cat_to_mates: list[str]
) -> bool:
    """
    Check if all current mates fulfill the required conditions to allow a new mate.
    :return: True if conditions are fulfilled, False if not
    """
    current_mate_condition = get_config("mates.poly.current_mate_condition")
    current_to_new_condition = get_config("mates.poly.mates_to_each_other")

    # check relationship from current mates from cat_from
    for mate_id in cat_from_mates:
        mate: Cat = Cat.fetch_cat(mate_id)
        if mate_id in cat_from.relationships and cat_from.ID in mate.relationships:
            if not cat_from.relationships[mate_id].relationship_qualifies(
                current_mate_condition
            ) or not mate.relationships[cat_from.ID].relationship_qualifies(
                current_mate_condition
            ):
                return False

        if mate_id in cat_to.relationships and cat_to.ID in mate.relationships:
            if not cat_to.relationships[mate_id].relationship_qualifies(
                current_to_new_condition
            ) or not mate.relationships[cat_to.ID].relationship_qualifies(
                current_to_new_condition
            ):
                return False

    # check relationship from current mates from cat_to
    for mate_id in cat_to_mates:
        mate = Cat.fetch_cat(mate_id)
        if mate_id in cat_to.relationships and cat_to.ID in mate.relationships:
            if not cat_to.relationships[mate_id].relationship_qualifies(
                current_mate_condition
            ) or not mate.relationships[cat_to.ID].relationship_qualifies(
                current_mate_condition
            ):
                return False

        if mate_id in cat_from.relationships and cat_from.ID in mate.relationships:
            if not cat_from.relationships[mate_id].relationship_qualifies(
                current_to_new_condition
            ) or not mate.relationships[cat_from.ID].relationship_qualifies(
                current_to_new_condition
            ):
                return False

    return True


def _check_against_grief(cat_from: Cat, cat_to: Cat) -> bool:
    """
    Checks if cat_to will still attempt to become mates with a grief stricken cat_from.
    :return: True if they will attempt, False if they won't
    """
    if "grief stricken" not in cat_to.illnesses:
        return True

    chance = get_config("mates.approach_grief.chance")
    # some cats might not be reading the room
    if cat_from.personality.trait in ("oblivious", "loving"):
        chance += get_config("mates.approach_grief.specific_trait_influence")
    for threshold_reached in [
        cat_from.personality.lawfulness < 8,
        cat_from.personality.sociability < 8,
        cat_from.personality.aggression > 8,
    ]:
        if threshold_reached:
            chance += get_config("mates.approach_grief.facet_influence")

    return random.random() < chance


def _get_existing_mates(cat_from: Cat, cat_to: Cat) -> tuple[list[str], list[str]]:
    """
    Returns living and present mates for cat_from and cat_to.
    return: Tuple with a list of IDs for each cat's mates
    """
    existing_from_cat_mates = [
        mate
        for mate in cat_from.mate
        if cat_from.fetch_cat(mate).status.alive_in_player_clan
    ]
    existing_to_cat_mates = [
        mate
        for mate in cat_to.mate
        if cat_to.fetch_cat(mate).status.alive_in_player_clan
    ]
    return existing_from_cat_mates, existing_to_cat_mates


def _get_relationship_change_dict(
    confession_changes: dict[str, dict], variability: tuple[int, int]
) -> tuple[dict, dict]:
    """
    Compiles rel change dictionaries for both cats according to the given base dictionary. Variability is applied to the values.
    """
    cat_from_change = confession_changes["cat_from"]
    for change in cat_from_change:
        cat_from_change[change] += random.randint(variability[0], variability[1])
    cat_to_change = confession_changes["cat_to"]
    for change in cat_to_change:
        cat_to_change[change] += random.randint(variability[0], variability[1])
    return cat_from_change, cat_to_change


def _get_mate_string(
    key: Literal[
        "high_romantic",
        "low_romantic",
        "like_to_romance",
        "rejected",
        "high_romantic_makeup",
        "low_romantic_makeup",
        "makeup_fail",
    ],
    poly: bool,
    cat_from_mates: list[str],
    cat_to_mates: list[str],
) -> str:
    """Returns a mate string within the given dictionary key based on given mates and poly status."""
    _rebuild_dicts()
    if not poly:
        return choice(MATE_DICTS[key])
    else:
        poly_key = ""
        if cat_from_mates and cat_to_mates:
            poly_key = "both_mates"
        elif not cat_to_mates and cat_from_mates:
            poly_key = "m_c_mates"
        elif not cat_from_mates and cat_to_mates:
            poly_key = "r_c_mates"
        if not poly_key:
            # none of the other involved mates are alive
            return choice(MATE_DICTS[key])
        return choice(POLY_MATE_DICTS[key][poly_key])


def _rebuild_dicts():
    global current_loaded_lang
    global MATE_DICTS
    global BREAKUP_STRINGS
    global POLY_MATE_DICTS

    if current_loaded_lang == i18n.config.get("locale"):
        return

    path = "events/relationship_events/"
    MATE_DICTS = load_lang_resource(f"{path}become_mates.json")
    BREAKUP_STRINGS = load_lang_resource(f"{path}breakup_mates.json")
    POLY_MATE_DICTS = load_lang_resource(f"{path}become_mates_poly.json")

    current_loaded_lang = i18n.config.get("locale")
