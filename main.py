#!/usr/bin/env python3


# pylint: disable=line-too-long
"""



This file is the main file for the game.
It also contains the main pygame loop
It first sets up logging, then loads the version hash from version.ini (if it exists), then loads the cats and clan.
It then loads the settings, and then loads the start screen.




"""  # pylint: enable=line-too-long
# DO NOT ADD YOUR IMPORTS HERE.
# Scroll down to the "Load game" comment and add them there.
# Side effects of imports WILL BREAK crucial setup logic for logging and init
import os
import shutil
import sys
import threading
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

from scripts.housekeeping.log_cleanup import prune_logs
from scripts.housekeeping.stream_duplexer import UnbufferedStreamDuplexer
from scripts.housekeeping.datadir import get_log_dir, setup_data_dir
from scripts.housekeeping.version import get_version_info, VERSION_NAME

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

# Load game
from scripts.clan import clan_class
from scripts.game_structure.audio import sound_manager, music_manager
from scripts.game_structure.load_cat import load_cats, version_convert
from scripts.game_structure.windows import SaveCheck
from scripts.game_structure.screen_settings import screen_scale, MANAGER, screen
from scripts.game_structure.game_essentials import game
from scripts.game_structure import constants
from scripts.game_structure.game.save_load import read_clans
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.game.switches import (
    switch_get_value,
    switch_set_value,
    Switch,
)
from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.cat.sprites import sprites
from scripts.utility import (
    quit,
)  # pylint: disable=redefined-builtin

# from scripts.debug_menu import debugmode
from scripts.debug_console import debug_mode
import pygame

# import all screens for initialization (Note - must be done after pygame_gui manager is created)
from scripts.screens.all_screens import AllScreens
import scripts.game_structure.screen_settings

# P Y G A M E
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load("resources/images/icon.png"))

game.rpc = _DiscordRPC("1076277970060185701", daemon=True)
game.rpc.start()
game.rpc.start_rpc.set()

# LOAD cats & clan
finished_loading = False


def load_data():
    global finished_loading

    # load in the spritesheets
    sprites.load_all()

    clan_list = read_clans()
    if clan_list:
        switch_set_value(Switch.clan_list, clan_list)
        switch_set_value(Switch.clan_name, clan_list[0])
        try:
            load_cats()
            version_info = clan_class.load_clan()
            version_convert(version_info)
            game.load_events()
            scripts.screens.screens_core.screens_core.rebuild_core()
        except Exception as e:
            logging.exception("File failed to load")
            if switch_get_value(Switch.error_message) is None:
                switch_set_value(
                    Switch.error_message, "There was an error loading the cats file!"
                )
                switch_set_value(Switch.traceback, e)

    finished_loading = True


images = []


