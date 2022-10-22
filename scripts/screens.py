from importlib import invalidate_caches
from re import T
from .clan import *
from .events import *
from .patrol import *
if mapavailable:
    from .world import *

import random

random.seed()


# SCREENS PARENT CLASS
class Screens(object):
    game_screen = screen
    game_x = screen_x
    game_y = screen_y
    all_screens = {}
    last_screen = ''

    def __init__(self, name=None):
        self.name = name
        if name is not None:
            self.all_screens[name] = self
            game.all_screens[name] = self

    def on_use(self):
        """Runs every frame this screen is used."""
        pass

    def screen_switches(self):
        """Runs when this screen is switched to."""
        pass


# SCREEN CHILD CLASSES
class StartScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.bg = pygame.image.load("resources/menu.png").convert()

    def on_use(self):
        # background
        screen.blit(self.bg, (0, 0))

        # buttons
        if game.clan is not None and game.switches['error_message'] == '':
            buttons.draw_image_button((70, 310),
                                      path='continue',
                                      text='Continue >',
                                      cur_screen='clan screen')
            buttons.draw_image_button((70, 355),
                                      path='switch_clan',
                                      text='Switch Clan >',
                                      cur_screen='switch clan screen')
        elif game.clan is not None and game.switches['error_message']:
            buttons.draw_image_button((70, 310),
                                      path='continue',
                                      text='Continue >',
                                      available=False)
            buttons.draw_image_button((70, 355),
                                      path='switch_clan',
                                      text='Switch Clan >',
                                      cur_screen='switch clan screen')
        else:
            buttons.draw_image_button((70, 310),
                                      path='continue',
                                      text='Continue >',
                                      available=False)
            buttons.draw_image_button((70, 355),
                                      path='switch_clan',
                                      text='Switch Clan >',
                                      available=False)
        buttons.draw_image_button((70, 400),
                                  path='new_clan',
                                  text='Make New >',
                                  cur_screen='make clan screen')
        buttons.draw_image_button((70, 445),
                                  path='settings',
                                  text='Settings & Info >',
                                  cur_screen='settings screen')

        if game.switches['error_message']:
            buttons.draw_button((50, 50),
                                text='There was an error loading the game:',
                                available=False)
            buttons.draw_button((50, 80),
                                text=game.switches['error_message'],
                                available=False)

    def screen_switches(self):
        if game.clan is not None:
            key_copy = tuple(cat_class.all_cats.keys())
            for x in key_copy:
                if x not in game.clan.clan_cats:
                    game.clan.remove_cat(x)

        # SAVE cats
        if game.clan is not None:
            cat_class.json_save_cats()
            game.clan.save_clan()
            if mapavailable:
                save_map(game.map_info, game.clan.name)

        # LOAD settings
        game.load_settings()


class SwitchClanScreen(Screens):

    def on_use(self):
        verdana_big.text('Switch Clan:', ('center', 100))
        verdana.text(
            'Note: this will close the game. When you open it next, it should have the new clan.',
            ('center', 150))
        game.switches['read_clans'] = True

        y_pos = 200

        for i in range(len(game.switches['clan_list'])):
            if len(game.switches['clan_list'][i]) > 1 and i < 9:
                buttons.draw_button(
                    ('center', 50 * i + y_pos),
                    text=game.switches['clan_list'][i] + 'clan',
                    switch_clan=game.switches['clan_list'][i],
                    hotkey=[i + 1])

        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            hotkey=[0])


class SettingsScreen(Screens):
    text_size = {
        '0': 'small',
        '1': 'medium',
        '2': 'big'
    }  # How text sizes will show up on the screen
    bool = {True: 'Yes', False: 'No', None: 'None'}

    def on_use(self):
        # layout
        buttons.draw_button((244, 100), text='Settings', available=False)
        buttons.draw_button((-210, 100), text='Info', cur_screen='info screen')
        buttons.draw_button((-255, 100),
                            text='Language',
                            cur_screen='language screen')
        buttons.draw_button((320, 100),
                            text='Relation Settings',
                            cur_screen='relationsihp setting screen')
        verdana.text("Change the setting of your game here.", ('center', 130))

        # Setting names
        verdana.text("Dark mode:", (100, 200))
        verdana.text("Enable clan page background:", (100, 230))
        verdana.text("Automatically save every five moons:", (100, 260))
        verdana.text("Allow mass extinction events:", (100, 290))
        verdana.text("Force cats to retire after severe injury:", (100, 320))
        verdana.text("Enable shaders:", (100, 350))
        verdana.text("Display hotkeys on text buttons:", (100, 380))

        # Setting values
        verdana.text(self.bool[game.settings['dark mode']], (-170, 200))
        buttons.draw_button((-80, 200), text='SWITCH', setting='dark mode')
        verdana.text(self.bool[game.settings['backgrounds']], (-170, 230))
        buttons.draw_button((-80, 230), text='SWITCH', setting='backgrounds')
        verdana.text(self.bool[game.settings['autosave']], (-170, 260))
        buttons.draw_button((-80, 260), text='SWITCH', setting='autosave')
        verdana.text(self.bool[game.settings['disasters']], (-170, 290))
        buttons.draw_button((-80, 290), text='SWITCH', setting='disasters')
        verdana.text(self.bool[game.settings['retirement']], (-170, 320))
        buttons.draw_button((-80, 320), text='SWITCH', setting='retirement')
        verdana.text(self.bool[game.settings['shaders']], (-170, 350))
        buttons.draw_button((-80, 350), text='SWITCH', setting='shaders')
        verdana.text(self.bool[game.settings['hotkey display']], (-170, 380))
        buttons.draw_button((-80, 380),
                            text='SWITCH',
                            setting='hotkey display')

        # other buttons
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen')
        if game.settings_changed:
            buttons.draw_button(('center', -130),
                                text='Save Settings',
                                save_settings=True)
        else:
            buttons.draw_button(('center', -130),
                                text='Save Settings',
                                available=False)


class RelationshipSettingsScreen(Screens):
    text_size = {
        '0': 'small',
        '1': 'medium',
        '2': 'big'
    }  # How text sizes will show up on the screen
    bool = {True: 'Yes', False: 'No', None: 'None'}

    def on_use(self):
        # layout
        buttons.draw_button((244, 100),
                            text='Settings',
                            cur_screen='settings screen')
        buttons.draw_button((-210, 100), text='Info', cur_screen='info screen')
        buttons.draw_button((-255, 100),
                            text='Language',
                            cur_screen='language screen')
        buttons.draw_button((320, 100),
                            text='Relation Settings',
                            available=False)
        verdana.text("Change the setting of the relationships here.",
                     ('center', 130))

        # Setting names
        verdana.text("Randomize relationship values, when creating clan:",
                     (100, 200))
        verdana.text("Allow affairs and mate switches based on relationships:",
                     (100, 230))
        verdana.text("Allow couples to have kittens despite same-sex status:",
                     (100, 260))
        verdana.text("Allow unmated cats to have offspring:", (100, 290))
        verdana.text(
            "Allow romantic interactions with former apprentices/mentor:",
            (100, 320))

        # Setting values
        verdana.text(self.bool[game.settings['random relation']], (-170, 200))
        buttons.draw_button((-80, 200),
                            text='SWITCH',
                            setting='random relation')
        verdana.text(self.bool[game.settings['affair']], (-170, 230))
        buttons.draw_button((-80, 230), text='SWITCH', setting='affair')
        verdana.text(self.bool[game.settings['no gendered breeding']],
                     (-170, 260))
        buttons.draw_button((-80, 260),
                            text='SWITCH',
                            setting='no gendered breeding')
        verdana.text(self.bool[game.settings['no unknown fathers']],
                     (-170, 290))
        buttons.draw_button((-80, 290),
                            text='SWITCH',
                            setting='no unknown fathers')
        verdana.text(self.bool[game.settings['romantic with former mentor']],
                     (-170, 320))
        buttons.draw_button((-80, 320),
                            text='SWITCH',
                            setting='romantic with former mentor')

        # other buttons
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen')
        if game.settings_changed:
            buttons.draw_button(('center', -130),
                                text='Save Settings',
                                save_settings=True)
        else:
            buttons.draw_button(('center', -130),
                                text='Save Settings',
                                available=False)


class InfoScreen(Screens):

    def on_use(self):
        # layout
        buttons.draw_button((244, 100),
                            text='Settings',
                            cur_screen='settings screen')
        buttons.draw_button((-210, 100), text='Info', available=False)
        buttons.draw_button((-255, 100),
                            text='Language',
                            cur_screen='language screen')
        buttons.draw_button((320, 100),
                            text='Relation Settings',
                            cur_screen='relationsihp setting screen')

        verdana.text("Welcome to Warrior Cats clan generator!",
                     ('center', 140))
        verdana.text(
            "This is fan-made generator for the Warrior Cats -book series by Erin Hunter.",
            ('center', 175))
        verdana.text(
            "Create a new clan in the 'Make New' section. That clan is saved and can be",
            ('center', 195))
        verdana.text(
            "revisited until you decide the overwrite it with a new one.",
            ('center', 215))
        verdana.text(
            "You're free to use the characters and sprites generated in this program",
            ('center', 235))
        verdana.text(
            "as you like, as long as you don't claim the sprites as your own creations.",
            ('center', 255))
        verdana.text("Original creator: just-some-cat.tumblr.com",
                     ('center', 275))
        verdana.text("Fan edit made by: SableSteel", ('center', 295))

        verdana.text("Thank you for playing!!", ('center', 550))

        # other buttons
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen')


