from enum import StrEnum
from random import choice
from typing import Dict, Union, List

import ujson

_poi_names = set()
_poi_tags = set()

_poi_by_tags = {}

_undiscovered_poi_remaining = 3

with open("resources/dicts/points_of_interest.json", "r", encoding="utf-8") as f:
    _poi_data = ujson.load(f)


class PoiType(StrEnum):
    GATHERING = "gathering"
    MOONPLACE = "moonplace"
    TERRAIN = "terrain"


def get_poi_names_set():
    return _poi_names


def get_poi_tags_set():
    """
    Return a set containing all POI tags
    :return:
    """
    return _poi_tags


def get_random_poi_by_tag(tag):
    """
    Return a random POI name that fits the requested tag/s.
    :param tag:
    :return: string name of POI that fits.
    """
    return choice(_poi_by_tags.get(tag, ["MISSING_POI"]))


def add_poi(name, elements):
    """
    Add a new POI to the Clan
    :param name:
    :param elements:
    :return:
    """
    _poi_names.update([name])
    _poi_tags.update(elements["tags"])
    _poi_tags.update(tag.split(":", 1)[0] for tag in elements["tags"] if ":" in tag)

    global _poi_by_tags
    for tag in elements["tags"]:
        if tag in _poi_by_tags:
            _poi_by_tags[tag].append(name)
        else:
            _poi_by_tags[tag] = [name]


def get_poi_save_dict():
    return {
        "gathering": [name for name in _poi_names if name.startswith("gather_")],
        "moonplace": [name for name in _poi_names if name.startswith("moon_")],
        "terrain": [name for name in _poi_names if name.startswith("terrain_")],
    }


def load_pois(save_data: Dict[str, List[str]]):
    for category, data in save_data.items():
        for poi in data:
            add_poi(poi, _poi_data[poi])


def clear_pois():
    """
    Clear the PoI system (e.g., when creating a new Clan or loading)
    :return:
    """
    _poi_tags.clear()
    _poi_names.clear()

    _poi_by_tags.clear()

    global _undiscovered_poi_remaining
    _undiscovered_poi_remaining = 3


def generate_and_add_new_poi(
    biome: str, category: PoiType, possible_pois=None, random_choice_func=choice
):
    """
    Choose and add an appropriate POI from the pool, based on the Clan biome and whether they already have a given POI type
    :param biome: the Clan's current biome
    :param category: The requested POI type (moonplace, gathering, or terrain)
    :param possible_pois: Optional, list of all possible POIs to choose from
    :param random_choice_func: Optional, for testing only - replace RNG functions
    :return: None
    """
    possible_pois = possible_pois if possible_pois else _poi_data.copy()

    # first, remove the POIs that are already in the Clan.
    for key in _poi_names:
        possible_pois.pop(key, None)

    # now exclude anything that isn't either an "any" biome or the actual biome
    possible_pois = {
        k: v
        for k, v in possible_pois.items()
        if set(v["biome"]) & {"any", biome.casefold()}
    }

    # keep only the correct type of POI
    possible_pois = {
        k: v for k, v in possible_pois.items() if v["category"] == category
    }

    if not possible_pois:
        raise Exception(
            "Tried to generate a new point of interest, but no suitable candidate was found"
        )

    chosen_poi = random_choice_func(list(possible_pois.keys()))
    add_poi(chosen_poi, possible_pois[chosen_poi])
