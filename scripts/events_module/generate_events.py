import ujson
from scripts.game_structure.game_essentials import game


class GenerateEvents():

    def possible_injury_events(self, status, age):

        event_list = []

        if game.clan.biome == 'Forest':
            if status == "kitten":
                event_list.extend(self.generate_injury_event(ALL_FOREST_KITTEN_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_KITTEN_EVENT_INJURIES))
            elif status == "apprentice":
                event_list.extend(self.generate_injury_event(ALL_FOREST_APPRENTICE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_APPRENTICE_EVENT_INJURIES))
            elif status == "warrior":
                event_list.extend(self.generate_injury_event(ALL_FOREST_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_WARRIOR_EVENT_INJURIES))
            elif status == "elder" and age == 'elder':
                event_list.extend(self.generate_injury_event(ALL_FOREST_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_injury_event(ALL_FOREST_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_injury_event(ALL_FOREST_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_injury_event(ALL_FOREST_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_LEADER_EVENT_INJURIES))

        elif game.clan.biome == 'Plains':
            if status == "kitten":
                event_list.extend(self.generate_injury_event(ALL_PLAINS_KITTEN_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_KITTEN_EVENT_INJURIES))
            elif status == "apprentice":
                event_list.extend(self.generate_injury_event(ALL_PLAINS_APPRENTICE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_APPRENTICE_EVENT_INJURIES))
            elif status == "warrior":
                event_list.extend(self.generate_injury_event(ALL_PLAINS_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_WARRIOR_EVENT_INJURIES))
            elif status == "elder" and age == 'elder':
                event_list.extend(self.generate_injury_event(ALL_PLAINS_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_injury_event(ALL_PLAINS_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_injury_event(ALL_PLAINS_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_injury_event(ALL_PLAINS_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_LEADER_EVENT_INJURIES))

        elif game.clan.biome == 'Mountainous':
            if status == "kitten":
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_KITTEN_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_KITTEN_EVENT_INJURIES))
            elif status == "apprentice":
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_APPRENTICE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_APPRENTICE_EVENT_INJURIES))
            elif status == "warrior":
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_WARRIOR_EVENT_INJURIES))
            elif status == "elder" and age == 'elder':
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_LEADER_EVENT_INJURIES))

        elif game.clan.biome == 'Beach':
            if status == "kitten":
                event_list.extend(self.generate_injury_event(ALL_BEACH_KITTEN_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_KITTEN_EVENT_INJURIES))
            elif status == "apprentice":
                event_list.extend(self.generate_injury_event(ALL_BEACH_APPRENTICE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_APPRENTICE_EVENT_INJURIES))
            elif status == "warrior":
                event_list.extend(self.generate_injury_event(ALL_BEACH_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_WARRIOR_EVENT_INJURIES))
            elif status == "elder" and age == 'elder':
                event_list.extend(self.generate_injury_event(ALL_BEACH_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_injury_event(ALL_BEACH_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_injury_event(ALL_BEACH_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_injury_event(ALL_BEACH_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_LEADER_EVENT_INJURIES))

        if status not in ['kitten', 'leader']:
            event_list.extend(self.generate_injury_event(GEN_GENERAL_EVENT_INJURIES))

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
                other_cat_skill=event["other_cat_skill"]
            )
            injury_list.append(injury_event)
        return injury_list
    
    def possible_death_events(self, status, age):

        event_list = []

        if game.clan.biome == 'Forest':
            if status == "kitten":
                event_list.extend(self.generate_death_events(ALL_FOREST_KITTEN_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_KITTEN_EVENT_DEATH))
            elif status == "apprentice":
                event_list.extend(self.generate_death_events(ALL_FOREST_APPRENTICE_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_APPRENTICE_EVENT_DEATH))
            elif status == "warrior":
                event_list.extend(self.generate_death_events(ALL_FOREST_WARRIOR_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_DEATH))
            elif status == "elder" and age == 'elder':
                event_list.extend(self.generate_death_events(ALL_FOREST_ELDER_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_ELDER_EVENT_DEATH))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_death_events(ALL_FOREST_MEDICINE_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_MEDICINE_EVENT_DEATH))
            elif status == "deputy":
                event_list.extend(self.generate_death_events(ALL_FOREST_DEPUTY_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_DEPUTY_EVENT_DEATH))
            elif status == "leader":
                event_list.extend(self.generate_death_events(ALL_FOREST_LEADER_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_LEADER_EVENT_DEATH))

        elif game.clan.biome == 'Plains':
            if status == "kitten":
                event_list.extend(self.generate_death_events(ALL_PLAINS_KITTEN_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_KITTEN_EVENT_DEATH))
            elif status == "apprentice":
                event_list.extend(self.generate_death_events(ALL_PLAINS_APPRENTICE_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_APPRENTICE_EVENT_DEATH))
            elif status == "warrior":
                event_list.extend(self.generate_death_events(ALL_PLAINS_WARRIOR_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_DEATH))
            elif status == "elder" and age == 'elder':
                event_list.extend(self.generate_death_events(ALL_PLAINS_ELDER_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_ELDER_EVENT_DEATH))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_death_events(ALL_PLAINS_MEDICINE_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_MEDICINE_EVENT_DEATH))
            elif status == "deputy":
                event_list.extend(self.generate_death_events(ALL_PLAINS_DEPUTY_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_DEPUTY_EVENT_DEATH))
            elif status == "leader":
                event_list.extend(self.generate_death_events(ALL_PLAINS_LEADER_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_LEADER_EVENT_DEATH))

        elif game.clan.biome == 'Mountainous':
            if status == "kitten":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_KITTEN_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_KITTEN_EVENT_DEATH))
            elif status == "apprentice":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_APPRENTICE_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_APPRENTICE_EVENT_DEATH))
            elif status == "warrior":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_WARRIOR_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_DEATH))
            elif status == "elder" and age == 'elder':
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_ELDER_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_ELDER_EVENT_DEATH))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_MEDICINE_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_MEDICINE_EVENT_DEATH))
            elif status == "deputy":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_DEPUTY_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_DEPUTY_EVENT_DEATH))
            elif status == "leader":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_LEADER_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_LEADER_EVENT_DEATH))

        elif game.clan.biome == 'Beach':
            if status == "kitten":
                event_list.extend(self.generate_death_events(ALL_BEACH_KITTEN_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_KITTEN_EVENT_DEATH))
            elif status == "apprentice":
                event_list.extend(self.generate_death_events(ALL_BEACH_APPRENTICE_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_APPRENTICE_EVENT_DEATH))
            elif status == "warrior":
                event_list.extend(self.generate_death_events(ALL_BEACH_WARRIOR_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_DEATH))
            elif status == "elder" and age == 'elder':
                event_list.extend(self.generate_death_events(ALL_BEACH_ELDER_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_ELDER_EVENT_DEATH))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_death_events(ALL_BEACH_MEDICINE_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_MEDICINE_EVENT_DEATH))
            elif status == "deputy":
                event_list.extend(self.generate_death_events(ALL_BEACH_DEPUTY_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_DEPUTY_EVENT_DEATH))
            elif status == "leader":
                event_list.extend(self.generate_death_events(ALL_BEACH_LEADER_EVENT_DEATH))
                event_list.extend(self.generate_death_events(GEN_LEADER_EVENT_DEATH))

        if status not in ['kitten', 'leader']:
            event_list.extend(self.generate_death_events(GEN_GENERAL_EVENT_DEATH))

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
                other_cat_skill=event["other_cat_skill"]
            )
            death_list.append(death_event)

        return death_list


