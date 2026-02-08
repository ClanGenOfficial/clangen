from random import choice
from typing import TYPE_CHECKING, Dict, Union, List

import i18n

from scripts.game_structure import game
from scripts.game_structure.game import game_setting_get
from scripts.game_structure.localization import get_lang_config, load_lang_resource

if TYPE_CHECKING:
    from scripts.cat.cats import Cat

default_pronouns: Dict[str, Dict[str, Dict[str, Union[str, int]]]] = {}


def get_pronouns(cat: "Cat"):
    """Get a cat's pronoun even if the cat has faded to prevent crashes (use gender-neutral pronouns when the cat has faded)"""
    if not cat.pronouns:
        # since get_new_pronouns returns a list with length 1
        return get_new_pronouns("default")[0]
    else:
        return choice(cat.pronouns)


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
