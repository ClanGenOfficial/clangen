import copy

from scripts.game_structure import constants, game


def get_config(
    config_path, creating_clan: bool = False, card_list_override: list[str] = None
):
    """
    Returns a given game config value. If the clan has cruel cards that can replace those values, then it will return the card modifier instead.
    :param config_path: Path to config value in dot notation - ex "graduation.min_graduating_age"
    :param creating_clan: Set to True if currently loaded game.clan.cruel_cards should be ignored.
    :param card_list_override: If you want to specify a list of cruel card IDs to search INSTEAD of using the saved clan cards, then list them here. Best used during clan creation.
    """
    config_value = constants.CONFIG
    config_keys = tuple(config_path.split("."))

    # checking cards first
    card_list = card_list_override if card_list_override else []
    if game.clan and not card_list and not creating_clan:
        card_list = game.clan.cruel_cards

    for card in card_list:
        card_info = constants.CRUEL_CARDS_ALL[card]
        if config_path in card_info["modifiers"]:
            config_value = card_info["modifiers"][config_path]

    # then checking game_config
    if config_value == constants.CONFIG:
        for key in config_keys:
            config_value = config_value[key]

    return copy.deepcopy(config_value)
