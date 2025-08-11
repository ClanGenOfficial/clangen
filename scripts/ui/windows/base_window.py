import pygame
import pygame_gui
from pygame_gui.elements import UIWindow

from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import UIImageButton
from scripts.utility import ui_scale, ui_scale_offset


class GameWindow(UIWindow):
    """
    Basic window class, this sets blocking, creates an exit button, and handles the exit event
    """

    def __init__(
        self,
        relative_rect,
        window_display_title: str = None,
        object_id: str = None,
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

        self.set_blocking(True)
        self.back_button = None
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
        super().kill()