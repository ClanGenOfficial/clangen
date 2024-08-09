from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from functools import cache
from math import ceil
from typing import Tuple, Dict, Union, Optional

import pygame

import scripts.game_structure.screen_settings
from scripts.utility import ui_scale_value, ui_scale_dimensions


@dataclass
class BoxData:
    surface: pygame.Surface
    tilecount: Tuple[int, int]


class BoxStyles(Enum):
    FRAME = BoxData(
        pygame.image.load("resources/images/generated_boxes/frame.png").convert_alpha(),
        (3, 3),
    )
    ROUNDED_BOX = BoxData(
        pygame.image.load(
            "resources/images/generated_boxes/selection_box.png"
        ).convert_alpha(),
        (7, 3),
    )


@dataclass
class Tileset:
    height: int
    topleft: pygame.Surface
    top: pygame.Surface
    topright: pygame.Surface
    left: pygame.Surface
    middle: pygame.Surface
    right: pygame.Surface
    bottomleft: pygame.Surface
    bottom: pygame.Surface
    bottomright: pygame.Surface

    top_noborder: Optional[pygame.Surface] = None
    right_noborder: Optional[pygame.Surface] = None
    bottom_noborder: Optional[pygame.Surface] = None
    left_noborder: Optional[pygame.Surface] = None

    topleft_notop: Optional[pygame.Surface] = None
    topleft_noleft: Optional[pygame.Surface] = None
    topright_notop: Optional[pygame.Surface] = None
    topright_noright: Optional[pygame.Surface] = None
    bottomleft_nobottom: Optional[pygame.Surface] = None
    bottomleft_noleft: Optional[pygame.Surface] = None
    bottomright_nobottom: Optional[pygame.Surface] = None
    bottomright_noright: Optional[pygame.Surface] = None


tilesets: Dict[float, Dict[BoxStyles, Tileset]] = {}


def get_tileset(style: BoxStyles) -> Tileset:
    screen_scale = scripts.game_structure.screen_settings.screen_scale
    if screen_scale in tilesets and style.name in tilesets[screen_scale]:
        return tilesets[screen_scale][style]

    surface = style.value.surface

    # ceiling to the nearest multiple of the tilecount
    width = (
        ceil(ui_scale_value(surface.get_width()) / style.value.tilecount[0])
        * style.value.tilecount[0]
    )
    height = (
        ceil(ui_scale_value(surface.get_height()) / style.value.tilecount[1])
        * style.value.tilecount[1]
    )

    scaled_base = pygame.transform.scale(surface, (width, height))

    tile_edge_length = round(height / style.value.tilecount[1])
    tile_size = (tile_edge_length, tile_edge_length)

    # make the tiles
    topleft = _get_tile_from_coords(scaled_base, (0, 0), tile_size)
    top = _get_tile_from_coords(scaled_base, (1, 0), tile_size)
    topright = _get_tile_from_coords(scaled_base, (2, 0), tile_size)

    left = _get_tile_from_coords(scaled_base, (0, 1), tile_size)
    middle = _get_tile_from_coords(scaled_base, (1, 1), tile_size)
    right = _get_tile_from_coords(scaled_base, (2, 1), tile_size)

    bottomleft = _get_tile_from_coords(scaled_base, (0, 2), tile_size)
    bottom = _get_tile_from_coords(scaled_base, (1, 2), tile_size)
    bottomright = _get_tile_from_coords(scaled_base, (2, 2), tile_size)

    try:
        topleft_notop = _get_tile_from_coords(scaled_base, (3, 0), tile_size)
        topleft_noleft = _get_tile_from_coords(scaled_base, (3, 1), tile_size)
        top_noborder = _get_tile_from_coords(scaled_base, (3, 2), tile_size)
        topright_notop = _get_tile_from_coords(scaled_base, (4, 0), tile_size)
        topright_noright = _get_tile_from_coords(scaled_base, (4, 1), tile_size)
        right_noborder = _get_tile_from_coords(scaled_base, (4, 2), tile_size)
        bottomleft_nobottom = _get_tile_from_coords(scaled_base, (5, 0), tile_size)
        bottomleft_noleft = _get_tile_from_coords(scaled_base, (5, 1), tile_size)
        bottom_noborder = _get_tile_from_coords(scaled_base, (5, 2), tile_size)
        bottomright_nobottom = _get_tile_from_coords(scaled_base, (6, 0), tile_size)
        bottomright_noright = _get_tile_from_coords(scaled_base, (6, 1), tile_size)
        left_noborder = _get_tile_from_coords(scaled_base, (6, 2), tile_size)

    except ValueError:
        (
            topleft_notop,
            topleft_noleft,
            topright_notop,
            topright_noright,
            bottomleft_nobottom,
            bottomleft_noleft,
            bottomright_nobottom,
            bottomright_noright,
            top_noborder,
            left_noborder,
            bottom_noborder,
            right_noborder,
        ) = [None] * 12

    if screen_scale not in tilesets:
        tilesets[screen_scale] = {}

    tilesets[screen_scale][style] = Tileset(
        height=tile_edge_length,
        topleft=topleft,
        top=top,
        topright=topright,
        left=left,
        middle=middle,
        right=right,
        bottomleft=bottomleft,
        bottom=bottom,
        bottomright=bottomright,
        top_noborder=top_noborder,
        left_noborder=left_noborder,
        bottom_noborder=bottom_noborder,
        right_noborder=right_noborder,
        topleft_notop=topleft_notop,
        topleft_noleft=topleft_noleft,
        topright_notop=topright_notop,
        topright_noright=topright_noright,
        bottomleft_nobottom=bottomleft_nobottom,
        bottomleft_noleft=bottomleft_noleft,
        bottomright_nobottom=bottomright_nobottom,
        bottomright_noright=bottomright_noright,
    )
    return tilesets[screen_scale][style]


