import random

from scripts.cat import pronouns
from scripts.cat.cats import Cat
from scripts.cat.enums import CatAge
from scripts.config import get_config
from scripts.events_module.event_information import EventInformation
from scripts.events_module.text_pool_event.event_retrieval import (
    load_text_pool_events,
    get_valid_event,
)
from scripts.events_module.text_pool_event.handle_consequences import execute_outcome
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import game


def attempt_coming_out(main_cat: Cat):
    """Check if main_cat wants to transition (turnin' the kitties trans...)"""

    if main_cat.moons < 3 or main_cat.gender != main_cat.genderalign:
        return

    transing_chance = get_config("transition_related")
    chance = transing_chance["base_trans_chance"]
    if main_cat.age in (CatAge.ADOLESCENT, CatAge.KITTEN):
        chance += transing_chance["adolescent_modifier"]
    elif main_cat.age in (CatAge.ADULT, CatAge.SENIOR_ADULT, CatAge.SENIOR):
        chance += transing_chance["older_modifier"]

    if not int(random.random() * chance):
        _generate_transition_event(main_cat=main_cat)

    return


def _generate_transition_event(main_cat: Cat):
    """
    Actually generate and execute transition event
    """
    possible_events = load_text_pool_events("events/transition.json")
    involved_cats = {"m_c": main_cat}

    other_clan = (
        random.choice(game.clan.all_other_clans) if game.clan.all_other_clans else None
    )

    chosen_event, involved_cats, cats_to_create = get_valid_event(
        primary_cat=main_cat,
        involved_cats=involved_cats,
        interactable_cats=Cat.all_cats_list,
        possible_events=possible_events,
        other_clan=other_clan,
        frequency_active=False,
    )
    

    processed_text = _handle_event(chosen_event, involved_cats, cats_to_create, main_cat, other_clan)

    game.cur_events_list.append(
        EventInformation(
            processed_text,
            ["misc"],
            [c.ID for c in involved_cats.values()],
        )
    )


def _handle_event(
    chosen_event: TextPoolEvent, involved_cats: dict, cats_to_create:dict, main_cat: Cat, other_clan
):
    """
    Changes the cat's genderalign and handles any other changes made by the event. Needs to be its own function for testing purposes.
    """
    # DO the transing before we execute_outcome, this ensures that we don't misgender
    main_cat.genderalign = random.choice(chosen_event.new_gender)
    main_cat.pronouns = pronouns.get_new_pronouns(main_cat.genderalign)
    # we won't use results and rel_results here
    processed_text, results, rel_results = execute_outcome(
        event=chosen_event,
        event_involved_cats=involved_cats,
        event_cats_to_create=cats_to_create,
        other_clan=other_clan,
    )
    return processed_text
