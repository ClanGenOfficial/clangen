import random

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.clan_resources.freshkill import (MAL_PERCENTAGE, STARV_PERCENTAGE, FRESHKILL_ACTIVE, )
from scripts.event_class import Single_Event
from scripts.events_module.freshkill_pile_events import FreshkillEvents
from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure.game_essentials import game
from scripts.utility import event_text_adjust


def malnourishment_check(cat: Cat) -> None:
    """
    Handles gaining conditions or death for cats with low nutrient.
    This function should only be called if the game is in 'expanded' or 'cruel season' mode.

        Parameters
        ----------
        cat : Cat
            the cat which has to be checked and updated
    """
    if not FRESHKILL_ACTIVE:
        return

    # get all events for a certain status of a cat
    cat_nutrition = cat.nutrition
    possible_events = GenerateEvents.possible_short_events(cat.status, cat.age, "nutrition")

    # get the other needed information and values to create an event
    possible_other_cats = [i for i in Cat.all_cats.values() if not (i.dead or i.outside) and i.ID != cat.ID]
    if len(possible_other_cats) <= 0:
        other_cat = None
    else:
        other_cat = random.choice(possible_other_cats)
    other_clan = random.choice(game.clan.all_clans)
    other_clan_name = f"{other_clan.name}Clan"

    needed_tags = []
    illness = None
    heal = False

    # handle death first, if percentage is 0 or lower, the cat will die
    if cat_nutrition.percentage <= 0:
        final_events = FreshkillEvents.get_filtered_possibilities(possible_events, ["death"], cat, other_cat)
        if len(final_events) <= 0:
            return

        nutrition_death(cat, final_events, other_cat, other_clan_name)
        return

    # Remove malnourished illness if nutrition above the threshold
    if (cat_nutrition.percentage > MAL_PERCENTAGE
            # and cat.is_ill()
            and "malnourished" in cat.illnesses):
        needed_tags = ["malnourished_healed"]
        illness = "malnourished"
        heal = True

    # Remove starving illness if nutrition above the threshold
    elif (cat_nutrition.percentage > STARV_PERCENTAGE
          # and cat.is_ill()
          and "starving" in cat.illnesses):
        if cat_nutrition.percentage < MAL_PERCENTAGE:
            if "malnourished" not in cat.illnesses:
                cat.get_ill("malnourished")

            needed_tags = ["starving_healed"]
            illness = "starving"
            heal = True

    # Cat's nutrition is lower than malnutrition but above starvation
    elif MAL_PERCENTAGE >= cat_nutrition.percentage > STARV_PERCENTAGE:
        # because of the smaller 'nutrition buffer', kitten and elder should get the starving condition.
        if cat.status in ["kitten", "elder"]:
            needed_tags = ["starving"]
            illness = "starving"
        else:
            needed_tags = ["malnourished"]
            illness = "malnourished"

    # Cat is starving
    elif cat_nutrition.percentage <= STARV_PERCENTAGE:
        needed_tags = ["starving"]
        illness = "starving"

    # handle the gaining/healing illness
    if heal:
        cat.illnesses.pop(illness)
    elif not heal and illness:
        cat.get_ill(illness)

    # filter the events according to the needed tags
    final_events = FreshkillEvents.get_filtered_possibilities(possible_events, needed_tags, cat, other_cat)
    if len(final_events) <= 0:
        return

    chosen_event = random.choice(final_events)
    event_text = event_text_adjust(Cat, chosen_event.event_text, cat, other_cat, other_clan_name)
    types = ["health"]
    game.cur_events_list.append(Single_Event(event_text, types, [cat.ID]))
    return


def nutrition_death(cat, final_events, other_cat, other_clan_name):
    chosen_event = random.choice(final_events)
    # set up all the text's
    death_text = event_text_adjust(Cat, chosen_event.event_text, cat, other_cat, other_clan_name)
    history_text = "this should not show up - history text"
    # give history to cat if they die
    if cat.status != "leader" and chosen_event.history_text[0] is not None:
        history_text = event_text_adjust(Cat, chosen_event.history_text[0], cat, other_cat, other_clan_name)
    elif cat.status == "leader" and chosen_event.history_text[1] is not None:
        history_text = event_text_adjust(Cat, chosen_event.history_text[1], cat, other_cat, other_clan_name)
    if cat.status == "leader":
        game.clan.leader_lives -= 1
    cat.die()
    History.add_death(cat, history_text)
    # if the cat is the leader, the illness "starving" needs to be added again
    if cat.status == "leader" and game.clan.leader_lives > 0:
        cat.get_ill("starving")
    types = ["birth_death"]
    game.cur_events_list.append(Single_Event(death_text, types, [cat.ID]))