class InjuryEvent:
    def __init__(self,
                 injury=None,
                 camp='any',
                 tags=None,
                 event_text='',
                 history_text=None,
                 cat_trait=None,
                 cat_skill=None,
                 other_cat_trait=None,
                 other_cat_skill=None):
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
    def __init__(self,
                 camp,
                 tags=None,
                 death_text='',
                 history_text=None,
                 cat_trait=None,
                 cat_skill=None,
                 other_cat_trait=None,
                 other_cat_skill=None):
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


resource_directory = "resources/dicts/events/"

# ---------------------------------------------------------------------------- #
#                               INJURY EVENTS                                  #
# ---------------------------------------------------------------------------- #
event_triggered = "injury/"

GEN_KITTEN_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general/kitten.json", 'r') as read_file:
    GEN_KITTEN_EVENT_INJURIES = ujson.loads(read_file.read())

GEN_APPRENTICE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general/apprentice.json", 'r') as read_file:
    GEN_APPRENTICE_EVENT_INJURIES = ujson.loads(read_file.read())

GEN_WARRIOR_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general/warrior.json", 'r') as read_file:
    GEN_WARRIOR_EVENT_INJURIES = ujson.loads(read_file.read())

GEN_MEDICINE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general/medicine.json", 'r') as read_file:
    GEN_MEDICINE_EVENT_INJURIES = ujson.loads(read_file.read())

GEN_DEPUTY_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general/deputy.json", 'r') as read_file:
    GEN_DEPUTY_EVENT_INJURIES = ujson.loads(read_file.read())

GEN_LEADER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general/leader.json", 'r') as read_file:
    GEN_LEADER_EVENT_INJURIES = ujson.loads(read_file.read())

GEN_ELDER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general/elder.json", 'r') as read_file:
    GEN_ELDER_EVENT_INJURIES = ujson.loads(read_file.read())

GEN_GENERAL_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}general/general.json", 'r') as read_file:
    GEN_GENERAL_EVENT_INJURIES = ujson.loads(read_file.read())

# forest specific injury events

FOREST_KITTEN_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}forest/kitten.json", 'r') as read_file:
    FOREST_KITTEN_EVENT_INJURIES = ujson.loads(read_file.read())

