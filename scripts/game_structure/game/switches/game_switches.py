from enum import auto
from typing import Tuple, Any, Union, Dict

from strenum import StrEnum


# TO ADD A NEW SWITCH:
# 1. Add the name to the Enum class (so it can be autocompleted in calls)
# 2. Make sure its value is auto()
# 3. Add the name and actual default value to __switches dict below


class Switches(StrEnum):
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


__switches: Dict[str, Union[str, int, bool, list, dict, None]] = {
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
}
"""If you are somehow accessing this from outside game_switches.py, something has gone terribly wrong."""


def get_switch(name: Switches):
    """
    Get a game switch
    :param name: The name of the switch
    :return: The switch value
    """
    return __switches[name]


def set_switch(name: Switches, value):
    """
    Set a game switch
    :param name: The name of the switch
    :param value: The new value
    :return:
    """
    __switches[name] = value


def set_switch_dict_value(name: Switches, key: str, value):
    """
    Change the value of a nested dictionary
    :param name: The switch to change
    :param key: The dictionary key
    :param value: New dictionary value
    :return: None
    """
    if not isinstance(__switches[name], dict):
        raise TypeError(f"Switch {name} is not a dict")
    __switches[name][key] = value


def switch_list_append(name: Switches, value):
    """Used to append a value to a switch of type list
    :param name: The name of the switch
    :param value: Value to append to list
    :raises: TypeError if name argument does not correspond to a list"""
    if not isinstance(__switches[name], list):
        raise TypeError(f"Switch {name} is not a list")
    __switches[name].append(value)


def switch_list_remove(name: Switches, value):
    """Used to remove a value from a switch of type list"""
    if not isinstance(__switches[name], list):
        raise TypeError(f"Switch {name} is not a list")
    __switches[name].remove(value)


def switch_generator() -> Tuple[str, Any]:
    """
    Iterate through the switch keys and values. Made for debug, try to avoid using
    :return:
    """
    for key, value in __switches.items():
        yield key, value
