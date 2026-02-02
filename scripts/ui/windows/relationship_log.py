import i18n
import pygame
import pygame_gui

from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import (
    UISurfaceImageButton,
)
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class RelationshipLogWindow(GameWindow):
    """This window allows the user to see the relationship log of a certain relationship."""

    def __init__(self, relationship, disable_button_list, hide_button_list):
        super().__init__(
            ui_scale(pygame.Rect((273, 122), (505, 550))),
        )
        self.set_blocking(False)
        self.hide_button_list = hide_button_list
        for button in self.hide_button_list:
            button.hide()

        self.exit_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 645), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
        )
        self.log_icon = UISurfaceImageButton(
            ui_scale(pygame.Rect((222, 404), (34, 34))),
            Icon.NOTEPAD,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )
        self.closing_buttons = [self.back_button, self.exit_button, self.log_icon]

        self.disable_button_list = []
        for button in disable_button_list:
            if button.is_enabled:
                self.disable_button_list.append(button)
                button.disable()

        opposite_log_string = None
        if not relationship.opposite_relationship:
            relationship.link_relationship()
        if (
            relationship.opposite_relationship
            and len(relationship.opposite_relationship.log) > 0
        ):
            opposite_log = relationship.opposite_relationship.log.copy()
            opposite_log.reverse()
            opposite_log_string = (
                f"{f'<br>-----------------------------<br>'.join(opposite_log)}<br>"
            )

        log = relationship.log.copy()
        log.reverse()
        log_string = (
            f"{f'<br>-----------------------------<br>'.join(log)}<br>"
            if len(relationship.log) > 0
            else i18n.t("windows.no_relation_logs")
        )

        if not opposite_log_string:
            self.log = pygame_gui.elements.UITextBox(
                log_string,
                ui_scale(pygame.Rect((15, 45), (476, 425))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )
        else:
            self.log = pygame_gui.elements.UITextBox(
                log_string,
                ui_scale(pygame.Rect((15, 45), (476, 250))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )
            self.opp_heading = pygame_gui.elements.UITextBox(
                "windows.other_perspective",
                ui_scale(pygame.Rect((15, 275), (-1, -1))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )
            self.opp_heading.disable()
            self.opp_log = pygame_gui.elements.UITextBox(
                opposite_log_string,
                ui_scale(pygame.Rect((15, 305), (476, 232))),
                object_id="#text_box_30_horizleft",
                manager=MANAGER,
                container=self,
            )

    def closing_process(self):
        """Handles to enable and kill all processes when an exit button is clicked."""
        for button in self.disable_button_list:
            button.enable()

        for button in self.hide_button_list:
            button.show()
            button.enable()
        self.log_icon.kill()
        self.exit_button.kill()
        self.back_button.kill()
        self.kill()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element in self.closing_buttons:
                self.closing_process()
        return super().process_event(event)
