import pygame
import pygame_gui

from scripts.game_structure import game
from scripts.game_structure.ui_elements import (
    UIImageButton,
)
from scripts.screens.enums import GameScreen
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class CatToggleWindow(GameWindow):
    """This window allows the user to edit various cat behavior toggles"""

    def __init__(self, cat):
        super().__init__(
            ui_scale(pygame.Rect((300, 215), (400, 185))),
        )
        self.the_cat = cat

        self.checkboxes = {}
        self.refresh_checkboxes()

        # Text
        self.text_1 = pygame_gui.elements.UITextBox(
            "windows.prevent_fading",
            ui_scale(pygame.Rect(55, 25, -1, 32)),
            object_id="#text_box_30_horizleft_pad_0_8",
            container=self,
        )

        self.text_2 = pygame_gui.elements.UITextBox(
            "windows.prevent_kits",
            ui_scale(pygame.Rect(55, 50, -1, 32)),
            object_id="#text_box_30_horizleft_pad_0_8",
            container=self,
        )

        self.text_3 = pygame_gui.elements.UITextBox(
            "windows.prevent_retirement",
            ui_scale(pygame.Rect(55, 75, -1, 32)),
            object_id="#text_box_30_horizleft_pad_0_8",
            container=self,
        )

        self.text_4 = pygame_gui.elements.UITextBox(
            "windows.prevent_romance",
            ui_scale(pygame.Rect(55, 100, -1, 32)),
            object_id="#text_box_30_horizleft_pad_0_8",
            container=self,
        )

    def refresh_checkboxes(self):
        for x in self.checkboxes.values():
            x.kill()
        self.checkboxes = {}

        # Prevent Fading
        if self.the_cat == game.clan.instructor:
            box_type = "@checked_checkbox"
            tool_tip = "windows.prevent_fading_tooltip_guide"
        elif self.the_cat.prevent_fading:
            box_type = "@checked_checkbox"
            tool_tip = "windows.prevent_fading_tooltip"
        else:
            box_type = "@unchecked_checkbox"
            tool_tip = "windows.prevent_fading_tooltip"

        # Fading
        self.checkboxes["prevent_fading"] = UIImageButton(
            ui_scale(pygame.Rect((22, 25), (34, 34))),
            "",
            container=self,
            object_id=box_type,
            tool_tip_text=tool_tip,
        )

        if self.the_cat == game.clan.instructor:
            self.checkboxes["prevent_fading"].disable()

        # No Kits
        self.checkboxes["prevent_kits"] = UIImageButton(
            ui_scale(pygame.Rect((22, 50), (34, 34))),
            "",
            container=self,
            object_id=(
                "@checked_checkbox" if self.the_cat.no_kits else "@unchecked_checkbox"
            ),
            tool_tip_text="windows.prevent_kits_tooltip",
        )

        # No Retire
        self.checkboxes["prevent_retire"] = UIImageButton(
            ui_scale(pygame.Rect((22, 75), (34, 34))),
            "",
            container=self,
            object_id=(
                "@checked_checkbox" if self.the_cat.no_retire else "@unchecked_checkbox"
            ),
            tool_tip_text=(
                "windows.prevent_retirement_tooltip_yes"
                if self.the_cat.no_retire
                else "windows.prevent_retirement_tooltip_no"
            ),
        )

        # No mates
        self.checkboxes["prevent_mates"] = UIImageButton(
            ui_scale(pygame.Rect((22, 100), (34, 34))),
            "",
            container=self,
            object_id=(
                "@checked_checkbox" if self.the_cat.no_mates else "@unchecked_checkbox"
            ),
            tool_tip_text="windows.prevent_romance_tooltip",
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()
            elif event.ui_element == self.checkboxes["prevent_fading"]:
                self.the_cat.prevent_fading = not self.the_cat.prevent_fading
                self.refresh_checkboxes()
            elif event.ui_element == self.checkboxes["prevent_kits"]:
                self.the_cat.no_kits = not self.the_cat.no_kits
                self.refresh_checkboxes()
            elif event.ui_element == self.checkboxes["prevent_retire"]:
                self.the_cat.no_retire = not self.the_cat.no_retire
                self.refresh_checkboxes()
            elif event.ui_element == self.checkboxes["prevent_mates"]:
                self.the_cat.no_mates = not self.the_cat.no_mates
                self.refresh_checkboxes()

        return super().process_event(event)
