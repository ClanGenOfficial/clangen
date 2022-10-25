import pygame
from math import ceil

from .base_screens import Screens, draw_menu_buttons

from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.cat.cats import Cat
from scripts.cat.sprites import tiles
#from scripts.world import load_map

class OutsideClanScreen(Screens):

    def on_use(self):
        verdana_big.text('Cats Outside The Clan', ('center', 30))
        verdana.text('ALL CATS LIST', ('center', 100))
        living_cats = []
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if not the_cat.dead and the_cat.exiled:
                living_cats.append(the_cat)

        search_text = game.switches['search_text']
        pygame.draw.rect(screen, 'lightgray', pygame.Rect((170, 130),
                                                          (150, 20)))
        verdana.text('Search: ', (100, 130))
        verdana_black.text(game.switches['search_text'], (180, 130))
        search_cats = []
        if search_text.strip() != '':
            for cat in living_cats:
                if search_text.lower() in str(cat.name).lower():
                    search_cats.append(cat)
        else:
            search_cats = living_cats.copy()
        all_pages = int(ceil(len(search_cats) /
                             20.0)) if len(search_cats) > 20 else 1
        pos_x = 0
        pos_y = 0
        cats_on_page = 0
        for x in range(len(search_cats)):
            if x + (game.switches['list_page'] - 1) * 20 >= len(search_cats):
                game.switches['list_page'] -= 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            the_cat = search_cats[x + (game.switches['list_page'] - 1) * 20]
            if not the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y),
                                    image=the_cat.sprite,
                                    cat=the_cat.ID)

                name_len = verdana.text(str(the_cat.name))
                verdana_red.text(str(the_cat.name),
                                 (155 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100
                if cats_on_page >= 20 or x + (game.switches['list_page'] -
                                              1) * 20 == len(search_cats) - 1:
                    break
        verdana.text(
            'page ' + str(game.switches['list_page']) + ' / ' + str(all_pages),
            ('center', 600))

        if game.switches['list_page'] > 1:
            buttons.draw_button((300, 600),
                                text='<',
                                list_page=game.switches['list_page'] - 1,
                                hotkey=[23])

        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600),
                                text='>',
                                list_page=game.switches['list_page'] + 1,
                                hotkey=[21])

        buttons.draw_button((-70, 140),
                            text='Cats in ' + str(game.clan.name) + 'Clan',
                            cur_screen='list screen',
                            hotkey=[9])
        draw_menu_buttons()

