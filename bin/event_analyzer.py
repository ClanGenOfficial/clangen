import json
import os
from collections import Counter
from typing import MutableMapping

import ujson

# Please don't mind this truly horrifying list of global variables.
# Lord have mercy on my soul
missing = "[tag missing]"
indent = "    "

global event_count

all_ids = {}
dupe_ids = []

valid_records = {
    "location": {
        "any": [],
        "beach": {},
        "desert": {},
        "forest": {},
        "mountainous": {},
        "plains": {},
        "wetlands": {}
    },
    "season": {
        "any": [],
        "newleaf": [],
        "greenleaf": [],
        "leaf-fall": [],
        "leaf-bare": []
    },
    "sub_type": {
        "war": [],
        "romance": [],
        "murder": [],
        "old_age": [],
        "mass_death": [],
        "adoption": [],
        "murder_reveal": [],
        "accessory": [],
        "ceremony": []},
    "tags": {
        "classic": [],
        "cruel_season": [],
        "clan": {},
        "no_body": [],
        "skill_trait_required": [],
        "clan_wide": [],
        "all_lives": [],
        "some_lives": [],
        "lives_remain": [],
        "high_lives": [],
        "mid_lives": [],
        "low_lives": []
    },
    "new_accessory": {},
    "injury": {
        "cats": {
            "m_c": [],
            "r_c": [],
            "n_c": []
        },
        "injuries": {},
        "scars": {}
    },
    "m_c": {
        "age": {
            "any": [],
            "newborn": [],
            "kitten": [],
            "adolescent": [],
            "young adult": [],
            "adult": [],
            "senior adult": [],
            "senior": [],
        },
        "status": {
            "any": [],
            "newborn": [],
            "kitten": [],
            "apprentice": [],
            "warrior": [],
            "medicine cat apprentice": [],
            "medicine cat": [],
            "mediator apprentice": [],
            "mediator": [],
            "elder": [],
            "deputy": [],
            "leader": [],
        },
        "relationship_status": {
            "siblings": [],
            "mates": [],
            "not_mates": [],
            "parent/child": [],
            "child/parent": [],
            "app/mentor": [],
            "mentor/app": [],

            "romantic": [],
            "platonic": [],
            "dislike": [],
            "comfortable": [],
            "jealousy": [],
            "admiration": [],
            "trust": []
        },
        "skill": {
            "TEACHER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "HUNTER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "FIGHTER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "RUNNER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLIMBER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SWIMMER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SPEAKER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "MEDIATOR": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLEVER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "INSIGHTFUL": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SENSE": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "KIT": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "STORY": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "LORE": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CAMP": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "HEALER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "STAR": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DUSK": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "OMEN": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DREAM": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLAIRVOYANT": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "PROPHET": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "GHOST": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DARK": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
        },
        "not_skill": {
            "TEACHER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "HUNTER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "FIGHTER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "RUNNER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLIMBER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SWIMMER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SPEAKER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "MEDIATOR": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLEVER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "INSIGHTFUL": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SENSE": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "KIT": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "STORY": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "LORE": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CAMP": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "HEALER": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "STAR": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DUSK": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "OMEN": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DREAM": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLAIRVOYANT": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "PROPHET": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "GHOST": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DARK": {
                "0": [],
                "1": [],
                "2": [],
                "3": [],
                "4": []
            }, },
        "trait": {
            "troublesome": [],
            "lonesome": [],
            "fierce": [],
            "bloodthirsty": [],
            "cold": [],
            "childish": [],
            "playful": [],
            "charismatic": [],
            "bold": [],
            "daring": [],
            "nervous": [],
            "righteous": [],
            "insecure": [],
            "strict": [],
            "compassionate": [],
            "thoughtful": [],
            "ambitious": [],
            "confident": [],
            "adventurous": [],
            "calm": [],
            "gloomy": [],
            "faithful": [],
            "loving": [],
            "loyal": [],
            "responsible": [],
            "shameless": [],
            "sneaky": [],
            "strange": [],
            "vengeful": [],
            "wise": [],
            "arrogant": [],
            "competitive": [],
            "grumpy": [],
            "cunning": [],
            "oblivious": [],
            "flamboyant": [],
            "rebellious": [],
            "sincere": [],
            "careful": [],

            # kit traits
            "unruly": [],
            "shy": [],
            "impulsive": [],
            "bullying": [],
            "attention-seeker": [],
            "charming": [],
            "self-conscious": [],
            "noisy": [],
            "skittish": [],
            "daydreamer": [],
            "fearless": [],
            "sweet": [],
            "know-it-all": [],
            "polite": [],
            "bossy": [],
            "bouncy": [],
        },
        "not_trait": {
            "troublesome": [],
            "lonesome": [],
            "fierce": [],
            "bloodthirsty": [],
            "cold": [],
            "childish": [],
            "playful": [],
            "charismatic": [],
            "bold": [],
            "daring": [],
            "nervous": [],
            "righteous": [],
            "insecure": [],
            "strict": [],
            "compassionate": [],
            "thoughtful": [],
            "ambitious": [],
            "confident": [],
            "adventurous": [],
            "calm": [],
            "gloomy": [],
            "faithful": [],
            "loving": [],
            "loyal": [],
            "responsible": [],
            "shameless": [],
            "sneaky": [],
            "strange": [],
            "vengeful": [],
            "wise": [],
            "arrogant": [],
            "competitive": [],
            "grumpy": [],
            "cunning": [],
            "oblivious": [],
            "flamboyant": [],
            "rebellious": [],
            "sincere": [],
            "careful": [],

            # kit traits
            "unruly": [],
            "shy": [],
            "impulsive": [],
            "bullying": [],
            "attention-seeker": [],
            "charming": [],
            "self-conscious": [],
            "noisy": [],
            "skittish": [],
            "daydreamer": [],
            "fearless": [],
            "sweet": [],
            "know-it-all": [],
            "polite": [],
            "bossy": [],
            "bouncy": [],
        },
        "backstory": {},
        "dies": {
            "True": []
        }
    },
    "r_c": {
        "age": {
            "any": [],
            "newborn": [],
            "kitten": [],
            "adolescent": [],
            "young adult": [],
            "adult": [],
            "senior adult": [],
            "senior": [],
        },
        "status": {
            "any": [],
            "newborn": [],
            "kitten": [],
            "apprentice": [],
            "warrior": [],
            "medicine cat apprentice": [],
            "medicine cat": [],
            "mediator apprentice": [],
            "mediator": [],
            "elder": [],
            "deputy": [],
            "leader": [],
        },
        "relationship_status": {
            "romantic": [],
            "platonic": [],
            "dislike": [],
            "comfortable": [],
            "jealousy": [],
            "admiration": [],
            "trust": []
        },
        "skill": {
            "TEACHER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "HUNTER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "FIGHTER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "RUNNER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLIMBER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SWIMMER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SPEAKER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "MEDIATOR": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLEVER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "INSIGHTFUL": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SENSE": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "KIT": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "STORY": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "LORE": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CAMP": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "HEALER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "STAR": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DUSK": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "OMEN": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DREAM": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLAIRVOYANT": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "PROPHET": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "GHOST": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
        },
        "not_skill": {
            "TEACHER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "HUNTER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "FIGHTER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "RUNNER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLIMBER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SWIMMER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SPEAKER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "MEDIATOR": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLEVER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "INSIGHTFUL": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "SENSE": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "KIT": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "STORY": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "LORE": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CAMP": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "HEALER": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "STAR": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DUSK": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "OMEN": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "DREAM": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "CLAIRVOYANT": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "PROPHET": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
            "GHOST": {
                "1": [],
                "2": [],
                "3": [],
                "4": []
            },
        },
        "trait": {
            "troublesome": [],
            "lonesome": [],
            "fierce": [],
            "bloodthirsty": [],
            "cold": [],
            "childish": [],
            "playful": [],
            "charismatic": [],
            "bold": [],
            "daring": [],
            "nervous": [],
            "righteous": [],
            "insecure": [],
            "strict": [],
            "compassionate": [],
            "thoughtful": [],
            "ambitious": [],
            "confident": [],
            "adventurous": [],
            "calm": [],
            "gloomy": [],
            "faithful": [],
            "loving": [],
            "loyal": [],
            "responsible": [],
            "shameless": [],
            "sneaky": [],
            "strange": [],
            "vengeful": [],
            "wise": [],
            "arrogant": [],
            "competitive": [],
            "grumpy": [],
            "cunning": [],
            "oblivious": [],
            "flamboyant": [],
            "rebellious": [],
            "sincere": [],
            "careful": [],

            # kit traits
            "unruly": [],
            "shy": [],
            "impulsive": [],
            "bullying": [],
            "attention-seeker": [],
            "charming": [],
            "self-conscious": [],
            "noisy": [],
            "skittish": [],
            "daydreamer": [],
            "fearless": [],
            "sweet": [],
            "know-it-all": [],
            "polite": [],
            "bossy": [],
            "bouncy": [],
        },
        "not_trait": {
            "troublesome": [],
            "lonesome": [],
            "fierce": [],
            "bloodthirsty": [],
            "cold": [],
            "childish": [],
            "playful": [],
            "charismatic": [],
            "bold": [],
            "daring": [],
            "nervous": [],
            "righteous": [],
            "insecure": [],
            "strict": [],
            "compassionate": [],
            "thoughtful": [],
            "ambitious": [],
            "confident": [],
            "adventurous": [],
            "calm": [],
            "gloomy": [],
            "faithful": [],
            "loving": [],
            "loyal": [],
            "responsible": [],
            "shameless": [],
            "sneaky": [],
            "strange": [],
            "vengeful": [],
            "wise": [],
            "arrogant": [],
            "competitive": [],
            "grumpy": [],
            "cunning": [],
            "oblivious": [],
            "flamboyant": [],
            "rebellious": [],
            "sincere": [],
            "careful": [],

            # kit traits
            "unruly": [],
            "shy": [],
            "impulsive": [],
            "bullying": [],
            "attention-seeker": [],
            "charming": [],
            "self-conscious": [],
            "noisy": [],
            "skittish": [],
            "daydreamer": [],
            "fearless": [],
            "sweet": [],
            "know-it-all": [],
            "polite": [],
            "bossy": [],
            "bouncy": [],
        },
        "backstory": {},
        "dies": {
            "True": []
        }
    },
}
invalid_records = {
    "location": {
        missing: [],
    },
    "season": {
        missing: []
    },
    "sub_type": {
    },
    "tags": {},
    "new_accessory": {},
    "weight": [],
    "injury": {
        "cats": {},
        "injuries": {},
        "scars": {},
        "history": {
            missing: []
        }

    },
    "m_c": {
        "age": {},
        "status": {},
        "relationship_status": {
            "invalid block": []
        },
        "skill": {},
        "not_skill": {},
        "trait": {},
        "not_trait": {},
        "backstory": {},
        "dies": {}
    },
    "r_c": {
        "age": {},
        "status": {},
        "relationship_status": {
            "invalid block": []
        },
        "skill": {},
        "not_skill": {},
        "trait": {},
        "not_trait": {},
        "backstory": {},
        "dies": {}
    },
}

