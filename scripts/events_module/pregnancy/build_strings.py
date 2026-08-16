from typing import Optional, Dict, Union, List

import i18n

from scripts.game_structure.localization import load_lang_resource

PREGNANT_STRINGS: Optional[Dict[str, Union[List, Dict[str, List]]]] = {}
NEWBORN_REL_REACTIONS: Dict = {}
BREAKUP_STRINGS: Dict = {}
currently_loaded_lang: str = None


def rebuild_strings():
    global PREGNANT_STRINGS, NEWBORN_REL_REACTIONS, BREAKUP_STRINGS, currently_loaded_lang

    if currently_loaded_lang == i18n.config.get("locale"):
        return
    PREGNANT_STRINGS = load_lang_resource("conditions/pregnancy.json")

    NEWBORN_REL_REACTIONS = load_lang_resource(
        "events/relationship_events/newborn_relative_logs.json"
    )

    BREAKUP_STRINGS = load_lang_resource(
        "events/relationship_events/breakup_mates.json"
    )

    currently_loaded_lang = i18n.config.get("locale")
