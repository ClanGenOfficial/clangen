import os

import ujson
import i18n

from scripts.game_structure.localization import load_lang_resource


class Herb:
    def __init__(self, herb_name):
        self.name: str = herb_name
        self._herb_dict: dict = HERBS.get(self.name, {})

        self._display_dict = self._herb_dict.get("display", {})

        self.expiration: int = self._herb_dict.get("expiration", 1)

    @property
    def singular_display(self):
        return i18n.t(
            f"conditions.herbs.{self.name}",
            count=1,
        )

    @property
    def plural_display(self):
        return i18n.t(
            f"conditions.herbs.{self.name}",
            count=2,
        )

    def get_rarity(self, biome, season) -> int:
        """
        returns rarity of the herb within clan's current biome and season
        """
        rarity_dict = self._herb_dict.get("rarity", {})

        return rarity_dict.get(biome.casefold(), {}).get(season.casefold(), 0)


with open(
    os.path.normpath("resources/dicts/herb_info.json"), "r", encoding="utf-8"
) as read_file:
    HERBS = ujson.loads(read_file.read())
