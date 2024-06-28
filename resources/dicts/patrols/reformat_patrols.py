import json as ujson
import collections
import os
from os.path import exists as file_exists
import re

""" This script exists to count and catalogue all patrols.   """

ALL_PATROLS = []
DETAILS = {}

SPRITES_USED = []
EXPLICIT_PATROL_ART = None


def history_regex_helper(m):
    capture_group = m.group(1)
    inner_strings = re.findall(r'".*?"|null', capture_group)
    new_history_dict = {}
    new_labels = ["scar", "reg_death", "lead_death"]

    for i, text in enumerate(inner_strings):
        text = text.replace('"', "")
        if text != "null":
            new_history_dict[new_labels[i]] = text

    if not new_history_dict:
        return ""

    dict_text = ujson.dumps(new_history_dict, indent=4)
    dict_text = dict_text.replace(
        "\/", "/"
    )  # ujson tries to escape "/", but doesn't end up doing a good job.

    # Add some indent
    dict_text = dict_text.split("\n")
    for i in range(1, len(dict_text)):
        dict_text[i] = "    " + dict_text[i]

    dict_text = "\n".join(dict_text)
    # add history text:
    dict_text = '"history_text": ' + dict_text

    return dict_text


def reformat_history_text(path):
    try:
        with open(path, "r") as read_file:
            patrols = read_file.read()
            patrol_ujson = ujson.loads(patrols)

    except:
        print(f"Something went wrong with {path}")

    if not patrol_ujson:
        return

    if type(patrol_ujson[0]) != dict:
        print(
            path, "is not in the correct patrol format. It may not be a patrol .json."
        )
        return

    patrols = re.sub(
        r'"history_text" ?\: ?\[(.*?)\]', history_regex_helper, patrols, flags=re.DOTALL
    )

    with open(path, "w") as write_file:
        write_file.write(patrols)


root_dir = "../patrols"
file_set = set()

for dir_, _, files in os.walk(root_dir):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, root_dir)
        rel_file = os.path.join(rel_dir, file_name)
        if os.path.splitext(rel_file)[-1].lower() == ".json":
            file_set.add(rel_file)

for pa in file_set:
    reformat_history_text(pa)


def patrol_success_regex_helper(m):
    capture_group = m.group(1)
    inner_strings = re.findall(r'".*?"|null', capture_group)
    new_success_dict = {}
    new_labels = ["unscathed_common", "unscathed_rare", "stat_skill", "stat_trait"]

    for i, text in enumerate(inner_strings):
        text = text.replace('"', "")
        if text != "null":
            new_success_dict[new_labels[i]] = text

    if not new_success_dict:
        return ""

    dict_text = ujson.dumps(new_success_dict, indent=4)
    dict_text = dict_text.replace(
        "\/", "/"
    )  # ujson tries to escape "/", but doesn't end up doing a good job.

    # Add some indent
    dict_text = dict_text.split("\n")
    for i in range(1, len(dict_text)):
        dict_text[i] = "    " + dict_text[i]

    dict_text = "\n".join(dict_text)
    # add success text:
    dict_text = '"success_text": ' + dict_text

    return dict_text


def reformat_success_text(path):
    try:
        with open(path, "r") as read_file:
            patrols = read_file.read()
            patrol_ujson = ujson.loads(patrols)

    except:
        print(f"Something went wrong with {path}")

    if not patrol_ujson:
        return

    if type(patrol_ujson[0]) != dict:
        print(
            path, "is not in the correct patrol format. It may not be a patrol .json."
        )
        return

    patrols = re.sub(
        r'"success_text" ?\: ?\[(.*?)\]',
        patrol_success_regex_helper,
        patrols,
        flags=re.DOTALL,
    )

    with open(path, "w") as write_file:
        write_file.write(patrols)


root_dir = "../patrols"
file_set = set()

for dir_, _, files in os.walk(root_dir):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, root_dir)
        rel_file = os.path.join(rel_dir, file_name)
        if os.path.splitext(rel_file)[-1].lower() == ".json":
            file_set.add(rel_file)

print(file_set)
for pa in file_set:
    reformat_success_text(pa)
