import tomllib

from scripts.game_structure.game.switches import switch_get_value, Switch

with open("resources/game_config.toml", "r", encoding="utf-8") as read_file:
    CONFIG = tomllib.loads(read_file.read())


# config_path passed as a string using dot notation - ex "graduation.min_graduating_age"
def get_config(clan, config_path):
    """
    returns a config value from game_config OR a modified value from active cards (cruel season). 

    config_path is passed as a string using dot notation - ex "graduation.min_graduating_age"
    
    """
    config_value = CONFIG
    config_keys = tuple(config_path.split("."))

    # checking cards first
    for card in clan.cruel_cards:
        if config_path in card["modifiers"]:
            config_value = card["modifiers"][config_path]

    # then checking game_config
    if config_value == CONFIG:
        for key in config_keys:
            config_value = config_value[key]

    return config_value