history_scarrable = [
    "bite-wound",
    "cat-bite",
    "severe burn",
    "rat bite",
    "snake bite",
    "mangled tail",
    "mangled leg",
    "torn ear",
    "frostbite",
    "torn pelt",
    "damaged eyes",
    "quilled by porcupine",
    "claw-wound",
    "beak bite",
    "broken jaw",
    "broken back",
    "broken bone",
]
history_lethal = []
all_history = []

type_subtype = {
    "death": ["war", "murder", "old_age", "mass_death", "romance"],
    "injury": ["war", "romance"],
    "new": ["war", "adoption", "romance"],
    "misc": ["war", "murder_reveal", "accessory", "ceremony", "romance"]
}


def event_analysis(directory: str = None, blacklist: list[str] = None):
    global event_flat
    pa_header("Event analyzer\nv0.1", "For finding gaps in our current offering", trailing_newline=False)
    if directory is None:
        directory = "../resources/dicts/events/"

    if blacklist is None:
        blacklist = ["ceremonies", "death\\death_reactions", "death\\murder",
                     "disaster", "leader_den", "nutrition", "war.json"]

    events = pa_init(directory, blacklist)
    pa_split(events)

    event_flat = flatten(valid_records)
    event_count = len(tuple(event_flat))
    pa_problem_report()
    pa_overview_report(event_count)

    # pa_intersection(group1="location.any", group2="season.leaf-bare")
    # pa_intersection(group1="season.any", group2="location.any")


