import ujson
import random

import ujson as ujson

from scripts.cat.cats import Cat
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.utility import save_death, event_text_adjust, get_med_cats
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
        event = None
        cat.healed_condition = False
        event_list = []
        healed_illnesses = []
        new_illness = []
        old_illness = []

        illness_progression = {
            "running nose": ["greencough", "whitecough", "yellowcough"],
            "kitten-cough": ["whitecough"],
            "whitecough": ["greencough", "yellowcough"],
            "greencough": ["yellowcough"],
            "yellowcough": ["redcough"],
            "an infected wound": ["a festering wound"],
            "heat exhaustion": ["heat stroke"],
            "stomachache": ["diarrhea"],
        }

        if cat.dead or game.clan.game_mode == "classic":
            return triggered

        # handle if the current cat is already sick
        if cat.is_ill() and not cat.dead:
            triggered = True
            for illness in cat.illnesses:
                illness_name = illness

                # moon skip to try and kill or heal cat
                cat.moon_skip_illness(illness_name)

                # kill
                if cat.dead:
                    event = f"{cat.name} has died of {illness_name}."
                    event_list.append(event)
                    break

                # heal
                elif cat.healed_condition is True:
                    # gather potential event strings for healed illness
                    possible_string_list = ILLNESS_HEALED_STRINGS[illness]

                    # choose event string
                    random_index = int(random.random() * len(possible_string_list))

                    event = possible_string_list[random_index]
                    event = event_text_adjust(Cat, event, cat, other_cat=None)
                    healed_illnesses.append(illness_name)

                # if not dead or healed try to assign new illness from current illness risks
                else:
                    for risk in cat.illnesses[illness]["risks"]:
                        # adjust chance of risk gain if clan has enough meds
                        amount_per_med = get_amount_cat_for_one_medic(game.clan)
                        chance = risk["chance"]
                        if medical_cats_condition_fulfilled(Cat.all_cats.values(), amount_per_med):
                            chance = risk["chance"] + 10
                        if game.clan.medicine_cat is None:
                            chance = chance / 2
                            if chance <= 0:
                                chance = 1
                        if not int(random.random() * chance) and risk['name'] not in cat.illnesses:
                            new_illness_name = risk['name']
                            risk["chance"] = 0
                            new_illness.append(new_illness_name)
                            old_illness.append(illness)
                            # gather potential event strings for gotten illness
                            possible_string_list = ILLNESS_RISK_STRINGS[illness][new_illness_name]

                            # choose event string and ensure clan's med cat number aligns with event text
                            random_index = int(random.random() * len(possible_string_list))
                            med_list = get_med_cats(Cat)
                            med_cat = None
                            if len(med_list) == 0 and random_index == 0:
                                random_index = 1
                            else:
                                med_cat = random.choice(med_list)
                            event = possible_string_list[random_index]
                            event = event_text_adjust(Cat, event, cat, med_cat)  # adjust the text
                            break

                # add whatever event string to the event list
                if event is not None:
                    event_list.append(event)

            # making sure that when an illness progresses, the old illness is not kept and new illness is given
            if len(new_illness) > 0:
                for y in range(len(new_illness)):
                    for x in illness_progression:
                        if x == old_illness[y]:
                            if new_illness[y] in illness_progression.get(x) and old_illness[y] in cat.illnesses:
                                cat.illnesses.pop(old_illness[y])
                            else:
                                continue
                    cat.get_ill(new_illness[y])

        # joining event list into one event string
        if len(event_list) > 0:
            event_string = ' '.join(event_list)
        else:
            event_string = None

        # if the cat healed from illnesses, then remove those illnesses
        if cat.healed_condition is True and not cat.dead:
            for y in healed_illnesses:
                cat.illnesses.pop(y)
            # reset healed_condition value
            cat.healed_condition = False

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

        # if an event happened, then add event to cur_event_list and save death if it happened.
        if event_string:
            if cat.dead:
                if SAVE_DEATH:
                    save_death(cat, event_string)
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

                for event in possible_events:

                    if event.injury in INJURIES:
                        injury = INJURIES[event.injury]
                        severity = injury['severity']
                        if cat.status in INJURY_DISTRIBUTION:
                            severity_chance = INJURY_DISTRIBUTION[cat.status][severity]
                            if int(random.random() * severity_chance):
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

        if not triggered:
            return triggered
        else:
            game.cur_events_list.append(text)

            return triggered

    def handle_permanent_conditions(self,
                                    cat,
                                    condition=None,
                                    injury_name=None,
                                    scar=None,
                                    born_with=False):
        """
        this function handles overall the permanent conditions of a cat.
        returns boolean if event was triggered
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

        scarless_conditions = [
            "weak leg", "paralyzed", "raspy lungs", "wasting disease", "blind", "failing eyesight", "one bad eye",
            "partial hearing loss", "deaf", "constant joint pain", "constantly dizzy", "recurring shock"
        ]

        got_condition = False
        perm_condition = None
        possible_conditions = []

        if injury_name is not None:
            if scar is not None and scar in scar_to_condition:
                possible_conditions = scar_to_condition.get(scar)
                perm_condition = random.choice(possible_conditions)
            elif scar is None:
                if cat.injuries[injury_name] is not None:
                    conditions = cat.injuries[injury_name]["cause_permanent"]
                    for x in conditions:
                        if x in scarless_conditions:
                            possible_conditions.append(x)

                    if len(possible_conditions) > 0 and not int(random.random() * 40):
                        perm_condition = random.choice(possible_conditions)
                    else:
                        return perm_condition

        elif condition is not None:
            perm_condition = condition

        if perm_condition is not None:
            got_condition = cat.get_permanent_condition(cat, perm_condition, born_with)

        if got_condition is True:
            return perm_condition

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
        event_list = []
        new_condition = None

        if game.clan.game_mode == "classic":
            return triggered

        for injury in cat.injuries:
            risks = cat.injuries[injury]["risks"]
            for risk in risks:
                # adjust chance of risk gain if clan has enough meds or if clan has no meds at all
                amount_per_med = get_amount_cat_for_one_medic(game.clan)
                chance = risk["chance"]
                if medical_cats_condition_fulfilled(Cat.all_cats.values(), amount_per_med):
                    chance = risk["chance"] + 10
                if game.clan.medicine_cat is None:
                    chance = chance / 2
                    if chance <= 0:
                        chance = 1
                if not int(random.random() * chance):
                    if risk['name'] not in cat.injuries and risk['name'] not in cat.illnesses:
                        if risk['name'] == 'an infected wound' and 'a festering wound' in cat.illnesses:
                            break  # prevents a cat with a festering wound from receiving an infected wound
                        new_condition = risk['name']
                        # gather potential event strings for gotten condition
                        possible_string_list = INJURY_RISK_STRINGS[injury][new_condition]

                        # choose event string and ensure clan's med cat number aligns with event text
                        random_index = int(random.random() * len(possible_string_list))
                        med_list = get_med_cats(Cat)
                        med_cat = None
                        if len(med_list) == 0 and random_index == 0:
                            random_index = 1
                        else:
                            med_cat = random.choice(med_list)
                        event = possible_string_list[random_index]
                        event = event_text_adjust(Cat, event, cat, med_cat)  # adjust the text
                        event_list.append(event)
                        break
            if new_condition is not None:
                triggered = True
                break

        if new_condition in ILLNESSES:
            cat.get_ill(new_condition)
        elif new_condition in INJURIES:
            if new_condition == 'lingering shock':
                print(new_condition)
                cat.injuries.pop('shock')
            cat.get_injured(new_condition)

        if not triggered:
            for y in cat.injuries:
                injury = y
                cat.moon_skip_injury(injury)
                if cat.dead:
                    triggered = True
                    # TODO: need to make death events for these so that we can have more variety

                    if injury in ["bruises", "cracked pads", "joint pain", "scrapes", "tick bites",
                                  "water in their lungs", "frostbite"]:
                        if cat.status == "leader":
                            event = f"{cat.name} has died in the medicine den from {injury}, losing a life."
                            cat.died_by = f"died from {injury}."
                        else:
                            event = f"{cat.name} has died in the medicine den from {injury}."
                            cat.died_by = f"{cat.name} died from {injury}."
                    else:
                        if cat.status == "leader":
                            event = f"{cat.name} has died in the medicine den from a {injury}, losing a life."
                            cat.died_by = f"died from a {injury}."
                        else:
                            event = f"{cat.name} has died in the medicine den from a {injury}."
                            cat.died_by = f"{cat.name} died from a {injury}."
                    event_list.append(event)
                    save_death(cat, event)
                    break

                elif cat.healed_condition is True:
                    triggered = True
                    scar_given = None

                    # only try to give a scar if the event gave possible scar history
                    if cat.possible_scar is not None and injury not in ["blood loss", "shock", "lingering shock"]:
                        event, scar_given = self.scar_events.handle_scars(cat, injury)
                    else:
                        if injury in ["bruises", "cracked pads", "scrapes", "tick bites"]:
                            event = f"{cat.name}'s {injury} have healed."
                        elif injury == 'recovering from birth':
                            event = f'{cat.name} is no longer recovering from birth.'
                        else:
                            event = f"{cat.name}'s {injury} has healed."

                    healed_injury.append(injury)

                    # try to give a permanent condition based on healed injury and new scar if any
                    condition_got = self.handle_permanent_conditions(cat, injury_name=injury, scar=scar_given)

                    if condition_got is not None:
                        # gather potential event strings for gotten condition
                        possible_string_list = PERMANENT_CONDITION_GOT_STRINGS[injury][condition_got]

                        # choose event string and ensure clan's med cat number aligns with event text
                        random_index = int(random.random() * len(possible_string_list))
                        med_list = get_med_cats(Cat)
                        med_cat = None
                        if len(med_list) == 0 and random_index == 0:
                            random_index = 2
                        else:
                            med_cat = random.choice(med_list)
                            if med_cat == cat:
                                random_index = 2
                        event = possible_string_list[random_index]
                        event = event_text_adjust(Cat, event, cat, other_cat=med_cat)  # adjust the text

                    if event is not None:
                        event_list.append(event)

        if cat.healed_condition is True:
            for y in healed_injury:
                cat.injuries.pop(y)
            cat.healed_condition = False

        if len(event_list) > 0:
            event_string = ' '.join(event_list)
        else:
            event_string = None
        return triggered, event_string

    def handle_already_disabled(self, cat):
        """
        this function handles what happens if the cat already has a permanent condition.
        Returns: boolean (if something happened) and the event_string
        """
        triggered = False

        if game.clan.game_mode == "classic":
            return triggered

        event_list = []

        new_condition = []
        old_condition = []

        condition_progression = {
            "one bad eye": ["failing eyesight"],
            "failing eyesight": ["blind"],
            "partial hearing loss": ["deaf"]
        }

        for condition in cat.permanent_condition:
            # checking if the cat has a congenital condition to reveal
            condition_appears = cat.moon_skip_permanent_condition(condition)
            if cat.dead:
                triggered = True

                event = f"{cat.name} has died from complications caused by {condition}."
                event_list.append(event)
                save_death(cat, event)

            elif condition_appears:

                triggered = True

        if not triggered:
            for condition in cat.permanent_condition:
                if cat.permanent_condition[condition]["moons_until"] is None or cat.permanent_condition[condition]["moons_until"] == 0:
                    for risk in cat.permanent_condition[condition]["risks"]:
                        if not int(random.random() * risk["chance"]):
                            triggered = True
                            new_ouchie = risk["name"]

                            # gather potential event strings for gotten risk
                            possible_string_list = PERM_CONDITION_RISK_STRINGS[condition][new_ouchie]

                            # choose event string and ensure clan's med cat number aligns with event text
                            random_index = int(random.random() * len(possible_string_list))
                            med_list = get_med_cats(Cat)
                            med_cat = None
                            if len(med_list) == 0 and random_index == 0:
                                random_index = 1
                            else:
                                med_cat = random.choice(med_list)
                            event = possible_string_list[random_index]
                            event = event_text_adjust(Cat, event, cat, other_cat=med_cat)  # adjust the text
                            event_list.append(event)
                            if new_ouchie in INJURIES:
                                cat.get_injured(new_ouchie, event_triggered=True)
                                break
                            elif new_ouchie in ILLNESSES:
                                cat.get_ill(new_ouchie, event_triggered=True)
                                break
                            elif new_ouchie in PERMANENT:
                                new_condition.append(new_ouchie)
                                old_condition.append(condition)
                                break

            if len(new_condition) > 0:
                for y in range(len(new_condition)):
                    for x in condition_progression:
                        if x == old_condition[y]:
                            if new_condition[y] in condition_progression.get(x):
                                cat.permanent_condition.pop(old_condition[y])
                    cat.get_permanent_condition(cat, new_condition[y], event_triggered=True)

        retire_chances = {
            'kitten': 0,
            'adolescent': 100,
            'young adult': 80,
            'adult': 70,
            'senior adult': 50,
            'elder': 0
        }

        if not triggered and not cat.dead and not cat.retired and cat.status not in ['leader', 'medicine cat', 'kitten']:
            for condition in cat.permanent_condition:
                if cat.permanent_condition[condition]['severity'] == 'major':
                    chance = int(retire_chances.get(cat.age))
                    if not int(random.random() * chance):
                        cat.retire_cat()
                        event = f'{cat.name} has decided to retire from normal clan duty.'
                        event_list.append(event)

                if cat.permanent_condition[condition]['severity'] == 'severe':
                    cat.retire_cat()
                    event = f'{cat.name} has decided to retire from normal clan duty.'
                    event_list.append(event)

        if len(event_list) > 0:
            event_string = ' '.join(event_list)
            game.cur_events_list.append(event_string)
        return

# ---------------------------------------------------------------------------- #
#                                LOAD RESOURCES                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/conditions/"

ILLNESSES = None
with open(f"{resource_directory}illnesses.json", 'r') as read_file:
    ILLNESSES = ujson.loads(read_file.read())

INJURIES = None
with open(f"{resource_directory}injuries.json", 'r') as read_file:
    INJURIES = ujson.loads(read_file.read())

PERMANENT = None
with open(f"resources/dicts/conditions/permanent_conditions.json", 'r') as read_file:
    PERMANENT = ujson.loads(read_file.read())
# ---------------------------------------------------------------------------- #
#                                    CHANCE                                    #
# ---------------------------------------------------------------------------- #

ILLNESSES_SEASON_LIST = None
with open(f"resources/dicts/conditions/illnesses_seasons.json", 'r') as read_file:
    ILLNESSES_SEASON_LIST = ujson.loads(read_file.read())

INJURY_DISTRIBUTION = None
with open(f"resources/dicts/conditions/event_injuries_distribution.json", 'r') as read_file:
    INJURY_DISTRIBUTION = ujson.loads(read_file.read())

not_integrated_illness = ["redcough"]
not_integrated_injuries = ["carrionplace disease"]

# ---------------------------------------------------------------------------- #
#                                   STRINGS                                    #
# ---------------------------------------------------------------------------- #

PERM_CONDITION_RISK_STRINGS = None
with open(f"resources/dicts/conditions/risk_strings/permanent_condition_risk_strings.json", 'r') as read_file:
    PERM_CONDITION_RISK_STRINGS = ujson.loads(read_file.read())

ILLNESS_RISK_STRINGS = None
with open(f"resources/dicts/conditions/risk_strings/illness_risk_strings.json", 'r') as read_file:
    ILLNESS_RISK_STRINGS = ujson.loads(read_file.read())

INJURY_RISK_STRINGS = None
with open(f"resources/dicts/conditions/risk_strings/injuries_risk_strings.json", 'r') as read_file:
    INJURY_RISK_STRINGS = ujson.loads(read_file.read())

CONGENITAL_CONDITION_GOT_STRINGS = None
with open(f"resources/dicts/conditions/condition_got_strings/gain_congenital_condition_strings.json", 'r') as read_file:
    CONGENITAL_CONDITION_GOT_STRINGS = ujson.loads(read_file.read())

PERMANENT_CONDITION_GOT_STRINGS = None
with open(f"resources/dicts/conditions/condition_got_strings/gain_permanent_condition_strings.json", 'r') as read_file:
    PERMANENT_CONDITION_GOT_STRINGS = ujson.loads(read_file.read())

ILLNESS_HEALED_STRINGS = None
with open(f"resources/dicts/conditions/healed_strings/illness_healed_strings.json", 'r') as read_file:
    ILLNESS_HEALED_STRINGS = ujson.loads(read_file.read())