def _get_tile_from_coords(
    tilemap: pygame.Surface, tile_coords: Tuple[int, int], tile_size: Tuple[int, int]
):
    return tilemap.subsurface(
        (tile_coords[0] * tile_size[0], tile_coords[1] * tile_size[1]), tile_size
    )


def get_box(
    style: BoxStyles,
    unscaled_dimensions: Tuple[int, int],
    sides=True,
    use_extra_if_available: bool = True,
) -> pygame.Surface:
    """
    Generate a surface of arbitrary length and height from a given input surface
    :param style: the BoxStyles style to create from
    :param unscaled_dimensions: the SCALED dimensions of the final box
    :param sides: Whether to render the sides of the box or just end it abruptly.
        Tuple of booleans in order: Top, right, bottom, left. Also accepts a single boolean for all 4 values
    :param use_extra_if_available: Whether to use the expanded tileset if the style has it. Default True.
    :return: A surface
    """
    return pygame.transform.scale(
        _get_box(style, unscaled_dimensions, sides, use_extra_if_available),
        ui_scale_dimensions(unscaled_dimensions),
    )


@cache
def _get_box(
    style: BoxStyles,
    scaled_dimensions: Tuple[int, int],
    sides: Union[bool, Tuple[bool, bool, bool, bool]] = True,
    use_extra_if_available=True,
) -> pygame.Surface:
    """
    A wrapper for get_box that lets it be typehinted & still cache properly
    :param style:
    :param scaled_dimensions:
    :return:
    """

    tileset = _build_needed_tileset(
        style, sides, use_extra_if_available=use_extra_if_available
    )

    if (
        scaled_dimensions[0] < tileset.height * 3
        or scaled_dimensions[1] < tileset.height * 3
    ):
        # this is smaller than the absolute minimum dimensions for this item. Raise an exception.
        raise Exception(
            f"Requested dimensions are too small! "
            f"Minimum size {tileset.height * 3} x {tileset.height * 3}, requested size "
            f"{scaled_dimensions[0]} x {scaled_dimensions[1]}."
        )

    # the number of tiles we need to make the desired size
    tilecount = (
        scaled_dimensions[0] // tileset.height,
        scaled_dimensions[1] // tileset.height,
    )

    # not all requests will be clean multiples of the tile size. this fixes that.
    extra_width = scaled_dimensions[0] % tileset.height
    extra_height = scaled_dimensions[1] % tileset.height

    extra_width_tiles = (
        None
        if extra_width == 0
        else {
            "top": tileset.top.subsurface((0, 0), (extra_width, tileset.height)),
            "middle": tileset.middle.subsurface((0, 0), (extra_width, tileset.height)),
            "bottom": tileset.bottom.subsurface((0, 0), (extra_width, tileset.height)),
        }
    )

    extra_height_tiles = (
        None
        if extra_height == 0
        else {
            "left": tileset.left.subsurface((0, 0), (tileset.height, extra_height)),
            "middle": tileset.middle.subsurface(
                ((0, 0), (tileset.height, extra_height))
            ),
            "right": tileset.right.subsurface(((0, 0), (tileset.height, extra_height))),
        }
    )

    extra_corner_tile = (
        tileset.middle.subsurface(
            (0, 0),
            (extra_width, extra_height),
        )
        if extra_width != 0 and extra_height != 0
        else None
    )

    # okay, here's how the nine-tile system works. check the comments to see
    # which tile is being referred to in each part of this awful construction

    #      0     1     *     2
    #   |-----|-----|-----|-----|
    # 0 |  A  |  B  |  *  |  C  |
    #   |-----|-----|-----|-----|
    # 1 |  D  |  E  |  *  |  F  |
    #   |-----|-----|-----|-----|
    # * |  *  |  *  |  *  |  *  |
    #   |-----|-----|-----|-----|
    # 2 |  G  |  H  |  *  |  I  |
    #   |-----|-----|-----|-----|

    # asterisk = extra, cut-off tile to make up full desired size

    row_length = tilecount[0] + (1 if extra_width_tiles is not None else 0)
    row_x = [x * tileset.height for x in range(row_length - 1)]
    if extra_width_tiles is not None:
        row_x.append(row_x[-1] + extra_width)
    else:
        row_x.append(row_x[-1] + tileset.height)

    # AB*C
    top_row = (
        [tileset.topleft]
        + [tileset.top] * (tilecount[0] - 2)
        + (
            [extra_width_tiles["top"]] + [tileset.topright]
            if extra_width_tiles is not None
            else [tileset.topright]
        )
    )
    coords = [(x, 0) for x in row_x]
    top_row = tuple(zip(top_row, coords))

    # DE*F
    middle_row = (
        [tileset.left]
        + [tileset.middle] * (tilecount[0] - 2)
        + (
            [extra_width_tiles["middle"]] + [tileset.right]
            if extra_width_tiles is not None
            else [tileset.right]
        )
    )

    # ****
    extra_row = (
        (
            [extra_height_tiles["left"]]
            + [extra_height_tiles["middle"]] * (tilecount[0] - 2)
            + (
                [extra_corner_tile] + [extra_height_tiles["right"]]
                if extra_width_tiles is not None
                else [extra_height_tiles["right"]]
            )
        )
        if extra_height_tiles is not None
        else None
    )

    # GH*I
    bottom_row = (
        [tileset.bottomleft]
        + [tileset.bottom] * (tilecount[0] - 2)
        + (
            [extra_width_tiles["bottom"]] + [tileset.bottomright]
            if extra_width_tiles is not None
            else [tileset.bottomright]
        )
    )
    coords = [(x, scaled_dimensions[1] - tileset.height) for x in row_x]
    bottom_row = tuple(zip(bottom_row, coords))

    # ok time to build this ungodly contraption.
    surface = pygame.Surface(scaled_dimensions, flags=pygame.SRCALPHA)
    surface.fblits(top_row)

    for i in range(1, tilecount[1] - 1):
        coords = [(x, i * tileset.height) for x in row_x]
        row = tuple(zip(middle_row, coords))
        surface.fblits(row)
    if extra_row is not None:
        coords = [
            (x, scaled_dimensions[1] - tileset.height - extra_height) for x in row_x
        ]
        extra_row = tuple(zip(extra_row, coords))
        surface.fblits(extra_row)

    surface.fblits(bottom_row)

    return surface


