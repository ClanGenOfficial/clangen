from typing import List

from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.game_structure.game.settings import (
    game_setting_set,
    game_setting_get,
    game_settings_generator,
)
from scripts.game_structure.game.switches import (
    switch_get_value,
    switch_set_value,
    Switch,
)
from scripts.game_structure.game.switches import switch_generator
from scripts.game_structure import game, constants
from scripts.screens import all_screens
from scripts.screens.enums import GameScreen
from scripts.ui.windows.dev_tool_windows.white_patch_tool import WhitePatchToolWindow
from scripts.ui.windows.tortie_patch_tool import TortiePatchToolWindow


class ToggleCommand(Command):
    name = "toggle"
    description = "Toggle game settings"
    usage = "[game|switch|debug] <setting: str>"
    aliases = ["t"]

    def callback(self, args: List[str]):
        if len(args) != 2 or args[0] not in ["game", "switch", "debug"]:
            add_output_line_to_log(f"Usage: {self.name} {self.usage}")
            return

        try:
            if args[0] == "game":
                game_setting_set(args[1], not game_setting_get(args[1]))
                output = game_setting_get(args[1])
            elif args[0] == "switch":
                switch_set_value(Switch[args[1]], not switch_get_value(Switch[args[1]]))
                output = switch_get_value(Switch[args[1]])
            elif args[0] == "debug":
                game.debug_settings[args[1]] = not game.debug_settings[args[1]]
                output = game.debug_settings[args[1]]
            else:
                add_output_line_to_log(f"Unknown setting type {args[0]}")
                return
            add_output_line_to_log(f"Set {args[1]} to {output}")
        except KeyError:
            add_output_line_to_log(f"Unknown setting {args[1]}")


class SetCommand(Command):
    name = "set"
    description = "Set game settings"
    usage = "[game|switch|debug] <setting: str> <value: int|bool>"
    aliases = ["s"]

    def callback(self, args: List[str]):
        if len(args) != 3 or args[0] not in ["game", "switch", "debug"]:
            add_output_line_to_log(f"Usage: {self.name} {self.usage}")
            return

        value = args[2]

        if value in ["true", "True", "1"]:
            value = True
        elif value in ["false", "False", "0"]:
            value = False
        elif value.isnumeric():
            value = int(value)

        if args[0] == "game":
            game_setting_set(args[1], value)
            output = game_setting_get(args[1])
        elif args[0] == "switch":
            switch_set_value(Switch[args[1]], not switch_get_value(Switch[args[1]]))
            output = switch_get_value(Switch[args[1]])
        elif args[0] == "debug":
            game.debug_settings[args[1]] = value
            output = game.debug_settings[args[1]]
        else:
            add_output_line_to_log(f"Unknown setting type {args[0]}")
            return
        add_output_line_to_log(f"Set {args[1]} to {output}")


class GetCommand(Command):
    name = "get"
    description = "Get game settings"
    usage = "[game|switch|debug] <setting: str>"
    aliases = ["g"]

    def callback(self, args: List[str]):
        if len(args) == 0 or args[0] not in ["game", "switch", "debug"]:
            add_output_line_to_log(f"Usage: {self.name} {self.usage}")
            return

        try:
            if args[0] == "game":
                if len(args) == 1:
                    add_output_line_to_log("Available settings:")
                    for setting, val in game_settings_generator():
                        add_output_line_to_log(f"  {setting} - {val}")
                    return
                output = game_setting_get(args[1])
            elif args[0] == "switch":
                if len(args) == 1:
                    add_output_line_to_log("Available settings:")
                    for (
                        setting,
                        val,
                    ) in switch_generator():
                        add_output_line_to_log(f"  {setting} - {val}")
                    return
                output = switch_get_value(args[1])
            elif args[0] == "debug":
                if len(args) == 1:
                    add_output_line_to_log("Available settings:")
                    for setting, val in game.debug_settings.items():
                        add_output_line_to_log(f"  {setting} - {val}")
                    return
                output = game.debug_settings[args[1]]
            else:
                add_output_line_to_log(f"Unknown setting type {args[0]}")
                return
            add_output_line_to_log(f"{args[1]} is {output}")
        except KeyError:
            add_output_line_to_log(f"Unknown setting {args[1]}")


class DevToolsCommand(Command):
    name = "devtools"
    description = "Access the developer tools."
    usage = "[enable] | ([open] [event_edit|tortie_patch|white_patch])"
    aliases = ["dev", "tools"]

    def callback(self, args: List[str]):
        if len(args) == 0 or args[0] not in ["enable", "list", "open"]:
            add_output_line_to_log(f"Usage: {self.name} {self.usage}")
            return

        try:
            if args[0] == "enable":
                constants.CONFIG["dev_tools"] = True
                add_output_line_to_log(
                    "Enabled developer tools, note that this only applies for the current session"
                )
                add_output_line_to_log(
                    "If you want to enable dev tools for all sessions, enable it in game_config.toml"
                )
                if switch_get_value(Switch.cur_screen) == GameScreen.START:
                    all_screens.get_screen(
                        switch_get_value(Switch.cur_screen)
                    ).change_screen(GameScreen.START)
                return
            elif args[0] == "open":
                tool_name = args[1]
                if tool_name == "event_edit":
                    all_screens.get_screen(
                        switch_get_value(Switch.cur_screen)
                    ).change_screen(GameScreen.EVENT_EDIT)
                elif tool_name == "tortie_patch":
                    TortiePatchToolWindow()
                elif tool_name == "white_patch":
                    WhitePatchToolWindow()
                else:
                    raise KeyError()
                add_output_line_to_log(f"Successfully opened {tool_name}")
                return
        except KeyError:
            add_output_line_to_log(f"Unknown tool {args[1]}")
