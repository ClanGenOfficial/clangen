from random import choice, randint

from scripts.cat.names import names
from scripts.clan.baseclan import BaseClan
from scripts.utility import clan_symbol_sprite


class OtherClan(BaseClan):
    """
    A non-player clan in the ClanGen universe.
    """

    interaction_dict = {
        "ally": ["offend", "praise"],
        "neutral": ["provoke", "befriend"],
        "hostile": ["antagonize", "appease", "declare"],
    }

    name = ""
    relations = 10
    temperament = "mellow"
    chosen_symbol = None

    def __init__(self, name="", relations=0, temperament="", chosen_symbol=""):
        clan_names = names.names_dict["normal_prefixes"]
        clan_names.extend(names.names_dict["clan_prefixes"])
        self.name = name or choice(clan_names)
        self.relations = relations or randint(8, 12)
        temperament_dict = [value for category in self.temperament_dict.values() for value in category]
        self.temperament = temperament or choice(temperament_dict)
        if self.temperament not in temperament_dict:
            self.temperament = choice(temperament_dict)

        self.chosen_symbol = (
            None  # have to establish None first so that clan_symbol_sprite works
        )
        self.chosen_symbol = (
            chosen_symbol
            if chosen_symbol
            else clan_symbol_sprite(self, return_string=True)
        )


