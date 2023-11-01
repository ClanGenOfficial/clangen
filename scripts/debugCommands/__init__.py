from scripts.debugCommands.command import Command
from scripts.debugCommands.help import HelpCommand
from scripts.debugCommands.settings import ToggleCommand, SetCommand, GetCommand
from scripts.debugCommands.eval import EvalCommand
from scripts.debugCommands.fps import FpsCommand
from scripts.debugCommands.cat import CatsCommand
from typing import List

commandList: List[Command] = [
    ToggleCommand(),
    SetCommand(),
    GetCommand(),
    EvalCommand(),
    FpsCommand(),
    CatsCommand()
]

helpCommand = HelpCommand(commandList)
commandList.append(helpCommand)