class LanguageScreen(Screens):

    def on_use(self):
        # layout
        buttons.draw_button((244, 100),
                            text='Settings',
                            cur_screen='settings screen')
        buttons.draw_button((-210, 100), text='Info', cur_screen='info screen')
        buttons.draw_button((-255, 100), text='Language', available=False)
        buttons.draw_button((320, 100),
                            text='Relation Settings',
                            cur_screen='relationsihp setting screen')
        verdana.text("Choose the language of your game here:", ('center', 130))

        # Language options
        a = 200
        for language_name in game.language_list:
            buttons.draw_button(
                ('center', a),
                text=language_name,
                language=language_name,
                available=language_name != game.switches['language'])
            a += 30

        if game.switches['language'] != game.settings['language']:
            game.settings['language'] = game.switches['language']
            game.settings_changed = True
            if game.settings['language'] != 'english':
                game.switch_language()

        # other buttons
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen')
        if game.settings_changed:
            buttons.draw_button(('center', -150),
                                text='Save Settings',
                                save_settings=True)
        else:
            buttons.draw_button(('center', -150),
                                text='Save Settings',
                                available=False)


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
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
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
            if not cat_class.all_cats[x].dead and cat_class.all_cats[
                    x].in_camp and not cat_class.all_cats[x].exiled:
                buttons.draw_button(cat_class.all_cats[x].placement,
                                    image=cat_class.all_cats[x].sprite,
                                    cat=x,
                                    cur_screen='profile screen',
                                    hotkey=[hotkey_assign_1, hotkey_assign_2])
                hotkey_assign_2 = hotkey_assign_2 + 1
                if hotkey_assign_2 == 20:
                    hotkey_assign_1 = hotkey_assign_1 + 1
                    hotkey_assign_2 = hotkey_assign_1 + 1
        draw_menu_buttons()
        buttons.draw_button(('center', -50),
                            text='Save Clan',
                            save_clan=True,
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
        self.change_brightness()
        game.switches['cat'] = None
        p = game.clan.cur_layout
        game.clan.leader.placement = choice(p['leader place'])
        game.clan.medicine_cat.placement = choice(p['medicine place'])
        for x in game.clan.clan_cats:
            i = randint(0, 20)
            if cat_class.all_cats[x].status == 'apprentice':
                if i < 13:
                    cat_class.all_cats[x].placement = choice([
                        choice(p['apprentice place']),
                        choice(p['clearing place'])
                    ])

                elif i >= 19:
                    cat_class.all_cats[x].placement = choice(p['leader place'])
                else:
                    cat_class.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['warrior place']),
                        choice(p['elder place']),
                        choice(p['medicine place'])
                    ])

            elif cat_class.all_cats[x].status == 'deputy':
                if i < 17:
                    cat_class.all_cats[x].placement = choice([
                        choice(p['warrior place']),
                        choice(p['leader place']),
                        choice(p['clearing place'])
                    ])

                else:
                    cat_class.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['leader place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

            elif cat_class.all_cats[x].status == 'elder':
                cat_class.all_cats[x].placement = choice(p['elder place'])
            elif cat_class.all_cats[x].status == 'kitten':
                if i < 13:
                    cat_class.all_cats[x].placement = choice(
                        p['nursery place'])
                elif i == 19:
                    cat_class.all_cats[x].placement = choice(p['leader place'])
                else:
                    cat_class.all_cats[x].placement = choice([
                        choice(p['clearing place']),
                        choice(p['warrior place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

            elif cat_class.all_cats[x].status in [
                    'medicine cat apprentice', 'medicine cat'
            ]:
                cat_class.all_cats[x].placement = choice(p['medicine place'])
            elif cat_class.all_cats[x].status == 'warrior':
                if i < 15:
                    cat_class.all_cats[x].placement = choice([
                        choice(p['warrior place']),
                        choice(p['clearing place'])
                    ])

                else:
                    cat_class.all_cats[x].placement = choice([
                        choice(p['nursery place']),
                        choice(p['leader place']),
                        choice(p['elder place']),
                        choice(p['medicine place']),
                        choice(p['apprentice place'])
                    ])

    def change_brightness(self):
        if game.settings['dark mode']:
            if game.clan.biome == "Forest":
                self._extracted_from_change_brightness_3(
                    'resources/greenleafcamp_dark.png',
                    'resources/newleafcamp_dark.png',
                    'resources/leafbarecamp_dark.png',
                    'resources/leaffallcamp_dark.png')
            elif game.clan.biome == "Plains":
                try:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_plains_dark.png',
                        'resources/newleafcamp_plains_dark.png',
                        'resources/leafbarecamp_plains_dark.png',
                        'resources/leaffallcamp_plains_dark.png')
                except:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_dark.png',
                        'resources/newleafcamp_dark.png',
                        'resources/leafbarecamp_dark.png',
                        'resources/leaffallcamp_dark.png')
            elif game.clan.biome == "Beach":
                try:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_beach_dark.png',
                        'resources/newleafcamp_beach_dark.png',
                        'resources/leafbarecamp_beach_dark.png',
                        'resources/leaffallcamp_beach_dark.png')
                except:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_dark.png',
                        'resources/newleafcamp_dark.png',
                        'resources/leafbarecamp_dark.png',
                        'resources/leaffallcamp_dark.png')
            elif game.clan.biome == "Mountainous":
                try:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_mountain_dark.png',
                        'resources/newleafcamp_mountain_dark.png',
                        'resources/leafbarecamp_mountain_dark.png',
                        'resources/leaffallcamp_mountain_dark.png')
                except:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_dark.png',
                        'resources/newleafcamp_dark.png',
                        'resources/leafbarecamp_dark.png',
                        'resources/leaffallcamp_dark.png')
            elif game.clan.biome == "Desert":
                try:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_desert_dark.png',
                        'resources/newleafcamp_desert_dark.png',
                        'resources/leafbarecamp_desert_dark.png',
                        'resources/leaffallcamp_desert_dark.png')
                except:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_dark.png',
                        'resources/newleafcamp_dark.png',
                        'resources/leafbarecamp_dark.png',
                        'resources/leaffallcamp_dark.png')
            else:
                self._extracted_from_change_brightness_3(
                    'resources/greenleafcamp_dark.png',
                    'resources/newleafcamp_dark.png',
                    'resources/leafbarecamp_dark.png',
                    'resources/leaffallcamp_dark.png')

        else:
            if game.clan.biome == "Forest":
                self._extracted_from_change_brightness_3(
                    'resources/greenleafcamp.png', 'resources/newleafcamp.png',
                    'resources/leafbarecamp.png', 'resources/leaffallcamp.png')
            elif game.clan.biome == "Plains":
                self._extracted_from_change_brightness_3(
                    'resources/greenleafcamp_plains.png',
                    'resources/newleafcamp_plains.png',
                    'resources/leafbarecamp_plains.png',
                    'resources/leaffallcamp_plains.png')
            elif game.clan.biome == "Beach":
                try:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_beach.png',
                        'resources/newleafcamp_beach.png',
                        'resources/leafbarecamp_beach.png',
                        'resources/leaffallcamp_beach.png')
                except:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp.png',
                        'resources/newleafcamp.png',
                        'resources/leafbarecamp.png',
                        'resources/leaffallcamp.png')
            elif game.clan.biome == "Mountainous":
                try:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_mountain.png',
                        'resources/newleafcamp_mountain.png',
                        'resources/leafbarecamp_mountain.png',
                        'resources/leaffallcamp_mountain.png')
                except:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp.png',
                        'resources/newleafcamp.png',
                        'resources/leafbarecamp.png',
                        'resources/leaffallcamp.png')
            elif game.clan.biome == "Desert":
                try:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp_desert.png',
                        'resources/newleafcamp_desert.png',
                        'resources/leafbarecamp_desert.png',
                        'resources/leaffallcamp_desert.png')
                except:
                    self._extracted_from_change_brightness_3(
                        'resources/greenleafcamp.png',
                        'resources/newleafcamp.png',
                        'resources/leafbarecamp.png',
                        'resources/leaffallcamp.png')
            else:
                self._extracted_from_change_brightness_3(
                    'resources/greenleafcamp.png', 'resources/newleafcamp.png',
                    'resources/leafbarecamp.png', 'resources/leaffallcamp.png')

    # TODO Rename this here and in `change_brightness`
    def _extracted_from_change_brightness_3(self, arg0, arg1, arg2, arg3):
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(arg0).convert(), (800, 700))
        self.newleaf_bg = pygame.transform.scale(
            pygame.image.load(arg1).convert(), (800, 700))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(arg2).convert(), (800, 700))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(arg3).convert(), (800, 700))


class StarClanScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.starclan_bg = pygame.transform.scale(
            pygame.image.load("resources/starclanbg.png").convert(),
            (800, 700))

    def on_use(self):
        bg = self.starclan_bg
        screen.blit(bg, (0, 0))
        verdana_big_white.text(f'{game.clan.name}Clan', ('center', 30))
        verdana_white.text('StarClan Cat List', ('center', 100))
        dead_cats = [game.clan.instructor]
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if the_cat.dead and the_cat.ID != game.clan.instructor.ID and not the_cat.exiled:
                dead_cats.append(the_cat)

        search_text = game.switches['search_text']
        pygame.draw.rect(screen, 'lightgray', pygame.Rect((170, 130),
                                                          (150, 20)))
        verdana_white.text('Search: ', (100, 130))
        verdana_black.text(game.switches['search_text'], (180, 130))
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
                verdana_white.text(str(the_cat.name),
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
            buttons.draw_button((300, 600),
                                text='<',
                                list_page=game.switches['list_page'] - 1,
                                hotkey=[23])

        if game.switches['list_page'] < all_pages:
            buttons.draw_button((-300, 600),
                                text='>',
                                list_page=game.switches['list_page'] + 1,
                                hotkey=[21])

        draw_menu_buttons()

    def screen_switches(self):
        cat_profiles()


class MakeClanScreen(Screens):

    def first_phase(self):
        # layout
        if game.settings['dark mode']:
            name_clan_img = pygame.image.load(
                'resources/name_clan.png').convert_alpha()
        else:
            name_clan_img = pygame.image.load(
                'resources/name_clan_light.png').convert_alpha()
        screen.blit(name_clan_img, (0, 0))

        self.game_screen.blit(game.naming_box, (150, 620))
        if game.settings['dark mode']:
            verdana_black.text(game.switches['naming_text'], (155, 620))
        else:
            verdana.text(game.switches['naming_text'], (155, 620))
        verdana.text('-Clan', (290, 620))
        buttons.draw_button((350, 620),
                            text='Randomize',
                            naming_text=choice(names.normal_prefixes),
                            hotkey=[1])
        buttons.draw_button((450, 620),
                            text='Reset Name',
                            naming_text='',
                            hotkey=[2])

        # buttons
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (50, 25))
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')
        buttons.draw_button((570, 620),
                            text='Name Clan',
                            clan_name=game.switches['naming_text'],
                            hotkey=[3])

    def second_phase(self):
        game.switches['naming_text'] = ''
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            leader_img = pygame.image.load(
                'resources/leader.png').convert_alpha()
        else:
            leader_img = pygame.image.load(
                'resources/leader_light.png').convert_alpha()
        screen.blit(leader_img, (0, 400))
        for u in range(6):
            buttons.draw_button((50, 150 + 50 * u),
                                image=game.choose_cats[u].sprite,
                                cat=u,
                                hotkey=[1, u + 10])
        for u in range(6, 12):
            buttons.draw_button((100, 150 + 50 * (u - 6)),
                                image=game.choose_cats[u].sprite,
                                cat=u,
                                hotkey=[2, u + 4])

        if game.switches['cat'] is not None and 12 > game.switches['cat'] >= 0:
            game.choose_cats[game.switches['cat']].draw_large((250, 200))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana.text(str(game.choose_cats[game.switches['cat']].name),
                             (420, 200))
            else:
                verdana.text(
                    str(game.choose_cats[game.switches['cat']].name) +
                    ' --> ' +
                    game.choose_cats[game.switches['cat']].name.prefix +
                    'star', (420, 200))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (420, 245))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become leader.', (420, 300))
            else:
                buttons.draw_button((420, 300),
                                    text='Grant this cat their nine lives',
                                    leader=game.switches['cat'],
                                    hotkey=[1])
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')

        buttons.draw_button((-50, 50),
                            text='< Last step',
                            clan_name='',
                            cat=None,
                            hotkey=[0])

    def third_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            deputy_img = pygame.image.load(
                'resources/deputy.png').convert_alpha()
        else:
            deputy_img = pygame.image.load(
                'resources/deputy_light.png').convert_alpha()
        screen.blit(deputy_img, (0, 400))

        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            else:
                buttons.draw_button((50, 150 + 50 * u),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[1, u + 10])
        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            else:
                buttons.draw_button((100, 150 + 50 * (u - 6)),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[2, u + 4])

        if game.switches['cat'] is not None and 12 > game.switches[
                'cat'] >= 0 and game.switches['cat'] != game.switches['leader']:
            game.choose_cats[game.switches['cat']].draw_large((250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name),
                         (420, 200))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (420, 245))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become deputy.', (420, 300))
            else:
                buttons.draw_button((420, 300),
                                    text='This cat will support the leader',
                                    deputy=game.switches['cat'],
                                    hotkey=[1])
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (50, 25))

        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')
        buttons.draw_button((-50, 50),
                            text='< Last Step',
                            leader=None,
                            cat=None,
                            hotkey=[0])

    def fourth_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            medic_img = pygame.image.load(
                'resources/medic.png').convert_alpha()
        else:
            medic_img = pygame.image.load(
                'resources/med_light.png').convert_alpha()
        screen.blit(medic_img, (0, 400))

        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((650, 250))
            else:
                buttons.draw_button((50, 150 + 50 * u),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[1, u + 10])

        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((650, 250))
            else:
                buttons.draw_button((100, 150 + 50 * (u - 6)),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[2, u + 4])

        if game.switches['cat'] is not None and 12 > game.switches[
                'cat'] >= 0 and game.switches['cat'] != game.switches[
                    'leader'] and game.switches['cat'] != game.switches[
                        'deputy']:
            game.choose_cats[game.switches['cat']].draw_large((250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name),
                         (420, 200))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (420, 245))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if game.choose_cats[game.switches['cat']].age in [
                    'kitten', 'adolescent'
            ]:
                verdana_red.text('Too young to become medicine cat.',
                                 (420, 300))
            else:
                buttons.draw_button((420, 300),
                                    text='This cat will aid the clan',
                                    medicine_cat=game.switches['cat'],
                                    hotkey=[1])
        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (50, 25))
        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')
        buttons.draw_button((-50, 50),
                            text='< Last step',
                            deputy=None,
                            cat=None,
                            hotkey=[0])

    def fifth_phase(self):
        verdana.text(game.switches['clan_name'] + 'Clan', ('center', 90))
        if game.settings['dark mode']:
            clan_img = pygame.image.load('resources/clan.png').convert_alpha()
        else:
            clan_img = pygame.image.load(
                'resources/clan_light.png').convert_alpha()
        screen.blit(clan_img, (0, 400))
        for u in range(6):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((650, 250))
            elif game.switches['medicine_cat'] == u:
                game.choose_cats[u].draw((650, 300))
            elif u not in game.switches['members']:
                buttons.draw_button((50, 150 + 50 * u),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[1, u + 10])
            try:
                if u == game.switches['members'][0]:
                    game.choose_cats[u].draw((700, 100))
                elif u == game.switches['members'][1]:
                    game.choose_cats[u].draw((700, 150))
                elif u == game.switches['members'][2]:
                    game.choose_cats[u].draw((700, 200))
                elif u == game.switches['members'][3]:
                    game.choose_cats[u].draw((700, 250))
                elif u == game.switches['members'][4]:
                    game.choose_cats[u].draw((700, 300))
                elif u == game.switches['members'][5]:
                    game.choose_cats[u].draw((700, 350))
                elif u == game.switches['members'][6]:
                    game.choose_cats[u].draw((700, 400))
            except IndexError:
                pass

        for u in range(6, 12):
            if game.switches['leader'] == u:
                game.choose_cats[u].draw((650, 200))
            elif game.switches['deputy'] == u:
                game.choose_cats[u].draw((650, 250))
            elif game.switches['medicine_cat'] == u:
                game.choose_cats[u].draw((650, 300))
            elif u not in game.switches['members']:
                buttons.draw_button((100, 150 + 50 * (u - 6)),
                                    image=game.choose_cats[u].sprite,
                                    cat=u,
                                    hotkey=[2, u + 4])
            try:
                if u == game.switches['members'][0]:
                    game.choose_cats[u].draw((700, 100))
                elif u == game.switches['members'][1]:
                    game.choose_cats[u].draw((700, 150))
                elif u == game.switches['members'][2]:
                    game.choose_cats[u].draw((700, 200))
                elif u == game.switches['members'][3]:
                    game.choose_cats[u].draw((700, 250))
                elif u == game.switches['members'][4]:
                    game.choose_cats[u].draw((700, 300))
                elif u == game.switches['members'][5]:
                    game.choose_cats[u].draw((700, 350))
                elif u == game.switches['members'][6]:
                    game.choose_cats[u].draw((700, 400))
            except IndexError:
                pass

        if 12 > game.switches['cat'] >= 0 and game.switches['cat'] not in [
                game.switches['leader'], game.switches['deputy'],
                game.switches['medicine_cat']
        ] and game.switches['cat'] not in game.switches['members']:
            game.choose_cats[game.switches['cat']].draw_large((250, 200))
            verdana.text(str(game.choose_cats[game.switches['cat']].name),
                         (420, 200))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].gender), (420, 230))
            verdana_small.text(str(game.choose_cats[game.switches['cat']].age),
                               (420, 245))
            verdana_small.text(
                str(game.choose_cats[game.switches['cat']].trait), (420, 260))
            if len(game.switches['members']) < 7:
                buttons.draw_button((420, 300),
                                    text='Recruit',
                                    members=game.switches['cat'],
                                    add=True,
                                    hotkey=[1])

        verdana_small.text(
            'Note: going back to main menu resets the generated cats.',
            (50, 25))

        buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen',
                            naming_text='')

        buttons.draw_button((-50, 50),
                            text='< Last step',
                            medicine_cat=None,
                            members=[],
                            cat=None,
                            hotkey=[0])

        if 3 < len(game.switches['members']) < 8:
            buttons.draw_button(('center', 350),
                                text='Done',
                                choosing_camp=True,
                                hotkey=[2])
        else:
            buttons.draw_button(('center', 350), text='Done', available=False)

    def sixth_phase(self):
        if mapavailable:
            for y in range(44):
                for x in range(40):
                    noisevalue = self.world.check_noisetile(x, y)
                    if noisevalue > 0.1:
                        #buttons.draw_maptile_button((x*TILESIZE,y*TILESIZE),image=(pygame.transform.scale(terrain.images[1],(TILESIZE,TILESIZE))))
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain1'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Desert", "Unclaimed",
                            'Twoleg Activity: ' + random.choice([
                                'none', 'low', 'low', 'medium', 'medium',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            random.choice(['none', 'low', 'medium', 'high']),
                            'Prey Levels: ' +
                            random.choice(['none', 'low', 'medium']),
                            'Plant Cover: ' +
                            random.choice(['none', 'low', 'medium'])
                        ]
                    elif noisevalue < -0.015:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain3'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Forest", "Unclaimed",
                            'Twoleg Activity: ' + random.choice(
                                ['none', 'low', 'low', 'medium', 'high']),
                            'Thunderpath Traffic: ' +
                            random.choice(['none', 'low', 'medium']),
                            'Prey Levels: ' +
                            random.choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            random.choice(['low', 'medium', 'high'])
                        ]
                    else:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain0'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Plains", "Unclaimed",
                            'Twoleg Activity: ' + random.choice([
                                'none', 'low', 'medium', 'medium', 'high',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            random.choice(['none', 'low', 'medium', 'high']),
                            'Prey Levels: ' +
                            random.choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            random.choice(['low', 'medium', 'high'])
                        ]
            for y in range(44):
                for x in range(40):
                    height = self.world.check_heighttile(x, y)
                    if height < 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + random.choice(['none']),
                            'Thunderpath Traffic: ' + random.choice(['none']),
                            'Prey Levels: ' + random.choice(['none']),
                            'Plant Cover: ' + random.choice(['none'])
                        ]
                    elif x == 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + random.choice(['none']),
                            'Thunderpath Traffic: ' + random.choice(['none']),
                            'Prey Levels: ' + random.choice(['none']),
                            'Plant Cover: ' + random.choice(['none'])
                        ]
                    elif x == 39:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + random.choice(['none']),
                            'Thunderpath Traffic: ' + random.choice(['none']),
                            'Prey Levels: ' + random.choice(['none']),
                            'Plant Cover: ' + random.choice(['none'])
                        ]
                    elif y == 0:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + random.choice(['none']),
                            'Thunderpath Traffic: ' + random.choice(['none']),
                            'Prey Levels: ' + random.choice(['none']),
                            'Plant Cover: ' + random.choice(['none'])
                        ]
                    elif y == 43:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain2'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Ocean", "Unclaimable",
                            'Twoleg Activity: ' + random.choice(['none']),
                            'Thunderpath Traffic: ' + random.choice(['none']),
                            'Prey Levels: ' + random.choice(['none']),
                            'Plant Cover: ' + random.choice(['none'])
                        ]
                    elif height < 0.03:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain6'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Beach", "Unclaimed",
                            'Twoleg Activity: ' + random.choice([
                                'none', 'low', 'medium', 'medium', 'high',
                                'high'
                            ]), 'Thunderpath Traffic: ' +
                            random.choice(['none', 'low', 'medium']),
                            'Prey Levels: ' +
                            random.choice(['low', 'medium', 'high']),
                            'Plant Cover: ' +
                            random.choice(['none', 'low', 'medium'])
                        ]
                    elif height > 0.35:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terrain5'],
                                                (16, 16)),
                                            map_selection=(x, y))
                        game.map_info[(x, y)] = [
                            x, y, "Mountainous", "Unclaimed",
                            'Twoleg Activity: ' + random.choice([
                                'none', 'none', 'low', 'low', 'medium', 'high'
                            ]), 'Thunderpath Traffic: ' + random.choice([
                                'none', 'none', 'low', 'low', 'medium',
                                'medium', 'high'
                            ]), 'Prey Levels: ' +
                            random.choice(['none', 'low', 'medium', 'high']),
                            'Plant Cover: ' +
                            random.choice(['none', 'low', 'medium', 'high'])
                        ]
                    if (x, y) == game.switches['map_selection']:
                        buttons.draw_button((x * 16, y * 16),
                                            image=pygame.transform.scale(
                                                tiles.sprites['terraintwo0'],
                                                (16, 16)),
                                            camp_site=(x, y))
            verdana_big.text('Map', (-16, 50))
            verdana.text(
                str(game.map_info[game.switches['map_selection']][0]) + ", " +
                str(game.map_info[game.switches['map_selection']][1]),
                (-16, 100))
            verdana.text(str(game.map_info[game.switches['map_selection']][2]),
                         (-16, 150))
            verdana.text(str(game.map_info[game.switches['map_selection']][3]),
                         (-16, 200))
            verdana.text(str(game.switches['camp_site']), (-16, 250))

            if game.map_info[game.switches['map_selection']][3] == 'Unclaimed':
                buttons.draw_button(
                    (-16, 300),
                    text='Done',
                    choosing_camp=False,
                    biome=game.map_info[game.switches['map_selection']][2],
                    world_seed=self.worldseed,
                    cur_screen='clan created screen')
            else:
                buttons.draw_button((-16, 300), text='Done', available=False)
        else:
            buttons.draw_button(('center', 350),
                                text='Done',
                                cur_screen='clan created screen')

            buttons.draw_button((250, 50),
                                text='Forest',
                                biome='Forest',
                                available=game.switches['biome'] != 'Forest',
                                hotkey=[1])
            buttons.draw_button(
                (325, 50),
                text='Mountainous',
                biome='Mountainous',
                available=game.switches['biome'] != 'Mountainous',
                hotkey=[2])
            buttons.draw_button((450, 50),
                                text='Plains',
                                biome='Plains',
                                available=game.switches['biome'] != 'Plains',
                                hotkey=[3])
            buttons.draw_button((525, 50),
                                text='Beach',
                                biome='Beach',
                                available=game.switches['biome'] != 'Beach',
                                hotkey=[4])

    def on_use(self):
        if len(game.switches['clan_name']) == 0:
            self.first_phase()
        elif len(game.switches['clan_name']
                 ) > 0 and game.switches['leader'] is None:
            self.second_phase()
        elif game.switches[
                'leader'] is not None and game.switches['deputy'] is None:
            Clan.leader_lives = 9
            self.third_phase()
        elif game.switches['leader'] is not None and game.switches[
                'medicine_cat'] is None:
            self.fourth_phase()
        elif game.switches['medicine_cat'] is not None and game.switches[
                'choosing_camp'] is False:
            self.fifth_phase()
        else:
            self.sixth_phase()

    def screen_switches(self):
        game.switches['clan_name'] = ''
        game.switches['leader'] = None
        game.switches['cat'] = None
        game.switches['medicine_cat'] = None
        game.switches['deputy'] = None
        game.switches['members'] = []
        game.switches['choosing_camp'] = False
        create_example_cats()
        self.worldseed = random.randrange(10000)
        if mapavailable:
            self.world = World((44, 44), self.worldseed)


