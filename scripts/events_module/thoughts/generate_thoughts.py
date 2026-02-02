import traceback
from random import choice, getrandbits
from typing import TYPE_CHECKING, Optional

import i18n

from scripts.cat.enums import CatGroup
from scripts.events_module.event_filters import event_for_cat
from scripts.game_structure.localization import load_lang_resource
from scripts.events_module.event_filters import filter_relationship_type

if TYPE_CHECKING:
    from scripts.cat.cats import Cat

random_cat_constraints = [
    "random_backstory_constraint",
    "random_status_constraint",
    "random_age_constraint",
    "random_trait_constraint",
    "random_skill_constraint",
    "random_living_status",
    "random_outside_status",
]


def get_other_cat_for_thought(
    cat_list: list["Cat"], main_cat: "Cat"
) -> Optional["Cat"]:
    """
    Returns a cat object selected from the given cat_list. This will be a cat acceptable as the subject of main_cat's thought.
    """
    if main_cat in cat_list:
        cat_list.remove(main_cat)

    if not cat_list:
        return None

    other_cat = choice(cat_list)

    # sometimes cats can think about a dead cat
    thinking_of_dead_cat = getrandbits(4) == 1

    # dead cats think of anyone
    if main_cat.status.group.is_afterlife():
        return other_cat

    else:
        # count and give up if we don't find a suitable cat within 100 checks
        i = 0
        while cat_list and (
            (other_cat.dead and not thinking_of_dead_cat)
            or other_cat.ID not in main_cat.relationships
        ):
            cat_list.remove(other_cat)

            i += 1
            if i > 100 or not cat_list:
                other_cat = None
                break

            other_cat = choice(cat_list)

    return other_cat


def _filter_list(
    inter_list: list, main_cat: "Cat", other_cat: "Cat", biome, season, camp
) -> list:
    """
    Filters thoughts in the inter_list per their constraints and returns a list of allowed thoughts.
    """
    created_list = []
    for inter in inter_list:
        if _constraints_fulfilled(main_cat, other_cat, inter, biome, season, camp):
            created_list.append(inter)
    return created_list


def _load_group(main_cat: "Cat", other_cat: "Cat", biome, season, camp):
    """
    Loads and returns thoughts appropriate for the given args.
    """
    rank = main_cat.status.rank
    rank = rank.replace(" ", "_")

    if not main_cat.dead:
        life_dir = "alive"
    else:
        life_dir = "dead"

    if main_cat.dead:
        if main_cat.status.group == CatGroup.UNKNOWN_RESIDENCE:
            spec_dir = "/unknownresidence"
        elif main_cat.status.group == CatGroup.DARK_FOREST:
            spec_dir = "/darkforest"
        else:
            spec_dir = "/starclan"
    elif main_cat.status.is_outsider:
        spec_dir = "/alive_outside"
    else:
        spec_dir = ""

    try:
        # newborns only pull from their status thoughts. this is done for convenience
        if main_cat.age == "newborn":
            loaded_thoughts = load_lang_resource(
                f"thoughts/{life_dir}{spec_dir}/newborn.json"
            )
        else:
            thoughts = load_lang_resource(f"thoughts/{life_dir}{spec_dir}/{rank}.json")
            genthoughts = load_lang_resource(
                f"thoughts/{life_dir}{spec_dir}/general.json"
            )
            loaded_thoughts = thoughts + genthoughts

        final_thoughts = _filter_list(
            loaded_thoughts, main_cat, other_cat, biome, season, camp
        )

        return final_thoughts
    except IOError:
        print("ERROR: loading thoughts")


def new_thought(main_cat: "Cat", other_cat: "Cat", biome, season, camp):
    """
    Finds a thought appropriate for the given args.
    """
    # get possible thoughts
    try:
        # checks if the cat is Rick Astley to give the rickroll thought, otherwise proceed as usual
        if (main_cat.name.prefix + main_cat.name.suffix).replace(
            " ", ""
        ).lower() == "rickastley":
            return i18n.t("defaults.rickroll")
        else:
            chosen_thought_group = choice(
                _load_group(main_cat, other_cat, biome, season, camp)
            )
            chosen_thought = choice(chosen_thought_group["thoughts"])
    except IndexError:
        traceback.print_exc()
        chosen_thought = i18n.t("defaults.thought")

    return chosen_thought


def new_death_thought(
    main_cat: "Cat",
    other_cat: "Cat",
    biome,
    season,
    camp,
    afterlife,
    lives_left,
):
    """
    Finds an on_death thought appropriate for the given args.
    """
    THOUGHTS: []
    try:
        if main_cat.status.is_leader and lives_left > 0:
            loaded_thoughts = load_lang_resource(
                f"thoughts/on_death/{afterlife}/leader_life.json"
            )
        elif main_cat.status.is_leader and lives_left == 0:
            loaded_thoughts = load_lang_resource(
                f"thoughts/on_death/{afterlife}/leader_death.json"
            )
        else:
            loaded_thoughts = load_lang_resource(
                f"thoughts/on_death/{afterlife}/general.json"
            )
        thought_group = choice(
            _filter_list(loaded_thoughts, main_cat, other_cat, biome, season, camp)
        )
        chosen_thought = choice(thought_group["thoughts"])
        return chosen_thought

    except IndexError:
        traceback.print_exc()
        return i18n.t("defaults.thought")


