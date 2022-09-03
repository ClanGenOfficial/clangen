import sys
import os
from scripts.screens import *

if sys.platform == "darwin":
    os.chdir("/Applications/Clangen.app/Contents/Resources/")

# P Y G A M E
clock = pygame.time.Clock()
pygame.display.set_icon(pygame.image.load('resources/icon.png'))

# LOAD cats & clan
if not os.path.exists('saves/clanlist.txt'):
    os.makedirs('saves', exist_ok=True)
    with open('saves/clanlist.txt', 'w') as write_file:
        write_file.write('')
with open('saves/clanlist.txt', 'r') as read_file:
    clan_list = read_file.read()
    if_clans = len(clan_list)
if if_clans > 0:
    game.switches['clan_list'] = clan_list.split('\n')
    try:
        cat_class.load_cats()
        clan_class = Clan()
        clan_class.load_clan()
    except Exception:
        if not game.switches['error_message']:
            game.switches['error_message'] = 'There was an error loading the cats file!'

    try:
        game.map_info = load_map('saves/'+game.clan.name)
    except NameError:
        game.map_info = {}
    except:   
        game.map_info = load_map("Fallback")
        print("Default map loaded.")

# LOAD settings
if not os.path.exists('saves/settings.txt'):
    with open('saves/settings.txt', 'w') as write_file:
        write_file.write('')
game.load_settings()

