from typing import List

from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log, clear_log


class ClearCommand(Command):
    name = "clear"
    description = "Clear the console"
    aliases = ["self", "clr"]

    def callback(self, args: List[str]):
        clear_log()


class HelpCommand(Command):
    name = "help"
    description = "Shows help for commands"
    usage = "<command: str>"
    aliases = ["h"]

    command_list: List[Command] = []

    def __init__(self, commands: List[Command]):
        self.command_list = commands + [self]

    def _get_command_help_text(self, command: Command):
        add_output_line_to_log(f"Help for {command.name}:")
        add_output_line_to_log(f"   {command.description}")
        add_output_line_to_log(f"   Usage: {command.name} {command.usage}")
        add_output_line_to_log(f"   Aliases: {command.valid_names}")

        if len(command.sub_commands) > 0:
            add_output_line_to_log(f"  Subcommands:")
            for sub_command in command.sub_commands:
                add_output_line_to_log(
                    f"      {sub_command.name}: {sub_command.description}"
                )

    def callback(self, args: List[str]):
        if len(args) == 0:
            for command in self.command_list:
                add_output_line_to_log(f"{command.name}: {command.description}")
                for sub_command in command.sub_commands:
                    add_output_line_to_log(
                        f"  {sub_command.name}: {sub_command.description}"
                    )
        else:
            for command in self.command_list:
                if args[0] not in command.valid_names:
                    continue

                if len(args) > 1:
                    while len(args) > 1 and len(command.sub_commands) > 0:
                        command_found = False
                        for sub_command in command.sub_commands:
                            if args[1] not in sub_command.valid_names:
                                continue

                            command_found = True
                            args = args[1:]
                            command = sub_command

                        if not command_found:
                            break

                self._get_command_help_text(command)
                return

            add_output_line_to_log(f"Command {args[0]} not found")
