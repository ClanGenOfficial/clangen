import pygame
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import UITextBoxTweaked


class RelChangeDetailWindow(GameWindow):
    """
    This window displays given rel logs.
    """

    def __init__(self, rel_logs: list[str]):
        super().__init__(ui_scale(pygame.Rect((100, 200), (600, 400))))

        text = "<br><br>".join(rel_logs)

        self.heading = UITextBoxTweaked(
            text,
            ui_scale(pygame.Rect((10, 20), (580, 370))),
            object_id="#text_box_30_horizcenter",
            manager=MANAGER,
            container=self,
        )