FOREST_APPRENTICE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}forest/apprentice.json", 'r') as read_file:
    FOREST_APPRENTICE_EVENT_INJURIES = ujson.loads(read_file.read())

FOREST_WARRIOR_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}forest/warrior.json", 'r') as read_file:
    FOREST_WARRIOR_EVENT_INJURIES = ujson.loads(read_file.read())

FOREST_MEDICINE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}forest/medicine.json", 'r') as read_file:
    FOREST_MEDICINE_EVENT_INJURIES = ujson.loads(read_file.read())

FOREST_DEPUTY_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}forest/deputy.json", 'r') as read_file:
    FOREST_DEPUTY_EVENT_INJURIES = ujson.loads(read_file.read())

FOREST_LEADER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}forest/leader.json", 'r') as read_file:
    FOREST_LEADER_EVENT_INJURIES = ujson.loads(read_file.read())

FOREST_ELDER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}forest/elder.json", 'r') as read_file:
    FOREST_ELDER_EVENT_INJURIES = ujson.loads(read_file.read())

FOREST_GENERAL_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}forest/general.json", 'r') as read_file:
    FOREST_GENERAL_EVENT_INJURIES = ujson.loads(read_file.read())

# plains specific injury events

PLAINS_KITTEN_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}plains/kitten.json", 'r') as read_file:
    PLAINS_KITTEN_EVENT_INJURIES = ujson.loads(read_file.read())

PLAINS_APPRENTICE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}plains/apprentice.json", 'r') as read_file:
    PLAINS_APPRENTICE_EVENT_INJURIES = ujson.loads(read_file.read())

PLAINS_WARRIOR_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}plains/warrior.json", 'r') as read_file:
    PLAINS_WARRIOR_EVENT_INJURIES = ujson.loads(read_file.read())

PLAINS_MEDICINE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}plains/medicine.json", 'r') as read_file:
    PLAINS_MEDICINE_EVENT_INJURIES = ujson.loads(read_file.read())

PLAINS_DEPUTY_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}plains/deputy.json", 'r') as read_file:
    PLAINS_DEPUTY_EVENT_INJURIES = ujson.loads(read_file.read())

PLAINS_LEADER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}plains/leader.json", 'r') as read_file:
    PLAINS_LEADER_EVENT_INJURIES = ujson.loads(read_file.read())

PLAINS_ELDER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}plains/elder.json", 'r') as read_file:
    PLAINS_ELDER_EVENT_INJURIES = ujson.loads(read_file.read())

PLAINS_GENERAL_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}plains/general.json", 'r') as read_file:
    PLAINS_GENERAL_EVENT_INJURIES = ujson.loads(read_file.read())

# mountainous specific injury events

MOUNTAINOUS_KITTEN_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}mountainous/kitten.json", 'r') as read_file:
    MOUNTAINOUS_KITTEN_EVENT_INJURIES = ujson.loads(read_file.read())

MOUNTAINOUS_APPRENTICE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}mountainous/apprentice.json", 'r') as read_file:
    MOUNTAINOUS_APPRENTICE_EVENT_INJURIES = ujson.loads(read_file.read())

MOUNTAINOUS_WARRIOR_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}mountainous/warrior.json", 'r') as read_file:
    MOUNTAINOUS_WARRIOR_EVENT_INJURIES = ujson.loads(read_file.read())

MOUNTAINOUS_MEDICINE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}mountainous/medicine.json", 'r') as read_file:
    MOUNTAINOUS_MEDICINE_EVENT_INJURIES = ujson.loads(read_file.read())

MOUNTAINOUS_DEPUTY_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}mountainous/deputy.json", 'r') as read_file:
    MOUNTAINOUS_DEPUTY_EVENT_INJURIES = ujson.loads(read_file.read())

MOUNTAINOUS_LEADER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}mountainous/leader.json", 'r') as read_file:
    MOUNTAINOUS_LEADER_EVENT_INJURIES = ujson.loads(read_file.read())

MOUNTAINOUS_ELDER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}mountainous/elder.json", 'r') as read_file:
    MOUNTAINOUS_ELDER_EVENT_INJURIES = ujson.loads(read_file.read())

MOUNTAINOUS_GENERAL_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}mountainous/general.json", 'r') as read_file:
    MOUNTAINOUS_GENERAL_EVENT_INJURIES = ujson.loads(read_file.read())

# beach specific injury events

BEACH_KITTEN_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}beach/kitten.json", 'r') as read_file:
    BEACH_KITTEN_EVENT_INJURIES = ujson.loads(read_file.read())

BEACH_APPRENTICE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}beach/apprentice.json", 'r') as read_file:
    BEACH_APPRENTICE_EVENT_INJURIES = ujson.loads(read_file.read())

BEACH_WARRIOR_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}beach/warrior.json", 'r') as read_file:
    BEACH_WARRIOR_EVENT_INJURIES = ujson.loads(read_file.read())

