#!/usr/bin/env python3
# -*- coding: ascii -*-
import random

try:
    import ujson
except ImportError:
    import json as ujson
from scripts.game_structure.game_essentials import game

resource_directory = "resources/dicts/events/"

# ---------------------------------------------------------------------------- #
#                Tagging Guidelines can be found at the bottom                 #
# ---------------------------------------------------------------------------- #

class GenerateEvents:
    @staticmethod
    def get_event_dicts(event_triggered, cat_type, biome):
        events = None
        try:
            file_path = f"{resource_directory}{event_triggered}/{cat_type}.json"
            if biome:
                file_path = f"{resource_directory}{event_triggered}/{biome}/{cat_type}.json"
            with open(
                file_path,
                "r",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"ERROR: Unable to load {event_triggered} events for {cat_type} from biome {biome}.")

        return events

    def generate_events(self, events_dict):
        event_list = []
        if not events_dict:
            return event_list
        for event in events_dict:
            event_text = event["event_text"] if "event_text" in event else None
            if not event_text:
                event_text = event["death_text"] if "death_text" in event else None

            if not event_text:
                print(f"WARNING: some events resources which are used in generate_events. Have no 'event_text'.")
            event = SingleEvent(
                camp="any",
                tags=event["tags"],
                event_text=event_text,
                history_text=event["history_text"] if "history_text" in event else None,
                cat_trait=event["cat_trait"],
                cat_skill=event["cat_skill"],
                other_cat_trait=event["other_cat_trait"],
                other_cat_skill=event["other_cat_skill"],
                cat_negate_trait=event["cat_negate_trait"] if "cat_negate_trait" in event else None,
                cat_negate_skill=event["cat_negate_skill"] if "cat_negate_skill" in event else None,
                other_cat_negate_trait=event["other_cat_negate_trait"] if "other_cat_negate_trait" in event else None,
                other_cat_negate_skill=event["other_cat_negate_trait"] if "other_cat_negate_trait" in event else None,
                backstory_constraint=event["backstory_constraint"] if "backstory_constraint" in event else None,

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
                reputation=event["reputation"] if "reputation" in event else None
            )
            event_list.append(event)
        return event_list

    def possible_events(self, cat_type, age, event_type):
        event_list = []
        if cat_type in ["medicine cat", "medicine cat apprentice"]:
            cat_type = "medicine"
        elif cat_type in ["mediator", "mediator apprentice"]:
            cat_type = "mediator"

        biome = None
        if event_type != "nutrition":
            biome = game.clan.biome.lower()

            event_list.extend(
                self.generate_events(
                    self.get_event_dicts(event_type, cat_type, "general")
                )
            )

        # skip the rest of the loading if there is an unrecognised cat type
        if cat_type not in game.clan.CAT_TYPES:
            print(f"WARNING: unrecognised cat status {cat_type} in generate_events. Have you added it to CAT_TYPES in clan.py?")

        elif game.clan.biome not in game.clan.BIOME_TYPES:
            print(f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES in clan.py?")

        else:
            event_list.extend(
                self.generate_events(
                    self.get_event_dicts(
                        event_type, cat_type, biome
                    )
                )
            )

            if cat_type in ["apprentice", "deputy", "leader"]:
                event_list.extend(
                    self.generate_events(
                        self.get_event_dicts(
                            event_type, "warrior", biome
                        )
                    )
                )

            if cat_type not in ["kitten", "leader"]:
                if event_type != "nutrition":
                    event_list.extend(
                        self.generate_events(
                            self.get_event_dicts(event_type, "general", "general")
                        )
                    )
                event_list.extend(
                    self.generate_events(
                        self.get_event_dicts(
                            event_type, "general", biome
                        )
                    )
                )

        return event_list

    def filter_possible_events(self, possible_events, cat, other_cat, war, enemy_clan, other_clan, alive_kits):
        final_events = []
        murder_events = []

        for event in possible_events:

            # some events are classic only
            if game.clan.game_mode in ["expanded", "cruel season"] and "classic" in event.tags:
                continue

            if "other_cat" in event.tags and not other_cat:
                continue

            if event.backstory_constraint and cat.backstory not in event.backstory_constraint:
                continue

            # make complete leader death less likely until the leader is over 150 moons
            if "all_lives" in event.tags:
                if int(cat.moons) < 150 and int(random.random() * 5):
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

            # check hate and jealousy before allowing murder
            if "murder" in event.tags and other_cat:
                hate = False
                relationships = other_cat.relationships.values()
                dislike_relation = list(filter(lambda rel: rel.dislike > 50, relationships))
                jealous_relation = list(filter(lambda rel: rel.jealousy > 50, relationships))
                for y in range(len(dislike_relation)):
                    cat_to = dislike_relation[y].cat_to
                    if cat_to == cat:
                        hate = True
                        print('MURDER ATTEMPT', other_cat.name, 'to', cat.name)
                        break
                for y in range(len(jealous_relation)):
                    cat_to = jealous_relation[y].cat_to
                    if cat_to == cat:
                        hate = True
                        print('MURDER ATTEMPT', other_cat.name, 'to', cat.name)
                        break
                if not hate:
                    continue
                else:
                    murder_events.append(event)

            # roll chance to get an injury of certain severity and check that injury is possible
            if event.injury in INJURIES:
                injury = INJURIES[event.injury]
                severity = injury['severity']
                if cat.status in INJURY_DISTRIBUTION:
                    severity_chance = INJURY_DISTRIBUTION[cat.status][severity]
                    if int(random.random() * severity_chance):
                        continue

                if event.injury == 'mangled tail' and ('NOTAIL' in cat.scars or 'HALFTAIL' in cat.scars):
                    continue

                if event.injury == 'torn ear' and 'NOEAR' in cat.scars:
                    continue

            # check meddie tags
            if "medicine_cat" in event.tags and cat.status != "medicine cat":
                continue
            elif "medicine_cat_app" in event.tags and cat.status != "medicine cat apprentice":
                continue

            # other clan related checks
            if "other_clan" in event.tags:
                if "war" in event.tags and not war:
                    continue
                if "ally" in event.tags and int(other_clan.relations) < 17:
                    continue
                elif "neutral" in event.tags and (int(other_clan.relations) <= 7 or int(other_clan.relations) >= 17):
                    continue
                elif "hostile" in event.tags and int(other_clan.relations) > 7:
                    continue

            # check if clan has kits
            if "clan_kits" in event.tags and not alive_kits:
                continue

            # check for old age
            if "old_age" in event.tags and cat.moons < 150:
                continue

            # check other_cat status and other identifiers
            if other_cat:
                if "other_cat_leader" in event.tags and other_cat.status != "leader":
                    continue
                elif "other_cat_dep" in event.tags and other_cat.status != "deputy":
                    continue
                elif "other_cat_med" in event.tags and other_cat.status != "medicine cat":
                    continue
                elif "other_cat_med_app" in event.tags and other_cat.status != "medicine cat apprentice":
                    continue
                elif "other_cat_warrior" in event.tags and other_cat.status != "warrior":
                    continue
                elif "other_cat_app" in event.tags and other_cat.status != "apprentice":
                    continue
                elif "other_cat_elder" in event.tags and other_cat.status != "elder":
                    continue
                elif "other_cat_adult" in event.tags and other_cat.age in ["elder", "kitten"]:
                    continue
                elif "other_cat_kit" in event.tags and other_cat.status != "kitten":
                    continue

                if "other_cat_mate" in event.tags and other_cat.ID != cat.mate:
                    continue
                elif "other_cat_child" in event.tags and other_cat.ID not in cat.get_children():
                    continue
                elif "other_cat_parent" in event.tags and other_cat.ID not in cat.get_parents():
                    continue

                if "other_cat_own_app" in event.tags and other_cat.ID not in cat.apprentice:
                    continue
                elif "other_cat_mentor" in event.tags and other_cat.ID != cat.mentor:
                    continue

                # check other_cat trait and skill
                if event.other_cat_trait:
                    if other_cat.trait not in event.other_cat_trait and int(random.random() * 15):
                        continue
                if event.other_cat_skill:
                    if other_cat.skill not in event.other_cat_skill and int(random.random() * 15):
                        continue
                if event.other_cat_negate_trait:
                    if other_cat.trait in event.other_cat_negate_trait and int(random.random() * 15):
                        continue
                if event.other_cat_negate_skill:
                    if other_cat.skill in event.other_cat_negate_skill and int(random.random() * 15):
                        continue

            else:
                if "other_cat" in event.tags or "multi_death" in event.tags:
                    continue

            # check for mate if the event requires one
            if "mate" in event.tags and cat.mate is None:
                continue

            # check cat trait and skill
            if event.cat_trait:
                if cat.trait not in event.cat_trait and int(random.random() * 15):
                    continue
            if event.cat_skill:
                if cat.skill not in event.cat_skill and int(random.random() * 15):
                    continue
            if event.cat_negate_trait:
                if cat.trait in event.cat_negate_trait and int(random.random() * 15):
                    continue
            if event.cat_negate_skill:
                if cat.skill in event.cat_negate_skill and int(random.random() * 15):
                    continue

            final_events.append(event)

        if murder_events and (other_cat.trait in ["vengeful", "bloodthirsty", "cold"] or not int(random.random() * 3)):
            print('WE KILL TONIGHT')
            return murder_events
        return final_events

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
            print(f"ERROR: Unable to load death reaction events for {family_relation}_{rel_value}.")
        return events

    def get_possible_death_reactions(self, family_relation, rel_value, trait, body_status):
        possible_events = []
        # grab general events first, since they'll always exist
        events = self.get_death_reaction_dicts("general", rel_value)
        possible_events.extend(events["general"][body_status])
        possible_events.extend(events[trait][body_status])

        # grab family events if they're needed
        if family_relation != 'general':
            events = self.get_death_reaction_dicts(family_relation, rel_value)
            possible_events.extend(events["general"][body_status])
            possible_events.extend(events[trait][body_status])

        # print(possible_events)

        return possible_events


class SingleEvent:
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
            reputation=None
    ):
        self.camp = camp
        self.tags = tags
        self.event_text = event_text
        self.history_text = history_text
        self.cat_trait = cat_trait
        self.cat_skill = cat_skill
        self.other_cat_trait = other_cat_trait
        self.other_cat_skill = other_cat_skill
        self.cat_negate_trait = cat_negate_trait
        self.cat_negate_skill = cat_negate_skill
        self.other_cat_negate_trait = other_cat_negate_trait
        self.other_cat_negate_skill = other_cat_negate_skill
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

"clan_kits" < clan must have kits for this event to appear

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


INJURY_DISTRIBUTION = None
with open(f"resources/dicts/conditions/event_injuries_distribution.json", 'r') as read_file:
    INJURY_DISTRIBUTION = ujson.loads(read_file.read())

INJURIES = None
with open(f"resources/dicts/conditions/injuries.json", 'r') as read_file:
    INJURIES = ujson.loads(read_file.read())
