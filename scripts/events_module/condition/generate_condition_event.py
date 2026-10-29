from scripts.cat.cats import Cat
from scripts.events_module.event_information import EventInformation
from scripts.events_module.text_pool_event.event_retrieval import (
    load_text_pool_events,
    get_valid_event,
)
from scripts.events_module.text_pool_event.handle_consequences import execute_outcome


def generate_condition_event(path: str, involved_cats: dict) -> EventInformation:
    """
    Generates and executes condition event
    :param involved_cats: Cats involved in the event. Key is string designation and value is cat object (or list of cat objects)
    :param path: The path to the required condition events
    """
    possible_events = load_text_pool_events(path)

    chosen_event, involved_cats = get_valid_event(
        primary_cat=involved_cats.get("m_c", None),
        involved_cats=involved_cats,
        interactable_cats=Cat.all_cats_list,
        possible_events=possible_events,
        frequency_active=False,
    )

    # we won't use results and rel_results here
    processed_text, results, rel_results = execute_outcome(
        event=chosen_event, event_involved_cats=involved_cats
    )

    types = ["health"]
    main_cat: Cat | None = involved_cats.get("m_c", None)
    if main_cat:
        if main_cat.dead or results["death"]:
            types.append("birth_death")

        # add life loss message
        if main_cat.status.is_leader and results["death"]:
            processed_text = " ".join([processed_text, results["death"]])

    involved_ids = []
    for c in involved_cats.values():
        if isinstance(c, list):
            involved_ids.extend([_c.ID for _c in c])
        else:
            involved_ids.append(c.ID)

    return EventInformation(
        processed_text,
        types,
        involved_ids,
    )
