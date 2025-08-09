import os

import pygame
import pygame_gui

from scripts.game_structure.game.switches import (
    switch_get_value,
    Switch,
)
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
    UITextBoxTweaked,
    UIImageButton,
)
from scripts.housekeeping.datadir import get_cache_dir
from scripts.housekeeping.update import get_latest_version_number
from scripts.housekeeping.version import get_version_info
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.announce_restart import AnnounceRestart
from scripts.ui.windows.base_window import GameWindow
from scripts.ui.windows.update import UpdateWindow
from scripts.utility import ui_scale


class UpdateAvailablePopup(GameWindow):
    def __init__(self, show_checkbox: bool = False):
        super().__init__(
            ui_scale(pygame.Rect((200, 200), (400, 230))),
            window_display_title="Update available",
            object_id="#game_over_window",
        )

        self.begin_update_title = UIImageButton(
            ui_scale(pygame.Rect((97, 15), (200, 40))),
            "",
            object_id="#new_update_button",
            container=self,
        )

        latest_version_number = "{:.16}".format(get_latest_version_number())
        current_version_number = "{:.16}".format(get_version_info().version_number)

        self.game_over_message = UITextBoxTweaked(
            "update_available",
            ui_scale(pygame.Rect((10, 80), (400, -1))),
            line_spacing=0.8,
            object_id="#update_popup_title",
            container=self,
            text_kwargs={"latest_version_number": latest_version_number},
        )

        self.game_over_message = UITextBoxTweaked(
            "windows.current_version",
            ui_scale(pygame.Rect((11, 100), (400, -1))),
            line_spacing=0.8,
            object_id="#current_version",
            container=self,
            text_kwargs={"ver": current_version_number},
        )

        self.game_over_message = UITextBoxTweaked(
            "windows.install_update",
            ui_scale(pygame.Rect((10, 131), (200, -1))),
            line_spacing=0.8,
            object_id="#text_box_30",
            container=self,
        )

        self.box_unchecked = UIImageButton(
            ui_scale(pygame.Rect((7, 183), (34, 34))),
            "",
            object_id="@unchecked_checkbox",
            container=self,
        )
        self.box_checked = UIImageButton(
            ui_scale(pygame.Rect((7, 183), (34, 34))),
            "",
            object_id="@checked_checkbox",
            container=self,
        )
        self.box_text = UITextBoxTweaked(
            "windows.dont_ask_again",
            ui_scale(pygame.Rect((39, 190), (125, -1))),
            line_spacing=0.8,
            object_id="#text_box_30",
            container=self,
        )

        self.continue_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((278, 185), (102, 30))),
            "buttons.continue",
            get_button_dict(ButtonStyles.SQUOVAL, (77, 30)),
            object_id="@buttonstyles_squoval",
            container=self,
        )

        self.cancel_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((187, 185), (78, 30))),
            "buttons.cancel",
            get_button_dict(ButtonStyles.SQUOVAL, (77, 30)),
            object_id="@buttonstyles_squoval",
            container=self,
        )

        if show_checkbox:
            self.box_unchecked.enable()
            self.box_checked.hide()
        else:
            self.box_checked.hide()
            self.box_unchecked.hide()
            self.box_text.hide()

        self.continue_button.enable()
        self.cancel_button.enable()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.continue_button:
                self.x = UpdateWindow(
                    switch_get_value(Switch.cur_screen), self.announce_restart_callback
                )
                self.kill()
            elif event.ui_element == self.cancel_button:
                self.kill()
            elif event.ui_element == self.box_unchecked:
                self.box_unchecked.disable()
                self.box_unchecked.hide()
                self.box_checked.enable()
                self.box_checked.show()
                with open(
                    f"{get_cache_dir()}/suppress_update_popup", "w", encoding="utf-8"
                ) as write_file:
                    write_file.write(get_latest_version_number())
            elif event.ui_element == self.box_checked:
                self.box_checked.disable()
                self.box_checked.hide()
                self.box_unchecked.enable()
                self.box_unchecked.show()
                if os.path.exists(f"{get_cache_dir()}/suppress_update_popup"):
                    os.remove(f"{get_cache_dir()}/suppress_update_popup")
        return super().process_event(event)

    def announce_restart_callback(self):
        self.x.kill()
        y = AnnounceRestart(switch_get_value(Switch.cur_screen))
        y.update(1)
