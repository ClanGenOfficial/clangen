from typing import List

from scripts.cat.enums import CatAge
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.pelts import Pelt
from scripts.cat.sprites.load_sprites import Sprites, sprites
from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.game_structure import game


class SpawnPeltsCommand(Command):
    name = "pelts"
    description = "Spawn a cat of each colour for a given pelt."
    usage = "<pelt_name: str>"
    alias = ["pelt", "p"]

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
    usage = "<colour: str>"
    aliases = ["color", "colors", "colour", "c"]

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


class SpawnTintsCommand(Command):
    name = "tints"
    description = "Spawn a cat of each tint for a given pelt and colour."
    usage = "<pelt_name: str> <colour: str>"
    aliases = ["tint", "t"]

    def callback(self, args: List[str]):
        if len(args) < 2:
            add_output_line_to_log(f"Must specify a pelt and colour! (in that order)")
            return

        pelt = args[0]
        possible_pelts_str = ", ".join(
            set(Sprites.PELT_TO_RECIPE.keys()) - {"Tortie", "Calico"}
        )
        if pelt not in Sprites.PELT_TO_RECIPE:
            add_output_line_to_log(
                f"Pelt {pelt} does not seem to exist! Possible pelts are {possible_pelts_str}."
            )
            return

        if pelt in ("Tortie", "Calico"):
            add_output_line_to_log(f"Pelt cannot be Tortie or Calico!")
            return

        colour = args[1]
        possible_colours_str = ", ".join(Sprites.PELT_COLOR_PALETTES.keys())
        if colour not in Sprites.PELT_COLOR_PALETTES:
            add_output_line_to_log(
                f"Colour {colour} does not seem to exist! Possible colours are {possible_colours_str}."
            )
            return

        base_tints = sprites.cat_tints["possible_tints"]["basic"]
        if colour in sprites.cat_tints["colour_groups"]:
            color_group = sprites.cat_tints["colour_groups"].get(colour, "warm")
            colour_tints = sprites.cat_tints["possible_tints"][color_group]
        else:
            colour_tints = []
        possible_tints = base_tints + colour_tints

        for tint in possible_tints:
            cat = NewCatFactory.create_cat(
                prefix=f"{tint}_{pelt}_{colour}",
                suffix="",
                moons=60,
                pelt=Pelt(name=pelt, colour=colour, tint=tint),
            )
            cat.pelt.cat_sprites["adult"] = "adult_short2"
            game.clan.add_cat(cat)
            add_output_line_to_log(f"Added {cat.name} with ID {cat.ID}")


class SpawnCommand(Command):
    name = "spawn"
    description = "Spawn specific sets of cats to test things"
    aliases = ["sp"]

    sub_commands = [
        SpawnPeltsCommand(),
        SpawnColoursCommand(),
        SpawnTintsCommand(),
    ]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
