import traceback
from random import choice, getrandbits
from typing import Optional

import i18n

from scripts.cat.cats import Cat
from scripts.cat.enums import CatGroup, CatThought, CatAge
from scripts.events_module.text_adjust import event_text_adjust
from scripts.events_module.text_pool_event.event_retrieval import (
    get_valid_event,
    load_text_pool_events,
)
from scripts.game_structure import game, constants

used_thoughts = set()


def get_new_thought(
    main_cat: Cat, thought_type: CatThought = None, other_cat: Cat = None
):
    """
    Generates a thought for the cat, which displays on their profile.
    :param main_cat: The cat object receiving the thought.
    :param thought_type: Indicate what type of thought should be generated
    :param other_cat: If a specific other cat should be included, include their object here.
    """
    # default thought type
    if not thought_type:
        thought_type = (
            CatThought.WHILE_DEAD if main_cat.dead else CatThought.WHILE_ALIVE
        )

    if main_cat.status.is_other_clancat and not main_cat.dead:
        cat_list = [c for c in Cat.all_cats_list if c.status.is_other_clancat]
        other_clan_id = main_cat.status.group_ID
    else:
        cat_list = main_cat.all_cats_list.copy()
        other_clan_id = (
            choice(game.clan.other_clan_IDs)
            if game.clan
            and hasattr(game.clan, "other_clan_ids")
            and game.clan.other_clan_IDs
            else None
        )  # this is so stupid convoluted because of tests and game.clan initialization

    if not other_cat:
        other_cat = _get_other_cat_for_thought(
            cat_list=cat_list,
            main_cat=main_cat,
        )

    # get chosen thought
    chosen_thought = _new_thought(
        thought_type, main_cat, other_cat, other_clan_id=other_clan_id
    )

    chosen_thought = event_text_adjust(
        Cat,
        chosen_thought,
        main_cat=main_cat,
        random_cat=other_cat,
        clan=game.clan,
    )

    # insert thought
    main_cat.thought = str(chosen_thought)