BEACH_MEDICINE_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}beach/medicine.json", 'r') as read_file:
    BEACH_MEDICINE_EVENT_INJURIES = ujson.loads(read_file.read())

BEACH_DEPUTY_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}beach/deputy.json", 'r') as read_file:
    BEACH_DEPUTY_EVENT_INJURIES = ujson.loads(read_file.read())

BEACH_LEADER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}beach/leader.json", 'r') as read_file:
    BEACH_LEADER_EVENT_INJURIES = ujson.loads(read_file.read())

BEACH_ELDER_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}beach/elder.json", 'r') as read_file:
    BEACH_ELDER_EVENT_INJURIES = ujson.loads(read_file.read())

BEACH_GENERAL_EVENT_INJURIES = None
with open(f"{resource_directory}{event_triggered}beach/general.json", 'r') as read_file:
    BEACH_GENERAL_EVENT_INJURIES = ujson.loads(read_file.read())



ALL_FOREST_KITTEN_EVENT_INJURIES = None
ALL_PLAINS_KITTEN_EVENT_INJURIES = None
ALL_MOUNTAINOUS_KITTEN_EVENT_INJURIES = None
ALL_BEACH_KITTEN_EVENT_INJURIES = None

ALL_FOREST_KITTEN_EVENT_INJURIES = FOREST_KITTEN_EVENT_INJURIES
ALL_PLAINS_KITTEN_EVENT_INJURIES = PLAINS_KITTEN_EVENT_INJURIES
ALL_MOUNTAINOUS_KITTEN_EVENT_INJURIES = MOUNTAINOUS_KITTEN_EVENT_INJURIES
ALL_BEACH_KITTEN_EVENT_INJURIES = BEACH_KITTEN_EVENT_INJURIES

ALL_FOREST_APPRENTICE_EVENT_INJURIES = None
ALL_PLAINS_APPRENTICE_EVENT_INJURIES = None
ALL_MOUNTAINOUS_APPRENTICE_EVENT_INJURIES = None
ALL_BEACH_APPRENTICE_EVENT_INJURIES = None

ALL_FOREST_APPRENTICE_EVENT_INJURIES = FOREST_GENERAL_EVENT_INJURIES + \
                            FOREST_APPRENTICE_EVENT_INJURIES + \
                            FOREST_WARRIOR_EVENT_INJURIES
ALL_PLAINS_APPRENTICE_EVENT_INJURIES = PLAINS_GENERAL_EVENT_INJURIES + \
                            PLAINS_APPRENTICE_EVENT_INJURIES + \
                            PLAINS_WARRIOR_EVENT_INJURIES
ALL_MOUNTAINOUS_APPRENTICE_EVENT_INJURIES = MOUNTAINOUS_GENERAL_EVENT_INJURIES + \
                            MOUNTAINOUS_APPRENTICE_EVENT_INJURIES + \
                            MOUNTAINOUS_WARRIOR_EVENT_INJURIES
ALL_BEACH_APPRENTICE_EVENT_INJURIES = BEACH_GENERAL_EVENT_INJURIES + \
                            BEACH_APPRENTICE_EVENT_INJURIES + \
                            BEACH_WARRIOR_EVENT_INJURIES

ALL_FOREST_WARRIOR_EVENT_INJURIES = None
ALL_PLAINS_WARRIOR_EVENT_INJURIES = None
ALL_MOUNTAINOUS_WARRIOR_EVENT_INJURIES = None
ALL_BEACH_WARRIOR_EVENT_INJURIES = None

ALL_FOREST_WARRIOR_EVENT_INJURIES = FOREST_GENERAL_EVENT_INJURIES + \
                         FOREST_WARRIOR_EVENT_INJURIES
ALL_PLAINS_WARRIOR_EVENT_INJURIES = PLAINS_GENERAL_EVENT_INJURIES + \
                         PLAINS_WARRIOR_EVENT_INJURIES
ALL_MOUNTAINOUS_WARRIOR_EVENT_INJURIES = MOUNTAINOUS_GENERAL_EVENT_INJURIES + \
                         MOUNTAINOUS_WARRIOR_EVENT_INJURIES
ALL_BEACH_WARRIOR_EVENT_INJURIES = BEACH_GENERAL_EVENT_INJURIES + \
                         BEACH_WARRIOR_EVENT_INJURIES


ALL_FOREST_ELDER_EVENT_INJURIES = None
ALL_PLAINS_ELDER_EVENT_INJURIES = None
ALL_MOUNTAINOUS_ELDER_EVENT_INJURIES = None
ALL_BEACH_ELDER_EVENT_INJURIES = None

ALL_FOREST_ELDER_EVENT_INJURIES = FOREST_GENERAL_EVENT_INJURIES + \
                       FOREST_ELDER_EVENT_INJURIES
ALL_PLAINS_ELDER_EVENT_INJURIES = PLAINS_GENERAL_EVENT_INJURIES + \
                       PLAINS_ELDER_EVENT_INJURIES
