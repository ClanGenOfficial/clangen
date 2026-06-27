from random import choice, choices, sample
from typing import Union, List, Optional

import i18n

from scripts.cat.cats import Cat
from scripts.config import get_config
from scripts.event_class import Single_Event
from scripts.events_module.consequences import change_relationship_values
from scripts.events_module.event_filters import (
    event_for_cat,
    cat_for_event,
    check_rel_constraint_groups,
)
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
)
from scripts.events_module.text_adjust import process_text, adjust_list_text
from scripts.events_module.text_pool_event import TextPoolEvent
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource

loaded_events = {}


def trigger_interaction(main_cat: Cat, interactable_cats: list) -> list[str]:
    """
    Start a group relationship event.
    :param main_cat: The main cat that the event revolves around
    :param interactable_cats: The list of cats m_c can interact with
    :return: List of involved cat IDs
    """

    # GET EVENTS
    # choose if this is lowering or raising the relationship
    type_of_change = choice(["negative", "positive"])

    # pick how intense the change is
    intensity_chances = get_config("relationship.group_events.intensity_chances")
    chosen_intensity = choices(
        list(intensity_chances.keys()), list(intensity_chances.values())
    )[0]
    path = f"events/relationship_events/group_interactions/{chosen_intensity}/{type_of_change}.json"
    events = _load_file(path)

    # FIND VALID EVENT
    chosen_event, involved_cats = _get_event(events, interactable_cats, main_cat)

    # RESOLVE EVENT
    if not chosen_event:  # aww... nothing was possible
        return []
    else:
        return _resolve_event(
            chosen_event, chosen_intensity, involved_cats, type_of_change
        )


def _get_event(
    events: list[TextPoolEvent], interactable_cats: list[Cat], main_cat: Cat
):
    # find events that m_c can have
    possible_events = _find_events_for_main_cat(main_cat, events)

    # set up the basic cat dict
    involved_cats: dict[str, Union[Cat, list[Cat]]] = {"m_c": main_cat}

    # attempt to find a valid event where we can fill the other roles
    chosen_event, involved_cats = _find_event_and_cats(
        interactable_cats, involved_cats, main_cat, possible_events
    )
    return chosen_event, involved_cats


def _resolve_event(
    chosen_event, chosen_intensity, involved_cats, type_of_change
) -> list[str]:
    # now format up the string
    event_string = choice(chosen_event.strings)

    # handle replacing the multi_cat string
    if "multi_cat" in involved_cats:
        event_string = event_string.replace(
            "multi_cat",
            adjust_list_text([str(c.name) for c in involved_cats["multi_cat"]]),
        )
    # collect all the names and pronouns for the other cats
    replace_dict = {
        abbr: (str(c.name), choice(c.pronouns))
        for abbr, c in involved_cats.items()
        if abbr != "multi_cat"
    }
    # replace their abbreviations
    event_string = process_text(event_string, replace_dict)

    # add the postscript text
    event_string = i18n.t(
        f"relationships.{type_of_change}_postscript_{chosen_intensity}",
        text=event_string,
    )

    # collect cat IDs for the involved cat buttons
    cat_ids = []
    if "multi_cat" in involved_cats:
        cat_ids = [c.ID for c in involved_cats["multi_cat"]]
    cat_ids += [c.ID for abbr, c in involved_cats.items() if abbr != "multi_cat"]

    # append the event to the events list!
    game.cur_events_list.append(
        Single_Event(event_string, ["relation", "interaction"], cat_ids)
    )

    # influence relationships
    _influence_relationships(involved_cats, chosen_event, event_string)

    return cat_ids


def _find_event_and_cats(
    interactable_cats, involved_cats, main_cat, possible_events
) -> tuple[TextPoolEvent, dict]:
    """
    Filters through the possible events to find the ones that we have valid cats for. Returns both the event and the valid cats.
    """
    chosen_event: Optional[TextPoolEvent] = None

    while not chosen_event and possible_events:
        involved_cats = {"m_c": main_cat}
        failed = False
        event_to_test = choice(possible_events)
        possible_cats = interactable_cats.copy()

        # we go through each required kitty to see if we can find a match within our interactable cats
        for other_cat, constraints in event_to_test.involved_cats.items():
            # early break if we're out of cat options
            if not possible_cats:
                failed = True
                break

            # MAIN CAT
            if other_cat == "m_c":
                continue  # we skip this cus we already have our m_c

            # MULTI CAT
            if other_cat == "multi_cat":
                involved_cats["multi_cat"] = _get_multi_cats(
                    involved_cats, possible_cats.copy(), event_to_test, constraints
                )
                # if we found no one, then this event isn't possible, and we should try a different one
                if not involved_cats["multi_cat"]:
                    failed = True
                else:
                    # remove cats from the pool so they don't get repeated in the event
                    for c in involved_cats["multi_cat"]:
                        possible_cats.remove(c)

            # OTHER SINGLE CATS
            else:
                involved_cats[other_cat] = _get_single_cat(
                    involved_cats,
                    possible_cats.copy(),
                    event_to_test,
                    other_cat,
                    constraints,
                )

                if not involved_cats[other_cat]:
                    failed = True
                    break
                else:
                    possible_cats.remove(involved_cats[other_cat])

        if failed:
            possible_events.remove(event_to_test)
            chosen_event = None
            continue
        else:
            chosen_event = event_to_test

    return chosen_event, involved_cats