def pa_init(directory, blacklist) -> list:
    print("Preparing...")
    with open("../resources/dicts/conditions/injuries.json", "r") as f:
        data = ujson.loads(f.read())
    history_lethal = [lethal for lethal in data.values() if lethal["mortality"].values() != 0]

    all_history = history_scarrable + history_lethal
    print("OK\n")

    print("Gathering events...")
    all_data = []

    # used to hide/ignore invalid or undesirable json files
    for root, _, files in os.walk(directory):
        for filename in files:
            if not filename.endswith('.json'):
                continue

            filepath = os.path.join(root, filename)
            relative_path = os.path.relpath(str(filepath), directory)

            if relative_path.startswith(tuple(blacklist)):
                continue
            with open(filepath, 'r') as f:
                data = json.load(f)
                all_data.extend(data)
    print(f"OK\n")
    return all_data


# -------------------------------------------------
#               SPLITTEDY DOO DAH
# -------------------------------------------------
def pa_split(events):
    for event in events:
        event_id = event["event_id"]

        # DUPE EVENT NAME
        if event_id in all_ids.keys():
            dupe_ids.append(event_id)
            continue
        all_ids[event_id] = True

        # LOCATION
        if "location" not in event:
            invalid_records["location"][missing].append(event_id)
        else:  # event has a location
            pa_add_records_with_subtype(event_id, event["location"], valid_records["location"],
                                        invalid_records["location"])

        # SEASON
        if "season" in event:
            pa_add_records(event_id, event["season"], valid_records["season"], invalid_records["season"])
        else:
            invalid_records["season"][missing].append(event_id)

        # SUB TYPE
        if "sub_type" in event:
            event_type = event_id.split("_")[1]
            for genre in event["sub_type"]:
                if genre not in type_subtype[event_type]:
                    pa_invalid_record(event_id, event["sub_type"] + " in " + genre, invalid_records["sub_type"])
            pa_add_records(event_id, event["sub_type"], valid_records["sub_type"], invalid_records["sub_type"])

        # TAGS
        if "tags" in event:
            for tag in event["tags"]:
                if "no_body" in tag:
                    if not ("dies" in die_check for main_c in event["m_c"] for die_check in main_c):
                        pa_invalid_record(event_id, "[no_body but m_c doesn't die]",
                                          invalid_records["tags"])
                if "skill_trait_requirement" in tag:
                    if not (("skill" in skill_check for skill_check in event["m_c"]) or
                            ("trait" in trait_check for trait_check in event["m_c"]) or
                            ("skill" in skill_check for skill_check in event["r_c"]) or
                            ("trait" in trait_check for trait_check in event["r_c"])):
                        pa_invalid_record(event_id, "[skill_trait_requirement but no skill_traits]",
                                          invalid_records["tags"])

            pa_add_records_with_subtype(event_id, event["tags"], valid_records["tags"], invalid_records["tags"])

        if "new_accessory" in event:
            if not ("accessory" in e for e in event["sub_type"]):
                pa_invalid_record(event_id, "[no accessory tag]", invalid_records["new_accessory"])
            pa_add_records(event_id, event["new_accessory"],
                           valid_records["new_accessory"], invalid_records["new_accessory"],
                           ignore_categories=True)

        # WEIGHT - only care if it's missing
        if "weight" not in event:
            invalid_records["weight"].append(event_id)

        # CATTOS
        if "m_c" in event:
            rel_valid = True
            if "relationship_status" in event["m_c"] and "r_c" not in event:
                rel_valid = False

            pa_handle_cat(event_id, event["m_c"], valid_records["m_c"], invalid_records["m_c"], rel_valid=rel_valid)

        if "r_c" in event:
            pa_handle_cat(event_id, event["r_c"], valid_records["r_c"], invalid_records["r_c"])

        # INJURIES & HISTORY
        if "injury" in event:
            for injury in event["injury"]:
                # this horrible thing checks if any of the injuries cause death or scarring and have no history
                if "history" not in event and len(set(all_history).intersection(set(injury["injuries"]))) > 0:
                    print("Magical wound with no history!")
                    print(event_id)
                    pa_invalid_record(event_id, missing, invalid_records["injury"]["history"])
                    break

                if "cats" in injury:
                    pa_add_records(event_id, injury["cats"], valid_records["injury"]["cats"],
                                   invalid_records["injury"]["cats"],
                                   validation={"type": "startswith",
                                               "data": valid_records["injury"]["cats"].keys()})
                else:
                    pa_invalid_record(event_id, missing, invalid_records["injury"]["cats"])

                if "injuries" in injury:
                    pa_add_records(event_id, injury["injuries"], valid_records["injury"]["injuries"],
                                   invalid_records["injury"]["injuries"],
                                   ignore_categories=True)
                else:
                    pa_invalid_record(event_id, missing, invalid_records["injury"]["injuries"])

                if "scars" in injury:
                    pa_add_records(event_id, injury["scars"], valid_records["injury"]["scars"],
                                   invalid_records["injury"]["scars"],
                                   ignore_categories=True)
                elif injury["injuries"] in history_scarrable:
                    pa_invalid_record(event_id, "[scarrable but no scars]",
                                      invalid_records["injury"]["injuries"])