ALL_MOUNTAINOUS_ELDER_EVENT_INJURIES = MOUNTAINOUS_GENERAL_EVENT_INJURIES + \
                       MOUNTAINOUS_ELDER_EVENT_INJURIES
ALL_BEACH_ELDER_EVENT_INJURIES = BEACH_GENERAL_EVENT_INJURIES + \
                       BEACH_ELDER_EVENT_INJURIES

ALL_FOREST_MEDICINE_EVENT_INJURIES = None
ALL_PLAINS_MEDICINE_EVENT_INJURIES = None
ALL_MOUNTAINOUS_MEDICINE_EVENT_INJURIES = None
ALL_BEACH_MEDICINE_EVENT_INJURIES = None

ALL_FOREST_MEDICINE_EVENT_INJURIES = FOREST_GENERAL_EVENT_INJURIES + \
                          FOREST_MEDICINE_EVENT_INJURIES
ALL_PLAINS_MEDICINE_EVENT_INJURIES = PLAINS_GENERAL_EVENT_INJURIES + \
                          PLAINS_MEDICINE_EVENT_INJURIES
ALL_MOUNTAINOUS_MEDICINE_EVENT_INJURIES = MOUNTAINOUS_GENERAL_EVENT_INJURIES + \
                          MOUNTAINOUS_MEDICINE_EVENT_INJURIES
ALL_BEACH_MEDICINE_EVENT_INJURIES = BEACH_GENERAL_EVENT_INJURIES + \
                          BEACH_MEDICINE_EVENT_INJURIES

ALL_FOREST_DEPUTY_EVENT_INJURIES = None
ALL_PLAINS_DEPUTY_EVENT_INJURIES = None
ALL_MOUNTAINOUS_DEPUTY_EVENT_INJURIES = None
ALL_BEACH_DEPUTY_EVENT_INJURIES = None

ALL_FOREST_DEPUTY_EVENT_INJURIES = FOREST_GENERAL_EVENT_INJURIES + \
                        FOREST_DEPUTY_EVENT_INJURIES + \
                        FOREST_WARRIOR_EVENT_INJURIES
ALL_PLAINS_DEPUTY_EVENT_INJURIES = PLAINS_GENERAL_EVENT_INJURIES + \
                        PLAINS_DEPUTY_EVENT_INJURIES + \
                        PLAINS_WARRIOR_EVENT_INJURIES
ALL_MOUNTAINOUS_DEPUTY_EVENT_INJURIES = MOUNTAINOUS_GENERAL_EVENT_INJURIES + \
                        MOUNTAINOUS_DEPUTY_EVENT_INJURIES + \
                        MOUNTAINOUS_WARRIOR_EVENT_INJURIES
ALL_BEACH_DEPUTY_EVENT_INJURIES = BEACH_GENERAL_EVENT_INJURIES + \
                        BEACH_DEPUTY_EVENT_INJURIES + \
                        BEACH_WARRIOR_EVENT_INJURIES


ALL_FOREST_LEADER_EVENT_INJURIES = None
ALL_PLAINS_LEADER_EVENT_INJURIES = None
ALL_MOUNTAINOUS_LEADER_EVENT_INJURIES = None
ALL_BEACH_LEADER_EVENT_INJURIES = None

ALL_FOREST_LEADER_EVENT_INJURIES = FOREST_GENERAL_EVENT_INJURIES + \
                        FOREST_LEADER_EVENT_INJURIES + \
                        FOREST_WARRIOR_EVENT_INJURIES
ALL_PLAINS_LEADER_EVENT_INJURIES = PLAINS_GENERAL_EVENT_INJURIES + \
                        PLAINS_LEADER_EVENT_INJURIES + \
                        PLAINS_WARRIOR_EVENT_INJURIES
ALL_MOUNTAINOUS_LEADER_EVENT_INJURIES = MOUNTAINOUS_GENERAL_EVENT_INJURIES + \
                        MOUNTAINOUS_LEADER_EVENT_INJURIES + \
                        MOUNTAINOUS_WARRIOR_EVENT_INJURIES
ALL_BEACH_LEADER_EVENT_INJURIES = BEACH_GENERAL_EVENT_INJURIES + \
                        BEACH_LEADER_EVENT_INJURIES + \
                        BEACH_WARRIOR_EVENT_INJURIES


# ---------------------------------------------------------------------------- #
#                                DEATH EVENTS                                  #
# ---------------------------------------------------------------------------- #

event_triggered = "death/"

GEN_KITTEN_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}general/kitten.json", 'r') as read_file:
    GEN_KITTEN_EVENT_DEATH = ujson.loads(read_file.read())

GEN_APPRENTICE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}general/apprentice.json", 'r') as read_file:
    GEN_APPRENTICE_EVENT_DEATH = ujson.loads(read_file.read())

GEN_WARRIOR_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}general/warrior.json", 'r') as read_file:
    GEN_WARRIOR_EVENT_DEATH = ujson.loads(read_file.read())

