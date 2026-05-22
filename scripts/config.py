import tomllib

from scripts.game_structure.game.switches import switch_get_value, Switch

with open("resources/game_config.toml", "r", encoding="utf-8") as read_file:
    CONFIG = tomllib.loads(read_file.read())


# config_path passed as a string using dot notation - ex "graduation.min_graduating_age"
def get_config(clan, config_path):
    war_effected = {
        ("death_related", "leader_death_chance"): (
            "death_related",
            "war_death_modifier_leader",
        ),
        ("death_related", "classic_death_chance"): (
            "death_related",
            "war_death_modifier",
        ),
        ("death_related", "expanded_death_chance"): (
            "death_related",
            "war_death_modifier",
        ),
        ("death_related", "cruel season_death_chance"): (
            "death_related",
            "war_death_modifier",
        ),
        ("condition_related", "classic_injury_chance"): (
            "condition_related",
            "war_injury_modifier",
        ),
        ("condition_related", "expanded_injury_chance"): (
            "condition_related",
            "war_injury_modifier",
        ),
        ("condition_related", "cruel season_injury_chance"): (
            "condition_related",
            "war_injury_modifier",
        ),
    }
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

    # Apply war if needed
    if clan and clan.war.get("at_war", False) and config_keys in war_effected:
        rel_change_type = switch_get_value(Switch.war_rel_change_type)
        # if the war was positively affected this moon, we don't apply war modifier
        # this way we only see increased death/injury when the war is going badly or is neutral
        if rel_change_type != "rel_up":
            # Grabs the modifier
            mod = CONFIG
            for key in war_effected[config_keys]:
                mod = mod[key]

            config_value -= mod
    return config_value
