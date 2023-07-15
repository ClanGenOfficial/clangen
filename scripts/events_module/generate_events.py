#!/usr/bin/env python3
# -*- coding: ascii -*-
import random

import ujson
from scripts.game_structure.game_essentials import game

resource_directory = "resources/dicts/events/"


# ---------------------------------------------------------------------------- #
#                Tagging Guidelines can be found at the bottom                 #
# ---------------------------------------------------------------------------- #

class GenerateEvents:
    loaded_events = {}

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

    def generate_short_events(self, event_triggered, cat_type, biome):

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
                    camp=event["camp"] if "camp" in event else "any",
                    tags=event["tags"],
                    event_text=event_text,
                    history_text=event["history_text"] if "history_text" in event else {},
                    cat_trait= event["cat_trait"] if "cat_trait" in event else [],
                    cat_skill=event["cat_skill"] if "cat_skill" in event else [],
                    other_cat_trait=event["other_cat_trait"] if "other_cat_trait" in event else [],
                    other_cat_skill=event["other_cat_skill"] if "other_cat_skill" in event else [],
                    cat_negate_trait=event["cat_negate_trait"] if "cat_negate_trait" in event else [],
                    cat_negate_skill=event["cat_negate_skill"] if "cat_negate_skill" in event else [],
                    other_cat_negate_trait=event[
                        "other_cat_negate_trait"] if "other_cat_negate_trait" in event else [],
                    other_cat_negate_skill=event[
                        "other_cat_negate_skill"] if "other_cat_negate_skill" in event else [],
                    backstory_constraint=event["backstory_constraint"] if "backstory_constraint" in event else [],

                    # injury event only
                    injury=event["injury"] if "injury" in event else None,

                    # new cat event only
                    loner=event["loner"] if "loner" in event else False,
                    kittypet=event["kittypet"] if "kittypet" in event else False,
                    other_clan=event["other_clan"] if "other_clan" in event else False,
                    kit=event["kit"] if "kit" in event else False,
                    new_name=event["new_name"] if "new_name" in event else False,
                    litter=event["litter"] if "litter" in event else False,
                    backstory=event["backstory"] if "backstory" in event else None,
                    reputation=event["reputation"] if "reputation" in event else None,

                    # for misc events only
                    accessories=event["accessories"] if "accessories" in event else None
                )
                event_list.append(event)

            # Add to loaded events.
            GenerateEvents.loaded_events[file_path] = event_list
            return event_list

    def generate_ongoing_events(self, event_type, biome, specific_event=None):

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
                        #print(event["event"], 'is not', specific_event)
                        continue
                    #print(event["event"], "is", specific_event)
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

    def possible_short_events(self, cat_type=None, age=None, event_type=None):
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
                self.generate_short_events(event_type, cat_type, biome))

            if cat_type in warrior_adjacent_ranks:
                event_list.extend(
                    self.generate_short_events(event_type, "warrior", biome))

            if cat_type not in excluded_from_general:
                event_list.extend(
                    self.generate_short_events(event_type, "general", biome))

        else:
            biome = game.clan.biome.lower()

            # RANK SPECIFIC
            # biome specific rank specific events
            event_list.extend(
                self.generate_short_events(event_type, cat_type, biome))

            # any biome rank specific events
            event_list.extend(
                self.generate_short_events(event_type, cat_type, "general"))

            # WARRIOR-LIKE
            if cat_type in warrior_adjacent_ranks:
                # biome specific warrior events for "warrior-like" ranks
                event_list.extend(
                    self.generate_short_events(event_type, "warrior", biome))

                # any biome warrior events for "warrior-like" ranks
                event_list.extend(
                    self.generate_short_events(event_type, "warrior", "general"))

            # GENERAL
            if cat_type not in excluded_from_general:
                # biome specific general rank events
                event_list.extend(
                    self.generate_short_events(event_type, "general", biome))

                # any biome general rank events
                event_list.extend(
                    self.generate_short_events(event_type, "general", "general"))

        return event_list

    def filter_possible_short_events(self, possible_events, cat, other_cat, war, enemy_clan, other_clan, alive_kits, murder=False, murder_reveal=False):
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
            
            # Normally, there is a chance to bypass skill and trait requirments. 
            # the "skill_trait_required" tags turns this off. Lets grab this tag once, for simplicity. 
            prevent_bypass = "skill_trait_required" in event.tags
            
            if war_event and ("war" not in event.tags and "hostile" not in event.tags):
                continue
            if not war and "war" in event.tags:
                continue

            # some events are classic only
            if game.clan.game_mode in ["expanded", "cruel season"] and "classic" in event.tags:
                continue

            if "other_cat" in event.tags and not other_cat:
                continue

            if event.backstory_constraint and cat.backstory not in event.backstory_constraint:
                continue

            if murder and "murder" not in event.tags:
                continue
            if not murder and "murder" in event.tags:
                continue

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

            # check season
            if game.clan.current_season not in event.tags:
                continue

            if event.reputation:
                reputation = game.clan.reputation
                # hostile
                if 1 <= reputation <= 30 and "hostile" not in event.reputation:
                    continue
                # neutral
                elif 31 <= reputation <= 70 and "neutral" not in event.reputation:
                    continue
                # welcoming
                elif 71 <= reputation <= 100 and "welcoming" not in event.reputation:
                    continue

            # check that injury is possible
            if event.injury in INJURIES:

                if event.injury == 'mangled tail' and ('NOTAIL' in cat.pelt.scars or 'HALFTAIL' in cat.pelt.scars):
                    continue

                if event.injury == 'torn ear' and 'NOEAR' in cat.pelt.scars:
                    continue

            # check meddie tags
            if "medicine_cat" in event.tags and cat.status != "medicine cat":
                continue
            elif "medicine_cat_app" in event.tags and cat.status != "medicine cat apprentice":
                continue

            # other Clan related checks
            if "other_clan" in event.tags:
                if "war" in event.tags and not war:
                    continue
                if "ally" in event.tags and int(other_clan.relations) < 17:
                    continue
                elif "neutral" in event.tags and (int(other_clan.relations) <= 7 or int(other_clan.relations) >= 17):
                    continue
                elif "hostile" in event.tags and int(other_clan.relations) > 7:
                    continue

            # check if Clan has kits
            if "clan_kits" in event.tags and not alive_kits:
                continue
            
            if "adoption" in event.tags:
                # If the cat or any of their mates have "no kits" toggled, forgo the adoption event.
                if cat.no_kits:
                    continue
                if any(cat.fetch_cat(i).no_kits for i in cat.mate):
                    continue
            
            # check for old age
            if "old_age" in event.tags and cat.moons < 150:
                continue
            # remove some non-old age events to encourage elders to die of old age more often
            if "old_age" not in event.tags and cat.moons > 150:
                if not int(random.random() * 2):
                    continue

            # check other_cat status and other identifiers
            if other_cat:
                if "other_cat_leader" in event.tags and other_cat.status != "leader":
                    continue
                if "other_cat_dep" in event.tags and other_cat.status != "deputy":
                    continue
                if "other_cat_med" in event.tags and other_cat.status != "medicine cat":
                    continue
                if "other_cat_med_app" in event.tags and other_cat.status != "medicine cat apprentice":
                    continue
                if "other_cat_warrior" in event.tags and other_cat.status != "warrior":
                    continue
                if "other_cat_app" in event.tags and other_cat.status != "apprentice":
                    continue
                if "other_cat_elder" in event.tags and other_cat.status != "elder":
                    continue
                if "other_cat_adult" in event.tags and other_cat.age in ["elder", "kitten", "newborn"]:
                    continue
                if "other_cat_kit" in event.tags and other_cat.status not in ['newborn', 'kitten']:
                    continue

                if "other_cat_mate" in event.tags and other_cat.ID not in cat.mate:
                    continue
                if "other_cat_child" in event.tags and other_cat.ID not in cat.get_children():
                    continue
                if "other_cat_parent" in event.tags and other_cat.ID not in cat.get_parents():
                    continue

                if "other_cat_own_app" in event.tags and other_cat.ID not in cat.apprentice:
                    continue
                if "other_cat_mentor" in event.tags and other_cat.ID != cat.mentor:
                    continue
                
                # check other cat trait and skill
                has_trait = False
                if event.other_cat_trait:
                    if other_cat.personality.trait in event.other_cat_trait:
                        has_trait = True
                
                has_skill = False
                if event.other_cat_skill:
                    for _skill in event.other_cat_skill:
                        split = _skill.split(",")
                        
                        if len(split) < 2:
                            print("Cat skill incorrectly formatted", _skill)
                            continue
                        
                        if other_cat.skills.meets_skill_requirement(split[0], int(split[1])):
                            has_skill = True
                            break
                    
                # There is a small chance to bypass the skill or trait requirments.  
                if event.other_cat_trait and event.other_cat_skill:
                    if not (has_trait or has_skill) and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue
                elif event.other_cat_trait:
                    if not has_trait and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue
                elif event.other_cat_skill:
                    if not has_skill and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                        continue
                
                
                # check cat negate trait and skill
                has_trait = False
                if event.other_cat_negate_trait:
                    if other_cat.personality.trait in event.other_cat_negate_trait:
                        has_trait = True
                
                has_skill = False
                if event.other_cat_negate_trait:
                    for _skill in event.other_cat_negate_trait:
                        split = _skill.split(",")
                        
                        if len(split) < 2:
                            print("Cat skill incorrectly formatted", _skill)
                            continue
                        
                        if other_cat.skills.meets_skill_requirement(split[0], int(split[1])):
                            has_skill = True
                            break
                    
                # There is a small chance to bypass the skill or trait requirments.  
                if (has_trait or has_skill) and int(random.random() * trait_skill_bypass):
                    continue

            else:
                if "other_cat" in event.tags or "multi_death" in event.tags:
                    continue

            # check for mate if the event requires one
            if "mate" in event.tags and len(cat.mate) < 1:
                continue


            # check cat trait and skill
            has_trait = False
            if event.cat_trait:
                if cat.personality.trait in event.cat_trait:
                    has_trait = True
            else:
                has_trait = None
            
            has_skill = False
            if event.cat_skill:
                for _skill in event.cat_skill:
                    split = _skill.split(",")
                    
                    if len(split) < 2:
                        print("Cat skill incorrectly formatted", _skill)
                        continue
                    
                    if cat.skills.meets_skill_requirement(split[0], int(split[1])):
                        has_skill = True
                        break
            
            # There is a small chance to bypass the skill or trait requirments.  
            if event.cat_trait and event.cat_skill:
                if not (has_trait or has_skill) and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                    continue
            elif event.cat_trait:
                if not has_trait and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                    continue
            elif event.cat_skill:
                if not has_skill and (prevent_bypass or int(random.random() * trait_skill_bypass)):
                    continue
            
            
            # check cat negate trait and skill
            has_trait = False
            if event.cat_negate_trait:
                if cat.personality.trait in event.cat_negate_trait:
                    has_trait = True
            
            has_skill = False
            if event.cat_negate_skill:
                for _skill in event.cat_negate_skill:
                    split = _skill.split(",")
                    
                    if len(split) < 2:
                        print("Cat skill incorrectly formatted", _skill)
                        continue
                    
                    if cat.skills.meets_skill_requirement(split[0], int(split[1])):
                        has_skill = True
                        break
                
            # There is a small chance to bypass the skill or trait requirments.  
            if (has_trait or has_skill) and int(random.random() * trait_skill_bypass):
                continue

            # determine injury severity chance
            if event.injury:
                injury = INJURIES[event.injury]
                severity = injury['severity']

                if severity == 'minor':
                    minor.append(event)
                elif severity == 'major':
                    major.append(event)
                else:
                    severe.append(event)

            else:
                final_events.append(event)

        # determine which injury severity list will be used
        if minor or major or severe:
            if cat.status in INJURY_DISTRIBUTION:
                minor_chance = INJURY_DISTRIBUTION[cat.status]['minor']
                major_chance = INJURY_DISTRIBUTION[cat.status]['major']
                severe_chance = INJURY_DISTRIBUTION[cat.status]['severe']
                severity_chosen = random.choices(["minor", "major", "severe"], [minor_chance, major_chance, severe_chance], k=1)
                if severity_chosen[0] == 'minor':
                    final_events = minor
                elif severity_chosen[0] == 'major':
                    final_events = major
                else:
                    final_events = severe

        return final_events

    def possible_ongoing_events(self, event_type=None, specific_event=None):
        event_list = []

        if game.clan.biome not in game.clan.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES in clan.py?")

        else:
            biome = game.clan.biome.lower()
            if not specific_event:
                event_list.extend(
                    self.generate_ongoing_events(event_type, biome)
                )
                """event_list.extend(
                    self.generate_ongoing_events(event_type, "general", specific_event)
                )"""
                return event_list
            else:
                #print(specific_event)
                event = (
                    self.generate_ongoing_events(event_type, biome, specific_event)
                )
                return event

    def possible_death_reactions(self, family_relation, rel_value, trait, body_status):
        possible_events = []
        # grab general events first, since they'll always exist
        events = self.get_death_reaction_dicts("general", rel_value)
        possible_events.extend(events["general"][body_status])
        if trait in events:
            possible_events.extend(events[trait][body_status])

        # grab family events if they're needed
        if family_relation != 'general':
            events = self.get_death_reaction_dicts(family_relation, rel_value)
            possible_events.extend(events["general"][body_status])
            if trait in events:
                possible_events.extend(events[trait][body_status])

        # print(possible_events)

        return possible_events


