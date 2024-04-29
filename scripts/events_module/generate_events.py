#!/usr/bin/env python3
# -*- coding: ascii -*-
import random

import ujson

from scripts.cat.cats import Cat
from scripts.clan_resources.freshkill import FRESHKILL_EVENT_ACTIVE, FRESHKILL_EVENT_TRIGGER_FACTOR
from scripts.game_structure.game_essentials import game
from scripts.utility import filter_relationship_type, get_cats_of_romantic_interest, get_living_clan_cat_count

resource_directory = "resources/dicts/events/"


# ---------------------------------------------------------------------------- #
#                Tagging Guidelines can be found at the bottom                 #
# ---------------------------------------------------------------------------- #

class GenerateEvents:
    loaded_events = {}

    INJURY_DISTRIBUTION = None
    with open(f"resources/dicts/conditions/event_injuries_distribution.json", 'r') as read_file:
        INJURY_DISTRIBUTION = ujson.loads(read_file.read())

    INJURIES = None
    with open(f"resources/dicts/conditions/injuries.json", 'r') as read_file:
        INJURIES = ujson.loads(read_file.read())

    @staticmethod
    def get_short_event_dicts(file_path):
        try:
            with open(
                    file_path,
                    "r",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"ERROR: Unable to load {file_path}.")
            return None

        return events

    @staticmethod
    def get_ongoing_event_dicts(file_path):
        events = None
        try:
            with open(
                    file_path,
                    "r",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"ERROR: Unable to load events from biome {file_path}.")

        return events

    @staticmethod
    def get_death_reaction_dicts(family_relation, rel_value):
        try:
            file_path = f"{resource_directory}/death/death_reactions/{family_relation}/{family_relation}_{rel_value}.json"
            with open(
                    file_path,
                    "r",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            events = None
            print(f"ERROR: Unable to load death reaction events for {family_relation}_{rel_value}.")
        return events

    @staticmethod
    def clear_loaded_events():
        GenerateEvents.loaded_events = {}

    @staticmethod
    def generate_short_events(event_triggered, cat_type, biome):

        if cat_type and not biome:
            file_path = f"{resource_directory}{event_triggered}/{cat_type}.json"
        elif not cat_type and biome:
            file_path = f"{resource_directory}{event_triggered}/{biome}.json"
        else:
            file_path = f"{resource_directory}{event_triggered}/{biome}/{cat_type}.json"

        if file_path in GenerateEvents.loaded_events:
            return GenerateEvents.loaded_events[file_path]
        else:
            events_dict = GenerateEvents.get_short_event_dicts(file_path)

            event_list = []
            if not events_dict:
                return event_list
            for event in events_dict:
                event_text = event["event_text"] if "event_text" in event else None
                if not event_text:
                    event_text = event["death_text"] if "death_text" in event else None

                if not event_text:
                    print(f"WARNING: some events resources which are used in generate_events. Have no 'event_text'.")
                event = ShortEvent(
                    event_id=event["event_id"] if "event_id" in event else "",
                    biome=event["biome"] if "biome" in event else ["any"],
                    camp=event["camp"] if "camp" in event else ["any"],
                    season=event["season"] if "season" in event else ["any"],
                    tags=event["tags"] if "tags" in event else [],
                    weight=event["weight"] if "weight" in event else 20,
                    event_text=event_text,
                    new_accessory=event["new_accessory"] if "new_accessory" in event else [],
                    m_c=event["m_c"] if "m_c" in event else {},
                    r_c=event["r_c"] if "r_c" in event else {},
                    new_cat=event["new_cat"] if "new_cat" in event else [],
                    injury=event["injury"] if "injury" in event else [],
                    relationships=event["relationships"] if "relationships" in event else [],
                    outsider=event["outsider"] if "outsider" in event else {},
                    other_clan=event["other_clan"] if "other_clan" in event else {}
                )
                event_list.append(event)

            # Add to loaded events.
            GenerateEvents.loaded_events[file_path] = event_list
            return event_list

    @staticmethod
    def generate_ongoing_events(event_type, biome, specific_event=None):

        file_path = f"resources/dicts/events/{event_type}/{biome}.json"

        if file_path in GenerateEvents.loaded_events:
            return GenerateEvents.loaded_events[file_path]
        else:
            events_dict = GenerateEvents.get_ongoing_event_dicts(file_path)

            if not specific_event:
                event_list = []
                for event in events_dict:
                    event = OngoingEvent(
                        event=event["event"],
                        camp=event["camp"],
                        season=event["season"],
                        tags=event["tags"],
                        priority=event["priority"],
                        duration=event["duration"],
                        current_duration=0,
                        rarity=event["rarity"],
                        trigger_events=event["trigger_events"],
                        progress_events=event["progress_events"],
                        conclusion_events=event["conclusion_events"],
                        secondary_disasters=event["secondary_disasters"],
                        collateral_damage=event["collateral_damage"]
                    )
                    event_list.append(event)
                return event_list
            else:
                event = None
                for event in events_dict:
                    if event["event"] != specific_event:
                        # print(event["event"], 'is not', specific_event)
                        continue
                    # print(event["event"], "is", specific_event)
                    event = OngoingEvent(
                        event=event["event"],
                        camp=event["camp"],
                        season=event["season"],
                        tags=event["tags"],
                        priority=event["priority"],
                        duration=event["duration"],
                        current_duration=0,
                        progress_events=event["progress_events"],
                        conclusion_events=event["conclusion_events"],
                        collateral_damage=event["collateral_damage"]
                    )
                    break
                return event

    @staticmethod
    def possible_short_events(cat_type=None, age=None, event_type=None):
        event_list = []
        biome = None

        excluded_from_general = []
        warrior_adjacent_ranks = []

        if event_type == 'death':
            warrior_adjacent_ranks.extend(["deputy", "apprentice"])
            excluded_from_general.extend(["kitten", "leader", "newborn"])
        elif event_type in ['injury', 'nutrition', 'misc_events', 'new_cat']:
            warrior_adjacent_ranks.extend(["deputy", "apprentice", "leader"])
            excluded_from_general.extend(["kitten", "leader", "newborn"])

        if cat_type in ["medicine cat", "medicine cat apprentice"]:
            cat_type = "medicine"
        elif cat_type in ["mediator", "mediator apprentice"]:
            cat_type = "mediator"

        # skip the rest of the loading if there is an unrecognised cat type
        if cat_type not in game.clan.CAT_TYPES:
            print(
                f"WARNING: unrecognised cat status {cat_type} in generate_events. Have you added it to CAT_TYPES in "
                f"clan.py?")

        elif game.clan.biome not in game.clan.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES "
                f"in clan.py?")

        # NUTRITION this needs biome to be None so is handled separately
        elif event_type == 'nutrition':
            event_list.extend(
                GenerateEvents.generate_short_events(event_type, cat_type, biome))

            if cat_type in warrior_adjacent_ranks:
                event_list.extend(
                    GenerateEvents.generate_short_events(event_type, "warrior", biome))

            if cat_type not in excluded_from_general:
                event_list.extend(
                    GenerateEvents.generate_short_events(event_type, "general", biome))

        else:
            biome = game.clan.biome.lower()

            # RANK SPECIFIC
            # biome specific rank specific events
            event_list.extend(
                GenerateEvents.generate_short_events(event_type, cat_type, biome))

            # any biome rank specific events
            event_list.extend(
                GenerateEvents.generate_short_events(event_type, cat_type, "general"))

            # WARRIOR-LIKE
            if cat_type in warrior_adjacent_ranks:
                # biome specific warrior events for "warrior-like" ranks
                event_list.extend(
                    GenerateEvents.generate_short_events(event_type, "warrior", biome))

                # any biome warrior events for "warrior-like" ranks
                event_list.extend(
                    GenerateEvents.generate_short_events(event_type, "warrior", "general"))

            # GENERAL
            if cat_type not in excluded_from_general:
                # biome specific general rank events
                event_list.extend(
                    GenerateEvents.generate_short_events(event_type, "general", biome))

                # any biome general rank events
                event_list.extend(
                    GenerateEvents.generate_short_events(event_type, "general", "general"))

        return event_list

    @staticmethod
    def filter_possible_short_events(possible_events, cat, other_cat, war, enemy_clan, other_clan, alive_kits,
                                     murder=False, murder_reveal=False):
        final_events = []

        minor = []
        major = []
        severe = []

        # Chance to bypass the skill or trait requirements. 
        trait_skill_bypass = 15

        if war and random.randint(1, 10) != 1 and other_clan == enemy_clan:
            war_event = True
        else:
            war_event = False

        for event in possible_events:

            # check biome
            if game.clan.biome.lower() not in event.biome and "any" not in event.biome:
                continue
            # check camp
            if game.clan.camp_bg.lower() not in event.camp and "any" not in event.camp:
                continue
            # check season
            if game.clan.current_season.lower() not in event.season and "any" not in event.season:
                continue

            # check tags
            prevent_bypass = "skill_trait_required" in event.tags

            # ensure that war events only happen during war
            if war_event and ("war" not in event.tags and "hostile" not in event.other_clan["current_rep"]):
                continue
            if not war and "war" in event.tags:
                continue

            # some events are classic only
            if game.clan.game_mode in ["expanded", "cruel season"] and "classic" in event.tags:
                continue
            # cruel season only events
            if game.clan.game_mode in ["classic", "expanded"] and "cruel_season" in event.tags:
                continue

            # ensure murder only happens when meant to
            if murder and "murder" not in event.tags:
                continue
            if not murder and "murder" in event.tags:
                continue
            # ensure reveal only happens when meant to
            if murder_reveal and "murder_reveal" not in event.tags:
                continue
            if not murder_reveal and "murder_reveal" in event.tags:
                continue

            # make complete leader death less likely until the leader is over 150 moons
            if "all_lives" in event.tags:
                if int(cat.moons) < 150 and int(random.random() * 5):
                    continue

            # make sure that 'some lives' events don't show up if the leader doesn't have multiple lives to spare
            if "some_lives" in event.tags and game.clan.leader_lives <= 3:
                continue

            if "low_lives" in event.tags:
                if game.clan.leader_lives > 3:
                    continue

            # check if Clan has kits
            if "clan_kits" in event.tags and not alive_kits:
                continue

            # If the cat or any of their mates have "no kits" toggled, forgo the adoption event.
            if "adoption" in event.tags:
                if cat.no_kits:
                    continue
                if any(cat.fetch_cat(i).no_kits for i in cat.mate):
                    continue

            # check for old age
            if "old_age" in event.tags and cat.moons < game.config["death_related"]["old_age_death_start"]:
                continue
            # remove some non-old age events to encourage elders to die of old age more often
            if "old_age" not in event.tags and cat.moons > game.config["death_related"]["old_age_death_start"] \
                    and int(random.random() * 3):
                continue

            # if the event is marked as changing romantic interest, check that the cats are allowed to be romantic
            if "romance" in event.tags and other_cat.is_potential_mate(cat):
                continue

            if event.m_c:
                if cat.age not in event.m_c["age"]:
                    continue
                if cat.status not in event.m_c["status"]:
                    continue
                if event.m_c["relationship_status"]:
                    if not filter_relationship_type(group=[cat, other_cat],
                                                    filter_types=event.m_c["relationship_status"],
                                                    event_id=event.event_id):
                        continue

                # check cat trait and skill
                has_trait = False
                if event.m_c["trait"]:
                    if cat.personality.trait in event.m_c["trait"]:
                        has_trait = True

                has_skill = False
                if event.m_c["skill"]:
                    for _skill in event.m_c["skill"]:
                        split = _skill.split(",")

                        if len(split) < 2:
                            print("Cat skill incorrectly formatted", _skill)
                            continue

                        if cat.skills.meets_skill_requirement(split[0], int(split[1])):
                            has_skill = True
                            break

                if event.m_c["trait"] and event.m_c["skill"]:
                    if not (has_trait or has_skill) and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue
                elif event.m_c["trait"]:
                    if not has_trait and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue
                elif event.m_c["skill"]:
                    if not has_skill and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue

                # check cat negate trait and skill
                has_trait = False
                if event.m_c["not_trait"]:
                    if cat.personality.trait in event.m_c["not_trait"]:
                        has_trait = True

                has_skill = False
                if event.m_c["not_skill"]:
                    for _skill in event.m_c["not_skill"]:
                        split = _skill.split(",")

                        if len(split) < 2:
                            print("Cat skill incorrectly formatted", _skill)
                            continue

                        if cat.skills.meets_skill_requirement(split[0], int(split[1])):
                            has_skill = True
                            break

                # There is a small chance to bypass the skill or trait requirements.
                if (has_trait or has_skill) and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                    continue

                # check backstory
                if cat.backstory not in event.m_c["backstory"]:
                    continue

            # check that an other_cat is available to use for r_c
            if event.r_c and other_cat:
                if other_cat.age not in event.r_c["age"]:
                    continue
                if other_cat.status not in event.r_c["status"]:
                    continue
                if event.r_c["relationship_status"]:
                    if not filter_relationship_type(group=[cat, other_cat],
                                                    filter_types=event.r_c["relationship_status"],
                                                    event_id=event.event_id):
                        continue

                # check other_cat trait and skill
                has_trait = False
                if event.r_c["trait"]:
                    if other_cat.personality.trait in event.r_c["trait"]:
                        has_trait = True

                has_skill = False
                if event.r_c["skill"]:
                    for _skill in event.r_c["skill"]:
                        split = _skill.split(",")

                        if len(split) < 2:
                            print("other_cat skill incorrectly formatted", _skill)
                            continue

                        if other_cat.skills.meets_skill_requirement(split[0], int(split[1])):
                            has_skill = True
                            break

                if event.r_c["trait"] and event.r_c["skill"]:
                    if not (has_trait or has_skill) and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue
                elif event.r_c["trait"]:
                    if not has_trait and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue
                elif event.r_c["skill"]:
                    if not has_skill and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue

                # check other_cat negate trait and skill
                has_trait = False
                if event.r_c["not_trait"]:
                    if other_cat.personality.trait in event.r_c["not_trait"]:
                        has_trait = True

                has_skill = False
                if event.r_c["not_skill"]:
                    for _skill in event.r_c["not_skill"]:
                        split = _skill.split(",")

                        if len(split) < 2:
                            print("other_cat skill incorrectly formatted", _skill)
                            continue

                        if other_cat.skills.meets_skill_requirement(split[0], int(split[1])):
                            has_skill = True
                            break

                # There is a small chance to bypass the skill or trait requirements.
                if (has_trait or has_skill) and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                    continue

                # check backstory
                if other_cat.backstory not in event.r_c["backstory"]:
                    continue
            else:
                continue

            # check that injury is possible
            if event.injury:
                for injury in event.injury["injuries"]:
                    if injury in GenerateEvents.INJURIES:
                        if injury == 'mangled tail' and (
                                'NOTAIL' in cat.pelt.scars or 'HALFTAIL' in cat.pelt.scars):
                            continue

                        if injury == 'torn ear' and 'NOEAR' in cat.pelt.scars:
                            continue

            # check if outsider event is allowed
            if event.outsider:
                # don't waste time checking rep if any rep is allowed
                if "any" in event.outsider["current_rep"]:
                    pass
                # hostile
                elif 1 <= game.clan.reputation <= 30 and "hostile" not in event.outsider["current_rep"]:
                    continue
                # neutral
                elif 31 <= game.clan.reputation <= 70 and "neutral" not in event.outsider["current_rep"]:
                    continue
                # welcoming
                elif 71 <= game.clan.reputation <= 100 and "welcoming" not in event.outsider["current_rep"]:
                    continue

            # other Clan related checks
            if event.other_clan:
                if "war" in event.tags and not war:  # just double-checking
                    continue

                # don't waste time checking rep if any rep is allowed
                if "any" in event.other_clan["current_rep"]:
                    pass
                # ally
                elif "ally" in event.other_clan["current_rep"] and int(other_clan.relations) < 17:
                    continue
                # neutral
                elif "neutral" in event.other_clan["current_rep"] and (
                        int(other_clan.relations) <= 7 or int(other_clan.relations) >= 17):
                    continue
                # hostile
                elif "hostile" in event.other_clan["current_rep"] and int(other_clan.relations) > 7:
                    continue

            if event.supplies:
                # TODO: freshkill events were previously locked out until clan 5 moons old, should we keep that?
                clan_size = get_living_clan_cat_count(Cat)
                for supply in event.supplies:
                    if supply["type"] == "freshkill":
                        # classic mode doesn't do freshkill
                        # TODO: consider if events could still be allowed as "flavor" rather than actual supply changes
                        if game.clan.game_mode == "classic":
                            continue

                        discard = True
                        pile = game.clan.freshkill_pile
                        needed_amount = pile.amount_food_needed()
                        if not FRESHKILL_EVENT_ACTIVE:
                            continue

                        # "low" means total_amount must be less than half what is needed
                        if "low" in supply["trigger"]:
                            if needed_amount / 2 > pile.total_amount:
                                discard = False

                        # "adequate" means total_amount must be greater than half needed,
                        # but not greater than 1 moons worth of food
                        if "adequate" in supply["trigger"]:
                            if needed_amount / 2 < pile.total_amount < needed_amount:
                                discard = False

                        # now do the math to find how much is too much prey
                        trigger_factor = FRESHKILL_EVENT_TRIGGER_FACTOR
                        divider = 35 if game.clan.game_mode == "expanded" else 20
                        trigger_factor = trigger_factor - round(pow((clan_size / divider), 2))
                        if trigger_factor < 2 and game.clan.game_mode == "expanded":
                            trigger_factor = 2
                        if trigger_factor < 1.2 and game.clan.game_mode == "cruel season":
                            trigger_factor = 1.2

                        trigger_value = round(trigger_factor * needed_amount, 2)
                        print(
                            f" -- FRESHKILL: trigger amount {trigger_value}. current amount (after feed, before moon gathering) {pile.total_amount}")

                        # "full" means total_amount is enough for 1 moons worth, but is not over the multiplier
                        if "full" in supply["trigger"]:
                            # check this quick to see if we can skip the math
                            if needed_amount < pile.total_amount < trigger_value:
                                discard = False

                        # "excess" means total_amount is over the multiplier and there's too much food!
                        if "excess" in supply["trigger"]:
                            if pile.total_amount > trigger_value:
                                discard = False

                        if discard:
                            continue

                    # TODO: figure out how to make this function for herbs

        return final_events

    @staticmethod
    def possible_ongoing_events(event_type=None, specific_event=None):
        event_list = []

        if game.clan.biome not in game.clan.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES in clan.py?")

        else:
            biome = game.clan.biome.lower()
            if not specific_event:
                event_list.extend(
                    GenerateEvents.generate_ongoing_events(event_type, biome)
                )
                """event_list.extend(
                    GenerateEvents.generate_ongoing_events(event_type, "general", specific_event)
                )"""
                return event_list
            else:
                # print(specific_event)
                event = (
                    GenerateEvents.generate_ongoing_events(event_type, biome, specific_event)
                )
                return event

    @staticmethod
    def possible_death_reactions(family_relation, rel_value, trait, body_status):
        possible_events = []
        # grab general events first, since they'll always exist
        events = GenerateEvents.get_death_reaction_dicts("general", rel_value)
        possible_events.extend(events["general"][body_status])
        if trait in events:
            possible_events.extend(events[trait][body_status])

        # grab family events if they're needed. Family events should not be romantic. 
        if family_relation != 'general' and rel_value != "romantic":
            events = GenerateEvents.get_death_reaction_dicts(family_relation, rel_value)
            possible_events.extend(events["general"][body_status])
            if trait in events:
                possible_events.extend(events[trait][body_status])

        # print(possible_events)

        return possible_events


