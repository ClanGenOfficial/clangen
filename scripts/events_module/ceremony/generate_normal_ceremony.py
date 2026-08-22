from random import choice

from scripts.cat.cats import Cat
from scripts.events_module.text_pool_event.handle_consequences import execute_outcome


def get_ceremony(main_cat: Cat, old_name: str):
    involved_cats = {"m_c": main_cat}

    new_rank = main_cat.status.rank
    # TODO: load ceremony file for new_rank
    possible_events = []

    # TODO: send through get_valid_event
    possible_events, involved_cats = get_valid_event()

    chosen_ceremony = choice(possible_events)

    # we won't actually use results or rel results for ceremonies
    processed_string, results, rel_results = execute_outcome(
        chosen_ceremony, involved_cats
    )

    # add in the old name
    processed_string = processed_string.replace("(old_name)", old_name)

    return processed_string
