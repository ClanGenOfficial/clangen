import ujson
import random

from scripts.cat.cats import Cat
from scripts.utility import save_death
from scripts.game_structure.game_essentials import game, SAVE_DEATH
from scripts.events_module.scar_events import Scar_Events

# ---------------------------------------------------------------------------- #
#                             Condition Event Class                            #
# ---------------------------------------------------------------------------- #

class Condition_Events():
    """All events with a connection to conditions."""

    def __init__(self) -> None:
        self.living_cats = len(list(filter(lambda r: not r.dead, Cat.all_cats.values())))
        self.event_sums = 0
        self.had_one_event = False
        self.scar_events = Scar_Events()
        pass

    def handle_illnesses(self, cat, season):
        """ 
        This function handles overall the illnesses in 'expanded' (or 'cruel season') game mode
        """
        # one if-statement has a range of 10
        number_of_conditions = 1 * 10
        ratio = 125  # 1/100 times triggering for each cat each moon
        chance_number = number_of_conditions * ratio

        random_number = int(random.random() * chance_number)
        triggered = False
        event_string = None

        if cat.dead or game.clan.game_mode == "classic":
            return triggered

        # handle if the current cat is already sick
        if cat.is_ill():
            for risk in cat.illness.risks:
                if not int(random.random() * risk["chance"]):
                    triggered = True
                    new_illness = risk['name']
                    event_string = f"{cat.name}'s {cat.illness.name} turned into {new_illness}."
                    cat.get_ill(new_illness, risk=True)
                    break

            if not triggered:
                illness_name = cat.illness.name
                cat.moon_skip_illness()

                if cat.dead:
                    triggered = True
                    event_string = f"{cat.name} has died of {illness_name}."
                elif not cat.is_ill():
                    if illness_name in ["running nose", "stomachache"]:
                        event_string = f"{cat.name} has been cured of their {illness_name}."
                    else:
                        event_string = f"{cat.name} has been cured of {illness_name}."

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
            
            if possible_illnesses[random_index] in ["running nose", "stomachache"]:
                event_string = f"{cat.name} has gotten a {possible_illnesses[random_index]}."
            else:
                event_string = f"{cat.name} has gotten {possible_illnesses[random_index]}."
        
        if event_string:
            if cat.dead:
                if SAVE_DEATH:
                    save_death(cat, event_string)
                game.cur_events_list.append(event_string)
            else: 
                game.cur_events_list.append(event_string)

        return triggered

    def handle_injuries(self, cat, other_cat, alive_kits, season, biome):
        """ 
        This function handles overall the injuries in 'expanded' (or 'cruel season') game mode.
        Returns: boolean - if an event was triggered
        """
        # one if-statement has a range of 10
        number_of_conditions = 4 * 10
        ratio = 40 # 1/75 times triggering for each cat each moon
        chance_number = number_of_conditions * ratio

        random_number = int(random.random() * chance_number)
        triggered = False
        text = None

        if cat.dead:
            return triggered

        # handle if the current cat is already injured
        if cat.is_injured():
            triggered, event_string = self.handle_already_injured(cat)
            text = event_string
        else:
            # EVENTS
            possible_events = []
            final_events = []

            if not triggered and\
                    cat.trait in ["adventurous",
                                 "bold",
                                 "daring",
                                 "confident",
                                 "ambitious",
                                 "bloodthirsty",
                                 "fierce",
                                 "strict",
                                 "troublesome",
                                 "vengeful",
                                 "impulsive"] and\
                    random_number <= 60:
                triggered = True
            elif not triggered and random_number <= 50:
                triggered = True

            if triggered:
                if cat.status == "kitten":
                    possible_events.extend((self.generate_injury_event(KITTEN_EVENT_INJURIES)))
                elif cat.status == "apprentice":
                    possible_events.extend((self.generate_injury_event(GENERAL_EVENT_INJURIES)))
                    possible_events.extend((self.generate_injury_event(APPRENTICE_EVENT_INJURIES)))
                    possible_events.extend((self.generate_injury_event(WARRIOR_EVENT_INJURIES)))
                elif cat.status in ["warrior", "deputy"]:
                    possible_events.extend((self.generate_injury_event(GENERAL_EVENT_INJURIES)))
                    possible_events.extend((self.generate_injury_event(WARRIOR_EVENT_INJURIES)))
                elif cat.status == "elder":
                    possible_events.extend((self.generate_injury_event(GENERAL_EVENT_INJURIES)))
                    possible_events.extend((self.generate_injury_event(ELDER_EVENT_INJURIES)))
                elif cat.status in ["medicine cat", "medicine cat apprentice"]:
                    possible_events.extend((self.generate_injury_event(GENERAL_EVENT_INJURIES)))
                    possible_events.extend((self.generate_injury_event(MED_ALIKE_EVENT_INJURIES)))
                elif cat.status == "leader":
                    possible_events.extend((self.generate_injury_event(GENERAL_EVENT_INJURIES)))
                    possible_events.extend((self.generate_injury_event(WARRIOR_EVENT_INJURIES)))
                    possible_events.extend((self.generate_injury_event(LEADER_EVENT_INJURIES)))

                triggered = True

                for event in possible_events:
                    if biome not in event.tags:
                        continue

                    if season not in event.tags:
                        continue

                    if "other_cat_leader" in event.tags and other_cat.status != "leader":
                        continue
                    if "other_cat_mentor" in event.tags and cat.mentor != other_cat.ID:
                        continue
                    elif "other_cat_adult" in event.tags and other_cat.age in ["elder", "kitten"]:
                        continue

                    if "clan_kits" in event.tags and not alive_kits:
                        continue

                    if event.cat_trait is not None:
                        if cat.trait not in event.cat_trait and int(random.random() * 10):
                            continue

                    if event.cat_skill is not None:
                        if cat.skill not in event.cat_skill and int(random.random() * 10):
                            continue

                    if event.other_cat_trait is not None:
                        if other_cat.trait not in event.other_cat_trait and int(random.random() * 10):
                            continue

                    if event.other_cat_skill is not None:
                        if other_cat.skill not in event.other_cat_skill and int(random.random() * 10):
                            continue

                    final_events.append(event)

                name = str(cat.name)
                other_name = str(other_cat.name)
                danger = ["a rogue", "a dog", "a fox", "an otter", "a hawk", "an enemy warrior", "a badger"]
                tail_danger = ["a rogue", "a dog", "a fox", "an otter", "a hawk",
                               "an enemy warrior", "a badger", "a Twoleg trap"]

                if len(final_events) > 0:
                    injury_event = random.choice(final_events)
                    danger_chosen = random.choice(danger)
                    tail_danger_chosen = random.choice(tail_danger)

                    print(cat.name, cat.status, len(final_events), other_cat.name)

                    text = injury_event.event_text
                    text = text.replace("m_c", name)
                    text = text.replace("r_c", other_name)
                    text = text.replace("d_l", danger_chosen)
                    text = text.replace("t_l", tail_danger_chosen)

                    if injury_event.scar_text is not None:
                        scar_text = injury_event.scar_text
                        scar_text = scar_text.replace("m_c", name)
                        scar_text = scar_text.replace("r_c", other_name)
                        scar_text = scar_text.replace("d_l", danger_chosen)
                        scar_text = scar_text.replace("t_l", tail_danger_chosen)
                        cat.possible_scar = str(scar_text)

                    cat.get_injured(injury_event.injury)
                else:
                    triggered = False

        if not triggered:
            return triggered
        else:
            game.cur_events_list.append(text)

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
        healed_injury = []

        if game.clan.game_mode == "classic":
            return triggered

        event_string = None
        for injury in cat.injuries:
            risks = cat.injuries[injury]["risks"]
            for risk in risks:
                if risk["chance"] and not int(random.random() * risk["chance"]):
                    for chosen_risk in risks:
                        # this stops the cat from gaining a risk condition that they've already gotten
                        chosen_risk["chance"] = 0
                    triggered = True
                    new_illness = risk['name']
                    event_string = f'The {injury} caused {cat.name} to get {new_illness}.'
                    cat.get_ill(new_illness)
                    break

        if not triggered:
            for y in cat.injuries:
                injury = y
                cat.moon_skip_injury(injury)
                if cat.dead:
                    triggered = True
                    """
                    need to make death events for these so that we can have more variety
                    death history tho needs to be determined by the event that caused the injury, not sure yet how to do that best
                    """
                    if injury in ["bruises", "cracked pads", "joint pain", "scrapes", "tick bites", "water in their lungs", "frostbite"]:
                        event_string = "{cat.name} has died in the medicine den from {injury}."
                        if cat.status == "leader":
                            cat.died_by = f"died from {injury}."
                        else:
                            cat.died_by = f"{cat.name} died from {injury}."
                    else:
                        event_string = f"{cat.name} has died in the medicine den from a {injury}."
                        if cat.status == "leader":
                            cat.died_by = f"died from a {injury}."
                        else:
                            cat.died_by = f"{cat.name} died from a {injury}."

                    save_death(cat, event_string)
                    cat.not_working = False

                elif cat.healed_injury is not None:
                    triggered = True
                    scar_given = None
                    if cat.possible_scar is not None and injury != "blood loss":
                        event_string, scar_given = self.scar_events.handle_scars(cat, injury)
                    else:
                        if injury in ["bruises", "cracked pads", "scrapes", "tick bites"]:
                            event_string = f"{cat.name}'s {injury} have healed."
                        else:
                            event_string = f"{cat.name}'s {injury} has healed."

                    healed_injury.append(injury)
                    cat.not_working = False
                    self.handle_permanent_conditions(cat, injury, scar_given)

        if cat.healed_injury is not None:
            for y in healed_injury:
                cat.injuries.pop(y)
            cat.healed_injury = None

        if 1 < len(healed_injury) < 3:
            adjust_text = " and ".join(healed_injury)
            event_string = f"{cat.name}'s {adjust_text} have healed"
        elif 2 < len(healed_injury):
            extra_word = healed_injury[-1]
            healed_injury.pop(-1)
            adjust_text = ", ".join(healed_injury)
            event_string = f"{cat.name}'s {adjust_text}, and {extra_word} have healed"


        return triggered, event_string

    def handle_permanent_conditions(self, cat, injury_name, scar):
        """
        need to check for what injury was healed and assign condition that may have been caused

        need to check for what scar was assigned and assign condition that may have been caused

        """


    def generate_injury_event(self, events_dict):
        possible_events = []
        for event in events_dict:
            injury_event = InjuryEvent(
                injury=event["injury"],
                tags=event["tags"],
                event_text=event["event_text"],
                scar_text=event["scar_text"],
                cat_trait=event["cat_trait"],
                cat_skill=event["cat_skill"],
                other_cat_trait=event["other_cat_trait"],
                other_cat_skill=event["other_cat_skill"]
            )
            possible_events.append(injury_event)

        return possible_events


class InjuryEvent:
    def __init__(self,
                 injury=None,
                 tags=None,
                 event_text='',
                 scar_text='',
                 cat_trait=None,
                 cat_skill=None,
                 other_cat_trait=None,
                 other_cat_skill=None):
        self.injury = injury
        self.tags = tags
        self.event_text = event_text
        self.scar_text = scar_text
        self.cat_trait = cat_trait
        self.cat_skill = cat_skill
        self.other_cat_trait = other_cat_trait
        self.other_cat_skill = other_cat_skill


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

# ---------------------------------------------------------------------------- #
#                                    EVENTS                                    #
# ---------------------------------------------------------------------------- #

not_integrated_illness = ["redcough"]
not_integrated_injuries = ["carrionplace disease"]


KITTEN_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}kitten.json", 'r') as read_file:
    KITTEN_EVENT_INJURIES = ujson.loads(read_file.read())

APPRENTICE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}apprentice.json", 'r') as read_file:
    APPRENTICE_EVENT_INJURIES = ujson.loads(read_file.read())

WARRIOR_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}warrior.json", 'r') as read_file:
    WARRIOR_EVENT_INJURIES = ujson.loads(read_file.read())

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