def pa_add_records(event_id, records, valid_log, error_log, validation=None, ignore_categories=False):
    if isinstance(records, list):
        for record in records:
            pa_add_record(event_id, record, valid_log, error_log, validation, ignore_categories)
    else:
        pa_add_record(event_id, records, valid_log, error_log, validation, ignore_categories)


def pa_add_records_with_subtype(event_id, records, valid_log, invalid_log,
                                allow_category=True, delineator=":"):
    for record in records:
        if delineator not in record:
            if allow_category:
                if record in valid_log:
                    if record == "any":
                        valid_log[record].append(event_id)
                        continue
                    if isinstance(valid_log[record], list):
                        valid_log[record].append(event_id)
                        continue

                    if "any" in valid_log[record]:
                        valid_log[record]["any"].append(event_id)
                    else:
                        if isinstance(valid_log[record], dict):
                            valid_log[record]["any"] = [event_id]
                        else:
                            valid_log[record] = [event_id]
                else:
                    pa_invalid_record(event_id, record, invalid_log)
        else:
            # we have specified subtypes
            data = record.split(delineator)
            category = data.pop(0)
            for value in data[0].split("_"):
                if category in valid_log and value in valid_log[category]:
                    valid_log[category][value].append(event_id)
                elif category in valid_log:
                    valid_log[category][str(value)] = [event_id]
                else:
                    pa_invalid_record(event_id, (category + delineator + value), invalid_log)


