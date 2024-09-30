from typing import List

from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log


# Command is an abstract class


class ClearCommand(Command):
    name = "clear"
    description = "Clear the console"
    aliases = ["self"]

    def callback(self, args: List[str]):
        pass


class HelpCommand(Command):
    name = "help"
    description = "Shows help for commands"
    usage = "[command]"
    aliases = ["h"]

    commandList: List[Command] = []

    def __init__(self, command_list: List[Command]):
        self.commandList = command_list + [self, ClearCommand()]

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log("Commands:")
            for command in self.commandList:
                add_output_line_to_log(f"  {command.name}: {command.description}")
                for subcommand in command.sub_commands:
                    add_output_line_to_log(
                        f"    {subcommand.name}: {subcommand.description}"
                    )
        else:
            for command in self.commandList:
                if args[0] in command._aliases:  # pylint: disable=protected-access
                    if len(args) > 1:
                        for sub_command in command.sub_commands:
                            if (
                                args[1] in sub_command._aliases
                            ):  # pylint: disable=protected-access
                                add_output_line_to_log(
                                    f"Help for {command.name} {sub_command.name}:"
                                )
                                add_output_line_to_log(f"  {sub_command.description}")
                                add_output_line_to_log(
                                    f"  Usage: {command.name} {sub_command.name} {sub_command.usage}"
                                )
                                return
                    add_output_line_to_log(f"Help for {command.name}:")
                    add_output_line_to_log(f"  {command.description}")
                    add_output_line_to_log(f"  Usage: {command.name} {command.usage}")
                    for subcommand in command.sub_commands:
                        add_output_line_to_log(
                            f"    {subcommand.name}: {subcommand.description}"
                        )
                    break
            else:
                add_output_line_to_log(f"Command {args[0]} not found")
