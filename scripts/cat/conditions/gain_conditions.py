import itertools
from random import random, choice
from typing import Optional, Literal

import i18n

from scripts.cat.conditions.permanent_condition import PermanentCondition
from scripts.cat.conditions.temporary_condition import TemporaryCondition
from scripts.cat.constants import TEMPORARY_CONDITIONS, PERMANENT_CONDITIONS
from scripts.cat.enums import CatRank
from scripts.cat.pelts import Pelt
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.game_structure import game


def gain_temporary_condition(
    cat,
    name: str,
    omit_moonskip: bool = False,
    prevent_death: bool = False,
    severity: Optional[Literal["minor", "major", "severe"]] = None,
    scar_pool_override: Optional[list[str]] = None,
    allow_side_effects: bool = True,
):
    """
    Add a temporary condition
    :param cat: The cat gaining the condition
    :param name: The name of the condition
    :param omit_moonskip: If true, the next moonskip check will be skipped for this condition
    :param prevent_death: if true, the cat will not be able to die, even if this condition typically can
    :param severity: override the condition's typical severity with the given one
    :param scar_pool_override: override the condition's typical scar pool with the given list
    :param allow_side_effects: If true, the condition can apply additional conditions as side effects
    """
    if cat.dead:
        return
    # TODO: check if name is legit condition name
    if name in cat.temporary_conditions:
        return
    if name == "kittencough" and cat.status.rank not in (
        CatRank.KITTEN,
        CatRank.NEWBORN,
    ):
        return

    condition_info = TEMPORARY_CONDITIONS[name]

    new_condition = TemporaryCondition(
        name=name,
        severity=severity if severity else condition_info["severity"],
        duration=condition_info["duration"],
        mortality=condition_info["mortality"].get(cat.age, 0.0)
        if not prevent_death
        else 0.0,
        moon_gained=game.clan.age if game.clan else 0,
        infectiousness=condition_info["infectiousness"],
        immune_system_effect=condition_info["immune_system_effect"],
        progression=condition_info["progression"],
        risks=condition_info["risks"],
        current_complication=None,
        scar_pool_override=scar_pool_override,
        omit_moonskip=omit_moonskip,
    )

    cat.temporary_conditions.append(new_condition)

    if allow_side_effects and condition_info.get("side_effect"):
        _handle_condition_side_effect(cat, side_effects=condition_info["side_effect"])


def _handle_condition_side_effect(cat, side_effects: dict[str, float]):
    """
    Attempts to give side effect conditions to the cat.
    """
    for effect, chance in side_effects.items():
        avoided = False
        if random() < chance:
            # if this is blood loss, and we have meddies, then they'll try to stop the bleeding
            if effect == "blood_loss" and find_alive_cats_with_rank(
                cat, [CatRank.MEDICINE_CAT], working=True
            ):
                # find what herbs we need
                needed_herbs = itertools.chain.from_iterable(
                    TEMPORARY_CONDITIONS["blood_loss"]["treatment_strength"].values()
                )
                for herb in needed_herbs:
                    if herb in game.clan.herb_supply.entire_supply:
                        # we have an available herb, so we use it and move on to the next side effect
                        avoided = True
                        game.clan.herb_supply.remove_herb(herb, -1)
                        text = i18n.t("screens.med_den.blood_loss", name=cat.name)
                        game.herb_events_list.append(text)
                        break

            if avoided:
                continue

            gain_temporary_condition(cat, effect)


def gain_permanent_condition(
    cat,
    name: str,
    is_congenital: bool = False,
    set_moons_until=None,
    omit_moonskip: bool = False,
):
    """
    Add a permanent condition
    :param cat: The cat gaining the condition
    :param name: The name of the condition
    :param is_congenital: If true, condition will be marked as present at birth
    :param set_moons_until: Overrides the typical "moons_until" of a congenital condition
    :param omit_moonskip: If true, the next moonskip check will be skipped for this condition
    """
    if cat.dead:
        return
    if name not in PERMANENT_CONDITIONS:
        print(
            cat.name,
            f"WARNING: {name} is not in the permanent conditions collection.",
        )
        return

    condition = PERMANENT_CONDITIONS[name]

    if any([con in cat.permanent_conditions for con in condition["progression"]]):
        # if cat already has one of the progressions of the new condition, then we shouldn't give it to them
        print(
            f"INFO: {name} was not given to {str(cat.name)} as the cat already had one of the progressions of {name}."
        )
        return

    if is_congenital and not condition["can_be_congenital"]:
        print(
            f"WARNING: attempted to give {name} as a congenital condition, but {name} is not allowed to be set as congenital."
        )
        return
    if not is_congenital and not condition["can_be_acquired"]:
        is_congenital = True

    new_condition = PermanentCondition(
        name=name,
        severity=condition["severity"],
        is_congenital=is_congenital,
        removed_on_death=condition.get("removed_on_death", True),
        moons_until_discovery=set_moons_until
        if set_moons_until is not None
        else condition["moons_until_discovery"],
        moon_gained=game.clan.age if game.clan else 0,
        mortality=condition["mortality"].get(cat.age, 0.0),
        immune_system_effect=condition["immune_system_effect"],
        progression=condition["progression"],
        risks=condition["risks"],
        omit_moonskip=omit_moonskip,
        current_complication=None,
    )

    cat.permanent_conditions.append(new_condition)

    # APPEARANCE
    if name == "paralyzed":
        cat.pelt.paralyzed = True

    if condition.get("requires_scar"):
        new_scar = choice(condition["possible_scars"])
        cat.pelt.scars = (*cat.pelt.scars, new_scar)

    # remove accessories if need be
    if "NOTAIL" in cat.pelt.scars or "HALFTAIL" in cat.pelt.scars:
        cat.pelt.accessory = tuple(
            acc for acc in cat.pelt.accessory if acc not in Pelt.tail_accessories
        )


def add_congenital_condition(cat):
    """
    Adds a random congenital condition to the cat
    """
    possible_conditions = []

    for condition in PERMANENT_CONDITIONS:
        possible = PERMANENT_CONDITIONS[condition]
        if possible["is_congenital"]:
            possible_conditions.append(condition)

    new_condition = choice(possible_conditions)

    gain_permanent_condition(cat, new_condition, is_congenital=True)
