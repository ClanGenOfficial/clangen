from enum import Enum
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
            "resources/images/generated_buttons/mainmenu_hovered.png"
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


def generate_button(base: pygame.Surface, dimensions: Tuple[int, int], scale=1):
    dimensions = ui_scale_dimensions(dimensions)
    height = base.height
    vertical_scale = dimensions[1] / height
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
    if dimensions[0] - width_bookends > 0:
        middle = pygame.transform.scale(
            middle, (dimensions[0] - width_bookends, middle.get_height())
        )
        surface = pygame.Surface(dimensions, pygame.SRCALPHA)
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
        excess_width = left.get_width() * 2 - dimensions[0]
        surface = pygame.Surface(dimensions, pygame.SRCALPHA)
        surface.convert_alpha()
        surface.blits(
            (
                (
                    left,
                    (0, 0),
                    pygame.Rect((0, 0), (height - excess_width / 2, height)),
                ),
                (
                    right,
                    (height - excess_width / 2, 0),
                    pygame.Rect(
                        excess_width / 2,
                        0,
                        height - excess_width / 2,
                        height,
                    ),
                ),
            )
        )

    if scale != 1:
        surface = pygame.transform.scale(
            surface, (surface.get_width() * scale, surface.get_height() * scale)
        )
    return surface


def get_button_dict(style: ButtonStyles, dimensions: Tuple[int, int]):
    return {
        "normal": generate_button(buttonstyles[style.value]["normal"], dimensions),
        "hovered": generate_button(buttonstyles[style.value]["hovered"], dimensions),
        "selected": generate_button(buttonstyles[style.value]["selected"], dimensions),
        "disabled": generate_button(buttonstyles[style.value]["disabled"], dimensions),
    }
