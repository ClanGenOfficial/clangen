from collections import deque
from random import randint, choice

import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.game_structure import constants, image_cache
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.ui.elements.card_button import UICruelCard
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme


class ChooseCardsScreen(MakeClanScreenBase):
    def __init__(self, name="choose_cards_screen"):
        super().__init__(name)

        self.card_elements: dict[str, UICruelCard] = {}
        self.card_chunks: deque[list[UICruelCard]] = deque([])

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["next_step"]:
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_NAME)

            elif event.ui_element == self.elements["page_left"]:
                self.card_chunks.rotate(-1)
                self.update_cruel_cards()
            elif event.ui_element == self.elements["page_right"]:
                self.card_chunks.rotate()
                self.update_cruel_cards()

        super().handle_event(event)

    def screen_switches(self):
        super().screen_switches()

        self.elements["header"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.cruel_card_header",
            ui_scale(pygame.Rect((0, 60), (300, -1))),
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
        )

        self.elements["page_left"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((50, 170), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            anchors={"top_target": self.elements["header"]},
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["card_container"] = UIContainer(
            ui_scale(pygame.Rect((10, 50), (590, 450))),
            anchors={
                "left_target": self.elements["page_left"],
            },
            manager=MANAGER,
        )

        self.elements["page_right"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((10, 170), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            starting_height=1,
            anchors={
                "top_target": self.elements["header"],
                "left_target": self.elements["card_container"],
            },
            manager=MANAGER,
        )

        self.elements["info_box"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((20, -50), (300, 150))),
            get_box(BoxStyles.FRAME, (300, 150)),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["card_container"],
                "left_target": self.elements["page_left"],
            },
        )

        self.card_chunks = deque(
            self.chunks(list(constants.CRUEL_CARDS_ALL.keys()), 10)
        )

        self.update_cruel_cards()

    def update_cruel_cards(self):
        for ele in self.card_elements.values():
            ele.kill()
        self.card_elements.clear()

        chunk = self.card_chunks[0]

        cards = {k: v for k, v in constants.CRUEL_CARDS_ALL.items() if k in chunk}

        x_pos = 0  # need to start at consistent place and then move by intervals for each card
        layer_num = 1  # need to give each card a consecutive layer to ensure they stay layered correctly
        for name, info in cards.items():
            # TODO: decide if u actually want the scatter
            y_mod = choice([2, 6, 10, 14])  # just to introduce some random scatter
            self.card_elements[name] = UICruelCard(
                (x_pos, 10),
                f"resources/images/cruel_cards/{info['card_art']}",
                card_interval=40,
                last_in_line=name == chunk[-1],
                group_layer_count=len(chunk),
                starting_height=layer_num,
                container=self.elements["card_container"],
                anchors={"top_target": self.elements["header"]},
                manager=MANAGER,
            )
            x_pos += 40  # move x_pos for next card
            layer_num += 1  # increase layer num for next card
