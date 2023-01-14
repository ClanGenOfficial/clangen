import random

from scripts.events_module.generate_events import GenerateEvents
from scripts.game_structure.game_essentials import game
from scripts.utility import event_text_adjust
from scripts.cat.cats import Cat
from scripts.event_class import Single_Event

class Freshkill_Events():
    """All events with a connection to freshkill pile or the nutrition of cats."""

    def __init__(self) -> None:
        self.generate_events = GenerateEvents()


    def handle_nutrient(self, cat, nutrition_info):
        """
        Handles gaining conditions or death for cats with low nutrient.
        Game-mode: 'expanded' & 'cruel season'
        """
        if cat.ID not in nutrition_info.keys():
            print(f"WARNING: Could not find cat with ID {cat.ID}({cat.name}) in the nutrition information.")
            return

        nutr = nutrition_info[cat.ID]

        # first remove the illnesses of the cat, when nutrition are raised
        if nutr.percentage > 70 and cat.is_ill() and "malnourished" in cat.illnesses:
            print("TODO - heal")

        elif nutr.percentage > 30 and cat.is_ill() and "starving" in cat.illnesses:
            if nutr.percentage < 70:
                print("TODO - gain malnourished")
            else:
                print("TODO - heal")

        elif nutr.percentage <= 0:
            # this statement above will prevent, that a dead cat will get an illness
            # if percentage is 0 or lower, the cat will die
            possible_events = self.generate_events.possible_events(cat.status, cat.age, "freshkill_pile")
            final_events = []

            # get the other needed information and values
            possible_other_cats = list(filter(
                lambda c: not c.dead and not c.outside, Cat.all_cats.values()
            ))
            other_cat = random.choice(possible_other_cats)
            other_clan = random.choice(game.clan.all_clans)
            other_clan_name = f'{str(other_clan.name)}Clan'

            if other_clan_name == 'None':
                other_clan = game.clan.all_clans[0]
                other_clan_name = f'{str(other_clan.name)}Clan'

            # sort out the events
            for event in possible_events:
                final_events.append(event)

            chosen_event = (random.choice(final_events))

            # set up all the text's
            death_text = event_text_adjust(Cat, chosen_event.event_text, cat, other_cat, other_clan_name)
            history_text = 'this should not show up - history text'

            # give history to cat if they die
            if cat.status != "leader" and chosen_event.history_text[0] is not None and "other_cat_death" not in chosen_event.tags:
                history_text = event_text_adjust(Cat, chosen_event.history_text[0], cat, other_cat, other_clan_name)
            elif cat.status == "leader" and chosen_event.history_text[1] is not None and "other_cat_death" not in chosen_event.tags:
                history_text = event_text_adjust(Cat, chosen_event.history_text[1], cat, other_cat, other_clan_name)


            if cat.status == "leader":
                game.clan.leader_lives -= 1
            cat.die()
            cat.died_by.append(history_text)

            types = ["birth_death"]
            game.cur_events_list.append(Single_Event(death_text, types, [cat]))

        elif nutr.percentage <= 70:
            # if percentage is 70 or lower, the cat will gain "malnourished" illness
            # (except kits, they will already get the illness "starving")
            print("TODO - gain malnourished")

        elif nutr.percentage <= 40:
            # if percentage is 40 or lower, the cat will gain "starving" status
            print("TODO - gain starving")


    def handle_amount_freshkill_pile(self, freshkill_pile, living_cats):
        """
        Handles events (eg. a fox is attacking the camp), which are related to the freshkill pile.
        Game-mode: 'expanded' & 'cruel season'
        """
        print("TODO - events if the amount of prey is too much")
