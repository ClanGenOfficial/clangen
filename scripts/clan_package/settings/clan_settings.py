import os
from pathlib import Path

import ujson

from scripts.game_structure.game.save_load import safe_save
from scripts.game_structure.game.switches import Switch, switch_get_value
from scripts.housekeeping.datadir import get_save_dir


def load_clan_settings():
    reset_loaded_clan_settings()
    if os.path.exists(
        get_save_dir() + f"/{switch_get_value(Switch.clan_list)[0]}/clan_settings.json"
    ):
        with open(
            get_save_dir()
            + f"/{switch_get_value(Switch.clan_list)[0]}/clan_settings.json",
            "r",
            encoding="utf-8",
        ) as write_file:
            _load_settings = ujson.loads(write_file.read())

        for key, value in _load_settings.items():
            if key in clan_settings:
                clan_settings[key] = value

    # if settings files does not exist, default has been loaded by __init__


def save_clan_settings():
    safe_save(
        Path(get_save_dir())
        / switch_get_value(Switch.clan_name)
        / "clan_settings.json",
        clan_settings,
    )


def get_clan_setting(name: str, *, default=None):
    return clan_settings.get(name, default)


def set_clan_setting(name: str, value):
    clan_settings[name] = value


def switch_clan_setting(setting_name):
    """Call this function to change a setting given in the parameter by one to the right on it's list"""

    # Give the index that the list is currently at
    list_index = setting_lists[setting_name].index(clan_settings[setting_name])
    list_index = (list_index + 1) % len(setting_lists[setting_name])

    clan_settings[setting_name] = setting_lists[setting_name][list_index]


def reset_loaded_clan_settings():
    global clan_settings

    for setting in all_settings:  # Add all the settings to the settings dictionary
        for setting_name, inf in setting.items():
            clan_settings[setting_name] = inf[2]


# Init Settings
clan_settings = {}
setting_lists = {}
with open("resources/clansettings.json", "r", encoding="utf-8") as read_file:
    _settings = ujson.loads(read_file.read())

for setting, values in _settings["__other"].items():
    clan_settings[setting] = values[0]
    setting_lists[setting] = values

all_settings = [
    _settings["general"],
    _settings["role"],
    _settings["relation"],
    _settings["freshkill_tactics"],
    _settings["clan_focus"],
]

setting_lists = {
    key: [inf[2], not inf[2]]
    for category in all_settings
    for key, inf in category.items()
}
reset_loaded_clan_settings()
