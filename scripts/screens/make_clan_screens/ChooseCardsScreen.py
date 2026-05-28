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
from scripts.ui.elements.modified_scrolling_container import (
    UIModifiedScrollingContainer,
)
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
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

        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            if event.ui_element in self.card_elements.values():
                self.elements["info_default"].hide()
                self.update_card_info(event.card_name)

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

        # CARD DISPLAY
        self.elements["page_left"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((60, 175), (34, 34))),
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
            ui_scale(pygame.Rect((10, 175), (34, 34))),
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
        # chunk the card list
        self.card_chunks = deque(
            self.chunks(list(constants.CRUEL_CARDS_ALL.keys()), 10)
        )
        # update the display with cards
        self.update_cruel_cards()

        # CARD INFO
        self.elements["info_box"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((20, -50), (300, 150))),
            get_box(BoxStyles.FRAME, (300, 150)),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["card_container"],
                "left_target": self.elements["page_left"],
            },
        )
        # "hover to see effects" message
        self.elements["info_default"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.cruel_card_info_placeholder",
            ui_scale(pygame.Rect((30, -20), (280, 110))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["card_container"],
                "left_target": self.elements["page_left"],
            },
        )
        # hidden to begin with, but these will be the card info text
        self.elements["card_info_container"] = UIContainer(
            ui_scale(pygame.Rect((30, -20), (280, 110))),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["card_container"],
                "left_target": self.elements["page_left"],
            },
            visible=False,
        )
        self.elements["card_title"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, 0), (280, -1))),
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            container=self.elements["card_info_container"],
        )
        self.elements["card_description"] = UITextBoxTweaked(
            "",
            ui_scale(pygame.Rect((0, 0), (280, 80))),
            object_id=get_text_box_theme("#text_box_22_horizleft_spacing_95"),
            manager=MANAGER,
            container=self.elements["card_info_container"],
            anchors={"top_target": self.elements["card_title"]},
        )

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
            y_mod = choice([2, 6, 10])  # just to introduce some random scatter
            self.card_elements[name] = UICruelCard(
                (x_pos, 10 + y_mod),
                f"resources/images/cruel_cards/{info['card_art']}",
                name=name,
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

    def update_card_info(self, card_name: str):
        """
        Takes the name of the card, retrieves its information, and displays it.
        """
        self.elements["card_info_container"].show()

        self.elements["card_title"].set_text(f"cruel_season.card_names.{card_name}")
        self.elements["card_description"].set_text(
            f"cruel_season.card_descriptions.{card_name}"
        )
