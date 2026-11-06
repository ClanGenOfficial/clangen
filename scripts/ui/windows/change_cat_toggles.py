import pygame
import pygame_gui

from scripts.game_structure import game
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.checkbox import UICheckbox
from scripts.screens.enums import GameScreen
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class CatToggleWindow(GameWindow):
    """This window allows the user to edit various cat behavior toggles"""

    cat_toggles = [
        "prevent_fading",
        "prevent_kits",
        "prevent_retirement",
        "prevent_romance",
    ]

    def __init__(self, cat):
        super().__init__(
            ui_scale(pygame.Rect((300, 215), (400, 185))),
        )
        self.the_cat = cat

        self.checkboxes = {}
        self.textbox = {}
        self.refresh_checkboxes()

        prev_element = None
        for text in self.cat_toggles:
            self.textbox[text] = pygame_gui.elements.UITextBox(
                f"windows.{text}",
                ui_scale(pygame.Rect(55, 0 if prev_element else 26, -1, 34)),
                object_id="#text_box_30_horizleft_pad_0_8",
                container=self,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            prev_element = self.textbox[text]

    def refresh_checkboxes(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

        self.checkboxes["prevent_fading"] = UICheckbox(
            (22, 25),
            container=self,
            tool_tip_text=f"windows.prevent_fading_tooltip",
            check=self.the_cat.prevent_fading,
        )
        self.checkboxes["prevent_kits"] = UICheckbox(
            (22, 0),
            container=self,
            anchors={
                "top_target": self.checkboxes["prevent_fading"],
            },
            tool_tip_text=f"windows.prevent_kits_tooltip",
            check=self.the_cat.no_kits,
        )

        self.checkboxes["prevent_retirement"] = UICheckbox(
            (22, 0),
            container=self,
            anchors={
                "top_target": self.checkboxes["prevent_kits"],
            },
            tool_tip_text=f"windows.prevent_retirement_tooltip",
            check=self.the_cat.no_retire,
        )

        self.checkboxes["prevent_romance"] = UICheckbox(
            (22, 0),
            container=self,
            anchors={
                "top_target": self.checkboxes["prevent_retirement"],
            },
            tool_tip_text=f"windows.prevent_romance_tooltip",
            check=self.the_cat.no_mates,
        )

        if self.the_cat == game.clan.instructor:
            self.checkboxes["prevent_fading"].set_tooltip(
                "windows.prevent_fading_tooltip_guide"
            )
            self.checkboxes["prevent_fading"].disable()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()
            elif event.ui_element == self.checkboxes["prevent_fading"]:
                if self.checkboxes["prevent_fading"].checked:
                    self.checkboxes["prevent_fading"].uncheck()
                    self.the_cat.prevent_fading = False
                else:
                    self.checkboxes["prevent_fading"].check()
                    self.the_cat.prevent_fading = True
            elif event.ui_element == self.checkboxes["prevent_kits"]:
                if self.checkboxes["prevent_kits"].checked:
                    self.checkboxes["prevent_kits"].uncheck()
                    self.the_cat.no_kits = False
                else:
                    self.checkboxes["prevent_kits"].check()
                    self.the_cat.no_kits = True
            elif event.ui_element == self.checkboxes["prevent_retirement"]:
                if self.checkboxes["prevent_retirement"].checked:
                    self.checkboxes["prevent_retirement"].uncheck()
                    self.the_cat.no_retire = False
                else:
                    self.checkboxes["prevent_retirement"].check()
                    self.the_cat.no_retire = True
            elif event.ui_element == self.checkboxes["prevent_romance"]:
                if self.checkboxes["prevent_romance"].checked:
                    self.checkboxes["prevent_romance"].uncheck()
                    self.the_cat.no_mates = False
                else:
                    self.checkboxes["prevent_romance"].check()
                    self.the_cat.no_mates = True

        return super().process_event(event)
