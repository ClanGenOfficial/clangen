#!/usr/bin/env python3
# -*- coding: ascii -*-
try:
    import ujson
except ImportError:
    import json as ujson
from scripts.game_structure.game_essentials import game

resource_directory = "resources/dicts/events/"

# ---------------------------------------------------------------------------- #
#                     Tagging Guidelines can be found below                    #
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
                history_text=event["history_text"],
                cat_trait=event["cat_trait"],
                cat_skill=event["cat_skill"],
                other_cat_trait=event["other_cat_trait"],
                other_cat_skill=event["other_cat_skill"],
                injury=event["injury"] if "injury" in event else None,
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
        injury=None,
    ):
        self.camp = camp
        self.tags = tags
        self.event_text = event_text
        self.history_text = history_text
        self.cat_trait = cat_trait
        self.cat_skill = cat_skill
        self.other_cat_trait = other_cat_trait
        self.other_cat_skill = other_cat_skill

        # for injury event
        self.injury = injury


"""
Tagging Guidelines: (if you add more tags, please add guidelines for them here) 
"Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare" < specify season.  If event happens in all seasons then include all of those tags.

"classic" < use for death events caused by illness.  This tag ensures that illness death events only happen in classic mode since illness deaths are caused differently in enhanced/cruel mode

"multi_death" < use to indicate that two cats have died.  Two cats is the limit here.  Any more than that is a disaster death and i haven't touched disasters yet (and might not touch at all bc the code is scary lol)

"old_age" < use to mark deaths caused by old age

"all_lives" < take all the lives from a leader
"some_lives" < take a random number, but not all, lives from a leader

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

mc_to_rc < change mc's relationship values towards rc
rc_to_mc < change rc's relationship values towards mc
to_both < change both cat's relationship values

Tagged relationship parameters are: "romantic", "platonic", "comfort", "respect", "trust", "dislike", "jealousy", 
Add "neg_" in front of parameter to make it a negative value change (i.e. "neg_romantic", "neg_platonic", ect)


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