class ClanCreatedScreen(Screens):

    def on_use(self):
        # LAYOUT
        verdana.text('Your clan has been created and saved!', ('center', 50))
        game.clan.leader.draw_big((screen_x / 2 - 50, 100))

        # buttons
        buttons.draw_button(('center', 250),
                            text='Continue',
                            cur_screen='clan screen',
                            hotkey=[1])

    def screen_switches(self):
        game.clan = Clan(game.switches['clan_name'],
                         game.choose_cats[game.switches['leader']],
                         game.choose_cats[game.switches['deputy']],
                         game.choose_cats[game.switches['medicine_cat']],
                         game.switches['biome'], game.switches['world_seed'],
                         game.switches['camp_site'])
        game.clan.create_clan()
        if mapavailable:
            territory_claim = str(game.clan.name) + 'Clan Territory'
            otherclan_campsite = {}
            for clan in game.clan.all_clans:
                x = random.randrange(40)
                y = random.randrange(44)
                clan_camp = self.choose_other_clan_territory(x, y)
                territory_biome = str(game.map_info[clan_camp][2])
                territory_twolegs = str(game.map_info[clan_camp][4])
                territory_thunderpath = str(game.map_info[clan_camp][5])
                territory_prey = str(game.map_info[clan_camp][6])
                territory_plants = str(game.map_info[clan_camp][7])
                game.map_info[clan_camp] = [
                    clan_camp[0], clan_camp[1], territory_biome,
                    str(clan) + " Camp", territory_twolegs,
                    territory_thunderpath, territory_prey, territory_plants
                ]
                otherclan_campsite[str(clan)] = clan_camp
            for y in range(44):
                for x in range(40):
                    if (x, y) == (game.switches['camp_site'][0] - 1,
                                  game.switches['camp_site'][1]):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0],
                                    game.switches['camp_site'][1] - 1):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0] + 1,
                                    game.switches['camp_site'][1]):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    elif (x, y) == (game.switches['camp_site'][0],
                                    game.switches['camp_site'][1] + 1):
                        territory_biome = str(game.map_info[(x, y)][2])
                        territory_twolegs = str(game.map_info[(x, y)][4])
                        territory_thunderpath = str(game.map_info[(x, y)][5])
                        territory_prey = str(game.map_info[(x, y)][6])
                        territory_plants = str(game.map_info[(x, y)][7])
                        if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                            game.map_info[(x, y)] = [
                                x, y, territory_biome, territory_claim,
                                territory_twolegs, territory_thunderpath,
                                territory_prey, territory_plants
                            ]
                    for clan in game.clan.all_clans:
                        if (x, y) == (otherclan_campsite[str(clan)][0] - 1,
                                      otherclan_campsite[str(clan)][1]):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0],
                                        otherclan_campsite[str(clan)][1] - 1):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0] + 1,
                                        otherclan_campsite[str(clan)][1]):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
                        elif (x, y) == (otherclan_campsite[str(clan)][0],
                                        otherclan_campsite[str(clan)][1] + 1):
                            territory_biome = str(game.map_info[(x, y)][2])
                            territory_twolegs = str(game.map_info[(x, y)][4])
                            territory_thunderpath = str(game.map_info[(x,
                                                                       y)][5])
                            territory_prey = str(game.map_info[(x, y)][6])
                            territory_plants = str(game.map_info[(x, y)][7])
                            if str(game.map_info[(x, y)][3]) != 'Unclaimable':
                                game.map_info[(x, y)] = [
                                    x, y, territory_biome,
                                    str(clan) + ' Territory',
                                    territory_twolegs, territory_thunderpath,
                                    territory_prey, territory_plants
                                ]
            save_map(game.map_info, game.switches['clan_name'])

    def choose_other_clan_territory(self, x, y):
        self.x = x
        self.y = y
        if game.map_info[(self.x, self.y)][3] != "Unclaimed":
            self.x = random.randrange(40)
            self.y = random.randrange(44)
            if game.map_info[(self.x, self.y)][3] == "Unclaimed":
                return self.x, self.y
            else:
                self.x = random.randrange(40)
                self.y = random.randrange(44)
                return self.x, self.y
        else:
            return self.x, self.y


class EventsScreen(Screens):

    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text(
            'Check this page to see which events are currently happening at the Clan.',
            ('center', 110))

        verdana.text(f'Current season: {str(game.clan.current_season)}',
                     ('center', 140))

        if game.clan.age == 1:
            verdana.text(f'Clan age: {str(game.clan.age)} moon',
                         ('center', 170))
        if game.clan.age != 1:
            verdana.text(f'Clan age: {str(game.clan.age)} moons',
                         ('center', 170))

        if game.switches['events_left'] == 0:
            buttons.draw_button((200, 220),
                                text='TIMESKIP ONE MOON',
                                timeskip=True,
                                hotkey=[11])
            if game.switches['timeskip']:
                game.cur_events_list = []
                game.relation_events_list = []
        else:
            buttons.draw_button((200, 220),
                                text='TIMESKIP ONE MOON',
                                available=False)
        events_class.one_moon()

        # show the Relationshipevents
        buttons.draw_button((-200, 220),
                            text='RELATIONSHIP EVENTS',
                            cur_screen='relationship event screen',
                            hotkey=[12])

        a = 0
        if game.cur_events_list is not None and game.cur_events_list != []:
            for x in range(
                    min(len(game.cur_events_list), game.max_events_displayed)):
                #TODO: Find the real cause for game.cur_events_list[x] being a function sometimes
                if game.cur_events_list[x] is None or not isinstance(game.cur_events_list[x], str):
                    continue
                if "Clan has no " in game.cur_events_list[x]:
                    verdana_red.text(game.cur_events_list[x],
                                     ('center', 260 + a * 30))
                else:
                    verdana.text(game.cur_events_list[x],
                                 ('center', 260 + a * 30))
                a += 1
        else:
            verdana.text("Nothing significant happened this moon.",
                         ('center', 260 + a * 30))

        draw_menu_buttons()
        if len(game.cur_events_list) > game.max_events_displayed:
            buttons.draw_button((700, 180),
                                image=game.up,
                                arrow="UP",
                                hotkey=[20])
            buttons.draw_button((700, 630),
                                image=game.down,
                                arrow="DOWN",
                                hotkey=[22])


