import ujson
import random

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
        event_string = None
        # handle if the current cat is already sick
        if cat.is_ill():
            for risk in cat.illness.risks:
                if not int(random.random() * risk["chance"]):
                    triggered = True
                    new_illness = risk['name']
                    event_string = f"{cat.name}'s {cat.illness.name}, turned into {new_illness}"
                    cat.get_ill(new_illness , risk=True)
                    break

            if not triggered:
                illness_name = cat.illness.name
                cat.moon_skip_illness()

                if cat.dead:
                    triggered = True
                    event_string = f"{cat.name} has died of {illness_name}"
                if not cat.is_ill():
                    event_string = f"{cat.name}'s {illness_name} has cured"

        if not triggered and not int(random.random() * 100):
            triggered = True
            season_dict = ILLNESSES_SEASON_LIST[season]
            possible_illnesses = []

            for illness_name in season_dict:
                possible_illnesses += [illness_name] * season_dict[illness_name]

            random_index = int(random.random() * len(possible_illnesses))
            cat.get_ill(possible_illnesses[random_index])
            
            if possible_illnesses[random_index] in ["running nose"]:
                event_string = f"{cat.name} has gotten a {possible_illnesses[random_index]}"
            else:
                event_string = f"{cat.name} has gotten {possible_illnesses[random_index]}"
        
        if event_string:
            game.cur_events_list.append(event_string)

        return triggered

    def handle_injuries(self, cat):
        """ 
        This function handles overall the injuries in 'expanded' (or 'cruel season') game mode
        """
        triggered = False
        event_string = None

        # handle if the current cat is already injured
        if cat.is_injured():
            for risk in cat.injury.risks:
                if not int(random.random() * risk["chance"]):
                    triggered = True
                    new_illness = risk['name']
                    event_string = f"{cat.name}'s {cat.illness.name}, lead to {new_illness}"
                    cat.get_ill(new_illness , risk=True)
                    break

            if not triggered:
                cat.moon_skip_illness()
                if cat.dead:
                    event_string = f"{cat.name} has died in the medicine den, with a(n) {cat.injury.name}"
                    triggered = True

        if event_string:
            game.cur_events_list.append(event_string)

        return triggered


# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/conditions/"

ILLNESSES_SEASON_LIST = None
with open(f"{resource_directory}illnesses_seasons.json", 'r') as read_file:
    ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

