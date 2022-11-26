import ujson
import random

from scripts.cat.cats import Cat
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
        # one if-statement has a range of 10
        number_of_conditions = 1 * 10
        ratio = 70 # 1/70 times triggering for each cat each moon
        chance_number = number_of_conditions * ratio

        random_number = int(random.random() * chance_number)
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
                    event_string = f"{cat.name}'s {cat.illness.name} turned into {new_illness}."
                    cat.get_ill(new_illness , risk=True)
                    break

            if not triggered:
                illness_name = cat.illness.name
                cat.moon_skip_illness()

                if cat.dead:
                    triggered = True
                    event_string = f"{cat.name} has died of {illness_name}"
                elif not cat.is_ill():
                    event_string = f"{cat.name}'s {illness_name} has been cured."

        # handle if the cat is not sick
        # SEASON
        if not triggered and random_number <= 10:
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

    def handle_injuries(self, cat, season, biome):
        """ 
        This function handles overall the injuries in 'expanded' (or 'cruel season') game mode.
        Returns: boolean - if an event was triggered
        """
        # one if-statement has a range of 10
        number_of_conditions = 4 * 10
        ratio = 45 # 1/45 times triggering for each cat each moon
        chance_number = number_of_conditions * ratio

        random_number = int(random.random() * chance_number)
        triggered = False
        event_string = None

        if cat.dead:
            return triggered

        # handle if the current cat is already injured
        if cat.is_injured():
            triggered, event_string = self.handle_already_injured(cat)

        # NORMAL EVENTS
        if not triggered and random_number <= 10:
            triggered = True
            event_string = self.handle_event_injuries(cat)

        # NORMAL SEASON
        if not triggered and random_number > 10 and random_number <= 20:
            triggered = True
            season_dict = INJURIES_SEASON_LIST[season]
            possible_injuries = []

            for injury_name in season_dict:
                possible_injuries += [injury_name] * season_dict[injury_name]

            random_index = int(random.random() * len(possible_injuries))
            cat.get_injured(possible_injuries[random_index])
            
            if possible_injuries[random_index] in\
                ["bruises","cracked pads","joint pain","scrapes","tickbites"]:
                event_string = f"{cat.name} has gotten {possible_injuries[random_index]}."
            else:
                event_string = f"{cat.name} has gotten a(n) {possible_injuries[random_index]}."

        # SPECIAL SEASON EVENTS
        if not triggered and random_number > 20 and random_number <= 30:
            if season == "Leaf-bare" and cat.status == "elder":
                triggered = True
                event_string = f"{cat.name} did go for a walk outside the camp, but it was so slippery that they fell and broke their bone."
                cat.get_injured("broken bone")

        # handle if the cat is not injured
        # BIOME EVENTS
        if not triggered and random_number > 30 and random_number <= 40:
            triggered = True
            injury_dict = BIOME_INJURIES[biome]
            random_index = int(random.random() * len(injury_dict))
            injury_name = list(injury_dict.keys())[random_index]
            cat.get_injured(injury_name)
            if injury_name in ["bruises","cracked pads","joint pain","scrapes","tickbites"]:
                event_string = f"{injury_dict[injury_name]} {cat.name} has gotten {injury_name}."
            else:
                event_string = f"{injury_dict[injury_name]} {cat.name} has gotten a(n) {injury_name}."

        # handle if a rat attack has happened --> lead to festering wounds
        if event_string and "rat" in event_string:
            chance_number = 15
            if int(random.random() * chance_number):
                cat.get_ill("festering wounds")
                event_string = f"{event_string} The bites of the rat doesn't look good and {cat.name} has gotten a festering wounds."


        if event_string:
            event_string = event_string.replace('r_c', str(cat.name))
            game.cur_events_list.append(event_string)

        return triggered