class ProfileScreen(Screens):

    def on_use(self):
        # use this variable to point to the cat object in question
        the_cat = cat_class.all_cats.get(game.switches['cat'],
                                         game.clan.instructor)
        # use these attributes to create differing profiles for starclan cats etc.
        is_instructor = False
        if the_cat.dead and game.clan.instructor.ID == the_cat.ID:
            is_instructor = True

        # back and next buttons on the profile page
        previous_cat = 0
        next_cat = 0

        if the_cat.dead and not is_instructor:
            previous_cat = game.clan.instructor.ID
        if is_instructor:
            next_cat = 1
        for check_cat in cat_class.all_cats:
            if cat_class.all_cats[check_cat].ID == the_cat.ID:
                next_cat = 1
            if next_cat == 0 and cat_class.all_cats[
                    check_cat].ID != the_cat.ID and cat_class.all_cats[
                        check_cat].dead == the_cat.dead and cat_class.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not cat_class.all_cats[
                                check_cat].exiled:
                previous_cat = cat_class.all_cats[check_cat].ID
            elif next_cat == 1 and cat_class.all_cats[
                    check_cat].ID != the_cat.ID and cat_class.all_cats[
                        check_cat].dead == the_cat.dead and cat_class.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not cat_class.all_cats[
                                check_cat].exiled:
                next_cat = cat_class.all_cats[check_cat].ID
            elif int(next_cat) > 1:
                break
        if next_cat == 1:
            next_cat = 0
        if next_cat != 0:
            buttons.draw_button((-40, 40),
                                text='Next Cat',
                                cat=next_cat,
                                hotkey=[21])
        if previous_cat != 0:
            buttons.draw_button((40, 40),
                                text='Previous Cat',
                                cat=previous_cat,
                                hotkey=[23])

        # Info in string
        cat_name = str(the_cat.name)  # name
        if the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        if is_instructor:
            the_cat.thought = "Hello. I am here to guide the dead cats of " + game.clan.name + "Clan into StarClan."

        # LAYOUT
        count = 0
        count2 = 0
        verdana_big.text(cat_name, ('center', 150))  # NAME
        the_cat.draw_large((100, 200))  # IMAGE

        if len(the_cat.thought) < 100:
            verdana.text(the_cat.thought, ('center', 180))  # THOUGHT
        else:
            cut = the_cat.thought.find(' ', int(len(the_cat.thought)/2))
            first_part = the_cat.thought[:cut]
            second_part = the_cat.thought[cut:]
            verdana.text(first_part, ('center', 180))  # THOUGHT
            verdana.text(second_part, ('center', 200))  # THOUGHT

        
        if the_cat.genderalign == None or the_cat.genderalign == True or the_cat.genderalign == False:
            verdana_small.text(str(the_cat.gender), (300, 230 + count * 15))
        else:
            verdana_small.text(str(the_cat.genderalign), (300, 230 + count * 15))
        count += 1  # SEX / GENDER
        if (the_cat.exiled): 
            verdana_red.text("exiled", (490, 230 + count2 * 15))
        else:
            verdana_small.text(the_cat.status, (490, 230 + count2 * 15))
        if not the_cat.dead and 'leader' in the_cat.status:  #See Lives
            count2 += 1
            verdana_small.text(
                'remaining lives: ' + str(game.clan.leader_lives),
                (490, 230 + count2 * 15))
        count2 += 1  # STATUS
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is None:
                the_cat.update_mentor()
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name),
                                   (490, 230 + count2 * 15))
                count2 += 1
        if len(the_cat.apprentice) != 0:
            if len(the_cat.apprentice) == 1:
                apps = 'apprentice: ' + str(the_cat.apprentice[0].name)
            else:
                apps = 'apprentices: '
                num = 1
                for cat in the_cat.apprentice:
                    if num % 2 == 0:
                        apps += str(cat.name) + ', '
                    else:
                        apps += str(cat.name) + ', '
                    num += 1
                apps = apps[:len(apps) - 2]
            verdana_small.text(apps, (490, 230 + count2 * 15))
            count2 += 1
        if len(the_cat.former_apprentices
               ) != 0 and the_cat.former_apprentices[0] is not None:
            if len(the_cat.former_apprentices) == 1:
                former_apps = 'former apprentice: ' + str(
                    the_cat.former_apprentices[0].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
            elif len(the_cat.former_apprentices) == 2:
                former_apps = 'former apprentices: ' + str(
                    the_cat.former_apprentices[0].name) + ', ' + str(
                        the_cat.former_apprentices[1].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
            elif len(the_cat.former_apprentices) == 3:
                former_apps = 'former apprentices: ' + str(
                    the_cat.former_apprentices[0].name) + ', ' + str(
                        the_cat.former_apprentices[1].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
                verdana_small.text(str(the_cat.former_apprentices[2].name), (490, 230 + count2 * 15))
                count2+=1
            elif len(the_cat.former_apprentices) == 4:
                former_apps = 'former apprentices: ' + str(
                    the_cat.former_apprentices[0].name) + ', ' + str(
                        the_cat.former_apprentices[1].name)
                verdana_small.text(former_apps, (490, 230 + count2 * 15))
                count2 += 1
                former_apps2 = str(the_cat.former_apprentices[2].name) + ', ' + str(the_cat.former_apprentices[3].name)
                verdana_small.text(former_apps2, (490, 230 + count2 * 15))
                count2+=1
            else:
                num = 1
                rows = []
                name = ''
                for cat in the_cat.former_apprentices:
                    name = name + str(cat.name) + ', '
                    if num == 2:
                        rows.append(name)
                        name = ''
                        num += 1
                    if num % 3 == 0 and name != '':
                        rows.append(name)
                        name = ''
                    num += 1
                for ind in range(len(rows)):
                    if ind == 0:
                        verdana_small.text('former apprentices: ' + rows[ind],
                                           (490, 230 + count2 * 15))
                    elif ind == len(rows) - 1:
                        verdana_small.text(rows[ind][:-2],
                                           (490, 230 + count2 * 15))
                    else:
                        verdana_small.text(rows[ind], (490, 230 + count2 * 15))
                    count2 += 1
        if the_cat.age == 'kitten':
            verdana_small.text('young', (300, 230 + count * 15))
        elif the_cat.age == 'elder':
            verdana_small.text('senior', (300, 230 + count * 15))
        else:
            verdana_small.text(the_cat.age, (300, 230 + count * 15))
        count += 1  # AGE
        verdana_small.text(the_cat.trait, (490, 230 + count2 * 15))
        count2 += 1  # CHARACTER TRAIT
        verdana_small.text(the_cat.skill, (490, 230 + count2 * 15))
        count2 += 1  # SPECIAL SKILL
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(),
                           (300, 230 + count * 15))
        count += 1  # EYE COLOR
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(),
                           (300, 230 + count * 15))
        count += 1  # PELT TYPE
        verdana_small.text('fur length: ' + the_cat.pelt.length,
                           (300, 230 + count * 15))
        count += 1  # PELT LENGTH
        verdana_small.text('accessory: ' + str(the_cat.accessory).lower(),
                           (300, 230 + count * 15))
        count += 1  # accessory

        # PARENTS
        if the_cat.parent1 is None:
            verdana_small.text('parents: unknown', (300, 230 + count * 15))
            count += 1
        elif the_cat.parent2 is None and the_cat.parent1 in the_cat.all_cats:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            verdana_small.text('parents: ' + par1 + ', unknown',
                               (300, 230 + count * 15))
            count += 1
        elif the_cat.parent2 is None:
            par2 = "unknown"
            par1 = "Error: Cat#" + the_cat.parent1 + " not found"
            verdana_small.text('parents: ' + par1 + ', unknown',
                               (300, 230 + count * 15))
            count += 1
        else:
            if the_cat.parent1 in the_cat.all_cats and the_cat.parent2 in the_cat.all_cats:
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            elif the_cat.parent1 in the_cat.all_cats:
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
            elif the_cat.parent2 in the_cat.all_cats:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            else:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"

            verdana_small.text('parents: ' + par1 + ' and ' + par2,
                               (300, 230 + count * 15))
            count += 1

        # MOONS
        if the_cat.dead:
            if the_cat.moons == 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moon (in life)',
                    (300, 230 + count * 15))
                count += 1
            elif the_cat.moons != 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moons (in life)',
                    (300, 230 + count * 15))
                count += 1
            if the_cat.dead_for == 1:
                verdana_small.text(
                    str(the_cat.dead_for) + ' moon (in death)',
                    (300, 230 + count * 15))
                count += 1
            elif the_cat.dead_for != 1:
                verdana_small.text(
                    str(the_cat.dead_for) + ' moons (in death)',
                    (300, 230 + count * 15))
                count += 1
        else:
            if the_cat.moons == 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moon', (300, 230 + count * 15))
                count += 1
            elif the_cat.moons != 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moons', (300, 230 + count * 15))
                count += 1

        # MATE
        if the_cat.mate is not None and not the_cat.dead:
            if the_cat.mate in cat_class.all_cats:
                if cat_class.all_cats.get(
                        the_cat.mate
                ).dead:  # TODO: fix when mate dies mate becomes none
                    verdana_small.text(
                        'former mate: ' +
                        str(cat_class.all_cats[the_cat.mate].name),
                        (300, 230 + count * 15))
                else:
                    verdana_small.text(
                        'mate: ' + str(cat_class.all_cats[the_cat.mate].name),
                        (300, 230 + count * 15))
                count += 1
            else:
                verdana_small.text(
                    'Error: mate: ' + str(the_cat.mate) + " not found",
                    ('center', 495))

        # experience
        if not the_cat.dead:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (490, 230 + count2 * 15))
            count2 += 1
        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (490, 230 + count2 * 15))
            count2 += 1

        # buttons
        buttons.draw_button(('center', 400),
                            text="See Family",
                            cur_screen='see kits screen')

        buttons.draw_button(('center', 430),
                            text="See Relationships",
                            cur_screen='relationship screen')

        buttons.draw_button(('center', 460),
                            text='Options',
                            cur_screen='options screen')

        buttons.draw_button(('center', 510),
                            text='Back',
                            cur_screen=game.switches['last_screen'])


    def screen_switches(self):
        cat_profiles()


class SingleEventScreen(Screens):

    def on_use(self):
        # LAYOUT
        if game.switches['event'] is not None:
            events_class.all_events[game.switches['event']].page()

        # buttons
        buttons.draw_button(('center', -150),
                            text='Continue',
                            cur_screen='events screen')

    def screen_switches(self):
        pass


class ViewChildrenScreen(Screens):

    def on_use(self):
        the_cat = cat_class.all_cats[game.switches['cat']]
        verdana_big.text(f'Family of {str(the_cat.name)}', ('center', 50))
        verdana.text('Parents:', ('center', 85))
        if the_cat.parent1 is None:
            verdana_small.text('Unknown', (342, 165))
        elif the_cat.parent1 in cat_class.all_cats:
            buttons.draw_button(
                (350, 120),
                image=cat_class.all_cats[the_cat.parent1].sprite,
                cat=the_cat.parent1,
                cur_screen='profile screen')

            name_len = verdana.text(
                str(cat_class.all_cats[the_cat.parent1].name))
            verdana_small.text(str(cat_class.all_cats[the_cat.parent1].name),
                               (375 - name_len / 2, 185))

        else:
            verdana_small.text(f'Error: cat {str(the_cat.parent1)} not found',
                               (342, 165))
        if the_cat.parent2 is None:
            verdana_small.text('Unknown', (422, 165))
        elif the_cat.parent2 in cat_class.all_cats:
            buttons.draw_button(
                (430, 120),
                image=cat_class.all_cats[the_cat.parent2].sprite,
                cat=the_cat.parent2,
                cur_screen='profile screen')

            name_len = verdana.text(
                str(cat_class.all_cats[the_cat.parent2].name))
            verdana_small.text(str(cat_class.all_cats[the_cat.parent2].name),
                               (455 - name_len / 2, 185))

        else:
            verdana_small.text(
                'Error: cat ' + str(the_cat.parent2) + ' not found',
                (342, 165))

        pos_x = 0
        pos_y = 20
        siblings = False
        for x in game.clan.clan_cats:
            if (cat_class.all_cats[x].parent1 in (the_cat.parent1, the_cat.parent2) or cat_class.all_cats[x].parent2 in (
                    the_cat.parent1, the_cat.parent2) and the_cat.parent2 is not None) and the_cat.ID != cat_class.all_cats[x].ID and the_cat.parent1 is not None and \
                    cat_class.all_cats[x].parent1 is not None:
                buttons.draw_button((40 + pos_x, 220 + pos_y),
                                    image=cat_class.all_cats[x].sprite,
                                    cat=cat_class.all_cats[x].ID,
                                    cur_screen='profile screen')

                name_len = verdana.text(str(cat_class.all_cats[x].name))
                verdana_small.text(str(cat_class.all_cats[x].name),
                                   (65 + pos_x - name_len / 2, 280 + pos_y))

                siblings = True
                pos_x += 80
                if pos_x > 640:
                    pos_y += 70
                    pos_x = 0
        if siblings:
            verdana.text('Siblings:', ('center', 210))
        else:
            verdana.text('This cat has no siblings.', ('center', 210))
        buttons.draw_button(('center', -100),
                            text='Back',
                            cur_screen='profile screen')
        pos_x = 0
        pos_y = 60
        kittens = False
        for x in game.clan.clan_cats:
            if the_cat.ID in [
                    cat_class.all_cats[x].parent1,
                    cat_class.all_cats[x].parent2
            ]:
                buttons.draw_button((40 + pos_x, 370 + pos_y),
                                    image=cat_class.all_cats[x].sprite,
                                    cat=cat_class.all_cats[x].ID,
                                    cur_screen='profile screen')

                name_len = verdana.text(str(cat_class.all_cats[x].name))
                verdana_small.text(str(cat_class.all_cats[x].name),
                                   (65 + pos_x - name_len / 2, 430 + pos_y))

                kittens = True
                pos_x += 80
                if pos_x > 640:
                    pos_y += 70
                    pos_x = 0
        if kittens:
            verdana.text('Offspring:', ('center', 400))
        else:
            verdana.text('This cat has never had offspring.', ('center', 400))
        buttons.draw_button(('center', -100),
                            text='Back',
                            cur_screen='profile screen')

    def screen_switches(self):
        cat_profiles()