def pa_add_record(event_id, record, valid_log, invalid_log, validation=None, ignore_categories=False):
    if validation is not None:
        is_valid, record_name = pa_validate_record(record, validation)
        if is_valid:
            valid_log[record_name].append(event_id)
        else:
            pa_invalid_record(event_id, record_name, invalid_log)
        return

    if str(record) in valid_log:
        valid_log[str(record)].append(event_id)
    elif ignore_categories:
        valid_log[record] = [record]
    else:
        pa_invalid_record(event_id, record, invalid_log)


def pa_validate_record(record: str, validation: dict[str, str]):
    valid = tuple(validation["data"])
    if validation["type"] == "startswith":
        for check in valid:
            if record.startswith(check):
                return True, check
        return False, record

    elif validation["type"] == "match":
        return True, record if record in valid else False, "no"


def pa_invalid_record(event_id, record, invalid_log):
    if record in invalid_log:
        invalid_log[record].append(event_id)
    else:
        invalid_log[record] = [event_id]


def pa_handle_cat(event_id, cat, valid_log, error_log, rel_valid=True):
    # AGE
    if "age" in cat:
        pa_add_records(event_id, cat["age"], valid_log["age"], error_log["age"])

    # STATUS
    if "status" in cat:
        pa_add_records(event_id, cat["status"], valid_log["status"], error_log["status"])

    # RELATIONSHIP_STATUS
    if "relationship_status" in cat:
        validation = {
            "type": "startswith",
            "data": valid_log["relationship_status"].keys()
        }
        if rel_valid:
            pa_add_records(event_id, cat["relationship_status"],
                           valid_log["relationship_status"], error_log["relationship_status"], validation)
        else:
            error_log["relationship_status"]["invalid block"].append(event_id)

    # SKILL
    if "skill" in cat:
        pa_add_records_with_subtype(event_id, cat["skill"], valid_log["skill"], error_log["skill"], delineator=",")

    # NOT SKILL
    if "not_skill" in cat:
        pa_add_records_with_subtype(event_id, cat["not_skill"], valid_log["not_skill"], error_log["not_skill"],
                                    delineator=",")

    # TRAIT
    if "trait" in cat:
        pa_add_records(event_id, cat["trait"], valid_log["trait"], error_log["trait"])

    # NOT TRAIT
    if "not_trait" in cat:
        pa_add_records(event_id, cat["not_trait"],
                       valid_log["not_trait"], error_log["not_trait"])

    # BACKSTORY
    if "backstory" in cat:
        pa_add_records(event_id, cat["backstory"],
                       valid_log["backstory"], error_log["backstory"], ignore_categories=True)

    # DIES
    if "dies" in cat:
        pa_add_records(event_id, cat["dies"], valid_log["dies"], error_log["dies"])


