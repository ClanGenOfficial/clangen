try:
    import ujson
except ImportError:
    import json as ujson
import random

from scripts.cat.cats import Cat, INJURIES
from scripts.events_module.generate_events import GenerateEvents, OngoingEvent
from scripts.utility import event_text_adjust, change_clan_relations, change_relationship_values
from scripts.game_structure.game_essentials import game
from scripts.event_class import Single_Event

# ---------------------------------------------------------------------------- #
#                               Death Event Class                              #
# ---------------------------------------------------------------------------- #

class DisasterEvents():
    """All events with a connection to conditions."""

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        self.generate_events = GenerateEvents()
        pass

    def handle_disasters(self):
        """ 
        This function handles the disasters
        """

        if game.clan.primary_disaster:
            """
            need to decrease duration - always decrease by one and give a chance to decrease by 2
            need to trigger a progress event
            need to check if duration reached 0, if it did then trigger conclusion event
            check if a secondary disaster is triggered
            
            """
            print('test')
            duration = game.clan.primary_disaster.duration
            # decreasing duration, default decrease is 1 with a chance to decrease by 2
            if not int(random.random() * 10):
                game.clan.primary_disaster.duration -= 2
            else:
                game.clan.primary_disaster.duration -= 1
            print(game.clan.primary_disaster.duration)

            # triggering conclusion if duration reaches 0
            if game.clan.primary_disaster.duration <= 0:
                game.cur_events_list.append(Single_Event(random.choice(game.clan.primary_disaster.conclusion_events), "misc"))
                game.clan.primary_disaster = None
                return

            game.cur_events_list.append(
                Single_Event(random.choice(game.clan.primary_disaster.progress_events), "misc"))
            return

        print('new disaster')

        possible_events = self.generate_events.possible_ongoing_events("disasters")
        final_events = []

        for event in possible_events:
            '''if event.priority == 'secondary':
                continue
            if game.clan.current_season not in event.season:
                continue
            if game.clan.camp_bg not in event.camp and event.camp != 'any':
                continue

            if int(random.random() * event.chance):
                continue'''

            final_events.append(event)

        chosen_disaster = random.choice(final_events)

        game.clan.primary_disaster = chosen_disaster

        game.cur_events_list.append(Single_Event(random.choice(chosen_disaster.trigger_events), "misc"))