class ChooseMateScreen(Screens):

    def on_use(self):
        the_cat = cat_class.all_cats[game.switches['cat']]
        verdana_big.text(f'Choose mate for {str(the_cat.name)}',
                         ('center', 50))
        verdana_small.text(
            'If the cat has chosen a mate, they will stay loyal and not have kittens with anyone else,',
            ('center', 80))
        verdana_small.text(
            'even if having kittens in said relationship is impossible.',
            ('center', 95))
        verdana_small.text(
            'Chances of having kittens when possible is heightened though.',
            ('center', 110))

        the_cat.draw_large((200, 130))
        self._extracted_from_on_use_29(the_cat, 70)
        mate = None
        if game.switches['mate'] is not None and the_cat.mate is None:
            mate = cat_class.all_cats[game.switches['mate']]
        elif the_cat.mate is not None:
            if the_cat.mate in cat_class.all_cats:
                mate = cat_class.all_cats[the_cat.mate]
            else:
                the_cat.mate = None
        if mate is not None:
            mate.draw_large((450, 130))
            verdana.text(str(mate.name), ('center', 300))
            self._extracted_from_on_use_29(mate, -100)
            if the_cat.gender == mate.gender and not game.settings[
                    'no gendered breeding']:
                verdana_small.text(
                    '(this pair will not be able to have kittens)',
                    ('center', 320))

        valid_mates = []
        pos_x = 0
        pos_y = 20
        if the_cat.mate is None:
            self._extracted_from_on_use_42(the_cat, valid_mates, pos_x, pos_y)
        else:
            verdana.text('Already in a relationship.', ('center', 340))
            kittens = False
            for x in game.clan.clan_cats:
                if the_cat.ID in [
                        cat_class.all_cats[x].parent1,
                        cat_class.all_cats[x].parent2
                ] and mate.ID in [
                        cat_class.all_cats[x].parent1,
                        cat_class.all_cats[x].parent2
                ]:
                    buttons.draw_button((200 + pos_x, 370 + pos_y),
                                        image=cat_class.all_cats[x].sprite,
                                        cat=cat_class.all_cats[x].ID,
                                        cur_screen='profile screen')

                    kittens = True
                    pos_x += 50
                    if pos_x > 400:
                        pos_y += 50
                        pos_x = 0
            if kittens:
                verdana.text('Their offspring:', ('center', 360))
            else:
                verdana.text('This pair has never had offspring.',
                             ('center', 360))
        if mate is not None and the_cat.mate is None:
            buttons.draw_button(('center', -130),
                                text="It\'s official!",
                                cat_value=the_cat,
                                mate=mate)

        elif the_cat.mate is not None:
            buttons.draw_button(('center', -130),
                                text="Break it up...",
                                cat_value=the_cat,
                                mate=None)

        buttons.draw_button(('center', -100),
                            text='Back',
                            cur_screen='profile screen')

    # TODO Rename this here and in `on_use`
    def _extracted_from_on_use_42(self, the_cat, valid_mates, pos_x, pos_y):
        for x in game.clan.clan_cats:
            relevant_cat = cat_class.all_cats[x]
            invalid_age = relevant_cat.age not in ['kitten', 'adolescent']

            direct_related = the_cat.is_sibling(relevant_cat) or the_cat.is_parent(relevant_cat) or relevant_cat.is_parent(the_cat)
            indirect_related = the_cat.is_uncle_aunt(relevant_cat) or relevant_cat.is_uncle_aunt(the_cat)
            related = direct_related or indirect_related

            not_aviable = relevant_cat.dead or relevant_cat.exiled

            if not related and relevant_cat.ID != the_cat.ID and invalid_age and not not_aviable and relevant_cat.mate == None:
                valid_mates.append(relevant_cat)
        all_pages = int(ceil(len(valid_mates) /
                             27.0)) if len(valid_mates) > 27 else 1
        cats_on_page = 0
        for x in range(len(valid_mates)):
            if x + (game.switches['list_page'] - 1) * 27 > len(valid_mates):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            pot_mate = valid_mates[x + (game.switches['list_page'] - 1) * 27]
            buttons.draw_button((100 + pos_x, 320 + pos_y),
                                image=pot_mate.sprite,
                                mate=pot_mate.ID)

            pos_x += 50
            cats_on_page += 1
            if pos_x > 400:
                pos_y += 50
                pos_x = 0
            if cats_on_page >= 27 or x + (game.switches['list_page'] -
                                          1) * 27 == len(valid_mates) - 1:
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

    # TODO Rename this here and in `on_use`
    def _extracted_from_on_use_29(self, arg0, arg1):
        verdana_small.text(arg0.age, (arg1, 200))
        if (arg0.genderalign is not None):
            verdana_small.text(arg0.genderalign, (arg1, 215))
        else:
            verdana_small.text(arg0.gender, (arg1, 215))
        verdana_small.text(arg0.trait, (arg1, 230))

    def screen_switches(self):
        game.switches['mate'] = None
        cat_profiles()


class ListScreen(Screens):
    # page can be found in game.switches['list_page']
    # the amount of cats a page can hold is 20, so the amount of pages is cats/20

    def on_use(self):
        verdana_big.text(game.clan.name + 'Clan', ('center', 30))
        verdana.text('ALL CATS LIST', ('center', 100))
        living_cats = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if not the_cat.dead and not the_cat.exiled:
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
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            if x + (game.switches['list_page'] - 1) * 20 >= len(search_cats):
                game.switches['list_page'] -= 1
            if (x + (game.switches['list_page'] - 1) * 20 < len(search_cats)):
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
                verdana.text(str(the_cat.name), (155 + pos_x - name_len/2, 240 + pos_y))
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
                            text='Cats Outside Clans',
                            cur_screen='other screen')

        draw_menu_buttons()

    def screen_switches(self):
        cat_profiles()


class OtherScreen(Screens):

    def on_use(self):
        verdana_big.text('Cats Outside The Clan', ('center', 30))
        verdana.text('ALL CATS LIST', ('center', 100))
        living_cats = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
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


# def choose_banner():
# if game.clan is not None:
#     # if game.clan.current_season == 'Leaf-fall':
#     fall = pygame.image.load('resources/seasonbanners/fall/fall banner.png')
#     fall_fog = pygame.image.load('resources/seasonbanners/fall/fall banner fog.png')
#     fall_night = pygame.image.load('resources/seasonbanners/fall/fall banner night.png')
#     fall_night_fog = pygame.image.load('resources/seasonbanners/fall/fall banner night fog.png')
#     fall_night_overcast = pygame.image.load('resources/seasonbanners/fall/fall banner night overcast.png')
#     fall_night_rain = pygame.image.load('resources/seasonbanners/fall/fall banner night rain.png')
#     fall_overcast = pygame.image.load('resources/seasonbanners/fall/fall banner overcast.png')
#     fall_rain = pygame.image.load('resources/seasonbanners/fall/fall banner rain.png')
#     leaffall = [fall, fall_fog, fall_night, fall_night_fog, fall_night_overcast, fall_night_rain, fall_overcast,
#                 fall_rain]
#     return choice(leaffall)


class PatrolScreen(Screens):

    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text(
            'These cats are currently in the camp, ready for a patrol.',
            ('center', 115))
        verdana.text('Choose up to six to take on patrol.', ('center', 135))
        verdana.text(
            'Smaller patrols help cats gain more experience, but larger patrols are safer.',
            ('center', 155))

        draw_menu_buttons()
        able_cats = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
            if not the_cat.dead and the_cat.in_camp and the_cat not in game.patrolled and the_cat.status in [
                    'leader', 'deputy', 'warrior', 'apprentice'
            ] and not the_cat.exiled:

                able_cats.append(the_cat)
        if not game.patrol_cats:
            i_max = min(len(able_cats), 12)
            for i in range(i_max):
                test_cat = random.choice(able_cats)
                able_cats.remove(test_cat)
                game.patrol_cats[i] = test_cat
        else:
            i_max = len(game.patrol_cats)
        random_options = []
        for u in range(6):
            if u < i_max:
                if game.patrol_cats[u] in game.switches['current_patrol']:
                    game.patrol_cats[u].draw(
                        (screen_x / 2 - 50 * (u + 2), 550))
                else:
                    buttons.draw_button((50, 150 + 50 * u),
                                        image=game.patrol_cats[u].sprite,
                                        cat=u,
                                        hotkey=[u + 1, 11])
                    random_options.append(game.patrol_cats[u])
        for u in range(6, 12):
            if u < i_max:
                if game.patrol_cats[u] in game.switches['current_patrol']:
                    game.patrol_cats[u].draw(
                        (screen_x / 2 + 50 * (u - 5), 550))
                else:
                    buttons.draw_button((screen_x - 100, 150 + 50 * (u - 6)),
                                        image=game.patrol_cats[u].sprite,
                                        cat=u,
                                        hotkey=[u + 1, 12])
                    random_options.append(game.patrol_cats[u])
        if random_options and len(game.switches['current_patrol']) < 6:
            random_patrol = choice(random_options)
            buttons.draw_button(('center', 530),
                                text='Add Random',
                                current_patrol=random_patrol,
                                add=True,
                                hotkey=[12])

        else:
            buttons.draw_button(('center', 530),
                                text='Add Random',
                                available=False)
        if game.switches['cat'] is not None and 12 > game.switches[
                'cat'] >= 0 and game.patrol_cats[game.switches[
                    'cat']] not in game.switches['current_patrol']:
            self._extracted_from_on_use_58()
        if len(game.switches['current_patrol']) > 0:
            buttons.draw_button(('center', 630),
                                text='Start Patrol',
                                cur_screen='patrol event screen',
                                hotkey=[13])

        else:
            buttons.draw_button(('center', 630),
                                text='Start Patrol',
                                available=False)

    # TODO Rename this here and in `on_use`
    def _extracted_from_on_use_58(self):
        game.patrol_cats[game.switches['cat']].draw_large((320, 200))
        verdana.text(str(game.patrol_cats[game.switches['cat']].name),
                     ('center', 360))
        verdana_small.text(str(game.patrol_cats[game.switches['cat']].status),
                           ('center', 385))

        verdana_small.text(str(game.patrol_cats[game.switches['cat']].trait),
                           ('center', 405))

        verdana_small.text(str(game.patrol_cats[game.switches['cat']].skill),
                           ('center', 425))

        verdana_small.text(
            'experience: ' +
            str(game.patrol_cats[game.switches['cat']].experience_level),
            ('center', 445))

        if game.patrol_cats[game.switches['cat']].status == 'apprentice':
            if game.patrol_cats[game.switches['cat']].mentor is not None:
                verdana_small.text(
                    'mentor: ' +
                    str(game.patrol_cats[game.switches['cat']].mentor.name),
                    ('center', 465))

        if len(game.switches['current_patrol']) < 6:
            buttons.draw_button(
                ('center', 500),
                text='Add to Patrol',
                current_patrol=game.patrol_cats[game.switches['cat']],
                add=True,
                hotkey=[11])

    def screen_switches(self):
        game.switches['current_patrol'] = []
        game.switches['cat'] = None
        game.patrol_cats = {}
        game.switches['event'] = 0
        cat_profiles()


