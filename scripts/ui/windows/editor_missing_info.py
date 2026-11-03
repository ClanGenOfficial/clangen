import pygame
import pygame_gui
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class EditorMissingInfoWindow(GameWindow):
    def __init__(self, alert_text):
        super().__init__(
            ui_scale(pygame.Rect((200, 200), (400, 200))),
        )

        text = "windows.editor_missing_info" if not alert_text else alert_text
        self.missing_info = pygame_gui.elements.UITextBox(
            text,
            ui_scale(pygame.Rect((0, 30), (360, -1))),
            object_id="#text_box_30_horizcenter",
            container=self,
            anchors={
                "centerx": "centerx",
            },
        )
