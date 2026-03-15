from utils.json_compat import json
import os

_resource_directory = "resources/dicts/conditions/"

with open(
    os.path.normpath("resources/dicts/backstories.json"), "r", encoding="utf-8"
) as read_file:
    BACKSTORIES = json.loads(read_file.read())

with open(
    os.path.normpath(f"{_resource_directory}illnesses.json"), "r", encoding="utf-8"
) as read_file:
    ILLNESSES = json.loads(read_file.read())

with open(
    os.path.normpath(f"{_resource_directory}injuries.json"), "r", encoding="utf-8"
) as read_file:
    INJURIES = json.loads(read_file.read())

with open(
    os.path.normpath(f"{_resource_directory}permanent_conditions.json"),
    "r",
    encoding="utf-8",
) as read_file:
    PERMANENT = json.loads(read_file.read())