class PatrolEventScreen(Screens):

    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        if game.switches['event'] == 0:
            patrol.add_patrol_cats()
            patrol.add_possible_patrols()
            game.switches['event'] = -1
        if game.switches['event'] == -1:
            intro_text = patrol.patrol_event.intro_text
            intro_text = intro_text.replace('r_c',
                                            str(patrol.patrol_random_cat.name))
            intro_text = intro_text.replace('p_l',
                                            str(patrol.patrol_leader.name))
            verdana.blit_text(intro_text, (150, 200))
            buttons.draw_button((290, 320), text='Proceed', event=-2)
            buttons.draw_button((150, 320), text='Do Not Proceed', event=2)
            if patrol.patrol_event.patrol_id in [500, 501, 502, 503, 510]:
                buttons.draw_button((150, 290), text='Antagonize', event=3)

        if game.switches['event'] == -2:
            patrol.calculate_success()
            game.switches['event'] = 1
        elif game.switches['event'] == 3:
            game.switches['event'] = 4
        if game.switches['event'] > 0:
            if game.switches['event'] == 1:
                if patrol.success:
                    success_text = patrol.patrol_event.success_text
                    success_text = success_text.replace(
                        'r_c', str(patrol.patrol_random_cat.name))
                    success_text = success_text.replace(
                        'p_l', str(patrol.patrol_leader.name))
                    verdana.blit_text(success_text, (150, 200))
                else:
                    fail_text = patrol.patrol_event.fail_text
                    fail_text = fail_text.replace(
                        'r_c', str(patrol.patrol_random_cat.name))
                    fail_text = fail_text.replace(
                        'p_l', str(patrol.patrol_leader.name))
                    verdana.blit_text(fail_text, (150, 200))
            elif game.switches['event'] == 2:
                decline_text = patrol.patrol_event.decline_text
                decline_text = decline_text.replace(
                    'r_c', str(patrol.patrol_random_cat.name))
                decline_text = decline_text.replace(
                    'p_l', str(patrol.patrol_leader.name))
                verdana.blit_text(decline_text, (150, 200))
            elif game.switches['event'] == 4:
                antagonize_text = patrol.patrol_event.antagonize_text
                antagonize_text = antagonize_text.replace(
                    'r_c', str(patrol.patrol_random_cat.name))
                antagonize_text = antagonize_text.replace(
                    'p_l', str(patrol.patrol_leader.name))
                verdana.blit_text(antagonize_text, (150, 200))
            buttons.draw_button((150, 350),
                                text='Return to Clan',
                                cur_screen='clan screen')
            buttons.draw_button((280, 350),
                                text='Patrol Again',
                                cur_screen='patrol screen')

        for u in range(6):
            if u < len(patrol.patrol_cats):
                patrol.patrol_cats[u].draw((50, 200 + 50 * (u)))
        verdana_small.blit_text('season: ' + str(game.clan.current_season),
                                (150, 400))
        verdana_small.blit_text(
            'patrol leader: ' + str(patrol.patrol_leader.name), (150, 430))
        verdana_small.blit_text(
            'patrol members: ' + self.get_list_text(patrol.patrol_names),
            (150, 460))
        verdana_small.blit_text(
            'patrol skills: ' + self.get_list_text(patrol.patrol_skills),
            (150, 510))
        verdana_small.blit_text(
            'patrol traits: ' + self.get_list_text(patrol.patrol_traits),
            (150, 560))
        draw_menu_buttons()

    def get_list_text(self, patrol_list):
        if not patrol_list:
            return "None"
        # Removes duplicates.
        patrol_set = list(set(patrol_list))
        return ", ".join(patrol_set)

    def screen_switches(self):
        game.switches['event'] = 0
        cat_profiles()


class AllegiancesScreen(Screens):

    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))

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
            buttons.draw_button((700, 180),
                                image=game.up,
                                arrow="UP",
                                hotkey=[20])
            buttons.draw_button((700, 630),
                                image=game.down,
                                arrow="DOWN",
                                hotkey=[22])
        draw_menu_buttons()

    def screen_switches(self):
        living_cats = []
        game.allegiance_scroll_ct = 0
        game.allegiance_list = []
        for x in range(len(cat_class.all_cats.values())):
            the_cat = list(cat_class.all_cats.values())[x]
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
                if cat_class.all_cats[living_cat_.parent1].gender == 'male':
                    if living_cat_.parent2 is None or cat_class.all_cats[
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
                if len(living_cat__.apprentice) > 0:
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


class ChooseMentorScreen(Screens):

    def on_use(self):
        verdana_big.text('Choose Mentor', ('center', 30))
        living_cats = []
        for cat in cat_class.all_cats.values():
            if not cat.dead and cat != game.switches[
                    'apprentice'].mentor and cat.status in [
                        'warrior', 'deputy', 'leader'
                    ]:
                living_cats.append(cat)
        all_pages = 1
        if len(living_cats) > 20:
            all_pages = int(ceil(len(living_cats) / 20.0))
        pos_x = 0
        pos_y = 0
        cats_on_page = 0
        for x in range(len(living_cats)):
            if x + (game.switches['list_page'] - 1) * 20 > len(living_cats):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            the_cat = living_cats[x + (game.switches['list_page'] - 1) * 20]
            if not the_cat.dead:
                buttons.draw_button((130 + pos_x, 180 + pos_y),
                                    image=the_cat.sprite,
                                    cat=the_cat.ID,
                                    cur_screen='choose mentor screen2')

                name_len = verdana.text(str(the_cat.name))
                verdana.text(str(the_cat.name),
                             (130 + pos_x - name_len / 2, 240 + pos_y))
                cats_on_page += 1
                pos_x += 100
                if pos_x >= 600:
                    pos_x = 0
                    pos_y += 100
                if cats_on_page >= 20 or x + (game.switches['list_page'] -
                                              1) * 20 == len(living_cats) - 1:
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

        draw_menu_buttons()


class ChooseMentorScreen2(Screens):

    def on_use(self):
        # use this variable to point to the cat object in question
        the_cat = cat_class.all_cats.get(game.switches['cat'])

        # back and next buttons on the profile page
        previous_cat = 0
        next_cat = 0

        for check_cat in cat_class.all_cats:
            if cat_class.all_cats[check_cat].ID == the_cat.ID:
                next_cat = 1

            if next_cat == 0 and cat_class.all_cats[
                    check_cat].ID != the_cat.ID and not cat_class.all_cats[
                        check_cat].dead and cat_class.all_cats[
                            check_cat].status in [
                                'warrior', 'deputy', 'leader'
                            ] and cat_class.all_cats[check_cat] != game.switches[
                                'apprentice'].mentor and not cat_class.all_cats[
                                    check_cat].exiled:
                previous_cat = cat_class.all_cats[check_cat].ID
            elif next_cat == 1 and cat_class.all_cats[check_cat].ID != the_cat.ID and not cat_class.all_cats[check_cat].dead and cat_class.all_cats[check_cat].status in ['warrior',
                                                                                                                                                                          'deputy',
                                                                                                                                                                          'leader'] and \
                    cat_class.all_cats[check_cat] != game.switches['apprentice'].mentor and not cat_class.all_cats[
                    check_cat].exiled:
                next_cat = cat_class.all_cats[check_cat].ID
            elif int(next_cat) > 1:
                break

        if next_cat == 1:
            next_cat = 0

        if next_cat != 0:
            buttons.draw_button((-40, 40),
                                text='Next Cat',
                                cat=next_cat,
                                hotkey=[21])
        if previous_cat != 0:
            buttons.draw_button((40, 40),
                                text='Previous Cat',
                                cat=previous_cat,
                                hotkey=[23])

        # Info in string
        cat_name = str(the_cat.name)  # name
        cat_thought = the_cat.thought  # thought

        # LAYOUT
        count = 0
        count2 = 0
        verdana_big.text(cat_name, ('center', 70))  # NAME
        the_cat.draw_large(('center', 100))  # IMAGE
        verdana_small.text(the_cat.genderalign, (250, 330 + count * 15))
        count += 1  # SEX / GENDER
        verdana_small.text(the_cat.status, (450, 330 + count2 * 15))
        count2 += 1  # STATUS
        if 'apprentice' in the_cat.status:
            if the_cat.mentor is not None:
                verdana_small.text('mentor: ' + str(the_cat.mentor.name),
                                   (450, 330 + count2 * 15))
                count2 += 1
        if len(the_cat.apprentice) != 0:
            if len(the_cat.apprentice) == 1:
                apps = 'apprentice: ' + str(the_cat.apprentice[0].name)
            else:
                apps = 'apprentices: '
                for cat in the_cat.apprentice:
                    apps += str(cat.name) + ', '
                apps = apps[:len(apps) - 2]
            verdana_small.text(apps, (450, 330 + count2 * 15))
            count2 += 1
        if len(the_cat.former_apprentices
               ) != 0 and the_cat.former_apprentices[0] is not None:
            if len(the_cat.former_apprentices) == 1:
                former_apps = 'former apprentice: ' + str(
                    the_cat.former_apprentices[0].name)
            else:
                former_apps = 'former apprentices: '
                for cat in the_cat.former_apprentices:
                    former_apps += str(cat.name) + ', '
                former_apps = former_apps[:len(former_apps) - 2]
            verdana_small.text(former_apps, (450, 330 + count2 * 15))
            count2 += 1
        if the_cat.age == 'kitten':
            verdana_small.text('young', (250, 330 + count * 15))
        elif the_cat.age == 'elder':
            verdana_small.text('senior', (250, 330 + count * 15))
        else:
            verdana_small.text(the_cat.age, (250, 330 + count * 15))
        count += 1  # AGE
        verdana_small.text(the_cat.trait, (450, 330 + count2 * 15))
        count2 += 1  # CHARACTER TRAIT
        verdana_small.text(the_cat.skill, (450, 330 + count2 * 15))
        count2 += 1  # SPECIAL SKILL
        verdana_small.text('eyes: ' + the_cat.eye_colour.lower(),
                           (250, 330 + count * 15))
        count += 1  # EYE COLOR
        verdana_small.text('pelt: ' + the_cat.pelt.name.lower(),
                           (250, 330 + count * 15))
        count += 1  # PELT TYPE
        verdana_small.text('fur length: ' + the_cat.pelt.length,
                           (250, 330 + count * 15))
        count += 1  # PELT LENGTH

        # PARENTS
        if the_cat.parent1 is None:
            verdana_small.text('parents: unknown', (250, 330 + count * 15))
            count += 1
        elif the_cat.parent2 is None:
            par1 = str(the_cat.all_cats[the_cat.parent1].name)
            verdana_small.text('parents: ' + par1 + ', unknown',
                               (250, 330 + count * 15))
            count += 1
        else:
            if the_cat.parent1 in the_cat.all_cats and the_cat.parent2 in the_cat.all_cats:
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            elif the_cat.parent1 in the_cat.all_cats:
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
            elif the_cat.parent2 in the_cat.all_cats:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            else:
                par1 = "Error: Cat#" + the_cat.parent1 + " not found"
                par2 = "Error: Cat#" + the_cat.parent2 + " not found"

            verdana_small.text('parents: ' + par1 + ' and ' + par2,
                               (250, 330 + count * 15))
            count += 1

        # MOONS
        if the_cat.dead:
            if the_cat.moons == 1:
                verdana_small.text(
                    str(the_cat.moon) + ' moons (in life)',
                    (250, 330 + count * 15))
                count += 1
            elif the_cat.moons != 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moons (in life)',
                    (250, 330 + count * 15))
                count += 1
            if the_cat.dead_for == 1:
                verdana_small.text(
                    str(the_cat.dead_for) + ' moon (in death)',
                    (250, 330 + count * 15))
                count += 1
            elif the_cat.dead_for != 1:
                verdana_small.text(
                    str(the_cat.dead_for) + ' moons (in death)',
                    (250, 330 + count * 15))
                count += 1
        else:
            if the_cat.moons == 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moon', (250, 330 + count * 15))
                count += 1
            elif the_cat.moons != 1:
                verdana_small.text(
                    str(the_cat.moons) + ' moons', (250, 330 + count * 15))
                count += 1

        # MATE
        if the_cat.mate is not None and not the_cat.dead:
            if the_cat.mate in cat_class.all_cats:
                if cat_class.all_cats.get(
                        the_cat.mate
                ).dead:  # TODO: fix when mate dies mate becomes none
                    verdana_small.text(
                        'former mate: ' +
                        str(cat_class.all_cats[the_cat.mate].name),
                        (250, 330 + count * 15))
                else:
                    verdana_small.text(
                        'mate: ' + str(cat_class.all_cats[the_cat.mate].name),
                        (250, 330 + count * 15))
                count += 1
            else:
                verdana_small.text(
                    'Error: mate: ' + str(the_cat.mate) + " not found",
                    ('center', 495))

        # experience
        if not the_cat.dead:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (450, 330 + count2 * 15))
            count2 += 1
        else:
            verdana_small.text('experience: ' + str(the_cat.experience_level),
                               (450, 330 + count2 * 15))
            count2 += 1

        # buttons

        buttons.draw_button(
            ('center', -100),
            text='Choose as ' + str(game.switches['apprentice'].name) +
            '\'s mentor',
            cur_screen=game.switches['last_screen'],
            cat_value=the_cat,
            apprentice=game.switches['apprentice'])
        buttons.draw_button(('center', -50),
                            text='Back',
                            cur_screen='clan screen',
                            hotkey=[0])


class ChangeNameScreen(Screens):

    def on_use(self):
        if game.settings['dark mode']:
            pygame.draw.rect(screen, 'white', pygame.Rect((300, 200),
                                                          (200, 20)))
            verdana_black.text(game.switches['naming_text'], (315, 200))
        else:
            pygame.draw.rect(screen, 'gray', pygame.Rect((300, 200),
                                                         (200, 20)))
            verdana.text(game.switches['naming_text'], (315, 200))
        verdana.text('Change Name', ('center', 50))
        verdana.text('Add a space between the new prefix and suffix',
                     ('center', 70))
        verdana.text('i.e. Fire heart', ('center', 90))
        buttons.draw_button(('center', -100),
                            text='Change Name',
                            cur_screen='change name screen',
                            cat_value=game.switches['name_cat'])
        buttons.draw_button(('center', -50),
                            text='Back',
                            cur_screen='profile screen',
                            hotkey=[0])


