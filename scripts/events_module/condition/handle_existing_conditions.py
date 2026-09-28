import logging
from random import choice, random
from typing import Optional

import i18n

from scripts.cat.cats import Cat
from scripts.cat.conditions.condition_state import (
    ConditionState,
    update_permanent_condition_state,
    update_temporary_condition_state,
)
from scripts.cat.conditions.gain_conditions import (
    gain_temporary_condition,
    gain_permanent_condition,
)
from scripts.cat.conditions.permanent_condition import PermanentCondition
from scripts.cat.conditions.temporary_condition import TemporaryCondition
from scripts.cat.constants import TEMPORARY_CONDITIONS, PERMANENT_CONDITIONS
from scripts.cat.enums import CatRank, CatAge
from scripts.clan_package.settings import get_clan_setting
from scripts.clan_resources.freshkill import (
    FRESHKILL_ACTIVE,
    MAL_PERCENTAGE,
    STARV_PERCENTAGE,
)
from scripts.config import get_config
from scripts.events_module.ceremony.generate_normal_ceremony import create_ceremony
from scripts.events_module.condition.generate_condition_event import (
    generate_condition_event,
)
from scripts.events_module.condition.handle_new_conditions import logger
from scripts.events_module.event_information import EventInformation
from scripts.events_module.text_adjust import event_text_adjust
from scripts.game_structure import game

logger = logging.getLogger(__name__)

# these are only for use by tests!!!!!
force_progression = ""
force_risk = ""


def handle_nutrition(cat: Cat, nutrition_info: dict) -> None:
    """
    Handles gaining conditions or death for cats with low nutrient.
    This function should only be called if the game is in 'expanded' or 'cruel_season' mode.

    Starvation and malnutrtion must be handled separately from other illnesses due to their distinct death triggers.

        Parameters
        ----------
        cat : Cat
            the cat which has to be checked and updated
        nutrition_info : dict
            dictionary of all nutrition information (can be found in the freshkill pile)
    """
    if not FRESHKILL_ACTIVE:
        return

    if cat.ID not in nutrition_info.keys():
        logger.error(
            "Could not find cat with ID %s (%s) in the nutrition information.",
            cat.ID,
            str(cat.name),
        )
        return

    # get all events for a certain rank of a cat
    cat_nutrition = nutrition_info[cat.ID]

    event = None
    illness = None
    heal = False

    # handle death first, if percentage is 0 or lower, the cat will die
    if cat_nutrition.percentage <= 0:
        event = generate_condition_event(
            path="conditions/death_strings/starving.json", involved_cats={"m_c": cat}
        )
        # if the cat is the leader and isn't full dead
        # make them malnourished and refill nutrition slightly
        if cat.status.is_leader and game.clan.leader_lives > 0:
            mal_score = nutrition_info[cat.ID].max_score / 100 * (MAL_PERCENTAGE + 1)
            nutrition_info[cat.ID].current_score = round(mal_score, 2)
            gain_temporary_condition(cat, "malnourished")

        game.cur_events_list.append(event)
        return

    # heal cat if percentage is high enough and cat is ill
    if (
        cat_nutrition.percentage > MAL_PERCENTAGE
        and "malnourished" in cat.temporary_conditions
    ):
        heal = True
        illness = "malnourished"

    # heal cat if percentage is high enough and cat is ill
    elif (
        cat_nutrition.percentage > STARV_PERCENTAGE
        and "starving" in cat.temporary_conditions
    ):
        if cat_nutrition.percentage < MAL_PERCENTAGE:
            if "malnourished" not in cat.temporary_conditions:
                gain_temporary_condition(cat, "malnourished")
            illness = "starving"
            heal = True
        else:
            illness = "starving"
            heal = True

    elif MAL_PERCENTAGE >= cat_nutrition.percentage > STARV_PERCENTAGE:
        # because of the smaller 'nutrition buffer', kitten and elder should get the starving condition.
        if cat.status.rank in (CatRank.KITTEN, CatRank.ELDER):
            illness = "starving"
        else:
            illness = "malnourished"

    elif cat_nutrition.percentage <= STARV_PERCENTAGE:
        illness = "starving"

    # handle the gaining/healing illness
    if heal:
        event = generate_condition_event(
            path=f"conditions/healed_strings/{illness}.json", involved_cats={"m_c": cat}
        )
        cat.remove_condition(illness)
    elif not heal and illness:
        event = generate_condition_event(
            path=f"conditions/gain_temporary_condition_strings/{illness}.json",
            involved_cats={"m_c": cat},
        )
        gain_temporary_condition(cat, illness)

    if event:
        game.cur_events_list.append(event)


