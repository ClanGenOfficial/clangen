import copy
import tomllib

from scripts.game_structure import constants, game


# config_path passed as a string using dot notation - ex "graduation.min_graduating_age"
def get_config(config_path):
    config_value = game.constants.CONFIG
    config_keys = tuple(config_path.split("."))

    # checking cards first
    for card in game.clan.cruel_cards:
        card_info = constants.CRUEL_CARDS_ALL[card]
        if config_path in card_info["modifiers"]:
            config_value = card_info["modifiers"][config_path]

    # then checking game_config
    if config_value == game.constants.CONFIG:
        for key in config_keys:
            config_value = config_value[key]

    return copy.deepcopy(
        config_value
    )  # deepcopy so that the actual CONFIG can't be modified
