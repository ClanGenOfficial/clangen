import threading

import pygame
import pygame_gui

from scripts.game_structure.ui_elements import (
    UITextBoxTweaked,
)
from scripts.housekeeping.progress_bar_updater import UIUpdateProgressBar
from scripts.housekeeping.update import self_update, UpdateChannel
from scripts.housekeeping.version import get_version_info
from scripts.ui.windows.window_base_class import GameWindow
from scripts.utility import ui_scale


class UpdateWindow(GameWindow):
    def __init__(self, last_screen, announce_restart_callback):
        super().__init__(
            ui_scale(pygame.Rect((250, 200), (300, 160))),
        )
        self.last_screen = last_screen
        self.update_message = pygame_gui.elements.UITextBox(
            "windows.update_message",
            ui_scale(pygame.Rect((20, 10), (260, -1))),
            object_id="#text_box_30_horizcenter_spacing_95",
            starting_height=4,
            container=self,
        )
        self.announce_restart_callback = announce_restart_callback

        self.step_text = UITextBoxTweaked(
            "windows.downloading_update",
            ui_scale(pygame.Rect((20, 40), (260, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
        )

        self.progress_bar = UIUpdateProgressBar(
            ui_scale(pygame.Rect((20, 65), (260, 45))),
            self.step_text,
            object_id="progress_bar",
            container=self,
        )

        self.update_thread = threading.Thread(
            target=self_update,
            daemon=True,
            args=(
                UpdateChannel(get_version_info().release_channel),
                self.progress_bar,
                announce_restart_callback,
            ),
        )
        self.update_thread.start()