class ShortEvent:
    """
    A moon event that only affects the moon it was triggered on.  Can involve two cats directly and be restricted by various constraints.
    - full documentation available on github wiki
    """

    def __init__(
            self,
            event_id="",
            biome=None,
            camp=None,
            season=None,
            tags=None,
            weight=0,
            event_text="",
            new_accessory=None,
            m_c=None,
            r_c=None,
            new_cat=None,
            injury=None,
            relationships=None,
            outsider=None,
            other_clan=None,
            supplies=None
    ):
        if not event_id:
            print("WARNING: moon event has no event_id")
        self.event_id = event_id
        self.biome = biome if biome else ["any"]
        self.camp = camp if camp else ["any"]
        self.season = season if season else ["any"]
        self.tags = tags if tags else []
        self.weight = weight
        self.event_text = event_text
        self.new_accessory = new_accessory
        self.m_c = m_c if m_c else {}
        if self.m_c:
            if "age" not in self.m_c:
                self.m_c["age"] = []
            if "status" not in self.m_c:
                self.m_c["status"] = []
            if "relationship_status" not in self.m_c:
                self.m_c["relationship_status"] = []
            if "skill" not in self.m_c:
                self.m_c["skill"] = []
            if "not_skill" not in self.m_c:
                self.m_c["not_skill"] = []
            if "not_trait" not in self.m_c:
                self.m_c["not_trait"] = []
            if "age" not in self.m_c:
                self.m_c["age"] = []
            if "backstory" not in self.m_c:
                self.m_c["backstory"] = []
            if "dies" not in self.m_c:
                self.m_c["dies"] = False

        self.r_c = r_c if r_c else {}
        if self.r_c:
            if "age" not in self.r_c:
                self.r_c["age"] = []
            if "status" not in self.r_c:
                self.r_c["status"] = []
            if "relationship_status" not in self.r_c:
                self.r_c["relationship_status"] = []
            if "skill" not in self.r_c:
                self.r_c["skill"] = []
            if "not_skill" not in self.r_c:
                self.r_c["not_skill"] = []
            if "not_trait" not in self.r_c:
                self.r_c["not_trait"] = []
            if "age" not in self.r_c:
                self.r_c["age"] = []
            if "backstory" not in self.r_c:
                self.r_c["backstory"] = []
            if "dies" not in self.r_c:
                self.r_c["dies"] = False

        self.new_cat = new_cat if new_cat else []
        self.injury = injury if injury else []
        self.relationships = relationships if relationships else []
        self.outsider = outsider if outsider else {}
        if self.outsider:
            if "current_rep" not in self.outsider:
                self.outsider["current_rep"] = []
            if "changed" not in self.outsider:
                self.outsider["changed"] = 0
        self.other_clan = other_clan if other_clan else {}
        if self.other_clan:
            if "current_rep" not in self.other_clan:
                self.other_clan["current_rep"] = []
            if "changed" not in self.other_clan:
                self.other_clan["changed"] = 0
        self.supplies = supplies if supplies else []


class OngoingEvent:
    def __init__(self,
                 event=None,
                 camp=None,
                 season=None,
                 tags=None,
                 priority='secondary',
                 duration=None,
                 current_duration=0,
                 rarity=0,
                 trigger_events=None,
                 progress_events=None,
                 conclusion_events=None,
                 secondary_disasters=None,
                 collateral_damage=None
                 ):
        self.event = event
        self.camp = camp
        self.season = season
        self.tags = tags
        self.priority = priority
        self.duration = duration
        self.current_duration = current_duration
        self.rarity = rarity
        self.trigger_events = trigger_events
        self.progress_events = progress_events
        self.conclusion_events = conclusion_events
        self.secondary_disasters = secondary_disasters
        self.collateral_damage = collateral_damage