# ---------------------------------------------------------------------------- #
#                               helper functions                               #
# ---------------------------------------------------------------------------- #

    def handle_already_injured(self, cat):
        """
        This function handles, when the cat is already injured
        Returns: boolean (if something happened) and the event_string
        """
        triggered = False
        event_string = None
        for risk in cat.injury.risks:
            if risk["chance"] and not int(random.random() * risk["chance"]):
                for risk in cat.injury.risks:
                    risk["chance"] = 0
                triggered = True
                new_illness = risk['name']
                event_string = f"{cat.name}'s {cat.injury.name}, lead to {new_illness}."
                cat.get_ill(new_illness)
                break

        if not triggered:
            injury_name = cat.injury.name
            cat.moon_skip_injury()
            if cat.dead:
                triggered = True
                save_death(cat, event_string)
                if injury_name in ["bruises","cracked pads","joint pain","scrapes","tickbites"]:
                    event_string = f"{cat.name} has died in the medicine den, with {injury_name} "
                else:
                    event_string = f"{cat.name} has died in the medicine den, with a(n) {injury_name}."
            elif not cat.is_injured():
                event_string = f"{cat.name}'s {injury_name} has been cured."

        return triggered, event_string

    def handle_event_injuries(self, cat):
        """
        This function handles, when the cat is already injured
        Returns: event_string
        """
        event_string = None

        # create a list of possible injuries and get one
        poss_injuries = POSSIBLE_INJURIES_DICT[cat.status]
        random_index = int(random.random() * len(poss_injuries))
        injury_name = poss_injuries[random_index]

        # get the needed event string dicts
        if GENERAL_EVENT_INJURIES[injury_name]:
            event_dicts = [GENERAL_EVENT_INJURIES[injury_name]]
        else:
            event_dicts = []

        # event strings based on status
        if cat.status == "kitten":
            if KITTEN_EVENT_INJURIES[injury_name]:
                event_dicts.append(KITTEN_EVENT_INJURIES[injury_name])
        elif cat.status == "apprentice":
            if WARRIOR_ALIKE_EVENT_INJURIES[injury_name]:
                event_dicts.append(WARRIOR_ALIKE_EVENT_INJURIES[injury_name])
            if APPRENTICE_EVENT_INJURIES[injury_name]:
                event_dicts.append(APPRENTICE_EVENT_INJURIES[injury_name])
        elif cat.status == "medicine cat apprentice":
            if MED_ALIKE_EVENT_INJURIES[injury_name]:
                event_dicts.append(MED_ALIKE_EVENT_INJURIES[injury_name])
        elif cat.status == "warrior":
            if WARRIOR_ALIKE_EVENT_INJURIES[injury_name]:
                event_dicts.append(WARRIOR_ALIKE_EVENT_INJURIES[injury_name])
            if WARRIOR_EVENT_INJURIES[injury_name]:
                event_dicts.append(WARRIOR_EVENT_INJURIES[injury_name])
        elif cat.status == "elder":
            if ELDER_EVENT_INJURIES[injury_name]:
                event_dicts.append(ELDER_EVENT_INJURIES[injury_name])
        elif cat.status == "medicine cat":
            if MED_ALIKE_EVENT_INJURIES[injury_name]:
                event_dicts.append(MED_ALIKE_EVENT_INJURIES[injury_name])
        elif cat.status == "deputy":
            if WARRIOR_ALIKE_EVENT_INJURIES[injury_name]:
                event_dicts.append(WARRIOR_ALIKE_EVENT_INJURIES[injury_name])
        elif cat.status == "leader":
            if WARRIOR_ALIKE_EVENT_INJURIES[injury_name]:
                event_dicts.append(WARRIOR_ALIKE_EVENT_INJURIES[injury_name])
            if LEADER_EVENT_INJURIES[injury_name]:
                event_dicts.append(LEADER_EVENT_INJURIES[injury_name])

        # create a list with all event strings
        possible_events = []
        for event_dict in event_dicts:
            for p_event_string in event_dict:
                possible_events += [p_event_string] * event_dict[p_event_string]

        # choose one string and injure the cat and replace the string inserts
        event_string = random.choice(possible_events)
        if injury_name in ["bruises","cracked pads","joint pain","scrapes", "stomachache", "tickbites"]:
            event_string = f"{event_string} {cat.name} has gotten {injury_name}."
        elif injury_name in []:
            event_string = f"{event_string} {cat.name} has gotten an {injury_name}."
        else:
            event_string = f"{event_string} {cat.name} has gotten a {injury_name}."

        cat.get_injured(injury_name)
        
        return event_string

# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/conditions/"
event_triggered = "event_injuries_strings/"

