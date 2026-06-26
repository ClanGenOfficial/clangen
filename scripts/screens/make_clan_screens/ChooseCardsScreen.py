from collections import deque
from random import choice

import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.config import get_config
from scripts.game_structure import constants, image_cache
from scripts.game_structure.game import switch_get_value, Switch, game_setting_get
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.ui.elements.cruel_card_icon import UICruelCardIcon
from scripts.ui.elements.cruel_card_large import UICruelCardLarge
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme
from scripts.ui.windows.cruel_card_conflicts import CruelCardConflicts
from scripts.ui.windows.cruel_card_limit import CruelCardLimit


class ChooseCardsScreen(MakeClanScreenBase):
    def __init__(self, name="choose_cards_screen"):
        super().__init__(name)

        self.card_elements: dict[str, UICruelCardLarge] = {}
        self.card_chunks: deque[list[UICruelCardLarge]] = deque([])

        self.card_icon_elements: dict[str, UICruelCardIcon] = {}

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            # PREV/NEXT
            if event.ui_element == self.elements["next_step"]:
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_NAME)
            elif event.ui_element == self.elements["previous_step"]:
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_MODE)

            # CYCLE CARDS
            elif event.ui_element == self.elements["page_left"]:
                self.card_chunks.rotate(-1)
                self.update_cruel_cards()
            elif event.ui_element == self.elements["page_right"]:
                self.card_chunks.rotate()
                self.update_cruel_cards()

            # CHOOSE CARDS
            elif event.ui_element in self.card_elements.values():
                card_name = event.card_name
                self.handle_card_chosen(card_name)

            # RANDOM CARD
            elif event.ui_element == self.elements["random_card"]:
                random_card = self.random_card()
                if random_card:
                    self.handle_card_chosen(random_card)
                    self.update_card_info(random_card)

            # UNDO CHOICES
            elif event.ui_element in self.card_icon_elements.values():
                self.clan_info.cruel_cards.remove(event.card_name)
                self.reset_chosen_cards()
                self.update_cruel_cards(update_chunks=True)

        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            # UPDATE CARD INFO DISPLAY
            if event.ui_element in self.card_elements.values():
                self.update_card_info(event.card_name)
            elif event.ui_element in self.card_icon_elements.values():
                self.update_card_info(event.card_name)

        super().handle_event(event)

    def handle_card_chosen(self, card_name):
        """
        Handles checking card limits, conflicts, marking the card as chosen, and updating the displays
        """
        # limit hit
        if len(self.clan_info.cruel_cards) >= get_config("cruel_season.card_limit"):
            CruelCardLimit()
        # card conflicts
        elif self.card_has_conflicts(card_name):
            CruelCardConflicts(
                new_card=card_name, chosen_cards=self.clan_info.cruel_cards
            )
        # otherwise just add the card
        else:
            self.clan_info.cruel_cards.append(card_name)
            self.update_cruel_cards(update_chunks=True)
            self.add_chosen_card(card_name=card_name)

    def on_use(self):
        if switch_get_value(Switch.card_conflict_changes):
            card_changes = switch_get_value(Switch.card_conflict_changes)
            for c in card_changes["remove"]:
                self.clan_info.cruel_cards.remove(c)
            self.clan_info.cruel_cards.append(card_changes["add"])
            self.update_cruel_cards(update_chunks=True)
            self.reset_chosen_cards()

            switch_set_value(Switch.card_conflict_changes, {})

        super().on_use()

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
            ui_scale(pygame.Rect((65, 175), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            anchors={"top_target": self.elements["header"]},
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["card_container"] = UIContainer(
            ui_scale(pygame.Rect((12, 50), (583, 450))),
            anchors={
                "left_target": self.elements["page_left"],
            },
            manager=MANAGER,
        )
        self.elements["card_backdrop"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 120), (580, 256))),
            pygame.transform.scale(
                image_cache.load_image(
                    f"resources/images/cruel_cards/card_backdrop_{'dark' if game_setting_get('dark mode') else 'light'}.png"
                ),
                ui_scale_dimensions((580, 256)),
            ),
            container=self.elements["card_container"],
            manager=MANAGER,
            starting_height=0,
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

        # update the display with cards
        self.update_cruel_cards()

        # RANDOM CARD
        self.elements["random_card"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((88, -10), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
            anchors={
                "top_target": self.elements["card_container"],
            },
            starting_height=-1,
        )

        # CARD INFO
        self.elements["info_box"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((20, -50), (300, 150))),
            get_box(BoxStyles.FRAME, (300, 150)),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["card_container"],
                "left_target": self.elements["page_left"],
            },
            starting_height=-1,
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

        # CHOSEN CARDS
        self.elements["chosen_cards_container"] = UIContainer(
            ui_scale(pygame.Rect((30, -20), (220, 100))),
            manager=MANAGER,
            anchors={
                "top_target": self.elements["card_container"],
                "left_target": self.elements["info_box"],
            },
        )
        # this is an inner container which will actually hold the icons
        # it helps make things visually fancy and dynamically shift the card icons to be centered
        self.elements[
            "card_icon_container"
        ] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((0, 0), (0, 0))),
            manager=MANAGER,
            container=self.elements["chosen_cards_container"],
            anchors={
                "centerx": "centerx",
                "centery": "centery",
            },
            resize_top=False,
            resize_left=False,
        )

        self.reset_chosen_cards()

    def update_cruel_cards(self, update_chunks=False):
        """
        Updates the cruel card display.
        :param update_chunks: If there were changes to the chosen cards, then set this to True to update the page chunks.
        """
        for ele in self.card_elements.values():
            ele.kill()
        self.card_elements.clear()

        # chunk the card list, we don't include any cards that have already been chosen
        if update_chunks or not self.card_chunks:
            self.card_chunks = deque(
                self.chunks(
                    [
                        x
                        for x in constants.CRUEL_CARDS_ALL.keys()
                        if x not in self.clan_info.cruel_cards
                    ],
                    12,
                )
            )
        chunk = self.card_chunks[0]

        cards = {k: v for k, v in constants.CRUEL_CARDS_ALL.items() if k in chunk}

        x_pos = 0  # need to start at consistent place and then move by intervals for each card
        layer_num = 1  # need to give each card a consecutive layer to ensure they stay layered correctly
        for name, info in cards.items():
            # TODO: decide if u actually want the scatter
            y_mod = choice([2, 6, 10])  # just to introduce some random scatter
            self.card_elements[name] = UICruelCardLarge(
                (x_pos, 10 + y_mod),
                f"resources/images/cruel_cards/{info['card_art']}",
                name=name,
                card_interval=32,
                last_in_line=name == chunk[-1],
                group_layer_count=len(chunk),
                starting_height=layer_num,
                container=self.elements["card_container"],
                anchors={"top_target": self.elements["header"]},
                manager=MANAGER,
            )
            x_pos += 32  # move x_pos for next card
            layer_num += 1  # increase layer num for next card

    def update_card_info(self, card_name: str):
        """
        Takes the name of the card, retrieves its information, and displays it.
        """
        self.elements["info_default"].hide()
        self.elements["card_info_container"].show()

        self.elements["card_title"].set_text(f"cruel_season.card_names.{card_name}")
        self.elements["card_description"].set_text(
            f"cruel_season.card_descriptions.{card_name}"
        )

    def add_chosen_card(self, card_name: str):
        """
        Adds given card to the chosen card display.
        """
        self.elements["next_step"].enable()

        # aiming for 5 cards in each row
        columns = 6

        if card_name in constants.CRUEL_CARDS_DANGER:
            button = "danger"
        elif card_name in constants.CRUEL_CARDS_ORIGIN:
            button = "origin"
        elif card_name in constants.CRUEL_CARDS_BEHAVIOR:
            button = "behavior"
        else:
            button = "environment"

        if len(self.card_icon_elements) < columns:
            # anchor to left element, if there's an existing icon already
            self.card_icon_elements[card_name] = UICruelCardIcon(
                unscaled_position=(0 if not self.card_icon_elements else 5, 0),
                name=card_name,
                container=self.elements["card_icon_container"],
                tool_tip_text="screens.make_clan.cruel_card_icon_remove",
                object_id=f"#card_icon_{button}",
                anchors={"left_target": list(self.card_icon_elements.values())[-1]}
                if self.card_icon_elements
                else None,
            )

        elif len(self.card_icon_elements) >= columns:
            # anchor to one of the top cards and to left element (if one exists)
            self.card_icon_elements[card_name] = UICruelCardIcon(
                unscaled_position=(
                    0 if len(self.card_icon_elements) == columns else 5,
                    5,
                ),
                name=card_name,
                container=self.elements["card_icon_container"],
                tool_tip_text="screens.make_clan.cruel_card_icon_remove",
                object_id=f"#card_icon_{button}",
                anchors={
                    "left_target": list(self.card_icon_elements.values())[-1],
                    "top_target": list(self.card_icon_elements.values())[0],
                }
                if len(self.card_icon_elements) > columns
                else {"top_target": list(self.card_icon_elements.values())[0]},
            )

    def reset_chosen_cards(self):
        """
        Wipes all chosen card elements and recreates them.
        """
        if not self.clan_info.cruel_cards:
            self.elements["next_step"].disable()
        for ele in self.card_icon_elements.values():
            ele.kill()
        self.card_icon_elements.clear()

        for card in self.clan_info.cruel_cards:
            self.add_chosen_card(card)

    def exit_screen(self):
        for ele in self.card_elements.values():
            ele.kill()
        self.card_elements.clear()

        for ele in self.card_icon_elements.values():
            ele.kill()
        self.card_icon_elements.clear()

        self.card_chunks.clear()

        super().exit_screen()
