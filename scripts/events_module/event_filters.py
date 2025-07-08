import re
from random import choice

import ujson

from scripts.cat.enums import CatRank
from scripts.game_structure.game_essentials import game
from scripts.special_dates import get_special_date, contains_special_date_tag
from scripts.utility import (
    find_alive_cats_with_rank,
    filter_relationship_type,
)


def event_for_location(locations: list) -> bool:
    """
    checks if the clan is within the given locations
    """
    if "any" in locations:
        return True

    for place in locations:
        if ":" in place:
            info = place.split(":")
            req_biome = info[0]
            req_camps = info[1].split("_")
        else:
            req_biome = place
            req_camps = ["any"]

        if game.clan.override_biome:
            if req_biome == game.clan.override_biome:
                if "any" in req_camps or game.clan.camp_bg in req_camps:
                    return True
        elif req_biome == game.clan.biome.lower():
            if "any" in req_camps or game.clan.camp_bg in req_camps:
                return True
        return False


def event_for_season(seasons: list) -> bool:
    """
    checks if the clan is within the given seasons
    """
    if "any" in seasons or game.clan.current_season.lower() in seasons:
        return True

    return False


def event_for_tags(tags: list, cat, other_cat=None) -> bool:
    """
    checks if current tags disqualify the event
    """
    if not tags:
        return True

    # some events are mode specific
    mode = game.clan.game_mode
    possible_modes = ["classic", "expanded", "cruel_season"]
    for _poss in possible_modes:
        if _poss in tags and mode != _poss:
            return False

    # check leader life tags
    if hasattr(cat, "ID"):
        if cat.status.is_leader:
            leader_lives = game.clan.leader_lives

            life_lookup = {
                "some_lives": 4,
                "lives_remain": 2,
                "high_lives": 7,
                "mid_lives": 4,
                "low_lives": 1,
            }

            for _con, _val in life_lookup.items():
                if _con in tags and leader_lives < _val:
                    return False

        # check if main cat will allow for adoption
        if "adoption" in tags:
            if cat.no_kits:
                return False
            if cat.moons <= 14 + cat.age_moons["kitten"][1]:
                return False
            if any(cat.fetch_cat(i).no_kits for i in cat.mate):
                return False

        if other_cat and "romantic" in tags and not other_cat.is_potential_mate(cat):
            return False

    # check for required ranks within the clan
    for _tag in tags:
        rank_match = re.match(r"clan:(.+)", _tag)
        if not rank_match:
            continue
        ranks = [x for x in rank_match.group(1).split(",")]

        for rank in ranks:
            if rank == "apps":
                if not find_alive_cats_with_rank(
                    cat,
                    [
                        CatRank.APPRENTICE,
                        CatRank.MEDIATOR_APPRENTICE,
                        CatRank.MEDICINE_APPRENTICE,
                    ],
                ):
                    return False
                else:
                    continue

            if rank in [
                CatRank.LEADER,
                CatRank.DEPUTY,
            ] and not find_alive_cats_with_rank(cat, [rank]):
                return False

            if (
                rank not in [CatRank.LEADER, CatRank.DEPUTY]
                and not len(find_alive_cats_with_rank(cat, [rank])) >= 2
            ):
                return False

    special_date = get_special_date()
    # filtering for dates
    if contains_special_date_tag(tags):
        if not special_date or special_date.patrol_tag not in tags:
            return False

    return True


def event_for_reputation(required_rep: list) -> bool:
    """
    checks if the clan has reputation matching required_rep
    """
    if "any" in required_rep:
        return True

    clan_rep = game.clan.reputation

    if "hostile" in required_rep and 0 <= clan_rep <= 30:
        return True
    elif "neutral" in required_rep and 31 <= clan_rep <= 70:
        return True
    elif "welcoming" in required_rep and 71 <= clan_rep:
        return True

    return False


def event_for_clan_relations(required_rel: list, other_clan) -> bool:
    """
    checks if the clan has clan relations matching required_rel
    """
    if "any" in required_rel:
        return True

    current_rel = other_clan.relations

    if "hostile" in required_rel and 0 <= current_rel <= 6:
        return True
    elif "neutral" in required_rel and 7 <= current_rel <= 17:
        return True
    elif "ally" in required_rel and 18 <= current_rel:
        return True

    return False