def handle_temporary_conditions(cat: Cat, forced_state: ConditionState = None):
    """
    Checks on the temporary conditions of the cat: updating their state and applying any relevant changes to both the condition and the cat
    """
    conditions_to_remove = []
    event_list = []
    progression_events = []

    for condition in cat.temporary_conditions.copy():
        if condition.omit_moonskip:
            continue

        condition_extra_info = TEMPORARY_CONDITIONS[condition.name]

        if forced_state:
            state = forced_state
        else:
            state = update_temporary_condition_state(condition)

        # PROGRESSION - this can happen during various states, so we check it first
        for progression, info in condition.progression.items():
            if info["when"] == state:
                chance = info["chance"]
                progression_events, conditions_to_remove = _check_progression(
                    cat, condition, progression, chance, conditions_to_remove
                )
                if progression_events:
                    # if there are events, then we progressed and should move on!
                    break

        if state == ConditionState.SKIPPED:
            continue

        elif state == ConditionState.FATAL:
            event_list = _apply_fatality(cat, condition, event_list)
            break

        elif state == ConditionState.HEALED:
            event = _attempt_scarring(
                cat,
                condition,
                possible_scars=condition_extra_info.get("possible_scars", []),
            )

            if not event:
                event = generate_condition_event(
                    path=f"conditions/healed_strings/{condition.name}.json",
                    involved_cats={"m_c": cat},
                )

            else:
                # if nothing else happened, make the scar event into EventInformation
                event = EventInformation(
                    event,
                    ["health"],
                    [cat.ID],
                )

            game.herb_events_list.append(event.text)

            cat.history.remove_possible_history(condition)
            conditions_to_remove.append(condition)

            if condition.is_complication:
                # if it's a complication, take it off whatever condition it's linked to
                for c in cat.temporary_conditions + cat.permanent_conditions:
                    if condition == c.current_complication:
                        c.current_complication = None

            continue

        elif state == ConditionState.CONTINUING:
            if condition in conditions_to_remove:
                # we don't want to give a risk if the condition was removed
                continue

            # decrease mortality on all conditions (mimicking the idea that the cat is healing in increments)
            if condition.mortality:
                condition.mortality = max(0.01, (condition.mortality - get_config("condition.related.moonskip_mortality_reduction")))

            additional_events, conditions_to_remove = _check_risks(
                cat, condition, conditions_to_remove
            )

            if additional_events:
                event_list.extend(additional_events)

        # add progression events to the end of the event_list
        # we want them at the end for continuity purposes,
        # i.e. cat heals from mangled leg -> discovers the leg is weakened
        if progression_events:
            event_list.extend(progression_events)

    for c in conditions_to_remove:
        cat.remove_condition(c.name)

    if event_list:
        game.cur_events_list.extend(event_list)


