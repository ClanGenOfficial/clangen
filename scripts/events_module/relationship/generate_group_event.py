from random import choice, choices
from typing import Union

import i18n

from scripts.cat.cats import Cat
from scripts.config import get_config
from scripts.events_module.event_information import EventInformation
from scripts.events_module.consequences import change_relationship_values
from scripts.events_module.text_adjust import process_text, adjust_list_text
from scripts.events_module.text_pool_event.event_retrieval import (
    get_valid_event,
    load_text_pool_events,
)
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import game


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
    events = load_text_pool_events(path)

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
    # this is its own function so that we can test

    # attempt to find a valid event where we can fill the other roles
    chosen_event, involved_cats = get_valid_event(
        primary_cat=main_cat,
        involved_cats={"m_c": main_cat},
        interactable_cats=interactable_cats,
        possible_events=events,
        other_clan=(
            choice(game.clan.all_other_clans) if game.clan.all_other_clans else None
        ),
        frequency_active=False,
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
        EventInformation(event_string, ["relation", "interaction"], cat_ids)
    )

    # influence relationships
    _influence_relationships(involved_cats, chosen_event, event_string)

    return cat_ids


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