# -----------------------
# GENERATE PROBLEM REPORT
# -----------------------


def pa_problem_report():
    pa_header("Error list", big=True, trailing_newline=False)
    # ERRORS FIRST
    if dupe_ids:
        pa_header("Duplicate IDs")
        pa_dump_records(dupe_ids)
        no_errors = False

    if len(invalid_records["location"]) > 0:
        pa_header("Invalid locations")
        pa_dump_records(invalid_records["location"])
        no_errors = False

    if len(invalid_records["season"]) > 0:
        pa_header("Invalid season")
        pa_dump_records(invalid_records["season"])
        no_errors = False

    if invalid_records["sub_type"]:
        pa_header("Missing/invalid subtypes")
        pa_dump_records(invalid_records["sub_type"])
        no_errors = False

    if invalid_records["tags"]:
        pa_header("Invalid tags")
        pa_dump_records(invalid_records["tags"])
        no_errors = False

    if invalid_records["weight"]:
        pa_header("Events missing a weighting")
        pa_dump_records(invalid_records["sub_type"])
        no_errors = False

    if invalid_records["new_accessory"]:
        pa_header("Accessory")
        pa_dump_records(invalid_records["new_accessory"])
        no_errors = False

    pa_header("Injury Errors", trailing_newline=False, big=True)
    no_injury_errors = True

    if any(invalid_records["injury"]["cats"].values()):
        pa_header("Missing/invalid cats")
        pa_dump_records(invalid_records["injury"]["cats"])
        no_injury_errors = False

    if any(invalid_records["injury"]["injuries"].values()):
        pa_header("Injuries with no... injuries")
        pa_dump_records(invalid_records["injury"]["injuries"])
        no_injury_errors = False

    if any(invalid_records["injury"]["scars"].values()):
        pa_header("Injuries with invalid scars")
        pa_dump_records(invalid_records["injury"]["scars"])
        no_injury_errors = False

    if no_injury_errors:
        print("No errors found :)")

    pa_header("m_c Errors", trailing_newline=False, big=True)
    no_mc_errors = True

    if any(invalid_records["m_c"]["age"].values()):
        pa_header(normal_text="Age")
        pa_dump_records(invalid_records["m_c"]["age"])
        no_mc_errors = False

    if invalid_records["m_c"]["status"]:
        pa_header(normal_text="Status")
        pa_dump_records(invalid_records["m_c"]["status"])
        no_mc_errors = False

    if invalid_records["m_c"]["relationship_status"]:
        pa_header(normal_text="Relationship status")
        pa_dump_records(invalid_records["m_c"]["relationship_status"])
        no_mc_errors = False

    if invalid_records["m_c"]["skill"]:
        pa_header(normal_text="Skill")
        pa_dump_records(invalid_records["m_c"]["skill"])
        no_mc_errors = False

    if invalid_records["m_c"]["not_skill"]:
        pa_header(normal_text="Not skill")
        pa_dump_records(invalid_records["m_c"]["not_skill"])
        no_mc_errors = False

    if any(invalid_records["m_c"]["trait"].values()):
        pa_header(normal_text="Trait")
        pa_dump_records(invalid_records["m_c"]["trait"])
        no_mc_errors = False

    if any(invalid_records["m_c"]["not_trait"].values()):
        pa_header(normal_text="Not trait")
        pa_dump_records(invalid_records["m_c"]["not_trait"])
        no_mc_errors = False

    if any(invalid_records["m_c"]["backstory"].values()):
        pa_header(normal_text="Backstory")
        pa_dump_records(invalid_records["m_c"]["backstory"])
        no_mc_errors = False

    if any(invalid_records["m_c"]["dies"].values()):
        pa_header(normal_text="Death flag")
        pa_dump_records(invalid_records["m_c"]["dies"])
        no_mc_errors = False

    if no_mc_errors:
        print("No errors found :)")

    pa_header("r_c Errors", trailing_newline=False, big=True)
    no_rc_errors = True

    if any(invalid_records["r_c"]["age"].values()):
        pa_header(normal_text="Age")
        pa_dump_records(invalid_records["r_c"]["age"])
        no_rc_errors = False

    if invalid_records["r_c"]["status"]:
        pa_header(normal_text="Status")
        pa_dump_records(invalid_records["r_c"]["status"])
        no_rc_errors = False

    if invalid_records["r_c"]["relationship_status"]:
        pa_header(normal_text="Relationship status")
        pa_dump_records(invalid_records["r_c"]["relationship_status"])
        no_rc_errors = False

    if invalid_records["r_c"]["skill"]:
        pa_header(normal_text="Skill")
        pa_dump_records(invalid_records["r_c"]["skill"])
        no_rc_errors = False

    if invalid_records["r_c"]["not_skill"]:
        pa_header(normal_text="Not skill")
        pa_dump_records(invalid_records["r_c"]["not_skill"])
        no_rc_errors = False

    if any(invalid_records["r_c"]["trait"].values()):
        pa_header(normal_text="Trait")
        pa_dump_records(invalid_records["r_c"]["trait"])
        no_rc_errors = False

    if any(invalid_records["r_c"]["not_trait"].values()):
        pa_header(normal_text="Not trait")
        pa_dump_records(invalid_records["r_c"]["not_trait"])
        no_rc_errors = False

    if any(invalid_records["r_c"]["backstory"].values()):
        pa_header(normal_text="Backstory")
        pa_dump_records(invalid_records["r_c"]["backstory"])
        no_rc_errors = False

    if any(invalid_records["r_c"]["dies"].values()):
        pa_header(normal_text="Death flag")
        pa_dump_records(invalid_records["r_c"]["dies"])
        no_rc_errors = False

    if no_rc_errors:
        print("No errors found :)")