def handle_permanent_conditions(cat: Cat, forced_state: ConditionState = None):
    """
    Checks on the permanent conditions of the cat: updating their state and applying any relevant changes to both the condition and the cat
    """
    event_list: list[EventInformation] = []
    conditions_to_remove = []
    progression_events = []

    for condition in cat.permanent_conditions.copy():
        if condition.omit_moonskip:
            continue

        if forced_state:
            state = forced_state
        else:
            state = update_permanent_condition_state(condition)

        # PROGRESSION - this can happen during various states, so we check it first
        for progression, info in condition.progression.items():
            if info["when"] == state:
                chance = info["chance"]
                progression_events, conditions_to_remove = _check_progression(
                    cat, condition, progression, chance, conditions_to_remove
                )
                if progression_events:
                    # if there are events, then we progressed and should move on!
                    break

        if state == ConditionState.SKIPPED:
            continue

        elif state == ConditionState.FATAL:
            event_list = _apply_fatality(cat, condition, event_list)
            break

        elif state == ConditionState.REVEALED:
            event_list.append(
                generate_condition_event(
                    path=f"conditions/reveal_condition_strings/{condition.name}.json",
                    involved_cats={"m_c": cat},
                )
            )

        elif state == ConditionState.CONTINUING:
            if condition in conditions_to_remove:
                # we don't want to give a risk if the condition was removed
                continue

            additional_events, conditions_to_remove = _check_risks(
                cat, condition, conditions_to_remove
            )

            if additional_events:
                event_list.extend(additional_events)

        # add progression events to the end of the event_list
        # we want them at the end for continuity purposes,
        # i.e. cat heals from mangled leg -> discovers the leg is weakened
        if progression_events:
            event_list.extend(progression_events)

    for c in conditions_to_remove:
        cat.temporary_conditions.remove(c)

    if event_list:
        game.cur_events_list.extend(event_list)

    if not cat.dead:
        _determine_retirement(cat)


def _apply_fatality(cat, condition, event_list) -> list:
    event = generate_condition_event(
        path=f"conditions/death_strings/{condition.name}.json",
        involved_cats={"m_c": cat},
    )
    # clear event list first to make sure any heal or risk events from other injuries are not shown
    event_list.clear()
    event_list.append(event)
    game.herb_events_list.append(event.text)

    return event_list


def _check_risks(
    cat: Cat,
    condition: TemporaryCondition | PermanentCondition,
    conditions_to_remove: list[TemporaryCondition | PermanentCondition],
) -> tuple[list[EventInformation], list[TemporaryCondition | PermanentCondition]]:
    """
    Checks if the condition should apply a risk
    :param cat: The cat that the condition belongs to
    :param condition: The condition to check
    :param conditions_to_remove: The current list of conditions being removed. This will be modified within this function and returned.
    :return: A tuple of two lists: A list of new events created, and a list of conditions to remove
    """
    current_conditions = {
        c.name
        for c in cat.temporary_conditions + cat.permanent_conditions
        if c != condition
    }
    event_list = []

    full_condition_dict = TEMPORARY_CONDITIONS.copy()
    full_condition_dict.update(PERMANENT_CONDITIONS)

    # CHECK RISKS
    for risk, chance in condition.risks.items():
        if risk in cat.temporary_conditions:
            # don't double up
            continue

        # check for force_progression too, cus we don't want to do any risks if we need to progress instead
        if force_risk and risk != force_risk or force_progression:
            continue

        # don't give them a condition that they already have a progression of
        if _condition_overlaps(current_conditions, risk):
            continue

        if (chance and random() <= chance) or force_risk:
            # set the risk chance back down to make it less likely it occurs again
            # for complications this is set to 0 to avoid annoying loops
            if full_condition_dict[risk].get("is_complication", False):
                condition.risks[risk] = 0.0
                # mark the current condition as having this complication
                condition.current_complication = risk
            else:
                condition.risks[risk] = 0.05

            event = generate_condition_event(
                path=f"conditions/risk_strings/{condition.name}/{risk}.json",
                involved_cats={"m_c": cat},
            )

            event_list.append(event)
            if risk in TEMPORARY_CONDITIONS:
                gain_temporary_condition(cat, risk)
            else:
                gain_permanent_condition(cat, risk, is_congenital=False)

            return event_list, conditions_to_remove

    return event_list, conditions_to_remove


