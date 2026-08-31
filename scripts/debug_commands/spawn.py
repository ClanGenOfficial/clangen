from typing import List

from scripts.cat.enums import CatAge
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.pelts import Pelt
from scripts.cat.sprites.load_sprites import Sprites
from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.game_structure import game


class SpawnPeltsCommand(Command):
    name = "pelts"
    description = "Spawn a cat of each colour for a given pelt."
    alias = ["pelt"]

    def callback(self, args: List[str]):
        possible_pelts_str = ", ".join(
            set(Sprites.PELT_TO_RECIPE.keys()) - {"Tortie", "Calico"}
        )
        if len(args) < 1:
            add_output_line_to_log(
                f"Must specify a pelt! Possible pelts are {possible_pelts_str}."
            )
            return

        pelt_name = args[0]
        if pelt_name not in Sprites.PELT_TO_RECIPE:
            add_output_line_to_log(
                f"Pelt {pelt_name} does not seem to exist! Possible pelts are {possible_pelts_str}."
            )
            return

        for colour in Sprites.PELT_COLOR_PALETTES:
            cat = NewCatFactory.create_cat(
                prefix=f"{colour}_{pelt_name}",
                suffix="",
                moons=60,
                pelt=Pelt(
                    name=pelt_name,
                    colour=colour,
                ),
            )
            cat.pelt.cat_sprites["adult"] = "adult_short2"
            game.clan.add_cat(cat)
            add_output_line_to_log(f"Added {cat.name} with ID {cat.ID}")


class SpawnColoursCommand(Command):
    name = "colours"
    description = "Spawn a cat of each pelt for a given colour."
    aliases = ["color", "colors", "colour"]

    def callback(self, args: List[str]):
        possible_colours_str = ", ".join(Sprites.PELT_COLOR_PALETTES.keys())

        if len(args) < 1:
            add_output_line_to_log(
                f"Must specify a colour! Possible colours are {possible_colours_str}."
            )
            return

        colour = args[0]
        if colour not in Sprites.PELT_COLOR_PALETTES:
            add_output_line_to_log(
                f"Colour {colour} does not seem to exist! This command is case sensitive. Possible colours are {possible_colours_str}."
            )
            return

        for pelt_name in Sprites.PELT_TO_RECIPE:
            if pelt_name in ("Tortie", "Calico"):
                continue
            cat = NewCatFactory.create_cat(
                prefix=f"{pelt_name}_{colour}",
                suffix="",
                moons=60,
                pelt=Pelt(
                    name=pelt_name,
                    colour=colour,
                ),
            )
            cat.pelt.cat_sprites["adult"] = "adult_short2"
            game.clan.add_cat(cat)
            add_output_line_to_log(f"Added {cat.name} with ID {cat.ID}")


class SpawnCommand(Command):
    name = "spawn"
    description = "Spawn specific sets of cats to test things"

    sub_commands = [
        SpawnPeltsCommand(),
        SpawnColoursCommand(),
    ]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
