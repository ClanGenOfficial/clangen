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

    if screen_scale not in tilesets:
        tilesets[screen_scale] = {}

    tilesets[screen_scale][style] = Tileset(
        tile_edge_length,
        topleft,
        top,
        topright,
        left,
        middle,
        right,
        bottomleft,
        bottom,
        bottomright,
    )
    return tilesets[screen_scale][style]


def _get_tile_from_coords(
    tilemap: pygame.Surface, tile_coords: Tuple[int, int], tile_size: Tuple[int, int]
):
    return tilemap.subsurface(
        (tile_coords[0] * tile_size[0], tile_coords[1] * tile_size[1]), tile_size
    )


def get_box(
    style: BoxStyles, unscaled_dimensions: Tuple[int, int], sides=True
) -> pygame.Surface:
    """
    Generate a surface of arbitrary length and height from a given input surface
    :param style: the BoxStyles style to create from
    :param unscaled_dimensions: the SCALED dimensions of the final box
    :param sides: Whether to render the sides of the box or just end it abruptly.
        Tuple of booleans in order: Top, right, bottom, left. Also accepts a single boolean for all 4 values
    :return: A surface of the correct dimensions
    """
    return _get_box(style, ui_scale_dimensions(unscaled_dimensions), sides)


@cache
def _get_box(
    style: BoxStyles,
    scaled_dimensions: Tuple[int, int],
    sides: Union[bool, Tuple[bool, bool, bool, bool]] = True,
) -> pygame.Surface:
    """
    A wrapper for get_box that lets it be typehinted & still cache properly
    :param style:
    :param scaled_dimensions:
    :return:
    """

    tileset = get_sides_tileset(style, sides)

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


def get_sides_tileset(
    style: BoxStyles, sides: Union[bool, Tuple[bool, bool, bool, bool]]
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

    tiles_top = tileset.top if border_top else tileset.middle
    tiles_topleft = (
        tileset.topleft
        if (border_top and border_left)
        else tileset.top
        if border_top
        else tileset.left
        if border_left
        else tileset.middle
    )

    tiles_topright = (
        tileset.topright
        if (border_top and border_right)
        else tileset.top
        if border_top
        else tileset.right
        if border_right
        else tileset.middle
    )

    tiles_middle = tileset.middle
    tiles_left = tileset.left if border_left else tileset.middle
    tiles_right = tileset.right if border_right else tileset.middle

    tiles_bottom = tileset.bottom if border_bottom else tileset.middle

    tiles_bottomleft = (
        tileset.bottomleft
        if (border_bottom and border_left)
        else tileset.bottom
        if border_bottom
        else tileset.left
        if border_left
        else tileset.middle
    )

    tiles_bottomright = (
        tileset.bottomright
        if (border_bottom and border_right)
        else tileset.bottom
        if border_bottom
        else tileset.right
        if border_right
        else tileset.middle
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
