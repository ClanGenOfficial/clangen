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
        possible_events = self.generate_events.possible_events(cat.status, cat.age, "freshkill_pile")

        # get the other needed information and values
        possible_other_cats = list(filter(
            lambda c: not c.dead and not c.outside and c.ID != cat.ID, Cat.all_cats.values()
        ))
        if len(possible_other_cats) <= 0:
            other_cat = None
        else:
            other_cat = random.choice(possible_other_cats)
        other_clan = random.choice(game.clan.all_clans)
        other_clan_name = f'{str(other_clan.name)}Clan'

        if other_clan_name == 'None':
            other_clan = game.clan.all_clans[0]
            other_clan_name = f'{str(other_clan.name)}Clan'

        needed_tags = []
        illness = None
        heal = False

        # handle death first, if percentage is 0 or lower, the cat will die
        if nutr.percentage <= 0:
            # this statement above will prevent, that a dead cat will get an illness
            final_events = self.get_filtered_possibilities(possible_events, ["death"], cat, other_cat)
            if len(final_events) <= 0:
                return
            chosen_event = (random.choice(final_events))

            # set up all the text's
            death_text = event_text_adjust(Cat, chosen_event.event_text, cat, other_cat, other_clan_name)
            history_text = 'this should not show up - history text'

            # give history to cat if they die
            if cat.status != "leader" and chosen_event.history_text[0] is not None:
                history_text = event_text_adjust(Cat, chosen_event.history_text[0], cat, other_cat, other_clan_name)
            elif cat.status == "leader" and chosen_event.history_text[1] is not None:
                history_text = event_text_adjust(Cat, chosen_event.history_text[1], cat, other_cat, other_clan_name)

            if cat.status == "leader":
                game.clan.leader_lives -= 1
            cat.die()
            cat.died_by.append(history_text)

            types = ["birth_death"]
            game.cur_events_list.append(Single_Event(death_text, types, [cat]))
            return

        # change health status according to nutrient status
        if nutr.percentage > 70 and cat.is_ill() and "malnourished" in cat.illnesses:
            needed_tags = ["malnourished_healed"]
            illness = "malnourished"
            heal = True

        elif nutr.percentage > 30 and cat.is_ill() and "starving" in cat.illnesses:
            if nutr.percentage < 70:
                if "malnourished" not in cat.illnesses:
                    cat.get_ill("malnourished")
                needed_tags = ["starving_healed"]
                illness = "starving"
                heal = True
            else:
                needed_tags = ["starving_healed"]
                illness = "starving"
                heal = True

        elif nutr.percentage <= 70 and nutr.percentage > 40:
            # if percentage is 70 or lower, the cat will gain "malnourished" illness
            if cat.status in ["kitten", "elder"]:
                needed_tags = ["starving"]
                illness = "starving"
            else:        
                needed_tags = ["malnourished"]
                illness = "malnourished"

        elif nutr.percentage <= 40:
            # if percentage is 40 or lower, the cat will gain "starving" status
            needed_tags = ["starving"]
            illness = "starving"

        if heal:
            cat.illnesses.pop(illness)
        elif not heal and illness:
            cat.get_ill(illness)

        final_events = self.get_filtered_possibilities(possible_events, needed_tags, cat, other_cat)        
        if len(final_events) <= 0:
            return

        chosen_event = (random.choice(final_events))
        event_text = event_text_adjust(Cat, chosen_event.event_text, cat, other_cat, other_clan_name)
        types = ["health"]
        game.cur_events_list.append(Single_Event(event_text, types, [cat]))
        

    def handle_amount_freshkill_pile(self, freshkill_pile, living_cats):
        """
        Handles events (eg. a fox is attacking the camp), which are related to the freshkill pile.
        Game-mode: 'expanded' & 'cruel season'
        """
        print("TODO - events if the amount of prey is too much")


    # ---------------------------------------------------------------------------- #
    #                                helper function                               #
    # ---------------------------------------------------------------------------- #

    def get_filtered_possibilities(self, possible_events, needed_tags, cat, other_cat):
        """Returns a filtered list of possible events for a given list of tags."""
        final_events = []
        for event in possible_events:
            if any(x in event.tags for x in needed_tags):
                if event.other_cat_trait and other_cat and \
                   other_cat.trait in event.other_cat_trait:
                    final_events.append(event)
                    continue

                if event.cat_trait and cat.trait in event.cat_trait:
                    final_events.append(event)
                    continue

                if event.other_cat_skill and other_cat and \
                   other_cat.skill in event.other_cat_skill:
                    final_events.append(event)
                    continue

                if event.cat_skill and cat.skill in event.cat_skill:
                    final_events.append(event)
                    continue

                # if this event has no specification, but one of the needed tags, the event should be considered to be chosen
                if not event.other_cat_trait and not event.cat_trait and \
                    not event.other_cat_skill and not event.cat_skill:
                    final_events.append(event)
        return final_events