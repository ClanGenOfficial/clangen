from typing import List

from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.game_structure.game.switches import (
    Switch,
    switch_set_value,
    switch_get_value,
)


class FpsCommand(Command):
    name = "fps"
    description = "Toggle fps counter"
    usage = "[value]"

    def callback(self, args: List[str]):
        if len(args) == 1:
            if args[0].lower() in ["none", "null", "false"] or (
                args[0].lstrip("-").isnumeric() and int(args[0]) <= 0
            ):
                # weird workaround to allow 0 and negative numbers to remove the FPS cap
                switch_set_value(Switch.fps, 0)
                add_output_line_to_log("FPS cap removed")
            elif args[0].isnumeric():
                switch_set_value(Switch.fps, int(args[0]))
                add_output_line_to_log(f"FPS cap set to {args[0]}")
            else:
                add_output_line_to_log(f"Invalid value, {args[0]}")
        elif len(args) == 0:
            add_output_line_to_log(f"FPS cap is set to {switch_get_value('fps')}")
