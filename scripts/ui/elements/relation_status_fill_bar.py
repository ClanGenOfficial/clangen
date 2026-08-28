import pygame
import pygame_gui

from scripts.game_structure import image_cache
from scripts.ui.scale import ui_scale_value


class UIRelationStatusFillBar(pygame_gui.elements.UIStatusBar):
    """Wraps together a status bar"""

    def __init__(
        self,
        relative_rect,
        percent_full=0,
        manager=None,
        anchors=None,
        tool_tip_text: str = None,
        container=None,
    ):
        rect = (
            (relative_rect.x + ui_scale_value(2), relative_rect.y + ui_scale_value(2)),
            (
                relative_rect.width - ui_scale_value(4),
                relative_rect.height - ui_scale_value(4),
            ),
        )
        super().__init__(
            rect,
            object_id="#relation_bar",
            manager=manager,
            anchors=anchors,
            container=container,
        )
        self.percent_full = percent_full / 100

        # Now to make the overlay
        image = pygame.transform.scale(
            image_cache.load_image(
                "resources/images/relations_border_bars.png"
            ).convert_alpha(),
            (relative_rect[2], relative_rect[3]),
        )

        self.overlay = pygame_gui.elements.UIImage(
            relative_rect,
            image,
            manager=manager,
            anchors=anchors,
            object_id="#relation_bar",
            container=container,
        )
        self.overlay.set_tooltip(tool_tip_text)
        self.overlay.tool_tip_delay = 0
        self.join_focus_sets(self.overlay)

    def kill(self):
        self.overlay.kill()
        super().kill()