def _new_thought(
    thought_type: CatThought, main_cat: Cat, other_cat: Cat, other_clan_id: str
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
            ensured_id = constants.CONFIG["thought_generation"][
                "debug_ensure_thought_id"
            ]

            involved_cats = {
                "m_c": main_cat,
            }
            if other_cat:
                involved_cats.update({"r_c": other_cat})
            if other_clan_id and game.clan.all_other_clans:
                other_clan = next(
                    c for c in game.clan.all_other_clans if c.group_ID == other_clan_id
                )
            else:
                other_clan = None

            chosen_thought_group = None
            allowed_thoughts = _load_allowed_thoughts(thought_type, main_cat)
            while not chosen_thought_group:
                unused = [
                    t for t in allowed_thoughts if t.event_id not in used_thoughts
                ]
                if not unused:
                    used_thoughts.clear()
                    unused = allowed_thoughts

                chosen_thought_group, temp_involved_cats = get_valid_event(
                    primary_cat=main_cat,
                    involved_cats=involved_cats,
                    interactable_cats=[],
                    possible_events=unused,
                    other_clan=other_clan,
                    ensured_id=ensured_id,
                    frequency_active=False,
                )

                if not chosen_thought_group:
                    used_thoughts.clear()

            if ensured_id and ensured_id != chosen_thought_group.event_id:
                print(
                    "Thought ID ensured, but the ensured thoughts could not be found. This cat likely doesn't meet the constraints."
                )

            # only use ensured index if a thought as been ensured
            ensured_index: int = (
                constants.CONFIG["thought_generation"]["debug_ensure_thought_index"]
                if ensured_id
                else None
            )
            used_thoughts.add(chosen_thought_group.event_id)

            # specifically "is not None" so that index 0 isn't picked up as a NoneType
            chosen_thought = (
                chosen_thought_group.strings[ensured_index]
                if ensured_index is not None
                else choice(chosen_thought_group.strings)
            )

    except ValueError:
        traceback.print_exc()
        chosen_thought = i18n.t("defaults.thought")

    return chosen_thought


def _get_other_cat_for_thought(
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


def _load_allowed_thoughts(thought_type: CatThought, main_cat: Cat):
    """
    Loads and returns thoughts appropriate for the given cat.
    """
    # get rank
    rank = main_cat.status.rank
    rank = rank.replace(" ", "_")

    start_path = f"thoughts/{thought_type}"
    new_path = start_path
    thoughts = []

    # GUIDES
    if thought_type == CatThought.IS_GUIDE:
        thoughts = load_text_pool_events(f"{start_path}/{main_cat.status.group}.json")

    # DEAD CATS
    elif thought_type == CatThought.WHILE_DEAD:
        new_path = f"{start_path}/{main_cat.status.group}"
        thoughts = load_text_pool_events(f"{new_path}/{rank}.json")
        thoughts.extend(_get_exiled_and_former(main_cat, new_path))
        thoughts.extend(_get_general(main_cat, new_path))

    # LIVING CATS
    elif thought_type == CatThought.WHILE_ALIVE:
        if main_cat.age == CatAge.NEWBORN:  # accounting for non-clan newborns
            thoughts = load_text_pool_events(f"{new_path}/newborn.json")
        else:
            thoughts = load_text_pool_events(f"{new_path}/{rank}.json")

        # make sure lost thoughts are included
        if main_cat.status.is_lost(CatGroup.PLAYER_CLAN_ID):
            prior_rank = main_cat.status.find_prior_clan_rank(CatGroup.PLAYER_CLAN_ID)
            if prior_rank:
                prior_rank = prior_rank.replace(" ", "_")
                thoughts.extend(
                    load_text_pool_events(f"{start_path}/while_lost/{prior_rank}.json")
                )

        else:
            thoughts.extend(_get_general(main_cat, new_path))
            thoughts.extend(_get_exiled_and_former(main_cat, new_path))
            thoughts.extend(_get_clancat(main_cat, new_path))

    # CATS WHO JUST CHANGED RANK
    elif thought_type == CatThought.ON_RANK_CHANGE:
        thoughts = load_text_pool_events(f"{new_path}/{rank}.json")
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
            thoughts = load_text_pool_events(f"{new_path}/general.json")
        else:
            # leader dies fully
            if leader_death:
                thoughts = load_text_pool_events(f"{new_path}/leader_death.json")
            # leader only loses a life
            else:
                thoughts = load_text_pool_events(f"{new_path}/leader_life.json")

    # PARENTAL REACTION TO BIRTH
    elif thought_type == CatThought.ON_BIRTH:
        thoughts = load_text_pool_events(f"{new_path}/parent.json")

    # ON NEW CAT ENCOUNTER
    elif thought_type == CatThought.ON_MEETING:
        if main_cat.status.is_clancat:
            thoughts = load_text_pool_events(f"{new_path}/clancat.json")
        else:
            thoughts = load_text_pool_events(f"{new_path}/outsider.json")

    # thought types with just a general path
    elif thought_type in (
        CatThought.ON_JOIN,
        CatThought.ON_EXILE,
        CatThought.ON_LOST,
        CatThought.ON_GRIEF_TOWARD_BODY,
        CatThought.ON_GRIEF_NO_BODY,
    ):
        thoughts = load_text_pool_events(f"{new_path}/general.json")

    # ON CHANGING AFTERLIFE
    elif thought_type == CatThought.ON_AFTERLIFE_CHANGE:
        thoughts = load_text_pool_events(f"{new_path}/{main_cat.status.group}.json")
        pass

    return thoughts


def _get_exiled_and_former(main_cat: Cat, path) -> list:
    """
    Checks if cat needs exiled or former clancat thoughts and returns loaded resources
    """
    thoughts = []
    # make sure exiled thoughts are included
    if main_cat.status.is_exiled(CatGroup.PLAYER_CLAN):
        thoughts.extend(load_text_pool_events(f"{path}/exiled.json"))

    # former clancat thoughts
    if main_cat.status.is_former_clancat:
        thoughts.extend(load_text_pool_events(f"{path}/former_clancat.json"))

    return thoughts


def _get_general(main_cat: Cat, path) -> list:
    """
    Returns general thoughts if the cat is not a newborn
    """
    # newborns don't receive general thoughts
    if main_cat.age != CatAge.NEWBORN:
        return load_text_pool_events(f"{path}/general.json")

    return []


def _get_clancat(main_cat: Cat, path) -> list:
    """
    Returns clancat thoughts if the cat is a clancat
    """
    # newborns don't receive general thoughts
    if main_cat.status.is_clancat and main_cat.age != CatAge.NEWBORN:
        return load_text_pool_events(f"{path}/clancat.json")

    return []
