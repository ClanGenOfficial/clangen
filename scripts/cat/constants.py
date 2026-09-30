import ujson
import os

_resource_directory = "resources/dicts/conditions/"

with open(
    os.path.normpath("resources/dicts/backstories.json"), "r", encoding="utf-8"
) as read_file:
    BACKSTORIES = ujson.loads(read_file.read())

with open(
    os.path.normpath(f"{_resource_directory}temporary_conditions/minor.json"),
    "r",
    encoding="utf-8",
) as read_file:
    TEMPORARY_CONDITIONS = ujson.loads(read_file.read())
with open(
    os.path.normpath(f"{_resource_directory}temporary_conditions/major.json"),
    "r",
    encoding="utf-8",
) as read_file:
    TEMPORARY_CONDITIONS.update(ujson.loads(read_file.read()))
with open(
    os.path.normpath(f"{_resource_directory}temporary_conditions/severe.json"),
    "r",
    encoding="utf-8",
) as read_file:
    TEMPORARY_CONDITIONS.update(ujson.loads(read_file.read()))

with open(
    os.path.normpath(f"{_resource_directory}permanent_conditions/minor.json"),
    "r",
    encoding="utf-8",
) as read_file:
    PERMANENT_CONDITIONS = ujson.loads(read_file.read())
with open(
    os.path.normpath(f"{_resource_directory}permanent_conditions/major.json"),
    "r",
    encoding="utf-8",
) as read_file:
    PERMANENT_CONDITIONS.update(ujson.loads(read_file.read()))
with open(
    os.path.normpath(f"{_resource_directory}permanent_conditions/severe.json"),
    "r",
    encoding="utf-8",
) as read_file:
    PERMANENT_CONDITIONS.update(ujson.loads(read_file.read()))
