from random import choice

from scripts.cat.cats import Cat
from scripts.event_class import Single_Event
from scripts.events_module.text_adjust import ceremony_text_adjust
from scripts.events_module.text_pool_event.handle_consequences import execute_outcome
from scripts.game_structure import game


def create_ceremony(
    main_cat: Cat, old_name: str = None, involved_cats: dict[str, Cat] = None
):
    """
    Finds appropriate ceremony for main_cat and adds it to the cur_events_list
    :param main_cat: Cat object for the cat receiving the ceremony
    :param old_name: The old name of the cat, if their name is changing per the ceremony
    :param involved_cats: Dict of cats who are already involved, main_cat does not need to be included here. This is
    just for any specific extra cats. Key is abbreviation and value is cat object.
    """
    if not involved_cats:
        involved_cats = {}
    involved_cats.update({"m_c": main_cat})

    new_rank = main_cat.status.rank
    # TODO: load ceremony file for new_rank
    path = f"resources/lang/en/events/ceremonies/{new_rank}.json"
    possible_events = []

    # TODO: send through get_valid_event
    possible_events, involved_cats = get_valid_event()

    chosen_ceremony = choice(possible_events)

    # we won't actually use results or rel results for ceremonies
    processed_string, results, rel_results = execute_outcome(
        chosen_ceremony, involved_cats
    )

    button_cats = [c for c in involved_cats.values() if c is not None]

    # do the extra processing for specifically ceremony text
    processed_string = ceremony_text_adjust(
        main_cat.personality.trait, old_name, processed_string
    )

    game.cur_events_list.append(
        Single_Event(processed_string, "ceremony", [c.ID for c in button_cats])
    )