class ShortEvent:
    def __init__(
            self,
            camp="any",
            tags=None,
            event_text="",
            history_text=None,
            cat_trait=None,
            cat_skill=None,
            other_cat_trait=None,
            other_cat_skill=None,
            cat_negate_trait=None,
            cat_negate_skill=None,
            other_cat_negate_trait=None,
            other_cat_negate_skill=None,
            backstory_constraint=None,
            injury=None,
            loner=False,
            new_name=False,
            kittypet=False,
            kit=False,
            litter=False,
            backstory=None,
            other_clan=None,
            reputation=None,
            accessories=None
    ):
        self.camp = camp
        self.tags = tags
        self.event_text = event_text
        self.history_text = history_text
        self.cat_trait = cat_trait if cat_trait else []
        self.cat_skill = cat_skill if cat_skill else []
        self.other_cat_trait = other_cat_trait if other_cat_trait else []
        self.other_cat_skill = other_cat_skill if other_cat_skill else []
        self.cat_negate_trait = cat_negate_trait if cat_negate_trait else []
        self.cat_negate_skill = cat_negate_skill if cat_negate_skill else []
        self.other_cat_negate_trait = other_cat_negate_trait if other_cat_negate_trait else []
        self.other_cat_negate_skill = other_cat_negate_skill if other_cat_negate_skill else []
        self.backstory_constraint = backstory_constraint

        # for injury event
        self.injury = injury

        # for new cat events
        self.loner = loner
        self.new_name = new_name
        self.kittypet = kittypet
        self.kit = kit
        self.litter = litter
        self.backstory = backstory
        self.other_clan = other_clan
        self.reputation = reputation

        # for misc events
        self.accessories = accessories


