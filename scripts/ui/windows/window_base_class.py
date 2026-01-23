import pygame
import pygame_gui
from pygame_gui.elements import UIWindow

from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import UIImageButton
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.utility import (
    ui_scale,
    ui_scale_offset,
    ui_scale_value,
)


class GameWindow(UIWindow):
    """
    Basic window class, this sets blocking, creates an exit button, and handles the exit event
    """

    def __init__(
        self,
        relative_rect,
        window_display_title: str = None,
        object_id: str = "#window_base_theme",
        resizable: bool = False,
        always_on_top: bool = True,
        back_button: bool = True,
        click_outside_to_close: bool = True,
    ):
        super().__init__(
            relative_rect,
            window_display_title=window_display_title,
            object_id=object_id,
            resizable=resizable,
            always_on_top=always_on_top,
        )

        self.click_outside_to_close = click_outside_to_close
        self.set_blocking(True)
        self.back_button = None

        fade_surface = pygame.Surface(MANAGER.window_resolution)

        fade_surface.fill(
            constants.CONFIG["theme"][
                f"{'dark' if game_setting_get('dark mode') else 'light'}_mode_background"
            ]
        )

        MANAGER.draw_ui(fade_surface)

        temp_surface = pygame.Surface(MANAGER.window_resolution, pygame.SRCALPHA)

        temp_surface.fill(constants.CONFIG["theme"]["fade"])

        self.fade = pygame_gui.elements.UIImage(
            pygame.Rect((0, 0), MANAGER.window_resolution),
            temp_surface,
            starting_height=self.layer,
            object_id="#fade",
        )

        pos_offset = ui_scale_value(6)
        dim_offset = ui_scale_value(12)
        scale_rect = pygame.Rect(
            (relative_rect[0] - pos_offset, relative_rect[1] - pos_offset),
            (relative_rect[2] + dim_offset, relative_rect[3] + dim_offset),
        )

        self.box = None
        if object_id != "#loading_window":
            self.box = pygame_gui.elements.UIImage(
                scale_rect,
                get_box(BoxStyles.ROUNDED_BOX, scale_rect.size),
                starting_height=self.layer,
                manager=MANAGER,
            )

        if back_button:
            scale_rect = ui_scale(pygame.Rect((0, 0), (22, 22)))
            scale_rect.topright = ui_scale_offset((-5, 7))
            self.back_button = UIImageButton(
                scale_rect,
                "",
                object_id="#exit_window_button",
                starting_height=10,
                container=self,
                anchors={"top": "top", "right": "right"},
            )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS and self.back_button:
            if event.ui_element == self.back_button:
                self.kill()

        elif (
            self.click_outside_to_close
            and event.type == pygame.MOUSEBUTTONDOWN
            and not self.are_contents_hovered()
        ):
            self.kill()

        return super().process_event(event)

    def are_contents_hovered(self) -> bool:
        any_hovered = super().are_contents_hovered()
        if not any_hovered and not self.window_element_container.hovered:
            return any_hovered
        else:
            any_hovered = True
        return any_hovered

    def kill(self):
        self.fade.kill()
        if self.box:
            self.box.kill()
        super().kill()
