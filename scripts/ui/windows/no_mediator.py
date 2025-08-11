import pygame
import pygame_gui

from scripts.game_structure.game.switches import (
    switch_set_value,
    Switch,
    switch_get_value,
)
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import UITextBoxTweaked, UISurfaceImageButton
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.base_window import GameWindow
from scripts.utility import ui_scale


class NoMediators(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((300, 200), (200, 150))),
            window_display_title="No Mediators",
            object_id="#window_base_theme",
            click_outside_to_close=False,
        )

        self.missing_info = UITextBoxTweaked(
            "windows.no_mediators",
            ui_scale(pygame.Rect((0, 30), (200, -1))),
            line_spacing=1,
            manager=MANAGER,
            object_id="#text_box_30_horizcenter",
            container=self,
            anchors={
                "centerx": "centerx",
            },
        )

        self.return_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 100), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in (self.return_button, self.back_button):
                switch_set_value(Switch.cur_screen, game.last_screen_forupdate)
                game.last_screen_forupdate = GameScreen.MEDIATION
                game.switch_screens = True
                self.kill()

        return super().process_event(event)