class ChangeGenderScreen(Screens):

    def on_use(self):
        if game.settings['dark mode']:
            pygame.draw.rect(screen, 'white', pygame.Rect((300, 200),
                                                          (200, 20)))
            verdana_black.text(game.switches['naming_text'], (315, 200))
        else:
            pygame.draw.rect(screen, 'gray', pygame.Rect((300, 200),
                                                         (200, 20)))
            verdana.text(game.switches['naming_text'], (315, 200))
        verdana.text('Change Gender', ('center', 50))
        verdana.text('You can set this to anything.', ('center', 70))
        buttons.draw_button(('center', -100),
                            text=' Change Gender ',
                            cur_screen='change gender screen',
                            cat_value=game.switches['name_cat'])
        buttons.draw_button(('center', -50),
                            text='Back',
                            cur_screen='profile screen',
                            hotkey=[0])


class OptionsScreen(Screens):

    def relations_tab(self):
        buttons.draw_button((10, 85), text="Relations Tab", available=False)
        buttons.draw_button((150, 85),
                            text="Roles Tab",
                            options_tab="Roles Tab",
                            hotkey=[12])
        buttons.draw_button((260, 85),
                            text="Personal Tab",
                            options_tab="Personal Tab",
                            hotkey=[13])
        buttons.draw_button((-10, 85),
                            text="Dangerous Tab",
                            options_tab="Dangerous Tab",
                            hotkey=[14])

        the_cat = cat_class.all_cats.get(game.switches['cat'])
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50
        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='See Family',
                            cur_screen='see kits screen',
                            hotkey=[button_count + 1])
        button_count += 1

        # buttons.draw_button((x_value, y_value + button_count * y_change),
        #                     text='Family Tree',
        #                     hotkey=[button_count + 1])
        # button_count += 1

        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='See Relationships',
                            cur_screen='relationship screen',
                            hotkey=[button_count + 1])
        button_count += 1

        if the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'
                           ] and not the_cat.dead:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Pick mate for ' + str(the_cat.name),
                                cur_screen='choose mate screen',
                                hotkey=[button_count + 1])
            button_count += 1

        if the_cat.status == 'apprentice' and not the_cat.dead:
            game.switches['apprentice'] = the_cat
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change Mentor',
                                cur_screen='choose mentor screen',
                                hotkey=[button_count + 1])
            button_count += 1

        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='Back',
                            cur_screen='profile screen',
                            hotkey=[0])

    def roles_tab(self):
        buttons.draw_button((10, 85),
                            text="Relations Tab",
                            options_tab="Relations Tab",
                            hotkey=[11])
        buttons.draw_button((150, 85), text="Roles Tab", available=False)
        buttons.draw_button((260, 85),
                            text="Personal Tab",
                            options_tab="Personal Tab",
                            hotkey=[13])
        buttons.draw_button((-10, 85),
                            text="Dangerous Tab",
                            options_tab="Dangerous Tab",
                            hotkey=[14])

        the_cat = cat_class.all_cats.get(game.switches['cat'])
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50
        if game.switches['new_leader'] is not False and game.switches[
                'new_leader'] is not None:
            game.clan.new_leader(game.switches['new_leader'])
        if the_cat.status in ['warrior'
                              ] and not the_cat.dead and game.clan.leader.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Promote to Leader',
                                new_leader=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        elif the_cat.status in [
                'warrior'
        ] and not the_cat.dead and game.clan.deputy is None and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Promote to Deputy',
                                deputy_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        elif the_cat.status in ['deputy'] and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Demote from Deputy',
                                deputy_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        elif the_cat.status in ['warrior'
                                ] and not the_cat.dead and game.clan.deputy:
            if game.clan.deputy.dead and not the_cat.exiled:
                buttons.draw_button(
                    (x_value, y_value + button_count * y_change),
                    text='Promote to Deputy',
                    deputy_switch=the_cat,
                    hotkey=[button_count + 1])
                button_count += 1

        if the_cat.status in ['apprentice'] and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Switch to medicine cat apprentice',
                                apprentice_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.status in ['medicine cat apprentice'
                                ] and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Switch to warrior apprentice',
                                apprentice_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.status == 'warrior' and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Switch to medicine cat',
                                apprentice_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.status == 'medicine cat' and not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Switch to warrior',
                                apprentice_switch=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='Back',
                            cur_screen='profile screen',
                            hotkey=[0])

    def personal_tab(self):
        buttons.draw_button((10, 85),
                            text="Relations Tab",
                            options_tab="Relations Tab",
                            hotkey=[11])
        buttons.draw_button((150, 85),
                            text="Roles Tab",
                            options_tab="Roles Tab",
                            hotkey=[12])
        buttons.draw_button((260, 85), text="Personal Tab", available=False)
        buttons.draw_button((-10, 85),
                            text="Dangerous Tab",
                            options_tab="Dangerous Tab",
                            hotkey=[14])

        the_cat = cat_class.all_cats.get(game.switches['cat'])
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50

        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='Change Name',
                            cur_screen='change name screen',
                            hotkey=[button_count + 1])
        button_count += 1
        game.switches['name_cat'] = the_cat.ID

        if the_cat.genderalign == "female":
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Trans Male',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Nonbinary/Specify Gender',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.genderalign == "male":
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Trans Female',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Nonbinary/Specify Gender',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1
        elif the_cat.genderalign == "nonbinary":
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Specify Gender',
                                cur_screen='change gender screen',
                                hotkey=[button_count + 1])
            button_count += 1
        if the_cat.genderalign != "female" and the_cat.genderalign != "male":
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Change to Cisgender',
                                cat_value=game.switches['cat'],
                                hotkey=[button_count + 1])
            button_count += 1

        if the_cat.age in ['young adult', 'adult', 'senior adult'
                           ] and not the_cat.no_kits:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Prevent kits',
                                no_kits=True,
                                cat_value=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        elif the_cat.age in ['young adult', 'adult', 'senior adult'
                             ] and the_cat.no_kits:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Allow kits',
                                no_kits=False,
                                cat_value=the_cat,
                                hotkey=[button_count + 1])
            button_count += 1

        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='Back',
                            cur_screen='profile screen',
                            hotkey=[0])

    def dangerous_tab(self):
        buttons.draw_button((10, 85),
                            text="Relations Tab",
                            options_tab="Relations Tab",
                            hotkey=[1])
        buttons.draw_button((150, 85),
                            text="Roles Tab",
                            options_tab="Roles Tab",
                            hotkey=[2])
        buttons.draw_button((260, 85),
                            text="Personal Tab",
                            options_tab="Personal Tab",
                            hotkey=[3])
        buttons.draw_button((-10, 85), text="Dangerous Tab", available=False)

        the_cat = cat_class.all_cats.get(game.switches['cat'])
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50

        if not the_cat.dead and not the_cat.exiled:
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Exile Cat',
                                cat_value=game.switches['cat'],
                                hotkey=[12],
                                cur_screen='other screen')
            button_count += 1
            buttons.draw_button((x_value, y_value + button_count * y_change),
                                text='Kill Cat',
                                kill_cat=the_cat,
                                hotkey=[11])
            button_count += 1
        # elif the_cat.dead and not the_cat.exiled:
        #     buttons.draw_button((x_value, y_value + button_count * y_change),
        #                         text='Exile to Dark Forest',
        #                         cat_value=game.switches['cat'],
        #                         hotkey=[11])
        #     button_count += 1

        buttons.draw_button((x_value, y_value + button_count * y_change),
                            text='Back',
                            cur_screen='profile screen',
                            hotkey=[0])

    def on_use(self):
        the_cat = cat_class.all_cats.get(game.switches['cat'])
        verdana_big.text('Options - ' + str(the_cat.name), ('center', 40))
        button_count = 0
        x_value = 'center'
        y_value = 150
        y_change = 50

        if game.switches['options_tab'] == "Relations Tab":
            self.relations_tab()
        elif game.switches['options_tab'] == "Roles Tab":
            self.roles_tab()
        elif game.switches['options_tab'] == "Personal Tab":
            self.personal_tab()
        elif game.switches['options_tab'] == "Dangerous Tab":
            self.dangerous_tab()
        else:
            self.relations_tab()

        if game.switches['deputy_switch'] is not False and game.switches[
                'deputy_switch'] is not None and game.switches[
                    'deputy_switch'].status == 'warrior':
            game.clan.deputy = game.switches['deputy_switch']
            game.switches['deputy_switch'].status_change('deputy')
            game.switches['deputy_switch'] = False
        elif game.switches['deputy_switch'] is not False and game.switches[
                'deputy_switch'] is not None and game.switches[
                    'deputy_switch'].status == 'deputy':
            game.clan.deputy = None
            game.switches['deputy_switch'].status_change('warrior')
            game.switches['deputy_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches[
                'apprentice_switch'] is not None and game.switches[
                    'apprentice_switch'].status == 'apprentice':
            game.switches['apprentice_switch'].status_change(
                'medicine cat apprentice')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches[
                'apprentice_switch'] is not None and game.switches[
                    'apprentice_switch'].status == 'medicine cat apprentice':
            game.switches['apprentice_switch'].status_change('apprentice')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches[
                'apprentice_switch'] is not None and game.switches[
                    'apprentice_switch'].status == 'warrior':
            game.switches['apprentice_switch'].status_change('medicine cat')
            game.switches['apprentice_switch'] = False

        if game.switches['apprentice_switch'] is not False and game.switches[
                'apprentice_switch'] is not None and game.switches[
                    'apprentice_switch'].status == 'medicine cat':
            game.switches['apprentice_switch'].status_change('warrior')
            game.switches['apprentice_switch'] = False

        if game.switches['kill_cat'] is not False and game.switches[
                'kill_cat'] is not None:
            if game.switches['kill_cat'].status == 'leader':
                game.clan.leader_lives -= 10
            events_class.dies(game.switches['kill_cat'])
            game.switches['kill_cat'] = False


class StatsScreen(Screens):

    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        living_num = 0
        warriors_num = 0
        app_num = 0
        kit_num = 0
        elder_num = 0
        starclan_num = 0
        for cat in cat_class.all_cats.values():
            if not cat.dead:
                living_num += 1
                if cat.status == 'warrior':
                    warriors_num += 1
                elif cat.status in ['apprentice', 'medicine cat apprentice']:
                    app_num += 1
                elif cat.status == 'kitten':
                    kit_num += 1
                elif cat.status == 'elder':
                    elder_num += 1
            else:
                starclan_num += 1

        verdana.text('Number of Living Cats: ' + str(living_num), (100, 150))
        verdana.text('Number of Warriors: ' + str(warriors_num), (100, 200))
        verdana.text('Number of Apprentices: ' + str(app_num), (100, 250))
        verdana.text('Number of Kits: ' + str(kit_num), (100, 300))
        verdana.text('Number of Elders: ' + str(elder_num), (100, 350))
        verdana.text('Number of StarClan Cats: ' + str(starclan_num),
                     (100, 400))
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

    def screen_switches(self):
        try:
            game.map_info = load_map('saves/' + game.clan.name)
            print("Map loaded.")
        except:
            game.map_info = load_map("Fallback")
            print("Default map loaded.")


