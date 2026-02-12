from random import choice
from re import sub

import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.cat.enums import CatSocial
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UIImageButton,
    UICheckbox,
)
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.cat.sprites.display_sprites import update_sprite
from scripts.events_module.text_adjust import process_text
from scripts.ui.scale import ui_scale


class LeaveClanWindow(GameWindow):
    """This window allows the user to send the selected cat away from the Clan"""

    def __init__(self, cat: Cat):
        super().__init__(
            ui_scale(pygame.Rect((250, 225), (300, 250))),
        )
        self.checkboxes = {}
        self.the_cat = cat
        self.chosen_social = None

        self.heading = pygame_gui.elements.UITextBox(
            "windows.leave_clan",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

        prev_element = self.heading
        for social in (CatSocial.LONER, CatSocial.ROGUE, CatSocial.KITTYPET):
            self.checkboxes[social] = UICheckbox(
                position=(-30, 10),
                manager=MANAGER,
                container=self,
                anchors={"top_target": prev_element, "centerx": "centerx"},
            )

            self.checkboxes[f"{social}_text"] = pygame_gui.elements.UITextBox(
                i18n.t(social, count=1),
                ui_scale(pygame.Rect((0, 10), (100, -1))),
                object_id="#text_box_30_horizleft_spacing_95",
                manager=MANAGER,
                container=self,
                anchors={
                    "top_target": prev_element,
                    "left_target": self.checkboxes[social],
                },
            )
            prev_element = self.checkboxes[social]

        self.done_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 200), (77, 30))),
            "buttons.done_lower",
            get_button_dict(ButtonStyles.SQUOVAL, (77, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

    def process_event(self, event):
        super().process_event(event)

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                self.the_cat.leave_clan(self.chosen_social)
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()
                self.kill()

            for name, button in self.checkboxes.items():
                if event.ui_element == button:
                    for _b in self.checkboxes.values():
                        if isinstance(_b, UICheckbox):
                            _b.uncheck()
                    if button.checked:
                        button.uncheck()
                    else:
                        button.check()
                        self.chosen_social = CatSocial(name)
