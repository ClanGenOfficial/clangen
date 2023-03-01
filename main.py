#!/usr/bin/env python3
import sys
import os
directory = os.path.dirname(__file__)
if directory:
    os.chdir(directory)

import subprocess

# Setup logging
import logging 
formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
# Logging for file
file_handler = logging.FileHandler("clangen.log")
file_handler.setFormatter(formatter)
# Only log errors to file
file_handler.setLevel(logging.ERROR)
# Logging for console 
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logging.root.addHandler(file_handler)
logging.root.addHandler(stream_handler)

def log_crash(type, value, tb):
    # Log exception on crash
    logging.critical("Uncaught exception", exc_info=(type, value, tb))

sys.excepthook = log_crash

# Load game
from scripts.game_structure.load_cat import load_cats
from scripts.game_structure.windows import SaveCheck
from scripts.game_structure.game_essentials import game, MANAGER, screen
# from scripts.game_structure.discord_rpc import _DiscordRPC
from scripts.cat.sprites import sprites
from scripts.clan import clan_class
from scripts.utility import get_text_box_theme
import pygame_gui
import pygame

# if user is developing in a github codespace
if os.environ.get('CODESPACES'):
    print('')
    print("Github codespace user!!! Please ignore the ALSA related errors above.")
    print("They are not a problem, and are caused by the way codespaces work.")
    print('')
    print("Web VNC:")
    print(f"https://{os.environ.get('CODESPACE_NAME')}-6080.{os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN')}/?autoconnect=true&reconnect=true&password=clangen&resize=scale")
    print("(use clangen in fullscreen)")
    print('')

# Version Number to be displayed.
# This will only be shown as a fallback, when the git commit hash can't be found.
VERSION_NUMBER = "Ver. 0.6.0dev"

# import all screens for initialization (Note - must be done after pygame_gui manager is created)
from scripts.screens.all_screens import start_screen

# P Y G A M E
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load('resources/images/icon.png'))

# LOAD cats & clan
clan_list = game.read_clans()
if clan_list:
    game.switches['clan_list'] = clan_list
    try:
        load_cats()
        clan_class.load_clan()
    except Exception as e:
        logging.exception("File failed to load")
        if not game.switches['error_message']:
            game.switches[
                'error_message'] = 'There was an error loading the cats file!'
"""
    try:
        game.map_info = load_map('saves/' + game.clan.name)
    except NameError:
        game.map_info = {}
    except:
        game.map_info = load_map("Fallback")
        """

# LOAD settings

sprites.load_scars()

start_screen.screen_switches()


if os.path.exists("commit.txt"):
    with open(f"commit.txt", 'r') as read_file:
        print("Running on pyinstaller build")
        VERSION_NUMBER = read_file.read()
else:
    print("Running on source code")
    try:
        VERSION_NUMBER = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except:
        print("Failed to get git commit hash, using hardcoded version number instead.")
        print("Hey testers! We recommend you use git to clone the repository, as it makes things easier for everyone.")
        print("There are instructions at https://discord.com/channels/1003759225522110524/1054942461178421289/1078170877117616169")
print("Running on commit " + VERSION_NUMBER)



#Version Number
if game.settings['fullscreen']:
    version_number = pygame_gui.elements.UILabel(pygame.Rect((1500, 1350), (-1, -1)), VERSION_NUMBER[0:8],
                                             object_id=get_text_box_theme())
    # Adjust position
    version_number.set_position((1600 - version_number.get_relative_rect()[2] - 8, 1400 - version_number.get_relative_rect()[3]))
else:
    version_number = pygame_gui.elements.UILabel(pygame.Rect((700, 650), (-1, -1)), VERSION_NUMBER[0:8],
                                             object_id=get_text_box_theme())
    # Adjust position
    version_number.set_position((800 - version_number.get_relative_rect()[2] - 8, 700 - version_number.get_relative_rect()[3]))


# game.rpc = _DiscordRPC("1076277970060185701")
while True:
    time_delta = clock.tick(30) / 1000.0
    if game.switches['cur_screen'] not in ['start screen']:
        if game.settings['dark mode']:
            screen.fill((57, 50, 36))
        else:
            screen.fill((206, 194, 168))

    # Draw screens
    # This occurs before events are handled to stop pygame_gui buttons from blinking.
    game.all_screens[game.current_screen].on_use()

    # EVENTS
    for event in pygame.event.get():
        game.all_screens[game.current_screen].handle_event(event)

        if event.type == pygame.QUIT:
            # Dont display if on the start screen or there is no clan.
            if (game.switches['cur_screen'] in ['start screen', 'switch clan screen', 'settings screen', 'info screen', 'make clan screen']
                or not game.clan):
                #game.rpc.close()
                pygame.display.quit()
                pygame.quit()
                sys.exit()
            else:
                SaveCheck(game.switches['cur_screen'], False, None)


        # MOUSE CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.clicked = True

        # F2 turns toggles visual debug mode for pygame_gui, allowed for easier bug fixes.
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F2:
                if not MANAGER.visual_debug_active:
                    MANAGER.set_visual_debug_mode(True)
                else:
                    MANAGER.set_visual_debug_mode(False)

        MANAGER.process_events(event)

    MANAGER.update(time_delta)

    # update
    game.update_game()
    if game.switch_screens:
        game.all_screens[game.last_screen_forupdate].exit_screen()
        game.all_screens[game.current_screen].screen_switches()
        game.switch_screens = False

    # END FRAME
    MANAGER.draw_ui(screen)

    pygame.display.update()
