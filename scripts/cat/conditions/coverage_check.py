from scripts.cat.enums import CatRank

from scripts.cat.skills import SkillPath
from scripts.config import get_config
from scripts.game_structure import game


def amount_of_clan_covered_total(all_cats) -> int:
    """
    number of clan members the meds in total can treat
    """

    medicine_cats = [
        i
        for i in all_cats
        if i.status.alive_in_player_clan
        and i.can_work()
        and i.status.rank.is_any_medicine_rank()
    ]
    full_med = [i for i in medicine_cats if i.status.rank == CatRank.MEDICINE_CAT]
    apprentices = [
        i for i in medicine_cats if i.status.rank == CatRank.MEDICINE_APPRENTICE
    ]

    total_exp = 0
    for cat in medicine_cats:
        total_exp += cat.experience
    total_exp = total_exp * 0.003

    # Determine the total med number. Med cats with certain skill counts
    # as "more" of a med cat.  Only full medicine cat can have their skills have effect
    total_med_number = len(apprentices) / 2
    for cat in full_med:
        if cat.skills.meets_skill_requirement(SkillPath.HEALER, 3):
            total_med_number += 2
        elif cat.skills.meets_skill_requirement(SkillPath.HEALER, 2):
            total_med_number += 1.75
        elif cat.skills.meets_skill_requirement(SkillPath.HEALER, 1):
            total_med_number += 1.5
        else:
            total_med_number += 1

    adjust_med_number = total_med_number + total_exp

    return int(
        adjust_med_number * (get_amount_cat_for_one_medic(game.clan) + 1)
    )  # number of cats they can care for


def medicine_cats_can_cover_clan(all_cats) -> bool:
    """
    whether the player has enough meds for the whole clan
    """
    relevant_cats = [c for c in all_cats if c.status.alive_in_player_clan]
    return amount_of_clan_covered_total(all_cats) >= len(relevant_cats)


def get_amount_cat_for_one_medic(clan):
    """
    Returns the amount of cats a single medicine cat can treat
    """
    amount = get_config("condition_related.medcats.medcat_base_capacity")
    if clan and clan.game_mode == "classic":
        # just hope nobody has clans with more than 1,000,000 cats in classic
        amount = 1000000
    return amount
