import os
import traceback
from typing import Any, Tuple

import ujson

from scripts.game_structure.game.save_load import safe_save
from scripts.housekeeping.datadir import get_save_dir

settings_changed: bool = False
settings = {"moon_and_seasons_open": False}
setting_lists = {}


# Init Settings
with open("resources/gamesettings.json", "r", encoding="utf-8") as read_file:
    _settings = ujson.loads(read_file.read())

for setting, values in _settings["__other"].items():
    settings[setting] = values[0]
    setting_lists[setting] = values

_ = [_settings["general"]]

for cat in _:  # Add all the settings to the settings dictionary
    for setting_name, inf in cat.items():
        settings[setting_name] = inf[2]
        setting_lists[setting_name] = [inf[2], not inf[2]]
del _settings, setting_name, _
# End init settings


def save_settings(currentscreen=None):
    """Save user settings for later use"""
    if os.path.exists(get_save_dir() + "/settings.txt"):
        os.remove(get_save_dir() + "/settings.txt")
    global settings_changed

    settings_changed = False
    try:
        safe_save(get_save_dir() + "/settings.json", settings)
    except RuntimeError:
        from scripts.game_structure.windows import SaveError

        SaveError(traceback.format_exc())
        if currentscreen is not None:
            currentscreen.change_screen("start screen")


def load_settings():
    """Load settings that user has saved from previous use"""

    try:
        with open(
            get_save_dir() + "/settings.json", "r", encoding="utf-8"
        ) as read_file:
            settings_data = ujson.loads(read_file.read())
    except FileNotFoundError:
        return

    for key, value in settings_data.items():
        if key in settings:
            settings[key] = value


def switch_setting(setting_name):
    """Call this function to change a setting given in the parameter by one to the right on it's list"""
    global settings_changed, settings
    settings_changed = True

    # Give the index that the list is currently at
    list_index = setting_lists[setting_name].index(settings[setting_name])

    if (
        list_index == len(setting_lists[setting_name]) - 1
    ):  # The option is at the list's end, go back to 0
        settings[setting_name] = setting_lists[setting_name][0]
    else:
        # Else move on to the next item on the list
        settings[setting_name] = setting_lists[setting_name][list_index + 1]


if not os.path.exists(get_save_dir() + "/settings.txt"):
    os.makedirs(get_save_dir(), exist_ok=True)
    with open(get_save_dir() + "/settings.txt", "w", encoding="utf-8") as write_file:
        write_file.write("")
load_settings()


def get_setting(name):
    return settings[name]


def set_setting(name, value):
    settings[name] = value


def settings_generator() -> Tuple[str, Any]:
    for key, value in settings:
        yield key, value
