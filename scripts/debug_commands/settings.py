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


class SettingsCommand(Command):
    name = "settings"
    description = "View or modify the game settings"
    usage = "[game|switch|debug] [get|set|toggle] <setting: str> <value: int|bool>?"
    aliases = ["setting", "s"]

    def _list_valid_settings(self, scope: str):
        add_output_line_to_log("Available settings:")

        items = None
        if scope == "game":
            items = game_settings_generator
        elif scope == "switch":
            items = switch_generator
        elif scope == "debug":
            items = game.debug_settings.items

        if items is None:
            return

        for setting, val in items():
            add_output_line_to_log(f"  {setting} - {val}")

    def callback(self, args: List[str]):
        if len(args) < 2:
            add_output_line_to_log("Missing one or more required arguments")
            return

        setting_type: str = args[0]
        setting_op: str = args[1]

        if len(args) < 3:
            self._list_valid_settings(setting_type)
            return

        setting_name: str = args[2]

        if setting_type not in ["game", "switch", "debug"]:
            add_output_line_to_log(
                "Argument two isn't a valid setting type, expected: 'game', 'switch', or 'debug'"
            )
            return
        if setting_op not in ["get", "set", "toggle"]:
            add_output_line_to_log(
                "Argument one isn't a valid setting operation, expected: 'get', 'set', or 'toggle'"
            )
            return

        setting_value = None
        if setting_op in ["set", "toggle"]:
            setting_value = args[3]
            if setting_value in ["True", "true"]:
                setting_value = True
            elif setting_value in ["False", "false"]:
                setting_value = False
            elif setting_value.isnumeric():
                setting_value = int(setting_value)

        try:
            if setting_type == "game":
                get_function = game_setting_get
                set_function = game_setting_set
            elif setting_type == "switch":
                setting_name = Switch[setting_name]
                get_function = switch_get_value
                set_function = switch_set_value
            elif setting_type == "debug":
                get_function = game.debug_settings.__getitem__
                set_function = game.debug_settings.__setitem__
            else:
                add_output_line_to_log(f"Unknown setting type '{setting_type}'")
                return

            previous_value = get_function(setting_name)
            if isinstance(previous_value, (int, str, bool)):
                if type(previous_value) != type(setting_value):
                    add_output_line_to_log(
                        f"Invalid value type for setting '{setting_name}'"
                    )
                    add_output_line_to_log(
                        f"   Expected: {type(previous_value)}, got: {type(setting_value)}"
                    )
                    return

                if setting_op == "set":
                    set_function(setting_name, setting_value)
                elif setting_op == "toggle":
                    set_function(setting_name, not previous_value)
            else:
                add_output_line_to_log(
                    f"Can't modify setting '{setting_name}' because it not an int, string, or boolean"
                )

            add_output_line_to_log(f"{setting_name} is {get_function(setting_name)}")
        except KeyError:
            add_output_line_to_log(f"Unknown setting '{setting_name}', expected:")
            self._list_valid_settings(setting_type)


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
                    "Enabled developer tools for the current session"
                )
                add_output_line_to_log(
                    "To enable dev tools for all sessions, enable it in game_config.toml"
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
