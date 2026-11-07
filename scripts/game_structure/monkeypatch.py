import i18n
from i18n import translator

from scripts.cat.cats import Cat
from scripts.game_structure import game
from scripts.events_module.text_adjust import event_text_adjust

# please for the love of GOD don't do this. ever.

groups = ["m_c", "r_c", "p_l", "s_c", "mur_c"]
other = [
    "dep_name",
    "lead_name",
    "med_name",
    "patrol_cats",
    "patrol_apprentices",
    "new_cats",
    "multi_cats",
    "clan",
    "other_clan",
    "chosen_herb",
]


# PYGAME_GUI REPLACEMENT
def translate(text: str, **kwargs):
    if text == "":
        return ""
    output = i18n.t(text, **kwargs)
    if game.event_editing:
        return output
    dict = {}
    for cat in groups:
        if cat in kwargs and cat in output:
            dict[cat] = kwargs[cat]
    for role in other:
        if role in kwargs:
            dict[role] = kwargs[role]
    if dict is not None:
        return event_text_adjust(
            Cat,
            output,
            main_cat=dict.get("m_c"),
            random_cat=dict.get("r_c"),
            victim_cat=dict.get("mur_c"),
            new_cats=dict.get("new_cats"),
            multi_cats=dict.get("multi_cats"),
            clan=dict.get("clan", game.clan),
            other_clan=dict.get("other_clan"),
            chosen_herb=dict.get("chosen_herb"),
        )
    return output


def i18n_translate(key, **kwargs):
    locale = kwargs.pop("locale", i18n.config.get("locale"))
    translation = i18n.translations.get(key, locale=locale)
    if "count" in kwargs:
        translation = pluralize(key, translation, kwargs["count"], locale)
    return translator.TranslationFormatter(translation).format(**kwargs)


def number_endswith(count, modulo, start, end):
    """
    Returns true if the number ends with the given modulo. INCLUSIVE OF START AND END
    :param start: number to start checking at
    :param end: number to end checking at
    :param modulo: should be a multiple of 10 (1, 10, 100 etc.)
    :param count: Number to check
    :return: True if it meets the criteria, False if not
    """
    unit = count % modulo
    if start <= unit <= end:
        return True


def pluralize(key, translation, count, locale):
    match locale:
        case "ru":  # RUSSIAN
            return pluralize_russian(key, translation, count)
        case "pu":  # POLISH
            return pluralize_polish(key, translation, count)
        case _:
            return i18n.translator.pluralize(key, translation, count)


def pluralize_russian(key, translation, count):
    if not isinstance(count, int):
        if "other" in translation:
            return translation["other"]
        else:
            return translation["many"]
    if "one" in translation and number_endswith(count, 10, 1, 1):
        return translation["one"]
    elif "few" in translation and (
        number_endswith(count, 10, 2, 4) and not number_endswith(count, 100, 12, 14)
    ):
        return translation["few"]
    elif "many" in translation and (
        number_endswith(count, 10, 0, 0)
        or number_endswith(count, 10, 5, 9)
        or number_endswith(count, 100, 11, 14)
    ):
        return translation["many"]
    elif "other" in translation:
        return translation["other"]
    else:
        return translation["many"]


def pluralize_polish(key, translation, count):
    if not isinstance(count, int):
        if "other" in translation:
            return translation["other"]
        else:
            return translation["many"]
    if "one" in translation and number_endswith(count, 10, 1, 1):
        return translation["one"]
    elif "few" in translation and (
        number_endswith(count, 10, 2, 4) or number_endswith(count, 100, 12, 14)
    ):
        return translation["few"]
    elif "many" in translation and (
        number_endswith(count, 10, 0, 1)
        or number_endswith(count, 10, 5, 9)
        or number_endswith(count, 100, 12, 14)
    ):
        return translation["many"]
    elif "other" in translation:
        return translation["other"]
    else:
        return translation["many"]
