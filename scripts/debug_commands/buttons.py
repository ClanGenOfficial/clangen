from typing import List

from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.buttons.buttons import _Language


class ChangeLanguageCmd(Command):
    name = "language"
    description = "Change the language of the game"
    usage = "[language]"

    def callback(self, args: List[str]):
        if len(args) == 1:
            if args[0].lower() in _Language.supported_languages:
                _Language.set_language(args[0].lower())
                add_output_line_to_log(f"Language set to {args[0]}")
            else:
                add_output_line_to_log(f"Language {args[0]} is not supported")
        elif len(args) == 0:
            add_output_line_to_log(f"Language is set to {_Language.get_language()}")
        else:
            add_output_line_to_log("Invalid usage")

class ListLanguagesCmd(Command):
    name = "languages"
    description = "List all available languages"

    def callback(self, args: List[str]):
        add_output_line_to_log("Available languages:")
        for lang in _Language.supported_languages:
            add_output_line_to_log(f'- {lang.lstrip("buttons.")}')