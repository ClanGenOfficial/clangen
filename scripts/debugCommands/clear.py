from scripts.debugCommands.command import Command

from scripts.debugCommands.utils import _debugClass


class ClearCommand(Command):
    name = "clear"
    description = "Clear the console"
    aliases = ["cls"]

    def callback(self, args: list[str]):
        _debugClass.clear_log()