def pa_overview_report(count):
    pa_header("Overview", big=True, trailing_newline=True)
    print(f"Total number of events: {count}\n")

    print("Breakdown by location:")
    pa_subgroup_report(valid_records["location"], True)

    print("\nBreakdown by season:")
    pa_group_report(valid_records["season"])

    print("\nBreakdown by sub-type:")
    pa_group_report(valid_records["sub_type"])

    print("\nBreakdown by tags:")
    pa_subgroup_report(valid_records["tags"], True)

    print("\nBreakdown by accessory gained:")
    pa_subgroup_report(valid_records["new_accessory"])


def pa_group_report(records, detailed=False):
    output = dict(sorted(records.items(), key=lambda x: len(x[1]), reverse=True))
    for name, group in output.items():
        print(f"{indent}{name}: {len(group)}")


def pa_subgroup_report(records, detailed=False):
    records = dict(sorted(records.items(), key=lambda x: pa_sort_subgroup(x), reverse=True))
    for name, group in records.items():
        if not isinstance(group, list):
            group = dict(sorted(group.items(), key=lambda x: len(x[1]), reverse=True))
        groupcount = sum(len(sub) for sub in group.values()) if not isinstance(group, list) else len(group)
        print(f"{indent}{name}: {groupcount}")
        if name == "any" or not detailed or not isinstance(group, dict):
            continue
        for name_sub, subgroup in group.items():
            print(f"{indent}{indent}{indent}{name_sub}: {len(subgroup)}")

