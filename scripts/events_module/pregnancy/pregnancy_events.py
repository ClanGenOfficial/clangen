from random import random

from scripts.cat.cats import Cat
from scripts.clan_package.settings import get_clan_setting
from scripts.events_module.pregnancy.check_parents import (
    check_if_can_have_kits,
    get_second_parent,
    check_second_parent,
)
from scripts.events_module.pregnancy.create_kits import (
    handle_adoption,
    get_balanced_kit_chance,
)
from scripts.events_module.pregnancy.handle_already_pregnant import (
    handle_one_moon_pregnant,
    handle_two_moon_pregnant,
)
from scripts.events_module.pregnancy.handle_become_pregnant import (
    handle_zero_moon_pregnant,
)
from scripts.game_structure import game


def increment_pregnancy_age():
    """Increase the moon for each pregnancy in the pregnancy dictionary"""
    for pregnancy_key in game.clan.pregnancy_data.keys():
        game.clan.pregnancy_data[pregnancy_key]["moons"] += 1


def handle_having_kits(cat: Cat):
    """
    Handles existing pregnancies and creates new pregnancies. If cats cannot get pregnant, this might have them adopt or
     bring back 'secret' kittens.
    """
    if not game.clan:
        return

    # Handles if a cat is already pregnant
    if cat.ID in game.clan.pregnancy_data:
        moons = game.clan.pregnancy_data[cat.ID]["moons"]
        if moons == 1:
            handle_one_moon_pregnant(cat)
            return
        if moons >= 2:
            handle_two_moon_pregnant(cat)
            return

    if not cat.status.alive_in_player_clan or cat.not_working():
        return

    # Handle birth cooldown outside the check_if_can_have_kits function, so it only happens once
    # for each cat.
    if cat.birth_cooldown:
        cat.birth_cooldown -= 1

    # Check if they can have kits.
    if not check_if_can_have_kits(cat):
        return

    # DETERMINE THE SECOND PARENT
    # check if there is a cat in the clan for the second parent
    second_parent, is_affair = get_second_parent(cat)

    if not second_parent and not get_clan_setting("single parentage"):
        return

    # check if the second_parent is not none and if they also can have kits
    can_have_kits, kits_are_adopted = check_second_parent(cat, second_parent)
    if second_parent and not can_have_kits:
        return

    chance = get_balanced_kit_chance(cat, second_parent, is_affair)

    if not int(random() * chance):
        # If you've reached here - congrats, kits!
        if kits_are_adopted:
            handle_adoption(cat, second_parent)
        else:
            handle_zero_moon_pregnant(cat, second_parent)
