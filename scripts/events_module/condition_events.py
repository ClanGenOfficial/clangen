import ujson
import random

from scripts.cat.cats import Cat
from scripts.utility import save_death, event_text_adjust
from scripts.game_structure.game_essentials import game, SAVE_DEATH
from scripts.events_module.scar_events import Scar_Events
from scripts.events_module.generate_events import GenerateEvents


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
        self.generate_events = GenerateEvents()
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

    def handle_injuries(self, cat, other_cat, alive_kits, war, enemy_clan, season):
        """ 
        This function handles overall the injuries in 'expanded' (or 'cruel season') game mode.
        Returns: boolean - if an event was triggered
        """
        # one if-statement has a range of 10
        number_of_conditions = 4 * 10
        ratio = 40  # 1/75 times triggering for each cat each moon
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

            if not triggered and \
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
                                  "impulsive"] and \
                    random_number <= 60:
                triggered = True
            elif not triggered and random_number <= 50:
                triggered = True

            if triggered:
                possible_events = self.generate_events.possible_injury_events(cat.status)
                final_events = []

                triggered = True

                if possible_events is not None:
                    for event in possible_events:

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

                    other_clan = random.choice(game.clan.all_clans)
                    other_clan_name = f'{str(other_clan.name)}Clan'
                    enemy_clan = f'{str(enemy_clan)}'
                    current_lives = int(game.clan.leader_lives)

                    if other_clan_name == 'None':
                        other_clan = game.clan.all_clans[0]
                        other_clan_name = f'{str(other_clan.name)}Clan'

                    if len(final_events) > 0:
                        injury_event = random.choice(final_events)

                        if "war" in injury_event.tags:
                            other_clan_name = enemy_clan

                        print(cat.name, cat.status, len(final_events), other_cat.name)

                        text = event_text_adjust(Cat, injury_event.event_text, cat, other_cat, other_clan_name)

                        # record proper history text possibilities
                        if injury_event.history_text is not None:
                            if injury_event.history_text[0] is not None:
                                history_text = event_text_adjust(Cat, injury_event.history_text[0], cat, other_cat,
                                                                 other_clan_name)
                                cat.possible_scar = str(history_text)
                            if injury_event.history_text[1] is not None and cat.status != "leader":
                                history_text = event_text_adjust(Cat, injury_event.history_text[1], cat, other_cat,
                                                                 other_clan_name)
                                cat.possible_death = str(history_text)
                            elif injury_event.history_text[2] is not None and cat.status == "leader":
                                history_text = event_text_adjust(Cat, injury_event.history_text[2], cat, other_cat,
                                                                 other_clan_name)
                                cat.possible_death = str(history_text)

                        cat.get_injured(injury_event.injury)
                    else:
                        triggered = False
                        print('possible events is 0')
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
                    if injury in ["bruises", "cracked pads", "joint pain", "scrapes", "tick bites",
                                  "water in their lungs", "frostbite"]:
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
                    condition_got = self.handle_permanent_conditions(cat, injury_name=injury, scar=scar_given)

                    if condition_got:
                        event_string = f"Despite healing from {injury}, {cat.name} now has {condition_got}."

        if cat.healed_injury is not None:
            for y in healed_injury:
                cat.injuries.pop(y)
            cat.healed_injury = None

        if 1 < len(healed_injury) < 3:
            adjust_text = " and ".join(healed_injury)
            event_string = f"{cat.name}'s {adjust_text} have healed."
        elif 2 < len(healed_injury):
            extra_word = healed_injury[-1]
            healed_injury.pop(-1)
            adjust_text = ", ".join(healed_injury)
            event_string = f"{cat.name}'s {adjust_text}, and {extra_word} have healed."

        return triggered, event_string

    def handle_permanent_conditions(self,
                                    cat,
                                    condition=None,
                                    injury_name=None,
                                    scar=None,
                                    born_with=False):
        """
        need to check for what injury was healed and assign condition that may have been caused

        need to check for what scar was assigned and assign condition that may have been caused
        """

        # dict of possible physical conditions that can be acquired from relevant scars
        scar_to_condition = {
            "LEGBITE": ["weak leg"],
            "THREE": ["one bad eye", "failing eyesight"],
            "NOPAW": ["lost a leg"],
            "TOETRAP": ["weak leg"],
            "NOTAIL": ["lost their tail"],
            "HALFTAIL": ["lost their tail"],
            "LEFTEAR": ["partial hearing loss"],
            "RIGHTEAR": ["partial hearing loss"],
        }

        got_condition = False
        perm_condition = None
        possible_conditions = []

        if injury_name is not None:
            if scar is not None and scar in scar_to_condition:
                possible_conditions = scar_to_condition.get(scar)
                perm_condition = possible_conditions
            else:
                if cat.injuries[injury_name] is not None:
                    conditions = cat.injuries[injury_name]["cause_permanent"]
                    for x in conditions:
                        possible_conditions.append(x)

                    # TODO: give a random chance to gain condition - for now always assign for testing purposes
                    if len(possible_conditions) > 0:
                        perm_condition = random.choice(possible_conditions)
        elif condition is not None:
            perm_condition = condition

        if perm_condition is not None:
            got_condition = cat.get_permanent_condition(cat, perm_condition, born_with)

        if got_condition is True:
            return perm_condition


# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/events/injury"
event_triggered = "injury/"

PERMANENT = None
with open(f"resources/dicts/conditions/permanent_conditions.json", 'r') as read_file:
    PERMANENT = ujson.loads(read_file.read())
# ---------------------------------------------------------------------------- #
#                                    SEASONS                                   #
# ---------------------------------------------------------------------------- #

ILLNESSES_SEASON_LIST = None
with open(f"resources/dicts/conditions/illnesses_seasons.json", 'r') as read_file:
    ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

# ---------------------------------------------------------------------------- #
#                                    EVENTS                                    #
# ---------------------------------------------------------------------------- #

not_integrated_illness = ["redcough"]
not_integrated_injuries = ["carrionplace disease"]
