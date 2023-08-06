from scripts.debugCommands.command import Command
from scripts.debugCommands.help import HelpCommand
from scripts.debugCommands.settings import ToggleCommand, SetCommand, GetCommand
from scripts.debugCommands.eval import EvalCommand, UnderstandRisksCommand
from scripts.debugCommands.clear import ClearCommand
from scripts.debugCommands.fps import FpsCommand

commandList: list[Command] = [
    ToggleCommand(),
    SetCommand(),
    GetCommand(),
    EvalCommand(),
    UnderstandRisksCommand(),
    ClearCommand(),
    FpsCommand()
]

helpCommand = HelpCommand(commandList)
commandList.append(helpCommand)