def _constraints_fulfilled(
    main_cat: "Cat", random_cat: "Cat", thought, biome, season, camp
) -> bool:
    """Check if thought constraints are fulfilled"""

    if "biome" in thought:
        if biome not in thought["biome"]:
            return False

    if "season" in thought:
        if season not in thought["season"]:
            return False

    if "camp" in thought:
        if camp not in thought["camp"]:
            return False

    if "not_working" in thought:
        if thought["not_working"] != main_cat.not_working():
            return False

    if not random_cat:
        r_c_in_text = [
            thought_str for thought_str in thought["thoughts"] if "r_c" in thought_str
        ]
        r_c_constraint = set(random_cat_constraints).intersection(set(thought.keys()))
        if r_c_in_text or r_c_constraint:
            return False

    if "relationship_constraint" in thought and random_cat:
        if not filter_relationship_type(
            group=[main_cat, random_cat],
            filter_types=thought["relationship_constraint"],
        ):
            return False

    main_info_dict = {}
    random_info_dict = {}

    if "main_status_constraint" in thought:
        main_info_dict["status"] = thought["main_status_constraint"]

    if "random_status_constraint" in thought and random_cat:
        random_info_dict["status"] = thought["random_status_constraint"]

    if "main_age_constraint" in thought:
        main_info_dict["age"] = thought["main_age_constraint"]

    if "random_age_constraint" in thought and random_cat:
        random_info_dict["age"] = thought["random_age_constraint"]

    if "main_trait_constraint" in thought:
        main_info_dict["trait"] = thought["main_trait_constraint"]

    if "random_trait_constraint" in thought and random_cat:
        random_info_dict["trait"] = thought["random_trait_constraint"]

    if "main_skill_constraint" in thought:
        main_info_dict["skill"] = thought["main_skill_constraint"]

    if "random_skill_constraint" in thought and random_cat:
        random_info_dict["skill"] = thought["random_skill_constraint"]

    if "main_backstory_constraint" in thought:
        main_info_dict["backstory"] = thought["main_backstory_constraint"]

    if "random_backstory_constraint" in thought:
        random_info_dict["backstory"] = thought["random_backstory_constraint"]

    if not event_for_cat(main_info_dict, main_cat):
        return False

    if random_cat and not event_for_cat(random_info_dict, random_cat):
        return False

    # Filter for the living status of the random cat. The living status of the main cat
    # is taken into account in the thought loading process.
    if random_cat and "random_living_status" in thought:
        if random_cat:
            if random_cat.dead:
                if random_cat.status.group == CatGroup.DARK_FOREST:
                    living_status = "darkforest"
                else:
                    living_status = "starclan"
            else:
                living_status = "living"
        else:
            living_status = "unknownresidence"
        if living_status and living_status not in thought["random_living_status"]:
            return False

    # this covers if living status isn't stated
    else:
        living_status = None
        if random_cat and not random_cat.dead and not random_cat.status.is_outsider:
            living_status = "living"
        if living_status and living_status != "living":
            return False

    if random_cat and random_cat.status.is_lost():
        outside_status = "lost"
    elif random_cat and random_cat.status.is_outsider:
        outside_status = "outside"
    else:
        outside_status = "clancat"

    if random_cat and "random_outside_status" in thought:
        if outside_status not in thought["random_outside_status"]:
            return False

    if "has_injuries" in thought:
        if "m_c" in thought["has_injuries"]:
            if main_cat.injuries or main_cat.illnesses:
                injuries_and_illnesses = list(main_cat.injuries.keys()) + list(
                    main_cat.injuries.keys()
                )
                if (
                    not [
                        i
                        for i in injuries_and_illnesses
                        if i in thought["has_injuries"]["m_c"]
                    ]
                    and "any" not in thought["has_injuries"]["m_c"]
                ):
                    return False
            else:
                return False

        if "r_c" in thought["has_injuries"] and random_cat:
            if random_cat.injuries or random_cat.illnesses:
                injuries_and_illnesses = list(random_cat.injuries.keys()) + list(
                    random_cat.injuries.keys()
                )
                if (
                    not [
                        i
                        for i in injuries_and_illnesses
                        if i in thought["has_injuries"]["r_c"]
                    ]
                    and "any" not in thought["has_injuries"]["r_c"]
                ):
                    return False
            else:
                return False

    if "perm_conditions" in thought:
        if "m_c" in thought["perm_conditions"]:
            if not main_cat.permanent_condition:
                return False

            valid_conditions = [
                value
                for key, value in main_cat.permanent_condition.items()
                if key in thought["perm_conditions"]["m_c"]
            ]

            if not valid_conditions and "any" not in thought["perm_conditions"]["m_c"]:
                return False

            # find whether the status is constrained to congenital
            if congenital := thought["perm_conditions"].get("born_with", {}).get("m_c"):
                # permit the event if any of the found permitted conditions matches the born_with param
                if any(
                    condition["born_with"] == congenital
                    for condition in valid_conditions
                ):
                    pass
                else:
                    return False

        if "r_c" in thought["perm_conditions"] and random_cat:
            if not random_cat.permanent_condition:
                return False

            valid_conditions = [
                value
                for key, value in random_cat.permanent_condition.items()
                if key in thought["perm_conditions"]["r_c"]
            ]

            if not valid_conditions and "any" not in thought["perm_conditions"]["r_c"]:
                return False

            # find whether the status is constrained to congenital
            if congenital := thought["perm_conditions"].get("born_with", {}).get("r_c"):
                # permit the event if any of the given permitted conditions matches the born_with param
                if any(
                    condition["born_with"] == congenital
                    for condition in valid_conditions
                ):
                    pass
                else:
                    return False

    return True
