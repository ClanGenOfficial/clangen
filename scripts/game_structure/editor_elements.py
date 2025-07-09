from typing import Tuple

import pygame
import pygame_gui

from scripts.game_structure.ui_elements import UITextBoxTweaked
from scripts.utility import get_text_box_theme, ui_scale


class EditorElement:
    def __init__(self):
        self.ui_elements = []

    def kill(self):
        for ele in self.ui_elements:
            ele.kill()

    def hide(self):
        for ele in self.ui_elements:
            ele.hide()

    def show(self):
        for ele in self.ui_elements:
            ele.show()


class EditorTextEntryLine(EditorElement):
    def __init__(
        self,
        position: Tuple[int, int],
        anchors: dict = None,
        container=None,
        description: str = None,
        entry_length: int = None,
        initial_entry_text: str = "",
        manager=None,
    ):
        """
        Creates descriptive text and an associated entry line.
        :param position: The element's position
        :param anchors: The element's anchors
        :param container: The element's container
        :param description: The descriptive text to precede the entry line
        :param entry_length: The entry line length
        :param initial_entry_text: The initial entry text
        :param manager: The element's manager
        """
        super().__init__()

        self.description = UITextBoxTweaked(
            description,
            ui_scale(pygame.Rect(position, (-1, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=manager,
            container=container,
            anchors=anchors,
        )
        self.ui_elements.append(self.description)

        self.initial_entry_text = initial_entry_text
        self.entry = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((0, 13), (entry_length, 29))),
            manager=manager,
            container=container,
            anchors={"left_target": self.description},
            initial_text=self.initial_entry_text,
        )
        self.ui_elements.append(self.entry)

        self.bottom_element = self.description

    @property
    def changed(self) -> bool:
        """
        Returns true if the entry text has changed since last checked.
        """
        if self.entry.text != self.initial_entry_text:
            # save new text state to compare when next changed
            self.initial_entry_text = self.entry.text
            return True
        return False

    @property
    def info(self) -> str:
        """
        Returns the currently entered text
        """
        return self.entry.text


class EditorDropDownSelection(EditorElement):

    def __init__(
        self,
        position: Tuple[int, int],
        anchors: dict = None,
        container=None,
        description: str = None,
        item_list: list = None,
        initial_selection: list = None,
        dropdown_parent_text: str = None,
        multiple_choice: bool = False,
        disable_selection: bool = False,
        child_trigger_close: bool = False,
        display_text: str = None,
        manager=None,
    ):
        super().__init__()

        self.description = UITextBoxTweaked(
            description,
            ui_scale(pygame.Rect(position, (250, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            line_spacing=1,
            manager=manager,
            container=container,
            anchors=anchors,
        )
        self.ui_elements.append(self.description)

        dropdown_anchors = {"left_target": self.description}
        if anchors.get("top_target"):
            dropdown_anchors["top_target"] = anchors["top_target"]
        self.selection = initial_selection
        self.dropdown = UIScrollingDropDown(
            pygame.Rect((10, 20), (150, 30)),
            dropdown_dimensions=(150, 200),
            parent_text=dropdown_parent_text,
            item_list=item_list,
            container=container,
            manager=manager,
            multiple_choice=multiple_choice,
            disable_selection=disable_selection,
            child_trigger_close=child_trigger_close,
            starting_selection=self.selection,
            starting_height=5,
            anchors=anchors,
        )
        self.ui_elements.append(self.dropdown)

        self.display_text = display_text
        self.display = UITextBoxTweaked(
            f"{self.display_text} {initial_selection}",
            ui_scale(pygame.Rect((10, 10), (380, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_10_10"),
            manager=manager,
            container=container,
            anchors={
                "top_target": self.description,
            },
            allow_split_dashes=False,
        )
        self.ui_elements.append(self.display)

    @property
    def changed(self):
        if self.selection != self.dropdown.selected_list:
            self.selection = self.dropdown.selected_list.copy()
            return True
        return False

    @property
    def info(self):
        return self.dropdown.selected_list.copy()

    @property
    def displayed_info(self):
        return self.display.html_text

    @displayed_info.setter
    def displayed_info(self, new_text):
        self.display.set_text(f"{self.display_text} {new_text}")