# ---------------------------------------------------------------------------- #
#                                    SEASONS                                   #
# ---------------------------------------------------------------------------- #

ILLNESSES_SEASON_LIST = None
with open(f"{resource_directory}illnesses_seasons.json", 'r') as read_file:
    ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

INJURIES_SEASON_LIST = None
with open(f"{resource_directory}injuries_seasons.json", 'r') as read_file:
    INJURIES_SEASON_LIST = ujson.loads(read_file.read())


# ---------------------------------------------------------------------------- #
#                                    BIOMES                                    #
# ---------------------------------------------------------------------------- #

BIOME_INJURIES = None
with open(f"{resource_directory}biome_injuries.json", 'r') as read_file:
    BIOME_INJURIES = ujson.loads(read_file.read())

# ---------------------------------------------------------------------------- #
#                                    EVENTS                                    #
# ---------------------------------------------------------------------------- #

not_integrated_illness = ["redcough"]
not_integrated_injuries = ["carrionplace disease"]

# define how likely each status can have this injury
EVENT_INJURIES = None
with open(f"{resource_directory}event_injuries_distribution.json", 'r') as read_file:
    EVENT_INJURIES = ujson.loads(read_file.read())

kitten_injuries_possibilities = []
for injury in EVENT_INJURIES:
    kitten_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["kitten"]

apprentice_injuries_possibilities = []
for injury in EVENT_INJURIES:
    apprentice_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["apprentice"]

warrior_injuries_possibilities = []
for injury in EVENT_INJURIES:
    warrior_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["warrior"]

med_injuries_possibilities = []
for injury in EVENT_INJURIES:
    med_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["medicine cat"]

med_app_injuries_possibilities = []
for injury in EVENT_INJURIES:
    med_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["medicine cat apprentice"]

deputy_injuries_possibilities = []
for injury in EVENT_INJURIES:
    deputy_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["deputy"]

leader_injuries_possibilities = []
for injury in EVENT_INJURIES:
    leader_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["leader"]

elder_injuries_possibilities = []
for injury in EVENT_INJURIES:
    elder_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["elder"]


general_injuries_possibilities = []
for injury in EVENT_INJURIES:
    general_injuries_possibilities += [injury] * EVENT_INJURIES[injury]["general"]

POSSIBLE_INJURIES_DICT = {
        "kitten": general_injuries_possibilities + kitten_injuries_possibilities,
        "apprentice": general_injuries_possibilities + apprentice_injuries_possibilities,
        "warrior": general_injuries_possibilities + warrior_injuries_possibilities,
        "medicine cat": general_injuries_possibilities + med_injuries_possibilities,
        "medicine cat apprentice": general_injuries_possibilities + med_app_injuries_possibilities,
        "deputy": general_injuries_possibilities + deputy_injuries_possibilities,
        "leader": general_injuries_possibilities + leader_injuries_possibilities,
        "elder": general_injuries_possibilities + elder_injuries_possibilities
}

# ---------------------------------------------------------------------------- #
#                                 event_string                                 #
# ---------------------------------------------------------------------------- #

KITTEN_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}kitten.json", 'r') as read_file:
    KITTEN_EVENT_INJURIES = ujson.loads(read_file.read())

APPRENTICE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}apprentice.json", 'r') as read_file:
    APPRENTICE_EVENT_INJURIES = ujson.loads(read_file.read())

WARRIOR_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}warrior.json", 'r') as read_file:
    WARRIOR_EVENT_INJURIES = ujson.loads(read_file.read())

WARRIOR_ALIKE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}warrior_and_alike.json", 'r') as read_file:
    WARRIOR_ALIKE_EVENT_INJURIES = ujson.loads(read_file.read())

MED_ALIKE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}medicine_and_alike.json", 'r') as read_file:
    MED_ALIKE_EVENT_INJURIES = ujson.loads(read_file.read())

LEADER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}leader.json", 'r') as read_file:
    LEADER_EVENT_INJURIES = ujson.loads(read_file.read())

ELDER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}elder.json", 'r') as read_file:
    ELDER_EVENT_INJURIES = ujson.loads(read_file.read())

GENERAL_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general.json", 'r') as read_file:
    GENERAL_EVENT_INJURIES = ujson.loads(read_file.read())
