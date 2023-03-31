import pygame
import pygame_gui

from scripts.datadir import get_save_dir

try:
    import ujson
except ImportError as e:
    print(f"ERROR: {e}\nFailed to import ujson, saving may be slower.")
    import json as ujson
import os
from ast import literal_eval

pygame.init()


# G A M E
class Game():
    max_name_length = 10
    # max_events_displayed = 10
    # event_scroll_ct = 0
    # max_allegiance_displayed = 17
    # allegiance_scroll_ct = 0
    # max_relation_events_displayed = 10
    # relation_scroll_ct = 0

    mediated = []  # Keep track of which couples have been mediated this moon.

    cur_events_list = []
    ceremony_events_list = []
    birth_death_events_list = []
    relation_events_list = []
    health_events_list = []
    other_clans_events_list = []
    misc_events_list = []
    herb_events_list = []

    allegiance_list = []
    language = {}
    game_mode = ''
    language_list = ['english', 'spanish', 'german']
    game_mode_list = ['classic', 'expanded', 'cruel season']

    cat_to_fade = []
    sub_tab_list = ['life events', 'user notes']

    # Keeping track of various last screen for various purposes
    last_screen_forupdate = 'start screen'
    last_screen_forProfile = 'list screen'

    # down = pygame.image.load("resources/images/buttons/arrow_down.png").convert_alpha()
    # up = pygame.image.load("resources/images/buttons/arrow_up.png").convert_alpha()

    # Sort-type
    sort_type = "rank"

    choose_cats = {}
    '''cat_buttons = {
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
    }'''
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
        're_roll': False,
        'roll_count': 0,
        'event': None,
        'cur_screen': 'start screen',
        'naming_text': '',
        'timeskip': False,
        'mate': None,
        'choosing_mate': False,
        'mentor': None,
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
        'patrol_remove': False,
        'cat_remove': False,
        'fill_patrol': False,
        'patrol_done': False,
        'error_message': '',
        'traceback': '',
        'apprentice': None,
        'change_name': '',
        'change_suffix': '',
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
        'profile_tab_group': None,
        'sub_tab_group': None,
        'gender_align': None,
        'show_details': False,
        'chosen_cat': None,
        'game_mode': '',
        'set_game_mode': False,
        'broke_up': False,
        'show_info': False,
        'patrol_chosen': 'general',
        'favorite_sub_tab': None,
        'root_cat': None,
        'window_open': False,
        'skip_conditions': []
    }
    all_screens = {}
    cur_events = {}
    map_info = {}

    # SETTINGS
    settings = {}
    setting_lists = {}

    with open("resources/gamesettings.json", 'r') as read_file:
        _settings = ujson.loads(read_file.read())

    for setting, values in _settings['__other'].items():
        settings[setting] = values[0]
        setting_lists[setting] = values

    _ = []
    _.append(_settings['relation'])
    _.append(_settings['general'])

    for cat in _:  # Add all the settings to the settings dictionary
        for setting_name, inf in cat.items():
            settings[setting_name] = inf[2]
            setting_lists[setting_name] = [inf[2], not inf[2]]

    settings_changed = False

    # CLAN
    clan = None
    cat_class = None
    config = {}

    rpc = None

    is_close_menu_open = False

    def __init__(self, current_screen='start screen'):
        self.current_screen = current_screen
        self.clicked = False
        self.keyspressed = []
        self.switch_screens = False

        with open(f"resources/game_config.json", 'r') as read_file:
            self.config = ujson.loads(read_file.read())

    def update_game(self):
        if self.current_screen != self.switches['cur_screen']:
            self.current_screen = self.switches['cur_screen']
            self.switch_screens = True
        self.clicked = False
        self.keyspressed = []

    def read_clans(self):
        '''with open(get_save_dir() + '/clanlist.txt', 'r') as read_file:
            clan_list = read_file.read()
            if_clans = len(clan_list)
        if if_clans > 0:
            clan_list = clan_list.split('\n')
            clan_list = [i.strip() for i in clan_list if i]  # Remove empty and whitespace
            return clan_list
        else:
            return None'''
        # All of the above is old code
        # Now, we want clanlist.txt to contain ONLY the name of the clan that is currently loaded
        # We will get the list of clans from the saves folder
        # each clan has its own folder, and the name of the folder is the name of the clan
        # so we can just get a list of all the folders in the saves folder

        # First, we need to make sure the saves folder exists
        if not os.path.exists(get_save_dir()):
            os.makedirs(get_save_dir())
            print('Created saves folder')
            return None

        # Now we can get a list of all the folders in the saves folder
        clan_list = [f.name for f in os.scandir(get_save_dir()) if f.is_dir()]

        # the clan specified in saves/clanlist.txt should be first in the list
        # so we can load it automatically

        if os.path.exists(get_save_dir() + '/clanlist.txt'):
            with open(get_save_dir() + '/clanlist.txt', 'r') as f:
                loaded_clan = f.read().strip().splitlines()
                if loaded_clan:
                    loaded_clan = loaded_clan[0]
                else:
                    loaded_clan = None
            os.remove(get_save_dir() + '/clanlist.txt')
            if loaded_clan:
                with open(get_save_dir() + '/currentclan.txt', 'w') as f:
                    f.write(loaded_clan)
        elif os.path.exists(get_save_dir() + '/currentclan.txt'):
            with open(get_save_dir() + '/currentclan.txt', 'r') as f:
                loaded_clan = f.read().strip()
        else:
            loaded_clan = None

        if loaded_clan and loaded_clan in clan_list:
            clan_list.remove(loaded_clan)
            clan_list.insert(0, loaded_clan)

        # Now we can return the list of clans
        if not clan_list:
            print('No clans found')
            return None
        # print('Clans found:', clan_list)
        return clan_list

    def save_clanlist(self, loaded_clan=None):
        '''clans = []
        if loaded_clan:
            clans.append(f"{loaded_clan}\n")

        for clan_name in self.switches['clan_list']:
            if clan_name and clan_name != loaded_clan:
                clans.append(f"{clan_name}\n")

        if clans:
            with open(get_save_dir() + '/clanlist.txt', 'w') as f:
                f.writelines(clans)'''
        if loaded_clan:
            if os.path.exists(get_save_dir() + '/clanlist.txt'):
                os.remove(get_save_dir() + '/clanlist.txt')  # we don't need clanlist.txt anymore
            with open(get_save_dir() + '/currentclan.txt', 'w') as f:
                f.write(loaded_clan)
        else:
            if os.path.exists(get_save_dir() + '/currentclan.txt'):
                os.remove(get_save_dir() + '/currentclan.txt')

    def save_settings(self):
        """ Save user settings for later use """
        data = ''.join(f"{s}:{self.settings[s]}" + "\n"
                       for s in self.settings.keys())

        with open(get_save_dir() + '/settings.txt', 'w') as write_file:
            write_file.write(data)
        self.settings_changed = False

    def load_settings(self):
        """ Load settings that user has saved from previous use """
        with open(get_save_dir() + '/settings.txt', 'r') as read_file:
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
        # add translation information here
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
        ''' if game.switches['clan_name'] != '':
            clanname = game.switches['clan_name']
        elif len(game.switches['clan_name']) > 0:
            clanname = game.switches['clan_list'][0]'''
        if game.clan is not None:
            clanname = game.clan.name
        directory = get_save_dir() + '/' + clanname
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Delete all existing relationship files
        if not os.path.exists(directory + '/relationships'):
            os.makedirs(directory + '/relationships')
        for f in os.listdir(directory + '/relationships'):
            os.remove(os.path.join(directory + '/relationships', f))

        self.save_faded_cats(clanname)  # Fades cat and saves them, if needed

        clan_cats = []
        for inter_cat in self.cat_class.all_cats.values():
            cat_data = {
                "ID": inter_cat.ID,
                "name_prefix": inter_cat.name.prefix,
                "name_suffix": inter_cat.name.suffix,
                "specsuffix_hidden": inter_cat.name.specsuffix_hidden,
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
                "mentor": inter_cat.mentor if inter_cat.mentor else None,
                "former_mentor": [cat for cat in inter_cat.former_mentor] if inter_cat.former_mentor else [],
                "patrol_with_mentor": inter_cat.patrol_with_mentor if inter_cat.patrol_with_mentor else 0,
                "mentor_influence": inter_cat.mentor_influence if inter_cat.mentor_influence else [],
                "mate": inter_cat.mate,
                "previous_mates": inter_cat.previous_mates,
                "dead": inter_cat.dead,
                "died_by": inter_cat.died_by if inter_cat.died_by else [],
                "paralyzed": inter_cat.paralyzed,
                "no_kits": inter_cat.no_kits,
                "exiled": inter_cat.exiled,
                "pelt_name": inter_cat.pelt.name,
                "pelt_color": inter_cat.pelt.colour,
                "pelt_white": inter_cat.pelt.white,
                "pelt_length": inter_cat.pelt.length,
                "sprite_kitten": inter_cat.cat_sprites['kitten'],
                "sprite_adolescent": inter_cat.cat_sprites['adolescent'],
                "sprite_young_adult": inter_cat.cat_sprites['young adult'],
                "sprite_adult": inter_cat.cat_sprites['adult'],
                "sprite_senior_adult": inter_cat.cat_sprites['senior adult'],
                "sprite_senior": inter_cat.cat_sprites['senior'],
                "sprite_para_adult": inter_cat.cat_sprites['para_adult'],
                "eye_colour": inter_cat.eye_colour,
                "eye_colour2": inter_cat.eye_colour2 if inter_cat.eye_colour2 else None,
                "reverse": inter_cat.reverse,
                "white_patches": inter_cat.white_patches,
                "vitiligo": inter_cat.vitiligo,
                "points": inter_cat.points,
                "white_patches_tint": inter_cat.white_patches_tint,
                "pattern": inter_cat.pattern,
                "tortie_base": inter_cat.tortiebase,
                "tortie_color": inter_cat.tortiecolour,
                "tortie_pattern": inter_cat.tortiepattern,
                "skin": inter_cat.skin,
                "tint": inter_cat.tint,
                "skill": inter_cat.skill,
                "scars": inter_cat.scars if inter_cat.scars else [],
                "accessory": inter_cat.accessory,
                "experience": inter_cat.experience,
                "dead_moons": inter_cat.dead_for,
                "current_apprentice": [appr for appr in inter_cat.apprentice],
                "former_apprentices": [appr for appr in inter_cat.former_apprentices],
                "possible_scar": inter_cat.possible_scar if inter_cat.possible_scar else None,
                "scar_event": inter_cat.scar_event if inter_cat.scar_event else [],
                "df": inter_cat.df,
                "outside": inter_cat.outside,
                "corruption": inter_cat.corruption if inter_cat.corruption else 0,
                "life_givers": inter_cat.life_givers if inter_cat.life_givers else [],
                "known_life_givers": inter_cat.known_life_givers if inter_cat.known_life_givers else [],
                "virtues": inter_cat.virtues if inter_cat.virtues else [],
                "retired": inter_cat.retired if inter_cat.retired else False,
                "faded_offspring": inter_cat.faded_offspring,
                "opacity": inter_cat.opacity,
                "prevent_fading": inter_cat.prevent_fading,
                "favourite": inter_cat.favourite,
            }
            clan_cats.append(cat_data)
            inter_cat.save_condition()
            if not inter_cat.dead:
                inter_cat.save_relationship_of_cat(directory + '/relationships')
        try:
            with open(get_save_dir() + '/' + clanname + '/clan_cats.json', 'w') as write_file:
                json_string = ujson.dumps(clan_cats, indent=4)
                write_file.write(json_string)
        except:
            print("ERROR: Saving cats didn't work.")

    def save_faded_cats(self, clanname):
        """Deals with fades cats, if needed, adding them as faded """
        if game.cat_to_fade:
            directory = get_save_dir() + '/' + clanname + "/faded_cats"
            if not os.path.exists(directory):
                os.makedirs(directory)

        copy_of_info = ""
        for cat in game.cat_to_fade:

            inter_cat = self.cat_class.all_cats[cat]

            # Add ID to list of faded cats.
            self.clan.faded_ids.append(cat)

            # If they have a mate, break it up
            if inter_cat.mate:
                if inter_cat.mate in self.cat_class.all_cats:
                    self.cat_class.all_cats[inter_cat.mate].mate = None

            # If they have parents, add them to their parents "faded offspring" list:
            if inter_cat.parent1:
                if inter_cat.parent1 in self.cat_class.all_cats:
                    self.cat_class.all_cats[inter_cat.parent1].faded_offspring.append(cat)
                else:
                    parent_faded = self.add_faded_offspring_to_faded_cat(inter_cat.parent1, cat)
                    if not parent_faded:
                        print("WARNING: Can't find faded parent1")

            if inter_cat.parent2:
                if inter_cat.parent2 in self.cat_class.all_cats:
                    self.cat_class.all_cats[inter_cat.parent2].faded_offspring.append(cat)
                else:
                    parent_faded = self.add_faded_offspring_to_faded_cat(inter_cat.parent2, cat)
                    if not parent_faded:
                        print("WARNING: Can't find faded parent2")

            # Get a copy of info
            if game.settings["save_faded_copy"]:
                copy_of_info += f''' ---------------
                "ID": {inter_cat.ID},
                "name_prefix": {inter_cat.name.prefix},
                "name_suffix": {inter_cat.name.suffix},
                "specsuffix_hidden": {inter_cat.name.specsuffix_hidden},
                "gender": {inter_cat.gender},
                "gender_align": {inter_cat.genderalign},
                "birth_cooldown": {inter_cat.birth_cooldown},
                "status": {inter_cat.status},
                "backstory": {inter_cat.backstory if inter_cat.backstory else None},
                "age": {inter_cat.age},
                "moons": {inter_cat.moons},
                "trait": {inter_cat.trait},
                "parent1": {inter_cat.parent1},
                "parent2": {inter_cat.parent2},
                "mentor": {inter_cat.mentor if inter_cat.mentor else None},
                "former_mentor": {[cat for cat in inter_cat.former_mentor] if inter_cat.former_mentor else []},
                "patrol_with_mentor": {inter_cat.patrol_with_mentor if inter_cat.patrol_with_mentor else 0},
                "mentor_influence": {inter_cat.mentor_influence if inter_cat.mentor_influence else []},
                "mate": {inter_cat.mate},
                "previous_mates": {inter_cat.previous_mates},
                "dead": {inter_cat.dead},
                "died_by": {inter_cat.died_by if inter_cat.died_by else []},
                "paralyzed": {inter_cat.paralyzed},
                "no_kits": {inter_cat.no_kits},
                "exiled": {inter_cat.exiled},
                "pelt_name": {inter_cat.pelt.name},
                "pelt_color": {inter_cat.pelt.colour},
                "pelt_white": {inter_cat.pelt.white},
                "pelt_length": {inter_cat.pelt.length},
                "sprite_kitten": {inter_cat.cat_sprites['kitten']},
                "sprite_adolescent": {inter_cat.cat_sprites['adolescent']},
                "sprite_young_adult": {inter_cat.cat_sprites['young adult']},
                "sprite_adult": {inter_cat.cat_sprites['adult']},
                "sprite_senior_adult": {inter_cat.cat_sprites['senior adult']},
                "sprite_senior": {inter_cat.cat_sprites['senior']},
                "sprite_para_adult": {inter_cat.cat_sprites['para_adult']},
                "eye_colour": {inter_cat.eye_colour},
                "eye_colour2": {inter_cat.eye_colour2 if inter_cat.eye_colour2 else None},
                "reverse": {inter_cat.reverse},
                "white_patches": {inter_cat.white_patches},
                "vitiligo": {inter_cat.vitiligo},
                "points": {inter_cat.points},
                "white_patches_tint": {inter_cat.white_patches_tint},
                "pattern": {inter_cat.pattern},
                "tortie_base": {inter_cat.tortiebase},
                "tortie_color": {inter_cat.tortiecolour},
                "tortie_pattern": {inter_cat.tortiepattern},
                "skin": {inter_cat.skin},
                "tint": {inter_cat.tint},
                "skill": {inter_cat.skill},
                "scars": {inter_cat.scars if inter_cat.scars else []},
                "accessory": {inter_cat.accessory},
                "experience": {inter_cat.experience},
                "dead_moons": {inter_cat.dead_for},
                "current_apprentice": {[appr for appr in inter_cat.apprentice]},
                "former_apprentices": {[appr for appr in inter_cat.former_apprentices]},
                "possible_scar": {inter_cat.possible_scar if inter_cat.possible_scar else None},
                "scar_event": {inter_cat.scar_event if inter_cat.scar_event else []},
                "df": {inter_cat.df},
                "outside": {inter_cat.outside},
                "corruption": {inter_cat.corruption if inter_cat.corruption else 0},
                "life_givers": {inter_cat.life_givers if inter_cat.life_givers else []},
                "known_life_givers": {inter_cat.known_life_givers if inter_cat.known_life_givers else []},
                "virtues": {inter_cat.virtues if inter_cat.virtues else []},
                "retired": {inter_cat.retired if inter_cat.retired else False},
                "faded_offspring": {inter_cat.faded_offspring},
                "opacity": {inter_cat.opacity},
                "prevent_fading": {inter_cat.prevent_fading},
                "favourite": {inter_cat.favourite}\n'''

            # SAVE TO IT'S OWN LITTLE FILE. This is a trimmed-down version for relation keeping only.
            cat_data = {
                "ID": inter_cat.ID,
                "name_prefix": inter_cat.name.prefix,
                "name_suffix": inter_cat.name.suffix,
                "status": inter_cat.status,
                "moons": inter_cat.moons,
                "parent1": inter_cat.parent1,
                "parent2": inter_cat.parent2,
                "df": inter_cat.df,
                "faded_offspring": inter_cat.faded_offspring
            }
            try:

                with open(get_save_dir() + '/' + clanname + '/faded_cats/' + cat + ".json", 'w') as write_file:
                    json_string = ujson.dumps(cat_data, indent=4)
                    write_file.write(json_string)
            except:
                print("ERROR: Something went wrong while saving a faded cat")

            self.clan.remove_cat(cat)  # Remove the cat from the active cats lists

        # Save the copy data is needed
        if game.settings["save_faded_copy"]:
            if not os.path.exists(get_save_dir() + '/' + clanname + '/faded_cats_info_copy.txt'):
                # Create the file if it doesn't exist
                with open(get_save_dir() + '/' + clanname + '/faded_cats_info_copy.txt', 'w') as create_file:
                    pass

            with open(get_save_dir() + '/' + clanname + '/faded_cats_info_copy.txt', 'a') as write_file:
                write_file.write(copy_of_info)

        game.cat_to_fade = []

    def add_faded_offspring_to_faded_cat(self, parent, offspring):
        """In order to siblings to work correctly, and not to lose relation info on fading, we have to keep track of
        both active and faded cat's faded offpsring. This will add a faded offspring to a faded parents file. """
        try:
            with open(get_save_dir() + '/' + self.clan.name + '/faded_cats/' + parent + ".json", 'r') as read_file:
                cat_info = ujson.loads(read_file.read())
        except:
            print("ERROR: loading faded cat")
            return False

        cat_info["faded_offspring"].append(offspring)

        with open(get_save_dir() + '/' + self.clan.name + '/faded_cats/' + parent + ".json", 'w') as write_file:
            json_string = ujson.dumps(cat_info, indent=4)
            write_file.write(json_string)

        return True