"""
Tagging Guidelines: (if you add more tags, please add guidelines for them here) 
"Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare" < specify season.  If event happens in all seasons then include all of those tags.

"classic" < use for death events caused by illness.  This tag ensures that illness death events only happen in classic mode since illness deaths are caused differently in enhanced/cruel mode

"multi_death" < use to indicate that two cats have died.  Two cats is the limit here.  Any more than that is a disaster death and i haven't touched disasters yet (and might not touch at all bc the code is scary lol)

"old_age" < use to mark deaths caused by old age

"all_lives" < take all the lives from a leader
"some_lives" < take a random number, but not all, lives from a leader
"low_lives" < only allow event if the leader is low on lives

"murder" < m_c was murdered by the other cat

"war" < event only happens during war and ensures o_c in event is warring clan
"other_clan" < mark event as including another clan
"rel_down" < event decreases relation with other clan
"rel_up" < event increases relation with other clan
"hostile" < event only happens with hostile clans
"neutral" < event only happens with neutral clans
"ally" < event only happens with allied clans

"medicine_cat", "medicine_cat_app" < ensure that m_c is one of these ranks.  All other ranks are separated into their own .jsons

"other_cat" < there is a second cat in this event

"other_cat_med", "other_cat_med_app", "other_cat_warrior", "other_cat_app", "other_cat_kit", "other_cat_lead", "other_cat_dep", "other_cat_elder" < mark the other cat as having to be a certain status, if none of these tags are used then other_cat can be anyone

"other_cat_mate" < mark the other cat as having to be the m_c's mate
"other_cat_child" < mark the other cat as having to be the m_c's kit
"other_cat_parent" < mark the other cat as having to be m_c's parent
"other_cat_adult" < mark the other cat as not being able to be a kit or elder

"other_cat_own_app", "other_cat_mentor" < mark the other cat has having to be the m_c's mentor or app respectively

"clan_kits" < Clan must have kits for this event to appear

**Relationship tags do not work for New Cat events**
mc_to_rc < change mc's relationship values towards rc
rc_to_mc < change rc's relationship values towards mc
to_both < change both cat's relationship values

Tagged relationship parameters are: "romantic", "platonic", "comfort", "respect", "trust", "dislike", "jealousy", 
Add "neg_" in front of parameter to make it a negative value change (i.e. "neg_romantic", "neg_platonic", ect)


Following tags are used for new cat events:
"parent" < this litter or kit also comes with a parent (this does not include adoptive parents from within the clan)
"m_c" < the event text includes the main cat, not just the new cat
"other_cat" < the event text includes the other cat, not just the new cat and main cat
"new_warrior", "new_apprentice", "new_medicine cat apprentice", "new_medicine cat" < make the new cat start with the tagged for status
"injured" < tag along with a second tag that's the name of the injury you want the new_cat to have
"major_injury" < tag to give the new cat a random major-severity injury

Following tags are used for nutrition events:
"death" < main cat will die
"malnourished" < main cat will get the illness malnourished
"starving" < main cat will get the illness starving
"malnourished_healed" < main cat will be healed from malnourished
"starving_healed" < main cat will be healed from starving

Following tags are used for freshkill pile events:
"death" < main cat will die
"multi_death" < as described above
"injury" < main cat get injured
"multi_injury" < use to indicate that two cats get injured.
"much_prey" < this event will be triggered when the pile is extremely full 
"reduce_half" < reduce prey amount of the freshkill pile by a half
"reduce_quarter" < reduce prey amount of the freshkill pile by a quarter
"reduce_eighth" < reduce prey amount of the freshkill pile by a eighth
"other_cat" < there is a second cat in this event

"""


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


INJURY_DISTRIBUTION = None
with open(f"resources/dicts/conditions/event_injuries_distribution.json", 'r') as read_file:
    INJURY_DISTRIBUTION = ujson.loads(read_file.read())

INJURIES = None
with open(f"resources/dicts/conditions/injuries.json", 'r') as read_file:
    INJURIES = ujson.loads(read_file.read())
