from typing import List

from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log, add_multiple_lines_to_log

import builtins
from typing import List

warningAccepted = False


class EvalCommand(Command):
    name = "eval"
    description = "Evaluate a python expression"
    usage = "<expression>"
    aliases = ["e"]
    bypassConjoinedStrings = True

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log(f"Usage: {self.name} {self.usage}")
            return
        global warningAccepted  # pylint: disable=global-statement,global-variable-not-assigned
        if not warningAccepted:
            add_multiple_lines_to_log("""WARNING: This command can be used to run code in your game. Only use this if you know what you're doing.
                                         If you have been told to use this by anyone other than the official clangen discord contributors, BLOCK THEM IMMEDIATELY.
                                         If you are not sure what this means, DO NOT USE THIS COMMAND.
                                         To disable this warning, type \"understandrisks\".""")
            return

        def print(*args, **kwargs):  # pylint: disable=redefined-builtin
            """
            Overwrite the print function so that it prints to the console
            """
            builtins.print(*args, **kwargs)
            add_output_line_to_log(' '.join([str(arg) for arg in args]))

        cmd = ' '.join(args)
        cmd = cmd.replace('\\n', '\n')
        try:
            exec(cmd)  # pylint: disable=exec-used
        except Exception as e:
            builtins.print(e)
            add_output_line_to_log("Eval failed: " + str(e))
        print = builtins.print


class UnderstandRisksCommand(Command):
    name = "understandrisks"
    description = "Accept the risks of using the eval command"

    def callback(self, args: List[str]):
        global warningAccepted  # pylint: disable=global-statement
        warningAccepted = True
        add_output_line_to_log(
            "You have disabled the warning for the eval command. Any code you run is your responsibility.")