GEN_MEDICINE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}general/medicine.json", 'r') as read_file:
    GEN_MEDICINE_EVENT_DEATH = ujson.loads(read_file.read())

GEN_DEPUTY_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}general/deputy.json", 'r') as read_file:
    GEN_DEPUTY_EVENT_DEATH = ujson.loads(read_file.read())

GEN_LEADER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}general/leader.json", 'r') as read_file:
    GEN_LEADER_EVENT_DEATH = ujson.loads(read_file.read())

GEN_ELDER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}general/elder.json", 'r') as read_file:
    GEN_ELDER_EVENT_DEATH = ujson.loads(read_file.read())

GEN_GENERAL_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}general/general.json", 'r') as read_file:
    GEN_GENERAL_EVENT_DEATH = ujson.loads(read_file.read())

# forest specific injury events

FOREST_KITTEN_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}forest/kitten.json", 'r') as read_file:
    FOREST_KITTEN_EVENT_DEATH = ujson.loads(read_file.read())

FOREST_APPRENTICE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}forest/apprentice.json", 'r') as read_file:
    FOREST_APPRENTICE_EVENT_DEATH = ujson.loads(read_file.read())

FOREST_WARRIOR_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}forest/warrior.json", 'r') as read_file:
    FOREST_WARRIOR_EVENT_DEATH = ujson.loads(read_file.read())

FOREST_MEDICINE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}forest/medicine.json", 'r') as read_file:
    FOREST_MEDICINE_EVENT_DEATH = ujson.loads(read_file.read())

FOREST_DEPUTY_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}forest/deputy.json", 'r') as read_file:
    FOREST_DEPUTY_EVENT_DEATH = ujson.loads(read_file.read())

FOREST_LEADER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}forest/leader.json", 'r') as read_file:
    FOREST_LEADER_EVENT_DEATH = ujson.loads(read_file.read())

FOREST_ELDER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}forest/elder.json", 'r') as read_file:
    FOREST_ELDER_EVENT_DEATH = ujson.loads(read_file.read())

FOREST_GENERAL_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}forest/general.json", 'r') as read_file:
    FOREST_GENERAL_EVENT_DEATH = ujson.loads(read_file.read())

# plains specific injury events

PLAINS_KITTEN_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}plains/kitten.json", 'r') as read_file:
    PLAINS_KITTEN_EVENT_DEATH = ujson.loads(read_file.read())

PLAINS_APPRENTICE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}plains/apprentice.json", 'r') as read_file:
    PLAINS_APPRENTICE_EVENT_DEATH = ujson.loads(read_file.read())

PLAINS_WARRIOR_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}plains/warrior.json", 'r') as read_file:
    PLAINS_WARRIOR_EVENT_DEATH = ujson.loads(read_file.read())

PLAINS_MEDICINE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}plains/medicine.json", 'r') as read_file:
    PLAINS_MEDICINE_EVENT_DEATH = ujson.loads(read_file.read())

PLAINS_DEPUTY_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}plains/deputy.json", 'r') as read_file:
    PLAINS_DEPUTY_EVENT_DEATH = ujson.loads(read_file.read())

PLAINS_LEADER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}plains/leader.json", 'r') as read_file:
    PLAINS_LEADER_EVENT_DEATH = ujson.loads(read_file.read())

PLAINS_ELDER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}plains/elder.json", 'r') as read_file:
    PLAINS_ELDER_EVENT_DEATH = ujson.loads(read_file.read())

PLAINS_GENERAL_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}plains/general.json", 'r') as read_file:
    PLAINS_GENERAL_EVENT_DEATH = ujson.loads(read_file.read())

# mountainous specific injury events

MOUNTAINOUS_KITTEN_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}mountainous/kitten.json", 'r') as read_file:
    MOUNTAINOUS_KITTEN_EVENT_DEATH = ujson.loads(read_file.read())

MOUNTAINOUS_APPRENTICE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}mountainous/apprentice.json", 'r') as read_file:
    MOUNTAINOUS_APPRENTICE_EVENT_DEATH = ujson.loads(read_file.read())

MOUNTAINOUS_WARRIOR_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}mountainous/warrior.json", 'r') as read_file:
    MOUNTAINOUS_WARRIOR_EVENT_DEATH = ujson.loads(read_file.read())

MOUNTAINOUS_MEDICINE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}mountainous/medicine.json", 'r') as read_file:
    MOUNTAINOUS_MEDICINE_EVENT_DEATH = ujson.loads(read_file.read())

MOUNTAINOUS_DEPUTY_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}mountainous/deputy.json", 'r') as read_file:
    MOUNTAINOUS_DEPUTY_EVENT_DEATH = ujson.loads(read_file.read())

MOUNTAINOUS_LEADER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}mountainous/leader.json", 'r') as read_file:
    MOUNTAINOUS_LEADER_EVENT_DEATH = ujson.loads(read_file.read())

