#!/usr/bin/env python3
import sys
import os
import traceback
directory = os.path.dirname(__file__)
if directory:
    os.chdir(directory)

from scripts.game_structure.load_cat import *
from scripts.cat.sprites import sprites
from scripts.clan import clan_class
from scripts.utility import get_text_box_theme
import pygame_gui
import pygame

# Version Number to be displayed.
VERSION_NUMBER = "Ver. 0.5.0dev"

# import all screens for initialization (Note - must be done after pygame_gui manager is created)
from scripts.screens.all_screens import *

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
        print("ERROR: \n",traceback.format_exc())
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

#Version Number
version_number = pygame_gui.elements.UILabel(pygame.Rect((1500, 1350), (-1, -1)), VERSION_NUMBER,
                                             object_id=get_text_box_theme())
# Adjust position
version_number.set_position((1600 - version_number.get_relative_rect()[2] - 8, 1400 - version_number.get_relative_rect()[3]))

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
            # close pygame
            pygame.display.quit()
            pygame.quit()
            sys.exit()

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
