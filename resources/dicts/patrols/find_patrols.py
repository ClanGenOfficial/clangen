import ujson
import collections
import os
from os.path import exists as file_exists

""" This script exists to count and catalogue all patrols.   """


ALL_BAD_PATROLS = []


def find_bad_patrol(path):
    
    with open(path, "r") as read_file:
        patrols = ujson.loads(read_file.read())
    
    if not patrols:
        return
    
    if type(patrols[0]) != dict:
        print(path, "is not in the correct patrol format. It may not be a patrol .json.")
        return
    
    for inter_patrol in patrols:
        for inter_outcome in inter_patrol.get("success_outcomes", ()):
            if "s_c" in inter_outcome["text"] and not (inter_outcome.get("stat_skill") or inter_outcome.get("stat_trait")):
                ALL_BAD_PATROLS.append((path, inter_patrol["patrol_id"]))
                continue
                
        for inter_outcome in inter_patrol.get("fail_outcomes", ()):
            if "s_c" in inter_outcome["text"] and not (inter_outcome.get("stat_skill") or inter_outcome.get("stat_trait")):
                ALL_BAD_PATROLS.append((path, inter_patrol["patrol_id"]))
                continue
                
        for inter_outcome in inter_patrol.get("antag_fail_outcomes", ()):
            if "s_c" in inter_outcome["text"] and not (inter_outcome.get("stat_skill") or inter_outcome.get("stat_trait")):
                ALL_BAD_PATROLS.append((path, inter_patrol["patrol_id"]))
                continue
                
        for inter_outcome in inter_patrol.get("antag_success_outcomes", ()):
            if "s_c" in inter_outcome["text"] and not (inter_outcome.get("stat_skill") or inter_outcome.get("stat_trait")):
                ALL_BAD_PATROLS.append((path, inter_patrol["patrol_id"]))
                continue


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
    find_bad_patrol(pa)
    
for x in ALL_BAD_PATROLS:
    print(x)

