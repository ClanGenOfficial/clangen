from random import choices
from typing import Union, Optional


from scripts.cat.cats import Cat
from scripts.clan import OtherClan
from scripts.events_module.event_filters import find_new_frequency, get_frequency
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event.check_general_constraints import (
    passes_general_constraints,
)
from scripts.events_module.text_pool_event.find_involved_cats import find_cats
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure.localization import load_lang_resource

loaded_events = {}


def get_valid_event(
    primary_cat: Cat,
    involved_cats: dict,
    interactable_cats: list[Cat],
    possible_events: list[Union[PatrolEvent, TextPoolEvent]],
    other_clan: Optional[OtherClan] = None,
    ensured_id: Optional[str] = None,
    general_constraints_active: bool = True,
    cat_constraints_active: bool = True,
    frequency_active: bool = True,
) -> tuple[Optional[Union[PatrolEvent, TextPoolEvent]], dict]:
    """
    Check given possible_events against current game state and involved cats. Returns a valid event and involved cats.
    :param primary_cat: The "main" cat of the event. For patrols this is the patrol leader.
    :param involved_cats: The dict of involved cats. Key is cat abbreviation, value is cat object.
    :param interactable_cats: List of cat objects who can participate in this event
    :param possible_events: List of event objects that we should find an event from
    :param other_clan: The other clan involved in this event
    :param ensured_id: ID of the ensured event, if any
    :param general_constraints_active: If true, filters by general constraints
    :param cat_constraints_active: If true, filters by cat constraints
    :param frequency_active: If true, filters by frequency.
    """
    used_frequencies = set()
    chosen_frequency = get_frequency() if frequency_active else 4

    chosen_event: Optional[Union[PatrolEvent, TextPoolEvent]] = None
    temp_involved_cats = {}
    tested_events = set()

    # retrieve the ensured event from the list
    ensured_event = None
    if ensured_id:
        ensured = next((e for e in possible_events if e.event_id == ensured_id), None)
        if ensured:
            ensured_event = ensured if ensured else None
            chosen_frequency = ensured_event.frequency
        else:
            print(
                "Debug event wasn't in the list of possible event, are you sure it can generate under the current constraints?"
            )

    outside_cats = []
    if cat_constraints_active:
        outside_cats = [
            c
            for c in Cat.all_cats_list
            if (c.status.is_other_clancat or c.status.is_outsider) and not c.dead
        ]
    while not chosen_event:
        temp_involved_cats = involved_cats.copy()
        if len(possible_events) == len(tested_events):  # try a new frequency if we can
            if (
                4 in used_frequencies and chosen_frequency == 4
            ) or not frequency_active:
                return (
                    None,
                    {},
                )  # failed to find anything, so we send back and origin handles it
            else:
                used_frequencies.add(chosen_frequency)
                chosen_frequency = find_new_frequency(used_frequencies)
                tested_events.clear()
            continue

        if ensured_event:
            test_event = ensured_event
            chosen_frequency = ensured_event.frequency
            # reset it to none so that any filtering failures let us move on to a different event
            ensured_event = None
        else:
            events = list(
                filter(lambda e: e.event_id not in tested_events, possible_events)
            )
            if not events:
                if frequency_active:
                    # no events of this frequency
                    used_frequencies.add(chosen_frequency)
                    chosen_frequency = find_new_frequency(used_frequencies)
                    tested_events.clear()
                    continue

                # otherwise we've failed to find anything so we send back and origin handles it
                return None, {}

            test_event = choices(events, [x.weight for x in events])[0]

        # CHECK FREQUENCY
        if frequency_active and test_event.frequency != chosen_frequency:
            tested_events.add(test_event.event_id)
            continue

        # CHECK GENERAL CONSTRAINTS
        if general_constraints_active:
            if not passes_general_constraints(
                test_event,
                primary_cat=primary_cat,
                involved_cats=involved_cats,
                other_clan=other_clan,
                is_debug_event=bool(ensured_event),
            ):
                tested_events.add(test_event.event_id)
                continue

        # CHECK CAT CONSTRAINTS
        if cat_constraints_active:
            temp_involved_cats = find_cats(
                interactable_cats=interactable_cats,
                involved_cats=temp_involved_cats,
                outside_cats=outside_cats,
                event=test_event,
                other_clan=other_clan,
            )
            if not temp_involved_cats:
                tested_events.add(test_event.event_id)
                continue

        chosen_event = test_event
        involved_cats = temp_involved_cats

    return chosen_event, temp_involved_cats


def load_text_pool_events(path: str) -> list[TextPoolEvent]:
    """
    Loads file at given path and returns the contents as a list of TextPoolEvent objects. If file has already been loaded before, then the cached contents are returned.
    """
    # check if we've already loaded these events and then load them if need be
    if path not in loaded_events.keys():
        loaded_events[path] = []
        for t in load_lang_resource(path):
            loaded_events[path].append(TextPoolEvent(**t))

    return loaded_events[path].copy()
