import collections
import os
from os.path import exists as file_exists

import ujson

""" This script exists to count and catalogue all patrols.   """

ALL_PATROLS = []
DETAILS = {}

SPRITES_USED = []
EXPLICIT_PATROL_ART = None


def get_patrol_details(path):
    global ALL_PATROLS
    global DETAILS
    global EXPLICIT_PATROL_ART
    patrols = None

    if path == ".\explicit_patrol_art.json":
        with open(path, "r") as read_file:
            EXPLICIT_PATROL_ART = ujson.loads(read_file.read())
    else:
        try:
            with open(path, "r") as read_file:
                patrols = ujson.loads(read_file.read())
        except:
            print(f"Something went wrong with {path}")

    if not patrols:
        return

    if type(patrols[0]) != dict:
        print(
            path, "is not in the correct patrol format. It may not be a patrol .json."
        )
        return

    if not patrols:
        return

    if type(patrols[0]) != dict:
        print(
            path, "is not in the correct patrol format. It may not be a patrol .json."
        )
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


def check_patrol_sprites():
    explicit_sprite = False
    needs_sprite = False
    available_sprite = False

    path = "resources/images/patrol_art/"

    if ID in EXPLICIT_PATROL_ART:
        explicit_sprite = True

    image_name = ID
    # this stays false until an acceptable image is found
    image_found = False

    # looking for exact patrol ID
    exists = file_exists(f"{path}{image_name}.png")
    if exists:
        has_patrol_sprite.append(ID)
        image_found = True
        available_sprite = True
        SPRITES_USED.append(image_name)

    # looking for patrol ID without numbers
    if not image_found:
        image_name = "".join([i for i in image_name if not i.isdigit()])

        exists = file_exists(f"{path}{image_name}.png")
        if exists:
            available_sprite = True
            image_found = True
            SPRITES_USED.append(image_name)

    # looking for patrol ID with biome indicator replaced with 'gen'
    # if that isn't found then patrol type placeholder will be used
    if not image_found:
        image_name = "".join([i for i in image_name if not i.isdigit()])
        image_name = image_name.replace("fst_", "gen_")
        image_name = image_name.replace("mtn_", "gen_")
        image_name = image_name.replace("pln_", "gen_")
        image_name = image_name.replace("bch_", "gen_")
        exists = file_exists(f"{path}{image_name}.png")
        if exists:
            available_sprite = True
            SPRITES_USED.append(image_name)
        else:
            needs_sprite = True

    return explicit_sprite, available_sprite, needs_sprite


root_dir = "../patrols"
file_set = set()

for dir_, _, files in os.walk(root_dir):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, root_dir)
        print(rel_dir)
        rel_file = os.path.join(rel_dir, file_name)
        print(rel_file)
        if os.path.splitext(rel_file)[-1].lower() == ".json":
            file_set.add(rel_file)

for pa in file_set:
    get_patrol_details(pa)

path = "../resources"

for root, dirs, files in os.walk(path):
    for name in files:
        print(os.path.join(root, name))
    for name in dirs:
        print(os.path.join(root, name))

# Now that we have everything gathered, lets do some checks.

print(
    """
You can ask me to do a few different things! But make sure to ask it correctly. When prompted, please use one of the following commands:
Check patrol IDs
Check patrol sprites
Check for certain patrols
"""
)
task = input("What would you like to do? ")

if "patrol ids" in task.casefold():
    # AT CHECK TO MAKE SURE ALL PATROL IDs ARE UNIQUE
    duplicates = [
        item for item, count in collections.Counter(ALL_PATROLS).items() if count > 1
    ]
    if duplicates:
        print("There are duplicate patrols IDs:")
        for d in duplicates:
            print(d)
        print("-----")
    else:
        print("All patrol IDs are unique. \n\n")

if "patrol sprite" in task.casefold():

    explicit_art = []
    has_patrol_sprite = []
    needs_patrol_sprite = []

    for ID in ALL_PATROLS:
        explicit, available, need = check_patrol_sprites()

        if explicit:
            explicit_art.append(ID)
        if available:
            has_patrol_sprite.append(ID)
        elif need:
            needs_patrol_sprite.append(ID)

# We can do a lot with these sets we have just generated! For example:

"""## FINDING ALL PATROLS IN THE FOREST BIOME WITH NEW_CAT TAG

forest_new_cat = DETAILS["BIOME_forest"].intersection(DETAILS["TAG_new_cat"])
print("Number of patrols with the new_cat tag in the forest biome: ", len(forest_new_cat))
print("Patrol IDs: ", forest_new_cat)

## FINDING PATROLS WITH DEATH TAG AND MIN_CAT = 1 and MAX_CATS = 1

looking = DETAILS["TAG_death"].intersection(DETAILS["MIN_1"], DETAILS["MAX_1"])
print("Number of patrols death tag and min_cat = 1 and max_cats = 1: ", len(looking))
print("Patrol IDs: ", looking)"""
