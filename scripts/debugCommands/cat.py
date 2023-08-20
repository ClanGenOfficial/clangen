from typing import List

from scripts.debugCommands.command import Command

from scripts.debugCommands.utils import add_output_line_to_log

from scripts.game_structure.game_essentials import game
from scripts.cat.cats import Cat

class addCatCommand(Command):
    name = "add"
    description = "Add a cat"
    aliases = ["a"]

    def callback(self, args: List[str]):
        cat = Cat()
        game.clan.add_cat(cat)
        add_output_line_to_log(f"Added {cat.name} with ID {cat.ID}")

class removeCatCommand(Command):
    name = "remove"
    description = "Remove a cat"
    aliases = ["r"]
    usage = "<cat name|id>"

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log("Please specify a cat name or ID")
            return
        for cat in Cat.all_cats_list:
            if str(cat.name).lower() == args[0].lower() or cat.ID == args[0]:
                game.clan.remove_cat(cat.ID)
                add_output_line_to_log(f"Removed {cat.name} with ID {cat.ID}")
                return
        add_output_line_to_log(f"Could not find cat with name or ID {args[0]}")

class listCatsCommand(Command):
    name = "list"
    description = "List all cats"
    aliases = ["l"]

    def callback(self, args: List[str]):
        for cat in Cat.all_cats_list:
            add_output_line_to_log(f"{cat.ID} - {cat.name}, {cat.status}, {cat.moons} moons old")

class ageCatsCommand(Command):
    name = "age"
    description = "Age a cat"
    aliases = ["a"]
    usage = "<cat name|id> [number]"

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log("Please specify a cat name or ID")
            return
        for cat in Cat.all_cats_list:
            if str(cat.name).lower() == args[0].lower() or cat.ID == args[0]:
                if len(args) == 1:
                    add_output_line_to_log(f"{cat.name} is {cat.moons} moons old")
                    return
                else:
                    if args[1].startswith("+"):
                        cat.moons += int(args[1][1:])
                    elif args[1].startswith("-"):
                        cat.moons -= int(args[1][1:])
                    else:
                        cat.moons = int(args[1])
                    add_output_line_to_log(f"{cat.name} is now {cat.moons} moons old")



class CatsCommand(Command):
    name = "cats"
    description = "Manage Cats"
    aliases = ["cat"]

    subCommands = [
        addCatCommand(),
        removeCatCommand(),
        listCatsCommand(),
        ageCatsCommand()
    ]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")