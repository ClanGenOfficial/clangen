from typing import List
from ast import literal_eval

from scripts.debugCommands.command import Command
from scripts.debugCommands.utils import add_output_line_to_log
from typing import List

from scripts.game_structure.game_essentials import game


class ToggleCommand(Command):
    name = "toggle"
    description = "Toggle game settings"
    usage = "<game|switch|debug> <setting>"
    aliases = ["t"]

    def callback(self, args: List[str]):
        if len(args) != 2 or args[0] not in ["game", "switch", "debug"]:
            add_output_line_to_log(f"Usage: {self.name} {self.usage}")
            return

        if args[0] == "game":
            game.settings[args[1]] = not game.settings[args[1]]
            output = game.settings[args[1]]
        elif args[0] == "switch":
            game.switches[args[1]] = not game.switches[args[1]]
            output = game.switches[args[1]]
        elif args[0] == "debug":
            game.debug_settings[args[1]] = not game.debug_settings[args[1]]
            output = game.debug_settings[args[1]]
        else:
            add_output_line_to_log(f"Unknown setting type {args[0]}")
            return
        add_output_line_to_log(f"Set {args[1]} to {output}")


class SetCommand(Command):
    name = "set"
    description = "Set game settings"
    usage = "<game|switch|debug> <setting> <value>"
    aliases = ["s"]

    def callback(self, args: List[str]):
        if len(args) != 3 or args[0] not in ["game", "switch", "debug"]:
            add_output_line_to_log(f"Usage: {self.name} {self.usage}")
            return

        if args[0] == "game":
            game.settings[args[1]] = literal_eval(args[2])
            output = game.settings[args[1]]
        elif args[0] == "switch":
            game.switches[args[1]] = literal_eval(args[2])
            output = game.switches[args[1]]
        elif args[0] == "debug":
            game.debug_settings[args[1]] = literal_eval(args[2])
            output = game.debug_settings[args[1]]
        else:
            add_output_line_to_log(f"Unknown setting type {args[0]}")
            return
        add_output_line_to_log(f"Set {args[1]} to {output}")


class GetCommand(Command):
    name = "get"
    description = "Get game settings"
    usage = "<game|switch|debug> <setting>"
    aliases = ["g"]

    def callback(self, args: List[str]):
        if len(args) == 0 or args[0] not in ["game", "switch", "debug"]:
            add_output_line_to_log(f"Usage: {self.name} {self.usage}")
            return

        if args[0] == "game":
            if len(args) == 1:
                add_output_line_to_log("Avaliable settings:")
                for setting, val in game.settings.items():
                    add_output_line_to_log(
                        f"  {setting} - {val}")
                return
            output = game.settings[args[1]]
        elif args[0] == "switch":
            if len(args) == 1:
                add_output_line_to_log("Avaliable settings:")
                for setting, val in game.switches.items():
                    add_output_line_to_log(
                        f"  {setting} - {val}")
                return
            output = game.switches[args[1]]
        elif args[0] == "debug":
            if len(args) == 1:
                add_output_line_to_log("Avaliable settings:")
                for setting, val in game.debug_settings.items():
                    add_output_line_to_log(
                        f"  {setting} - {val}")
                return
            output = game.debug_settings[args[1]]
        else:
            add_output_line_to_log(f"Unknown setting type {args[0]}")
            return
        add_output_line_to_log(f"{args[1]} is {output}")
