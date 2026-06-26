import i18n
import pygame
import pygame_gui

from scripts.config import get_config
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class CruelCardLimit(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((300, 200), (250, 170))),
            window_display_title="Cruel Card Limit",
        )

        self.limit_message = UITextBoxTweaked(
            i18n.t(
                "windows.cruel_card_limit",
                amount=get_config("cruel_season.card_limit"),
            ),
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
            ui_scale(pygame.Rect((0, 10), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx", "top_target": self.limit_message},
        )

    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.return_button:
                self.kill()

        return super().process_event(event)
