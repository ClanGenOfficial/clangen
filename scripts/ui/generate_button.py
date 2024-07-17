from enum import Enum
from math import floor
from typing import Tuple

import pygame

from scripts.utility import ui_scale_dimensions


class ButtonStyles(Enum):
    MAINMENU = "mainmenu"
    SQUOVAL = "squoval"
    MENU_LEFT = "menu_left"
    MENU_MIDDLE = "menu_middle"
    MENU_RIGHT = "menu_right"
    ROUNDED_RECT = "rounded_rect"
    DROPDOWN = "dropdown"
    HORIZONTAL_TAB = "horizontal_tab"
    VERTICAL_TAB = "vertical_tab"


buttonstyles = {
    "mainmenu": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/mainmenu_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/mainmenu_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/mainmenu_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/mainmenu_disabled.png"
        ).convert_alpha(),
    },
    "squoval": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/general_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/general_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/general_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/general_disabled.png"
        ).convert_alpha(),
    },
    "menu_left": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/menu_left_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/menu_left_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/menu_left_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/menu_left_disabled.png"
        ).convert_alpha(),
    },
    "menu_middle": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/menu_middle_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/menu_middle_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/menu_middle_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/menu_middle_disabled.png"
        ).convert_alpha(),
    },
    "rounded_rect": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/rounded_rect_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/rounded_rect_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/rounded_rect_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/rounded_rect_disabled.png"
        ).convert_alpha(),
    },
    "dropdown": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/dropdown_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/dropdown_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/dropdown_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/dropdown_disabled.png"
        ).convert_alpha(),
    },
    "horizontal_tab": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/horizontal_tab_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/horizontal_tab_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/horizontal_tab_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/horizontal_tab_disabled.png"
        ).convert_alpha(),
    },
    "vertical_tab": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/vertical_tab_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/vertical_tab_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/vertical_tab_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/vertical_tab_disabled.png"
        ).convert_alpha(),
    },
}

buttonstyles["menu_right"] = {
    "normal": pygame.transform.flip(buttonstyles["menu_left"]["normal"], True, False),
    "hovered": pygame.transform.flip(buttonstyles["menu_left"]["hovered"], True, False),
    "selected": pygame.transform.flip(
        buttonstyles["menu_left"]["selected"], True, False
    ),
    "disabled": pygame.transform.flip(
        buttonstyles["menu_left"]["disabled"], True, False
    ),
}


def generate_button(base: pygame.Surface, scaled_dimensions: Tuple[int, int]):
    """
    Generate a surface of arbitrary length from a given input surface
    :param base: the Surface to generate from
    :param scaled_dimensions: the SCALED dimensions of the final button
    :return: A surface of the correct dimensions, scaled automatically
    """
    height = base.height
    vertical_scale = scaled_dimensions[1] / height
    if vertical_scale < 0:
        vertical_scale = 1 / -vertical_scale

    left = base.subsurface((0, 0), (height, height))
    middle = base.subsurface((height, 0), (height, height))
    right = base.subsurface((height * 2, 0), (height, height))
    if vertical_scale == 0:
        pass
    else:
        left = pygame.transform.scale_by(left, vertical_scale)
        middle = pygame.transform.scale_by(middle, vertical_scale)
        right = pygame.transform.scale_by(right, vertical_scale)
        height = middle.get_height()
    width_bookends = height * 2

    # if we need the middle segment
    if scaled_dimensions[0] - width_bookends > 0:
        middle = pygame.transform.scale(
            middle, (scaled_dimensions[0] - width_bookends, middle.get_height())
        )
        surface = pygame.Surface(scaled_dimensions, pygame.SRCALPHA)
        surface.convert_alpha()
        surface.fblits(
            (
                (left, (0, 0)),
                (middle, (left.get_width(), 0)),
                (right, (left.get_width() + middle.get_width(), 0)),
            )
        )
    else:
        # if it's too small for us to put middle in there, just don't :)
        excess_width = left.get_width() * 2 - scaled_dimensions[0]
        surface = pygame.Surface(scaled_dimensions, pygame.SRCALPHA)
        surface.convert_alpha()
        excess = height - excess_width / 2
        if excess % 1 != 0:
            left_excess = floor(excess) + 1
            right_excess = floor(excess)
        else:
            left_excess = excess
            right_excess = excess
        surface.blits(
            (
                (
                    left,
                    (0, 0),
                    pygame.Rect((0, 0), (left_excess, height)),
                ),
                (
                    right,
                    (left_excess, 0),
                    pygame.Rect(
                        excess_width // 2,
                        0,
                        right_excess,
                        height,
                    ),
                ),
            )
        )

    return surface


def get_button_dict(style: ButtonStyles, unscaled_dimensions: Tuple[int, int]):
    """
    Return a dictionary of surfaces suitable for passing into a UISurfaceImageButton.
    :param style: The ButtonStyles style required for the button
    :param unscaled_dimensions: The UNSCALED dimensions of the button
    :return: A dictionary of surfaces
    """
    scaled_dimensions = ui_scale_dimensions(unscaled_dimensions)
    return {
        "normal": generate_button(
            buttonstyles[style.value]["normal"], scaled_dimensions
        ),
        "hovered": generate_button(
            buttonstyles[style.value]["hovered"], scaled_dimensions
        ),
        "selected": generate_button(
            buttonstyles[style.value]["selected"], scaled_dimensions
        ),
        "disabled": generate_button(
            buttonstyles[style.value]["disabled"], scaled_dimensions
        ),
    }
