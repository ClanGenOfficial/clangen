import re
from itertools import combinations
from random import choice, randint
from typing import List, Optional

from scripts.cat.constants import BACKSTORIES
from scripts.cat_relations.enums import RelType, rel_type_tiers, RelTier
from scripts.cat.enums import CatRank, CatAge, CatCompatibility
from scripts.special_dates import get_special_date, contains_special_date_tag
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.game_structure import game


def get_frequency() -> int:
    """
    Chooses an event frequency and returns it as an int. This is used by short and patrol events to determine what frequency of event to pull.
    """
    # think of it as "in a span of 10 moons, in how many moons should this sort of event appear?"
    frequency_roll = randint(1, 10)
    if frequency_roll <= 4:
        return 4
    elif frequency_roll <= 7:
        return 3
    elif frequency_roll <= 9:
        return 2
    else:
        return 1


def find_new_frequency(used_frequencies: set) -> int:
    """
    Finds and returns the next most common unused frequency.
    """
    possible_frequencies = (1, 2, 3, 4)
    sorted_f = sorted(list(used_frequencies), reverse=True)

    new_freq = sorted_f[0] + 1
    if new_freq in possible_frequencies and new_freq not in used_frequencies:
        return new_freq

    new_freq = sorted_f[-1] - 1
    if new_freq in possible_frequencies and new_freq not in used_frequencies:
        return new_freq

    else:
        return 4


def event_for_location(locations: list) -> bool:
    """
    Checks if the clan is within the allowed locations.
    """
    if "any" in locations:
        return True
    if not game.clan:
        return False

    is_exclusionary = _check_for_exclusionary_value(locations)

    for place in locations:
        if is_exclusionary:
            place = place.replace("-", "")

        # split to find req biomes and req camps
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
                    return not is_exclusionary

        elif req_biome == game.clan.biome.lower():
            if "any" in req_camps or game.clan.camp_bg in req_camps:
                return not is_exclusionary

    return is_exclusionary


def event_for_season(seasons: list) -> bool:
    """
    Checks if the clan is within the given seasons.
    """
    if not seasons:
        return True

    if "any" in seasons:
        # "any" will never be exclusionary, so we check for it first
        return True

    is_exclusionary = _check_for_exclusionary_value(seasons)
    if is_exclusionary:
        seasons = [x.replace("-", "") for x in seasons]

    if game.clan.current_season.lower() in seasons:
        return not is_exclusionary

    return is_exclusionary