def loading_animation(scale: float = 1):
    # Load images, adjust color
    color = pygame.Surface((200 * scale, 210 * scale))
    if game_setting_get("dark mode"):
        color.fill(constants.CONFIG["theme"]["light_mode_background"])
    else:
        color.fill(constants.CONFIG["theme"]["dark_mode_background"])

    if len(images) == 0:
        for i in range(1, 11):
            im = pygame.transform.scale_by(
                pygame.image.load(f"resources/images/loading_animate/startup/{i}.png"),
                screen_scale,
            )
            im.blit(color, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            images.append(im)
        del im

    # Cleanup
    del color

    x = screen.get_width() / 2
    y = screen.get_height() / 2

    i = 0
    total_frames = len(images)
    while not finished_loading:
        clock.tick(8)  # Loading screen is 8FPS

        if game_setting_get("dark mode"):
            screen.fill(constants.CONFIG["theme"]["dark_mode_background"])
        else:
            screen.fill(constants.CONFIG["theme"]["light_mode_background"])

        screen.blit(
            images[i], (x - images[i].get_width() / 2, y - images[i].get_height() / 2)
        )

        i += 1
        if i >= total_frames:
            i = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit(savesettings=False)

        pygame.display.update()


def load_game():
    """
    Performs the functions needed to load the game.

    This function is ran when the game loads and whenever the player
    switches clans.
    """
    global finished_loading

    game.cur_events_list.clear()
    game.patrol_cats.clear()
    game.patrolled.clear()
    game.clan = None
    switch_set_value(Switch.switch_clan, False)

    finished_loading = False
    loading_thread = threading.Thread(target=load_data)
    loading_thread.start()
    loading_animation(screen_scale)

    # loading thread should be done by now, so just join it for safety.
    loading_thread.join()
    del loading_thread


# load spritesheets
sprites.load_all()
load_game()

pygame.mixer.pre_init(buffer=44100)
try:
    pygame.mixer.init()
except pygame.error:
    print("Failed to initialize sound. Sound will be disabled.")
    music_manager.audio_disabled = True
    music_manager.muted = True
AllScreens.start_screen.screen_switches()

# dev screen info now lives in scripts/screens/screens_core

cursor_img = pygame.image.load("resources/images/cursor.png").convert_alpha()
cursor = pygame.cursors.Cursor((9, 0), cursor_img)
disabled_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
fps = switch_get_value(Switch.fps)
music_manager.check_music("start screen")
while 1:
    time_delta = clock.tick(fps) / 1000.0

    if game_setting_get("custom cursor"):
        if pygame.mouse.get_cursor() == disabled_cursor:
            pygame.mouse.set_cursor(cursor)
    elif pygame.mouse.get_cursor() == cursor:
        pygame.mouse.set_cursor(disabled_cursor)

    if switch_get_value(Switch.switch_clan):
        load_game()

    # Draw screens
    # This occurs before events are handled to stop pygame_gui buttons from blinking.
    game.all_screens[game.current_screen].on_use()
    # EVENTS
    for event in pygame.event.get():
        if (
            event.type == pygame.KEYDOWN
            and game_setting_get("keybinds")
            and debug_mode.debug_menu.visible
        ):
            pass
        else:
            # todo ...shouldn't this be `get_switch(Switch.cur_screen)`?
            getattr(AllScreens, game.current_screen.replace(" ", "_")).handle_event(
                event
            )

        sound_manager.handle_sound_events(event)

        if event.type == pygame.QUIT:
            # Don't display if on the start screen or there is no clan.
            if (
                switch_get_value(Switch.cur_screen)
                in (
                    "start screen",
                    "switch clan screen",
                    "settings screen",
                    "info screen",
                    "make clan screen",
                )
                or not game.clan
            ):
                quit(savesettings=False)
            else:
                SaveCheck(switch_get_value(Switch.cur_screen), False, None)

        # MOUSE CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.clicked = True

            if MANAGER.visual_debug_active:
                _ = pygame.mouse.get_pos()
                if game_setting_get("fullscreen"):
                    print(f"(x: {_[0]}, y: {_[1]})")
                else:
                    print(f"(x: {_[0] * screen_scale}, y: {_[1] * screen_scale})")
                del _

        # F2 turns toggles visual debug mode for pygame_gui, allowed for easier bug fixes.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F2:
                MANAGER.print_layer_debug()
            elif event.key == pygame.K_F3:
                debug_mode.toggle_debug_mode()
                # debugmode.toggle_console()
            elif event.key == pygame.K_F11:
                scripts.game_structure.screen_settings.toggle_fullscreen(
                    source_screen=getattr(
                        AllScreens,
                        switch_get_value(Switch.cur_screen).replace(" ", "_"),
                    ),
                    show_confirm_dialog=False,
                )

        MANAGER.process_events(event)

    MANAGER.update(time_delta)

    # update
    game.update_game()
    if game.switch_screens:
        getattr(AllScreens, game.last_screen_forupdate.replace(" ", "_")).exit_screen()
        getattr(AllScreens, game.current_screen.replace(" ", "_")).screen_switches()
        game.switch_screens = False
    if (
        not music_manager.audio_disabled
        and not pygame.mixer.music.get_busy()
        and not music_manager.muted
    ):
        music_manager.play_queued()

    debug_mode.pre_update(clock)
    # END FRAME

    MANAGER.draw_ui(screen)

    debug_mode.post_update(screen)

    pygame.display.update()