def event_for_freshkill_supply(pile, trigger, factor, clan_size) -> bool:
    """
    checks if clan has the correct amount of freshkill for event
    """
    if game.clan.game_mode == "classic":
        return False

    needed_amount = pile.amount_food_needed()
    half_amount = needed_amount / 2
    clan_supply = pile.total_amount

    if "always" in trigger:
        return True
    if "low" in trigger and half_amount > clan_supply:
        return True
    if "adequate" in trigger and half_amount < clan_supply < needed_amount:
        return True

    # find how much is too much freshkill
    # it would probably be good to move this section of finding trigger_value to the freshkill class
    divider = 35 if game.clan.game_mode == "expanded" else 20
    factor = factor - round(pow((clan_size / divider), 2))
    if factor < 2 and game.clan.game_mode == "expanded":
        factor = 2

    trigger_value = round(factor * needed_amount, 2)

    if "full" in trigger and needed_amount < clan_supply < trigger_value:
        return True
    if "excess" in trigger and clan_supply > trigger_value:
        return True

    # if it hasn't returned by now, it doesn't qualify
    return False


def event_for_herb_supply(trigger, supply_type, clan_size) -> bool:
    """
    checks if clan's herb supply qualifies for event
    """
    if "always" in trigger:
        return True

    herb_supply = game.clan.herb_supply

    if not herb_supply.entire_supply and "empty" in trigger:
        return True

    if supply_type == "all_herb":
        if herb_supply.get_overall_rating() in trigger:
            return True
        return False

    if supply_type == "any_herb":
        for herb in herb_supply.entire_supply:
            if herb_supply.get_herb_rating(herb) in trigger:
                return True
        return False

    else:
        possible_herbs = herb_supply.base_herb_list
        chosen_herb = supply_type
        if chosen_herb not in possible_herbs.keys():
            print(f"WARNING: possible typo in supply constraint: {chosen_herb}")
            return False
        if herb_supply.get_herb_rating(chosen_herb) in trigger:
            return True
        return False


def event_for_cat(
    cat_info: dict, cat, cat_group: list = None, event_id: str = None, p_l=None
) -> bool:
    """
    checks if a cat is suitable for the event
    :param cat_info: cat's dict of constraints
    :param cat: the cat object of the cat being checked
    :param cat_group: the group of cats being included within the event
    :param event_id: if event comes with an id, include it here
    :param p_l: if event is a patrol, include patrol leader object here
    """

    func_lookup = {
        "age": _check_cat_age(cat, cat_info.get("age", [])),
        "status": _check_cat_status(cat, cat_info.get("status", [])),
        "trait": _check_cat_trait(
            cat, cat_info.get("trait", []), cat_info.get("not_trait", [])
        ),
        "skills": _check_cat_skills(
            cat, cat_info.get("skill", []), cat_info.get("not_skill", [])
        ),
        "backstory": _check_cat_backstory(cat, cat_info.get("backstory", [])),
        "gender": _check_cat_gender(cat, cat_info.get("gender", [])),
    }

    for func in func_lookup:
        if not func_lookup[func]:
            return False

    if cat_info.get("relationship_status", []):
        if not filter_relationship_type(
            group=cat_group,
            filter_types=cat_info["relationship_status"],
            event_id=event_id,
            patrol_leader=p_l,
        ):
            return False

    return True


def _check_cat_age(cat, ages: list) -> bool:
    """
    checks if a cat's age is within ages list
    """
    if "any" in ages or not ages:
        return True

    return cat.age.value in ages


def _check_cat_status(cat, statuses: list) -> bool:
    """
    checks if cat's status is within statuses list
    """
    if "any" in statuses or not statuses:
        return True

    if cat.status.rank in statuses:
        return True

    if "lost" in statuses and cat.status.is_lost():
        return True

    return False


def _check_cat_trait(cat, traits: list, not_traits: list) -> bool:
    """
    checks if cat has the correct traits for traits and not_traits lists
    """
    if not traits and not not_traits:
        return True

    cat_trait = cat.personality.trait
    allowed = False

    if traits and cat_trait not in traits:
        return False
    if not_traits and cat_trait in not_traits:
        return False
    return True


def _check_cat_skills(cat, skills: list, not_skills: list) -> bool:
    """
    checks if the cat has the correct skills for skills and not skills lists
    """
    if not skills and not not_skills:
        return True

    has_good_skill = False
    has_bad_skill = False

    for _skill in skills:
        skill_info = _skill.split(",")

        if len(skill_info) < 2:
            print("Cat skill incorrectly formatted", _skill)
            continue

        if cat.skills.meets_skill_requirement(skill_info[0], int(skill_info[1])):
            has_good_skill = True
            break

    for _skill in not_skills:
        skill_info = _skill.split(",")

        if len(skill_info) < 2:
            print("Cat skill incorrectly formatted", _skill)
            continue

        if cat.skills.meets_skill_requirement(skill_info[0], int(skill_info[1])):
            has_bad_skill = True
            break

    if has_good_skill and not has_bad_skill:
        return True

    return False


