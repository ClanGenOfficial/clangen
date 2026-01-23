import os.path
from typing import Dict, Optional

import i18n
import ujson

lang_config: Optional[Dict] = None
_lang_config_directory = os.path.join("resources", "lang", "{locale}", "config.json")
_directory_changed: bool = False

additional_lang_list: Optional[Dict] = None


def get_default_adj():
    """

    :return: string representing the default adjective
    """
    return get_lang_config()["pronouns"]["adj_default"]


def load_lang_resource(location: str, *, root_directory=None):
    """
    Get a resource from the resources/lang folder for the loaded language
    :param location: If the language code is required, substitute `{lang}`. Relative location
    from the resources/lang/[language]/ folder. Don't include a slash.
    :param root_directory: for testing only.
    :return: Whatever resource was there, from either the locale or fallback
    :exception FileNotFoundError: If requested resource doesn't exist in selected locale or fallback
    """
    location = os.path.normpath(location)
    locale, fallback = str(i18n.config.get("locale")), str(i18n.config.get("fallback"))
    if root_directory is None:
        root_directory = os.path.join("resources", "lang")
    resource_directory = os.path.join(root_directory, locale)
    fallback_directory = os.path.join(root_directory, fallback)
    location = location.lstrip("\\/")  # just in case someone is an egg and does add it
    try:
        with open(
            os.path.join(resource_directory, location.replace("{lang}", locale)),
            "r",
            encoding="utf-8",
        ) as string_file:
            return ujson.loads(string_file.read())
    except FileNotFoundError:
        with open(
            os.path.join(fallback_directory, location.replace("{lang}", fallback)),
            "r",
            encoding="utf-8",
        ) as string_file:
            return ujson.loads(string_file.read())


def get_lang_config() -> Dict:
    """
    :return: the config file for the currently-loaded language. Raises error if config doesn't exist.
    """
    global lang_config, _directory_changed
    locale = i18n.config.get("locale")
    if _directory_changed or lang_config is None or lang_config["lang"] != locale:
        with open(
            _lang_config_directory.replace("{locale}", locale), "r", encoding="utf-8"
        ) as lang_file:
            lang_config = ujson.loads(lang_file.read())
        _directory_changed = False
    return lang_config


def get_additional_lang_list() -> Dict:
    global additional_lang_list, _directory_changed
    if additional_lang_list is None:
        with open(
            os.path.join("resources", "lang", "additional_lang_list.json"),
            "r",
            encoding="utf-8",
        ) as lang_file:
            additional_lang_list = ujson.loads(lang_file.read())
    return additional_lang_list


def set_lang_config_directory(directory: str):
    """
    Pretty much only useful for testing, so we can arbitrarily target a directory.
    :param directory: The directory that houses the config file
    :return: Nothing
    """
    global _lang_config_directory, _directory_changed
    _lang_config_directory = directory
    _directory_changed = True
