import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.events_module.text_adjust import adjust_list_text
from scripts.game_structure import constants
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale
from scripts.ui.windows.window_base_class import GameWindow


class CruelCardConflicts(GameWindow):
    def __init__(self, new_card: str, chosen_cards: list):
        super().__init__(
            ui_scale(pygame.Rect((200, 240), (400, 200))),
            window_display_title="Cruel Card Limit",
        )

        self.new_card = new_card

        # get conflict values
        conflict_lists = [
            l for l in constants.CRUEL_CARDS_CONFLICTS.values() if new_card in l
        ]
        self.conflicting_cards = []
        # find the names of selected cards that conflict
        for l in conflict_lists:
            self.conflicting_cards.extend([c for c in chosen_cards if c in l])

        self.conflict_message = UITextBoxTweaked(
            i18n.t(
                "windows.cruel_cards_conflict",
                new_card=i18n.t(f"cruel_season.card_names.{new_card}"),
                conflicting_cards_list=adjust_list_text(
                    [
                        i18n.t(f"cruel_season.card_names.{c}")
                        for c in self.conflicting_cards
                    ]
                ),
                count=len(self.conflicting_cards),
            ),
            ui_scale(pygame.Rect((0, 20), (380, -1))),
            line_spacing=1,
            manager=MANAGER,
            object_id="#text_box_30_horizcenter",
            container=self,
            anchors={
                "centerx": "centerx",
            },
        )

        self.button_container = UIContainer(
            ui_scale(pygame.Rect((0, 20), (230, 200))),
            manager=MANAGER,
            anchors={
                "top_target": self.conflict_message,
                "centerx": "centerx",
            },
            container=self,
        )

        self.keep_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 0), (105, 30))),
            "buttons.keep_cards",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self.button_container,
        )
        self.replace_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((20, 0), (105, 30))),
            "buttons.replace_cards",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self.button_container,
            anchors={"left_target": self.keep_button},
        )

    def process_event(self, event) -> bool:
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.keep_button:
                self.kill()

            elif event.ui_element == self.replace_button:
                switch_set_value(
                    Switch.card_conflict_changes,
                    {"remove": self.conflicting_cards, "add": self.new_card},
                )
                self.kill()

        return super().process_event(event)
