import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.game_structure import image_cache
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.scale import ui_scale, ui_scale_dimensions


class UISearchBar(UIContainer):
    def __init__(
        self,
        unscaled_position: tuple,
        visible: bool = True,
        container=None,
        anchors: dict = None,
    ):
        super().__init__(
            ui_scale(pygame.Rect(unscaled_position, (228, 32))),
            manager=MANAGER,
            visible=visible,
            container=container,
            anchors=anchors,
        )

        self.backdrop = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (228, 32))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/relationship_search.png"
                ).convert_alpha(),
                ui_scale_dimensions((228, 32)),
            ),
            container=self,
            manager=MANAGER,
        )
        self.text_entry = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((75, 8), (145, 23))),
            object_id="#search_entry_box",
            placeholder_text="general.name_search",
            container=self,
            manager=MANAGER,
        )
