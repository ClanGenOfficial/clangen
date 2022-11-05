#!/usr/bin/env python3
import sys
import os
directory = os.path.dirname(__file__)
if directory:
    os.chdir(directory)
from scripts.game_structure.text import verdana
from scripts.game_structure.buttons import buttons
from scripts.game_structure.load_cat import *
from scripts.cat.sprites import sprites
#from scripts.world import load_map
from scripts.clan import clan_class

# import all screens for initialization
from scripts.screens.all_screens import *

# P Y G A M E
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load('resources/images/icon.png'))

# LOAD cats & clan
if not os.path.exists('saves/clanlist.txt'):
    os.makedirs('saves', exist_ok=True)
    with open('saves/clanlist.txt', 'w') as write_file:
        write_file.write('')
with open('saves/clanlist.txt', 'r') as read_file:
    clan_list = read_file.read()
    if_clans = len(clan_list.strip())
if if_clans > 0:
    game.switches['clan_list'] = clan_list.split('\n')
    try:
        load_cats()
        clan_class.load_clan()
    except Exception as e:
        print("\nERROR MESSAGE:\n",e,"\n")
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
        print("Default map loaded.")
        """

# LOAD settings
if not os.path.exists('saves/settings.txt'):
    with open('saves/settings.txt', 'w') as write_file:
        write_file.write('')
game.load_settings()

# reset brightness to allow for dark mode to not look crap
verdana.change_text_brightness()
buttons.change_button_brightness()
sprites.load_scars()

pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT, pygame.MOUSEBUTTONDOWN])

while True:
    if game.settings['dark mode']:
        screen.fill((40, 40, 40))
    else:
        screen.fill((255, 255, 255))

    if game.settings_changed:
        verdana.change_text_brightness()
        buttons.change_button_brightness()

    mouse.check_pos()

    # EVENTS
    for event in pygame.event.get():
        if game.current_screen == 'profile screen':
            previous_cat = 0
            next_cat = 0
            the_cat = Cat.all_cats.get(game.switches['cat'],
                                             game.clan.instructor)
            for check_cat in Cat.all_cats:
                if Cat.all_cats[check_cat].ID == the_cat.ID:
                    next_cat = 1
                if next_cat == 0 and Cat.all_cats[
                        check_cat].ID != the_cat.ID and Cat.all_cats[
                            check_cat].dead == the_cat.dead and Cat.all_cats[
                                check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                    check_cat].exiled:
                    previous_cat = Cat.all_cats[check_cat].ID
                elif next_cat == 1 and Cat.all_cats[
                        check_cat].ID != the_cat.ID and Cat.all_cats[
                            check_cat].dead == the_cat.dead and Cat.all_cats[
                                check_cat].ID != game.clan.instructor.ID and not Cat.all_cats[
                                    check_cat].exiled:
                    next_cat = Cat.all_cats[check_cat].ID
                elif int(next_cat) > 1:
                    break
            if next_cat == 1:
                next_cat = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and previous_cat != 0:
                    game.switches['cat'] = previous_cat
                if event.key == pygame.K_RIGHT and next_cat != 0:
                    game.switches['cat'] = next_cat
                if event.key == pygame.K_0:
                    game.switches['cur_screen'] = 'list screen'
                if event.key == pygame.K_1:
                    game.switches['cur_screen'] = 'options screen'
                    game.switches['last_screen'] = 'profile screen'
        if game.current_screen == 'make clan screen' and game.switches[
                'clan_name'] == '' and event.type == pygame.KEYDOWN:
            if event.unicode.isalpha(
            ):  # only allows alphabet letters as an input
                if len(
                        game.switches['naming_text']
                ) < game.max_name_length:  # can't type more than max name length
                    game.switches['naming_text'] += event.unicode
            elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                game.switches['naming_text'] = game.switches[
                    'naming_text'][:-1]

        if game.current_screen == 'events screen' and len(
                game.cur_events_list) > game.max_events_displayed:
            max_scroll_direction = len(
                game.cur_events_list) - game.max_events_displayed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.event_scroll_ct < 0:
                    game.cur_events_list.insert(0, game.cur_events_list.pop())
                    game.event_scroll_ct += 1
                if event.key == pygame.K_DOWN and abs(
                        game.event_scroll_ct) < max_scroll_direction:
                    game.cur_events_list.append(game.cur_events_list.pop(0))
                    game.event_scroll_ct -= 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and game.event_scroll_ct < 0:
                    game.cur_events_list.insert(0, game.cur_events_list.pop())
                    game.event_scroll_ct += 1
                if event.button == 5 and abs(
                        game.event_scroll_ct) < max_scroll_direction:
                    game.cur_events_list.append(game.cur_events_list.pop(0))
                    game.event_scroll_ct -= 1

        if game.current_screen == 'allegiances screen' and len(
                game.allegiance_list) > game.max_allegiance_displayed:
            max_scroll_direction = len(
                game.allegiance_list) - game.max_allegiance_displayed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.allegiance_scroll_ct < 0:
                    game.allegiance_list.insert(0, game.allegiance_list.pop())
                    game.allegiance_scroll_ct += 1
                if event.key == pygame.K_DOWN and abs(
                        game.allegiance_scroll_ct) < max_scroll_direction:
                    game.allegiance_list.append(game.allegiance_list.pop(0))
                    game.allegiance_scroll_ct -= 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and game.allegiance_scroll_ct < 0:
                    game.allegiance_list.insert(0, game.allegiance_list.pop())
                    game.allegiance_scroll_ct += 1
                if event.button == 5 and abs(
                        game.allegiance_scroll_ct) < max_scroll_direction:
                    game.allegiance_list.append(game.allegiance_list.pop(0))
                    game.allegiance_scroll_ct -= 1
        if game.current_screen == 'patrol screen':
            random_options = []
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_9:
                    for u in range(12):
                        i_max = len(game.patrol_cats)
                        if u < i_max:
                            game.switches['current_patrol'].append(
                                game.patrol_cats[u])
        if game.current_screen == 'change name screen' and game.switches[
                'change_name'] == '' and event.type == pygame.KEYDOWN:
            if event.unicode.isalpha() or event.unicode.isspace(
            ):  # only allows alphabet letters/space as an input
                if len(game.switches['naming_text']
                       ) < 20:  # can't type more than max name length
                    game.switches['naming_text'] += event.unicode
            elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                game.switches['naming_text'] = game.switches[
                    'naming_text'][:-1]
        if game.current_screen == 'change gender screen' and game.switches[
                'change_name'] == '' and event.type == pygame.KEYDOWN:
            if event.unicode.isalpha() or event.unicode.isspace(
            ):  # only allows alphabet letters/space as an input
                if len(game.switches['naming_text']
                       ) < 20:  # can't type more than max name length
                    game.switches['naming_text'] += event.unicode
            elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                game.switches['naming_text'] = game.switches[
                    'naming_text'][:-1]
        if game.current_screen in [
                'list screen', 'starclan screen', 'other screen', 'relationship screen'
        ] and event.type == pygame.KEYDOWN:
            if event.unicode.isalpha() or event.unicode.isspace(
            ):  # only allows alphabet letters/space as an input
                if len(game.switches['search_text']
                       ) < 20:  # can't type more than max name length
                    game.switches['search_text'] += event.unicode
            elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                game.switches['search_text'] = game.switches[
                    'search_text'][:-1]

        if event.type == pygame.QUIT:
            # close pygame
            pygame.display.quit()
            pygame.quit()
            sys.exit()

        # MOUSE CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.clicked = True

        if event.type == pygame.KEYDOWN:
            game.keyspressed = []
            keys = pygame.key.get_pressed()
            if keys[pygame.K_0]:
                game.keyspressed.append(0)
            if keys[pygame.K_1]:
                game.keyspressed.append(1)
            if keys[pygame.K_2]:
                game.keyspressed.append(2)
            if keys[pygame.K_3]:
                game.keyspressed.append(3)
            if keys[pygame.K_4]:
                game.keyspressed.append(4)
            if keys[pygame.K_5]:
                game.keyspressed.append(5)
            if keys[pygame.K_6]:
                game.keyspressed.append(6)
            if keys[pygame.K_7]:
                game.keyspressed.append(7)
            if keys[pygame.K_8]:
                game.keyspressed.append(8)
            if keys[pygame.K_9]:
                game.keyspressed.append(9)
            if keys[pygame.K_KP0]:
                game.keyspressed.append(10)
            if keys[pygame.K_KP1]:
                game.keyspressed.append(11)
            if keys[pygame.K_KP2]:
                game.keyspressed.append(12)
            if keys[pygame.K_KP3]:
                game.keyspressed.append(13)
            if keys[pygame.K_KP4]:
                game.keyspressed.append(14)
            if keys[pygame.K_KP5]:
                game.keyspressed.append(15)
            if keys[pygame.K_KP6]:
                game.keyspressed.append(16)
            if keys[pygame.K_KP7]:
                game.keyspressed.append(17)
            if keys[pygame.K_KP8]:
                game.keyspressed.append(18)
            if keys[pygame.K_KP9]:
                game.keyspressed.append(19)
            if keys[pygame.K_UP]:
                game.keyspressed.append(20)
            if keys[pygame.K_RIGHT]:
                game.keyspressed.append(21)
            if keys[pygame.K_DOWN]:
                game.keyspressed.append(22)
            if keys[pygame.K_LEFT]:
                game.keyspressed.append(23)

    # SCREENS
    game.all_screens[game.current_screen].on_use()

    # update
    game.update_game()
    if game.switch_screens:
        game.all_screens[game.current_screen].screen_switches()
        game.switch_screens = False
    # END FRAME
    clock.tick(30)

    pygame.display.update()
