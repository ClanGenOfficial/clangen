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
from scripts.events_module.text_pool_event.find_involved_cats import find_cats
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
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
) -> tuple[TextPoolEvent, dict[str, Union[Cat, list[Cat]]]]:
    # set up the basic cat dict
    involved_cats: dict[str, Union[Cat, list[Cat]]] = {"m_c": main_cat}

    # attempt to find a valid event where we can fill the other roles
    chosen_event, involved_cats = _find_event_and_cats(
        interactable_cats, involved_cats, main_cat, events
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
    interactable_cats, involved_cats, main_cat, possible_events: list[TextPoolEvent]
) -> tuple[TextPoolEvent, dict]:
    """
    Filters through the possible events to find the ones that we have valid cats for. Returns both the event and the valid cats.
    """
    chosen_event: Optional[TextPoolEvent] = None
    outside_cats = [
        c
        for c in Cat.all_cats_list
        if (c.status.is_other_clancat or c.status.is_outsider) and not c.dead
    ]
    while not chosen_event and possible_events:
        involved_cats = {"m_c": main_cat}
        event_to_test = choices(possible_events, [e.weight for e in possible_events])[0]

        temp_involved_cats = find_cats(
            interactable_cats=interactable_cats,
            involved_cats=involved_cats,
            outside_cats=outside_cats,
            event=event_to_test,
            other_clan=choice(game.clan.all_other_clans)
            if game.clan.all_other_clans
            else None,
        )
        if not temp_involved_cats:
            possible_events.remove(event_to_test)
            continue

        chosen_event = event_to_test
        involved_cats = temp_involved_cats

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
            event_id=event.event_id,
        ):
            allowed.append(event)

    return allowed


def _load_file(path) -> list[TextPoolEvent]:
    """
    Loads and returns the events file
    """
    # check if we've already loaded these events and then load them if need be
    if path not in loaded_events.keys():
        loaded_events[path] = []
        for t in load_lang_resource(path):
            loaded_events[path].append(
                TextPoolEvent(
                    event_id=t.get("id"),
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
