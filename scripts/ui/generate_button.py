from enum import Enum
from functools import lru_cache
from math import floor
from typing import Tuple, Dict

import pygame

import scripts.game_structure.screen_settings
from scripts.ui.generate_box import BoxData, get_box
from scripts.utility import ui_scale_dimensions


class ButtonStyles(Enum):
    MAINMENU = "mainmenu"
    SQUOVAL = "squoval"
    MENU_LEFT = "menu_left"
    MENU_MIDDLE = "menu_middle"
    MENU_RIGHT = "menu_right"
    FILTER_DROPDOWN = "filter_dropdown"
    PROFILE_LEFT = "profile_left"
    PROFILE_MIDDLE = "profile_middle"
    PROFILE_RIGHT = "profile_right"
    ROUNDED_RECT = "rounded_rect"
    DROPDOWN = "dropdown"
    HORIZONTAL_TAB = "horizontal_tab"
    HORIZONTAL_TAB_MIRRORED = "horizontal_tab_mirrored"
    VERTICAL_TAB = "vertical_tab"
    LADDER_TOP = "ladder_top"
    LADDER_MIDDLE = "ladder_middle"
    LADDER_BOTTOM = "ladder_bottom"
    ICON = "icon"
    ICON_TAB_TOP = "icon_tab_top"
    ICON_TAB_LEFT = "icon_tab_left"
    ICON_TAB_BOTTOM = "icon_tab_bottom"
    ICON_TAB_RIGHT = "icon_tab_right"


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
        "ninetile": False,
        "scale_only": False,
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
        "ninetile": False,
        "scale_only": False,
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
        "ninetile": False,
        "scale_only": False,
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
        "ninetile": False,
        "scale_only": False,
    },
    "menu_right": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/menu_right_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/menu_right_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/menu_right_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/menu_right_disabled.png"
        ).convert_alpha(),
        "ninetile": False,
        "scale_only": False,
    },
    "profile_left": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/profile_left_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/profile_left_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/profile_left_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/profile_left_disabled.png"
        ).convert_alpha(),
        "ninetile": False,
        "scale_only": False,
    },
    "profile_middle": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/profile_middle_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/profile_middle_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/profile_middle_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/profile_middle_disabled.png"
        ).convert_alpha(),
        "ninetile": False,
        "scale_only": False,
    },
    "profile_right": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/profile_right_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/profile_right_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/profile_right_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/profile_right_disabled.png"
        ).convert_alpha(),
        "ninetile": False,
        "scale_only": False,
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
        "ninetile": False,
        "scale_only": False,
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
        "ninetile": True,
        "scale_only": False,
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
        "ninetile": False,
        "scale_only": False,
        "tab_movement": {"hovered": False, "disabled": True, "amount": (0, -4)},
    },
    "horizontal_tab_mirrored": {
        "normal": pygame.transform.flip(
            pygame.image.load(
                "resources/images/generated_buttons/horizontal_tab_normal.png"
            ).convert_alpha(),
            False,
            True,
        ),
        "hovered": pygame.transform.flip(
            pygame.image.load(
                "resources/images/generated_buttons/horizontal_tab_hovered.png"
            ).convert_alpha(),
            False,
            True,
        ),
        "selected": pygame.transform.flip(
            pygame.image.load(
                "resources/images/generated_buttons/horizontal_tab_normal.png"
            ).convert_alpha(),
            False,
            True,
        ),
        "disabled": pygame.transform.flip(
            pygame.image.load(
                "resources/images/generated_buttons/horizontal_tab_disabled.png"
            ).convert_alpha(),
            False,
            True,
        ),
        "ninetile": False,
        "scale_only": False,
        "tab_movement": {"hovered": False, "disabled": True, "amount": (0, 4)},
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
        "ninetile": False,
        "scale_only": False,
        "tab_movement": {"hovered": True, "disabled": False, "amount": (10, 0)},
    },
    "ladder_top": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/ladder_top_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/ladder_top_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/ladder_top_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/ladder_top_disabled.png"
        ).convert_alpha(),
        "ninetile": True,
        "scale_only": False,
    },
    "ladder_middle": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/ladder_middle_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/ladder_middle_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/ladder_middle_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/ladder_middle_disabled.png"
        ).convert_alpha(),
        "ninetile": True,
        "scale_only": False,
    },
    "ladder_bottom": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/ladder_bottom_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/ladder_bottom_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/ladder_bottom_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/ladder_bottom_disabled.png"
        ).convert_alpha(),
        "ninetile": True,
        "scale_only": False,
    },
    "icon": {
        "normal": pygame.image.load(
            "resources/images/generated_buttons/icon_normal.png"
        ).convert_alpha(),
        "hovered": pygame.image.load(
            "resources/images/generated_buttons/icon_hovered.png"
        ).convert_alpha(),
        "selected": pygame.image.load(
            "resources/images/generated_buttons/icon_normal.png"
        ).convert_alpha(),
        "disabled": pygame.image.load(
            "resources/images/generated_buttons/icon_disabled.png"
        ).convert_alpha(),
        "ninetile": False,
        "scale_only": True,
    },
    "icon_tab_top": {
        "ninetile": True,
        "scale_only": False,
        "tab_movement": {"hovered": True, "disabled": True, "amount": (0, 4)},
    },
    "icon_tab_left": {
        "ninetile": True,
        "scale_only": False,
        "tab_movement": {"hovered": True, "disabled": True, "amount": (-4, 0)},
    },
    "icon_tab_bottom": {
        "ninetile": True,
        "scale_only": False,
        "tab_movement": {"hovered": True, "disabled": True, "amount": (0, -4)},
    },
    "icon_tab_right": {
        "ninetile": True,
        "scale_only": False,
        "tab_movement": {"hovered": True, "disabled": True, "amount": (4, 0)},
    },
}


