import pygame
import pygame_gui
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIImage, UITextEntryLine

from scripts.cat.cats import Cat
from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.cat.sprites.load_sprites import sprites
from scripts.events_module.text_adjust import adjust_list_text
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.scrolling_button_list import SELECTION_CHANGED
from scripts.ui.elements.scrolling_dropdown import UIScrollingDropDown
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.windows.window_base_class import GameWindow


class ComboToolWindow(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((100, 100), (600, 500))),
        )
        self.current_pose = "adult_short2"

        self.elements = {}

    def create_elements(self):
        self.elements["example_cat"] = UIImage(
            ui_scale(pygame.Rect((10, 0), (200, 200))),
            pygame.transform.scale(
                self.example_cat.sprite, ui_scale_dimensions((200, 200))
            ),
            container=self,
        )
        self.elements["chosen_patches"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((10, 0), (200, 100))),
            html_text="",
            container=self,
            anchors={"top_target": self.elements["example_cat"]},
        )
        self.elements["warning"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((10, 0), (200, -1))),
            html_text="",
            container=self,
            anchors={"top_target": self.elements["chosen_patches"]},
        )
        self.elements["preview_cat"] = UIImage(
            ui_scale(pygame.Rect((40, 20), (100, 100))),
            pygame.transform.scale(
                self.preview_cat.sprite, ui_scale_dimensions((100, 100))
            ),
            container=self,
            anchors={"left_target": self.elements["example_cat"]},
        )
        self.elements["combo_preview_cat"] = UIImage(
            ui_scale(pygame.Rect((90, 20), (100, 100))),
            pygame.transform.scale(
                self.preview_cat.sprite, ui_scale_dimensions((100, 100))
            ),
            container=self,
            anchors={"left_target": self.elements["preview_cat"]},
        )
        combos = list(self.get_combos().keys())
        combos.sort()
        self.elements["existing_combos"] = UIScrollingDropDown(
            ui_scale(pygame.Rect((50, 10), (170, 34))),
            dropdown_dimensions=ui_scale_dimensions((170, 290)),
            parent_text="existing combos",
            item_list=combos,
            manager=MANAGER,
            container=self,
            anchors={
                "top_target": self.elements["combo_preview_cat"],
                "left_target": self.elements["preview_cat"],
            },
            child_trigger_close=True,
            starting_height=3,
            multiple_choice=False,
        )
        self.elements["pose_choice"] = UIScrollingDropDown(
            ui_scale(pygame.Rect((50, 30), (170, 34))),
            dropdown_dimensions=ui_scale_dimensions((170, 250)),
            parent_text="pose choice",
            item_list=[p for p in sprites.POSE_DATA["poses"] if p],
            manager=MANAGER,
            container=self,
            anchors={
                "top_target": self.elements["existing_combos"].parent_button,
                "left_target": self.elements["preview_cat"],
            },
            child_trigger_close=True,
            starting_height=3,
            multiple_choice=False,
        )
        self.elements["clear_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((320, 310), (150, 34))),
            text="clear choices",
            image_dict=get_button_dict(ButtonStyles.SQUOVAL, (150, 34)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
        )
        self.elements["saving_container"] = UIContainer(
            ui_scale(pygame.Rect((40, 420), (500, 40))),
            container=self,
            manager=MANAGER,
        )
        self.elements["name_entry"] = UITextEntryLine(
            ui_scale(pygame.Rect((0, 0), (150, 40))),
            container=self.elements["saving_container"],
            placeholder_text="new combo name",
        )
        self.elements["save_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((20, 0), (70, 34))),
            text="save",
            image_dict=get_button_dict(ButtonStyles.SQUOVAL, (70, 34)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self.elements["saving_container"],
            anchors={"left_target": self.elements["name_entry"], "centery": "centery"},
        )
        self.elements["save_text"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((10, 0), (200, -1))),
            html_text="",
            container=self.elements["saving_container"],
            anchors={"left_target": self.elements["save_button"]},
        )

    def process_event(self, event):
        super().process_event(event)
        if event.type == SELECTION_CHANGED:
            if event.ui_element == self.elements["pose_choice"].child_button_container:
                selection = self.elements["pose_choice"].selected_list
                if not selection:
                    return
                self.current_pose = selection[0]

                self.example_cat = self.create_cat("TEST")
                self.elements["example_cat"].set_image(
                    pygame.transform.scale(
                        self.example_cat.sprite, ui_scale_dimensions((200, 200))
                    )
                )
        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            for name, button in self.elements[
                "existing_combos"
            ].child_button_dicts.items():
                if button == event.ui_element:
                    self.preview_cat = self.create_cat(name)
                    self.elements["combo_preview_cat"].set_image(
                        pygame.transform.scale(
                            self.preview_cat.sprite, ui_scale_dimensions((100, 100))
                        )
                    )
                    return
            for name, button in self.elements["pose_choice"].child_button_dicts.items():
                if button == event.ui_element:
                    self.current_pose = name
                    self.example_cat = self.create_cat("TEST")
                    self.elements["example_cat"].set_image(
                        pygame.transform.scale(
                            self.example_cat.sprite, ui_scale_dimensions((200, 200))
                        )
                    )
                    return

    def create_cat(self, patch: str) -> Cat:
        """
        Class to be overridden by subclasses
        """
        return TestCatFactory.create_cat()

    def get_combos(self) -> dict:
        """
        Class to be overridden by subclasses
        """
        return {}

    def kill(self):
        super().kill()
        # sets the game to reload!
        # this makes sure the sprites info is up to date if a dev decides to play after using this tool
        switch_set_value(Switch.switch_clan, True)

    def check_current_combos(self, selection):
        if not selection:
            self.elements["warning"].set_text(f"")
            return

        existing_combos = []
        for name, combo in self.get_combos().items():
            if set(selection) == set(combo):
                self.elements["warning"].set_text(
                    f"This combo already exists as {name}"
                )
                existing_combos.clear()
                break

            elif set(selection).issubset(set(combo)):
                existing_combos.append(name)

        if existing_combos:
            self.elements["warning"].set_text(
                f"This combo is part of {adjust_list_text(existing_combos)}"
            )

        self.elements["warning"].update_containing_rect_position()