game = Game()

if not os.path.exists(get_save_dir() + '/settings.txt'):
    os.makedirs(get_save_dir(), exist_ok=True)
    with open(get_save_dir() + '/settings.txt', 'w') as write_file:
        write_file.write('')
game.load_settings()

pygame.display.set_caption('Clan Generator')

if game.settings['fullscreen']:
    screen_x, screen_y = 1600, 1400
    screen = pygame.display.set_mode((screen_x, screen_y), pygame.FULLSCREEN | pygame.SCALED)
else:
    screen_x, screen_y = 800, 700
    screen = pygame.display.set_mode((screen_x, screen_y))


def load_manager(res: tuple):
    # initialize pygame_gui manager, and load themes
    manager = pygame_gui.ui_manager.UIManager(res, 'resources/defaults.json', enable_live_theme_updates=False)
    manager.add_font_paths(
        font_name='notosans',
        regular_path='resources/fonts/NotoSans-Medium.ttf',
        bold_path='resources/fonts/NotoSans-ExtraBold.ttf',
        italic_path='resources/fonts/NotoSans-MediumItalic.ttf',
        bold_italic_path='resources/fonts/NotoSans-ExtraBoldItalic.ttf'
    )

    if res[0] > 800:
        manager.get_theme().load_theme('resources/defaults.json')
        manager.get_theme().load_theme('resources/buttons.json')
        manager.get_theme().load_theme('resources/text_boxes.json')
        manager.get_theme().load_theme('resources/text_boxes_dark.json')
        manager.get_theme().load_theme('resources/vertical_scroll_bar.json')
        manager.get_theme().load_theme('resources/windows.json')
        manager.get_theme().load_theme('resources/tool_tips.json')

        manager.preload_fonts([
            {'name': 'notosans', 'point_size': 30, 'style': 'italic'},
            {'name': 'notosans', 'point_size': 26, 'style': 'italic'},
            {'name': 'notosans', 'point_size': 30, 'style': 'bold'},
            {'name': 'notosans', 'point_size': 26, 'style': 'bold'},
            {'name': 'notosans', 'point_size': 22, 'style': 'bold'},
        ])


    else:
        manager.get_theme().load_theme('resources/defaults_small.json')
        manager.get_theme().load_theme('resources/buttons_small.json')
        manager.get_theme().load_theme('resources/text_boxes_small.json')
        manager.get_theme().load_theme('resources/text_boxes_dark_small.json')
        manager.get_theme().load_theme('resources/vertical_scroll_bar.json')
        manager.get_theme().load_theme('resources/windows.json')
        manager.get_theme().load_theme('resources/tool_tips_small.json')

        manager.preload_fonts([
            {'name': 'notosans', 'point_size': 11, 'style': 'bold'},
            {'name': 'notosans', 'point_size': 13, 'style': 'bold'},
            {'name': 'notosans', 'point_size': 15, 'style': 'bold'},
            {'name': 'notosans', 'point_size': 13, 'style': 'italic'},
            {'name': 'notosans', 'point_size': 15, 'style': 'italic'}
        ])

    return manager


MANAGER = load_manager((screen_x, screen_y))