def __separate_icon_tabs() -> Tuple[str, str, Dict[str, Dict[str, pygame.Surface]]]:
    """
    A separate helper method to build the icon tabs since I shoved them all in one file. It just made sense, ok?
    :return: a generator for the tab, status and associated surface
    """
    source = pygame.image.load(
        "resources/images/generated_buttons/icon_tab.png"
    ).convert_alpha()
    tab_size = source.get_width() // 3
    for y, fun_tab in enumerate(
        ["icon_tab_top", "icon_tab_left", "icon_tab_bottom", "icon_tab_right"], start=0
    ):
        for x, fun_status in enumerate(["normal", "hovered", "disabled"], start=0):
            yield fun_tab, fun_status, source.subsurface(
                (x * tab_size, y * tab_size, tab_size, tab_size)
            )


for tab, status, butt_surface in __separate_icon_tabs():
    if "normal" in buttonstyles[tab] and "selected" not in buttonstyles[tab]:
        buttonstyles[tab]["selected"] = buttonstyles[tab]["normal"]
    buttonstyles[tab][status] = butt_surface


def generate_button(base: pygame.Surface, scaled_dimensions: Tuple[int, int]):
    """
    Generate a surface of arbitrary length from a given input surface
    :param base: the Surface to generate from
    :param scaled_dimensions: the SCALED dimensions of the final button
    :return: A surface of the correct dimensions, scaled automatically
    """
    height = base.get_height()
    vertical_scale = scaled_dimensions[1] / height
    if vertical_scale < 0:
        vertical_scale = 1 / -vertical_scale

    left = base.subsurface((0, 0), (height, height))
    middle = base.subsurface((height, 0), (height, height))
    right = base.subsurface((height * 2, 0), (height, height))
    if vertical_scale == 0:
        pass
    else:
        scale = (scaled_dimensions[1], scaled_dimensions[1])
        left = pygame.transform.scale(left, scale)
        middle = pygame.transform.scale(middle, scale)
        right = pygame.transform.scale(right, scale)
        height = middle.get_height()
    del vertical_scale
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
                (right, (scaled_dimensions[0] - height, 0)),
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


