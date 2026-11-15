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
    temp_dict = {}
    for cat in groups:
        if cat in kwargs and cat in output:
            temp_dict[cat] = kwargs[cat]
    for role in other:
        if role in kwargs:
            temp_dict[role] = kwargs[role]
    if temp_dict is not None:
        return event_text_adjust(
            Cat,
            output,
            main_cat=temp_dict.get("m_c"),
            random_cat=temp_dict.get("r_c"),
            victim_cat=temp_dict.get("mur_c"),
            new_cats=temp_dict.get("new_cats"),
            multi_cats=temp_dict.get("multi_cats"),
            clan=temp_dict.get("clan", game.clan),
            other_clan=temp_dict.get("other_clan"),
            chosen_herb=temp_dict.get("chosen_herb"),
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
    return_value = key
    try:
        if type(translation) != dict:
            return_value = translation
            raise KeyError("use of count without dict for key {0}".format(key))
        match locale:
            case "ru":  # RUSSIAN
                return pluralize_russian(key, translation, count)
            case "pu":  # POLISH
                return pluralize_polish(key, translation, count)
            case _:
                return i18n.translator.pluralize(key, translation, count)
    except KeyError as e:
        if i18n.config.get("error_on_missing_plural"):
            raise e
        else:
            return return_value


def pluralize_russian(key, translation, count):
    if not isinstance(count, int):
        if "other" in translation:
            return translation["other"]
        else:
            return translation["many"]
    if "one" in translation and count != 11 and number_endswith(count, 10, 1, 1):
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
    if count == 1 and "one" in translation:
        return translation["one"]
    elif "few" in translation and (
        number_endswith(count, 10, 2, 4) and not number_endswith(count, 100, 12, 14)
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
