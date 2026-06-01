import traceback
from random import choice, getrandbits
from typing import TYPE_CHECKING, Optional

import i18n

from scripts.cat.enums import CatGroup, CatThought, CatAge
from scripts.events_module.event_filters import (
    event_for_cat,
    event_for_location,
    event_for_season,
    event_for_tags,
    check_rel_constraint_groups,
)
from scripts.events_module.text_pool_event import TextPoolEvent
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource

if TYPE_CHECKING:
    from scripts.cat.cats import Cat

loaded_thoughts = {}


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
            (
                other_cat.dead and not thinking_of_dead_cat
            )  # dead and thought isn't about dead cat
            or not main_cat.relationships.get(
                other_cat.ID
            )  # no existing relationship at all
            or (
                main_cat.relationships.get(other_cat.ID)
                and main_cat.relationships[other_cat.ID].total_relationship_value == 0
            )  # the main_cat has an empty relationship toward other_cat
            or other_cat.status.is_lost()  # other cat is lost
            or other_cat.status.group_ID
            != main_cat.status.group_ID  # must have matching group
        ):
            cat_list.remove(other_cat)

            i += 1
            if i > 100 or not cat_list:
                other_cat = None
                break

            other_cat = choice(cat_list)

    return other_cat


def _filter_list(
    inter_list: list, main_cat: "Cat", other_cat: "Cat", other_clan_id=str
) -> list:
    """
    Filters thoughts in the inter_list per their constraints and returns a list of allowed thoughts.
    """
    created_list = []
    for inter in inter_list:
        if _constraints_fulfilled(
            main_cat=main_cat,
            random_cat=other_cat,
            thought=inter,
            other_clan_id=other_clan_id,
        ):
            created_list.append(inter)
    return created_list


def _load_group(
    thought_type: CatThought, main_cat: "Cat", other_cat: "Cat", other_clan_id=str
):
    """
    Loads and returns thoughts appropriate for the given args.
    """
    # get rank
    rank = main_cat.status.rank
    rank = rank.replace(" ", "_")

    start_path = f"thoughts/{thought_type}"
    new_path = start_path
    thoughts = []

    # GUIDES
    if thought_type == CatThought.IS_GUIDE:
        thoughts = _load_file(f"{start_path}/{main_cat.status.group}.json")

    # DEAD CATS
    elif thought_type == CatThought.WHILE_DEAD:
        new_path = f"{start_path}/{main_cat.status.group}"
        thoughts = _load_file(f"{new_path}/{rank}.json")
        thoughts.extend(_get_exiled_and_former(main_cat, new_path))
        thoughts.extend(_get_general(main_cat, new_path))

    # LIVING CATS
    elif thought_type == CatThought.WHILE_ALIVE:
        if main_cat.age == CatAge.NEWBORN:  # accounting for non-clan newborns
            thoughts = _load_file(f"{new_path}/newborn.json")
        else:
            thoughts = _load_file(f"{new_path}/{rank}.json")

        # make sure lost thoughts are included
        if main_cat.status.is_lost(CatGroup.PLAYER_CLAN_ID):
            prior_rank = main_cat.status.find_prior_clan_rank(CatGroup.PLAYER_CLAN_ID)
            if prior_rank:
                prior_rank = prior_rank.replace(" ", "_")
                thoughts.extend(
                    _load_file(f"{start_path}/while_lost/{prior_rank}.json")
                )

        else:
            thoughts.extend(_get_general(main_cat, new_path))
            thoughts.extend(_get_exiled_and_former(main_cat, new_path))
            thoughts.extend(_get_clancat(main_cat, new_path))

    # CATS WHO JUST CHANGED RANK
    elif thought_type == CatThought.ON_RANK_CHANGE:
        thoughts = _load_file(f"{new_path}/{rank}.json")
        thoughts.extend(_get_general(main_cat, new_path))

    # CATS WHO JUST DIED
    elif thought_type == CatThought.ON_DEATH:
        is_leader = main_cat.status.is_leader
        leader_death = main_cat.dead

        if is_leader and not leader_death:
            new_path = f"{new_path}/{game.clan.instructor.status.group}"
        else:
            new_path = f"{start_path}/{main_cat.status.group}"

        if not is_leader:
            thoughts = _load_file(f"{new_path}/general.json")
        else:
            # leader dies fully
            if leader_death:
                thoughts = _load_file(f"{new_path}/leader_death.json")
            # leader only loses a life
            else:
                thoughts = _load_file(f"{new_path}/leader_life.json")

    # PARENTAL REACTION TO BIRTH
    elif thought_type == CatThought.ON_BIRTH:
        thoughts = _load_file(f"{new_path}/parent.json")

    # ON NEW CAT ENCOUNTER
    elif thought_type == CatThought.ON_MEETING:
        if main_cat.status.is_clancat:
            thoughts = _load_file(f"{new_path}/clancat.json")
        else:
            thoughts = _load_file(f"{new_path}/outsider.json")

    # thought types with just a general path
    elif thought_type in (
        CatThought.ON_JOIN,
        CatThought.ON_EXILE,
        CatThought.ON_LOST,
        CatThought.ON_GRIEF_TOWARD_BODY,
        CatThought.ON_GRIEF_NO_BODY,
    ):
        thoughts = _load_file(f"{new_path}/general.json")

    # ON CHANGING AFTERLIFE
    elif thought_type == CatThought.ON_AFTERLIFE_CHANGE:
        thoughts = _load_file(f"{new_path}/{main_cat.status.group}.json")
        pass

    final_thoughts = _filter_list(thoughts, main_cat, other_cat, other_clan_id)

    return final_thoughts