def get_button_dict(
    style: ButtonStyles, unscaled_dimensions: Tuple[int, int], *, static=False
) -> Dict[str, pygame.Surface]:
    """
    Return a dictionary of surfaces suitable for passing into a UISurfaceImageButton.
    :param style: The ButtonStyles style required for the button
    :param unscaled_dimensions: The UNSCALED dimensions of the button
    :param static: Whether to return only the normal surface, default False
    :return: A dictionary of surfaces
    """
    return _get_button_dict(
        style,
        unscaled_dimensions,
        scripts.game_structure.screen_settings.screen_scale,
        static,
    )


@lru_cache(maxsize=None)
def _get_button_dict(
    style: ButtonStyles, unscaled_dimensions: Tuple[int, int], scale, static
) -> Dict[str, pygame.Surface]:
    """
    This wrapper exists so that we can cache the values to make toggling quicker.
    :param style: The ButtonStyles style required for the button
    :param unscaled_dimensions: The UNSCALED dimensions of the button
    :return: A dictionary of surfaces
    """

    # scale exists pretty much only to ensure we have a different cached version of the function for different scales
    dontdeletethatpls = scale

    if buttonstyles[style.value]["scale_only"]:
        if static:
            return {
                "normal": pygame.transform.scale(
                    buttonstyles[style.value]["normal"],
                    ui_scale_dimensions(unscaled_dimensions),
                )
            }
        return {
            "normal": pygame.transform.scale(
                buttonstyles[style.value]["normal"],
                ui_scale_dimensions(unscaled_dimensions),
            ),
            "hovered": pygame.transform.scale(
                buttonstyles[style.value]["hovered"],
                ui_scale_dimensions(unscaled_dimensions),
            ),
            "selected": pygame.transform.scale(
                buttonstyles[style.value]["selected"],
                ui_scale_dimensions(unscaled_dimensions),
            ),
            "disabled": pygame.transform.scale(
                buttonstyles[style.value]["disabled"],
                ui_scale_dimensions(unscaled_dimensions),
            ),
        }

    if buttonstyles[style.value]["ninetile"]:
        if static:
            return {
                "normal": get_box(
                    BoxData(
                        style.value + "_normal",
                        buttonstyles[style.value]["normal"],
                        (3, 3),
                    ),
                    unscaled_dimensions,
                )
            }
        return {
            "normal": get_box(
                BoxData(
                    style.value + "_normal", buttonstyles[style.value]["normal"], (3, 3)
                ),
                unscaled_dimensions,
            ),
            "hovered": get_box(
                BoxData(
                    style.value + "_hovered",
                    buttonstyles[style.value]["hovered"],
                    (3, 3),
                ),
                unscaled_dimensions,
            ),
            "selected": get_box(
                BoxData(
                    style.value + "_selected",
                    buttonstyles[style.value]["selected"],
                    (3, 3),
                ),
                unscaled_dimensions,
            ),
            "disabled": get_box(
                BoxData(
                    style.value + "_disabled",
                    buttonstyles[style.value]["disabled"],
                    (3, 3),
                ),
                unscaled_dimensions,
            ),
        }

    if static:
        return {
            "normal": generate_button(
                buttonstyles[style.value]["normal"],
                ui_scale_dimensions(unscaled_dimensions),
            )
        }

    return {
        "normal": generate_button(
            buttonstyles[style.value]["normal"],
            ui_scale_dimensions(unscaled_dimensions),
        ),
        "hovered": generate_button(
            buttonstyles[style.value]["hovered"],
            ui_scale_dimensions(unscaled_dimensions),
        ),
        "selected": generate_button(
            buttonstyles[style.value]["selected"],
            ui_scale_dimensions(unscaled_dimensions),
        ),
        "disabled": generate_button(
            buttonstyles[style.value]["disabled"],
            ui_scale_dimensions(unscaled_dimensions),
        ),
    }
