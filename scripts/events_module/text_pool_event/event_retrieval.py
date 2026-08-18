from random import choices
from typing import Union, Optional

from scripts.cat.cats import Cat
from scripts.clan import OtherClan
from scripts.events_module.event_filters import find_new_frequency
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event.check_general_constraints import (
    passes_general_constraints,
)
from scripts.events_module.text_pool_event.find_involved_cats import find_cats
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent


def get_valid_event(
    primary_cat: Cat,
    involved_cats: dict,
    interactable_cats: list[Cat],
    possible_events: list[Union[PatrolEvent, TextPoolEvent]],
    chosen_frequency: int = 4,
    other_clan: Optional[OtherClan] = None,
    ensured_id: Optional[str] = None,
    test_general_constraints: bool = True,
    test_cat_constraints: bool = True,
) -> tuple[Optional[Union[PatrolEvent, TextPoolEvent]], dict]:
    """
    Check given possible_events against current game state and involved cats. Returns a valid event and involved cats.
    """
    used_frequencies = set()

    chosen_event: Optional[Union[PatrolEvent, TextPoolEvent]] = None
    temp_involved_cats = {}
    events_to_test = possible_events.copy()

    # retrieve the ensured event from the list
    ensured_event = None
    if ensured_id:
        ensured = [e for e in events_to_test if e.event_id == ensured_id]
        if ensured:
            ensured_event = ensured[0] if ensured else None
            chosen_frequency = ensured_event.frequency
        else:
            print(
                "Debug event wasn't in the list of possible event, are you sure it can generate under the current constraints?"
            )

    outside_cats = []
    if test_cat_constraints:
        outside_cats = [
            c
            for c in Cat.all_cats_list
            if (c.status.is_other_clancat or c.status.is_outsider) and not c.dead
        ]
    while not chosen_event:
        temp_involved_cats = involved_cats.copy()
        if not events_to_test:  # try a new frequency if we can
            if 4 in used_frequencies and chosen_frequency == 4:
                return (
                    None,
                    {},
                )  # failed to find anything, so we send back and origin handles it
            else:
                used_frequencies.add(chosen_frequency)
                chosen_frequency = find_new_frequency(used_frequencies)
                events_to_test = possible_events.copy()
            continue

        if ensured_event and ensured_event in possible_events:
            test_event = ensured_event
            chosen_frequency = ensured_event.frequency
            # reset it to none so that any filtering failures let us move on to a different event
            ensured_event = None
        else:
            test_event = choices(events_to_test, [x.weight for x in events_to_test])[0]

        # CHECK FREQUENCY
        if test_event.frequency != chosen_frequency:
            events_to_test.remove(test_event)
            continue

        # CHECK GENERAL CONSTRAINTS
        if test_general_constraints:
            if not passes_general_constraints(
                test_event,
                primary_cat=primary_cat,
                involved_cats=involved_cats,
                other_clan=other_clan,
                is_debug_event=bool(ensured_event),
            ):
                events_to_test.remove(test_event)
                continue

        # CHECK CAT CONSTRAINTS
        if test_cat_constraints:
            temp_involved_cats = find_cats(
                interactable_cats=interactable_cats,
                involved_cats=temp_involved_cats,
                outside_cats=outside_cats,
                event=test_event,
                other_clan=other_clan,
            )
            if not temp_involved_cats:
                events_to_test.remove(test_event)
                continue

        chosen_event = test_event
        involved_cats = temp_involved_cats

    return chosen_event, temp_involved_cats
