# pylint: disable=line-too-long
"""

Loads resources from the modloader directory.


""" # pylint: enable=line-too-long

import os
import typing
from types import UnionType

import pygame
import pygame.image
from .mods import modlist

from ._common import FileArg, Literal



def pyg_img_load(filename: FileArg, namehint: str = "") -> pygame.Surface:
    """
    Loads an image from the modloader directory
    """

    mods = modlist.get_mods()

    for mod in mods:
        if os.path.exists(os.path.join(os.getcwd(), "mods", mod, filename)):
            _ = os.path.join(os.getcwd(), "mods", mod, filename)
            if namehint == "":
                return pygame.image.load(_, namehint)

    return pygame.image.load(filename, namehint)


def mod_open(
    file,
    mode = "r",
    buffering: int = -1,
    encoding: str | None = None, # pylint: disable=unsupported-binary-operation
    errors: str | None = None, # pylint: disable=unsupported-binary-operation
    newline: str | None = None, # pylint: disable=unsupported-binary-operation
    closefd: bool = True,
    opener = None, # pylint: disable=unsupported-binary-operation
):
    """
    Opens a file from the modloader directory
    """

    mods = modlist.get_mods()

    for mod in mods:
        if os.path.exists(os.path.join(os.getcwd(), "mods", mod, file)):
            _ = os.path.join(os.getcwd(), "mods", mod, file)
            return open(_, mode, buffering, encoding, errors, newline, closefd, opener)

    return open(file, mode, buffering, encoding, errors, newline, closefd, opener)
