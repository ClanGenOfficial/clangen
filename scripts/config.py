import tomllib

from scripts.game_structure import constants, game

with open("resources/game_config.toml", "r", encoding="utf-8") as read_file:
    CONFIG = tomllib.loads(read_file.read())


# config_path passed as a string using dot notation - ex "graduation.min_graduating_age"
def get_config(config_path):
    config_value = CONFIG
    config_keys = tuple(config_path.split("."))

    # checking cards first
    for card in game.clan.cruel_cards:
        card_info = constants.CRUEL_CARDS_ALL[card]
        if config_path in card_info["modifiers"]:
            config_value = card_info["modifiers"][config_path]

    # then checking game_config
    if config_value == CONFIG:
        for key in config_keys:
            config_value = config_value[key]

    return config_value
