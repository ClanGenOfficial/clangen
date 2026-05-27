import pygame_gui

from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase


class ChooseCardsScreen(MakeClanScreenBase):
    def __init__(self, name="choose_cards_screen"):
        super().__init__(name)

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["next_step"]:
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_NAME)

        super().handle_event(event)

    def screen_switches(self):
        super().screen_switches()
