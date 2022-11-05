import pygame
import ujson
import os
from ast import literal_eval


screen_x = 800
screen_y = 700
screen = pygame.display.set_mode((screen_x, screen_y), pygame.HWSURFACE)
pygame.display.set_caption('Clan Generator')


# G A M E
class Game():
    # Text box variables
    naming_box = pygame.Surface((140, 20))
    naming_box.fill((230, 230, 230))
    max_name_length = 10
    max_events_displayed = 10
    event_scroll_ct = 0
    max_allegiance_displayed = 17
    allegiance_scroll_ct = 0
    max_relation_events_displayed = 13
    relation_scroll_ct = 0
    cur_events_list = []
    allegiance_list = []
    language = {}
    game_mode = ''
    language_list = ['english', 'spanish', 'german']
    game_mode_list = ['classic', 'expanded', 'cruel season']
    relation_events_list = []

    down = pygame.image.load("resources/images/buttons/arrow_down.png").convert_alpha()
    up = pygame.image.load("resources/images/buttons/arrow_up.png").convert_alpha()

    choose_cats = {}
    cat_buttons = {
        'cat0': None,
        'cat1': None,
        'cat2': None,
        'cat3': None,
        'cat4': None,
        'cat5': None,
        'cat6': None,
        'cat7': None,
        'cat8': None,
        'cat9': None,
        'cat10': None,
        'cat11': None
    }
    patrol_cats = {}
    patrolled = []

    # store changing parts of the game that the user can toggle with buttons
    switches = {
        'cat': None,
        'clan_name': '',
        'leader': None,
        'deputy': None,
        'medicine_cat': None,
        'members': [],
        'event': None,
        'cur_screen': 'start screen',
        'naming_text': '',
        'timeskip': False,
        'mate': None,
        'setting': None,
        'save_settings': False,
        'list_page': 1,
        'last_screen': 'start screen',
        'events_left': 0,
        'save_clan': False,
        'saved_clan': False,
        'new_leader': False,
        'apprentice_switch': False,
        'deputy_switch': False,
        'clan_list': '',
        'switch_clan': False,
        'read_clans': False,
        'kill_cat': False,
        'current_patrol': [],
        'error_message': '',
        'apprentice': None,
        'change_name': '',
        'name_cat': None,
        'biome': None,
        'camp_bg': None,
        'language': 'english',
        'search_text': '',
        'map_selection': (0, 0),
        'world_seed': None,
        'camp_site': (0, 0),
        'choosing_camp': False,
        'hunting_territory': (0, 0),
        'training_territory': (0, 0),
        'options_tab': None,
        'game_mode': '',
        'show_info': False
    }
    all_screens = {}
    cur_events = {}
    map_info = {}

    # SETTINGS
    settings = {
        'no gendered breeding': False,
        'text size': '0',
        'no unknown fathers': False,
        'dark mode': False,
        'backgrounds': True,
        'autosave': False,
        'disasters': False,
        'retirement': True,
        'language': 'english',
        'affair': False,
        'shaders': False,
        'hotkey display': False,
        'random relation': True,
        'show dead relation': True,
        'show empty relation': True,
        'romantic with former mentor': True,
        'game_mode': 'classic'
    }  # The current settings
    setting_lists = {
        'no gendered breeding': [False, True],
        'text size': ['0', '1', '2'],
        'no unknown fathers': [False, True],
        'dark mode': [False, True],
        'backgrounds': [True, False],
        'autosave': [False, True],
        'disasters': [False, True],
        'retirement': [True, False],
        'language': language_list,
        'affair': [False, True],
        'shaders': [False, True],
        'hotkey display': [False, True],
        'random relation': [False, True],
        'show dead relation': [False, True],
        'show empty relation': [False, True],
        'romantic with former mentor': [False, True],
        'game_mode': game_mode_list
    }  # Lists of possible options for each setting
    settings_changed = False

    # CLAN
    clan = None
    cat_class = None

    def __init__(self, current_screen='start screen'):
        self.current_screen = current_screen
        self.clicked = False
        self.keyspressed = []
        self.switch_screens = False

    def update_game(self):
        if self.current_screen != self.switches['cur_screen']:
            self.current_screen = self.switches['cur_screen']
            self.switch_screens = True
        self.clicked = False
        self.keyspressed = []
        # carry commands
        self.carry_commands()

    def carry_commands(self):
        """ Run this function to go through commands added to the switch-dictionary and carry them, then
        reset them back to normal after the action"""
        if self.switches['setting'] is not None:
            if self.switches['setting'] in self.settings.keys():
                self.switch_setting(self.switches['setting'])
            else:
                print('Wrong settings value:', self.switches['setting'])
            self.switches['setting'] = None
        if self.switches['save_settings']:
            self.save_settings()
            self.switches['save_settings'] = False
        if self.switches[
                'save_clan'] and self.clan is not None and self.cat_class is not None:
            self.clan.save_clan()
            self.clan.save_pregnancy(game.clan)
            self.save_cats()
            self.switches['save_clan'] = False
            self.switches['saved_clan'] = True
        if self.switches['switch_clan']:
            self.clan.switch_clans()
            self.switches['switch_clan'] = False
        if self.switches['read_clans']:
            with open('saves/clanlist.txt', 'r') as read_file:
                clan_list = read_file.read()
                if_clans = len(clan_list)
            if if_clans > 0:
                game.switches['clan_list'] = clan_list.split('\n')
            self.switches['read_clans'] = False

    def save_settings(self):
        """ Save user settings for later use """
        data = ''.join(f"{s}:{str(self.settings[s])}" + "\n"
                       for s in self.settings.keys())

        with open('saves/settings.txt', 'w') as write_file:
            write_file.write(data)
        self.settings_changed = False

    def load_settings(self):
        """ Load settings that user has saved from previous use """
        with open('saves/settings.txt', 'r') as read_file:
            settings_data = read_file.read()

        lines = settings_data.split(
            "\n"
        )  # Splits text file into singular lines, each line containing one setting
        # and value

        for x in lines:
            if len(x) > 0:  # If line isn't empty
                parts = x.split(
                    ":")  # first part is setting name, second is value
                # Turn value into right type (int types stay string and will be turned into int when needed)
                # And put it into game settings
                if parts[1] in ['True', 'True ', 'true', ' True']:
                    self.settings[parts[0]] = True
                elif parts[1] in ['False', 'False ', 'false', ' False']:
                    self.settings[parts[0]] = False
                elif parts[1] in ['None', 'None ', 'none', ' None']:
                    self.settings[parts[0]] = None
                else:
                    self.settings[parts[0]] = parts[1]

        self.switches['language'] = self.settings['language']
        self.switches['game_mode'] = self.settings['game_mode']
        if self.settings['language'] != 'english':
            self.switch_language()

    def switch_language(self):
        #add translation information here
        if os.path.exists('languages/' + game.settings['language'] + '.txt'):
            with open('languages/' + game.settings['language'] + '.txt',
                      'r') as read_file:
                raw_language = read_file.read()
            game.language = literal_eval(raw_language)

    def switch_setting(self, setting_name):
        """ Call this function to change a setting given in the parameter by one to the right on it's list """
        self.settings_changed = True

        # Give the index that the list is currently at
        list_index = self.setting_lists[setting_name].index(
            self.settings[setting_name])

        if list_index == len(
                self.setting_lists[setting_name]
        ) - 1:  # The option is at the list's end, go back to 0
            self.settings[setting_name] = self.setting_lists[setting_name][0]
        else:
            # Else move on to the next item on the list
            self.settings[setting_name] = self.setting_lists[setting_name][
                list_index + 1]

    def save_cats(self):
        """Save the cat data."""
        clanname = ''
        if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        elif len(game.switches['clan_name']) > 0:
            clanname = game.switches['clan_list'][0]
        elif game.clan is not None:
            clanname = game.clan.name
        directory = 'saves/' + clanname
        if not os.path.exists(directory):
            os.makedirs(directory)
        clan_cats = []
        for inter_cat in self.cat_class.all_cats.values():
            cat_data = {
                "ID": inter_cat.ID,
                "name_prefix": inter_cat.name.prefix,
                "name_suffix": inter_cat.name.suffix,
                "gender": inter_cat.gender,
                "gender_align": inter_cat.genderalign,
                "birth_cooldown": inter_cat.birth_cooldown,
                "status": inter_cat.status,
                "backstory": inter_cat.backstory if inter_cat.backstory else None,
                "age": inter_cat.age,
                "moons": inter_cat.moons,
                "trait": inter_cat.trait,
                "parent1": inter_cat.parent1,
                "parent2": inter_cat.parent2,
                "mentor": inter_cat.mentor.ID if inter_cat.mentor else None,
                "mate": inter_cat.mate,
                "dead": inter_cat.dead,
                "paralyzed": inter_cat.paralyzed,
                "no_kits": inter_cat.no_kits,
                "exiled": inter_cat.exiled,
                "pelt_name": inter_cat.pelt.name,
                "pelt_color": inter_cat.pelt.colour,
                "pelt_white": inter_cat.pelt.white,
                "pelt_length": inter_cat.pelt.length,
                "spirit_kitten": inter_cat.age_sprites['kitten'],
                "spirit_adolescent": inter_cat.age_sprites['adolescent'],
                "spirit_young_adult": inter_cat.age_sprites['young adult'],
                "spirit_adult": inter_cat.age_sprites['adult'],
                "spirit_senior_adult": inter_cat.age_sprites['senior adult'],
                "spirit_elder": inter_cat.age_sprites['elder'],
                "spirit_dead": inter_cat.age_sprites['dead'],
                "eye_colour": inter_cat.eye_colour,
                "reverse": inter_cat.reverse,
                "white_patches": inter_cat.white_patches,
                "pattern": inter_cat.pattern,
                "tortie_base": inter_cat.tortiebase,
                "tortie_color": inter_cat.tortiecolour,
                "tortie_pattern": inter_cat.tortiepattern,
                "skin": inter_cat.skin,
                "skill": inter_cat.skill,
                "specialty": inter_cat.specialty,
                "specialty2": inter_cat.specialty2,
                "accessory": inter_cat.accessory,
                "experience": inter_cat.experience,
                "dead_moons": inter_cat.dead_for,
                "current_apprentice": [appr.ID for appr in inter_cat.apprentice],
                "former_apprentices": [appr.ID for appr in inter_cat.former_apprentices]
            }
            clan_cats.append(cat_data)
            if not inter_cat.dead:
                inter_cat.save_relationship_of_cat()
        try:
            with open('saves/' + clanname + '/clan_cats.json', 'w') as write_file:
                json_string = ujson.dumps(clan_cats, indent=4)
                write_file.write(json_string)
        except:
            print("Saving cats didn't work.")

# M O U S E
class Mouse():
    used_screen = screen

    def __init__(self):
        self.pos = (0, 0)

    def check_pos(self):
        self.pos = pygame.mouse.get_pos()


mouse = Mouse()
game = Game()
