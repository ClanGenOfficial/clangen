from random import randint

import pygame
import pygame_gui

from scripts.game_structure import constants, image_cache
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme


class ChooseCardsScreen(MakeClanScreenBase):
    def __init__(self, name="choose_cards_screen"):
        super().__init__(name)

        self.card_elements = {}

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

        x_pos = 100
        for name, info in constants.CRUEL_CARDS_ALL.items():
            y_mod = randint(2, 10)  # just to introduce some random scatter
            art = image_cache.load_image(
                f"resources/images/cruel_cards/{info['card_art']}"
            ).convert_alpha()
            self.card_elements[name] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_pos, 25 + y_mod), (230, 360))),
                pygame.transform.scale(art, ui_scale_dimensions((230, 360))),
                object_id="#symbol_list_frame",
                starting_height=2,
                manager=MANAGER,
                anchors={"top_target": self.elements["header"]},
            )
            x_pos += 50
