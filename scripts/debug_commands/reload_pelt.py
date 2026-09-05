from scripts.cat.sprites.display_sprites import generate_sprite
from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log
from scripts.cat.sprites.load_sprites import Sprites
from scripts.cat.cats import Cat
from scripts.game_structure.game.switches import switch_get_value, Switch

from typing import TYPE_CHECKING

from scripts.screens import all_screens

if TYPE_CHECKING:
    from scripts.screens.Screens import Screens


class ReloadPeltCommand(Command):
    name = "reload-recipes"
    description = "Reloads pelts recipes"
    aliases = ["rr"]

    def callback(self, _: list[str]):
        Sprites.load_pelt_recipes()
        for cat in Cat.all_cats_list:
            cat.sprite = generate_sprite(cat)
        current_screen: Screens = all_screens.get_screen(
            switch_get_value(Switch.cur_screen)
        )
        current_screen.exit_screen()
        current_screen.screen_switches()

        add_output_line_to_log("Reloaded pelt recipes!")
