import pygame
import pygame_gui
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIAutoResizingContainer, UIImage

from scripts.game_structure import constants, game, image_cache
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.cruel_card_icon import UICruelCardIcon
from scripts.ui.elements.cruel_card_large import UICruelCardLarge
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme
from scripts.ui.windows.window_base_class import GameWindow


class ViewCardsWindow(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((160, 95), (480, 510))),
            window_display_title="View Cruel Cards",
        )

        self.elements = {}
        self.big_card_elements = {}
        self.card_icon_elements = {}

        self.create_card_icons()

        self.elements["card_info_container"] = UIContainer(
            ui_scale(pygame.Rect((25, 30), (300, 500))),
            container=self,
            anchors={"left_target": self.elements["card_icon_container"]},
            manager=MANAGER,
        )

        self.create_card_display(game.clan.cruel_cards[0])

    def create_card_icons(self):
        COLUMNS = 3

        self.elements["card_icon_container"] = UIAutoResizingContainer(
            ui_scale(pygame.Rect((40, 50), (0, 0))),
            manager=MANAGER,
            container=self,
            resize_top=False,
            resize_left=False,
        )

        top_target = None
        left_target = None
        for i, card_name in enumerate(game.clan.cruel_cards, 1):
            if card_name in constants.CRUEL_CARDS_DANGER:
                button = "danger"
            elif card_name in constants.CRUEL_CARDS_ORIGIN:
                button = "origin"
            elif card_name in constants.CRUEL_CARDS_BEHAVIOR:
                button = "behavior"
            else:
                button = "environment"

            anchors = {}
            if top_target:
                anchors["top_target"] = top_target
            if left_target:
                anchors["left_target"] = left_target
            self.card_icon_elements[card_name] = UICruelCardIcon(
                unscaled_position=(5 if left_target else 0, 5 if top_target else 0),
                name=card_name,
                container=self.elements["card_icon_container"],
                object_id=f"#card_icon_{button}",
                anchors=anchors if self.card_icon_elements else None,
            )
            if i % COLUMNS == 0:
                left_target = None
                top_target = self.card_icon_elements[card_name]
            else:
                left_target = self.card_icon_elements[card_name]

    def create_card_display(self, name):
        art = constants.CRUEL_CARDS_ALL[name]["card_art"]

        for ele in self.big_card_elements.values():
            ele.kill()
        self.big_card_elements.clear()

        self.big_card_elements[name] = UIImage(
            ui_scale(pygame.Rect((0, 0), (230, 360))),
            pygame.transform.scale(
                image_cache.load_image(f"resources/images/cruel_cards/{art}"),
                ui_scale_dimensions((230, 360)),
            ),
            container=self.elements["card_info_container"],
            anchors={"centerx": "centerx"},
            manager=MANAGER,
        )
        self.big_card_elements["card_title"] = pygame_gui.elements.UITextBox(
            f"cruel_season.card_names.{name}",
            ui_scale(pygame.Rect((0, 0), (300, -1))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            container=self.elements["card_info_container"],
            anchors={"top_target": self.big_card_elements[name]},
        )
        self.big_card_elements["card_description"] = UITextBoxTweaked(
            f"cruel_season.card_descriptions.{name}",
            ui_scale(pygame.Rect((0, 0), (300, 70))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
            container=self.elements["card_info_container"],
            anchors={
                "top_target": self.big_card_elements["card_title"],
            },
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            # UPDATE CARD INFO DISPLAY
            if event.ui_element in self.card_icon_elements.values():
                self.create_card_display(event.card_name)

        return super().process_event(event)
