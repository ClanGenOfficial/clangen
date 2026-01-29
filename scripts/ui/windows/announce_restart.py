import threading
import time

import pygame

from scripts.game_structure.ui_elements import (
    UITextBoxTweaked,
)
from scripts.ui.windows.window_base_class import GameWindow
from scripts.utility import ui_scale


class RestartAnnouncementWindow(GameWindow):
    def __init__(self, last_screen):
        super().__init__(
            ui_scale(pygame.Rect((250, 200), (300, 90))),
            back_button=False,
        )
        self.last_screen = last_screen
        self.announce_message = UITextBoxTweaked(
            f"windows.restart_announce",
            ui_scale(pygame.Rect((20, 20), (260, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
            text_kwargs={"count": "3"},
        )

        threading.Thread(target=self.update_text, daemon=True).start()

    def update_text(self):
        for i in range(2, 0, -1):
            time.sleep(1)
            self.announce_message.set_text(
                "windows.restart_announce", text_kwargs={"count": i}
            )
