from typing import Optional, List

import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.Screens import Screens
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale
from scripts.ui.theme import get_text_box_theme


class MakeClanScreenBase(Screens):
    # variables we are gonna hold onto the whole time
    game_mode: str = "classic"

    clan_name: str = ""
    selected_biome: str = ""
    selected_camp: int = 0
    selected_season: str = ""

    leader: Optional[Cat] = None
    deputy: Optional[Cat] = None
    med_cat: Optional[Cat] = None
    members: List[Cat] = []

    selected_symbol: str = ""

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
        self.elements["previous_step"].disable()
        self.elements["next_step"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 620), (147, 30))),
            "buttons.next_step",
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["random_clan_checkbox"] = UIImageButton(
            ui_scale(pygame.Rect((560, -32), (34, 34))),
            "",
            object_id="@unchecked_checkbox",
            manager=MANAGER,
            tool_tip_text="screens.make_clan.quick_start_tooltip",
            anchors={"top_target": self.elements["previous_step"]},
        )

        self.elements["random_clan_checkbox_label"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((5, -28), (-1, -1))),
            "screens.make_clan.quick_start",
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            anchors={
                "left_target": self.elements["random_clan_checkbox"],
                "top_target": self.elements["random_clan_checkbox"],
            },
        )
