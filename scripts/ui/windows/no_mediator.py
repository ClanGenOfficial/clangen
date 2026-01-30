import pygame
import pygame_gui

from scripts.game_structure import game
from scripts.game_structure.game.switches import (
    switch_set_value,
    Switch,
)
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import UITextBoxTweaked, UISurfaceImageButton
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class NoMediatorsWindow(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((300, 200), (250, 170))),
            window_display_title="No Mediators",
            click_outside_to_close=False,
        )

        self.missing_info = UITextBoxTweaked(
            "windows.no_mediators",
            ui_scale(pygame.Rect((0, 30), (220, -1))),
            line_spacing=1,
            manager=MANAGER,
            object_id="#text_box_30_horizcenter",
            container=self,
            anchors={
                "centerx": "centerx",
            },
        )

        self.return_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 80), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

        self.cat_list_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 115), (105, 30))),
            "buttons.cat_list",
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
            if event.ui_element == self.cat_list_button:
                switch_set_value(Switch.cur_screen, GameScreen.LIST)
                game.last_screen_forupdate = GameScreen.MEDIATION
                game.switch_screens = True
                self.kill()

        return super().process_event(event)
