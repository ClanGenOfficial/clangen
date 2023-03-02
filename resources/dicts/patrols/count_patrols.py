import ujson
import collections
import os

""" This script exists to count and catalogue all patrols.   """

ALL_PATROLS = []
DETAILS = {}

def get_patrol_details(path):
    global ALL_PATROLS
    global DETAILS

    try:
        with open(path, "r") as read_file:
            patrols = ujson.loads(read_file.read())
    except:
        print(f"Error in {path}")
        return

    if not patrols:
        return

    if type(patrols[0]) != dict:
        print(path, "is not in the correct patrol format. It may not be a patrol .json.")
        return

    for p_ in patrols:
        ALL_PATROLS.append(p_["patrol_id"])

        # Grab tags
        for tag in p_["tags"]:
            if "TAG_" + tag in DETAILS:
                DETAILS["TAG_" + tag].add(p_["patrol_id"])
            else:
                DETAILS["TAG_" + tag] = {p_["patrol_id"]}

        # Grab biome.
        if "BIOME_" + p_["biome"] in DETAILS:
            DETAILS["BIOME_" + p_["biome"]].add(p_["patrol_id"])
        else:
            DETAILS["BIOME_" + p_["biome"]] = {p_["patrol_id"]}

        # Grab Max Cats
        if "MAX_" + str(p_["max_cats"]) in DETAILS:
            DETAILS["MAX_" + str(p_["max_cats"])].add(p_["patrol_id"])
        else:
            DETAILS["MAX_" + str(p_["max_cats"])] = {p_["patrol_id"]}

        # Grab Min Cats
        if "MIN_" + str(p_["min_cats"]) in DETAILS:
            DETAILS["MIN_" + str(p_["min_cats"])].add(p_["patrol_id"])
        else:
            DETAILS["MIN_" + str(p_["min_cats"])] = {p_["patrol_id"]}


root_dir = "../patrols"
file_set = set()

for dir_, _, files in os.walk(root_dir):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, root_dir)
        rel_file = os.path.join(rel_dir, file_name)
        if os.path.splitext(rel_file)[-1].lower() == ".json":
            file_set.add(rel_file)

for pa in file_set:
    get_patrol_details(pa)

# Now that we have everything gathered, lets do some checks.

# AT CHECK TO MAKE SURE ALL PATROL IDs ARE UNIQUE
duplicates = [item for item, count in collections.Counter(ALL_PATROLS).items() if count > 1]
if duplicates:
    print("There are duplicate patrols IDs:")
    for d in duplicates:
        print(d)
    print("-----")
else:
    print("All patrol IDs are unique. \n\n")

# We can do a lot with these sets we have just generated! For example:

## FINDING ALL PATROLS IN THE FOREST BIOME WITH NEW_CAT TAG

forest_new_cat = DETAILS["BIOME_forest"].intersection(DETAILS["TAG_new_cat"])
print("Number of patrols with the new_cat tag in the forest biome: ", len(forest_new_cat))
print("Patrol IDs: ", forest_new_cat)

## FINDING PATROLS WITH DEATH TAG AND MIN_CAT = 1 and MAX_CATS = 1

looking = DETAILS["TAG_death"].intersection(DETAILS["MIN_1"], DETAILS["MAX_1"])
print("Number of patrols death tag and min_cat = 1 and max_cats = 1: ", len(looking))
print("Patrol IDs: ", looking)