def pa_sort_subgroup(group):
    return sum(len(sub) for sub in group[1]) if not isinstance(group[1], list) else len(group[1])


def pa_set_prep(group1, group2):
    left = []
    group1_key = group1.rsplit(".", 1)
    if "not_skill" in group1_key[0]:
        a = {key: val for key, val in event_flat.items()
             if key.startswith(group1_key[0])
             and key.endswith(str(range(1, int(group1_key[1]) + 1)))}


def pa_intersection(group1: str, group2: str, subgroup1=None, subgroup2=None):
    group1_key = group1.rsplit(".", 1)
    group2_key = group2.rsplit(".", 1)
    a = {key: val for key, val in event_flat.items() if
         key.startswith(group1_key[0] if group1_key[1] == "any" else group1)}
    left = []
    for value in a.values():
        left += value
    b = {key: val for key, val in event_flat.items() if
         key.startswith(group2_key[0] if group2_key[1] == "any" else group2)}
    right = []
    for value in b.values():
        right += value

    matching_events = list(filter(lambda x: x in set(left), set(right)))

    print(
        f"There are {len(matching_events)} events that match \"{group1.replace('.', ' -> ')}\" and \"{group2.replace('.', ' -> ')}\".")


def pa_innerjoin(group1, group1_sub, group2, group2_sub):
    if group1_sub is not None and group1_sub is not "any":
        a = valid_records[group1]["any"] + valid_records[group1][group1_sub]
    else:
        a = recursive_items(valid_records[group1])

    if group2_sub is not None and group2_sub is not "any":
        b = valid_records[group2]["any"] + valid_records[group2][group2_sub]
    else:
        b = recursive_items(valid_records[group2])

    out = list(set(a) & set(b))
    return out


def flatten(dictionary, parent_key='', separator='.'):
    items = []
    for key, value in dictionary.items():
        new_key = parent_key + separator + key if parent_key else key
        if isinstance(value, MutableMapping):
            items.extend(flatten(value, new_key, separator=separator).items())
        else:
            items.append((new_key, value))
    return dict(items)


# -------------
#   UTILITIES
# -------------

def pa_header(title: str = None, normal_text: str = None, leading_newline=True, trailing_newline=False, big=False):
    if leading_newline:
        print("")
    pa_dashes(big)
    if title is not None:
        print(title.upper())
        if normal_text is not None:
            print("")
    if normal_text is not None:
        print(normal_text)
    pa_dashes(big)
    if trailing_newline:
        print("")


def pa_dashes(big=False):
    if big:
        print("-----------------------------------------------------")
        return
    print("--------------------------")


def pa_dump_records(records):
    if isinstance(records, list):
        for item in records:
            print(item)
        return

    elif isinstance(records, dict):
        for name, record in records.items():
            if not record:
                continue
            print(name)
            for item in record:
                print(indent + item)


if __name__ == "__main__":
    event_analysis()
