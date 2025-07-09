from enum import auto
from typing import Tuple, Any, Union, Dict, Generator

from strenum import StrEnum


# TO ADD A NEW SWITCH:
# 1. Add the name to the Enum class (so it can be autocompleted in calls)
# 2. Make sure its value is auto()
# 3. Add the name and actual default value to __switches dict below


class Switch(StrEnum):
    cat = auto()
    clan_name = auto()
    cur_screen = auto()
    saved_clan = auto()
    clan_list = auto()
    error_message = auto()
    traceback = auto()
    biome = auto()
    camp_bg = auto()
    game_mode = auto()
    favorite_sub_tab = auto()
    root_cat = auto()
    skip_conditions = auto()
    show_history_moons = auto()
    fps = auto()
    war_rel_change_type = auto()
    disallowed_symbol_tags = auto()
    saved_scroll_positions = auto()
    moon_and_seasons_open = auto()
    sort_type = auto()
    no_able_left = auto()
    new_leader = auto()
    switch_clan = auto()


_switches: Dict[str, Union[str, int, bool, list, dict, None]] = {
    "cat": "",
    "clan_name": "",
    "cur_screen": "start screen",
    "saved_clan": False,
    "clan_list": [],
    "error_message": "",
    "traceback": None,
    "biome": "",
    "camp_bg": "",
    "game_mode": "",
    "favorite_sub_tab": None,
    "root_cat": None,
    "skip_conditions": [],
    "show_history_moons": False,
    "fps": 30,
    "war_rel_change_type": "neutral",
    "disallowed_symbol_tags": [],
    "saved_scroll_positions": {},
    "moon_and_seasons_open": False,
    "sort_type": "rank",
    "no_able_left": False,
    "new_leader": None,
    "switch_clans": False,
}
"""If you are somehow accessing this from outside game_switches.py, something has gone terribly wrong."""


def switch_get_value(name: Switch):
    """
    Get a game switch
    :param name: The name of the switch.
    :return: The switch value
    """
    return _switches[name]


def switch_set_value(name: Switch, value):
    """
    Set a game switch
    :param name: The name of the switch
    :param value: The new value
    :return:
    """
    _switches[name] = value


def switch_set_dict_value(name: Switch, key: str, value):
    """
    Change the value of a nested dictionary
    :param name: The switch to change
    :param key: The dictionary key
    :param value: New dictionary value
    :return: None
    """
    if not isinstance(_switches[name], dict):
        raise TypeError(f"Switch {name} is not a dict")
    _switches[name][key] = value


def switch_append_list_value(name: Switch, value):
    """Used to append a value to a switch of type list
    :param name: The name of the switch
    :param value: Value to append to list
    :raises: TypeError if name argument does not correspond to a list"""
    if not isinstance(_switches[name], list):
        raise TypeError(f"Switch {name} is not a list")
    _switches[name].append(value)


def switch_remove_list_value(name: Switch, value):
    """Used to remove a value from a switch of type list"""
    if not isinstance(_switches[name], list):
        raise TypeError(f"Switch {name} is not a list")
    _switches[name].remove(value)


def switch_generator() -> Generator[Tuple[str, Any], None, None]:
    """
    Iterate through the switch keys and values. Made for debug, try to avoid using
    :return:
    """
    for key, value in _switches.items():
        yield key, value
