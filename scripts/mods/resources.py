# pylint: disable=line-too-long
"""

Loads resources from the modloader directory.


""" # pylint: enable=line-too-long

import os
import typing

import pygame
import pygame.image
from .mods import get_mods

from ._common import FileArg, Literal




def pyg_img_load(filename: FileArg, namehint: str = "") -> pygame.Surface:
    """
    Loads an image from the modloader directory
    """

    mods = get_mods()

    for mod in mods:
        if os.path.exists(os.path.join(os.getcwd(), "mods", mod, filename)):
            _ = os.path.join(os.getcwd(), "mods", mod, filename)
            if namehint == "":
                return pygame.image.load(_, namehint)

    return pygame.image.load(filename, namehint)


def mod_open(
    file: FileDescriptorOrPath,
    mode: OpenTextMode = "r",
    buffering: int = -1,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
    closefd: bool = True,
    opener: _Opener | None = None,
) -> TextIOWrapper:
