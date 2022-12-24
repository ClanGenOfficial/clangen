import ujson
import random

import ujson as ujson

from scripts.cat.cats import Cat
from scripts.conditions import medical_cats_condition_fulfilled, get_amount_cat_for_one_medic
from scripts.utility import save_death, event_text_adjust, get_med_cats, change_relationship_values
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
        # return immediately if they're already dead or in the wrong game-mode
        triggered = False
        if cat.dead or game.clan.game_mode == "classic":
            if cat.dead:
                triggered = True
            return triggered

        # one if-statement has a range of 10
        number_of_conditions = 1 * 10
        ratio = 125  # 1/125 times triggering for each cat each moon

        cat.healed_condition = False
        event_list = []
        healed_illnesses = []
        new_illness = []
        old_illness = []

        illness_progression = {
            "running nose": "whitecough",
            "kittencough": "whitecough",
            "whitecough": "yellowcough",
            "greencough": "yellowcough",
            "yellowcough": "redcough",
            "an infected wound": "a festering wound",
            "heat exhaustion": "heat stroke",
            "stomachache": "diarrhea",
            "grief stricken": "lasting grief"
        }

        # ---------------------------------------------------------------------------- #
        #                         handle currently sick cats                           #
        # ---------------------------------------------------------------------------- #
        # need to hold this number so that we can check if the leader has died
        starting_life_count = game.clan.leader_lives
        clear_leader_conditions = False

        if cat.is_ill():
            triggered = True
            for illness in cat.illnesses:

                # moon skip to try and kill or heal cat
                skipped = cat.moon_skip_illness(illness)
                # test print, to track if events are displaying correctly
                #print(illness, cat.name, cat.healed_condition)

                # if event trigger was true, events should be skipped for this illness
                if skipped is True:
                    continue

                # death event text and break bc any other illnesses no longer matter
                if cat.dead and cat.status != 'leader':
                    event = f"{cat.name} has died of {illness}."
                    # clear event list to get rid of any healed or risk event texts from other illnesses
                    event_list.clear()
                    event_list.append(event)
                    break

                # if the leader died, then break before handling other illnesses cus they'll be fully healed
                elif cat.dead and cat.status == 'leader':
                    break
                elif cat.status == 'leader' and starting_life_count != game.clan.leader_lives:
                    clear_leader_conditions = True
                    break

                # heal the cat
                elif cat.healed_condition is True:
                    # gather potential event strings for healed illness
                    possible_string_list = ILLNESS_HEALED_STRINGS[illness]

                    # choose event string
                    random_index = int(random.random() * len(possible_string_list))
                    event = possible_string_list[random_index]
                    event = event_text_adjust(Cat, event, cat, other_cat=None)
                    event_list.append(event)

                    # append to healed illness list bc we can't remove the illness while inside the for loop
                    healed_illnesses.append(illness)
                    cat.healed_condition = False

                    # move to next illness, the cat can't get a risk from an illness that has healed
                    continue
                if illness in cat.illnesses:

                    # if not dead or healed try to assign new illness from current illness risks
                    for risk in cat.illnesses[illness]["risks"]:

                        # adjust chance of risk gain if clan has enough meds
                        chance = risk["chance"]
                        if medical_cats_condition_fulfilled(Cat.all_cats.values(), get_amount_cat_for_one_medic(game.clan)):
                            chance = risk["chance"] + 10  # lower risk if enough meds
                        if game.clan.medicine_cat is None:
                            chance = int(chance * .75)  # higher risk if no meds
                            if chance <= 0:  # ensure that chance is never 0
                                chance = 1

                        # if we hit the chance, then give the risk if the cat does not already have the risk
                        if not int(random.random() * chance) and risk['name'] not in cat.illnesses:
                            # check if the new risk is a previous stage of a current illness
                            skip = False
                            if risk['name'] in illness_progression:
                                if illness_progression[risk['name']] in cat.illnesses:
                                    skip = True
                            # if it is, then break instead of giving the risk
                            if skip is True:
                                break

                            new_condition_name = risk['name']
                            risk["chance"] += 10  # lower risk of getting it again

                            # check if the risk is an injury or perm, so we can treat it differently from new illnesses
                            if new_condition_name in INJURIES:
                                cat.get_injured(new_condition_name)
                            if new_condition_name in PERMANENT:
                                cat.get_permanent_condition(new_condition_name)
                            # but if it IS an illness, append to relevant lists, so we can handle it outside the loop
                            else:
                                new_illness.append(new_condition_name)
                                old_illness.append(illness)

                            # gather potential event strings for gotten illness
                            possible_string_list = ILLNESS_RISK_STRINGS[illness][new_condition_name]

                            # choose event string and ensure clan's med cat number aligns with event text
                            random_index = int(random.random() * len(possible_string_list))
                            med_list = get_med_cats(Cat)
                            med_cat = None
                            if len(med_list) == 0:
                                if random_index == 0:
                                    random_index = 1
                                else:
                                    med_cat = None
                            else:
                                med_cat = random.choice(med_list)
                                if med_cat == cat:
                                    random_index = 1
                            event = possible_string_list[random_index]
                            event = event_text_adjust(Cat, event, cat, med_cat)  # adjust the text
                            event_list.append(event)

                            # break out of risk giving loop cus we don't want to give multiple risks for one illness
                            break

            if clear_leader_conditions is True or cat.dead:
                # reset leader after death
                cat.injuries.clear()
                cat.illnesses.clear()
                new_illness.clear()
                old_illness.clear()
                healed_illnesses.clear()
                cat.healed_condition = False

            # making sure that when an illness progresses, the old illness is not kept and new illness is given
            if len(new_illness) > 0:
                for y in range(len(new_illness)):
                    # check against progression dict
                    for x in illness_progression:
                        if old_illness[y] == x and \
                                new_illness[y] == illness_progression.get(x) and \
                                old_illness[y] in cat.illnesses:
                            # remove the old illness if the new one is a progression
                            cat.illnesses.pop(old_illness[y])
                    # make the cat ill with new illness regardless of how progression check went
                    cat.get_ill(new_illness[y])

            # if the cat healed from illnesses, then remove those illnesses
            if len(healed_illnesses) != 0:
                # go through healed illness list one by one, in case they healed more than one this moon
                for illness in healed_illnesses:
                    # double check to make sure the cat WAS sick with that illness before trying to remove
                    if illness in cat.illnesses:
                        cat.illnesses.pop(illness)
                    # check if illness was a complication and erase if it was
                    if illness in ['an infected wound', 'a festering wound']:
                        # cat can only have one infection/fester at a time so just run through all illnesses
                        # and perm conditions to set all complication fields to None
                        for injury in cat.injuries:
                            keys = cat.injuries[injury].keys()
                            if 'complication' in keys:
                                cat.injuries[injury]['complication'] = None
                        for condition in cat.permanent_condition:
                            keys = cat.permanent_condition[condition].keys()
                            if 'complication' in keys:
                                cat.permanent_condition[condition]['complication'] = None

                # reset healed_condition value
                cat.healed_condition = False

        # joining event list into one event string
        event_string = None
        if len(event_list) > 0:
            event_string = ' '.join(event_list)

        # ---------------------------------------------------------------------------- #
        #                              make cats sick                                  #
        # ---------------------------------------------------------------------------- #
        chance_number = number_of_conditions * ratio
        random_number = int(random.random() * chance_number)
        if not cat.dead and not cat.is_ill() and random_number <= 10:
            season_dict = ILLNESSES_SEASON_LIST[season]
            possible_illnesses = []

            # pick up possible illnesses from the season dict
            for illness_name in season_dict:
                possible_illnesses += [illness_name] * season_dict[illness_name]

            # pick a random illness from those possible
            random_index = int(random.random() * len(possible_illnesses))
            chosen_illness = possible_illnesses[random_index]
            # if a non-kitten got kittencough, switch it to whitecough instead
            if chosen_illness == 'kittencough' and cat.status != 'kitten':
                chosen_illness = 'whitecough'
            # make em sick
            cat.get_ill(chosen_illness)

            # create event text
            if chosen_illness in ["running nose", "stomachache"]:
                event_string = f"{cat.name} has gotten a {chosen_illness}."
            else:
                event_string = f"{cat.name} has gotten {chosen_illness}."

        # if an event happened, then add event to cur_event_list and save death if it happened.
        if event_string:
            if cat.dead:
                if SAVE_DEATH:
                    save_death(cat, event_string)
                game.birth_death_events_list.append(event_string)
            game.cur_events_list.append(event_string)
            game.health_events_list.append(event_string)

        # just double-checking that trigger is only returned True if the cat is dead
        if cat.dead:
            triggered = True
        else:
            triggered = False

        return triggered

    def handle_injuries(self, cat, other_cat, alive_kits, war, enemy_clan, season):
        """ 
        This function handles overall the injuries in 'expanded' (or 'cruel season') game mode.
        Returns: boolean - if an event was triggered
        """
        has_other_clan = False

        random_number = int(random.random() * 150)
        triggered = False
        text = None

        if cat.dead:
            triggered = True
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
                    random_number <= 15:
                triggered = True
            elif not triggered and random_number <= 5:
                triggered = True

            if triggered:
                possible_events = self.generate_events.possible_injury_events(cat.status, cat.age)
                final_events = []

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
                    if "other_cat_adult" in event.tags and other_cat.age in ["elder", "kitten"]:
                        continue
                    if "other_cat_kit" in event.tags and other_cat.age != 'kitten':
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

                    if event.injury == 'mangled tail' and ('NOTAIL' in cat.scars or 'HALFTAIL' in cat.scars):
                        continue

                    if event.injury == 'torn ear' and 'NOEAR' in cat.scars:
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

                    if "other_clan" in injury_event.tags or "war" in injury_event.tags:
                        has_other_clan = True
                    if "war" in injury_event.tags:
                        other_clan_name = enemy_clan

                    #print('INJURY:', cat.name, cat.status, len(final_events), other_cat.name, other_cat.status)

                    # let's change some relationship values \o/ check if another cat is mentioned
                    if "other_cat" in injury_event.tags:
                        self.handle_relationship_changes(cat, injury_event, other_cat)

                    text = event_text_adjust(Cat, injury_event.event_text, cat, other_cat, other_clan_name)

                    # record proper history text possibilities
                    if injury_event.history_text is not None:
                        if injury_event.history_text[0] is not None:
                            history_text = event_text_adjust(Cat, injury_event.history_text[0], cat, other_cat,
                                                             other_clan_name, keep_m_c=True)
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

        # just double-checking that trigger is only returned True if the cat is dead
        if cat.dead:
            triggered = True
        else:
            triggered = False

        if text is not None:
            game.cur_events_list.append(text)
            game.health_events_list.append(text)
            if cat.dead:
                game.birth_death_events_list.append(text)
            if has_other_clan:
                game.other_clans_events_list.append(text)

        return triggered

    def handle_relationship_changes(self, cat, injury_event, other_cat):
        cat_to = None
        cat_from = None
        n = 10
        romantic = 0
        platonic = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0
        if "rc_to_mc" in injury_event.tags:
            cat_to = [cat.ID]
            cat_from = [other_cat]
        elif "mc_to_rc" in injury_event.tags:
            cat_to = [other_cat.ID]
            cat_from = [cat]
        elif "to_both" in injury_event.tags:
            cat_to = [cat.ID, other_cat.ID]
            cat_from = [other_cat, cat]
        if "romantic" in injury_event.tags:
            romantic = n
        elif "neg_romantic" in injury_event.tags:
            romantic = -n
        if "platonic" in injury_event.tags:
            platonic = n
        elif "neg_platonic" in injury_event.tags:
            platonic = -n
        if "dislike" in injury_event.tags:
            dislike = n
        elif "neg_dislike" in injury_event.tags:
            dislike = -n
        if "respect" in injury_event.tags:
            admiration = n
        elif "neg_respect" in injury_event.tags:
            admiration = -n
        if "comfort" in injury_event.tags:
            comfortable = n
        elif "neg_comfort" in injury_event.tags:
            comfortable = -n
        if "jealousy" in injury_event.tags:
            jealousy = n
        elif "neg_jealousy" in injury_event.tags:
            jealousy = -n
        if "trust" in injury_event.tags:
            trust = n
        elif "neg_trust" in injury_event.tags:
            trust = -n
        change_relationship_values(
            cat_to,
            cat_from,
            romantic,
            platonic,
            dislike,
            admiration,
            comfortable,
            jealousy,
            trust)

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
            "MANLEG": ["weak leg", "twisted leg"],
            "BRIGHTHEART": ["one bad eye"],
            "NOLEFTEAR": ["partial hearing loss"],
            "NORIGHTEAR": ["partial hearing loss"],
            "NOEAR": ["partial hearing loss, deaf"],
            "LEFTBLIND": ["one bad eye", "failing eyesight"],
            "RIGHTBLIND": ["one bad eye", "failing eyesight"],
            "BOTHBLIND": ["blind"],
            "RATBITE": ["weak leg"]
        }

        scarless_conditions = [
            "weak leg", "paralyzed", "raspy lungs", "wasting disease", "blind", "failing eyesight", "one bad eye",
            "partial hearing loss", "deaf", "constant joint pain", "constantly dizzy", "recurring shock",
            "lasting grief"
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
            got_condition = cat.get_permanent_condition(perm_condition, born_with)

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

        # need to hold this number so that we can check if the leader has died
        starting_life_count = game.clan.leader_lives
        clear_leader_conditions = False

        if game.clan.game_mode == "classic":
            return triggered

        if not triggered:
            for y in cat.injuries:
                injury = y
                skipped = cat.moon_skip_injury(injury)
                if skipped:
                    continue

                elif cat.status == 'leader' and starting_life_count != game.clan.leader_lives:
                    clear_leader_conditions = True
                    break

                if cat.dead:
                    triggered = True
                    # TODO: need to make death events for these so that we can have more variety

                    possible_string_list = INJURY_DEATH_STRINGS[injury]
                    event = random.choice(possible_string_list)
                    event = event_text_adjust(Cat, event, cat)
                    if cat.status == 'leader':
                        history_text = event.replace(cat.name, " ")
                        cat.died_by.append(history_text.strip())
                        event = event.replace('.', ', losing a life.')
                    else:
                        cat.died_by.append(event)

                    # clear event list first to make sure any heal or risk events from other injuries are not shown
                    event_list.clear()
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
                        # gather potential event strings for gotten condition
                        possible_string_list = INJURY_HEALED_STRINGS[injury]
                        random_index = int(random.random() * len(possible_string_list))
                        event = possible_string_list[random_index]
                        event = event_text_adjust(Cat, event, cat, other_cat=None)  # adjust the text

                    healed_injury.append(injury)
                    cat.healed_condition = False

                    # try to give a permanent condition based on healed injury and new scar if any
                    condition_got = self.handle_permanent_conditions(cat, injury_name=injury, scar=scar_given)

                    if condition_got is not None:
                        # gather potential event strings for gotten condition
                        possible_string_list = PERMANENT_CONDITION_GOT_STRINGS[injury][condition_got]

                        # choose event string and ensure clan's med cat number aligns with event text
                        random_index = int(random.random() * len(possible_string_list))
                        med_list = get_med_cats(Cat)
                        med_cat = None
                        if len(med_list) == 0:
                            if random_index == 0 or random_index == 1:
                                random_index = 2
                            else:
                                med_cat = None
                        else:
                            med_cat = random.choice(med_list)
                            if med_cat == cat:
                                random_index = 2
                        event = possible_string_list[random_index]
                        event = event_text_adjust(Cat, event, cat, other_cat=med_cat)  # adjust the text
                    if event is not None:
                        event_list.append(event)

                elif not triggered:
                    if injury in cat.injuries:
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
                                    complication = None
                                    if new_condition == 'an infected wound':
                                        complication = 'infected'
                                    elif new_condition == 'a festering wound':
                                        complication = 'festering'
                                    keys = cat.injuries[injury].keys()
                                    if 'complication' in keys:
                                        cat.injuries[injury]["complication"] = complication
                                    else:
                                        cat.injuries[injury].update({'complication': complication})
                                    # gather potential event strings for gotten condition
                                    possible_string_list = INJURY_RISK_STRINGS[injury][new_condition]

                                    # choose event string and ensure clan's med cat number aligns with event text
                                    random_index = int(random.random() * len(possible_string_list))
                                    med_list = get_med_cats(Cat)
                                    med_cat = None
                                    if len(med_list) == 0:
                                        if random_index == 0:
                                            random_index = 1
                                        else:
                                            med_cat = None
                                    else:
                                        med_cat = random.choice(med_list)
                                        if med_cat == cat:
                                            random_index = 1
                                    event = possible_string_list[random_index]
                                    event = event_text_adjust(Cat, event, cat, med_cat)  # adjust the text
                                    event_list.append(event)
                                    break
                    if new_condition is not None:
                        triggered = True
                        break

            if clear_leader_conditions is True or cat.dead:
                # reset leader after death
                cat.injuries.clear()
                cat.illnesses.clear()
                if new_condition is not None:
                    new_condition.clear()
                if healed_injury is not None:
                    healed_injury.clear()
                cat.healed_condition = False

            if len(healed_injury) != 0:
                for y in healed_injury:
                    if y in cat.injuries:
                        cat.injuries.pop(y)

        if new_condition in ILLNESSES:
            cat.get_ill(new_condition, event_triggered=True)
        elif new_condition in INJURIES:
            if new_condition == 'lingering shock':
                cat.injuries.pop('shock')
            cat.get_injured(new_condition)

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
                # gather potential event strings for gotten risk
                possible_string_list = CONGENITAL_CONDITION_GOT_STRINGS[condition]

                # choose event string and ensure clan's med cat number aligns with event text
                random_index = int(random.random() * len(possible_string_list))
                med_list = get_med_cats(Cat)
                med_cat = None
                if len(med_list) == 0:
                    if random_index == 0:
                        random_index = 1
                    else:
                        med_cat = None
                else:
                    med_cat = random.choice(med_list)
                    if med_cat == cat:
                        random_index = 1
                event = possible_string_list[random_index]
                event = event_text_adjust(Cat, event, cat, other_cat=med_cat)  # adjust the text
                event_list.append(event)
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
                            if len(med_list) == 0:
                                if random_index == 0:
                                    random_index = 1
                                else:
                                    med_cat = None
                            else:
                                med_cat = random.choice(med_list)
                                if med_cat == cat:
                                    random_index = 1
                            event = possible_string_list[random_index]
                            event = event_text_adjust(Cat, event, cat, other_cat=med_cat)  # adjust the text
                            event_list.append(event)
                            if new_ouchie in INJURIES:
                                cat.get_injured(new_ouchie, event_triggered=True)
                                break
                            elif new_ouchie in ILLNESSES:
                                cat.get_ill(new_ouchie, event_triggered=True)
                                keys = cat.permanent_condition[condition].keys()
                                complication = None
                                if new_ouchie == 'an infected wound':
                                    complication = 'infected'
                                elif new_ouchie == 'a festering wound':
                                    complication = 'festering'
                                if complication is not None:
                                    if 'complication' in keys:
                                        cat.permanent_condition[condition]['complication'] = complication
                                    else:
                                        cat.permanent_condition[condition].update({'complication': complication})
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
                    cat.get_permanent_condition(new_condition[y], event_triggered=True)

        retire_chances = {
            'kitten': 0,
            'adolescent': 100,
            'young adult': 80,
            'adult': 70,
            'senior adult': 50,
            'elder': 0
        }

        if not triggered and not cat.dead and not cat.retired and cat.status not in ['leader', 'medicine cat', 'kitten'] and game.settings['retirement'] is False:
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
            game.health_events_list.append(event_string)
            if cat.dead:
                game.birth_death_events_list.append(event_string)
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
with open(f"resources/dicts/conditions/healed_and_death_strings/illness_healed_strings.json", 'r') as read_file:
    ILLNESS_HEALED_STRINGS = ujson.loads(read_file.read())

INJURY_HEALED_STRINGS = None
with open(f"resources/dicts/conditions/healed_and_death_strings/injury_healed_strings.json", 'r') as read_file:
    INJURY_HEALED_STRINGS = ujson.loads(read_file.read())

INJURY_DEATH_STRINGS = None
with open(f"resources/dicts/conditions/healed_and_death_strings/injury_death_strings.json", 'r') as read_file:
    INJURY_DEATH_STRINGS = ujson.loads(read_file.read())
