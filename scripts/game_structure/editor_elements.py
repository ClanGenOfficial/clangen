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