def _check_cat_backstory(cat, backstories: list) -> bool:
    """
    checks if cat has the correct backstory
    """
    if not backstories:
        return True

    if cat.backstory in backstories:
        return True

    return False


def _check_cat_gender(cat, genders: list) -> bool:
    """
    checks if cat has the correct gender
    """
    if not genders:
        return True

    if cat.gender in genders:
        return True

    return False


def cat_for_event(constraint_dict: dict, possible_cats: list, comparison_cat=None):
    """
    Checks the given cat list against constraint_dict to find any eligible cats.
    Returns a single cat ID chosen from eligible cats.
    :param constraint_dict: Can include age, status, skill, trait, and backstory lists
    :param possible_cats: List of possible cat objects
    :param comparison_cat: If you need to search for cats with a specific relationship status, then include a comparison
     cat. Keep in mind that this will search for a possible cat with the given relationship toward comparison cat.
    """
    # gather funcs to use
    func_dict = {
        "age": _get_cats_with_age,
        "status": _get_cats_with_status,
        "skill": _get_cats_without_skill,
        "not_skill": _get_cats_without_skill,
        "trait": _get_cats_with_trait,
        "not_trait": _get_cats_without_trait,
        "backstory": _get_cats_with_backstory,
    }

    # run funcs
    allowed_cats = []
    for param in func_dict:
        if param not in constraint_dict:
            continue
        allowed_cats = func_dict[param](
            possible_cats, tuple(constraint_dict.get(param))
        )

        # if the list is emptied, break
        if not allowed_cats:
            break

    # rel status check
    if comparison_cat and constraint_dict.get("relationship_status", []):
        for cat in allowed_cats.copy():
            if not filter_relationship_type(
                group=[cat, comparison_cat],
                filter_types=constraint_dict["relationship_status"],
            ):
                allowed_cats.remove(cat)

    if not allowed_cats:
        return None

    return choice(allowed_cats).ID


def _get_cats_with_age(cat_list: list, ages: tuple) -> list:
    """
    checks cat_list against required ages and returns qualifying cats
    """
    if not ages or "any" in ages:
        return cat_list

    return [kitty for kitty in cat_list if kitty.age in ages]


def _get_cats_with_status(cat_list: list, statuses: tuple) -> list:
    """
    checks cat_list against required statuses and returns qualifying cats
    """
    if not statuses or "any" in statuses:
        return cat_list

    return [kitty for kitty in cat_list if kitty.status in statuses]


def _get_cats_with_skill(cat_list: list, skills: tuple) -> list:
    """
    checks cat_list against required skills and returns qualifying cats
    """
    if not skills:
        return cat_list

    for kitty in cat_list.copy():
        has_skill = False
        for _skill in skills:
            split_skill = _skill.split(",")

            if len(split_skill) < 2:
                print("Cat skill incorrectly formatted", _skill)
                continue

            if kitty.skills.meets_skill_requirement(
                split_skill[0], int(split_skill[1])
            ):
                has_skill = True

        if not has_skill:
            cat_list.remove(kitty)

    return cat_list


def _get_cats_without_skill(cat_list: list, skills: tuple) -> list:
    """
    checks cat_list against disallowed skills and returns qualifying cats
    """
    if not skills:
        return cat_list

    for kitty in cat_list.copy():
        for _skill in skills:
            split_skill = _skill.split(",")

            if len(split_skill) < 2:
                print("Cat skill incorrectly formatted", _skill)
                continue

            if kitty.skills.meets_skill_requirement(
                split_skill[0], int(split_skill[1])
            ):
                cat_list.remove(kitty)
                break

    return cat_list


def _get_cats_with_trait(cat_list: list, traits: tuple) -> list:
    """
    checks cat_list against required traits and returns qualifying cats
    """
    if not traits:
        return cat_list

    return [kitty for kitty in cat_list if kitty.trait in traits]


def _get_cats_without_trait(cat_list: list, traits: tuple) -> list:
    """
    checks cat_list against disallowed traits and returns qualifying cats
    """
    if not traits:
        return cat_list

    return [kitty for kitty in cat_list if kitty.trait not in traits]


def _get_cats_with_backstory(cat_list: list, backstories: tuple) -> list:
    """
    checks cat_list against required backstories and returns qualifying cats
    """
    if not backstories:
        return cat_list

    return [kitty for kitty in cat_list if kitty.backstory in backstories]
