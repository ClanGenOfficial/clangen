import json
import os

missing = "[tag missing]"

# Please don't mind this truly horrifying list of global variables.
# Lord have mercy on my soul
all_ids = {}
dupe_ids = []

location = {
    "any": [],
    "beach": {
        "any": [],
        "camp1": [],
        "camp2": [],
        "camp3": [],
        "camp4": [],
    },
    "desert": {
        "any": [],
        "camp1": [],
        "camp2": [],
        "camp3": [],
        "camp4": [], },
    "forest": {
        "any": [],
        "camp1": [],
        "camp2": [],
        "camp3": [],
        "camp4": [], },
    "mountainous": {
        "any": [],
        "camp1": [],
        "camp2": [],
        "camp3": [],
        "camp4": [], },
    "plains": {
        "any": [],
        "camp1": [],
        "camp2": [],
        "camp3": [],
        "camp4": [], },
    "wetlands": {
        "any": [],
        "camp1": [],
        "camp2": [],
        "camp3": [],
        "camp4": [], }
}
season = {
    "NONE": [],
    "any": [],
    "newleaf": [],
    "greenleaf": [],
    "leaf-fall": [],
    "leaf-bare": []
}
sub_type = {}
tags = {}
new_accessory = {}
injury = {
    "cats": {
        "m_c": [],
        "r_c": [],
    },
    "injuries": {},
    "scars": {}
}
m_c = {
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
    "status": {},
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
    "skill": {},
    "not_skill": {},
    "trait": {},
    "not_trait": {},
    "backstory": {},
    "dies": {
        "true": [],
        "false": []
    }
}
r_c = {
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
    "skill": {},
    "not_skill": {},
    "trait": {},
    "not_trait": {},
    "backstory": {},
    "dies": {
        "true": [],
        "false": []
    }
}

invalid_records = {
    "location": {
        missing: [],
    },
    "season": {
        missing: []
    },
    "sub_type": {},
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
        "dies": {
            "true": [],
            "false": []
        }
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
        "dies": {
            "true": [],
            "false": []
        }
    },
}


def event_analysis(directory: str = None, blacklist: list[str] = None):
    # 1: pull all the event scripts
    # 2
    pa_header("Event analyser\nv0.1", "For finding gaps in our current offering")
    if directory is None:
        directory = "../resources/dicts/events/"

    if blacklist is None:
        blacklist = ["ceremonies", "death\\death_reactions", "death\\murder",
                     "disaster", "leader_den", "nutrition", "war.json"]

    events = pa_init(directory, blacklist)
    dataset = pa_split(events)


def pa_init(directory, blacklist) -> list:
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
            pa_add_records_with_subtype(event_id, event["location"], location, invalid_records["location"])

        # SEASON
        if "season" in event:
            pa_add_records(event_id, event["season"], season, invalid_records["season"])
        else:
            invalid_records["season"][missing].append(event_id)

        # SUB TYPE
        if "sub_type" in event:
            pa_add_records(event_id, event["sub_type"], sub_type, invalid_records["sub_type"])

        # WEIGHT - only care if it's missing
        if "weight" not in event:
            invalid_records["weight"].append(event_id)

        # CATTOS
        if "m_c" in event:
            rel_valid = True
            if "relationship_status" in event["m_c"] and "r_c" not in event:
                rel_valid = False

            pa_handle_cat(event_id, event["m_c"], m_c, invalid_records["m_c"], rel_valid=rel_valid)

        if "r_c" in event:
            pa_handle_cat(event_id, event["r_c"], r_c, invalid_records["r_c"])

        # INJURIES
        if "injury" in event:
            if "history_text" not in event["injury"]:
                print("Magical wound with no history!")
                print(event_id)
                pa_invalid_record(event_id, missing, invalid_records["injury"]["history"])
            # pa_add_records(event_id, event["injury"], injury, invalid_records["injury"])


def pa_add_records(event_id, records, valid_log, error_log, validation=None):
    if isinstance(records, list):
        for record in records:
            pa_add_record(event_id, record, valid_log, error_log, validation)
    else:
        pa_add_record(event_id, records, valid_log, error_log, validation)


def pa_add_records_with_subtype(event_id, records, valid_log, invalid_log,
                                allow_category=True, no_subtype="[no subtype]"):
    for record in records:
        if ":" not in record:
            if allow_category:
                if record in valid_log:
                    if record == "any":
                        valid_log[record].append(event_id)
                    else:
                        valid_log[record]["any"].append(event_id)
                else:
                    pa_invalid_record(event_id, record, invalid_log)
        else:
            # we have specified subtypes
            data = record.split(":")
            category = data.pop(0)
            for value in data[0].split("_"):
                if category in valid_log and value in valid_log[category]:
                    valid_log[category][value].append(event_id)
                elif category in valid_log:
                    valid_log[category][value] = [event_id]
                else:
                    pa_invalid_record(event_id, (category + ":" + value), invalid_log)


def pa_add_record(event_id, record, valid_log, invalid_log, validation=None):
    if validation is not None:
        is_valid, record_name = pa_validate_record(record, validation)
        if is_valid:
            valid_log[record_name].append(event_id)
        else:
            pa_invalid_record(event_id, record_name, invalid_log)
        return

    if record in valid_log:
        valid_log[record].append(event_id)
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
        pa_add_records(event_id, cat["skill"], valid_log["skill"], error_log["skill"])

    # NOT SKILL
    if "not_skill" in cat:
        pa_add_records(event_id, cat["not_skill"], valid_log["not_skill"], error_log["not_skill"])

    # TRAIT
    if "trait" in cat:
        pa_add_records(event_id, cat["trait"], valid_log["trait"], error_log["trait"])

    # NOT TRAIT
    if "not_trait" in cat:
        pa_add_records(event_id, cat["not_trait"], valid_log["not_trait"], error_log["not_trait"])

    # BACKSTORY
    if "backstory" in cat:
        pa_add_records(event_id, cat["backstory"], valid_log["backstory"], error_log["backstory"])

    # DIES
    if "dies" in cat:
        pa_add_records(event_id, cat["dies"], valid_log["dies"], error_log["dies"])


# -------------
#   UTILITIES
# -------------

def pa_header(title: str = None, normal_text: str = None):
    print("-------------------------")
    if title is not None:
        print(title.upper())
        if normal_text is not None:
            print("")
    if normal_text is not None:
        print(normal_text)
    print("-------------------------\n")


if __name__ == "__main__":
    event_analysis()
