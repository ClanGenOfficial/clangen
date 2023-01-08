try:
    import ujson
except ImportError:
    import json as ujson
from scripts.game_structure.game_essentials import game

resource_directory = "resources/dicts/events/"


class GenerateEvents:
    @staticmethod
    def get_event_dicts(event_triggered, cat_type, biome):
        events = None
        try:
            with open(
                f"{resource_directory}{event_triggered}/{biome}/{cat_type}.json",
                "r",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"Error: Unable to load events for {cat_type} from biome {biome}.")

        return events

    def possible_injury_events(self, cat_type, age):

        event_list = []
        if cat_type in ["medicine cat", "medicine cat apprentice"]:
            cat_type = "medicine"

        event_list.extend(
            self.generate_injury_event(
                GenerateEvents.get_event_dicts("injury", cat_type, "general")
            )
        )

        # skip the rest of the loading if there is an unrecognised cat type
        if cat_type not in game.clan.CAT_TYPES:
            print(
                f"WARNING: unrecognised cat status {cat_type} in generate_events. Have you added it to CAT_TYPES in clan.py?"
            )

        elif game.clan.biome not in game.clan.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES in clan.py?"
            )

        else:
            event_list.extend(
                self.generate_injury_event(
                    GenerateEvents.get_event_dicts(
                        "injury", cat_type, game.clan.biome.lower()
                    )
                )
            )

            if cat_type in ["apprentice", "deputy", "leader"]:
                event_list.extend(
                    self.generate_injury_event(
                        GenerateEvents.get_event_dicts(
                            "injury", "warrior", game.clan.biome.lower()
                        )
                    )
                )

            if cat_type not in ["kitten", "leader"]:
                event_list.extend(
                    self.generate_injury_event(
                        GenerateEvents.get_event_dicts("injury", "general", "general")
                    )
                )
                event_list.extend(
                    self.generate_injury_event(
                        GenerateEvents.get_event_dicts(
                            "injury", "general", game.clan.biome.lower()
                        )
                    )
                )

        return event_list

    def generate_injury_event(self, events_dict):
        injury_list = []
        for event in events_dict:
            injury_event = InjuryEvent(
                injury=event["injury"],
                tags=event["tags"],
                event_text=event["event_text"],
                history_text=event["history_text"],
                cat_trait=event["cat_trait"],
                cat_skill=event["cat_skill"],
                other_cat_trait=event["other_cat_trait"],
                other_cat_skill=event["other_cat_skill"],
            )
            injury_list.append(injury_event)
        return injury_list

    def possible_death_events(self, cat_type, age):

        event_list = []
        if cat_type in ["medicine cat", "medicine cat apprentice"]:
            cat_type = "medicine"

        event_list.extend(
            self.generate_death_events(
                GenerateEvents.get_event_dicts("death", cat_type, "general")
            )
        )

        # skip the rest of the loading if there is an unrecognised cat type
        if cat_type not in game.clan.CAT_TYPES:
            print(
                f"WARNING: unrecognised cat status {cat_type} in generate_events. Have you added it to CAT_TYPES in clan.py?"
            )

        elif game.clan.biome not in game.clan.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES in clan.py?"
            )

        else:
            event_list.extend(
                self.generate_death_events(
                    GenerateEvents.get_event_dicts(
                        "death", cat_type, game.clan.biome.lower()
                    )
                )
            )

            if cat_type in ["apprentice", "deputy", "leader"]:
                event_list.extend(
                    self.generate_death_events(
                        GenerateEvents.get_event_dicts(
                            "death", "warrior", game.clan.biome.lower()
                        )
                    )
                )

            if cat_type not in ["kitten", "leader"]:
                event_list.extend(
                    self.generate_death_events(
                        GenerateEvents.get_event_dicts("death", "general", "general")
                    )
                )
                event_list.extend(
                    self.generate_death_events(
                        GenerateEvents.get_event_dicts(
                            "death", "general", game.clan.biome.lower()
                        )
                    )
                )

        return event_list

    def generate_death_events(self, events_dict):
        death_list = []
        for event in events_dict:
            death_event = DeathEvent(
                camp=event["camp"],
                tags=event["tags"],
                death_text=event["death_text"],
                history_text=event["history_text"],
                cat_trait=event["cat_trait"],
                cat_skill=event["cat_skill"],
                other_cat_trait=event["other_cat_trait"],
                other_cat_skill=event["other_cat_skill"],
            )
            death_list.append(death_event)

        return death_list


