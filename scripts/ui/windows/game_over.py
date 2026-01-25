import pygame
import pygame_gui

from scripts.game_structure.game.switches import (
    switch_get_value,
    Switch,
    switch_set_value,
)
from scripts.game_structure import game
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UITextBoxTweaked,
)
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.utility import ui_scale


class GameOverWindow(GameWindow):
    def __init__(self, last_screen):
        super().__init__(
            ui_scale(pygame.Rect((250, 200), (300, 180))),
        )
        self.clan_name = str(game.clan.displayname + "Clan")
        self.last_screen = last_screen
        self.game_over_message = UITextBoxTweaked(
            "windows.game_over_message",
            ui_scale(pygame.Rect((20, 20), (260, -1))),
            line_spacing=1,
            object_id="",
            container=self,
            text_kwargs={"clan": self.clan_name},
        )

        self.game_over_message = UITextBoxTweaked(
            "windows.game_over_leave_message",
            ui_scale(pygame.Rect((20, 155), (260, -1))),
            line_spacing=0.8,
            object_id="#text_box_22_horizcenter",
            container=self,
        )

        self.begin_anew_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 115), (111, 30))),
            "windows.begin_anew",
            get_button_dict(ButtonStyles.SQUOVAL, (111, 30)),
            object_id="@buttonstyles_squoval",
            container=self,
        )
        self.not_yet_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((159, 115), (111, 30))),
            "windows.not_yet",
            get_button_dict(ButtonStyles.SQUOVAL, (111, 30)),
            object_id="@buttonstyles_squoval",
            container=self,
        )

        self.not_yet_button.enable()
        self.begin_anew_button.enable()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.begin_anew_button:
                game.last_screen_forupdate = switch_get_value(Switch.cur_screen)
                switch_set_value(Switch.cur_screen, GameScreen.START)
                game.switch_screens = True
                self.kill()
            elif event.ui_element == self.not_yet_button:
                self.kill()
        return super().process_event(event)
