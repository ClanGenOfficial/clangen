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
from importlib.util import find_spec

if not getattr(sys, "frozen", False):
    requiredModules = [
        "ujson",
        "pygame",
        "pygame_gui",
        "platformdirs",
        "pgpy",
        "requests",
        "strenum",
    ]

    isMissing = False

    for module in requiredModules:
        if find_spec(module) is None:
            isMissing = True
            break

    if isMissing:
        print(
            """You are missing some requirements to run clangen!

                Please look at the "README.md" file for instructions on how to install them.
                """
        )

        print(
            "If you are still having issues, please ask for help in the clangen discord server: https://discord.gg/clangen"
        )
        sys.exit(1)

    del requiredModules
    del isMissing
del find_spec

from scripts.housekeeping.datadir import get_log_dir, setup_data_dir
from scripts.housekeeping.log_cleanup import prune_logs
from scripts.housekeeping.stream_duplexer import UnbufferedStreamDuplexer
from scripts.housekeeping.version import VERSION_NAME, get_version_info

try:
    directory = os.path.dirname(__file__)
except NameError:
    directory = os.getcwd()
if directory:
    os.chdir(directory)

if os.path.exists("auto-updated"):
    print("Clangen starting, deleting auto-updated file")
    os.remove("auto-updated")
    shutil.rmtree("Downloads", ignore_errors=True)
    print("Update Complete!")
    print("New version: " + get_version_info().version_number)

setup_data_dir()
timestr = time.strftime("%Y%m%d_%H%M%S")

stdout_file = open(get_log_dir() + f"/stdout_{timestr}.log", "a")
stderr_file = open(get_log_dir() + f"/stderr_{timestr}.log", "a")
sys.stdout = UnbufferedStreamDuplexer(sys.stdout, stdout_file)
sys.stderr = UnbufferedStreamDuplexer(sys.stderr, stderr_file)

# Setup logging
import logging

formatter = logging.Formatter(
    "%(name)s - %(levelname)s - %(filename)s / %(funcName)s / %(lineno)d - %(message)s"
)

# Logging for file
timestr = time.strftime("%Y%m%d_%H%M%S")
log_file_name = get_log_dir() + f"/clangen_{timestr}.log"
file_handler = logging.FileHandler(log_file_name)
file_handler.setFormatter(formatter)
# Only log errors to file
file_handler.setLevel(logging.ERROR)
# Logging for console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logging.root.addHandler(file_handler)
logging.root.addHandler(stream_handler)

prune_logs(logs_to_keep=10, retain_empty_logs=False)


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