# reset brightness to allow for dark mode to not look crap
verdana.change_text_brightness()
buttons.change_button_brightness()
sprites.load_scars()

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
        if game.current_screen == 'events screen' or game.current_screen == 'stats screen' or game.current_screen == 'clan screen' or game.current_screen == 'starclan screen' or game.current_screen == 'patrol screen' or game.current_screen == 'list screen' or game.current_screen == 'allegiances screen':
            if event.type == pygame.KEYDOWN:
                game.switches['last_screen'] = game.current_screen
                if event.key == pygame.K_0:
                    game.switches['cur_screen'] = 'stats screen'
                if event.key == pygame.K_1:
                    game.switches['cur_screen'] = 'events screen'
                if event.key == pygame.K_2:
                    game.switches['cur_screen'] = 'clan screen'
                if event.key == pygame.K_3:
                    game.switches['cur_screen'] = 'starclan screen'
                if event.key == pygame.K_4:
                    game.switches['cur_screen'] = 'patrol screen'
                if event.key == pygame.K_5:
                    game.switches['cur_screen'] = 'list screen'
                if event.key == pygame.K_6:
                    game.switches['cur_screen'] = 'allegiances screen'
                if event.key == pygame.K_7:
                    game.switches['cur_screen'] = 'map screen'
        if game.current_screen == 'map screen':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    game.switches['cur_screen'] = game.switches['last_screen']
                    game.switches['last_screen'] = 'map screen'
        if game.current_screen == 'list screen':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_8:
                    the_cat = list(cat_class.all_cats.values())[0]
                    game.switches['cat'] = the_cat.ID
                    game.switches['cur_screen'] = 'profile screen'
                    game.switches['last_screen'] = 'list screen'
        if game.current_screen == 'profile screen':
            previous_cat = 0
            next_cat = 0
            the_cat = cat_class.all_cats.get(game.switches['cat'],game.clan.instructor)
            for check_cat in cat_class.all_cats:
                if cat_class.all_cats[check_cat].ID == the_cat.ID:
                    next_cat = 1
                if next_cat == 0 and cat_class.all_cats[check_cat].ID != the_cat.ID and cat_class.all_cats[check_cat].dead == the_cat.dead and cat_class.all_cats[check_cat].ID != game.clan.instructor.ID and not cat_class.all_cats[check_cat].exiled:
                    previous_cat = cat_class.all_cats[check_cat].ID
                elif next_cat == 1 and cat_class.all_cats[check_cat].ID != the_cat.ID and cat_class.all_cats[check_cat].dead == the_cat.dead and cat_class.all_cats[check_cat].ID != game.clan.instructor.ID and not cat_class.all_cats[check_cat].exiled:
                    next_cat = cat_class.all_cats[check_cat].ID
                elif int(next_cat) > 1:
                    break
            if next_cat == 1:
                next_cat = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and previous_cat != 0:
                    game.switches['cat']=previous_cat
                if event.key == pygame.K_RIGHT and next_cat != 0:
                    print(next_cat)
                    game.switches['cat']=next_cat
                if event.key == pygame.K_0:
                    game.switches['cur_screen'] = 'list screen'
                if event.key == pygame.K_1:
                    game.switches['cur_screen'] = 'options screen'
                    game.switches['last_screen'] = 'profile screen'
        if game.current_screen == 'options screen':
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                if keys[pygame.K_LSHIFT] and keys[pygame.K_5]:
                    the_cat = cat_class.all_cats.get(game.switches['cat'])
                    game.switches['kill_cat'] = the_cat
                if event.key == pygame.K_0:
                    game.switches['cur_screen'] = 'profile screen'
                if event.key == pygame.K_1:
                    game.switches['cur_screen'] = 'change name screen'
                if event.key == pygame.K_2:
                    game.switches['cur_screen'] = 'see kits screen'
                if event.key == pygame.K_3:
                    game.switches['cur_screen'] = 'relationship screen'
                if event.key == pygame.K_4:
                    game.switches['cur_screen'] = 'choose mate screen'
        if game.current_screen == 'change name screen' or game.current_screen == 'see kits screen' or game.current_screen == 'relationship screen' or game.current_screen == 'choose mate screen':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    game.switches['cur_screen'] = 'options screen'
        if game.current_screen == 'make clan screen' and game.switches['clan_name'] == '' and event.type == pygame.KEYDOWN:
            if event.unicode.isalpha():  # only allows alphabet letters as an input
                if len(game.switches['naming_text']) < game.max_name_length:  # can't type more than max name length
                    game.switches['naming_text'] += event.unicode
            elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                game.switches['naming_text'] = game.switches['naming_text'][:-1]

        if game.current_screen == 'events screen' and len(game.cur_events_list) > game.max_events_displayed:
            max_scroll_direction = len(game.cur_events_list) - game.max_events_displayed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.event_scroll_ct < 0:
                    game.cur_events_list.insert(0, game.cur_events_list.pop())
                    game.event_scroll_ct += 1
                if event.key == pygame.K_DOWN and abs(game.event_scroll_ct) < max_scroll_direction:
                    game.cur_events_list.append(game.cur_events_list.pop(0))
                    game.event_scroll_ct -= 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and game.event_scroll_ct < 0:
                    game.cur_events_list.insert(0, game.cur_events_list.pop())
                    game.event_scroll_ct += 1
                if event.button == 5 and abs(game.event_scroll_ct) < max_scroll_direction:
                    game.cur_events_list.append(game.cur_events_list.pop(0))
                    game.event_scroll_ct -= 1

        if game.current_screen == 'allegiances screen' and len(game.allegiance_list) > game.max_allegiance_displayed:
            max_scroll_direction = len(game.allegiance_list) - game.max_allegiance_displayed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.allegiance_scroll_ct < 0:
                    game.allegiance_list.insert(0, game.allegiance_list.pop())
                    game.allegiance_scroll_ct += 1
                if event.key == pygame.K_DOWN and abs(game.allegiance_scroll_ct) < max_scroll_direction:
                    game.allegiance_list.append(game.allegiance_list.pop(0))
                    game.allegiance_scroll_ct -= 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4 and game.allegiance_scroll_ct < 0:
                        game.allegiance_list.insert(0, game.allegiance_list.pop())
                        game.allegiance_scroll_ct += 1
                if event.button == 5 and abs(game.allegiance_scroll_ct) < max_scroll_direction:
                        game.allegiance_list.append(game.allegiance_list.pop(0))
                        game.allegiance_scroll_ct -= 1
        if game.current_screen == 'patrol screen':
            random_options = []
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_8:
                    print(game.switches['current_patrol'])
                    for u in range(12):
                        i_max = len(game.patrol_cats)
                        if u < i_max:
                            game.switches['current_patrol'].append(game.patrol_cats[u])
        if game.current_screen == 'change name screen' and game.switches['change_name'] == '' and event.type == pygame.KEYDOWN:
            if event.unicode.isalpha() or event.unicode.isspace():  # only allows alphabet letters/space as an input
                if len(game.switches['naming_text']) < 20:  # can't type more than max name length
                    game.switches['naming_text'] += event.unicode
            elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                game.switches['naming_text'] = game.switches['naming_text'][:-1]
            elif event.key == pygame.K_1:
                game.switches['current_screen'] = 'change name screen'
                game.switches['cat'] = game.switches['name_cat']
                cat_value = cat_class.all_cats.get(game.switches['name_cat'])
                if game.switches['naming_text'] != '':
                    name = game.switches['naming_text'].split(' ')
                    cat_value.name.prefix = name[0]
                    if len(name) > 1:
                        cat_value.name.suffix = name[1]
                    cat_class.save_cats()
                    game.switches['naming_text'] = ''
        if game.current_screen in ['list screen', 'starclan screen', 'other screen'] and event.type == pygame.KEYDOWN:
            if event.unicode.isalpha() or event.unicode.isspace():  # only allows alphabet letters/space as an input
                if len(game.switches['search_text']) < 20:  # can't type more than max name length
                    game.switches['search_text'] += event.unicode
            elif event.key == pygame.K_BACKSPACE:  # delete last character of clan name
                game.switches['search_text'] = game.switches['search_text'][:-1]

        if event.type == pygame.QUIT:
            # close pygame
            pygame.display.quit()
            pygame.quit()
            sys.exit()

        # MOUSE CLICK
        if event.type == pygame.MOUSEBUTTONDOWN:
            game.clicked = True

    # SCREENS
    game.all_screens[game.current_screen].on_use()

    # update
    game.update_game()
    if game.switch_screens:
        screens.all_screens[game.current_screen].screen_switches()
        game.switch_screens = False
    # END FRAME
    clock.tick(60)

    pygame.display.update()