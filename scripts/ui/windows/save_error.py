import pygame
import pygame_gui

from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class SaveErrorWindow(GameWindow):
    def __init__(self, error_text):
        super().__init__(
            ui_scale(pygame.Rect((150, 150), (500, 400))),
        )
        self.changelog_popup_title = pygame_gui.elements.UITextBox(
            "windows.save_failed_title",
            ui_scale(pygame.Rect((20, 10), (445, 375))),
            object_id="#text_box_30",
            container=self,
            text_kwargs={"error": error_text},
        )