MOUNTAINOUS_ELDER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}mountainous/elder.json", 'r') as read_file:
    MOUNTAINOUS_ELDER_EVENT_DEATH = ujson.loads(read_file.read())

MOUNTAINOUS_GENERAL_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}mountainous/general.json", 'r') as read_file:
    MOUNTAINOUS_GENERAL_EVENT_DEATH = ujson.loads(read_file.read())

# beach specific injury events

BEACH_KITTEN_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}beach/kitten.json", 'r') as read_file:
    BEACH_KITTEN_EVENT_DEATH = ujson.loads(read_file.read())

BEACH_APPRENTICE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}beach/apprentice.json", 'r') as read_file:
    BEACH_APPRENTICE_EVENT_DEATH = ujson.loads(read_file.read())

BEACH_WARRIOR_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}beach/warrior.json", 'r') as read_file:
    BEACH_WARRIOR_EVENT_DEATH = ujson.loads(read_file.read())

BEACH_MEDICINE_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}beach/medicine.json", 'r') as read_file:
    BEACH_MEDICINE_EVENT_DEATH = ujson.loads(read_file.read())

BEACH_DEPUTY_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}beach/deputy.json", 'r') as read_file:
    BEACH_DEPUTY_EVENT_DEATH = ujson.loads(read_file.read())

BEACH_LEADER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}beach/leader.json", 'r') as read_file:
    BEACH_LEADER_EVENT_DEATH = ujson.loads(read_file.read())

BEACH_ELDER_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}beach/elder.json", 'r') as read_file:
    BEACH_ELDER_EVENT_DEATH = ujson.loads(read_file.read())

BEACH_GENERAL_EVENT_DEATH = None
with open(f"{resource_directory}{event_triggered}beach/general.json", 'r') as read_file:
    BEACH_GENERAL_EVENT_DEATH = ujson.loads(read_file.read())



ALL_FOREST_KITTEN_EVENT_DEATH = None
ALL_PLAINS_KITTEN_EVENT_DEATH = None
ALL_MOUNTAINOUS_KITTEN_EVENT_DEATH = None
ALL_BEACH_KITTEN_EVENT_DEATH = None

ALL_FOREST_KITTEN_EVENT_DEATH = FOREST_KITTEN_EVENT_DEATH
ALL_PLAINS_KITTEN_EVENT_DEATH = PLAINS_KITTEN_EVENT_DEATH
ALL_MOUNTAINOUS_KITTEN_EVENT_DEATH = MOUNTAINOUS_KITTEN_EVENT_DEATH
ALL_BEACH_KITTEN_EVENT_DEATH = BEACH_KITTEN_EVENT_DEATH

ALL_FOREST_APPRENTICE_EVENT_DEATH = None
ALL_PLAINS_APPRENTICE_EVENT_DEATH = None
ALL_MOUNTAINOUS_APPRENTICE_EVENT_DEATH = None
ALL_BEACH_APPRENTICE_EVENT_DEATH = None

ALL_FOREST_APPRENTICE_EVENT_DEATH = FOREST_GENERAL_EVENT_DEATH + \
                            FOREST_APPRENTICE_EVENT_DEATH + \
                            FOREST_WARRIOR_EVENT_DEATH
ALL_PLAINS_APPRENTICE_EVENT_DEATH = PLAINS_GENERAL_EVENT_DEATH + \
                            PLAINS_APPRENTICE_EVENT_DEATH + \
                            PLAINS_WARRIOR_EVENT_DEATH
ALL_MOUNTAINOUS_APPRENTICE_EVENT_DEATH = MOUNTAINOUS_GENERAL_EVENT_DEATH + \
                            MOUNTAINOUS_APPRENTICE_EVENT_DEATH + \
                            MOUNTAINOUS_WARRIOR_EVENT_DEATH
ALL_BEACH_APPRENTICE_EVENT_DEATH = BEACH_GENERAL_EVENT_DEATH + \
                            BEACH_APPRENTICE_EVENT_DEATH + \
                            BEACH_WARRIOR_EVENT_DEATH

ALL_FOREST_WARRIOR_EVENT_DEATH = None
ALL_PLAINS_WARRIOR_EVENT_DEATH = None
ALL_MOUNTAINOUS_WARRIOR_EVENT_DEATH = None
ALL_BEACH_WARRIOR_EVENT_DEATH = None

ALL_FOREST_WARRIOR_EVENT_DEATH = FOREST_GENERAL_EVENT_DEATH + \
                         FOREST_WARRIOR_EVENT_DEATH
ALL_PLAINS_WARRIOR_EVENT_DEATH = PLAINS_GENERAL_EVENT_DEATH + \
                         PLAINS_WARRIOR_EVENT_DEATH
ALL_MOUNTAINOUS_WARRIOR_EVENT_DEATH = MOUNTAINOUS_GENERAL_EVENT_DEATH + \
                         MOUNTAINOUS_WARRIOR_EVENT_DEATH
