import ujson
import random

from scripts.cat.cats import Cat, ILLNESSES, INJURIES
from scripts.utility import save_death
from scripts.game_structure.game_essentials import game, SAVE_DEATH

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

        if cat.dead:
            return triggered

        # handle if the current cat is already sick
        if cat.is_ill():
            for risk in cat.illness.risks:
                if not int(random.random() * risk["chance"]):
                    triggered = True
                    new_illness = risk['name']
                    event_string = f"{cat.name}'s {cat.illness.name}, turned into {new_illness}."
                    cat.get_ill(new_illness , risk=True)
                    break

            if not triggered:
                illness_name = cat.illness.name
                cat.moon_skip_illness()

                if cat.dead:
                    triggered = True
                    event_string = f"{cat.name} has died of {illness_name}"
                elif not cat.is_ill():
                    event_string = f"{cat.name}'s {illness_name} has cured."

        # handle if the cat is not sick
        # SEASON
        if not triggered and not int(random.random() * 100):
            triggered = True
            season_dict = ILLNESSES_SEASON_LIST[season]
            possible_illnesses = []

            for illness_name in season_dict:
                possible_illnesses += [illness_name] * season_dict[illness_name]

            random_index = int(random.random() * len(possible_illnesses))
            cat.get_ill(possible_illnesses[random_index])
            
            if possible_illnesses[random_index] in ["running nose"]:
                event_string = f"{cat.name} has gotten a {possible_illnesses[random_index]}."
            else:
                event_string = f"{cat.name} has gotten {possible_illnesses[random_index]}."
        
        if event_string:
            if cat.dead:
                if SAVE_DEATH:
                    save_death(cat, event_string)
                game.cur_events_list.append(f"{event_string} at {cat.moons} moons")
            else: 
                game.cur_events_list.append(event_string)

        return triggered

    def handle_injuries(self, cat, season):
        """ 
        This function handles overall the injuries in 'expanded' (or 'cruel season') game mode
        """
        triggered = False
        event_string = None

        if cat.dead:
            return triggered

        # handle if the current cat is already injured
        if cat.is_injured():
            for risk in cat.injury.risks:
                if not int(random.random() * risk["chance"]):
                    triggered = True
                    new_illness = risk['name']
                    event_string = f"{cat.name}'s {cat.injury.name}, lead to {new_illness}."
                    cat.get_ill(new_illness , risk=True)
                    break

            if not triggered:
                injury_name = cat.injury.name
                cat.moon_skip_injury()
                if cat.dead:
                    triggered = True
                    save_death(cat, event_string)
                    if cat.injury.name in ["bruises","cracked pads","joint pain","scrapes","stomach aches","tickbites"]:
                        event_string = f"{cat.name} has died in the medicine den, with {injury_name} "
                    else:
                        event_string = f"{cat.name} has died in the medicine den, with a(n) {injury_name}."
                elif not cat.is_injured():
                    event_string = f"{cat.name}'s {injury_name} has cured."

        # handle if the cat is not injured
        # SEASON
        if not triggered and not int(random.random() * 40):
            triggered = True
            season_dict = INJURIES_SEASON_LIST[season]
            possible_injuries = []

            for injury_name in season_dict:
                possible_injuries += [injury_name] * season_dict[injury_name]

            random_index = int(random.random() * len(possible_injuries))
            cat.get_injured(possible_injuries[random_index])
            
            if possible_injuries[random_index] in\
                ["bruises","cracked pads","joint pain","scrapes","stomach aches","tickbites"]:
                event_string = f"{cat.name} has gotten {possible_injuries[random_index]}."
            else:
                event_string = f"{cat.name} has gotten a(n) {possible_injuries[random_index]}."

        if event_string:
            game.cur_events_list.append(event_string)

        return triggered


# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/conditions/"

special_illness = ["redcough","rat-borne infections","infected wound"]
special_injury = ["bite","broken bone","bruises","claw-wound","dislocated bone","sprain","watered lung"]

ILLNESSES_SEASON_LIST = None
with open(f"{resource_directory}illnesses_seasons.json", 'r') as read_file:
    ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

INJURIES_SEASON_LIST = None
with open(f"{resource_directory}injuries_seasons.json", 'r') as read_file:
    INJURIES_SEASON_LIST = ujson.loads(read_file.read())