def _get_exiled_and_former(main_cat: "Cat", path) -> list:
    """
    Checks if cat needs exiled or former clancat thoughts and returns loaded resources
    """
    thoughts = []
    # make sure exiled thoughts are included
    if main_cat.status.is_exiled(CatGroup.PLAYER_CLAN):
        thoughts.extend(_load_file(f"{path}/exiled.json"))

    # former clancat thoughts
    if main_cat.status.is_former_clancat:
        thoughts.extend(_load_file(f"{path}/former_clancat.json"))

    return thoughts


def _get_general(main_cat: "Cat", path) -> list:
    """
    Returns general thoughts if the cat is not a newborn
    """
    # newborns don't receive general thoughts
    if main_cat.age != CatAge.NEWBORN:
        return _load_file(f"{path}/general.json")

    return []


def _get_clancat(main_cat: "Cat", path) -> list:
    """
    Returns clancat thoughts if the cat is a clancat
    """
    # newborns don't receive general thoughts
    if main_cat.status.is_clancat and main_cat.age != CatAge.NEWBORN:
        return _load_file(f"{path}/clancat.json")

    return []


def _load_file(path) -> list[TextPoolEvent]:
    """
    Loads and returns the thoughts file
    """
    # check if we've already loaded these thoughts and then load them if need be
    if path not in loaded_thoughts.keys():
        loaded_thoughts[path] = []
        for t in load_lang_resource(path):
            loaded_thoughts[path].append(
                TextPoolEvent(
                    id=t.get("id"),
                    location=t.get("location", []),
                    season=t.get("season", []),
                    tags=t.get("tags", []),
                    strings=t.get("strings", []),
                    involved_cats=t.get("involved_cats", {}),
                    relationship_constraint=t.get("relationship_constraint", []),
                )
            )

    return loaded_thoughts[path]


def new_thought(
    thought_type: CatThought, main_cat: "Cat", other_cat: "Cat", other_clan_id: str
):
    """
    Finds a thought appropriate for the given args.
    :param thought_type: An enum determining what kind of thought is required
    :param main_cat: The main cat involved
    :param other_cat: The other cat involved
    :param other_clan_id: An other_clan ID. If a thought requires another Clan to be involved, this is the Clan that will be used.
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
                _load_group(thought_type, main_cat, other_cat, other_clan_id)
            )

            chosen_thought = choice(chosen_thought_group.strings)
    except IndexError:
        traceback.print_exc()
        chosen_thought = i18n.t("defaults.thought")

    return chosen_thought


def new_death_thought(
    main_cat: "Cat",
    other_cat: "Cat",
    afterlife,
    lives_left,
):
    """
    Finds an on_death thought appropriate for the given args.
    """
    THOUGHTS: []
    try:
        if main_cat.status.is_leader and lives_left > 0:
            possible_thoughts = _load_file(
                f"thoughts/on_death/{afterlife}/leader_life.json"
            )
        elif main_cat.status.is_leader and lives_left == 0:
            possible_thoughts = _load_file(
                f"thoughts/on_death/{afterlife}/leader_death.json"
            )
        else:
            possible_thoughts = _load_file(
                f"thoughts/on_death/{afterlife}/general.json"
            )
        thought_group = choice(_filter_list(possible_thoughts, main_cat, other_cat))
        chosen_thought = choice(thought_group["thoughts"])
        return chosen_thought

    except IndexError:
        traceback.print_exc()
        return i18n.t("defaults.thought")


def _constraints_fulfilled(
    main_cat: "Cat", random_cat: "Cat", thought: TextPoolEvent, other_clan_id=str
) -> bool:
    """Check if thought constraints are fulfilled"""
    involved_cats = {
        "m_c": main_cat,
        "r_c": random_cat,
    }

    if thought.location:
        if not event_for_location(thought.location):
            return False

    if thought.season:
        if not event_for_season(thought.season):
            return False

    if thought.tags:
        if not event_for_tags(thought.tags, main_cat, random_cat):
            return False

    # check that we have a random cat if the thought requires one
    if not random_cat:
        r_c_in_text = [
            thought_str for thought_str in thought.strings if "r_c" in thought_str
        ]
        r_c_constraint = thought.involved_cats.get("r_c")
        # r_c mentioned in text or required with constraints, so we dump this thought
        if r_c_in_text or r_c_constraint or thought.relationship_constraint:
            return False

    if thought.involved_cats:
        if not event_for_cat(
            thought.involved_cats.get("m_c", {}),
            cat=main_cat,
            involved_cat_dict=involved_cats,
            event_id=thought.id,
            other_involved_clan_id=other_clan_id,
        ):
            return False

        if not event_for_cat(
            thought.involved_cats.get("r_c", {}),
            cat=random_cat,
            involved_cat_dict=involved_cats,
            event_id=thought.id,
            other_involved_clan_id=other_clan_id,
        ):
            return False

    if thought.relationship_constraint:
        for constraints in thought.relationship_constraint:
            if not check_rel_constraint_groups(constraints, involved_cats):
                return False

    return True
