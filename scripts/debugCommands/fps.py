from typing import List

from scripts.debugCommands.command import Command
from scripts.debugCommands.utils import add_output_line_to_log
from typing import List

from scripts.game_structure.game_essentials import game


class FpsCommand(Command):
    name = "fps"
    description = "Toggle fps counter"
    usage = "[value]"

    def callback(self, args: List[str]):
        if len(args) == 1:
            if args[0].lower() in ['none', 'null', '0'] or args[0].is_integer() and int(args[0]) <= 0:
                game.switches['fps'] = 0
                add_output_line_to_log("FPS cap removed")
            elif args[0].is_integer():
                game.switches['fps'] = int(args[0])
                add_output_line_to_log(f"FPS cap set to {args[0]}")
            else:
                add_output_line_to_log(f"Invalid value, {args[0]}")
        elif len(args) == 0:
            add_output_line_to_log(f"FPS cap is set to {game.switches['fps']}")
