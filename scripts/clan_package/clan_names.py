from typing import List

from scripts.cat.names import Name
from scripts.game_structure import constants
from scripts.game_structure.localization import get_lang_config


def get_possible_clan_names() -> List[str]:
    """
    Returns a list of all possible names for a Clan, handling logic on what names may appear
    :return: A list of possible Clan prefixes
    """
    clan_names = Name.names_dict["clan_prefixes"]

    if constants.CONFIG["cat_name_controls"][
        "always_use_english"
    ] or get_lang_config().get("names", {}).get("clans_can_have_cat_prefixes", True):
        clan_names += Name.names_dict["normal_prefixes"]
    return clan_names