class RelationshipScreen(Screens):
    bool = {True: 'on', False: 'off', None: 'None'}

    def on_use(self):
        # get the relevant cat
        the_cat = cat_class.all_cats.get(game.switches['cat'])

        # use this variable to point to the cat object in question
        the_cat = cat_class.all_cats.get(game.switches['cat'],
                                         game.clan.instructor)
        # use these attributes to create differing profiles for starclan cats etc.
        is_instructor = False
        if the_cat.dead and game.clan.instructor.ID == the_cat.ID:
            is_instructor = True

        # back and next buttons on the relationships page
        previous_cat = 0
        next_cat = 0

        if the_cat.dead and not is_instructor:
            previous_cat = game.clan.instructor.ID
        if is_instructor:
            next_cat = 1
        for check_cat in cat_class.all_cats:
            if cat_class.all_cats[check_cat].ID == the_cat.ID:
                next_cat = 1
            if next_cat == 0 and cat_class.all_cats[
                    check_cat].ID != the_cat.ID and cat_class.all_cats[
                        check_cat].dead == the_cat.dead and cat_class.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not cat_class.all_cats[
                                check_cat].exiled:
                previous_cat = cat_class.all_cats[check_cat].ID
            elif next_cat == 1 and cat_class.all_cats[
                    check_cat].ID != the_cat.ID and cat_class.all_cats[
                        check_cat].dead == the_cat.dead and cat_class.all_cats[
                            check_cat].ID != game.clan.instructor.ID and not cat_class.all_cats[
                                check_cat].exiled:
                next_cat = cat_class.all_cats[check_cat].ID
            elif int(next_cat) > 1:
                break
        if next_cat == 1:
            next_cat = 0
        if next_cat != 0:
            buttons.draw_button((-40, 40),
                                text='Next Cat',
                                cat=next_cat,
                                hotkey=[21])
        if previous_cat != 0:
            buttons.draw_button((40, 40),
                                text='Previous Cat',
                                cat=previous_cat,
                                hotkey=[23])

        # button for better displaying
        verdana_small.text(
            f"Display dead {self.bool[game.settings['show dead relation']]}",
            (50, 650))
        buttons.draw_button((50, 670),
                            text='switch',
                            setting='show dead relation')

        verdana_small.text(
            f"Display empty value {self.bool[game.settings['show empty relation']]}",
            (180, 650))
        buttons.draw_button((180, 670),
                            text='switch',
                            setting='show empty relation')

        # make a list of the relationships
        search_text = game.switches['search_text']
        pygame.draw.rect(screen, 'lightgray', pygame.Rect((620, 670),
                                                          (150, 20)))
        verdana.text('Search: ', (550, 670))
        verdana_black.text(game.switches['search_text'], (630, 670))
        search_relations = []
        if search_text.strip() != '':
            for rel in the_cat.relationships:
                if search_text.lower() in str(rel.cat_to.name).lower():
                    search_relations.append(rel)
        else:
            search_relations = the_cat.relationships.copy()

        # layout
        verdana_big.text(str(the_cat.name) + ' Relationships', ('center', 10))
        if the_cat != None and the_cat.mate != '':
            mate = cat_class.all_cats.get(the_cat.mate)
            if mate != None:
                verdana_small.text(
                    f"{str(the_cat.genderalign)}  - {str(the_cat.age)} -  mate: {str(mate.name)}",
                    ('center', 40))
            else:
                verdana_small.text(
                    f"{str(the_cat.genderalign)}  - {str(the_cat.age)}",
                    ('center', 40))
        else:
            verdana_small.text(
                f"{str(the_cat.genderalign)}  - {str(the_cat.age)}",
                ('center', 40))

        # filter relationships pased on the settings
        if not game.settings['show dead relation']:
            search_relations = list(
                filter(lambda rel: not rel.cat_to.dead, search_relations))

        if not game.settings['show empty relation']:
            search_relations = list(
                filter(
                    lambda rel: (rel.romantic_love + rel.platonic_like + rel.
                                 dislike + rel.admiration + rel.comfortable +
                                 rel.jealousy + rel.trust) > 0, search_relations))

        # pages
        all_pages = 1  # amount of pages
        if len(search_relations) > 10:
            all_pages = int(ceil(len(search_relations) / 10))

        pos_x = 0
        pos_y = 0
        cats_on_page = 0  # how many are on page already
        for x in range(len(search_relations)):
            if (x +
                (game.switches['list_page'] - 1) * 10) > len(search_relations):
                game.switches['list_page'] = 1
            if game.switches['list_page'] > all_pages:
                game.switches['list_page'] = 1
            the_relationship = search_relations[x +
                                             (game.switches['list_page'] - 1) *
                                             10]
            the_relationship.cat_to.update_sprite()
            buttons.draw_button((90 + pos_x, 60 + pos_y),
                                image=the_relationship.cat_to.sprite,
                                cat=the_relationship.cat_to.ID,
                                cur_screen='relationship screen')
            # name length
            string_len = verdana.text(str('romantic love: '))
            verdana.text(str(the_relationship.cat_to.name),
                         (140 + pos_x - string_len / 1.5, 105 + pos_y))
            verdana_small.text(
                f"{str(the_relationship.cat_to.genderalign)} - {str(the_relationship.cat_to.age)}",
                (140 + pos_x - string_len / 1.5, 120 + pos_y))

            # there is no way the mate is dead
            uncle_aunt = the_relationship.cat_to.is_uncle_aunt(the_cat) or\
                the_cat.is_uncle_aunt(the_relationship.cat_to)
            if (the_relationship.family or uncle_aunt) and the_relationship.cat_to.dead:
                verdana_small.text(
                    'related (dead)',
                    (140 + pos_x - string_len / 1.5, 130 + pos_y))
            elif (the_relationship.family or uncle_aunt):
                verdana_small.text(
                    'related', (140 + pos_x - string_len / 1.5, 130 + pos_y))
            elif the_relationship.cat_to.dead:
                verdana_small.text(
                    '(dead)', (140 + pos_x - string_len / 1.5, 130 + pos_y))

            if the_cat.mate != None and the_cat.mate != '' and the_relationship.cat_to.ID == the_cat.mate:
                verdana_small.text(
                    'mate', (140 + pos_x - string_len / 1.5, 140 + pos_y))
            elif the_relationship.cat_to.mate != None and the_relationship.cat_to.mate != '':
                verdana_small.text(
                    'has a mate',
                    (140 + pos_x - string_len / 1.5, 140 + pos_y))

            count = 15
            different_age = the_relationship.cat_to.age != the_relationship.cat_to.age
            adult_ages = ['young adult', 'adult', 'senior adult', 'elder']
            both_adult = the_relationship.cat_to.age in adult_ages and the_relationship.cat_to.age in adult_ages
            check_age = (different_age and both_adult) or both_adult
            if the_relationship.romantic_love > 49 and game.settings[
                    'dark mode'] and check_age:
                verdana_dark_margenta.text(
                    'romantic love:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            elif the_relationship.romantic_love > 49 and not game.settings[
                    'dark mode'] and check_age:
                verdana_margenta.text(
                    'romantic love:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            else:
                verdana_small.text(
                    'romantic like:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            count += 20
            current_x = 140 + pos_x - string_len / 1.5
            current_y = 145 + pos_y + count
            if (different_age and both_adult) or both_adult:
                draw_bar(the_relationship.romantic_love, current_x, current_y)
            else:
                draw_bar(0, current_x, current_y)
            count += 5

            if the_relationship.platonic_like > 49 and game.settings[
                    'dark mode']:
                verdana_dark_margenta.text(
                    'platonic love:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            elif the_relationship.platonic_like > 49 and not game.settings[
                    'dark mode']:
                verdana_margenta.text(
                    'platonic love:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            else:
                verdana_small.text(
                    'platonic like:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            count += 20
            current_x = 140 + pos_x - string_len / 1.5
            current_y = 145 + pos_y + count
            draw_bar(the_relationship.platonic_like, current_x, current_y)
            count += 5

            if the_relationship.dislike > 49 and game.settings['dark mode']:
                verdana_dark_margenta.text(
                    'hate:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            elif the_relationship.dislike > 49 and not game.settings[
                    'dark mode']:
                verdana_margenta.text(
                    'hate:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            else:
                verdana_small.text(
                    'dislike:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            count += 20
            current_x = 140 + pos_x - string_len / 1.5
            current_y = 145 + pos_y + count
            draw_bar(the_relationship.dislike, current_x, current_y)
            count += 5

            if the_relationship.admiration > 49 and game.settings['dark mode']:
                verdana_dark_margenta.text(
                    'admiration:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            elif the_relationship.admiration > 49 and not game.settings[
                    'dark mode']:
                verdana_margenta.text(
                    'admiration:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            else:
                verdana_small.text(
                    'respect:',
                    (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            count += 20
            current_x = 140 + pos_x - string_len / 1.5
            current_y = 145 + pos_y + count
            draw_bar(the_relationship.admiration, current_x, current_y)
            count += 5

            verdana_small.text(
                'comfortable:',
                (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            count += 20
            current_x = 140 + pos_x - string_len / 1.5
            current_y = 145 + pos_y + count
            draw_bar(the_relationship.comfortable, current_x, current_y)
            count += 5

            verdana_small.text(
                'jealousy:',
                (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            count += 20
            current_x = 140 + pos_x - string_len / 1.5
            current_y = 145 + pos_y + count
            draw_bar(the_relationship.jealousy, current_x, current_y)
            count += 5

            verdana_small.text(
                'trust:',
                (140 + pos_x - string_len / 1.5, 145 + pos_y + count))
            count += 20
            current_x = 140 + pos_x - string_len / 1.5
            current_y = 145 + pos_y + count
            draw_bar(the_relationship.trust, current_x, current_y)

            cats_on_page += 1
            pos_x += 140
            if pos_x >= 650:
                pos_x = 0
                pos_y += 100 + count

            if cats_on_page >= 10 or x + (game.switches['list_page'] -
                                          1) * 10 == len(search_relations) - 1:
                break

        # page buttons
        verdana.text(
            'page ' + str(game.switches['list_page']) + ' / ' + str(all_pages),
            ('center', 640))
        if game.switches['list_page'] > 1:
            buttons.draw_button((320, 640),
                                text='<',
                                list_page=game.switches['list_page'] - 1,
                                hotkey=[23])
        if game.switches['list_page'] < all_pages:

            buttons.draw_button((-320, 640),
                                text='>',
                                list_page=game.switches['list_page'] + 1,
                                hotkey=[21])

        buttons.draw_button(('center', 670),
                            text='Back',
                            cur_screen='profile screen')

    def screen_switches(self):
        cat_profiles()


class RelationshipEventScreen(Screens):

    def on_use(self):
        a = 0
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        verdana.text(
            'Check this page to see which events are currently happening at the Clan.',
            ('center', 110))

        verdana.text(f'Current season: {str(game.clan.current_season)}',
                     ('center', 140))

        if game.clan.age == 1:
            verdana.text(f'Clan age: {str(game.clan.age)} moon',
                         ('center', 170))
        if game.clan.age != 1:
            verdana.text(f'Clan age: {str(game.clan.age)} moons',
                         ('center', 170))

        if game.switches['events_left'] == 0:
            buttons.draw_button((200, 220),
                                text='TIMESKIP ONE MOON',
                                timeskip=True,
                                hotkey=[11])
            if game.switches['timeskip']:
                game.cur_events_list = []
                game.relation_events_list = []
        else:
            buttons.draw_button((200, 220),
                                text='TIMESKIP ONE MOON',
                                available=False)
        events_class.one_moon()

        # show the clan events
        buttons.draw_button((-250, 220),
                            text='CLAN EVENTS',
                            cur_screen='events screen',
                            hotkey=[12])

        if game.relation_events_list is not None and game.relation_events_list != []:
            for x in range(
                    min(len(game.relation_events_list),
                        game.max_relation_events_displayed)):
                if game.relation_events_list[x] is None:
                    continue
                verdana.text(game.relation_events_list[x],
                             ('center', 260 + a * 30))
                a += 1
        else:
            verdana.text("Nothing significant happened this moon.",
                         ('center', 260 + a * 30))
        # buttons
        draw_menu_buttons()

        if len(game.relation_events_list) > game.max_relation_events_displayed:
            buttons.draw_button((700, 180),
                                image=game.up,
                                arrow="UP",
                                hotkey=[20])
            buttons.draw_button((700, 630),
                                image=game.down,
                                arrow="DOWN",
                                hotkey=[22])

    def screen_switches(self):
        cat_profiles


# SCREENS
screens = Screens()

start_screen = StartScreen('start screen')
settings_screen = SettingsScreen('settings screen')
info_screen = InfoScreen('info screen')
clan_screen = ClanScreen('clan screen')
patrol_screen = PatrolScreen(
    'patrol screen')  # for picking cats to go on patrol
patrol_event_screen = PatrolEventScreen(
    'patrol event screen')  # for seeing the events of the patrol
starclan_screen = StarClanScreen('starclan screen')
make_clan_screen = MakeClanScreen('make clan screen')
clan_created_screen = ClanCreatedScreen('clan created screen')
events_screen = EventsScreen('events screen')
profile_screen = ProfileScreen('profile screen')
single_event_screen = SingleEventScreen('single event screen')
choose_mate_screen = ChooseMateScreen('choose mate screen')
view_children_screen = ViewChildrenScreen('see kits screen')
list_screen = ListScreen('list screen')
switch_clan_screen = SwitchClanScreen('switch clan screen')
allegiances_screen = AllegiancesScreen('allegiances screen')
choose_mentor_screen = ChooseMentorScreen('choose mentor screen')
choose_mentor_screen2 = ChooseMentorScreen2('choose mentor screen2')
change_name_screen = ChangeNameScreen('change name screen')
change_gender_screen = ChangeGenderScreen('change gender screen')
option_screen = OptionsScreen('options screen')
language_screen = LanguageScreen('language screen')
stats_screen = StatsScreen('stats screen')
other_screen = OtherScreen('other screen')
map_screen = MapScreen('map screen')
relationship_screen = RelationshipScreen('relationship screen')
relationship_event_screen = RelationshipEventScreen(
    'relationship event screen')
relattionship_setting_screen = RelationshipSettingsScreen(
    'relationsihp setting screen')


# CAT PROFILES
def cat_profiles():
    game.choose_cats.clear()
    game.cat_buttons.clear()
    for x in game.clan.clan_cats:
        game.choose_cats[x] = cat_class.all_cats[x]
        game.choose_cats[x].update_sprite()


def draw_menu_buttons():
    buttons.draw_button((260, 70),
                        text='EVENTS',
                        cur_screen='events screen',
                        hotkey=[2])
    buttons.draw_button((340, 70),
                        text='CLAN',
                        cur_screen='clan screen',
                        hotkey=[3])
    buttons.draw_button((400, 70),
                        text='STARCLAN',
                        cur_screen='starclan screen',
                        hotkey=[4])
    buttons.draw_button((500, 70),
                        text='PATROL',
                        cur_screen='patrol screen',
                        hotkey=[5])
    buttons.draw_button((50, 50),
                        text='< Back to Main Menu',
                        cur_screen='start screen',
                        hotkey=[0])
    buttons.draw_button((-70, 50),
                        text='List Cats',
                        cur_screen='list screen',
                        hotkey=[6])
    buttons.draw_button((-70, 80),
                        text='Allegiances',
                        cur_screen='allegiances screen',
                        hotkey=[7])
    buttons.draw_button((-70, 110),
                        text='Map',
                        cur_screen='map screen',
                        available=mapavailable,
                        hotkey=[8])
    buttons.draw_button((50, 80),
                        text='Stats',
                        cur_screen='stats screen',
                        hotkey=[1])