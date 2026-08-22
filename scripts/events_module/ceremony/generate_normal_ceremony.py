from random import choice

import i18n

from scripts.cat.cats import Cat
from scripts.event_class import Single_Event
from scripts.events_module.text_pool_event.handle_consequences import execute_outcome
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource


def create_ceremony(main_cat: Cat, old_name: str = None):
    """
    Finds appropriate ceremony for main_cat and adds it to the cur_events_list
    :param main_cat: Cat object for the cat receiving the ceremony
    :param old_name: The old name of the cat, if their name is changing per the ceremony
    """
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

    button_cats = involved_cats.values()
    if "clan:leader" in chosen_ceremony.tags:
        button_cats.append(game.clan.leader)

    # get random honor!
    if "r_h" in processed_string:
        try:
            honors = load_lang_resource("events/ceremonies/ceremony_traits.json")
            random_honor = choice(honors[main_cat.personality.trait])
        except FileNotFoundError or IndexError:
            random_honor = i18n.t("defaults.ceremony_honor")

        processed_string = processed_string.replace("r_h", random_honor)

    # add in the old name
    processed_string = processed_string.replace("(old_name)", old_name)

    game.cur_events_list.append(
        Single_Event(processed_string, "ceremony", [c.ID for c in button_cats])
    )
