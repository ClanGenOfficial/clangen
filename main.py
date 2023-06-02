#!/usr/bin/env python3


# pylint: disable=line-too-long
"""



This file is the main file for the game.
It also contains the main pygame loop
It first sets up logging, then loads the version hash from version.ini (if it exists), then loads the cats and clan.
It then loads the settings, and then loads the start screen.




""" # pylint: enable=line-too-long
import shutil
import sys
import time
import os

from scripts.housekeeping.log_cleanup import prune_logs
from scripts.housekeeping.stream_duplexer import UnbufferedStreamDuplexer
from scripts.housekeeping.datadir import get_log_dir, setup_data_dir
from scripts.housekeeping.version import get_version_info, VERSION_NAME


directory = os.path.dirname(__file__)
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


stdout_file = open(get_log_dir() + f'/stdout_{timestr}.log', 'a')
stderr_file = open(get_log_dir() + f'/stderr_{timestr}.log', 'a')
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
if os.environ.get('CODESPACES'):
    print('')
    print("Github codespace user!!! Sorry, but sound *may* not work :(")
    print("SDL_AUDIODRIVER is dsl. This is to avoid ALSA errors, but it may disable sound.")
    print('')
    print("Web VNC:")
    print(
        f"https://{os.environ.get('CODESPACE_NAME')}-6080"
        + f".{os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN')}"
        + "/?autoconnect=true&reconnect=true&password=clangen&resize=scale")
    print("(use clangen in fullscreen mode for best results)")
    print('')


if get_version_info().is_source_build:
    print("Running on source code")
    if get_version_info().version_number == VERSION_NAME:
        print("Failed to get git commit hash, using hardcoded version number instead.")
        print("Hey testers! We recommend you use git to clone the repository, as it makes things easier for everyone.")  # pylint: disable=line-too-long
        print("There are instructions at https://discord.com/channels/1003759225522110524/1054942461178421289/1078170877117616169")  # pylint: disable=line-too-long
else:
    print("Running on PyInstaller build")

print("Version Name: ", VERSION_NAME)
print("Running on commit " + get_version_info().version_number)

# Load game
from scripts.game_structure.load_cat import load_cats, version_convert
from scripts.game_structure.windows import SaveCheck
from scripts.game_structure.game_essentials import game, MANAGER, screen
from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.cat.sprites import sprites
from scripts.clan import clan_class
from scripts.utility import get_text_box_theme, quit, scale  # pylint: disable=redefined-builtin
from scripts.debugmode import debugmode
import pygame_gui
import pygame




# import all screens for initialization (Note - must be done after pygame_gui manager is created)
from scripts.screens.all_screens import start_screen # pylint: disable=ungrouped-imports

# P Y G A M E
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load('resources/images/icon.png'))

# LOAD cats & clan
clan_list = game.read_clans()
if clan_list:
    game.switches['clan_list'] = clan_list
    try:
        load_cats()
        version_info = clan_class.load_clan()
        version_convert(version_info)
    except Exception as e:
        logging.exception("File failed to load")
        if not game.switches['error_message']:
            game.switches[
                'error_message'] = 'There was an error loading the cats file!'
            game.switches['traceback'] = e


# LOAD settings

sprites.load_scars()

start_screen.screen_switches()

if game.settings['fullscreen']:
    version_number = pygame_gui.elements.UILabel(
        pygame.Rect((1500, 1350), (-1, -1)), get_version_info().version_number[0:8],
        object_id=get_text_box_theme())
    # Adjust position
    version_number.set_position(
        (1600 - version_number.get_relative_rect()[2] - 8,
         1400 - version_number.get_relative_rect()[3]))
else:
    version_number = pygame_gui.elements.UILabel(
        pygame.Rect((700, 650), (-1, -1)), get_version_info().version_number[0:8],
        object_id=get_text_box_theme())
    # Adjust position
    version_number.set_position(
        (800 - version_number.get_relative_rect()[2] - 8,
        700 - version_number.get_relative_rect()[3]))

if get_version_info().is_source_build or get_version_info().is_dev():
    dev_watermark = pygame_gui.elements.UILabel(
        scale(pygame.Rect((1050, 1321), (600, 100))),
        "Dev Build:",
        object_id="#dev_watermark"
    )

game.rpc = _DiscordRPC("1076277970060185701", daemon=True)
game.rpc.start()
game.rpc.start_rpc.set()


cursor_img = pygame.image.load('resources/images/cursor.png').convert_alpha()
cursor = pygame.cursors.Cursor((9,0), cursor_img)
disabled_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)





while True:
    time_delta = clock.tick(game.switches['fps']) / 1000.0
    if game.switches['cur_screen'] not in ['start screen']:
        if game.settings['dark mode']:
            screen.fill((57, 50, 36))
        else:
            screen.fill((206, 194, 168))

    if game.settings['custom cursor']:
        if pygame.mouse.get_cursor() == disabled_cursor:
            pygame.mouse.set_cursor(cursor)
    elif pygame.mouse.get_cursor() == cursor:
        pygame.mouse.set_cursor(disabled_cursor)
    # Draw screens
    # This occurs before events are handled to stop pygame_gui buttons from blinking.
    game.all_screens[game.current_screen].on_use()

    # EVENTS
    for event in pygame.event.get():
        game.all_screens[game.current_screen].handle_event(event)

        if event.type == pygame.QUIT:
            # Dont display if on the start screen or there is no clan.
            if (game.switches['cur_screen'] in ['start screen',
                                                'switch clan screen',
                                                'settings screen',
                                                'info screen',
                                                'make clan screen']
                or not game.clan):
                quit(savesettings=False)
            else:
                SaveCheck(game.switches['cur_screen'], False, None)


        # MOUSE CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.clicked = True

            if MANAGER.visual_debug_active:
                _ = pygame.mouse.get_pos()
                if game.settings['fullscreen']:
                    print(f"(x: {_[0]}, y: {_[1]})")
                else:
                    print(f"(x: {_[0]*2}, y: {_[1]*2})")
                del _

        # F2 turns toggles visual debug mode for pygame_gui, allowed for easier bug fixes.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F2:
                debugmode.toggle_console()

        MANAGER.process_events(event)
    

    MANAGER.update(time_delta)

    # update
    game.update_game()
    if game.switch_screens:
        game.all_screens[game.last_screen_forupdate].exit_screen()
        game.all_screens[game.current_screen].screen_switches()
        game.switch_screens = False


    debugmode.update1(clock)
    # END FRAME
    MANAGER.draw_ui(screen)
    debugmode.update2(screen)


    pygame.display.update()
