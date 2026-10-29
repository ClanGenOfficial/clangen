from typing import List

from scripts.game_structure import constants
from scripts.debug_commands import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.game_structure import game


class SetBiomeCommand(Command):
    name = "set"
    description = "Set the current clan's biome"
    usage = "<biome: str>"

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log("Specify a biome.")
            return
        if not game.clan:
            add_output_line_to_log("No clan loaded. Cannot set biome.")
            return

        biome = args[0].casefold()
        possible_biomes = [b.casefold() for b in constants.BIOME_TYPES]
        if biome not in possible_biomes:
            text_biomes = ", ".join(["'" + b + "'" for b in possible_biomes])
            add_output_line_to_log(
                f"Biome not recognized. Possible arguments: {text_biomes}"
            )
            return
        game.clan.override_biome = biome.capitalize()
        add_output_line_to_log("Biome updated successfully.")


class BiomeCommand(Command):
    name = "biome"
    description = "Get the current clan's biome"

    sub_commands = [SetBiomeCommand()]

    def callback(self, args: List[str]):
        if game.clan:
            if game.clan.override_biome:
                add_output_line_to_log(
                    f"Current biome: {game.clan.override_biome} (override)"
                )
            else:
                add_output_line_to_log(f"Current biome: {game.clan.biome}")
            add_output_line_to_log("To change the biome, use 'biome set [biome]'.")
        else:
            add_output_line_to_log("No clan currently loaded.")
