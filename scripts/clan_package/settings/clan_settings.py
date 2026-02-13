import os
from pathlib import Path

import ujson

from scripts.game_structure.game.save_load import safe_save
from scripts.game_structure.game.switches import Switch, switch_get_value
from scripts.housekeeping.datadir import get_save_dir
from ...game_structure.constants import DISPLAY_SETTINGS


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

        # creating a copy that we can iterate through while modifying the original dict
        _load_copy = _load_settings.copy()
        for key, value in _load_copy.items():
            # modifying outdated keys to utilize updated keys
            if key in _old_save_conversion:
                _load_settings[_old_save_conversion[key]] = value
                _load_settings.pop(key)

        # loading settings from converted dict
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
    if name in _clan_settings["other"].keys():
        raise ValueError(f"Use switch_clan_setting() to change setting '{name}'.")
    clan_settings[name] = value


def switch_clan_setting(setting_name):
    """Call this function to change a setting given in the parameter by one to the right on it's list"""

    # Give the index that the list is currently at
    list_index = setting_lists[setting_name].index(clan_settings[setting_name])
    list_index = (list_index + 1) % len(setting_lists[setting_name])

    clan_settings[setting_name] = setting_lists[setting_name][list_index]


def reset_loaded_clan_settings():
    global clan_settings

    clan_settings = {}

    for _setting in all_settings:  # Add all the settings to the settings dictionary
        for setting_name, value in _setting.items():
            clan_settings[setting_name] = value

    for setting, values in _clan_settings["other"].items():
        clan_settings[setting] = values[0]
        setting_lists[setting] = values


# Init Settings
clan_settings = {}
_clan_settings = DISPLAY_SETTINGS["clan"]
with open(
    "resources/clansettings_conversion.json", "r", encoding="utf-8"
) as conversion_file:
    _old_save_conversion = ujson.loads(conversion_file.read())

all_settings = [
    _clan_settings["general"],
    _clan_settings["role"],
    _clan_settings["relation"],
    _clan_settings["freshkill_tactics"],
    _clan_settings["clan_focus"],
]

setting_lists = {
    key: ([val, not val] if isinstance(val, bool) else [val[2], not val[2]])
    for category in all_settings
    for key, val in category.items()
}
reset_loaded_clan_settings()
