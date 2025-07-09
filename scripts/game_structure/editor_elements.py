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
            ui_scale(pygame.Rect((0, 13), (230, 29))),
            manager=manager,
            container=container,
            anchors={"left_target": self.description},
            initial_text=self.initial_entry_text,
        )
        self.ui_elements.append(self.entry)

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
