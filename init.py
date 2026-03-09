#!/usr/bin/env python3


# pylint: disable=line-too-long
"""
This line is responsible for initializing all the technical little details so that ClanGen
can run properly.
It sets up logging, then loads the version hash from version.ini (if it exists).
"""  # pylint: enable=line-too-long

# DO NOT ADD YOUR IMPORTS HERE.
# Scroll down to the "Load game" comment and add them there.
# Side effects of imports WILL BREAK crucial setup logic for logging and init
import os
import shutil
import sys
import time
from importlib import reload

from scripts.housekeeping.datadir import setup_data_dir
from scripts.housekeeping.version import VERSION_NAME, get_version_info
from scripts.housekeeping.platform import IS_IOS
from scripts.housekeeping.platform_manager import get_platform_manager

try:
    directory = os.path.dirname(__file__)
except NameError:
    directory = os.getcwd()

if directory and not IS_IOS:
    os.chdir(directory)

if os.path.exists("auto-updated"):
    print("Clangen starting, deleting auto-updated file")
    os.remove("auto-updated")
    shutil.rmtree("Downloads", ignore_errors=True)
    print("Update Complete!")
    print("New version: " + get_version_info().version_number)

setup_data_dir()
get_platform_manager().configure_logging()

# Setup logging
import logging


def log_crash(logtype, value, tb):
    """
    Log uncaught exceptions to file
    """
    logging.critical("Uncaught exception", exc_info=(logtype, value, tb))
    sys.__excepthook__(type, value, tb)


sys.excepthook = log_crash

# if user is developing in a github codespace
if os.environ.get("CODESPACES"):
    print("")
    print("Github codespace user!!! Sorry, but sound *may* not work :(")
    print(
        "SDL_AUDIODRIVER is dsl. This is to avoid ALSA errors, but it may disable sound."
    )
    print("")
    print("Web VNC:")
    print(
        f"https://{os.environ.get('CODESPACE_NAME')}-6080"
        + f".{os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN')}"
        + "/?autoconnect=true&reconnect=true&password=clangen&resize=scale"
    )
    print("(use clangen in fullscreen mode for best results)")
    print("")

if get_version_info().is_source_build:
    print("Running on source code")
    if get_version_info().version_number == VERSION_NAME:
        print("Failed to get git commit hash, using hardcoded version number instead.")
        print(
            "Hey testers! We recommend you use git to clone the repository, as it makes things easier for everyone."
        )  # pylint: disable=line-too-long
        print(
            "There are instructions at https://discord.com/channels/1003759225522110524/1054942461178421289/1078170877117616169"
        )  # pylint: disable=line-too-long
else:
    print("Running on PyInstaller build")

print("Version Name: ", VERSION_NAME)
print("Running on commit " + get_version_info().version_number)

import pygame_gui

from scripts.game_structure.monkeypatch import translate

# MONKEYPATCH

pygame_gui.core.utility.translate = translate
for module_name, module in list(sys.modules.items()):
    if module and hasattr(module, "translate"):  # Check for the attribute
        if (
            module.translate is pygame_gui.core.utility.translate
        ):  # Ensure it's the original reference
            setattr(module, "translate", translate)
            break

for module_name, module in list(sys.modules.items()):
    if module_name.startswith(f"pygame_gui."):
        if (
            not module_name.endswith("utility")
            and not module_name.endswith("container_interface")
            and not module_name.endswith("_constants")
            and not module_name.endswith("layered_gui_group")
            and not module_name.endswith("object_id")
        ):
            # Reload the module
            reload(module)
