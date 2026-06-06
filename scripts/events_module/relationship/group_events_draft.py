from random import choice, choices
from typing import Union, List

from scripts.cat.cats import Cat
from scripts.config import get_config
from scripts.events_module.event_filters import (
    event_for_cat,
    cat_for_event,
    check_rel_constraint_groups,
)
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    RelationshipConstraintDict,
)
from scripts.events_module.text_pool_event import TextPoolEvent
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource

loaded_events = {}


def start_interaction(main_cat: Cat, interactable_cats: list):
    """
    Start a group relationship event.
    :param main_cat: The main cat that the event revolves around
    :param interactable_cats: The list of cats m_c can interact with
    """

    # tracks our cats and their abbreviations
    involved_cats: dict[str, Union[Cat, list[Cat]]] = {"m_c": main_cat}

    # choose if this is lowering or raising the relationship
    type_of_change = choice(["negative", "positive"])

    # pick how intense the change is
    intensity_chances = get_config(
        game.clan, "relationship.group_events.intensity_chances"
    )
    chosen_intensity = choices(
        list(intensity_chances.keys()), list(intensity_chances.values())
    )[0]

    # find events that m_c can have
    possible_events = filter_by_main_cat(
        main_cat,
        _load_file(
            f"events/relationship_events/group_interactions/{chosen_intensity}/{type_of_change}.json"
        ),
    )

    # attempt to find a valid event where we can fill the other roles
    chosen_event = None
    possible_cats = interactable_cats.copy()
    while not chosen_event and possible_cats:
        failed = False
        event_to_test = choice(possible_events)

        # we go through each required kitty to see if we can find a match within our interactable cats
        for other_cat, constraints in event_to_test.involved_cats.items():
            if other_cat == "m_c":
                continue  # we skip this cus we already have our m_c
            # find the multi_cat group
            if other_cat == "multi_cat":
                involved_cats["multi_cat"] = _get_multi_cats(
                    involved_cats, possible_cats, event_to_test, constraints
                )
                # remove cats from the pool so they don't get repeated in the event
                for c in involved_cats["multi_cat"]:
                    possible_cats.remove(c)
                # if we found no one, then this event isn't possible, and we should try a different one
                if not involved_cats["multi_cat"]:
                    failed = True
                    break

            # onto the single cats
            involved_cats[other_cat] = _get_single_cat(
                involved_cats, interactable_cats, event_to_test, other_cat, constraints
            )

            if not involved_cats[other_cat]:
                failed = True
            else:
                possible_cats.remove(involved_cats[other_cat])

        if failed:
            continue
        else:
            chosen_event = event_to_test


def filter_by_main_cat(cat: Cat, possible_events: List[TextPoolEvent]) -> list:
    """
    Returns possible events for the given cat.
    """
    allowed = []
    for event in possible_events:
        if event_for_cat(
            event.involved_cats["m_c"],
            cat,
            event_id=event.id,
        ):
            allowed.append(event)

    return allowed


def _get_single_cat(
    involved_cats: dict,
    interactable_cats: list,
    event: TextPoolEvent,
    cat_abbr: str,
    cat_constraints: InvolvedCatDict,
) -> Cat:
    chosen_cat = None

    # get the cats who qualify
    possible_cats = cat_for_event(
        cat_constraints,
        interactable_cats,
        event.tags,
        involved_cat_dict=involved_cats,
        return_list=True,
        return_id=False,
    )

    while not chosen_cat and possible_cats:
        failed = False
        cat = choice(possible_cats)

        temp_involved_cats = involved_cats.copy()
        temp_involved_cats[cat_abbr] = cat
        for block in event.relationship_constraint:
            if not check_rel_constraint_groups(block, temp_involved_cats):
                failed = True
                break
        if failed:
            possible_cats.remove(cat)
            continue

        # if we're here, then this is a valid cat! we move on
        chosen_cat = cat

    return chosen_cat


def _get_multi_cats(
    involved_cats: dict,
    interactable_cats: list[Cat],
    event: TextPoolEvent,
    cat_constraints: InvolvedCatDict,
) -> list:
    max_cats = choice(
        get_config(game.clan, "relationship.group_events.multi_cat_amounts")
    )
    chosen_cats = []

    # get the cats who qualify
    possible_cats = cat_for_event(
        cat_constraints,
        interactable_cats,
        event.tags,
        involved_cat_dict=involved_cats,
        return_list=True,
        return_id=False,
    )

    # now we need to find who qualifies for the relationship constraints if we have those
    involved_cats["multi_cat"] = []  # set this up ahead of time
    while len(chosen_cats) < max_cats and possible_cats:
        failed = False
        cat = choice(possible_cats)

        # copy up so that it's easier to pass this and test it, but we can still go back to the OG dict if it fails
        temp_involved_cats = involved_cats.copy()
        temp_involved_cats["multi_cat"].append(cat)
        for block in event.relationship_constraint:
            if not check_rel_constraint_groups(block, temp_involved_cats):
                failed = True
                break

        # bad cat :( remove from possibilities and try and new one
        if failed:
            possible_cats.remove(cat)
            continue

        # if we're here, then this is a valid cat! we move on
        chosen_cats.append(cat)
        involved_cats["multi_cat"].append(cat)

    return chosen_cats


def _load_file(path) -> list[TextPoolEvent]:
    """
    Loads and returns the events file
    """
    # check if we've already loaded these thoughts and then load them if need be
    if path not in loaded_events.keys():
        loaded_events[path] = []
        for t in load_lang_resource(path):
            loaded_events[path].append(
                TextPoolEvent(
                    id=t.get("id"),
                    location=t.get("location", []),
                    season=t.get("season", []),
                    tags=t.get("tags", []),
                    strings=t.get("strings", []),
                    involved_cats=t.get("involved_cats", {}),
                    relationship_constraint=t.get("relationship_constraint", []),
                    relationship_changes=t.get("relationship_changes", []),
                )
            )

    return loaded_events[path]