ALL_BEACH_WARRIOR_EVENT_DEATH = BEACH_GENERAL_EVENT_DEATH + \
                         BEACH_WARRIOR_EVENT_DEATH


ALL_FOREST_ELDER_EVENT_DEATH = None
ALL_PLAINS_ELDER_EVENT_DEATH = None
ALL_MOUNTAINOUS_ELDER_EVENT_DEATH = None
ALL_BEACH_ELDER_EVENT_DEATH = None

ALL_FOREST_ELDER_EVENT_DEATH = FOREST_GENERAL_EVENT_DEATH + \
                       FOREST_ELDER_EVENT_DEATH
ALL_PLAINS_ELDER_EVENT_DEATH = PLAINS_GENERAL_EVENT_DEATH + \
                       PLAINS_ELDER_EVENT_DEATH
ALL_MOUNTAINOUS_ELDER_EVENT_DEATH = MOUNTAINOUS_GENERAL_EVENT_DEATH + \
                       MOUNTAINOUS_ELDER_EVENT_DEATH
ALL_BEACH_ELDER_EVENT_DEATH = BEACH_GENERAL_EVENT_DEATH + \
                       BEACH_ELDER_EVENT_DEATH

ALL_FOREST_MEDICINE_EVENT_DEATH = None
ALL_PLAINS_MEDICINE_EVENT_DEATH = None
ALL_MOUNTAINOUS_MEDICINE_EVENT_DEATH = None
ALL_BEACH_MEDICINE_EVENT_DEATH = None

ALL_FOREST_MEDICINE_EVENT_DEATH = FOREST_GENERAL_EVENT_DEATH + \
                          FOREST_MEDICINE_EVENT_DEATH
ALL_PLAINS_MEDICINE_EVENT_DEATH = PLAINS_GENERAL_EVENT_DEATH + \
                          PLAINS_MEDICINE_EVENT_DEATH
ALL_MOUNTAINOUS_MEDICINE_EVENT_DEATH = MOUNTAINOUS_GENERAL_EVENT_DEATH + \
                          MOUNTAINOUS_MEDICINE_EVENT_DEATH
ALL_BEACH_MEDICINE_EVENT_DEATH = BEACH_GENERAL_EVENT_DEATH + \
                          BEACH_MEDICINE_EVENT_DEATH

ALL_FOREST_DEPUTY_EVENT_DEATH = None
ALL_PLAINS_DEPUTY_EVENT_DEATH = None
ALL_MOUNTAINOUS_DEPUTY_EVENT_DEATH = None
ALL_BEACH_DEPUTY_EVENT_DEATH = None

ALL_FOREST_DEPUTY_EVENT_DEATH = FOREST_GENERAL_EVENT_DEATH + \
                        FOREST_DEPUTY_EVENT_DEATH + \
                        FOREST_WARRIOR_EVENT_DEATH
ALL_PLAINS_DEPUTY_EVENT_DEATH = PLAINS_GENERAL_EVENT_DEATH + \
                        PLAINS_DEPUTY_EVENT_DEATH + \
                        PLAINS_WARRIOR_EVENT_DEATH
ALL_MOUNTAINOUS_DEPUTY_EVENT_DEATH = MOUNTAINOUS_GENERAL_EVENT_DEATH + \
                        MOUNTAINOUS_DEPUTY_EVENT_DEATH + \
                        MOUNTAINOUS_WARRIOR_EVENT_DEATH
ALL_BEACH_DEPUTY_EVENT_DEATH = BEACH_GENERAL_EVENT_DEATH + \
                        BEACH_DEPUTY_EVENT_DEATH + \
                        BEACH_WARRIOR_EVENT_DEATH


ALL_FOREST_LEADER_EVENT_DEATH = None
ALL_PLAINS_LEADER_EVENT_DEATH = None
ALL_MOUNTAINOUS_LEADER_EVENT_DEATH = None
ALL_BEACH_LEADER_EVENT_DEATH = None

ALL_FOREST_LEADER_EVENT_DEATH = FOREST_GENERAL_EVENT_DEATH + \
                        FOREST_LEADER_EVENT_DEATH + \
                        FOREST_WARRIOR_EVENT_DEATH
ALL_PLAINS_LEADER_EVENT_DEATH = PLAINS_GENERAL_EVENT_DEATH + \
                        PLAINS_LEADER_EVENT_DEATH + \
                        PLAINS_WARRIOR_EVENT_DEATH
ALL_MOUNTAINOUS_LEADER_EVENT_DEATH = MOUNTAINOUS_GENERAL_EVENT_DEATH + \
                        MOUNTAINOUS_LEADER_EVENT_DEATH + \
                        MOUNTAINOUS_WARRIOR_EVENT_DEATH
ALL_BEACH_LEADER_EVENT_DEATH = BEACH_GENERAL_EVENT_DEATH + \
                        BEACH_LEADER_EVENT_DEATH + \
                        BEACH_WARRIOR_EVENT_DEATH

