import ujson

from scripts.cat.cats import Cat, ILLNESSES, INJURIES
from scripts.game_structure.game_essentials import game

# ---------------------------------------------------------------------------- #
#                             Condition Event Class                            #
# ---------------------------------------------------------------------------- #

class Condition_Events():
    """All events with a connection to conditions."""

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        pass

    def handle_illnesses(self, cat, season):
        """ 
        This function handles overall the illnesses in 'expanded' (or 'cruel season') game mode
        """
        triggered = False

        # handle if the current cat is already sick
        if cat.is_ill():
            cat.moon_skip_illness()
            if cat.dead:
                event_string = f"{cat.name} has died of a(n) {cat.illness.name}"
                game.cur_events_list.append(event_string)
            return triggered

        return triggered

    def handle_injuries(self, cat):
        """ 
        This function handles overall the injuries in 'expanded' (or 'cruel season') game mode
        """
        triggered = False

        # handle if the current cat is already injured
        if cat.is_injured():
            cat.moon_skip_illness()
            if cat.dead:
                event_string = f"{cat.name} has died in the medicine den, with a(n) {cat.injury.name}"
                game.cur_events_list.append(event_string)
            return triggered

        return triggered


# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/conditions/"

ILLNESSES_SEASON_LIST = None
with open(f"{resource_directory}illnesses_seasons.json", 'r') as read_file:
    ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

