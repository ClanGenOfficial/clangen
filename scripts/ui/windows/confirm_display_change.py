from typing import TYPE_CHECKING

import pygame
import pygame_gui

from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import UISurfaceImageButton
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.utility import ui_scale, ui_scale_offset

if TYPE_CHECKING:
    from scripts.screens.Screens import Screens


class ConfirmDisplayChangesWindow(GameWindow):
    def __init__(self, source_screen: "Screens"):
        super().__init__(
            ui_scale(pygame.Rect((275, 270), (250, 160))),
        )
        button_spacing = 10

        dismiss_button_rect = ui_scale(pygame.Rect((0, 0), (140, 30)))
        dismiss_button_rect.bottomright = ui_scale_offset(
            (-button_spacing, -button_spacing)
        )

        self.dismiss_button = UISurfaceImageButton(
            dismiss_button_rect,
            "windows.confirm_changes",
            get_button_dict(ButtonStyles.SQUOVAL, (140, 30)),
            MANAGER,
            container=self,
            object_id="@buttonstyles_squoval",
            anchors={
                "left": "right",
                "top": "bottom",
                "right": "right",
                "bottom": "bottom",
            },
        )

        revert_rect = ui_scale(pygame.Rect((0, 0), (75, 30)))
        revert_rect.bottomleft = ui_scale_offset((button_spacing, -button_spacing))

        self.revert_button = UISurfaceImageButton(
            revert_rect,
            "windows.revert",
            get_button_dict(ButtonStyles.SQUOVAL, (75, 30)),
            MANAGER,
            container=self,
            object_id="@buttonstyles_squoval",
            anchors={
                "left": "left",
                "bottom": "bottom",
            },
        )

        text_block_rect = pygame.Rect(
            ui_scale_offset((0, 22)),
            (
                self.get_container().get_size()[0],
                -1,
            ),
        )
        self.text_block = pygame_gui.elements.UITextBox(
            "windows.display_change_confirm",
            text_block_rect,
            manager=MANAGER,
            object_id="#text_box_30_horizcenter",
            container=self,
            anchors={
                "left": "left",
                "top": "top",
                "right": "right",
                "bottom": "bottom",
            },
            text_kwargs={"count": 10},
        )
        self.text_block.disable()
        self.text_block.rebuild_from_changed_theme_data()

        # make a timeout that will call in 10 seconds - if this window isn't closed,
        # it'll be used to revert the change
        pygame.time.set_timer(pygame.USEREVENT + 10, 10000, loops=1)

        self.source_screen_name = source_screen.name.replace(" ", "_")

    def revert_changes(self):
        """Revert the changes made to screen scaling"""
        from scripts.game_structure.screen_settings import toggle_fullscreen
        from scripts.screens import all_screens

        toggle_fullscreen(
            None,
            source_screen=all_screens.get_screen(self.source_screen_name),
            show_confirm_dialog=False,
        )

    def process_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.dismiss_button:
                self.kill()
            elif event.ui_element == self.revert_button:
                self.revert_changes()
        elif event.type == pygame.USEREVENT + 10:
            self.revert_changes()
            self.kill()
        return super().process_event(event)
