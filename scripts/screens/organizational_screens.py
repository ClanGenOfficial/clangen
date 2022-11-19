import pygame

from .base_screens import Screens, draw_menu_buttons, draw_clan_name

from scripts.clan import map_available
from scripts.cat.cats import Cat
# from scripts.world import save_map
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
                                      cur_screen='clan screen',
                                      size=(192, 35))
            buttons.draw_image_button((70, 355),
                                      button_name='switch_clan',
                                      text='Switch Clan >',
                                      cur_screen='switch clan screen',
                                      size=(192, 35))
        elif game.clan is not None and game.switches['error_message']:
            buttons.draw_image_button((70, 310),
                                      button_name='continue',
                                      text='Continue >',
                                      available=False,
                                      size=(192, 35))
            buttons.draw_image_button((70, 355),
                                      button_name='switch_clan',
                                      text='Switch Clan >',
                                      cur_screen='switch clan screen',
                                      size=(192, 35))
        else:
            buttons.draw_image_button((70, 310),
                                      button_name='continue',
                                      text='Continue >',
                                      available=False,
                                      size=(192, 35))
            buttons.draw_image_button((70, 355),
                                      button_name='switch_clan',
                                      text='Switch Clan >',
                                      available=False,
                                      size=(192, 35))
        buttons.draw_image_button((70, 400),
                                  button_name='new_clan',
                                  text='Make New >',
                                  cur_screen='make clan screen',
                                  size=(192, 35))
        buttons.draw_image_button((70, 445),
                                  button_name='settings',
                                  text='Settings & Info >',
                                  cur_screen='settings screen',
                                  size=(192, 35))

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

    saves_frame = pygame.image.load("resources/images/clan_saves_frame.png").convert_alpha()

    def on_use(self):

        game.switches['read_clans'] = True

        y_pos = 150
        screen.blit(SwitchClanScreen.saves_frame, (290, y_pos))
        y_pos += 39

        for i in range(len(game.switches['clan_list'])):
            if len(game.switches['clan_list'][i]) > 1 and i <= 7:
                buttons.draw_button(
                    (290, y_pos),
                    text=game.switches['clan_list'][i] + 'clan',
                    image='buttons/clan_save',
                    switch_clan=game.switches['clan_list'][i],
                    hotkey=[i + 1])
                verdana_dark.text(str(game.switches['clan_list'][i] + 'clan'), ('center', y_pos + 10))
            y_pos += 41

        y_pos = 540
        verdana.text(
            'Note: This will close the game.',
            ('center', y_pos))
        y_pos += 25
        verdana.text(
            'When you open it next, it should have the new clan.',
            ('center', y_pos))
        buttons.draw_image_button((25, 25),
                                  button_name='main_menu',
                                  text='< Back to Main Menu',
                                  cur_screen='start screen',
                                  size=(153, 30),
                                  hotkey=[0])


def draw_settings_header():
    buttons.draw_image_button((100, 100),
                              button_name='general_settings',
                              size=(150, 30),
                              cur_screen='settings screen')

    buttons.draw_image_button((250, 100),
                              button_name='relation_settings',
                              size=(150, 30),
                              cur_screen='relationship setting screen')
    buttons.draw_image_button((400, 100),
                              button_name='info',
                              size=(150, 30),
                              cur_screen='info screen')

    buttons.draw_image_button((550, 100),
                              button_name='language',
                              size=(150, 30),
                              cur_screen='language screen')


def draw_back_and_save():
    buttons.draw_image_button((25, 25),
                              button_name='main_menu',
                              text='< Back to Main Menu',
                              cur_screen='start screen',
                              size=(153, 30),
                              hotkey=[0])
    if game.settings_changed:
        buttons.draw_image_button((327, 550),
                                  button_name='save_settings',
                                  text='Save Settings',
                                  size=(146, 30),
                                  save_settings=True)
    else:
        buttons.draw_image_button((327, 550),
                                  button_name='save_settings',
                                  text='Save Settings',
                                  size=(146, 30),
                                  available=False)


