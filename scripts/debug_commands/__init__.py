from typing import List

from scripts.debug_commands.cat import CatsCommand
from scripts.debug_commands.cat_pregnancy import PregnanciesCommand
from scripts.debug_commands.cat_relationship import RelationshipsCommand
from scripts.debug_commands.command import Command
from scripts.debug_commands.eval import EvalCommand
from scripts.debug_commands.fps import FpsCommand
from scripts.debug_commands.help import HelpCommand, ClearCommand
from scripts.debug_commands.settings import (
    SettingsCommand,
    DevToolsCommand,
)
from scripts.debug_commands.clan import ClanCommand
from scripts.debug_commands.cruel import CruelCommand
from scripts.debug_commands.biome import BiomeCommand
from scripts.debug_commands.spawn import SpawnCommand

command_list: List[Command] = [
    SettingsCommand(),
    DevToolsCommand(),
    EvalCommand(),
    BiomeCommand(),
    FpsCommand(),
    CatsCommand(),
    ClanCommand(),
    CruelCommand(),
    PregnanciesCommand(),
    RelationshipsCommand(),
    SpawnCommand(),
    ClearCommand(),
]

help_command = HelpCommand(command_list)
command_list.append(help_command)