class MapScreen(Screens):

    def on_use(self):
        hunting_claim = str(game.clan.name) + 'Clan Hunting Grounds'
        territory_claim = str(game.clan.name) + 'Clan Territory'
        training_claim = str(game.clan.name) + 'Clan Training Grounds'
        for y in range(44):
            for x in range(40):
                biome = game.map_info[(x, y)][2]
                if biome == 'Desert':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain1'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Forest':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain3'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Plains':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain0'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Ocean':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain2'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Mountainous':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain5'],
                                                     (16, 16)),
                        map_selection=(x, y))
                elif biome == 'Beach':
                    buttons.draw_button(
                        (x * 16, y * 16),
                        image=pygame.transform.scale(tiles.sprites['terrain6'],
                                                     (16, 16)),
                        map_selection=(x, y))
                if (x, y) == game.clan.camp_site:
                    buttons.draw_button((x * 16, y * 16),
                                        image=pygame.transform.scale(
                                            tiles.sprites['terraintwo0'],
                                            (16, 16)),
                                        map_selection=(x, y))
                    game.map_info[(x, y)] = [
                        x, y,
                        str(biome), game.clan.name + 'Clan Camp',
                        "Twoleg Activity: none", "Thunderpath Traffic: none",
                        "Prey Levels: low",
                        str(game.map_info[(x, y)][7])
                    ]
                if (x, y) == game.switches['map_selection']:
                    if str(game.map_info[(x, y)][3]) == territory_claim:
                        buttons.draw_button((-16, 450),
                                            text='Hunting Grounds',
                                            hunting_territory=(x, y))
                        buttons.draw_button((-16, 500),
                                            text='Training Grounds',
                                            training_territory=(x, y))
                if (x, y) == game.switches['hunting_territory']:
                    territory_biome = str(game.map_info[(x, y)][2])
                    territory_twolegs = str(game.map_info[(x, y)][4])
                    territory_thunderpath = str(game.map_info[(x, y)][5])
                    territory_prey = str(game.map_info[(x, y)][6])
                    territory_plants = str(game.map_info[(x, y)][7])
                    if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                        game.map_info[(x, y)] = [
                            x, y, territory_biome, hunting_claim,
                            territory_twolegs, territory_thunderpath,
                            territory_prey, territory_plants
                        ]
                elif (x, y) == game.switches['training_territory']:
                    territory_biome = str(game.map_info[(x, y)][2])
                    territory_twolegs = str(game.map_info[(x, y)][4])
                    territory_thunderpath = str(game.map_info[(x, y)][5])
                    territory_prey = str(game.map_info[(x, y)][6])
                    territory_plants = str(game.map_info[(x, y)][7])
                    if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                        game.map_info[(x, y)] = [
                            x, y, territory_biome, training_claim,
                            territory_twolegs, territory_thunderpath,
                            territory_prey, territory_plants
                        ]
                if game.map_info[(x, y)][3] == hunting_claim:
                    buttons.draw_button((x * 16, y * 16),
                                        image=pygame.transform.scale(
                                            tiles.sprites['terraintwo1'],
                                            (16, 16)))
                    game.switches['hunting_territory'] = (x, y)
                elif game.map_info[(x, y)][3] == territory_claim:
                    buttons.draw_button((x * 16, y * 16),
                                        image=pygame.transform.scale(
                                            tiles.sprites['terraintwo2'],
                                            (16, 16)))
                elif game.map_info[(x, y)][3] == training_claim:
                    buttons.draw_button((x * 16, y * 16),
                                        image=pygame.transform.scale(
                                            tiles.sprites['terraintwo3'],
                                            (16, 16)))
                for clan in game.clan.all_clans:
                    camp_claim = str(clan) + " Camp"
                    other_territory = str(clan) + " Territory"
                    if game.map_info[(x, y)][3] == camp_claim:
                        if game.map_info[(x, y)][2] == "Ocean":
                            game.map_info[(x, y)] = [
                                x, y, game.map_info[(x, y)][2], "Unclaimable",
                                game.map_info[(x, y)][4],
                                game.map_info[(x, y)][5],
                                game.map_info[(x, y)][6],
                                game.map_info[(x, y)][7]
                            ]
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terraintwo4'],
                                                (16, 16)))
                    elif game.map_info[(x, y)][3] == other_territory:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terraintwo4'],
                                                (16, 16)))
        verdana_big.text('Map', (-16, 50))
        verdana.text(
            str(game.map_info[game.switches['map_selection']][0]) + ", " +
            str(game.map_info[game.switches['map_selection']][1]), (-16, 100))
        verdana.text(str(game.map_info[game.switches['map_selection']][2]),
                     (-16, 150))
        verdana.text(str(game.map_info[game.switches['map_selection']][3]),
                     (-16, 200))
        verdana.text(str(game.map_info[game.switches['map_selection']][4]),
                     (-16, 250))
        verdana.text(str(game.map_info[game.switches['map_selection']][5]),
                     (-16, 300))
        verdana.text(str(game.map_info[game.switches['map_selection']][6]),
                     (-16, 350))
        verdana.text(str(game.map_info[game.switches['map_selection']][7]),
                     (-16, 400))

        buttons.draw_button((-16, -56),
                            text='<< Back',
                            cur_screen=game.switches['last_screen'],
                            hotkey=[0])
"""
    def screen_switches(self):
        try:
            game.map_info = load_map('saves/' + game.clan.name)
            print("Map loaded.")
        except:
            game.map_info = load_map("Fallback")
            print("Default map loaded.")
"""