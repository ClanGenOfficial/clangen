from typing import List

from scripts.debugCommands.command import Command
from typing import List

from scripts.debugCommands.utils import _debugClass


class ClearCommand(Command):
    name = "clear"
    description = "Clear the console"
    aliases = ["cls"]

    def callback(self, args: List[str]):
        _debugClass.clear_log()