# ON / OFF BUTTONS
def draw_on_off(y_value, setting):
    x_value = 120
    if game.settings[setting] is True:
        buttons.draw_image_button((x_value, y_value),
                                  button_name='on',
                                  size=(46, 34),
                                  setting=setting
                                  )
        buttons.draw_image_button((x_value + 46, y_value),
                                  button_name='off',
                                  size=(46, 34),
                                  setting=setting,
                                  available=False
                                  )

    if game.settings[setting] is False:
        buttons.draw_image_button((x_value, y_value),
                                  button_name='on',
                                  size=(46, 34),
                                  setting=setting,
                                  available=False
                                  )
        buttons.draw_image_button((x_value + 46, y_value),
                                  button_name='off',
                                  size=(46, 34),
                                  setting=setting,
                                  )


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
        verdana.text("Change the settings of your game here.", ('center', 160))

        # Setting names
        x_value = 225
        verdana.text("Dark mode", (x_value, 226))
        verdana.text("Enable clan page background", (x_value, 265))
        verdana.text("Automatically save every five moons", (x_value, 304))
        verdana.text("Allow mass extinction events", (x_value, 343))
        verdana.text("Force cats to retire after severe injury", (x_value, 382))
        verdana.text("Enable shaders", (x_value, 421))
        verdana.text("Display hotkeys on text buttons", (x_value, 460))
        verdana.text("Allow leaders to automatically choose a new deputy", (x_value, 499))


        # Setting values
        draw_on_off(220, 'dark mode')
        draw_on_off(259, 'backgrounds')
        draw_on_off(298, 'autosave')
        draw_on_off(337, 'disasters')
        draw_on_off(376, 'retirement')
        draw_on_off(415, 'shaders')
        draw_on_off(454, 'hotkey display')
        draw_on_off(493, 'deputy')

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
        verdana.text("Change the settings of the relationships here.",
                     ('center', 160))

        # Setting names
        x_value = 225
        verdana.text("Randomize relationship values, when creating clan", (x_value, 226))
        verdana.text("Allow affairs and mate switches based on relationships", (x_value, 265))
        verdana.text("Allow couples to have kittens despite same-sex status", (x_value, 304))
        verdana.text("Allow unmated cats to have offspring", (x_value, 343))
        verdana.text("Allow romantic interactions with former apprentices/mentor", (x_value, 382))

        # Setting values
        draw_on_off(220, 'random relation')
        draw_on_off(259, 'affair')
        draw_on_off(298, 'no gendered breeding')
        draw_on_off(337, 'no unknown fathers')
        draw_on_off(376, 'romantic with former mentor')

        # other buttons
        draw_back_and_save()


class InfoScreen(Screens):

    def on_use(self):
        # layout
        draw_settings_header()

        verdana.text("Welcome to Warrior Cats clan generator!",
                     ('center', 160))
        verdana.text(
            "This is fan-made generator for the Warrior Cats -book series by Erin Hunter.",
            ('center', 205))
        verdana.text(
            "Create a new clan with the 'New Clan' button. 8 clans can be saved and revisited.",
            ('center', 245))
        verdana.text(
            "If you go over that number then the oldest save will be overwritten",
            ('center', 265))
        verdana.text(
            "You're free to use the characters and sprites generated in this program",
            ('center', 315))
        verdana.text(
            "as you like, as long as you don't claim the sprites as your own creations or sell them for any reason.",
            ('center', 335))
        verdana.text("Original creator: just-some-cat.tumblr.com",
                     ('center', 375))
        verdana.text("Fan edit made by: SableSteel", ('center', 395))

        verdana.text("Thank you for playing!!", ('center', 550))

        # other buttons
        buttons.draw_image_button((25, 25),
                                  button_name='main_menu',
                                  text='< Back to Main Menu',
                                  cur_screen='start screen',
                                  size=(153, 30),
                                  hotkey=[0])


class LanguageScreen(Screens):

    def on_use(self):
        # layout
        draw_settings_header()
        verdana.text("Choose the language of your game here:", ('center', 160))

        # Language options

        buttons.draw_image_button((310, 200),
                                  button_name='english',
                                  size=(180, 51),
                                  language='english',
                                  available='english' != game.switches['language'])
        buttons.draw_image_button((310, 251),
                                  button_name='spanish',
                                  size=(180, 37),
                                  language='spanish',
                                  available='spanish' != game.switches['language'])
        buttons.draw_image_button((310, 288),
                                  button_name='german',
                                  size=(180, 37),
                                  language='german',
                                  available='german' != game.switches['language'])

        if game.switches['language'] != game.settings['language']:
            game.settings['language'] = game.switches['language']
            game.settings_changed = True
            if game.settings['language'] != 'english':
                game.switch_language()

        # other buttons
        draw_back_and_save()


class StatsScreen(Screens):

    def on_use(self):
        draw_clan_name()
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
