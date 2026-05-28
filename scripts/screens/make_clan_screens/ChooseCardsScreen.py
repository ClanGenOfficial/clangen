from random import randint, choice

import pygame
import pygame_gui

from scripts.game_structure import constants, image_cache
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.ui.elements.card_button import UICruelCard
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme


class ChooseCardsScreen(MakeClanScreenBase):
    def __init__(self, name="choose_cards_screen"):
        super().__init__(name)

        self.card_elements: dict[str, UICruelCard] = {}
        self.card_page: int = 1
        self.card_chunks: list[list[UICruelCard]] = []

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["next_step"]:
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_NAME)

        super().handle_event(event)

    def screen_switches(self):
        super().screen_switches()

        self.elements["header"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.cruel_card_header",
            ui_scale(pygame.Rect((0, 75), (300, -1))),
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.card_chunks = self.chunks(list(constants.CRUEL_CARDS_ALL.keys()), 10)

        self.update_cruel_cards()

    def update_cruel_cards(self):
        # page starts at 1 but chunk index starts at 0, so we subtract 1 from page to get index
        chunk = self.card_chunks[self.card_page - 1]

        cards = {k: v for k, v in constants.CRUEL_CARDS_ALL.items() if k in chunk}

        x_pos = 100  # need to start at consistent place and then move by intervals for each card
        layer_num = 1  # need to give each card a consecutive layer to ensure they stay layered correctly
        for name, info in cards.items():
            y_mod = choice([2, 6, 10, 14])  # just to introduce some random scatter
            self.card_elements[name] = UICruelCard(
                (x_pos, 10 + y_mod),
                f"resources/images/cruel_cards/{info['card_art']}",
                last_in_line=name == chunk[-1],
                group_layer_count=len(chunk),
                starting_height=layer_num,
                manager=MANAGER,
                anchors={"top_target": self.elements["header"]},
            )
            x_pos += 40  # move x_pos for next card
            layer_num += 1  # increase layer num for next card
