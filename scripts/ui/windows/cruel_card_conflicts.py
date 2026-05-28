import pygame
import pygame_gui

from scripts.ui.scale import ui_scale
from scripts.ui.windows.window_base_class import GameWindow


class CruelCardConflicts(GameWindow):
    def __init__(self, new_card: str, chosen_cards: list):
        super().__init__(
            ui_scale(pygame.Rect((300, 200), (250, 170))),
            window_display_title="Cruel Card Limit",
        )

        self.new_card = new_card
        self.chosen_cards = chosen_cards

        # make buttons for 'keep current cards' and 'replace with new card'

    def conflicting_cards(self):
        # set up retrieval of conflicting card names

        pass

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            # keep current cards button
            # just kills window

            # replace with new card
            # update a switch? would need to hold info on what cards are leaving and what is replacing them

            pass

        return super().process_event(event)
