import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.events_module.text_adjust import adjust_list_text
from scripts.game_structure import constants
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale
from scripts.ui.windows.window_base_class import GameWindow


class CruelLockedAction(GameWindow):
    def __init__(self) -> None:
        super().__init__(
            ui_scale(pygame.Rect((200, 240), (400, 150))),
            window_display_title="Cruel Locked Action",
        )
        self.conflict_message = UITextBoxTweaked(
            "windows.cruel_locked_action",
            ui_scale(pygame.Rect((0, 20), (380, -1))),
            line_spacing=1,
            manager=MANAGER,
            object_id="#text_box_30_horizcenter",
            starting_height=self.layer,
            container=self,
            anchors={
                "centerx": "centerx",
            },
        )

        self.done_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((150, 20), (105, 30))),
            "buttons.done_lower",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            starting_height=self.layer,
            container=self,
            anchors={"top_target": self.conflict_message},
        )

    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                self.kill()
        return super().process_event(event)