def _build_needed_tileset(
    style: BoxStyles,
    sides: Union[bool, Tuple[bool, bool, bool, bool]],
    use_extra_if_available=True,
):
    if isinstance(sides, bool):
        border_top = sides
        border_right = sides
        border_bottom = sides
        border_left = sides
    elif isinstance(sides, tuple):
        border_top, border_right, border_bottom, border_left = sides
    else:
        raise Exception("invalid sides argument supplied")

    tileset = get_tileset(style)

    tiles_top = _handle_edges(
        {
            "border": tileset.top,
            "noborder": tileset.top_noborder,
            "middle": tileset.middle,
        },
        border_top,
        use_extra_if_available,
    )

    tiles_topleft = _handle_corners(
        {
            "all": tileset.topleft,
            "middle": tileset.middle,
            "side1": tileset.top,
            "side2": tileset.left,
            "noside1": tileset.topleft_notop,
            "noside2": tileset.topleft_noleft,
        },
        border_top,
        border_left,
        use_extra_if_available,
    )

    tiles_topright = _handle_corners(
        {
            "all": tileset.topright,
            "middle": tileset.middle,
            "side1": tileset.top,
            "side2": tileset.right,
            "noside1": tileset.topright_notop,
            "noside2": tileset.topright_noright,
        },
        border_top,
        border_right,
        use_extra_if_available,
    )

    tiles_middle = tileset.middle
    tiles_left = _handle_edges(
        {
            "border": tileset.left,
            "noborder": tileset.left_noborder,
            "middle": tileset.middle,
        },
        border_left,
        use_extra_if_available,
    )
    tiles_right = _handle_edges(
        {
            "border": tileset.right,
            "noborder": tileset.right_noborder,
            "middle": tileset.middle,
        },
        border_right,
        use_extra_if_available,
    )

    tiles_bottom = _handle_edges(
        {
            "border": tileset.bottom,
            "noborder": tileset.bottom_noborder,
            "middle": tileset.middle,
        },
        border_bottom,
        use_extra_if_available,
    )
    tiles_bottomleft = _handle_corners(
        {
            "all": tileset.bottomleft,
            "middle": tileset.middle,
            "side1": tileset.bottom,
            "side2": tileset.left,
            "noside1": tileset.bottomleft_nobottom,
            "noside2": tileset.bottomleft_noleft,
        },
        border_bottom,
        border_left,
        use_extra_if_available,
    )

    tiles_bottomright = _handle_corners(
        {
            "all": tileset.bottomright,
            "middle": tileset.middle,
            "side1": tileset.bottom,
            "side2": tileset.right,
            "noside1": tileset.bottomright_nobottom,
            "noside2": tileset.bottomright_noright,
        },
        border_bottom,
        border_right,
        use_extra_if_available,
    )

    return Tileset(
        tileset.height,
        tiles_topleft,
        tiles_top,
        tiles_topright,
        tiles_left,
        tiles_middle,
        tiles_right,
        tiles_bottomleft,
        tiles_bottom,
        tiles_bottomright,
    )


def _handle_corners(tiles, border_side1, border_side2, use_extra_if_available):
    if not border_side1 and not border_side2:
        return tiles["middle"]
    elif border_side1 and border_side2:
        return tiles["all"]
    elif not border_side1:
        return (
            tiles["noside1"]
            if tiles["noside1"] is not None and use_extra_if_available
            else tiles["side2"]
        )
    elif not border_side2:
        return (
            tiles["noside2"]
            if tiles["noside2"] is not None and use_extra_if_available
            else tiles["side1"]
        )
    else:
        raise Exception("Something went wrong in _build_needed_tileset")


def _handle_edges(tiles, show_border, use_extra_if_available):
    if show_border:
        return tiles["border"]
    return (
        tiles["noborder"]
        if tiles["noborder"] is not None and use_extra_if_available
        else tiles["middle"]
    )
