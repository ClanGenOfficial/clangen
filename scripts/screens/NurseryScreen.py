import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.screens.Screens import Screens
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from scripts.utility import scale, get_text_box_theme

class NurseryScreen(Screens):
    """
    Screen for the Nursery, in which play-sessions can be held for kittens, functioning similarly to patrols.
    """

    def __init__(self, name=None):
        self.name = name
        self.chosen_kits = []
        self.partaking_adult = None

    def screen_switches(self):
        """Runs when this screen is switched to."""

        self.hide_menu_buttons()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)

    def handle_event(self, event):
        """This is where events that occur on this page are handled.
        For the pygame_gui rewrite, button presses are also handled here. """

        if game.switches['window_open']:
            pass
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)

    def exit_screen(self):
        """Runs when screen exits"""
        pass
