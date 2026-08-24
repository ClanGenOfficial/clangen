from random import getrandbits
from typing import Optional, Literal

from scripts.clan_package.settings import get_clan_setting
from scripts.config import get_config
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource

loaded_events: dict[str, list[PatrolEvent]] = {}


def get_patrol_list(
    patrol_type: str,
    other_clan_rep: Optional[Literal["hostile", "ally", "neutral"]] = None,
    outsider_rep: Optional[Literal["hostile", "welcoming", "neutral"]] = None,
) -> list[PatrolEvent]:
    """
    Finds and returns a list of PatrolEvent objects for all patrols allowed according to given parameters, clan biome, and current season.
    """
    path = "patrols/"

    # OVERRIDE
    if get_config("patrol_generation.debug_override_patrol_stat_requirements"):
        return _generate_all_patrols(path)

    possible_patrols = []

    # TYPE PATROL
    biome = (
        game.clan.biome if not game.clan.override_biome else game.clan.override_biome
    )
    biome = biome.casefold()
    season = game.clan.current_season.casefold()

    # get specific type
    if patrol_type == "herb_gathering":
        # only one that doesn't match its path sadly
        patrol_type = "med"

    possible_patrols.extend(_get_all_patrols_of_type(patrol_type, biome, path, season))

    # OTHER CLAN
    possible_patrols.extend(_load_file(f"{path}other_clan.json"))
    if other_clan_rep != "neutral":
        possible_patrols.extend(_load_file(f"{path}other_clan_{other_clan_rep}.json"))

    # OUTSIDER
    if outsider_rep:
        possible_patrols.extend(_load_file(f"{path}new_cat.json"))
        if outsider_rep != "neutral":
            possible_patrols.extend(_load_file(f"{path}new_cat_{outsider_rep}.json"))

    # DISASTERS
    if get_clan_setting("disasters"):
        possible_patrols.extend(_load_file(f"{path}disaster.json"))

    return possible_patrols


def _get_all_patrols_of_type(_type: str, biome: str, path: str, season: str):
    """
    Grabs all patrols for a certain type of patrol
    """
    patrols = []
    patrols.extend(_load_file(f"{path}general/{_type}.json"))
    patrols.extend(_load_file(f"{path}{biome}/{_type}/any.json"))
    patrols.extend(_load_file(f"{path}{biome}/{_type}/{season}.json"))
    return patrols


def _generate_all_patrols(path) -> list[PatrolEvent]:
    """
    Generates all patrols regardless of type/season/location
    """
    patrols = []
    # loops through all types, biomes, and seasons to compile all the available patrols
    for _type in ["med", "hunting", "border", "training"]:
        for biome in game.constants.BIOME_TYPES:
            for season in game.constants.SEASONS:
                patrols.extend(
                    _get_all_patrols_of_type(_type, biome.lower(), path, season.lower())
                )

    # OTHER CLAN
    patrols.extend(_load_file(f"{path}other_clan.json"))
    patrols.extend(_load_file(f"{path}other_clan_hostile.json"))
    patrols.extend(_load_file(f"{path}other_clan_ally.json"))

    # OUTSIDER
    patrols.extend(_load_file(f"{path}new_cat.json"))
    patrols.extend(_load_file(f"{path}new_cat_hostile.json"))
    patrols.extend(_load_file(f"{path}new_cat_welcoming.json"))

    # DISASTER
    patrols.extend(_load_file(f"{path}disaster.json"))

    return patrols


def _load_file(path: str) -> list[PatrolEvent]:
    """
    Loads and returns the patrol events from a json file at the given path
    """
    if path not in loaded_events.keys():
        loaded_events[path] = []
        try:
            for p in load_lang_resource(path):
                loaded_events[path].append(PatrolEvent(**p))
        except FileNotFoundError:
            raise Exception(f"Patrol file {path} not found!")

    return loaded_events[path].copy()


def will_allow_outsider_patrols(small_clan: bool) -> Optional[str]:
    """
    Checks reputation and clan size to determine if outsider patrols should be allowed and what kind of patrol they can be
    :return: The type of outsider patrol allowed if outsider patrols are allowed. If they aren't allowed, then this will return None.
    """
    reputation = game.clan.reputation
    regular_chance = int(getrandbits(2))
    hostile_chance = int(getrandbits(5))
    welcoming_chance = int(getrandbits(1))

    if 1 <= int(reputation) <= 30:
        if small_clan:
            chance = welcoming_chance
        else:
            chance = hostile_chance
        if chance == 1:
            return "hostile"
    elif 31 <= int(reputation) <= 70:
        if small_clan:
            chance = welcoming_chance
        else:
            chance = regular_chance
        if chance == 1:
            return "neutral"
    elif int(reputation) >= 71:
        chance = welcoming_chance
        if chance == 1:
            return "welcoming"

    return None
