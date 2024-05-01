"""
Shim for pygbag (web runner) to detect all imports
"""

from __future__ import print_function
import builtins

builtin_print = builtins.print
def print(*args, **kwargs):
    excludes = [
        "pygame_gui/ui_manager.py",
        "Trying to pre-load font id"
    ]
    if any([str(args).__contains__(exclude) for exclude in excludes]): return 
    platform.window.console.log(str(args))
    return builtin_print(*args, **kwargs)
builtins.print = print

import asyncio

print("Loading...")

import os
import random
import time
random.seed(time.time())

import i18n
import pygame
import pygame_gui
import platform

from scripts.web import notifyFinishLoading, setDownloadLogsCallback, uploadFile, downloadFile, error
from scripts.housekeeping.datadir import get_log_dir

def downloadLogs():
    log_dir = get_log_dir()
    files = os.listdir(log_dir)
    # filter files that start with clangen_
    files = [f for f in files if f.startswith("clangen_")]
    
    # format: clangen_YYYYMMDD_HHMMSS.log
    files.sort()

    # get the latest file
    if len(files) > 0:
        latest = files[-1]
        uploadFile(os.path.join(log_dir, latest))

setDownloadLogsCallback(downloadLogs)

import pygame_gui.core.text
import pygame_gui.core.text.text_line_chunk

from scripts.game_structure.load_cat import load_cats, version_convert
from scripts.game_structure.windows import SaveCheck
from scripts.game_structure.game_essentials import game, MANAGER, screen
from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.cat.sprites import sprites
from scripts.clan import clan_class
from scripts.utility import get_text_box_theme, quit, scale  # pylint: disable=redefined-builtin
from scripts.debug_menu import debugmode
from scripts.screens.all_screens import start_screen





from main import main
try:
    asyncio.run(main())
except Exception as e:
    print(e)
    error(e)
    quit()