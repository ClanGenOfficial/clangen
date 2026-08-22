from typing import List

from scripts.cat.cats import Cat
from scripts.cat.save_load import save_cats
from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.game_structure.game.settings import game_settings_save
from scripts.game_structure.game.switches import (
    switch_set_value,
    Switch,
    switch_get_value,
)
from scripts.game_structure import constants, game


class CardCommand(Command):
    name = "card"
    description = "Manage cruel season cards"
    usage = "[add|remove] <card_name: str>"
    aliases = ["c"]

    def callback(self, args: List[str]):
        if len(args) < 2:
            add_output_line_to_log("Missing one or more required arguments")
            return
        if switch_get_value(Switch.game_mode) != "cruel_season":
            add_output_line_to_log("Current clan's game mode isn't Cruel Season")
            return

        card_name: str = args[1]
        if not constants.CRUEL_CARDS_ALL.get(card_name):
            add_output_line_to_log(
                f"Invalid card name, possible options: {constants.CRUEL_CARDS_ALL.keys()}"
            )
            return
        if constants.CRUEL_CARDS_ORIGIN.get(card_name):
            add_output_line_to_log(
                "Whilst a valid card name, adding an Origin card after clan creation does nothing"
            )
            return

        if args[0] == "add":
            if card_name in game.clan.cruel_cards:
                add_output_line_to_log(
                    f"Current clan already has {card_name} as a card"
                )
                return
            game.clan.cruel_cards.append(card_name)
        elif args[1] == "remove":
            if card_name not in game.clan.cruel_cards:
                add_output_line_to_log(
                    f"Current clan doesn't have {card_name} as a card"
                )
                return
            game.clan.cruel_cards.remove(card_name)
        else:
            add_output_line_to_log("Invalid card operation")
            return


class CruelCommand(Command):
    name = "cruel"
    description = "Manage cruel season specific settings for the clan"
    aliases = ["cruel", "cr"]

    sub_commands = [CardCommand()]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