def event_for_tags(
    tags: list, cat, other_cat=None, mentor_tags_fulfilled: dict = None
) -> bool:
    """
    Checks if current tags disqualify the event.
    :param tags: Tags to check validity for.
    :param cat: Main cat to compare against tags.
    :param other_cat: Secondary cat to compare against tags.
    :param mentor_tags_fulfilled: Dict of mentor values used to validate mentor tags. Only utilized by patrols.
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
                "some_lives": (4, 9),
                "lives_remain": (2, 9),
                "high_lives": (7, 9),
                "mid_lives": (4, 6),
                "low_lives": (1, 3),
            }

            for _con, _val in life_lookup.items():
                if _con in tags and not (_val[0] <= leader_lives <= _val[1]):
                    return False

        # check if main cat will allow for adoption
        if "adoption" in tags:
            if cat.no_kits:
                return False
            if cat.moons <= 14 + cat.age_moons["kitten"][1]:
                return False
            if any(cat.fetch_cat(i).no_kits for i in cat.mate):
                return False

        if (
            other_cat
            and RelType.ROMANCE in tags
            and not other_cat.is_potential_mate(cat)
        ):
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

    if "all_mentored" in tags:
        return mentor_tags_fulfilled.get("general", False)
    for _tag in tags:
        if re.match(r"app[1-6]_mentored", _tag) and not mentor_tags_fulfilled.get(
            _tag, False
        ):
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

    if herb_supply.total <= 0 and "empty" in trigger:
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
    cat_info: dict,
    cat,
    cat_group: list = None,
    event_id: str = None,
    p_l=None,
    injuries: list = None,
) -> bool:
    """
    checks if a cat is suitable for the event
    :param cat_info: cat's dict of constraints
    :param cat: the cat object of the cat being checked
    :param cat_group: the group of cats being included within the event
    :param event_id: if event comes with an id, include it here
    :param p_l: if event is a patrol, include patrol leader object here
    :param injuries: list of injuries that the event may give this cat
    """

    func_lookup = {
        "age": _check_cat_age,
        "status": _check_cat_status,
        "trait": _check_cat_trait,
        "skill": _check_cat_skills,
        "backstory": _check_cat_backstory,
        "gender": _check_cat_gender,
    }

    for param, func in func_lookup.items():
        if param in cat_info and not func(cat, cat_info[param]):
            return False

    # checking injuries
    if injuries:
        if "mangled tail" in injuries and (
            "NOTAIL" in cat.pelt.scars or "HALFTAIL" in cat.pelt.scars
        ):
            return False
        if "torn ear" in injuries and "NOEAR" in cat.pelt.scars:
            return False

    # checking relationships
    if cat_info.get("relationship_status", []):
        for status in cat_info.get("relationship_status", []):
            # just some preliminary checks to see if any of these are impossible for this cat
            if status == "siblings" and not cat.get_siblings():
                return False
            elif status == "mates" and not cat.mate:
                return False
            elif status == "mates_with_pl" and p_l.ID not in cat.mate:
                return False
            elif status == "parent/child" and not cat.get_children():
                return False
            elif status == "child/parent" and not cat.get_parents():
                return False
            elif status == "mentor/app" and not cat.apprentice:
                return False
            elif status == "app/mentor" and not cat.mentor:
                return False

        if cat_group and not filter_relationship_type(
            group=cat_group,
            filter_types=cat_info["relationship_status"],
            event_id=event_id,
            patrol_leader=p_l,
        ):
            return False

    return True


def _check_cat_age(cat, ages: list) -> bool:
    """
    Checks if a cat's age is within ages list.
    """
    # we only allow newborns if they are explicitly stated
    if cat.age == CatAge.NEWBORN and (not ages or CatAge.NEWBORN not in ages):
        return False

    if not ages or "any" in ages:
        return True

    is_exclusionary = _check_for_exclusionary_value(ages)

    if is_exclusionary:
        ages = [x.replace("-", "") for x in ages]

    if cat.age.value in ages:
        return not is_exclusionary

    return is_exclusionary


def _check_cat_status(cat, statuses: list) -> bool:
    """
    Checks if cat's status is within statuses list.
    """
    if not statuses or "any" in statuses:
        return True

    if (cat.status.rank in statuses) or ("lost" in statuses and cat.status.is_lost()):
        return True

    is_exclusionary = _check_for_exclusionary_value(statuses)

    if is_exclusionary:
        statuses = [x.replace("-", "") for x in statuses]

    if (cat.status.rank in statuses) or ("lost" in statuses and cat.status.is_lost()):
        return False

    return is_exclusionary


def _check_cat_trait(cat, traits: list) -> bool:
    """
    Checks if cat has required trait.
    """
    if not traits or "any" in traits:
        return True

    is_exclusionary = _check_for_exclusionary_value(traits)

    if is_exclusionary:
        traits = [x.replace("-", "") for x in traits]

    if cat.personality.trait in traits:
        return not is_exclusionary

    return is_exclusionary


def _check_cat_skills(cat, skills: list) -> bool:
    """
    Checks if the cat has all required skills.
    """
    if not skills or "any" in skills:
        return True

    is_exclusionary = _check_for_exclusionary_value(skills)
    if is_exclusionary:
        skills = [x.replace("-", "") for x in skills]

    for _skill in skills:
        skill_info = _skill.split(",")

        if len(skill_info) < 2:
            print("Cat skill incorrectly formatted", _skill)
            continue

        if cat.skills.meets_skill_requirement(skill_info[0], int(skill_info[1])):
            return not is_exclusionary

    return is_exclusionary


def _check_cat_backstory(cat, backstories: list) -> bool:
    """
    Checks if cat has the correct backstory.
    """
    if not backstories:
        return True

    is_exclusionary = _check_for_exclusionary_value(backstories)

    if is_exclusionary:
        backstories = [x.replace("-", "") for x in backstories]

    # do the real simple test first
    if cat.backstory in backstories:
        return False if is_exclusionary else True

    # now we look for backstory categories
    allowed_stories = []
    for story in backstories:
        if story in BACKSTORIES["backstory_categories"].keys():
            allowed_stories.extend(BACKSTORIES["backstory_categories"][story])
        else:
            allowed_stories.append(story)

    if cat.backstory in allowed_stories:
        return not is_exclusionary

    return is_exclusionary


def _check_cat_gender(cat, genders: list) -> bool:
    """
    Checks if cat has the correct gender.
    """
    if not genders:
        return True

    if cat.gender in genders:
        return True

    return False


def cat_for_event(
    constraint_dict: dict,
    possible_cats: list,
    comparison_cat=None,
    comparison_cat_rel_status: list = None,
    injuries: list = None,
    return_id: bool = True,
):
    """
    Checks the given cat list against constraint_dict to find any eligible cats.
    Returns a single cat ID chosen from eligible cats.
    :param constraint_dict: Can include age, status, skill, not_skill, trait, not_trait, relationship_status, and backstory lists
    :param possible_cats: List of possible cat objects
    :param comparison_cat: If you need to search for cats with a specific relationship status, then include a comparison
     cat. Keep in mind that this will search for a possible cat with the given relationship toward comparison cat.
    :param comparison_cat_rel_status: The relationship_status dict for the comparison cat
    :param injuries: List of injuries a cat may get from the event
    :param return_id: If true, return cat ID instead of object
    """
    # gather funcs to use
    func_dict = {
        "age": _get_cats_with_age,
        "status": _get_cats_with_status,
        "skill": _get_cats_with_skill,
        "trait": _get_cats_with_trait,
        "backstory": _get_cats_with_backstory,
    }

    # run funcs
    allowed_cats = possible_cats
    for param in func_dict:
        if param not in constraint_dict:
            continue
        allowed_cats = func_dict[param](allowed_cats, tuple(constraint_dict.get(param)))

        # if the list is emptied, return
        if not allowed_cats:
            return None

    # find cats that can get the injuries that will be given
    if injuries:
        for cat in allowed_cats.copy():
            if "mangled tail" in injuries and (
                "NOTAIL" in cat.pelt.scars or "HALFTAIL" in cat.pelt.scars
            ):
                allowed_cats.remove(cat)
            if "torn ear" in injuries and "NOEAR" in cat.pelt.scars:
                allowed_cats.remove(cat)

        # if the list is emptied, return
        if not allowed_cats:
            return None

    # rel status check
    if comparison_cat_rel_status or constraint_dict.get("relationship_status"):
        # preliminary check to see if we can just skip to gathering certain rel groups
        allowed_cats, comparison_cat_rel_status = _get_cats_with_rel_status(
            allowed_cats, comparison_cat, comparison_cat_rel_status
        )

        for cat in allowed_cats.copy():
            # checking comparison cat's rel values toward cat
            if comparison_cat_rel_status:
                if not filter_relationship_type(
                    group=[comparison_cat, cat], filter_types=comparison_cat_rel_status
                ):
                    allowed_cats.remove(cat)
                    continue

            # now we can check cat's rel toward comparison_cat
            if constraint_dict.get("relationship_status"):
                if not filter_relationship_type(
                    group=[cat, comparison_cat],
                    filter_types=constraint_dict["relationship_status"],
                ):
                    allowed_cats.remove(cat)

    if not allowed_cats:
        return None

    cat = choice(allowed_cats)

    if return_id:
        return cat.ID
    else:
        return cat


def _get_cats_with_rel_status(
    cat_list: list, cat, rel_status_list: list
) -> tuple[list, list]:
    is_exclusionary = _check_for_exclusionary_value(rel_status_list)
    rel_status_list = [x.replace("-", " ") for x in rel_status_list]

    if "siblings" in rel_status_list:
        if is_exclusionary:
            cat_list = [c for c in cat_list if c.ID not in cat.get_siblings()]
        else:
            cat_list = [c for c in cat_list if c.ID in cat.get_siblings()]
        rel_status_list.remove("siblings")
    if "mates" in rel_status_list:
        if is_exclusionary:
            cat_list = [c for c in cat_list if c.ID not in cat.mate]
        else:
            cat_list = [c for c in cat_list if c.ID in cat.mate]
        rel_status_list.remove("mates")
    if "parent/child" in rel_status_list:
        if is_exclusionary:
            cat_list = [c for c in cat_list if c.ID not in cat.get_children()]
        else:
            cat_list = [c for c in cat_list if c.ID in cat.get_children()]
        rel_status_list.remove("parent/child")
    if "child/parent" in rel_status_list:
        if is_exclusionary:
            cat_list = [c for c in cat_list if c.ID not in cat.get_parents()]
        else:
            cat_list = [c for c in cat_list if c.ID in cat.get_parents()]
        rel_status_list.remove("child/parent")
    if "mentor/app" in rel_status_list:
        if is_exclusionary:
            cat_list = [c for c in cat_list if c.ID not in cat.apprentice]
        else:
            cat_list = [c for c in cat_list if c.ID in cat.apprentice]
        rel_status_list.remove("mentor/app")
    if "app/mentor" in rel_status_list:
        if is_exclusionary:
            cat_list = [c for c in cat_list if c.ID != cat.mentor]
        else:
            cat_list = [c for c in cat_list if c.ID == cat.mentor]
        rel_status_list.remove("app/mentor")

    if is_exclusionary:
        # putting indicators back for later filter funcs
        rel_status_list = [f"-{x}" for x in rel_status_list]

    return cat_list, rel_status_list


def _get_cats_with_age(cat_list: list, ages: tuple) -> list:
    """
    Checks cat_list against required ages and returns qualifying cats.
    """
    if not ages or "any" in ages:
        return cat_list

    is_exclusionary = _check_for_exclusionary_value(ages)

    if is_exclusionary:
        ages = [x.replace("-", "") for x in ages]
        return [kitty for kitty in cat_list if kitty.age not in ages]
    else:
        return [kitty for kitty in cat_list if kitty.age in ages]


def _get_cats_with_status(cat_list: list, statuses: tuple) -> list:
    """
    Checks cat_list against required statuses and returns qualifying cats.
    """
    if not statuses or "any" in statuses:
        return cat_list

    is_exclusionary = _check_for_exclusionary_value(statuses)

    if is_exclusionary:
        statuses = [x.replace("-", "") for x in statuses]
        return [kitty for kitty in cat_list if kitty.age not in statuses]
    else:
        return [kitty for kitty in cat_list if kitty.age in statuses]


def _get_cats_with_skill(cat_list: list, skills: tuple) -> list:
    """
    Checks cat_list against required skills and returns qualifying cats.
    """
    if not skills:
        return cat_list

    is_exclusionary = _check_for_exclusionary_value(skills)
    if is_exclusionary:
        skills = [x.replace("-", "") for x in skills]

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

        if has_skill and is_exclusionary:
            cat_list.remove(kitty)

        if not has_skill and not is_exclusionary:
            cat_list.remove(kitty)

    return cat_list


def _get_cats_with_trait(cat_list: list, traits: tuple) -> list:
    """
    Checks cat_list against required traits and returns qualifying cats.
    """
    if not traits:
        return cat_list

    is_exclusionary = _check_for_exclusionary_value(traits)

    if is_exclusionary:
        traits = [x.replace("-", "") for x in traits]
        return [kitty for kitty in cat_list if kitty.personality.trait not in traits]
    else:
        return [kitty for kitty in cat_list if kitty.personality.trait in traits]


def _get_cats_with_backstory(cat_list: list, backstories: tuple) -> list:
    """
    Checks cat_list against required backstories and returns qualifying cats.
    """
    if not backstories:
        return cat_list

    # now we look for backstory categories
    allowed_stories = []
    for story in backstories:
        if story in BACKSTORIES["backstory_categories"].keys():
            allowed_stories.extend(BACKSTORIES["backstory_categories"][story])
        else:
            allowed_stories.append(story)

    is_exclusionary = _check_for_exclusionary_value(backstories)

    if is_exclusionary:
        backstories = [x.replace("-", "") for x in backstories]
        return [kitty for kitty in cat_list if kitty.backstory not in allowed_stories]
    else:
        return [kitty for kitty in cat_list if kitty.backstory in allowed_stories]


def _check_for_exclusionary_value(possible_values) -> bool:
    """
    Checks the given list for an exclusionary value and returns True or False
    """
    return any(value.find("-") == 0 for value in possible_values)


def filter_relationship_type(
    group: list, filter_types: List[str], event_id: str = None, patrol_leader=None
):
    """
    filters for specific types of relationships between groups of cat objects, returns bool
    :param group: the group of cats to be tested (make sure they're in the correct order (i.e. if testing for
    parent/child, the cat being tested as parent must be index 0)
    :param filter_types: the relationship types to check for.
    :param event_id: if the event has an ID, include it here
    :param patrol_leader: if you are testing a patrol, ensure you include the self.patrol_leader here
    """
    if not filter_types:
        return True

    filter_list = filter_types.copy()

    is_exclusionary = _check_for_exclusionary_value(filter_list)
    if is_exclusionary:
        filter_list = [x.replace("-", "") for x in filter_list]

    if patrol_leader:
        if patrol_leader in group:
            group.remove(patrol_leader)
        group.insert(0, patrol_leader)

    test_cat = group[0]
    testing_cats = [cat for cat in group if cat.ID != test_cat.ID]

    qualifies = False

    if "strangers" in filter_types:
        if not all(
            [inter_cat.ID in test_cat.relationships for inter_cat in testing_cats]
        ):
            if is_exclusionary:
                qualifies = True
            else:
                return False
        if is_exclusionary and not qualifies:
            return False
        filter_list.remove("strangers")

    if "siblings" in filter_types:
        if not all([test_cat.is_sibling(inter_cat) for inter_cat in testing_cats]):
            if is_exclusionary:
                qualifies = True
            else:
                return False
        if is_exclusionary and not qualifies:
            return False
        filter_list.remove("siblings")

    if "littermates" in filter_types:
        if not all([test_cat.is_littermate(inter_cat) for inter_cat in testing_cats]):
            if is_exclusionary:
                qualifies = True
            else:
                return False
        if is_exclusionary and not qualifies:
            return False
        filter_list.remove("littermates")

    if "mates" in filter_list:
        # first test if more than one cat
        if len(group) == 1:
            return False

        # then if cats don't have the needed number of mates
        if not all(len(i.mate) >= (len(group) - 1) for i in group):
            if is_exclusionary:
                qualifies = True
            else:
                return False
        else:
            # Now the expensive test.  We have to see if everyone is mates with each other
            # Hopefully the cheaper tests mean this is only needed on events with a small number of cats
            for x in combinations(group, 2):
                if x[0].ID not in x[1].mate:
                    if is_exclusionary:
                        qualifies = True
                    else:
                        return False
                if is_exclusionary and not qualifies:
                    return False
        filter_list.remove("mates")

    # check if all cats are mates with p_l (they do not have to be mates with each other)
    if "mates_with_pl" in filter_list:
        # First test if there is more than one cat
        if len(group) == 1:
            return False

        # Check each cat to see if it is mates with the patrol leader
        for cat in group:
            if cat.ID == patrol_leader.ID:
                continue
            if cat.ID not in patrol_leader.mate:
                if is_exclusionary:
                    qualifies = True
                else:
                    return False
            if is_exclusionary and not qualifies:
                return False
        filter_list.remove("mates_with_pl")

    # Check if the cats are in a parent/child relationship
    if "parent/child" in filter_list:
        # It should be exactly two cats for a "parent/child" event
        if len(group) != 2:
            return False
        # test for parentage
        if not group[0].is_parent(group[1]):
            if is_exclusionary:
                qualifies = True
            else:
                return False
        if is_exclusionary and not qualifies:
            return False
        filter_list.remove("parent/child")

    if "child/parent" in filter_list:
        # It should be exactly two cats for a "child/parent" event
        if len(group) != 2:
            return False
        # test for parentage
        if not group[1].is_parent(group[0]):
            if is_exclusionary:
                qualifies = True
            else:
                return False
        if is_exclusionary and not qualifies:
            return False
        filter_list.remove("child/parent")

    if "mentor/app" in filter_list:
        # It should be exactly two cats for a "mentor/app" event
        if len(group) != 2:
            return False
        # test for parentage
        if not group[1].ID in group[0].apprentice:
            if is_exclusionary:
                qualifies = True
            else:
                return False
        if is_exclusionary and not qualifies:
            return False
        filter_list.remove("mentor/app")

    if "app/mentor" in filter_list:
        # It should be exactly two cats for an "app/mentor" event
        if len(group) != 2:
            return False
        # test for parentage
        if not group[0].ID in group[1].apprentice:
            if is_exclusionary:
                qualifies = True
            else:
                return False
        if is_exclusionary and not qualifies:
            return False
        filter_list.remove("app/mentor")

    # return early if there's nothing left to check
    if not filter_list and is_exclusionary:
        return qualifies

    # Filtering relationship values
    # these don't get exclusionary values because it's giving me a headache
    # each cat has to have relationships toward each other matching every level tag
    for tier in filter_list:
        for inter_cat in group:
            if len(group) == 2 and inter_cat == group[1]:
                # if this is a two cat group, then we only look for the first cat's rel toward the second cat.
                # groups > 2 will require that all cats feel the same way toward each other.
                continue
            group_ids = [cat.ID for cat in group]

            relevant_relationships = [
                rel
                for rel in inter_cat.relationships.values()
                if rel.cat_to.ID in group_ids and rel.cat_to.ID != inter_cat.ID
            ]

            # list of every cat's tier list
            group_lists: list[RelTier] = [
                rel.get_reltype_tiers() for rel in relevant_relationships
            ]

            # now test each list to see if the required tag is inside
            for tier_list in group_lists:
                # just a quick check to see if we can avoid all the extra hullabaloo
                if tier in tier_list:
                    continue

                # if it's limited to *just* the given tier
                if "_only" in tier:
                    tier.replace("_only", "")
                    if tier not in tier_list:
                        return False
                # otherwise we allow both the given tier and any greater tiers
                else:
                    # finding the matching tier enum
                    rel_tier: RelTier = RelTier(tier)

                    # find the matching rel_type enum
                    rel_type: Optional[RelType] = None
                    for rel_type in rel_type_tiers:
                        if rel_tier in rel_type_tiers[rel_type]:
                            rel_type = rel_type
                            break
                    if not rel_type:
                        continue

                    # get the tier's index within the rel_types's list
                    index = rel_type_tiers[rel_type].index(rel_tier)
                    allowed_tiers = []
                    # if it's a pos tier, we allow that index and higher
                    if rel_tier.is_any_pos:
                        allowed_tiers = rel_type_tiers[rel_type][index:]
                    # if it's a neg tier, we allow that index and lower
                    elif rel_tier.is_any_neg:
                        allowed_tiers = rel_type_tiers[rel_type][0 : index + 1]

                    discard = True
                    for _t in tier_list:
                        if _t in allowed_tiers:
                            discard = False
                            break
                    if discard:
                        return False

    if is_exclusionary:
        if qualifies:
            return True
        else:
            return False

    return True


def get_highest_romantic_relation(
    relationships, exclude_mate=False, potential_mate=False
):
    """Returns the relationship with the highest romantic value."""
    max_love_value = 0
    current_max_relationship = None
    for rel in relationships:
        if rel.romance < 0:
            continue
        if exclude_mate and rel.cat_from.ID in rel.cat_to.mate:
            continue
        if potential_mate and not rel.cat_to.is_potential_mate(
            rel.cat_from, for_love_interest=True
        ):
            continue
        if rel.romance > max_love_value:
            current_max_relationship = rel
            max_love_value = rel.romance

    return current_max_relationship


def check_relationship_value(cat_from, cat_to, rel_value=None):
    """
    returns the value of the rel_value param given
    :param cat_from: the cat who is having the feelings
    :param cat_to: the cat that the feelings are directed towards
    :param rel_value: the relationship value that you're looking for,
    options are: romance, like, respect, comfort, trust
    """
    if cat_to.ID in cat_from.relationships:
        relationship = cat_from.relationships[cat_to.ID]
    else:
        relationship = cat_from.create_one_relationship(cat_to)

    if rel_value == RelType.ROMANCE:
        return relationship.romance
    elif rel_value == RelType.LIKE:
        return relationship.like
    elif rel_value == RelType.RESPECT:
        return relationship.respect
    elif rel_value == RelType.COMFORT:
        return relationship.comfort
    elif rel_value == RelType.TRUST:
        return relationship.trust

    return None


def get_personality_compatibility(cat1, cat2):
    """
    Returns matching CatCompatibility enum according to personalitiesof given cat objects.
    :param cat1: Cat object of first cat
    :param cat2: Cat object of second cat
    """
    personality1 = cat1.personality.trait
    personality2 = cat2.personality.trait

    if personality1 == personality2:
        if personality1 is None:
            return CatCompatibility.NEUTRAL
        return CatCompatibility.POSITIVE

    lawfulness_diff = abs(cat1.personality.lawfulness - cat2.personality.lawfulness)
    sociability_diff = abs(cat1.personality.sociability - cat2.personality.sociability)
    aggression_diff = abs(cat1.personality.aggression - cat2.personality.aggression)
    stability_diff = abs(cat1.personality.stability - cat2.personality.stability)
    list_of_differences = [
        lawfulness_diff,
        sociability_diff,
        aggression_diff,
        stability_diff,
    ]

    running_total = 0
    for x in list_of_differences:
        if x <= 4:
            running_total += 1
        elif x >= 6:
            running_total -= 1

    if running_total >= 2:
        return CatCompatibility.POSITIVE
    if running_total <= -2:
        return CatCompatibility.NEGATIVE

    return CatCompatibility.NEUTRAL
