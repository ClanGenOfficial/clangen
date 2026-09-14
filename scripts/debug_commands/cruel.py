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


def get_cards_list(card_scope: dict | None, limit_possible: bool = False):
    if card_scope is None:
        card_scope = constants.CRUEL_CARDS_ALL

    i = 0
    current_line = []
    for card_key in card_scope.keys():
        if limit_possible and (
            check_card_conflict(card_key) or card_key in game.clan.cruel_cards
        ):
            continue
        current_line.append(card_key)
        i += 1

        if i % 4 == 0 and i != 0:
            add_output_line_to_log(", ".join(current_line))
            current_line.clear()


def check_card_conflict(card_name: str) -> bool:
    for card_list in constants.CRUEL_CARDS_CONFLICTS.values():
        if (
            card_name in card_list
            and len(set(game.clan.cruel_cards).intersection(set(card_list))) > 0
        ):
            return True
    return False


class ListCardsCommand(Command):
    name = "list"
    description = "List all valid or possible cruel cards"
    usage = "[all|behavior|danger|environment|origin] [possible]?"
    aliases = ["l"]

    def callback(self, args: List[str]):
        if len(args) <= 0:
            card_scope = None
        elif args[0] == "behavior":
            card_scope = constants.CRUEL_CARDS_BEHAVIOR
        elif args[0] == "danger":
            card_scope = constants.CRUEL_CARDS_DANGER
        elif args[0] == "environment":
            card_scope = constants.CRUEL_CARDS_ENVIRONMENT
        elif args[0] == "origin":
            card_scope = constants.CRUEL_CARDS_ORIGIN
        else:
            card_scope = constants.CRUEL_CARDS_ALL

        limit_possible = len(args) >= 2
        get_cards_list(card_scope, limit_possible)


class CardCommand(Command):
    name = "card"
    description = "Manage cruel season cards"
    usage = "[add|remove] <card_name: str>"
    aliases = ["c", "cards"]

    sub_commands = [ListCardsCommand()]

    def callback(self, args: List[str]):
        if switch_get_value(Switch.game_mode) != "cruel_season":
            add_output_line_to_log("Current clan's game mode isn't cruel season")
            return

        if len(args) < 2:
            add_output_line_to_log("Missing one or more required arguments")
            return

        # Add/Remove Card
        card_name: str = args[1]
        if not constants.CRUEL_CARDS_ALL.get(card_name):
            add_output_line_to_log(
                f"Invalid card name, possible (non-conflicting) options:"
            )
            get_cards_list(None, True)
            return
        if constants.CRUEL_CARDS_ORIGIN.get(card_name):
            add_output_line_to_log(
                "Whilst a valid card name, adding/removing an Origin card after clan creation does nothing"
            )
            return

        if args[0] == "add":
            if card_name in game.clan.cruel_cards:
                add_output_line_to_log(
                    f'Current clan already has "{card_name}" as a card'
                )
                return
            if check_card_conflict(card_name):
                add_output_line_to_log(
                    f"WARNING: Added card ({card_name}) conflicts with another existing card"
                )
            game.clan.cruel_cards.append(card_name)
        elif args[0] == "remove":
            if card_name not in game.clan.cruel_cards:
                add_output_line_to_log(
                    f'Current clan doesn\'t have "{card_name}" as a card'
                )
                return
            game.clan.cruel_cards.remove(card_name)
        else:
            add_output_line_to_log("Invalid card operation")
            return


class CruelCommand(Command):
    name = "cruel"
    description = "Manage cruel season specific settings for the clan"
    aliases = ["cr"]

    sub_commands = [CardCommand()]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
