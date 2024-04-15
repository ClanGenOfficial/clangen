"""
Shim for pygbag (web runner) to detect all imports
"""

print("Loading...")

import i18n
import pygame
import pygame_gui
import asyncio
import platform


from scripts.game_structure.load_cat import load_cats, version_convert
from scripts.game_structure.windows import SaveCheck
from scripts.game_structure.game_essentials import game, MANAGER, screen
from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.cat.sprites import sprites
from scripts.clan import clan_class
from scripts.utility import get_text_box_theme, quit, scale  # pylint: disable=redefined-builtin
from scripts.debug_menu import debugmode

from main import main
asyncio.run(main())