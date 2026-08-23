import random

from scripts.cat import pronouns
from scripts.cat.cats import Cat
from scripts.cat.enums import CatAge
from scripts.config import get_config
from scripts.event_class import Single_Event
from scripts.events_module.text_pool_event.event_retrieval import (
    load_text_pool_events,
    get_valid_event,
)
from scripts.events_module.text_pool_event.handle_consequences import execute_outcome
from scripts.game_structure import game


def attempt_coming_out(main_cat: Cat):
    """Check if main_cat wants to transition (turnin' the kitties trans...)"""

    if main_cat.moons < 3 or main_cat.gender != main_cat.genderalign:
        return

    transing_chance = get_config("transition_related")
    chance = transing_chance["base_trans_chance"]
    if main_cat.age in [CatAge.ADOLESCENT, CatAge.KITTEN]:
        chance += transing_chance["adolescent_modifier"]
    elif main_cat.age in [CatAge.ADULT, CatAge.SENIOR_ADULT, CatAge.SENIOR]:
        chance += transing_chance["older_modifier"]

    if not int(random.random() * chance):
        _generate_transition_event(main_cat=main_cat)

    return


def _generate_transition_event(main_cat: Cat):
    """
    Actually generate and execute transition event
    """
    possible_events = load_text_pool_events("events/transition")
    involved_cats = {"m_c": main_cat}

    other_clan = (
        random.choice(game.clan.all_other_clans) if game.clan.all_other_clans else None
    )

    chosen_event, involved_cats = get_valid_event(
        primary_cat=main_cat,
        involved_cats=involved_cats,
        interactable_cats=Cat.all_cats_list,
        possible_events=possible_events,
        other_clan=other_clan,
        frequency_active=False,
    )

    main_cat.genderalign = random.choice(chosen_event.new_gender)
    main_cat.pronouns = pronouns.get_new_pronouns(main_cat.genderalign)

    # we won't use results and rel_results here
    processed_text, results, rel_results = execute_outcome(
        event=chosen_event,
        event_involved_cats=involved_cats,
        other_clan=other_clan,
    )

    game.cur_events_list.append(
        Single_Event(
            processed_text,
            ["misc"],
            [c.ID for c in involved_cats],
        )
    )
