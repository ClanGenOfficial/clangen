import pygame

from .base_screens import Screens, draw_menu_buttons

from scripts.clan import map_available
from scripts.cat.cats import Cat
#from scripts.world import save_map
from scripts.game_structure.text import *
from scripts.game_structure.buttons import buttons

class StartScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.bg = pygame.image.load("resources/images/menu.png").convert()

    def on_use(self):
        # background
        screen.blit(self.bg, (0, 0))

        # buttons
        if game.clan is not None and game.switches['error_message'] == '':
            buttons.draw_image_button((70, 310),
                                      button_name='continue',
                                      text='Continue >',
                                      cur_screen='clan screen')
            buttons.draw_image_button((70, 355),
                                      button_name='switch_clan',
                                      text='Switch Clan >',
                                      cur_screen='switch clan screen')
        elif game.clan is not None and game.switches['error_message']:
            buttons.draw_image_button((70, 310),
                                      button_name='continue',
                                      text='Continue >',
                                      available=False)
            buttons.draw_image_button((70, 355),
                                      button_name='switch_clan',
                                      text='Switch Clan >',
                                      cur_screen='switch clan screen')
        else:
            buttons.draw_image_button((70, 310),
                                      button_name='continue',
                                      text='Continue >',
                                      available=False)
            buttons.draw_image_button((70, 355),
                                      button_name='switch_clan',
                                      text='Switch Clan >',
                                      available=False)
        buttons.draw_image_button((70, 400),
                                  button_name='new_clan',
                                  text='Make New >',
                                  cur_screen='make clan screen')
        buttons.draw_image_button((70, 445),
                                  button_name='settings',
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
            key_copy = tuple(Cat.all_cats.keys())
            for x in key_copy:
                if x not in game.clan.clan_cats:
                    game.clan.remove_cat(x)

        # SAVE cats
        if game.clan is not None:
            game.save_cats()
            game.clan.save_clan()
            game.clan.save_pregnancy(game.clan)
            #if map_available:
            #    save_map(game.map_info, game.clan.name)

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

def draw_settings_header():
    x_pos = 140
    text = "Settings"
    buttons.draw_button((x_pos, 100),
                text=text,
                cur_screen='settings screen')

    x_pos += 90
    text = "Relation Settings"
    buttons.draw_button((x_pos, 100),
                text=text,
                cur_screen='relationship setting screen')

    x_pos += 155
    text = "Game Modes"
    buttons.draw_button((x_pos, 100),
                text=text,
                cur_screen='game_mode screen')

    x_pos += 125
    text = "Language"
    buttons.draw_button((x_pos, 100),
                text=text,
                cur_screen='language screen')

    x_pos += 100
    text = "Info"
    buttons.draw_button((x_pos, 100),
                text=text,
                cur_screen='info screen')

def draw_back_and_save():
    buttons.draw_button((50, 50),
                            text='<< Back to Main Menu',
                            cur_screen='start screen')
    if game.settings_changed:
        buttons.draw_button(('center', 550),
                                text='Save Settings',
                                save_settings=True)
    else:
        buttons.draw_button(('center', 550),
                                text='Save Settings',
                                available=False)

class SettingsScreen(Screens):
    text_size = {
        '0': 'small',
        '1': 'medium',
        '2': 'big'
    }  # How text sizes will show up on the screen
    bool = {True: 'Yes', False: 'No', None: 'None'}

    def on_use(self):
        # layout
        draw_settings_header()
        verdana.text("Change the setting of your game here.", ('center', 140))

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
        buttons.draw_button((-80, 380),text='SWITCH',setting='hotkey display')

        # other buttons
        draw_back_and_save()

class RelationshipSettingsScreen(Screens):
    text_size = {
        '0': 'small',
        '1': 'medium',
        '2': 'big'
    }  # How text sizes will show up on the screen
    bool = {True: 'Yes', False: 'No', None: 'None'}

    def on_use(self):
        # layout
        draw_settings_header()
        verdana.text("Change the setting of the relationships here.",
                     ('center', 140))

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
        draw_back_and_save()

class InfoScreen(Screens):

    def on_use(self):
        # layout
        draw_settings_header()

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
        draw_settings_header()
        verdana.text("Choose the language of your game here:", ('center', 140))

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
        draw_back_and_save()

class GameModeScreen(Screens):

    def on_use(self):
        # layout
        draw_settings_header()
        verdana.text("Choose the mode of your game here:", ('center', 140))

        # Mode options
        a = 200
        for game_mode in game.setting_lists['game_mode']:
            buttons.draw_button(
                ('center', a),
                text = game_mode,
                game_mode = game_mode,
                available = game_mode != game.switches['game_mode'])
            a += 30
            if game_mode == "classic":
                verdana.text("classic generator game", ('center', a))
                a += 20
                verdana.text("The player doesn't have to organize anything important and can focus on storytelling.", ('center', a))
                a += 50
            elif game_mode == "expanded":
                verdana.text("classic generator game with additional functions", ('center', a))
                a += 20
                verdana.text("The player has to organize and manage some values. Current additions:", ('center', a))
                a += 20
                verdana.text("---", ('center', a))
                a += 50
            elif game_mode == "cruel season":
                verdana.text("like expanded mode, but harder to survive", ('center', a))
                a += 20
                verdana.text("currently not available", ('center', a))
                a += 50

        if game.switches['game_mode'] != game.settings['game_mode']:
            game.settings['game_mode'] = game.switches['game_mode']
            game.settings_changed = True

        # other buttons
        draw_back_and_save()

class StatsScreen(Screens):

    def on_use(self):
        verdana_big.text(f'{game.clan.name}Clan', ('center', 30))
        living_num = 0
        warriors_num = 0
        app_num = 0
        kit_num = 0
        elder_num = 0
        starclan_num = 0
        for cat in Cat.all_cats.values():
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
