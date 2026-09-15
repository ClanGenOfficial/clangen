import i18n
import pygame
import pygame_gui

from scripts.config import get_config
from scripts.game_structure import constants, game, image_cache
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.windows.window_base_class import GameWindow


class ViewCardsWindow(GameWindow):
    def __init__(self, current_cards):
        super().__init__(
            ui_scale(pygame.Rect((180, 190), (440, 330))),
            window_display_title="View Cruel Cards",
        )
        self.current_cards = current_cards
        self.elements = {}

        self.elements["text"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((0, 20), (380, -1))),
            html_text="Input a list of desired cards. Card names should be separated by a comma.",
            container=self,
            manager=MANAGER,
            object_id="#text_box_30_horizcenter",
            anchors={"centerx": "centerx"},
        )

        self.elements["input"] = pygame_gui.elements.UITextEntryBox(
            relative_rect=ui_scale(pygame.Rect((0, 10), (350, 150))),
            container=self,
            manager=MANAGER,
            anchors={"centerx": "centerx", "top_target": self.elements["text"]},
            object_id="text_entry_line",
            placeholder_text="Card1, Card2, Card3...",
        )

        self.elements["warning"] = UITextBoxTweaked(
            relative_rect=ui_scale(pygame.Rect((0, -5), (380, -1))),
            html_text="error",
            container=self,
            manager=MANAGER,
            object_id="#text_box_30_horizcenter",
            anchors={"centerx": "centerx", "top_target": self.elements["input"]},
            visible=False,
        )

        self.elements["confirm"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 50), (100, 30))),
            "buttons.confirm",
            get_button_dict(ButtonStyles.SQUOVAL, (100, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx", "top_target": self.elements["input"]},
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["confirm"]:
                card_list = self.clean_input_text()

                failed, final_card_list = self.attempt_card_input(card_list)

                if not failed:
                    switch_set_value(Switch.confirmed_deck_list, final_card_list)
                    self.kill()

        return super().process_event(event)

    def attempt_card_input(self, card_list):
        failed = False

        # get internal names
        internal_card_names = list(constants.CRUEL_CARDS_ALL.keys())
        # get display names (we want to let players use these too)
        display_card_name_mapping = {}
        for c in internal_card_names:
            display_card_name_mapping[
                i18n.t(f"cruel_season.card_names.{c}").casefold()
            ] = c

        # now check the validity of the given cards
        final_card_list = []
        for card in card_list:
            if card in final_card_list:
                continue

            # CHECK CONFLICTS
            for conflict_list in constants.CRUEL_CARDS_CONFLICTS.values():
                if card in conflict_list and set(
                    final_card_list + self.current_cards
                ).intersection(set(conflict_list)):
                    self.elements["warning"].set_text("windows.deck_list_conflict")
                    self.elements["warning"].show()
                    failed = True

            if card in internal_card_names:
                final_card_list.append(card)
            elif card in display_card_name_mapping:
                internal = display_card_name_mapping[card]
                if internal in card_list:
                    continue
                final_card_list.append(internal)

        # CHECK DECK LIMIT
        if not failed and (len(final_card_list) + len(self.current_cards)) >= (
            get_config("cruel_season.card_limit")
        ):
            self.elements["warning"].set_text(
                "windows.deck_list_limit",
                text_kwargs={"amount": get_config("cruel_season.card_limit")},
            )
            self.elements["warning"].show()
            failed = True

        return failed, final_card_list

    def clean_input_text(self):
        # retrieve text input
        card_text = self.elements["input"].get_text()
        # split along commas
        card_list = card_text.split(",")
        # strip any whitespace from front and back
        card_list = [c.strip().casefold() for c in card_list]
        return card_list
