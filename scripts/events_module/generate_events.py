import ujson
from scripts.game_structure.game_essentials import game


class GenerateEvents():

    def possible_injury_events(self, status):

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
            elif status == "elder":
                event_list.extend(self.generate_injury_event(ALL_FOREST_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_injury_event(ALL_FOREST_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_injury_event(ALL_FOREST_DEPUTY_EVENT_INJURIES))
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
            elif status == "elder":
                event_list.extend(self.generate_injury_event(ALL_PLAINS_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_injury_event(ALL_PLAINS_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_injury_event(ALL_PLAINS_DEPUTY_EVENT_INJURIES))
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
            elif status == "elder":
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_injury_event(ALL_MOUNTAINOUS_DEPUTY_EVENT_INJURIES))
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
            elif status == "elder":
                event_list.extend(self.generate_injury_event(ALL_BEACH_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_injury_event(ALL_BEACH_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_injury_event(ALL_BEACH_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_injury_event(ALL_BEACH_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_injury_event(GEN_LEADER_EVENT_INJURIES))

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
    
    def possible_death_events(self, status):

        event_list = []

        if game.clan.biome == 'Forest':
            if status == "kitten":
                event_list.extend(self.generate_death_events(ALL_FOREST_KITTEN_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_KITTEN_EVENT_INJURIES))
            elif status == "apprentice":
                event_list.extend(self.generate_death_events(ALL_FOREST_APPRENTICE_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_APPRENTICE_EVENT_INJURIES))
            elif status == "warrior":
                event_list.extend(self.generate_death_events(ALL_FOREST_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_INJURIES))
            elif status == "elder":
                event_list.extend(self.generate_death_events(ALL_FOREST_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_death_events(ALL_FOREST_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_death_events(ALL_FOREST_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_death_events(ALL_FOREST_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_LEADER_EVENT_INJURIES))

        elif game.clan.biome == 'Plains':
            if status == "kitten":
                event_list.extend(self.generate_death_events(ALL_PLAINS_KITTEN_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_KITTEN_EVENT_INJURIES))
            elif status == "apprentice":
                event_list.extend(self.generate_death_events(ALL_PLAINS_APPRENTICE_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_APPRENTICE_EVENT_INJURIES))
            elif status == "warrior":
                event_list.extend(self.generate_death_events(ALL_PLAINS_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_INJURIES))
            elif status == "elder":
                event_list.extend(self.generate_death_events(ALL_PLAINS_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_death_events(ALL_PLAINS_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_death_events(ALL_PLAINS_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_death_events(ALL_PLAINS_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_LEADER_EVENT_INJURIES))

        elif game.clan.biome == 'Mountainous':
            if status == "kitten":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_KITTEN_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_KITTEN_EVENT_INJURIES))
            elif status == "apprentice":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_APPRENTICE_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_APPRENTICE_EVENT_INJURIES))
            elif status == "warrior":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_INJURIES))
            elif status == "elder":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_death_events(ALL_MOUNTAINOUS_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_LEADER_EVENT_INJURIES))

        elif game.clan.biome == 'Beach':
            if status == "kitten":
                event_list.extend(self.generate_death_events(ALL_BEACH_KITTEN_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_KITTEN_EVENT_INJURIES))
            elif status == "apprentice":
                event_list.extend(self.generate_death_events(ALL_BEACH_APPRENTICE_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_APPRENTICE_EVENT_INJURIES))
            elif status == "warrior":
                event_list.extend(self.generate_death_events(ALL_BEACH_WARRIOR_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_WARRIOR_EVENT_INJURIES))
            elif status == "elder":
                event_list.extend(self.generate_death_events(ALL_BEACH_ELDER_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_ELDER_EVENT_INJURIES))
            elif status in ["medicine cat", "medicine cat apprentice"]:
                event_list.extend(self.generate_death_events(ALL_BEACH_MEDICINE_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_MEDICINE_EVENT_INJURIES))
            elif status == "deputy":
                event_list.extend(self.generate_death_events(ALL_BEACH_DEPUTY_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_DEPUTY_EVENT_INJURIES))
            elif status == "leader":
                event_list.extend(self.generate_death_events(ALL_BEACH_LEADER_EVENT_INJURIES))
                event_list.extend(self.generate_death_events(GEN_LEADER_EVENT_INJURIES))

            return event_list

    def generate_death_events(self, events_dict):
        death_list = []
        for event in events_dict:
            death_event = DeathEvent(
                camp=event["camp"],
                tags=event["tags"],
                death_text=event["event_text"],
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
                 tags=None,
                 event_text='',
                 history_text=None,
                 cat_trait=None,
                 cat_skill=None,
                 other_cat_trait=None,
                 other_cat_skill=None):
        self.injury = injury
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
possible tags: 
"illness", "multi_death", "old_age", "all_lives", "some_lives", "murder", "war"
"leader", "kitten", "deputy", "medicine_cat", "apprentice", "elder"
"other_cat", "other_cat_med", "other_cat_app", "other_cat_kit", "other_cat_dep",  
"other_clan", "rel_down", "rel_up", 
"Forest", "Plains", "Mountainous", "Beach", 
"Newleaf", "Greenleaf", "Leaf-fall", "Leaf-bare"
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