def _check_progression(
    cat: Cat,
    condition: TemporaryCondition | PermanentCondition,
    progression: str,
    chance: float,
    conditions_to_remove: list,
):
    """
    Checks if the condition should progress into the given progression
    :param cat: The cat that the condition belongs to
    :param condition: The condition to check
    :param progression: The name of the condition that the cat may progress to
    :param chance: The chance that the cat may progress
    :param conditions_to_remove: The current list of conditions being removed. This will be modified within this function and returned.
    :return: A tuple of two lists: A list of new events created, and a list of conditions to remove
    """
    event_list = []

    if progression in cat.temporary_conditions + cat.permanent_conditions:
        # don't double up
        return event_list, conditions_to_remove

    if force_progression and progression != force_progression:
        return event_list, conditions_to_remove

    current_conditions = {
        c.name
        for c in cat.temporary_conditions + cat.permanent_conditions
        if c != condition
    }

    # don't give them a condition that they already have a progression of
    if _condition_overlaps(current_conditions, progression):
        return event_list, conditions_to_remove

    if (chance and random() <= chance) or force_progression:
        scar_event = None
        if progression in TEMPORARY_CONDITIONS:
            gain_temporary_condition(cat, progression)
        elif progression in PERMANENT_CONDITIONS:
            if condition.name in TEMPORARY_CONDITIONS:
                if condition.progression[progression].get("allow_scar"):
                    requires_scar = PERMANENT_CONDITIONS[progression].get(
                        "requires_scar", False
                    )
                    scar_pool = TEMPORARY_CONDITIONS[condition.name].get(
                        "possible_scars", []
                    ) + PERMANENT_CONDITIONS[progression].get("possible_scars", [])
                    # if the condition is going from temp to perm, try to give a scar
                    scar_event = _attempt_scarring(
                        cat,
                        condition,
                        possible_scars=scar_pool,
                        guarantee_scar=requires_scar,
                    )

                    if requires_scar and not scar_event:
                        # if the cat couldn't be scarred for some reason, but the condition required it
                        # then we're gonna continue before we can give the condition
                        return event_list, conditions_to_remove

            gain_permanent_condition(cat, progression)

        event = generate_condition_event(
            path=f"conditions/progression_strings/{condition.name}/{progression}.json",
            involved_cats={"m_c": cat},
        )

        if scar_event:
            event.text = " ".join([scar_event, event.text])

        event_list.append(event)
        conditions_to_remove.append(condition)

        return event_list, conditions_to_remove

    return event_list, conditions_to_remove


def _condition_overlaps(current_conditions, new_condition):
    """
    Checks if given condition overlaps with the progressions of the current conditions.
    """
    all_conditions = TEMPORARY_CONDITIONS.copy()
    all_conditions.update(PERMANENT_CONDITIONS)

    if new_condition in all_conditions:
        further_progressions = list(all_conditions[new_condition]["progression"].keys())
        while further_progressions:
            if set(further_progressions).intersection(current_conditions):
                return True
            else:
                progression_list = further_progressions.copy()
                further_progressions = []
                for p in progression_list:
                    if p in all_conditions:
                        further_progressions.extend(
                            all_conditions[p]["progression"].keys()
                        )

    return False


def _determine_retirement(cat: Cat):
    """
    Checks if the cat should retire due to a condition
    """
    if get_clan_setting("retirement") or cat.no_retire or not cat.status.is_clancat:
        return

    if cat.status.rank not in (
        CatRank.NEWBORN,
        CatRank.KITTEN,
        CatRank.LEADER,
        CatRank.ELDER,
    ):
        for condition in cat.permanent_conditions:
            if condition.severity == "minor":
                continue

            if cat.status.moons_as <= 1:
                # no retiring on the first moon as a rank
                continue

            if condition.severity == "severe":
                # Higher chances for "severe". These are meant to be nearly 100% without
                # being 100%
                retire_chances = {
                    CatAge.NEWBORN: 0,
                    CatAge.KITTEN: 0,
                    CatAge.ADOLESCENT: 30,
                    CatAge.YOUNG_ADULT: 20,
                    CatAge.ADULT: 10,
                    CatAge.SENIOR_ADULT: 6,
                    CatAge.SENIOR: 3,
                }
            else:
                retire_chances = {
                    CatAge.NEWBORN: 0,
                    CatAge.KITTEN: 0,
                    CatAge.ADOLESCENT: 80,
                    CatAge.YOUNG_ADULT: 70,
                    CatAge.ADULT: 60,
                    CatAge.SENIOR_ADULT: 40,
                    CatAge.SENIOR: 10,
                }

            chance = int(retire_chances.get(cat.age))
            if not int(random() * chance):
                old_name = str(cat.name)
                cat.retire_cat()

                create_ceremony(
                    main_cat=cat, old_name=old_name, involved_cats={"m_c": cat}
                )