def _influence_relationships(involved_cats, event: TextPoolEvent, chosen_string: str):
    for change in event.relationship_changes:
        # get the cats_from
        cats_from = [
            involved_cats[c]
            for c in change["cats_from"]
            if c in involved_cats and c != "multi_cat"
        ]
        if "multi_cat" in change["cats_from"]:
            cats_from.extend(involved_cats["multi_cat"])

        # get the cats_to
        cats_to = [
            involved_cats[c]
            for c in change["cats_to"]
            if c in involved_cats and c != "multi_cat"
        ]
        if "multi_cat" in change["cats_to"]:
            cats_to.extend(involved_cats["multi_cat"])

        # find the values and their amounts for the kwargs
        value_changes = {}
        for value in change["values"]:
            value_changes[value] = change["amount"]

        # change the relationship!
        change_relationship_values(
            cats_from=cats_from, cats_to=cats_to, **value_changes, log=chosen_string
        )


def _find_events_for_main_cat(cat: Cat, possible_events: List[TextPoolEvent]) -> list:
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
) -> Optional[Cat]:
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
    # early return if no cats
    if not possible_cats:
        return None

    # early return if we don't need to check anything else
    if not event.relationship_constraint:
        return choice(possible_cats)

    # now we check who will qualify for the relationship_constraint
    while not chosen_cat and possible_cats:
        failed = False
        cat = choice(possible_cats)

        # tempt dict to preserve the original while we test
        temp_involved_cats = involved_cats.copy()
        temp_involved_cats[cat_abbr] = cat
        # test if the cat matches the rel constraints
        for block in event.relationship_constraint:
            # if the cat isn't part of this constraint block, then we skip it
            if cat_abbr not in block["cats_from"] + block["cats_to"]:
                continue

            if not check_rel_constraint_groups(block, temp_involved_cats):
                failed = True
                break
        # they didn't! we take them out of the running and try again
        if failed:
            possible_cats.remove(cat)
            chosen_cat = None
            continue

        # if we're here, then this is a valid cat! we move on
        chosen_cat = cat

    return chosen_cat


def _get_multi_cats(
    involved_cats: dict,
    interactable_cats: list[Cat],
    event: TextPoolEvent,
    cat_constraints: InvolvedCatDict,
) -> list[Cat]:
    # find out how many cats we'll allow
    max_cats = choice(get_config("relationship.group_events.multi_cat_amounts"))
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
    # if not enough possible cats, return empty list
    if not possible_cats or len(possible_cats) <= 1:
        return []

    involved_cats["multi_cat"] = []  # set this up ahead of time

    # if relationships aren't required, then we just pick some cats and go!
    if not event.relationship_constraint:
        chosen_cats = sample(possible_cats, min(len(possible_cats), max_cats))
        return chosen_cats

    # now we need to find who qualifies for the relationship constraints
    while len(chosen_cats) < max_cats and possible_cats:
        failed = False
        cat = choice(possible_cats)

        # copy up so that it's easier to pass this and test it, but we can still go back to the OG dict if it fails
        _temp_involved_cats = involved_cats.copy()
        _temp_involved_cats["multi_cat"].append(cat)
        # find out if this cat will match the rel constraints
        for block in event.relationship_constraint:
            # if this block doesn't include multi_cat then we skip it
            if "multi_cat" not in block["cats_from"] + block["cats_to"]:
                continue
            if not check_rel_constraint_groups(block, _temp_involved_cats):
                failed = True
                break

        # no matter what, cat is no longer allowed in the possible_cats list
        possible_cats.remove(cat)

        # bad cat :( remove from possibilities and try and new one
        if failed:
            _temp_involved_cats["multi_cat"].remove(cat)
        else:
            # if we're here, then this is a valid cat! we move on
            chosen_cats.append(cat)

    # if we didn't find enough cats, then return empty list
    if not chosen_cats or len(chosen_cats) <= 1:
        return []
    # otherwise, return all the cats we found!
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