class InjuryEvent:
    def __init__(
        self,
        injury=None,
        camp="any",
        tags=None,
        event_text="",
        history_text=None,
        cat_trait=None,
        cat_skill=None,
        other_cat_trait=None,
        other_cat_skill=None,
    ):
        self.injury = injury
        self.camp = camp
        self.tags = tags
        self.event_text = event_text
        self.history_text = history_text
        self.cat_trait = cat_trait
        self.cat_skill = cat_skill
        self.other_cat_trait = other_cat_trait
        self.other_cat_skill = other_cat_skill


class DeathEvent:
    def __init__(
        self,
        camp,
        tags=None,
        death_text="",
        history_text=None,
        cat_trait=None,
        cat_skill=None,
        other_cat_trait=None,
        other_cat_skill=None,
    ):
        self.camp = camp
        self.tags = tags
        self.death_text = death_text
        self.history_text = history_text
        self.cat_trait = cat_trait
        self.cat_skill = cat_skill
        self.other_cat_trait = other_cat_trait
        self.other_cat_skill = other_cat_skill


"""
Tagging Guidelines: (if you add more tags, please add guidelines for them here) 
"Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare" < specify season.  If event happens in all seasons then include all of those tags.

“classic” < use for death events caused by illness.  This tag ensures that illness death events only happen in classic mode since illness deaths are caused differently in enhanced/cruel mode

“multi_death” < use to indicate that two cats have died.  Two cats is the limit here.  Any more than that is a disaster death and i haven't touched disasters yet (and might not touch at all bc the code is scary lol)

“old_age” < use to mark deaths caused by old age

“all_lives” < take all the lives from a leader
“some_lives” < take a random number, but not all, lives from a leader

“murder” < m_c was murdered by the other cat

“war” < event only happens during war and ensures o_c in event is warring clan
“other_clan” < mark event as including another clan
“rel_down” < event decreases relation with other clan
“rel_up” < event increases relation with other clan
“hostile” < event only happens with hostile clans
“neutral” < event only happens with neutral clans
“ally” < event only happens with allied clans

“medicine_cat”, “medicine_cat_app” < ensure that m_c is one of these ranks.  All other ranks are separated into their own .jsons

“other_cat” < there is a second cat in this event

“other_cat_med”, “other_cat_med_app”, “other_cat_warrior”, “other_cat_app”, “other_cat_kit”, “other_cat_lead”, “other_cat_dep”, “other_cat_elder” < mark the other cat as having to be a certain status, if none of these tags are used then other_cat can be anyone

“other_cat_mate” < mark the other cat as having to be the m_c's mate
“other_cat_child” < mark the other cat as having to be the m_c's kit
“other_cat_parent” < mark the other cat as having to be m_c's parent
“other_cat_adult” < mark the other cat as not being able to be a kit or elder

“other_cat_own_app”, “other_cat_mentor” < mark the other cat has having to be the m_c's mentor or app respectively

“clan_kits” < clan must have kits for this event to appear

"yearly" < mark this event to occur 100% of the time on the first month of the tagged season. Not used for injury or death events. 

rel_down_self < event decreases tagged relationship parameter clan wide. Not used for injury or death events.
rel_up_self < event increases tagged relationship parameter clan wide. Not used for injury or death events.

mc_to_rc < change mc's relationship values towards rc
rc_to_mc < change rc's relationship values towards mc
to_both < change both cat's relationship values

Tagged relationship parameters are: "romantic", "platonic", "comfort", "respect", "trust", "dislike", "jealousy", 
Add “neg_” in front of parameter to make it a negative value change (i.e. “neg_romantic”, “neg_platonic”, ect)

"single_cat" < marks events that have one version that triggers for a list of cats, and this version that triggers for a single cat

"multi_cat" < marks events triggering for multiple cats e.g many apprentices being named at once

Use these to determine what corruption level the main cat should have, if relevant
“corruption_low” - main cat generally cares for the wellbeing of others and avoids hurting other cats, even if it benefits them to do so.
“corruption_mid” - main cat cares more for their own wellbeing.  Does not necessarily want to hurt others, but will not explicitly avoid it if it benefits them.
“corruption_high” - main cat doesn't care about the wellbeing of others and will happily hurt other cats if it benefits them.
You can mix and match corruption tags if you feel an event is on the line between two of them, the code will allow the event for a cat with either of the corruption levels tagged

"""
