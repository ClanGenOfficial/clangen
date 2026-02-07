from typing import List

from scripts.debug_commands.cat import CatsCommand
from scripts.debug_commands.cat_pregnancy import PregnanciesCommand
from scripts.debug_commands.cat_relationship import RelationshipsCommand
from scripts.debug_commands.command import Command
from scripts.debug_commands.eval import EvalCommand
from scripts.debug_commands.fps import FpsCommand
from scripts.debug_commands.help import HelpCommand
from scripts.debug_commands.settings import ToggleCommand, SetCommand, GetCommand
from scripts.debug_commands.clan import ClanCommand
from scripts.debug_commands.biome import BiomeCommand

commandList: List[Command] = [
    ToggleCommand(),
    SetCommand(),
    GetCommand(),
    EvalCommand(),
    BiomeCommand(),
    FpsCommand(),
    CatsCommand(),
    ClanCommand(),
    PregnanciesCommand(),
    RelationshipsCommand(),
]

helpCommand = HelpCommand(commandList)
commandList.append(helpCommand)
