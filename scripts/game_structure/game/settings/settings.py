import traceback
from pathlib import Path
from typing import Any, Tuple, Generator

import ujson

from scripts.game_structure.game.save_load import safe_save
from scripts.housekeeping.datadir import get_save_dir

settings_changed: bool = False
settings = {"moon_and_seasons_open": False}
setting_lists = {}

settings_path = Path(get_save_dir()) / "settings.json"
settings_txt_path = Path(get_save_dir()) / "settings.txt"


def game_settings_save(currentscreen=None):
    """Save user settings for later use"""
    if settings_txt_path.exists():
        settings_txt_path.unlink()
    global settings_changed

    settings_changed = False
    try:
        safe_save(settings_path, settings)
    except RuntimeError:
        from scripts.game_structure.windows import SaveError

        SaveError(traceback.format_exc())
        if currentscreen is not None:
            currentscreen.change_screen("start screen")


def game_settings_load():
    """Load settings that user has saved from previous use"""

    try:
        with open(settings_path, "r", encoding="utf-8") as read_file:
            settings_data = ujson.loads(read_file.read())
    except FileNotFoundError:
        return

    for key, value in settings_data.items():
        if key in settings:
            settings[key] = value


def game_setting_toggle(setting_name):
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


def game_setting_get(name, *, default=None):
    return settings.get(name, default)


def game_setting_set(name, value):
    settings[name] = value


def game_settings_generator() -> Generator[Tuple[str, Any], None, None]:
    for key, value in settings.items():
        yield key, value


# Init Settings
with open(Path("resources") / "gamesettings.json", "r", encoding="utf-8") as read_file:
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

game_settings_load()
# End init settings
