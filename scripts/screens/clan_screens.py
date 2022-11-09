import pygame
from math import ceil
from random import choice, randint

from .base_screens import Screens, draw_menu_buttons, cat_profiles, draw_clan_name

from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons
from scripts.cat.cats import Cat
from scripts.game_structure.buttons import *


class ClanScreen(Screens):

    def on_use(self):
        if game.settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                screen.blit(self.newleaf_bg, (0, 0))
            elif game.clan.current_season == 'Greenleaf':
                screen.blit(self.greenleaf_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-bare':
                screen.blit(self.leafbare_bg, (0, 0))
            elif game.clan.current_season == 'Leaf-fall':
                screen.blit(self.leaffall_bg, (0, 0))

        draw_clan_name()

        verdana.text("Leader\'s Den", game.clan.cur_layout['leader den'])
        verdana.text('Medicine Cat Den', game.clan.cur_layout['medicine den'])
        verdana.text('Nursery', game.clan.cur_layout['nursery'])
        verdana.text('Clearing', game.clan.cur_layout['clearing'])
        verdana.text("Apprentices\' Den",
                     game.clan.cur_layout['apprentice den'])
        verdana.text("Warriors\' Den", game.clan.cur_layout['warrior den'])
        verdana.text("Elders\' Den", game.clan.cur_layout['elder den'])
        hotkey_assign_1 = 1
        hotkey_assign_2 = 2
        for x in game.clan.clan_cats:
            if not Cat.all_cats[x].dead and Cat.all_cats[
                    x].in_camp and not Cat.all_cats[x].exiled:
                buttons.draw_button(Cat.all_cats[x].placement,
                                    image=Cat.all_cats[x].sprite,
                                    cat=x,
                                    cur_screen='profile screen',
                                    hotkey=[hotkey_assign_1, hotkey_assign_2])
                hotkey_assign_2 = hotkey_assign_2 + 1
                if hotkey_assign_2 == 20:
                    hotkey_assign_1 = hotkey_assign_1 + 1
                    hotkey_assign_2 = hotkey_assign_1 + 1

        draw_menu_buttons()

        buttons.draw_image_button((343, 625),
                                  button_name='save_clan',
                                  text='Save Clan',
                                  save_clan=True,
                                  size=(114, 30),
                                  hotkey=[9])
        pygame.draw.rect(screen,
                         color='gray',
                         rect=pygame.Rect(320, 660, 160, 20))

        if game.switches['saved_clan']:
            verdana_green.text('Saved!', ('center', -20))
        else:
            verdana_red.text('Remember to save!', ('center', -20))

    def screen_switches(self):
        cat_profiles()
        self.update_camp_bg()
        game.switches['cat'] = None
        p = game.clan.cur_layout
        game.clan.leader.placement = choice(p['leader place'])
        game.clan.medicine_cat.placement = choice(p['medicine place'])
        for x in game.clan.clan_cats:
            i = randint(0, 20)
            if Cat.all_cats[x].status == 'apprentice':
                if i < 13:
                    Cat.all_cats[x].placement = choice([
                        choice(p['apprentice place']),
                        choice(p['clearing place'])
                    ])

                elif i >= 19:
                    Cat.all_cats[x].placement = choice(p['leader place'])
                else:
                    Cat.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['warrior place']),
                        choice(p['elder place']),
                        choice(p['medicine place'])
                    ])

            elif Cat.all_cats[x].status == 'deputy':
                if i < 17:
                    Cat.all_cats[x].placement = choice([
                        choice(p['warrior place']),
                        choice(p['leader place']),
                        choice(p['clearing place'])
                    ])

                else:
                    Cat.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['leader place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

            elif Cat.all_cats[x].status == 'elder':
                Cat.all_cats[x].placement = choice(p['elder place'])
            elif Cat.all_cats[x].status == 'kitten':
                if i < 13:
                    Cat.all_cats[x].placement = choice(
                        p['nursery place'])
                elif i == 19:
                    Cat.all_cats[x].placement = choice(p['leader place'])
                else:
                    Cat.all_cats[x].placement = choice([
                        choice(p['clearing place']),
                        choice(p['warrior place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

            elif Cat.all_cats[x].status in [
                    'medicine cat apprentice', 'medicine cat'
            ]:
                Cat.all_cats[x].placement = choice(p['medicine place'])
            elif Cat.all_cats[x].status == 'warrior':
                if i < 15:
                    Cat.all_cats[x].placement = choice([
                        choice(p['warrior place']),
                        choice(p['clearing place'])
                    ])

                else:
                    Cat.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['leader place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

    def update_camp_bg(self):
        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        camp_bg_base_dir = 'resources/images/camp_bg/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]
        camp_nr = game.clan.camp_bg

        if camp_nr is None:
            camp_nr = 'camp1'
            game.clan.camp_bg = camp_nr
        
        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome
        if biome not in available_biome:
            biome = available_biome[0]
            game.clan.biome = biome
        biome = biome.lower()

        all_backgrounds = []
        for leaf in leaves:
            platform_dir = f'{camp_bg_base_dir}/{biome}/{leaf}_{camp_nr}_{light_dark}.png'
            all_backgrounds.append(platform_dir)

        self.newleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[0]).convert(), (800, 700))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (800, 700))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (800, 700))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (800, 700))

class StarClanScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.starclan_bg = pygame.transform.scale(
            pygame.image.load("resources/images/starclanbg.png").convert(),
            (800, 700))
        self.search_bar = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (228, 34))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (180, 35))
    def on_use(self):
        bg = self.starclan_bg
        screen.blit(bg, (0, 0))

        screen.blit(self.clan_name_bg, (310, 25))

        verdana_big_light.text(f'Starclan', ('center', 32))

        dead_cats = [game.clan.instructor]
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.exiled and not the_cat.df:
                dead_cats.append(the_cat)

        search_text = game.switches['search_text']
        screen.blit(self.search_bar, (452, 135))
        verdana_black.text(game.switches['search_text'], (530, 142))

        search_cats = []
        if search_text.strip() != '':
            for cat in dead_cats:
                if search_text.lower() in str(cat.name).lower():
                    search_cats.append(cat)
        else:
            search_cats = dead_cats.copy()
        all_pages = int(ceil(len(search_cats) /
                             20.0)) if len(search_cats) > 20 else 1
        pos_x = 0
        pos_y = 0
        cats_on_page = 0
        for x in range(len(search_cats)):
            if x + (game.switches['list_page'] - 1) * 20 > len(search_cats):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            the_cat = search_cats[x + (game.switches['list_page'] - 1) * 20]
            if the_cat.dead:
                column = int(pos_x / 100)
                row = int(pos_y / 100)
                buttons.draw_button((130 + pos_x, 180 + pos_y),
                                    image=the_cat.sprite,
                                    cat=the_cat.ID,
                                    cur_screen='profile screen',
                                    hotkey=[row + 1, column + 11])

                name_len = verdana.text(str(the_cat.name))

                # CHECK NAME LENGTH
                name = str(the_cat.name)
                if len(name) >= 13:
                    short_name = str(the_cat.name)[0:12]
                    name = short_name + '...'

                # DISPLAY NAME
                verdana_white.text(name,
                                   (155 + pos_x - name_len/2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100
                if cats_on_page >= 20 or x + (game.switches['list_page'] -
                                              1) * 20 == len(search_cats) - 1:
                    break
        verdana_white.text(
            'page ' + str(game.switches['list_page']) + ' / ' + str(all_pages),
            ('center', 600))

        if game.switches['list_page'] > 1:
            buttons.draw_image_button((310, 595),
                                      button_name='arrow_left',
                                      text='<',
                                      list_page=game.switches['list_page'] - 1,
                                      size=(34, 34),
                                      hotkey=[23])

        if game.switches['list_page'] < all_pages:
            buttons.draw_image_button((456, 595),
                                      button_name='arrow_right',
                                      text='>',
                                      list_page=game.switches['list_page'] + 1,
                                      size=(34, 34),
                                      hotkey=[21])

        draw_menu_buttons()
        

        buttons.draw_image_button((150, 135),
                                  button_name='sc_toggle',
                                  text='SC',
                                  size=(34, 34),
                                  cur_screen='starclan screen',
                                  available=False,
                                  )
        buttons.draw_image_button((116, 135),
                                  button_name='df_toggle',
                                  text='DF',
                                  size=(34, 34),
                                  cur_screen='dark forest screen',
                                  )
    def screen_switches(self):
        cat_profiles()


class ListScreen(Screens):
    # page can be found in game.switches['list_page']
    # the amount of cats a page can hold is 20, so the amount of pages is cats/20

    search_bar = pygame.transform.scale(
        pygame.image.load("resources/images/search_bar.png").convert_alpha(), (228, 34))

    def on_use(self):
        draw_clan_name()

        living_cats = []
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if not the_cat.dead and not the_cat.exiled:
                living_cats.append(the_cat)

        search_text = game.switches['search_text']

        screen.blit(ListScreen.search_bar, (452, 135))
        verdana_black.text(game.switches['search_text'], (530, 142))

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
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            if x + (game.switches['list_page'] - 1) * 20 >= len(search_cats):
                game.switches['list_page'] -= 1
            if x + (game.switches['list_page'] - 1) * 20 < len(search_cats):
                the_cat = search_cats[x +
                                      (game.switches['list_page'] - 1) * 20]
            else:
                the_cat = search_cats[len(search_cats) - 1]
            if not the_cat.dead:
                column = int(pos_x / 100)
                row = int(pos_y / 100)
                buttons.draw_button((130 + pos_x, 180 + pos_y),
                                    image=the_cat.sprite,
                                    cat=the_cat.ID,
                                    cur_screen='profile screen',
                                    hotkey=[row + 1, column + 11])
                name_len = verdana.text(str(the_cat.name))

                # CHECK NAME LENGTH
                name = str(the_cat.name)
                if len(name) >= 13:
                    short_name = str(the_cat.name)[0:12]
                    name = short_name + '...'

                # DISPLAY NAME
                verdana.text(name,
                             ('center', 240 + pos_y),
                             x_start=125 + pos_x,
                             x_limit=125 + pos_x + 60
                             )

                cats_on_page += 1
                pos_x += 120
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
            buttons.draw_image_button((310, 595),
                                      button_name='arrow_left',
                                      text='<',
                                      list_page=game.switches['list_page'] - 1,
                                      size=(34, 34),
                                      hotkey=[23])

        if game.switches['list_page'] < all_pages:
            buttons.draw_image_button((456, 595),
                                      button_name='arrow_right',
                                      text='>',
                                      list_page=game.switches['list_page'] + 1,
                                      size=(34, 34),
                                      hotkey=[21])

        buttons.draw_image_button((150, 135),
                                  button_name='outside_clan',
                                  text='Cats Outside Clans',
                                  size=(34, 34),
                                  cur_screen='other screen')
        buttons.draw_image_button((116, 135),
                                  button_name='your_clan',
                                  text='your clan',
                                  size=(34, 34),
                                  available=False,
                                  cur_screen='other screen')

        draw_menu_buttons()

    def screen_switches(self):
        cat_profiles()

class AllegiancesScreen(Screens):

    def on_use(self):
        draw_clan_name()

        verdana_big.text(f'{game.clan.name}Clan Allegiances', (30, 110))
        a = 0
        if game.allegiance_list is not None and game.allegiance_list != []:
            for x in range(
                    min(len(game.allegiance_list),
                        game.max_allegiance_displayed)):
                if game.allegiance_list[x] is None:
                    continue
                verdana.text(game.allegiance_list[x][0], (30, 140 + a * 30))
                verdana.text(game.allegiance_list[x][1], (170, 140 + a * 30))
                a += 1
        if len(game.allegiance_list) > game.max_allegiance_displayed:
            buttons.draw_button((726, 120),
                                image=game.up,
                                arrow="UP",
                                hotkey=[20])
            buttons.draw_button((726, 600),
                                image=game.down,
                                arrow="DOWN",
                                hotkey=[22])
        draw_menu_buttons()

    def screen_switches(self):
        living_cats = []
        game.allegiance_scroll_ct = 0
        game.allegiance_list = []
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if not the_cat.dead and not the_cat.exiled:
                living_cats.append(the_cat)
        if game.clan.leader is not None:
            if not game.clan.leader.dead and not game.clan.leader.exiled:
                game.allegiance_list.append([
                    'LEADER:',
                    f"{str(game.clan.leader.name)} - a {game.clan.leader.describe_cat()}"
                ])

                if len(game.clan.leader.apprentice) > 0:
                    if len(game.clan.leader.apprentice) == 1:
                        game.allegiance_list.append([
                            '', '      Apprentice: ' +
                            str(game.clan.leader.apprentice[0].name)
                        ])
                    else:
                        app_names = ''
                        for app in game.clan.leader.apprentice:
                            app_names += str(app.name) + ', '
                        game.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        if game.clan.deputy != 0 and game.clan.deputy is not None and not game.clan.deputy.dead and not game.clan.deputy.exiled:
            game.allegiance_list.append([
                'DEPUTY:',
                f"{str(game.clan.deputy.name)} - a {game.clan.deputy.describe_cat()}"
            ])

            if len(game.clan.deputy.apprentice) > 0:
                if len(game.clan.deputy.apprentice) == 1:
                    game.allegiance_list.append([
                        '', '      Apprentice: ' +
                        str(game.clan.deputy.apprentice[0].name)
                    ])
                else:
                    app_names = ''
                    for app in game.clan.deputy.apprentice:
                        app_names += str(app.name) + ', '
                    game.allegiance_list.append(
                        ['', '      Apprentices: ' + app_names[:-2]])
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'medicine cat', 'MEDICINE CAT:')
        queens = []
        for living_cat_ in living_cats:
            if str(living_cat_.status
                   ) == 'kitten' and living_cat_.parent1 is not None:
                if Cat.all_cats[living_cat_.parent1].gender == 'male':
                    if living_cat_.parent2 is None or Cat.all_cats[
                            living_cat_.parent2].gender == 'male':
                        queens.append(living_cat_.parent1)
                else:
                    queens.append(living_cat_.parent1)
        cat_count = 0
        for living_cat__ in living_cats:
            if str(
                    living_cat__.status
            ) == 'warrior' and living_cat__.ID not in queens and not living_cat__.exiled:
                if not cat_count:
                    game.allegiance_list.append([
                        'WARRIORS:',
                        f"{str(living_cat__.name)} - a {living_cat__.describe_cat()}"
                    ])
                else:
                    game.allegiance_list.append([
                        '',
                        f"{str(living_cat__.name)} - a {living_cat__.describe_cat()}"
                    ])
                if len(living_cat__.apprentice) >= 1:
                    if len(living_cat__.apprentice) == 1:
                        game.allegiance_list.append([
                            '', '      Apprentice: ' +
                            str(living_cat__.apprentice[0].name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat__.apprentice:
                            app_names += str(app.name) + ', '
                        game.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['WARRIORS:', ''])
        cat_count = 0
        for living_cat___ in living_cats:
            if str(living_cat___.status) in [
                    'apprentice', 'medicine cat apprentice'
            ]:
                if cat_count == 0:
                    game.allegiance_list.append([
                        'APPRENTICES:',
                        f"{str(living_cat___.name)} - a {living_cat___.describe_cat()}"
                    ])
                else:
                    game.allegiance_list.append([
                        '',
                        f"{str(living_cat___.name)} - a {living_cat___.describe_cat()}"
                    ])
                cat_count += 1
        if not cat_count:
            game.allegiance_list.append(['APPRENTICES:', ''])
        cat_count = 0
        for living_cat____ in living_cats:
            if living_cat____.ID in queens:
                if cat_count == 0:
                    game.allegiance_list.append([
                        'QUEENS:',
                        f"{str(living_cat____.name)} - a {living_cat____.describe_cat()}"
                    ])
                else:
                    game.allegiance_list.append([
                        '',
                        f"{str(living_cat____.name)} - a {living_cat____.describe_cat()}"
                    ])
                cat_count += 1
                if len(living_cat____.apprentice) > 0:
                    if len(living_cat____.apprentice) == 1:
                        game.allegiance_list.append([
                            '', '      Apprentice: ' +
                            str(living_cat____.apprentice[0].name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat____.apprentice:
                            app_names += str(app.name) + ', '
                        game.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        if not cat_count:
            game.allegiance_list.append(['QUEENS:', ''])
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'elder', 'ELDERS:')
        cat_count = self._extracted_from_screen_switches_24(
            living_cats, 'kitten', 'KITS:')

        draw_menu_buttons()

    # TODO Rename this here and in `screen_switches`
    def _extracted_from_screen_switches_24(self, living_cats, arg1, arg2):
        result = 0
        for living_cat in living_cats:
            if str(living_cat.status) == arg1 and not living_cat.exiled:
                if result == 0:
                    game.allegiance_list.append([
                        arg2,
                        f"{str(living_cat.name)} - a {living_cat.describe_cat()}"
                    ])
                else:
                    game.allegiance_list.append([
                        "",
                        f"{str(living_cat.name)} - a {living_cat.describe_cat()}"
                    ])
                result += 1
                if len(living_cat.apprentice) > 0:
                    if len(living_cat.apprentice) == 1:
                        game.allegiance_list.append([
                            '', '      Apprentice: ' +
                            str(living_cat.apprentice[0].name)
                        ])
                    else:
                        app_names = ''
                        for app in living_cat.apprentice:
                            app_names += str(app.name) + ', '
                        game.allegiance_list.append(
                            ['', '      Apprentices: ' + app_names[:-2]])
        if not result:
            game.allegiance_list.append([arg2, ''])
        return result

# template for dark forest
class DFScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.df_bg = pygame.transform.scale(
            pygame.image.load("resources/images/darkforestbg.png").convert(),
            (800, 700))
        self.search_bar = pygame.transform.scale(
            pygame.image.load("resources/images/search_bar.png").convert_alpha(), (228, 34))
        self.clan_name_bg = pygame.transform.scale(
            image_cache.load_image("resources/images/clan_name_bg.png").convert_alpha(), (180, 35))
    def on_use(self):
        bg = self.df_bg
        screen.blit(bg, (0, 0))

        screen.blit(self.clan_name_bg, (310, 25))

        verdana_big_light.text(f'Dark Forest', ('center', 32))

        dead_cats = []
        for x in range(len(Cat.all_cats.values())):
            the_cat = list(Cat.all_cats.values())[x]
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.exiled and the_cat.df:
                dead_cats.append(the_cat)

        search_text = game.switches['search_text']
        screen.blit(self.search_bar, (452, 135))
        verdana_black.text(game.switches['search_text'], (530, 142))
        search_cats = []
        if search_text.strip() != '':
            for cat in dead_cats:
                if search_text.lower() in str(cat.name).lower():
                    search_cats.append(cat)
        else:
            search_cats = dead_cats.copy()
        all_pages = int(ceil(len(search_cats) /
                             20.0)) if len(search_cats) > 20 else 1
        pos_x = 0
        pos_y = 0
        cats_on_page = 0
        for x in range(len(search_cats)):
            if x + (game.switches['list_page'] - 1) * 20 > len(search_cats):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            the_cat = search_cats[x + (game.switches['list_page'] - 1) * 20]
            if the_cat.dead:
                column = int(pos_x / 100)
                row = int(pos_y / 100)
                buttons.draw_button((130 + pos_x, 180 + pos_y),
                                    image=the_cat.sprite,
                                    cat=the_cat.ID,
                                    cur_screen='profile screen',
                                    hotkey=[row + 1, column + 11])

                name_len = verdana.text(str(the_cat.name))

                # CHECK NAME LENGTH
                name = str(the_cat.name)
                if len(name) >= 13:
                    short_name = str(the_cat.name)[0:12]
                    name = short_name + '...'

                # DISPLAY NAME
                verdana_red.text(name,
                                   (155 + pos_x - name_len/2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 120
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100
                if cats_on_page >= 20 or x + (game.switches['list_page'] -
                                              1) * 20 == len(search_cats) - 1:
                    break
        verdana_white.text(
            'page ' + str(game.switches['list_page']) + ' / ' + str(all_pages),
            ('center', 600))

        if game.switches['list_page'] > 1:
            buttons.draw_image_button((310, 595),
                                      button_name='arrow_left',
                                      text='<',
                                      list_page=game.switches['list_page'] - 1,
                                      size=(34, 34),
                                      hotkey=[23])

        if game.switches['list_page'] < all_pages:
            buttons.draw_image_button((456, 595),
                                      button_name='arrow_right',
                                      text='>',
                                      list_page=game.switches['list_page'] + 1,
                                      size=(34, 34),
                                      hotkey=[21])

        draw_menu_buttons()



        buttons.draw_image_button((150, 135),
                                  button_name='sc_toggle',
                                  text='SC',
                                  size=(34, 34),
                                  cur_screen='starclan screen',
                                  )
        buttons.draw_image_button((116, 135),
                                  button_name='df_toggle',
                                  text='DF',
                                  size=(34, 34),
                                  cur_screen='dark forest screen',
                                  available=False,
                                  )


    # def screen_switches(self):
    #     cat_profiles()