import re
from math import ceil
from random import choice, sample
import pygame
import pygame_gui
from .base_screens import Screens, cat_profiles
from scripts.utility import get_text_box_theme, scale
# from scripts.game_structure.text import *
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked, UISpriteButton
from scripts.patrol import patrol
from scripts.cat.cats import Cat, INJURIES, ILLNESSES
from scripts.game_structure.game_essentials import *


class PatrolScreen(Screens):
    able_box = pygame.transform.scale(pygame.image.load("resources/images/patrol_able_cats.png").convert_alpha(),
                                      (540, 402))
    patrol_box = pygame.transform.scale(pygame.image.load("resources/images/patrol_cats.png").convert_alpha(),
                                        (540, 402))
    cat_frame = pygame.transform.scale(pygame.image.load("resources/images/patrol_cat_frame.png").convert_alpha(),
                                       (400, 550))
    app_frame = pygame.transform.scale(pygame.image.load("resources/images/patrol_app_frame.png").convert_alpha(),
                                       (332, 340))
    mate_frame = pygame.transform.scale(pygame.image.load("resources/images/patrol_mate_frame.png").convert_alpha(),
                                        (332, 340))

    current_patrol = []
    patrol_stage = 'choose_cats'  # Can be 'choose_cats' or 'patrol_events' Controls the stage of patrol.
    patrol_screen = 'patrol_cats'  # Can be "patrol_cats" or "skills". Controls the tab on the select_cats stage
    patrol_type = 'general'  # Can be 'general' or 'border' or 'training' or 'med' or 'hunting'
    current_page = 1
    elements = {}  # hold elements for sub-page
    cat_buttons = {}  # Hold cat image sprites.
    selected_cat = None  # Holds selected cat.
    selected_apprentice_index = 0

    def __init__(self, name=None):
        super().__init__(name)
        self.intro_image = None
        self.app_mentor = None
        self.able_cats = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if self.patrol_stage == "choose_cats":
                self.handle_choose_cats_events(event)
            elif self.patrol_stage == 'patrol_events':
                self.handle_patrol_events_event(event)
            elif self.patrol_stage == 'patrol_complete':
                self.handle_patrol_complete_events(event)

            self.menu_button_pressed(event)

            # Checking if the mentor or mate selection buttons are clicked. This must be separate, because
            # these buttons may not exist. 
            if "mate_button" in self.elements:
                if event.ui_element == self.elements['mate_button']:
                    self.selected_cat = Cat.all_cats[self.selected_cat.mate]
                    self.update_button()
                    self.update_cat_images_buttons()
                    self.update_selected_cat()

            if 'app_mentor_button' in self.elements:
                if event.ui_element == self.elements['app_mentor_button']:
                    self.selected_cat = self.app_mentor
                    self.update_button()
                    self.update_cat_images_buttons()
                    self.update_selected_cat()

            # Check if apprentice cycle buttons are clicked.
            if "cycle_app_mentor_left_button" in self.elements:
                if event.ui_element == self.elements['cycle_app_mentor_left_button']:
                    self.selected_apprentice_index -= 1
                    self.app_mentor = self.selected_cat.apprentice[self.selected_apprentice_index]
                    self.update_selected_cat()
                    self.update_button()

            if "cycle_app_mentor_right_button" in self.elements:
                if event.ui_element == self.elements['cycle_app_mentor_right_button']:
                    self.selected_apprentice_index += 1
                    self.app_mentor = self.selected_cat.apprentice[self.selected_apprentice_index]
                    self.update_selected_cat()
                    self.update_button()

    def handle_choose_cats_events(self, event):
        if event.ui_element == self.elements["random"]:
            self.selected_cat = choice(self.able_cats)
            self.update_selected_cat()
            self.update_button()
        # Check is a cat is clicked
        elif event.ui_element in self.cat_buttons.values():
            self.selected_cat = event.ui_element.return_cat_object()
            self.update_selected_cat()
            self.update_button()
        elif event.ui_element == self.elements["add_remove_cat"]:
            if self.selected_cat in self.current_patrol:
                self.current_patrol.remove(self.selected_cat)
            else:
                self.current_patrol.append(self.selected_cat)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['add_one']:
            self.selected_cat = choice(self.able_cats)
            self.update_selected_cat()
            self.current_patrol.append(self.selected_cat)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['add_three']:
            self.current_patrol += sample(self.able_cats, k=3)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['add_six']:
            self.current_patrol += sample(self.able_cats, k=6)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['remove_all']:
            self.current_patrol = []
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['patrol_tab']:
            self.patrol_screen = 'patrol_cats'
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['skills']:
            self.patrol_screen = 'skills'
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements["next_page"]:
            self.current_page += 1
            self.update_cat_images_buttons()
        elif event.ui_element == self.elements["last_page"]:
            self.current_page -= 1
            self.update_cat_images_buttons()
        elif event.ui_element == self.elements["paw"]:
            if self.patrol_type == 'training':
                self.patrol_type = 'general'
            else:
                self.patrol_type = 'training'
            self.update_button()
        elif event.ui_element == self.elements["claws"]:
            if self.patrol_type == 'border':
                self.patrol_type = 'general'
            else:
                self.patrol_type = 'border'
            self.update_button()
        elif event.ui_element == self.elements["herb"]:
            if self.patrol_type == 'med':
                self.patrol_type = 'general'
            else:
                self.patrol_type = 'med'
            self.update_button()
        elif event.ui_element == self.elements["mouse"]:
            if self.patrol_type == 'hunting':
                self.patrol_type = 'general'
            else:
                self.patrol_type = 'hunting'
            self.update_button()
        elif event.ui_element == self.elements['patrol_start']:
            self.selected_cat = None
            self.open_patrol_event_screen()  # Starting patrol.

    def handle_patrol_events_event(self, event):
        if event.ui_element == self.elements["proceed"]:
            self.open_patrol_complete_screen("proceed")
        elif event.ui_element == self.elements["not_proceed"]:
            self.open_patrol_complete_screen("notproceed")
        elif event.ui_element == self.elements["antagonize"]:
            self.open_patrol_complete_screen("antagonize")

    def handle_patrol_complete_events(self, event):
        if event.ui_element == self.elements['patrol_again']:
            self.open_choose_cats_screen()
        elif event.ui_element == self.elements["clan_return"]:
            self.change_screen('clan screen')

    def screen_switches(self):
        self.set_disabled_menu_buttons(["patrol_screen"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.show_menu_buttons()
        self.open_choose_cats_screen()
        cat_profiles()

    def update_button(self):
        """" Updates button availabilities. """
        if self.patrol_stage == 'choose_cats':
            # Killing it now, because we have to switch it out for a "remove cat" button if the cat if
            # already in the patrol
            self.elements["add_remove_cat"].kill()

            if self.selected_cat in self.current_patrol:
                self.elements["add_remove_cat"] = UIImageButton(scale(pygame.Rect((672, 920), (254, 60))), "",
                                                                object_id="#remove_cat_button", manager=MANAGER)
            elif self.selected_cat is None or len(self.current_patrol) >= 6:
                self.elements["add_remove_cat"] = UIImageButton(scale(pygame.Rect((700, 920), (196, 60))), "",
                                                                object_id="#add_cat_button", manager=MANAGER)
                self.elements["add_remove_cat"].disable()
            else:
                self.elements["add_remove_cat"] = UIImageButton(scale(pygame.Rect((700, 920), (196, 60))), "",
                                                                object_id="#add_cat_button", manager=MANAGER)

            # Update start patrol button
            if not self.current_patrol:
                self.elements['patrol_start'].disable()
            else:
                self.elements['patrol_start'].enable()

            # Update add random cat buttons
            # Enable all the buttons, to reset them
            self.elements['add_one'].enable()
            self.elements['add_three'].enable()
            self.elements['add_six'].enable()
            self.elements["random"].enable()

            if game.clan.game_mode != 'classic':
                self.elements['paw'].enable()
                self.elements['mouse'].enable()
                self.elements['claws'].enable()
                self.elements['herb'].enable()

            if len(self.current_patrol) >= 6 or len(self.able_cats) < 1:
                self.elements['add_one'].disable()
                self.elements["random"].disable()
            if len(self.current_patrol) > 3 or len(self.able_cats) < 3:
                self.elements['add_three'].disable()
            if len(self.current_patrol) >= 1 or len(self.able_cats) < 6:
                self.elements['add_six'].disable()

                # Update the availability of the tab buttons
            if self.patrol_screen == 'patrol_cats':
                self.elements['patrol_tab'].disable()
                self.elements['skills'].enable()
            elif self.patrol_screen == 'skills':
                self.elements['patrol_tab'].enable()
                self.elements['skills'].disable()

            if self.patrol_screen == 'patrol_cats':
                self.elements['patrol_tab'].disable()
                self.elements['skills'].enable()
            elif self.patrol_screen == 'skills':
                self.elements['patrol_tab'].enable()
                self.elements['skills'].disable()

            if game.clan.game_mode != 'classic':

                # making sure meds don't get the option for other patrols
                med = False
                for cat in self.current_patrol:
                    if cat.status in ['medicine cat', 'medicine cat apprentice']:
                        med = True
                        self.patrol_type = 'med'
                if med is False and self.current_patrol:
                    self.elements['herb'].disable()
                    if self.patrol_type == 'med':
                        self.patrol_type = 'general'

                self.elements['info'].kill()  # clearing the text before displaying new text

                if self.patrol_type == 'general':
                    text = 'random patrol type'
                elif self.patrol_type == 'training' and med is False:
                    text = 'training'
                elif self.patrol_type == 'border' and med is False:
                    text = 'border'
                elif self.patrol_type == 'hunting' and med is False:
                    text = 'hunting'
                elif self.patrol_type == 'med':
                    if med is True and self.current_patrol:
                        text = 'herb gathering'
                        self.elements['mouse'].disable()
                        self.elements['claws'].disable()
                        self.elements['paw'].disable()
                    else:
                        text = 'herb gathering'
                else:
                    text = ""

                self.elements['info'] = pygame_gui.elements.UITextBox(
                    text, scale(pygame.Rect((500, 1050), (600, 800))), object_id=get_text_box_theme(), manager=MANAGER
                )

            if self.selected_cat != None:
                if 'cycle_app_mentor_right_button' in self.elements and 'cycle_app_mentor_left_button' in self.elements:
                    if self.selected_apprentice_index == len(self.selected_cat.apprentice) - 1:
                        self.elements['cycle_app_mentor_right_button'].disable()
                    else:
                        self.elements['cycle_app_mentor_left_button'].enable()

                    if self.selected_apprentice_index == 0:
                        self.elements['cycle_app_mentor_left_button'].disable()
                    else:
                        self.elements['cycle_app_mentor_left_button'].enable()

                    if self.selected_cat.mentor != None:
                        self.elements['cycle_app_mentor_left_button'].hide()
                        self.elements['cycle_app_mentor_right_button'].hide()

    def open_choose_cats_screen(self):
        """Opens the choose-cat patrol stage. """
        self.clear_page()  # Clear the page
        self.clear_cat_buttons()
        cat_profiles()

        self.current_patrol = []
        self.current_page = 1
        self.patrol_stage = 'choose_cats'
        self.patrol_screen = 'patrol_cats'  # List

        self.elements["info"] = pygame_gui.elements.UITextBox(
            'Choose up to six cats to take on patrol.\n'
            'Smaller patrols help cats gain more experience, but larger patrols are safer.',
            scale(pygame.Rect((100, 190), (1400, -1))), object_id=get_text_box_theme())
        self.elements["cat_frame"] = pygame_gui.elements.UIImage(scale(pygame.Rect((600, 330), (400, 550))),
                                                                 pygame.image.load(
                                                                     "resources/images/patrol_cat_frame.png").convert_alpha()
                                                                 , manager=MANAGER)

        # Frames
        self.elements["able_frame"] = pygame_gui.elements.UIImage(scale(pygame.Rect((80, 920), self.able_box.get_size())),
                                                                  self.able_box, manager=MANAGER)
        self.elements["able_frame"].disable()

        self.elements["patrol_frame"] = pygame_gui.elements.UIImage(scale(pygame.Rect((980, 920), self.patrol_box.get_size())),
                                                                    self.patrol_box, manager=MANAGER)
        self.elements["patrol_frame"].disable()

        # Buttons
        self.elements["add_remove_cat"] = UIImageButton(scale(pygame.Rect((700, 920), (196, 60))), "",
                                                        object_id="#add_cat_button", manager=MANAGER)
        # No cat is selected when the screen is opened, so the button is disabled
        self.elements["add_remove_cat"].disable()

        # Randomizing buttons
        self.elements["random"] = UIImageButton(scale(pygame.Rect((646, 990), (68, 68))), "", object_id="#random_dice_button"
                                                , manager=MANAGER)
        self.elements["add_one"] = UIImageButton(scale(pygame.Rect((726, 990), (68, 68))), "", object_id="#add_one_button"
                                                 , manager=MANAGER)
        self.elements["add_three"] = UIImageButton(scale(pygame.Rect((806, 990), (68, 68))), "", object_id="#add_three_button"
                                                   , manager=MANAGER)
        self.elements["add_six"] = UIImageButton(scale(pygame.Rect((886, 990), (68, 68))), "", object_id="#add_six_button"
                                                 , manager=MANAGER)

        # patrol type buttons - disabled for now
        self.elements['paw'] = UIImageButton(scale(pygame.Rect((646, 1120), (68, 68))), "", object_id="#paw_patrol_button"
                                             , manager=MANAGER)
        self.elements['paw'].disable()
        self.elements['mouse'] = UIImageButton(scale(pygame.Rect((726, 1120), (68, 68))), "", object_id="#mouse_patrol_button"
                                               , manager=MANAGER)
        self.elements['mouse'].disable()
        self.elements['claws'] = UIImageButton(scale(pygame.Rect((806, 1120), (68, 68))), "", object_id="#claws_patrol_button"
                                               , manager=MANAGER)
        self.elements['claws'].disable()
        self.elements['herb'] = UIImageButton(scale(pygame.Rect((886, 1120), (68, 68))), "", object_id="#herb_patrol_button"
                                              , manager=MANAGER)
        self.elements['herb'].disable()

        # Able cat page buttons
        self.elements['last_page'] = UIImageButton(scale(pygame.Rect((150, 924), (68, 68))), "", object_id="#patrol_last_page"
                                                   , manager=MANAGER)
        self.elements['next_page'] = UIImageButton(scale(pygame.Rect((482, 924), (68, 68))), "", object_id="#patrol_next_page"
                                                   , manager=MANAGER)

        # Tabs for the current patrol
        self.elements['patrol_tab'] = UIImageButton(scale(pygame.Rect((1010, 920), (160, 70))), "",
                                                    object_id="#patrol_cats_tab", manager=MANAGER)
        self.elements['patrol_tab'].disable()  # We start on the patrol_cats_tab
        self.elements['skills'] = UIImageButton(scale(pygame.Rect((1180, 920), (308, 70))), "",
                                                object_id="#skills_cats_tab", manager=MANAGER)

        # Remove all button
        self.elements['remove_all'] = UIImageButton(scale(pygame.Rect((1120, 1254), (248, 70))), "",
                                                    object_id="#remove_all_button", manager=MANAGER)

        # Text box for skills and traits. Hidden for now, and with no text in it
        self.elements["skills_box"] = UITextBoxTweaked("", scale(pygame.Rect((1020, 1020), (480, 180))), visible=False,
                                                       object_id="#cat_profile_info_box",
                                                       line_spacing=0.95, manager=MANAGER)

        # Start Patrol Button
        self.elements['patrol_start'] = UIImageButton(scale(pygame.Rect((666, 1200), (270, 60))), "",
                                                      object_id="#start_patrol_button", manager=MANAGER)
        self.elements['patrol_start'].disable()

        self.update_cat_images_buttons()
        self.update_button()

    def adjust_patrol_text(self, text, size=1):
        """
        set text parameter to whichever patrol text you want to change (i.e. intro_text, success_text, ect.)
        always set size to patrol_size
        """
        vowels = ['A', 'E', 'I', 'O', 'U']
        if size == 1:
            text = text.replace('Your patrol',
                                str(patrol.patrol_leader_name))
            text = text.replace('The patrol',
                                str(patrol.patrol_leader_name))
        text = text.replace('p_l', str(patrol.patrol_leader_name))
        if patrol.patrol_random_cat is not None:
            text = text.replace('r_c', str(patrol.patrol_random_cat.name))
        else:
            text = text.replace('r_c', str(patrol.patrol_leader_name))
        text = text.replace('app1', str(patrol.app1_name))
        text = text.replace('app2', str(patrol.app2_name))
        text = text.replace('app3', str(patrol.app3_name))
        text = text.replace('app4', str(patrol.app4_name))
        text = text.replace('app5', str(patrol.app5_name))
        text = text.replace('app6', str(patrol.app6_name))
        if len(patrol.patrol_other_cats) == 1:
            text = text.replace('o_c1', str(patrol.patrol_other_cats[0].name))
        elif len(patrol.patrol_other_cats) == 2:
            text = text.replace('o_c1', str(patrol.patrol_other_cats[0].name))
            text = text.replace('o_c2', str(patrol.patrol_other_cats[1].name))
        elif len(patrol.patrol_other_cats) == 3:
            text = text.replace('o_c1', str(patrol.patrol_other_cats[0].name))
            text = text.replace('o_c2', str(patrol.patrol_other_cats[1].name))
            text = text.replace('o_c3', str(patrol.patrol_other_cats[2].name))
        elif len(patrol.patrol_other_cats) == 4:
            text = text.replace('o_c1', str(patrol.patrol_other_cats[0].name))
            text = text.replace('o_c2', str(patrol.patrol_other_cats[1].name))
            text = text.replace('o_c3', str(patrol.patrol_other_cats[2].name))
            text = text.replace('o_c4', str(patrol.patrol_other_cats[3].name))

        if 's_c' in text:
            if patrol.patrol_stat_cat is not None:
                text = text.replace('s_c', str(patrol.patrol_stat_cat.name))
            else:
                text = text.replace('s_c', str(patrol.patrol_leader_name))

        other_clan_name = patrol.other_clan.name
        s = 0
        for x in range(text.count('o_c_n')):
            index = text.index('o_c_n', s) or text.index("o_c_n's", s) or text.index('o_c_n.', s)
            for y in vowels:
                if str(other_clan_name).startswith(y):
                    modify = text.split()
                    pos = 0
                    if 'o_c_n' in modify:
                        pos = modify.index('o_c_n')
                    if "o_c_n's" in modify:
                        pos = modify.index("o_c_n's")
                    if 'o_c_n.' in modify:
                        pos = modify.index('o_c_n.')
                    if modify[pos - 1] == 'a':
                        modify.remove('a')
                        modify.insert(pos - 1, 'an')
                    text = " ".join(modify)
                    break
            s += index + 3

        text = text.replace('o_c_n', str(other_clan_name) + 'Clan')

        clan_name = game.clan.name
        s = 0
        pos = 0
        for x in range(text.count('c_n')):
            index = text.index('c_n', s) or text.index("c_n's", s) or text.index('c_n.', s)
            for y in vowels:
                if str(clan_name).startswith(y):
                    modify = text.split()
                    if 'c_n' in modify:
                        pos = modify.index('c_n')
                    if "c_n's" in modify:
                        pos = modify.index("c_n's")
                    if 'c_n.' in modify:
                        pos = modify.index('c_n.')
                    if modify[pos - 1] == 'a':
                        modify.remove('a')
                        modify.insert(pos - 1, 'an')
                    text = " ".join(modify)
                    break
            s += index + 3
        text = text.replace('c_n', str(game.clan.name) + 'Clan')

        sign_list = ['strangely-patterned stone', 'sharp stick', 'prey bone', 'cloud shaped like a cat',
                     'tuft of red fur', 'red feather', 'brown feather', 'black feather', 'white feather',
                     'star-shaped leaf',
                     'beetle shell', 'snail shell', 'tuft of badger fur', 'two pawprints overlapping',
                     'flower missing a petal',
                     'tuft of fox fur', ]
        sign = choice(sign_list)
        s = 0
        pos = 0
        for x in range(text.count('a_sign')):
            index = text.index('a_sign', s) or text.index('a_sign.', s)
            for y in vowels:
                if str(sign).startswith(y):
                    modify = text.split()
                    if 'a_sign' in modify:
                        pos = modify.index('a_sign')
                    if 'a_sign.' in modify:
                        pos = modify.index('a_sign.')
                    if modify[pos - 1] == 'a':
                        modify.remove('a')
                        modify.insert(pos - 1, 'an')
                    text = " ".join(modify)
                    break
            s += index + 3
        text = text.replace('a_sign', str(sign))

        return text

    def open_patrol_event_screen(self):
        """Open the patrol event screen. This sets up the patrol starting"""
        self.clear_page()
        self.clear_cat_buttons()
        self.patrol_stage = 'patrol_events'

        # Layout images
        self.elements['event_bg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((762, 330), (708, 540))),
                                                                pygame.transform.scale(
                                                                pygame.image.load(
                                                                    "resources/images/patrol_event_frame.png").convert_alpha(),
                                                                    (708, 540)
                                                                ), manager=MANAGER)
        self.elements['info_bg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((180, 912), (840, 408))),
                                                               pygame.transform.scale(
                                                               pygame.image.load(
                                                                   "resources/images/patrol_info.png").convert_alpha(),
                                                                   (840, 408)
                                                               ), manager=MANAGER)
        self.elements['image_frame'] = pygame_gui.elements.UIImage(scale(pygame.Rect((130, 280), (650, 640))),
                                                                   pygame.transform.scale(
                                                                   pygame.image.load(
                                                                       "resources/images/patrol_sprite_frame.png").convert_alpha(),
                                                                       (650, 640)
                                                                   ), manager=MANAGER)

        # Add selected cats to the patrol.
        patrol.add_patrol_cats(self.current_patrol)
        possible_events = patrol.get_possible_patrols(
            str(game.clan.current_season).casefold(),
            str(game.clan.biome).casefold(),
            game.clan.all_clans,
            self.patrol_type,
            game.settings.get('disasters')
        )
        patrol.patrol_event = choice(possible_events)  # Set patrol event.
        print(str(patrol.patrol_event.patrol_id))
        intro_text = patrol.patrol_event.intro_text
        patrol_size = len(patrol.patrol_cats)

        file = 'train'
        if patrol.patrol_event.patrol_id.find('med') != -1:
            file = 'med'
        elif patrol.patrol_event.patrol_id.find('hunt') != -1:
            file = 'hunt'
        elif patrol.patrol_event.patrol_id.find('train') != -1:
            file = 'train'
        elif patrol.patrol_event.patrol_id.find('bord') != -1:
            file = 'bord'

        try:
            self.elements['intro_image'] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((150, 300), (600, 600))),
                pygame.transform.scale(
                pygame.image.load(
                    f"resources/images/patrol_art/{file}_general_intro.png").convert_alpha(),
                    (600, 600))
            )
        except:
            print('ERROR: could not display patrol image')

        # Grab win trait.
        if patrol.patrol_event.win_trait is not None:
            win_trait = patrol.patrol_event.win_trait
            patrol_trait = patrol.patrol_traits.index(win_trait)
            patrol.patrol_stat_cat = patrol.patrol_cats[patrol_trait]

        # Prepare Intro Text
        # adjusting text for solo patrols
        intro_text = self.adjust_patrol_text(patrol.patrol_event.intro_text, patrol_size)
        self.elements["patrol_text"] = UITextBoxTweaked(intro_text, scale(pygame.Rect((770, 350), (660, 540))),
                                                        object_id="#patrol_text_box", manager=MANAGER)
        # Patrol Info
        # TEXT CATEGORIES AND CHECKING FOR REPEATS
        members = []
        skills = []
        traits = []
        for x in patrol.patrol_names:
            if x not in patrol.patrol_leader_name:
                members.append(x)
        for x in patrol.patrol_skills:
            if x not in skills:
                skills.append(x)
        for x in patrol.patrol_traits:
            if x not in traits:
                traits.append(x)

        self.elements['patrol_info'] = pygame_gui.elements.UITextBox(
            f'patrol leader: {patrol.patrol_leader_name} \n'
            f'patrol members: {self.get_list_text(members)} \n'
            f'patrol skills: {self.get_list_text(skills)} \n'
            f'patrol traits: {self.get_list_text(traits)}', scale(pygame.Rect((210, 920), (480, 400))),
            object_id="#cat_profile_info_box", manager=MANAGER)

        # Draw Patrol Cats
        pos_x = 800
        pos_y = 950
        for u in range(6):
            if u < len(patrol.patrol_cats):
                self.elements["cat" + str(u)] = pygame_gui.elements.UIImage(scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                                                                            patrol.patrol_cats[u].big_sprite,
                                                                            manager=MANAGER)
                pos_x += 100
                if pos_x > 900:
                    pos_y += 100
                    pos_x = 800
            else:
                break

        ##################### Buttons:
        self.elements["proceed"] = UIImageButton(scale(pygame.Rect((1100, 866), (344, 60))), "",
                                                 object_id="#proceed_button",
                                                 starting_height=2, manager=MANAGER)
        self.elements["not_proceed"] = UIImageButton(scale(pygame.Rect((1100, 922), (344, 60))), "",
                                                     object_id="#not_proceed_button",
                                                     starting_height=2, manager=MANAGER)

        self.elements["antagonize"] = UIImageButton(scale(pygame.Rect((1100, 980), (344, 72))), "",
                                                    object_id="#antagonize_button", manager=MANAGER)
        if patrol.patrol_event.antagonize_text is None:
            self.elements["antagonize"].hide()

    def open_patrol_complete_screen(self, user_input):
        """Deals with the next stage of the patrol, including antagonize, proceed, and do not proceed.
        You must put the type of next step (user input) into the user_input parameter.
        For antagonize: user_input = "antag" or "antagonize"
        For Proceed: user_input = "pro" or "proceed"
        For do not Proceed: user_input = "nopro" or "notproceed" """
        self.patrol_stage = "patrol_complete"

        self.elements["clan_return"] = UIImageButton(scale(pygame.Rect((800, 274), (324, 60))), "",
                                                     object_id="#return_to_clan", manager=MANAGER)
        self.elements['patrol_again'] = UIImageButton(scale(pygame.Rect((1120, 274), (324, 60))), "",
                                                      object_id="#patrol_again", manager=MANAGER)

        if user_input in ["antag", "antagonize"]:
            patrol.calculate_success(antagonize=True)
            if patrol.success:
                display_text = patrol.antagonize
            else:
                display_text = patrol.antagonize_fail

        elif user_input in ["pro", "proceed"]:
            patrol.calculate_success(antagonize=False)
            if patrol.success:
                display_text = patrol.final_success
            else:
                display_text = patrol.final_fail

        elif user_input in ["nopro", "notproceed"]:
            display_text = patrol.patrol_event.decline_text
        else:
            display_text = "ERROR"

        # Adjust text for solo patrols
        display_text = self.adjust_patrol_text(display_text, len(patrol.patrol_cats))

        self.elements["patrol_results"] = pygame_gui.elements.UITextBox("",
                                                                        scale(pygame.Rect((1100, 1000), (344, 150))),
                                                                        object_id=get_text_box_theme("#cat_patrol_info_box")
                                                                        , manager=MANAGER)
        self.elements["patrol_results"].set_text(patrol.results())

        self.elements["patrol_text"].set_text(display_text)

        self.elements["proceed"].disable()
        self.elements["not_proceed"].disable()
        self.elements["antagonize"].hide()

    def update_cat_images_buttons(self):
        """Updates all the cat sprite buttons. Also updates the skills tab, if open, and the next and
            previous page buttons.  """
        self.clear_cat_buttons()  # Clear all the cat buttons
        self.able_cats = []

        # ASSIGN TO ABLE CATS
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and the_cat.in_camp and the_cat not in game.patrolled and the_cat.status not in [
                'elder', 'kitten', 'mediator'
            ] and not the_cat.outside and the_cat not in self.current_patrol and not the_cat.not_working():
                self.able_cats.append(the_cat)

        if not self.able_cats:
            all_pages = []
        else:
            all_pages = self.chunks(self.able_cats, 15)

        if self.current_page > len(all_pages):
            if len(all_pages) == 0:
                self.current_page = 1
            else:
                self.current_page = len(all_pages)

        # Check for empty list (no able cats)
        if all_pages:
            display_cats = all_pages[self.current_page - 1]
        else:
            display_cats = []

        # Update next and previous page buttons
        if len(all_pages) <= 1:
            self.elements["next_page"].disable()
            self.elements["last_page"].disable()
        else:
            if self.current_page >= len(all_pages):
                self.elements["next_page"].disable()
            else:
                self.elements["next_page"].enable()

            if self.current_page <= 1:
                self.elements["last_page"].disable()
            else:
                self.elements["last_page"].enable()

        # Draw able cats.
        pos_y = 1000
        pos_x = 100
        i = 0
        for cat in display_cats:
            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                                                                   pygame.transform.scale(cat.large_sprite, (100, 100))
                                                                   , cat_object=cat, manager=MANAGER)
            pos_x += 100
            if pos_x >= 600:
                pos_x = 100
                pos_y += 100
            i += 1

        if self.patrol_screen == 'patrol_cats':
            # Hide Skills Info
            self.elements["skills_box"].hide()
            # Draw cats in patrol
            pos_y = 1016
            pos_x = 1050
            i = 0
            for cat in self.current_patrol:
                self.cat_buttons["patrol_cat" + str(i)] = UISpriteButton(scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                                                                         pygame.transform.scale(cat.large_sprite,
                                                                         (100, 100)), cat_object=cat, manager=MANAGER)
                pos_x += 150
                if pos_x >= 1450:
                    pos_x = 1050
                    pos_y += 100
                i += 1
        elif self.patrol_screen == 'skills':
            self.update_skills_tab()

    def update_skills_tab(self):
        self.elements["skills_box"].show()
        patrol_skills = []
        patrol_traits = []
        if self.current_patrol is not []:
            for x in self.current_patrol:
                if x.skill not in patrol_skills:
                    patrol_skills.append(x.skill)
                if x.trait not in patrol_traits:
                    patrol_traits.append(x.trait)

        self.elements["skills_box"].set_text(
            f"Current Patrol Skills: {', '.join(patrol_skills)}\nCurrent Patrol Traits: {', '.join(patrol_traits)}"
        )

    def update_selected_cat(self):
        """Refreshes the image displaying the selected cat, traits, mentor/apprentice/mate ext"""

        # Kill and delete all relevant elements
        if "selected_image" in self.elements:
            self.elements["selected_image"].kill()
            del self.elements["selected_image"]
        if 'selected_name' in self.elements:
            self.elements["selected_name"].kill()
            del self.elements["selected_name"]
        if 'selected_bio' in self.elements:
            self.elements["selected_bio"].kill()
            del self.elements["selected_bio"]

        # Kill mate frame, apprentice/mentor frame, and respective images, if they exist:
        if 'mate_frame' in self.elements:
            self.elements['mate_frame'].kill()
            del self.elements['mate_frame']  # No need to keep this in memory
        if 'mate_image' in self.elements:
            self.elements['mate_image'].kill()
            del self.elements['mate_image']  # No need to keep this in memory
        if 'mate_name' in self.elements:
            self.elements['mate_name'].kill()
            del self.elements['mate_name']  # No need to keep this in memory
        if 'mate_info' in self.elements:
            self.elements['mate_info'].kill()
            del self.elements['mate_info']
        if 'mate_button' in self.elements:
            self.elements['mate_button'].kill()
            del self.elements['mate_button']  # No need to keep this in memory
        if 'app_mentor_frame' in self.elements:
            self.elements['app_mentor_frame'].kill()
            del self.elements['app_mentor_frame']  # No need to keep this in memory
        if 'app_mentor_image' in self.elements:
            self.elements['app_mentor_image'].kill()
            del self.elements['app_mentor_image']  # No need to keep this in memory
        if 'app_mentor_name' in self.elements:
            self.elements['app_mentor_name'].kill()
            del self.elements['app_mentor_name']  # No need to keep this in memory
        if 'app_mentor_button' in self.elements:
            self.elements['app_mentor_button'].kill()
            del self.elements['app_mentor_button']  # No need to keep this in memory
        if 'app_mentor_info' in self.elements:
            self.elements['app_mentor_info'].kill()
            del self.elements['app_mentor_info']
        if 'cycle_app_mentor_left_button' in self.elements:
            self.elements['cycle_app_mentor_left_button'].kill()
            del self.elements['cycle_app_mentor_left_button']
        if 'cycle_app_mentor_right_button' in self.elements:
            self.elements['cycle_app_mentor_right_button'].kill()
            del self.elements['cycle_app_mentor_right_button']

        if self.selected_cat is not None:
            # Now, if the selected cat is not None, we rebuild everything with the correct cat info
            # Selected Cat Image
            self.elements["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((640, 350), (300, 300))),
                                                                          pygame.transform.scale(
                                                                              self.selected_cat.large_sprite,
                                                                              (300, 300)), manager=MANAGER)

            name = str(self.selected_cat.name)  # get name
            if 14 <= len(name) >= 16:  # check name length
                short_name = str(self.selected_cat.name)[0:15]
                name = short_name + '...'

            self.elements['selected_name'] = pygame_gui.elements.UITextBox(name, scale(pygame.Rect((600, 650), (400, 60))),
                                                                           object_id=get_text_box_theme())

            self.elements['selected_bio'] = UITextBoxTweaked(str(self.selected_cat.status) +
                                                             "\n" + str(self.selected_cat.trait) +
                                                             "\n" + str(self.selected_cat.skill) +
                                                             "\n" + str(self.selected_cat.experience_level),
                                                             scale(pygame.Rect((600, 700), (400, 150))),
                                                             object_id=get_text_box_theme("#cat_patrol_info_box"),
                                                             line_spacing=0.95
                                                             , manager=MANAGER)

            # Show Cat's Mate, if they have one
            if self.selected_cat.status not in ['medicine cat apprentice', 'apprentice']:
                if self.selected_cat.mate is not None:
                    self.elements['mate_frame'] = pygame_gui.elements.UIImage(scale(pygame.Rect((280, 380), (332, 340))),
                                                                              self.mate_frame)
                    mate = Cat.fetch_cat(self.selected_cat.mate)
                    self.elements['mate_image'] = pygame_gui.elements.UIImage(scale(pygame.Rect((300, 400), (200, 200))),
                                                                              pygame.transform.scale(
                                                                                  mate.large_sprite, (200, 200))
                                                                              , manager=MANAGER)
                    # Check for name length
                    name = str(mate.name)  # get name
                    if 11 <= len(name):  # check name length
                        short_name = str(mate.name)[0:10]
                        name = short_name + '...'
                    self.elements['mate_name'] = pygame_gui.elements.ui_label.UILabel(
                        scale(pygame.Rect((306, 600), (190, 60))),
                        name,
                        object_id=get_text_box_theme())
                    self.elements['mate_info'] = pygame_gui.elements.UITextBox(
                        "mate",
                        scale(pygame.Rect((300, 650), (200, 60))),
                        object_id=get_text_box_theme(
                            "#cat_patrol_info_box"))
                    self.elements['mate_button'] = UIImageButton(scale(pygame.Rect((296, 712), (208, 52))), "",
                                                                 object_id="#patrol_select_button", manager=MANAGER)
                    # Disable mate_button if the cat is not able to go on a patrol
                    if mate not in self.able_cats:
                        self.elements['mate_button'].disable()
            # Draw mentor or apprentice
            relation = "should not display"
            if self.selected_cat.status in ['medicine cat apprentice',
                                            'apprentice'] or self.selected_cat.apprentice != []:
                self.elements['app_mentor_frame'] = pygame_gui.elements.UIImage(scale(pygame.Rect((990, 380), (332, 340))),
                                                                                self.app_frame, manager=MANAGER)

                if self.selected_cat.status in ['medicine cat apprentice',
                                                'apprentice'] and self.selected_cat.mentor is not None:
                    self.app_mentor = Cat.fetch_cat(self.selected_cat.mentor)
                    relation = 'mentor'

                elif self.selected_cat.apprentice:
                    if self.selected_apprentice_index > len(self.selected_cat.apprentice) - 1:
                        self.selected_apprentice_index = 0
                    self.app_mentor = Cat.fetch_cat(self.selected_cat.apprentice[self.selected_apprentice_index])
                    relation = 'apprentice'
                else:
                    self.app_mentor = None
                    self.elements['app_mentor_frame'].hide()

                # Failsafe, if apprentice or mentor is set to none.
                if self.app_mentor is not None:
                    name = str(self.app_mentor.name)  # get name
                    if 11 <= len(name):  # check name length
                        short_name = str(self.app_mentor.name)[0:10]
                        name = short_name + '...'
                    self.elements['app_mentor_name'] = pygame_gui.elements.ui_label.UILabel(
                        scale(pygame.Rect((1106, 600), (190, 60))),
                        name,
                        object_id=get_text_box_theme(), manager=MANAGER)
                    self.elements['app_mentor_info'] = pygame_gui.elements.UITextBox(
                        relation,
                        scale(pygame.Rect((1100, 650), (200, 60))),
                        object_id=get_text_box_theme(
                            "#cat_patrol_info_box"))
                    self.elements['app_mentor_image'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1100, 400), (200, 200))),
                                                                                    pygame.transform.scale(
                                                                                        self.app_mentor.large_sprite,
                                                                                        (200, 200)), manager=MANAGER)

                    # Button to switch to that cat
                    self.elements['app_mentor_button'] = UIImageButton(scale(pygame.Rect((1096, 712), (208, 52))), "",
                                                                       object_id="#patrol_select_button",
                                                                       manager=MANAGER)
                    # Disable mate_button if the cat is not able to go on a patrol
                    if self.app_mentor not in self.able_cats:
                        self.elements['app_mentor_button'].disable()

                    # Buttons to cycle between apprentices
                    if self.selected_cat.mentor == None:
                        self.elements['cycle_app_mentor_left_button'] = UIImageButton(scale(pygame.Rect((1096, 780), (68, 68))),
                                                                                      "",
                                                                                      object_id="#arrow_left_button",
                                                                                      manager=MANAGER)
                        self.elements['cycle_app_mentor_right_button'] = UIImageButton(
                            scale(pygame.Rect((1236, 780), (68, 68))), "", object_id="#arrow_right_button", manager=MANAGER)
                        self.update_button()

    def clear_page(self):
        """Clears all the elements"""
        for ele in self.elements:
            self.elements[ele].kill()
        self.elements = {}

    def clear_cat_buttons(self):
        for cat in self.cat_buttons:
            self.cat_buttons[cat].kill()
        self.cat_buttons = {}

    def exit_screen(self):
        self.clear_page()
        self.clear_cat_buttons()

    def on_use(self):
        pass

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]

    def get_list_text(self, patrol_list):
        if not patrol_list:
            return "None"
        # Removes duplicates.
        patrol_set = list(patrol_list)
        return ", ".join(patrol_set)

