from typing import List

from scripts.cat.cats import Cat
from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.game_structure.game_essentials import game


class ReloadClanCommand(Command):
    name = "reload"
    description = "Reloads current clan, defaults to reloading without saving."
    aliases = ["r"]
    usage = "<save>"

    def callback(self, args: List[str]):
        if len(args) == 0:
            game.all_screens[game.current_screen].change_screen(game.current_screen)
            game.switches["switch_clan"] = True
            add_output_line_to_log("Reload successful!")
        elif len(args) > 0 and args[0] == "save":
            game.save_cats()
            game.clan.save_clan()
            game.clan.save_pregnancy(game.clan)
            game.save_events()
            game.save_settings(game.current_screen)
            game.all_screens[game.current_screen].change_screen(game.current_screen)
            game.switches["switch_clan"] = True
            add_output_line_to_log("Reload successful!")
        else:
            add_output_line_to_log(
                "Unable to reload clan, arguments might not be correct."
            )


class ClanCommand(Command):
    name = "clan"
    description = "Manage current loaded clan"
    aliases = ["clan", "cl"]

    sub_commands = [ReloadClanCommand()]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
