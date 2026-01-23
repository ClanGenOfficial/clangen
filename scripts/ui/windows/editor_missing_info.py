import pygame
from scripts.game_structure.ui_elements import UITextBoxTweaked
from scripts.ui.windows.base_window import GameWindow
from scripts.utility import ui_scale


class EditorMissingInfo(GameWindow):
    def __init__(self, alert_text):
        super().__init__(
            ui_scale(pygame.Rect((200, 200), (400, 200))),
            window_display_title="Info Missing",
            object_id="#editor_missing_info_window",
        )

        text = "windows.editor_missing_info" if not alert_text else alert_text
        self.missing_info = UITextBoxTweaked(
            text,
            ui_scale(pygame.Rect((0, 30), (360, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
            anchors={
                "centerx": "centerx",
            },
        )
