from random import choice
from re import sub
from typing import Optional, List
from uuid import uuid4

import pygame
import pygame_gui

from scripts.cat import save_load
from scripts.cat.cats import Cat
from scripts.cat.names import names
from scripts.clan import Clan
from scripts.events_module.patrol.patrol import Patrol
from scripts.game_structure import game
from scripts.game_structure.game import switch_get_value, Switch
from scripts.game_structure.game.switches import switch_set_dict_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.Screens import Screens
from scripts.screens.enums import GameScreen
from scripts.screens.screens_core.screens_core import rebuild_top_menu_buttons
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale
from scripts.ui.theme import get_text_box_theme


def _clan_name_exists(new_clan_name: str):
    return new_clan_name.casefold() in (
        clan.casefold() for clan in switch_get_value(Switch.clan_list)
    )


def _generate_unique_clan_name(new_clan_name: str):
    return f"{new_clan_name}_{uuid4()}"


class MakeClanScreenBase(Screens):
    def __init__(self, name="make_clan_screen"):
        super().__init__(name)

        self.elements = {}

    def screen_switches(self):
        super().screen_switches()
        self.set_mute_button_position("topright")
        self.show_mute_buttons()
        self.set_bg("default", "mainmenu_bg")

        # Buttons that appear on every screen.
        self.elements["menu_warning"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.menu_warning",
            ui_scale(pygame.Rect((25, 25), (600, -1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            manager=MANAGER,
        )
        self.elements["main_menu"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 50), (153, 30))),
            "buttons.main_menu",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_squoval",
            starting_height=1,
        )
        self.elements["previous_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((253, 620), (147, 30))),
            "buttons.previous_step",
            get_button_dict(ButtonStyles.MENU_LEFT, (147, 30)),
            object_id="@buttonstyles_menu_left",
            manager=MANAGER,
            starting_height=2,
        )
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 620), (147, 30))),
            "buttons.next_step",
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["next_step"].disable()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["main_menu"]:
                self.change_screen(GameScreen.START)

        return super().handle_event(event)

    def exit_screen(self):
        for ele in self.elements.values():
            ele.kill()
        self.elements.clear()
        return super().exit_screen()

    def save_clan(self):
        game.mediated.clear()
        game.patrolled.clear()
        game.just_died.clear()
        game.dead_cats_to_grieve.clear()
        save_load.faded_ids.clear()
        Cat.outside_cats.clear()
        Patrol.used_patrols.clear()
        save_id = switch_get_value(Switch.clan_creation_info)["name"]

        # extra sanitization for filenames
        clan_name = sub(r"[/\\?%*:|\"<>\x7F\x00-\x1F]", "-", save_id)
        if _clan_name_exists(clan_name):
            switch_set_dict_value(
                Switch.clan_creation_info, "name", _generate_unique_clan_name(clan_name)
            )

        game.clan = Clan(
            displayname=clan_name,
            **switch_get_value(Switch.clan_creation_info),
        )
        game.clan.create_clan()
        game.cur_events_list.clear()
        game.herb_events_list.clear()
        game.clan.herb_supply.start_storage(
            len(switch_get_value(Switch.clan_creation_info)["starting_members"])
        )
        game.clan.save_herb_supply(game.clan)
        game.clan.grief_strings.clear()
        Cat.sort_cats()
        rebuild_top_menu_buttons()

    def random_biome_selection(self):
        # Select a random biome and background
        possible_biomes = ["Forest", "Mountainous", "Plains", "Beach"]
        # ensuring that the new random camp will not be the same one
        if switch_get_value(Switch.clan_creation_info).get("biome"):
            possible_biomes.remove(switch_get_value(Switch.clan_creation_info)["biome"])
        chosen_biome = choice(possible_biomes)
        return chosen_biome

    def random_clan_name(self):
        clan_names = (
            names.names_dict["normal_prefixes"] + names.names_dict["clan_prefixes"]
        )
        if switch_get_value(Switch.clan_creation_info).get("name"):
            clan_names.remove(switch_get_value(Switch.clan_creation_info)["name"])

        return choice(clan_names)
