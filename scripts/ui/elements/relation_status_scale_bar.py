import math

import pygame
import pygame_gui

from scripts.cat_relations.enums import RelTier
from scripts.game_structure import image_cache
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.scale import ui_scale_value, ui_scale_dimensions


class UIRelationStatusScaleBar(pygame_gui.elements.UIImage):
    """Wraps together a status bar"""

    def __init__(
        self,
        relative_rect,
        tier: RelTier,
        container=None,
        manager=None,
        anchors: dict = None,
        starting_height: int = 1,
        scale_position: int = 0,
        tool_tip_text: str = None,
    ):
        # creating the colored bar
        path = "resources/images/relation_bar.png"

        bar = pygame.transform.scale(
            image_cache.load_image(path),
            (relative_rect[2], relative_rect[3]),
        )

        bar_center_offset = int(bar.width / 2)
        num_sub_bars = math.ceil((abs(scale_position)) / 25)
        sub_bar_width = bar.width // 8
        bar_width = sub_bar_width * num_sub_bars

        if scale_position < 0:
            short_bar = pygame.Rect(
                bar_center_offset - bar_width, 0, bar_width, bar.height
            )
        else:
            short_bar = pygame.Rect(bar_center_offset, 0, bar_width, bar.height)

        surf = pygame.Surface((short_bar.width, short_bar.height))

        bar.fill((130, 117, 82))

        bar_colour = (130, 117, 82)
        if tier.is_low_pos:
            bar_colour = (182, 174, 51)
        elif tier.is_mid_pos:
            bar_colour = (150, 195, 49)
        elif tier.is_extreme_pos:
            bar_colour = (154, 241, 32)
        elif tier.is_low_neg:
            bar_colour = (186, 128, 60)
        elif tier.is_mid_neg:
            bar_colour = (214, 90, 53)
        elif tier.is_extreme_neg:
            bar_colour = (233, 38, 30)

        surf.fill(bar_colour)
        bar.blit(surf, (short_bar.left, short_bar.top))

        # bar element is the base of this entire element
        super().__init__(
            relative_rect,
            bar,
            container=container,
            manager=manager,
            starting_height=starting_height,
            anchors=anchors,
        )

        # Now to make the overlay
        image = pygame.transform.scale(
            image_cache.load_image(
                "resources/images/relations_border_bars.png"
            ).convert_alpha(),
            (relative_rect[2], relative_rect[3]),
        )

        # overlay element
        self.overlay = UIModifiedImage(
            relative_rect,
            image,
            manager=manager,
            container=container,
            anchors=anchors,
            starting_height=starting_height,
            object_id="#relation_bar",
        )
        self.join_focus_sets(self.overlay)
        self.overlay.set_tooltip(tool_tip_text)
        self.overlay.tool_tip_delay = 0

        # pointer element
        # -7 bc coords are top-left so we have to shift over so arrow points at middle
        pointer_origin = (bar.width // 2 - ui_scale_value(7), 0)
        # every "unit" is 1/200th of the width of the bar
        pointer_offset = int(scale_position / 200 * bar.width)
        # -15 so it doesn't go past the end of the bar
        pointer_x = max(
            0, min(pointer_offset + pointer_origin[0], bar.width - ui_scale_value(15))
        )

        pointer_final_position = (
            pointer_x,
            pointer_origin[1],
        )
        pointer_size = ui_scale_dimensions((14, 12))

        pointer = pygame.transform.scale(
            image_cache.load_image("resources/images/rel_pointer.png").convert_alpha(),
            pointer_size,
        )
        self.pointer = pygame_gui.elements.UIImage(
            pygame.Rect(pointer_final_position, pointer_size),
            pointer,
            manager=manager,
            container=container,
            anchors=anchors,
            starting_height=starting_height,
        )
        self.join_focus_sets(self.pointer)

    def kill(self):
        self.overlay.kill()
        self.pointer.kill()
        super().kill()