def _attempt_scarring(
    cat: Cat,
    condition: TemporaryCondition,
    possible_scars: list,
    guarantee_scar: bool = False,
) -> Optional[str]:
    """
    Attempts to give the cat a scar based on the condition
    :param cat: Cat receiving a scar
    :param condition: Condition giving a scar
    :param possible_scars: List of possible scars to give
    :param guarantee_scar: If true, scar will happen regardless of RNG. However, this cannot override other blockers, such as the cat's existing scar count.
    :return: Event text for the scar
    """
    if not possible_scars or len(cat.pelt.scars) >= 4:
        return None

    # scar chance increased by num of moons with the condition
    if guarantee_scar:
        chance = 1
    else:
        moons_with = (game.clan.age if game.clan else 0) - condition.moon_gained
        chance = max(5 - moons_with, 1)

    if not int(random() * chance):
        scar_pool = possible_scars
        scar_conflicts = get_config("cat_sprites.scar_conflicts")

        for scar, conflicts in scar_conflicts.items():
            if scar in cat.pelt.scars:
                scar_pool = [i for i in scar_pool if i not in conflicts]

        if not scar_pool:
            return None
    else:
        return None

    # If we've reached this point, we can move forward with giving history.
    cat.history.add_scar(
        i18n.t(
            "cat.history.scar_from_injury",
            injury_name=i18n.t(f"conditions.temporary_conditions.{condition.name}"),
        ),
        condition=condition.name,
    )

    # pick the scar
    scar = choice(scar_pool)

    # remove acc if need be
    if scar in ("NOTAIL", "HALFTAIL"):
        cat.pelt.accessory = tuple(
            acc
            for acc in cat.pelt.accessory
            if acc
            not in (
                "RED FEATHERS",
                "BLUE FEATHERS",
                "JAY FEATHERS",
                "GULL FEATHERS",
                "SPARROW FEATHERS",
                "CLOVER",
                "DAISY",
            )
        )

    # combining left/right variations into the both version
    if "NOLEFTEAR" in cat.pelt.scars and scar == "NORIGHTEAR":
        cat.pelt.scars = tuple(scar for scar in cat.pelt.scars if scar != "NOLEFTEAR")
        scar = "NOEAR"
    elif "NORIGHTEAR" in cat.pelt.scars and scar == "NOLEFTEAR":
        cat.pelt.scars = tuple(scar for scar in cat.pelt.scars if scar != "NORIGHTEAR")
        scar = "NOEAR"

    if "RIGHTBLIND" in cat.pelt.scars and scar == "LEFTBLIND":
        cat.pelt.scars = tuple(scar for scar in cat.pelt.scars if scar != "RIGHTBLIND")
        scar = "BOTHBLIND"
    elif "LEFTBLIND" in cat.pelt.scars and scar == "RIGHTBLIND":
        cat.pelt.scars = tuple(scar for scar in cat.pelt.scars if scar != "LEFTBLIND")
        scar = "BOTHBLIND"

    # give scar to cat
    cat.pelt.scars = (*cat.pelt.scars, scar)

    # find string
    scar_gain_strings = [
        "hardcoded.scar_event0",
        "hardcoded.scar_event1",
        "hardcoded.scar_event2",
    ]
    event = event_text_adjust(Cat, choice(scar_gain_strings), main_cat=cat)

    return i18n.t(
        event,
        condition=i18n.t(f"conditions.temporary_conditions.{condition.name}"),
    )
