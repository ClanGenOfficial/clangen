from scripts.debugCommands.command import Command
from scripts.debugCommands.utils import add_output_line_to_log

# Command is an abstract class


class HelpCommand(Command):
    name = "help"
    description = "Shows help for commands"
    usage = "[command]"
    aliases = ["h"]

    commandList: list[Command] = []

    def __init__(self, commandList: list[Command]):
        self.commandList = commandList + [self]

    def callback(self, args: list[str]):
        if len(args) == 0:
            add_output_line_to_log("Commands:")
            for command in self.commandList:
                add_output_line_to_log(
                    f"  {command.name}: {command.description}")
        else:
            for command in self.commandList:
                if args[0] in command._aliases:  # pylint: disable=protected-access
                    add_output_line_to_log(f"Help for {command.name}:")
                    add_output_line_to_log(f"  {command.description}")
                    add_output_line_to_log(
                        f"  Usage: {command.name} {command.usage}")
                    break
            else:
                add_output_line_to_log(f"Command {args[0]} not found")
