import os.path
from typing import List, Dict, Union, Optional

import i18n
import i18n.translations
import ujson

from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure import game

lang_config: Optional[Dict] = None
_lang_config_directory = os.path.join("resources", "lang", "{locale}", "config.json")
_directory_changed: bool = False

default_pronouns: Dict[str, Dict[str, Dict[str, Union[str, int]]]] = {}


def get_new_pronouns(genderalign: str) -> List[Dict[str, Union[str, int]]]:
    """
    Handles getting the right pronoun set for the language.
    :param genderalign: The cat's gender alignment
    :return: The default list of pronouns for the cat's genderalign in the selected lang
    """
    config = get_lang_config()["pronouns"]
    if game_setting_get("they them default"):
        pronouns = config["sets"].get("default")
    else:
        pronouns = config["sets"].get(genderalign, config["sets"].get("default"))
    if pronouns is None:
        raise Exception(
            "Default pronouns not provided in lang file! Check config.json to confirm correct labels"
        )
    locale = i18n.config.get("locale")
    try:
        return [default_pronouns[locale][pronouns]]
    except KeyError:
        temp = load_lang_resource("pronouns.{lang}.json")
        try:
            default_pronouns[locale] = temp[locale]
        except KeyError:
            default_pronouns[locale] = temp[i18n.config.get("fallback")]
    return [default_pronouns[locale][pronouns]]


def determine_plural_pronouns(cat_list: List[Dict[str, Union[str, int]]]):
    """
    Returns the correct plural pronoun for the provided list
    :param cat_list: The pronouns for every cat in the plural
    :return: the correct plural pronoun
    """

    genders = [str(pronoun["gender"]) for pronoun in cat_list]

    config = get_lang_config()["pronouns"]
    for gender_code, group in config["plural_rules"]["order"].items():
        if gender_code in genders:
            return get_new_pronouns(group)[0]
    return get_new_pronouns("plural default")[0]


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


def set_lang_config_directory(directory: str):
    """
    Pretty much only useful for testing, so we can arbitrarily target a directory.
    :param directory: The directory that houses the config file
    :return: Nothing
    """
    global _lang_config_directory, _directory_changed
    _lang_config_directory = directory
    _directory_changed = True


def get_default_pronouns(lang=None):
    if lang is None:
        lang = i18n.config.get("locale")
    try:
        return default_pronouns[lang]
    except KeyError:
        temp: Dict[str, Dict[Dict[str, Union[str, int]]]] = load_lang_resource(
            "pronouns.{lang}.json"
        )
        default_pronouns[lang] = {
            key: pronoun_dict for key, pronoun_dict in temp[lang].items()
        }
    return default_pronouns[lang]


def get_custom_pronouns(lang=None):
    if lang is None:
        lang = i18n.config.get("locale")
    try:
        return game.clan.custom_pronouns[lang]
    except KeyError:
        game.clan.custom_pronouns[lang] = []
    return game.clan.custom_pronouns[lang]


def add_custom_pronouns(pronouns, lang=None):
    if lang is None:
        lang = i18n.config.get("locale")
    try:
        game.clan.custom_pronouns[lang].append(pronouns)
    except KeyError:
        game.clan.custom_pronouns[lang] = []
        game.clan.custom_pronouns[lang].append(pronouns)
