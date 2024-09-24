from random import choice, sample

import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.ui_elements import UIImageButton, UISpriteButton
from scripts.patrol.patrol import Patrol
from scripts.utility import get_text_box_theme, scale, shorten_text_to_fit
from .Screens import Screens


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
    selected_mate_index = 0

    def __init__(self, name=None):
        super().__init__(name)
        self.fav = {}
        self.normal_event_choice = None
        self.romantic_event_choice = None
        self.intro_image = None
        self.app_mentor = None
        self.able_cats = None
        self.current_patrol = None
        self.display_text = ""
        self.results_text = ""
        self.start_patrol_thread = None
        self.proceed_patrol_thread = None
        self.outcome_art = None

    def handle_event(self, event):
        if game.switches["window_open"]:
            return
        
        if event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED:
            if self.patrol_stage == "choose_cats":
                self.handle_choose_cats_events(event)

        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if self.patrol_stage == "choose_cats":
                self.handle_choose_cats_events(event)
            elif self.patrol_stage == 'patrol_events':
                self.handle_patrol_events_event(event)
            elif self.patrol_stage == 'patrol_complete':
                self.handle_patrol_complete_events(event)

            self.menu_button_pressed(event)
            self.mute_button_pressed(event)


        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_LEFT:
                self.change_screen("list screen")
            # elif event.key == pygame.K_RIGHT:
            # self.change_screen('list screen')

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
            # Checks if the event was a double click, if it was it add/removes the cat from the patrol as long as the patrol isn't full (6 cats).
            if event.type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED:
                if self.selected_cat in self.current_patrol:
                    self.current_patrol.remove(self.selected_cat)
                elif len(self.current_patrol) < 6:
                    self.current_patrol.append(self.selected_cat)
                self.update_cat_images_buttons()
                self.update_button()
        elif event.ui_element == self.elements["add_remove_cat"]:
            if self.selected_cat in self.current_patrol:
                self.current_patrol.remove(self.selected_cat)
            else:
                self.current_patrol.append(self.selected_cat)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['add_one']:
            if len(self.current_patrol) < 6:
                if not game.clan.clan_settings['random med cat']:
                    able_no_med = [cat for cat in self.able_cats if
                                   cat.status not in ['medicine cat', 'medicine cat apprentice']]
                    if len(able_no_med) == 0:
                        able_no_med = self.able_cats
                    self.selected_cat = choice(able_no_med)
                else:
                    self.selected_cat = choice(self.able_cats)
                self.update_selected_cat()
                self.current_patrol.append(self.selected_cat)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['add_three']:
            if len(self.current_patrol) <= 3:
                if not game.clan.clan_settings['random med cat']:
                    able_no_med = [cat for cat in self.able_cats if
                                   cat.status not in ['medicine cat', 'medicine cat apprentice']]
                    if len(able_no_med) < 3:
                        able_no_med = self.able_cats
                    self.current_patrol += sample(able_no_med, k=3)
                else:
                    self.current_patrol += sample(self.able_cats, k=3)
            self.update_cat_images_buttons()
            self.update_button()
        elif event.ui_element == self.elements['add_six']:
            if len(self.current_patrol) == 0:
                if not game.clan.clan_settings['random med cat']:
                    able_no_med = [cat for cat in self.able_cats if
                                   cat.status not in ['medicine cat', 'medicine cat apprentice']]
                    if len(able_no_med) < 6:
                        able_no_med = self.able_cats
                    self.current_patrol += sample(able_no_med, k=6)
                else:
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
            self.update_button()
        elif event.ui_element == self.elements["last_page"]:
            self.current_page -= 1
            self.update_cat_images_buttons()
            self.update_button()
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
            self.start_patrol_thread = self.loading_screen_start_work(self.run_patrol_start, "start")
        elif event.ui_element == self.elements.get('mate_button'):
            self.selected_cat = self.mate
            self.update_button()
            self.update_cat_images_buttons()
            self.update_selected_cat()
        elif event.ui_element == self.elements.get('app_mentor_button'):
            self.selected_cat = self.app_mentor
            self.update_button()
            self.update_cat_images_buttons()
            self.update_selected_cat()
        elif event.ui_element == self.elements.get('cycle_app_mentor_left_button'):
            self.selected_apprentice_index -= 1
            self.app_mentor = self.selected_cat.apprentice[self.selected_apprentice_index]
            self.update_selected_cat()
            self.update_button()
        elif event.ui_element == self.elements.get('cycle_app_mentor_right_button'):
            self.selected_apprentice_index += 1
            self.app_mentor = self.selected_cat.apprentice[self.selected_apprentice_index]
            self.update_selected_cat()
            self.update_button()
        elif event.ui_element == self.elements.get('cycle_mate_left_button'):
            self.selected_mate_index -= 1
            self.mate = self.selected_cat.mate[self.selected_mate_index]
            self.update_selected_cat()
            self.update_button()
        elif event.ui_element == self.elements.get('cycle_mate_right_button'):
            self.selected_mate_index += 1
            self.mate = self.selected_cat.mate[self.selected_mate_index]
            self.update_selected_cat()
            self.update_button()

    def handle_patrol_events_event(self, event):

        inp = None
        if event.ui_element == self.elements["proceed"]:
            inp = "proceed"
        elif event.ui_element == self.elements["not_proceed"]:
            inp = "notproceed"
        elif event.ui_element == self.elements["antagonize"]:
            inp = "antagonize"

        if inp:
            self.proceed_patrol_thread = self.loading_screen_start_work(self.run_patrol_proceed, "proceed", (inp,))

    def handle_patrol_complete_events(self, event):
        if event.ui_element == self.elements['patrol_again']:
            self.open_choose_cats_screen()
        elif event.ui_element == self.elements["clan_return"]:
            self.change_screen('camp screen')

    def screen_switches(self):
        self.set_disabled_menu_buttons(["patrol_screen"])
        self.update_heading_text(f'{game.clan.name}Clan')
        self.show_mute_buttons()
        self.show_menu_buttons()
        self.open_choose_cats_screen()

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

            # making sure meds don't get the option for other patrols
            if any((cat.status in ['medicine cat', 'medicine cat apprentice'] for cat in self.current_patrol)):
                self.patrol_type = 'med'
            else:
                if self.patrol_type == 'med':
                    self.patrol_type = 'general'

            self.elements['paw'].enable()
            self.elements['mouse'].enable()
            self.elements['claws'].enable()
            self.elements['herb'].enable()
            self.elements['info'].kill()  # clearing the text before displaying new text

            if self.patrol_type != 'med' and self.current_patrol:
                self.elements['herb'].disable()
                if self.patrol_type == 'med':
                    self.patrol_type = 'general'
            if self.patrol_type == 'general':
                text = 'random patrol type'
            elif self.patrol_type == 'training':
                text = 'training'
            elif self.patrol_type == 'border':
                text = 'border'
            elif self.patrol_type == 'hunting':
                text = 'hunting'
            elif self.patrol_type == 'med':
                if self.current_patrol:
                    text = 'herb gathering'
                    self.elements['mouse'].disable()
                    self.elements['claws'].disable()
                    self.elements['paw'].disable()
                else:
                    text = 'herb gathering'
            else:
                text = ""

            self.elements['info'] = pygame_gui.elements.UITextBox(
                text, scale(pygame.Rect((500, 1050), (600, 800))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"), manager=MANAGER
            )

            able_no_med = [cat for cat in self.able_cats if
                           cat.status not in ['medicine cat', 'medicine cat apprentice']]
            if game.clan.clan_settings['random med cat']:
                able_no_med = self.able_cats
            if len(able_no_med) == 0:
                able_no_med = self.able_cats
            if len(self.current_patrol) >= 6 or len(able_no_med) < 1:
                self.elements['add_one'].disable()
                self.elements["random"].disable()
            if len(self.current_patrol) > 3 or len(able_no_med) < 3:
                self.elements['add_three'].disable()
            if len(self.current_patrol) > 0 or len(able_no_med) < 6:
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

                if 'cycle_mate_right_button' in self.elements and 'cycle_mate_left_button' in self.elements:
                    if self.selected_mate_index == len(self.selected_cat.mate) - 1:
                        self.elements['cycle_mate_right_button'].disable()
                    else:
                        self.elements['cycle_mate_left_button'].enable()

                    if self.selected_mate_index == 0:
                        self.elements['cycle_mate_left_button'].disable()
                    else:
                        self.elements['cycle_mate_left_button'].enable()

                    if len(self.selected_cat.mate) <= 0:
                        self.elements['cycle_mate_left_button'].hide()
                        self.elements['cycle_mate_right_button'].hide()

    def open_choose_cats_screen(self):
        """Opens the choose-cat patrol stage. """
        self.clear_page()  # Clear the page
        self.clear_cat_buttons()
        self.patrol_obj = Patrol()

        self.display_text = ""
        self.results_text = ""
        self.current_patrol = []
        self.current_page = 1
        self.patrol_stage = 'choose_cats'
        self.patrol_screen = 'patrol_cats'  # List

        self.elements["info"] = pygame_gui.elements.UITextBox(
            'Choose up to six cats to take on patrol.\n'
            'Smaller patrols help cats gain more experience, but larger patrols are safer.',
            scale(pygame.Rect((375, 190), (850, 200))), object_id=get_text_box_theme("#text_box_22_horizcenter"))
        self.elements["cat_frame"] = pygame_gui.elements.UIImage(scale(pygame.Rect((600, 330), (400, 550))),
                                                                 pygame.image.load(
                                                                     "resources/images/patrol_cat_frame.png").convert_alpha()
                                                                 , manager=MANAGER)
        self.elements["cat_frame"].disable()

        # Frames
        self.elements["able_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((80, 920), self.able_box.get_size())),
            self.able_box,
            starting_height=1,
            manager=MANAGER)
        self.elements["able_frame"].disable()

        self.elements["patrol_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((980, 920), self.patrol_box.get_size())),
            self.patrol_box, manager=MANAGER)
        self.elements["patrol_frame"].disable()

        # Buttons
        self.elements["add_remove_cat"] = UIImageButton(scale(pygame.Rect((700, 920), (196, 60))), "",
                                                        object_id="#add_cat_button", manager=MANAGER)
        # No cat is selected when the screen is opened, so the button is disabled
        self.elements["add_remove_cat"].disable()

        # Randomizing buttons
        self.elements["random"] = UIImageButton(
            scale(pygame.Rect((646, 990), (68, 68))), "",
            object_id="#random_dice_button",
            manager=MANAGER,
            sound_id="dice_roll")
        self.elements["add_one"] = UIImageButton(
            scale(pygame.Rect((726, 990), (68, 68))), "",
            object_id="#add_one_button",
            manager=MANAGER,
            sound_id="dice_roll")
        self.elements["add_three"] = UIImageButton(
            scale(pygame.Rect((806, 990), (68, 68))), "",
            object_id="#add_three_button",
            manager=MANAGER,
            sound_id="dice_roll")
        self.elements["add_six"] = UIImageButton(
            scale(pygame.Rect((886, 990), (68, 68))), "",
            object_id="#add_six_button",
            manager=MANAGER,
            sound_id="dice_roll")

        # patrol type buttons - disabled for now
        self.elements['paw'] = UIImageButton(scale(pygame.Rect((646, 1120), (68, 68))), "",
                                             object_id="#paw_patrol_button"
                                             , manager=MANAGER)
        self.elements['paw'].disable()
        self.elements['mouse'] = UIImageButton(scale(pygame.Rect((726, 1120), (68, 68))), "",
                                               object_id="#mouse_patrol_button"
                                               , manager=MANAGER)
        self.elements['mouse'].disable()
        self.elements['claws'] = UIImageButton(scale(pygame.Rect((806, 1120), (68, 68))), "",
                                               object_id="#claws_patrol_button"
                                               , manager=MANAGER)
        self.elements['claws'].disable()
        self.elements['herb'] = UIImageButton(scale(pygame.Rect((886, 1120), (68, 68))), "",
                                              object_id="#herb_patrol_button"
                                              , manager=MANAGER)
        self.elements['herb'].disable()

        # Able cat page buttons
        self.elements['last_page'] = UIImageButton(scale(pygame.Rect((150, 924), (68, 68))), "",
                                                   object_id="#patrol_last_page",
                                                   starting_height=2,
                                                   manager=MANAGER)
        self.elements['next_page'] = UIImageButton(scale(pygame.Rect((482, 924), (68, 68))), "",
                                                   object_id="#patrol_next_page",
                                                   starting_height=2,
                                                   manager=MANAGER)

        # Tabs for the current patrol
        self.elements['patrol_tab'] = UIImageButton(scale(pygame.Rect((1010, 920), (160, 70))), "",
                                                    starting_height=2,
                                                    object_id="#patrol_cats_tab", manager=MANAGER)
        self.elements['patrol_tab'].disable()  # We start on the patrol_cats_tab
        self.elements['skills'] = UIImageButton(scale(pygame.Rect((1180, 920), (308, 70))), "",
                                                starting_height=2,
                                                object_id="#skills_cats_tab", manager=MANAGER)

        # Remove all button
        self.elements['remove_all'] = UIImageButton(scale(pygame.Rect((1120, 1254), (248, 70))), "",
                                                    starting_height=2,
                                                    object_id="#remove_all_button", manager=MANAGER)

        # Text box for skills and traits. Hidden for now, and with no text in it
        self.elements["skills_box"] = pygame_gui.elements.UITextBox("",
                                                                    scale(pygame.Rect((1020, 1020), (480, 180))),
                                                                    visible=False,
                                                                    object_id="#text_box_22_horizcenter_spacing_95",
                                                                    manager=MANAGER)

        # Start Patrol Button
        self.elements['patrol_start'] = UIImageButton(scale(pygame.Rect((666, 1200), (270, 60))), "",
                                                      object_id="#start_patrol_button", manager=MANAGER)
        self.elements['patrol_start'].disable()

        # add prey information
        if game.clan.game_mode != 'classic':
            current_amount = round(game.clan.freshkill_pile.total_amount, 2)
            self.elements['current_prey'] = pygame_gui.elements.UITextBox(
                f"current prey: {current_amount}", scale(pygame.Rect((600, 1260), (400, 800))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"), manager=MANAGER
            )
            needed_amount = round(game.clan.freshkill_pile.amount_food_needed(), 2)
            self.elements['needed_prey'] = pygame_gui.elements.UITextBox(
                f"needed prey: {needed_amount}", scale(pygame.Rect((600, 1295), (400, 800))),
                object_id=get_text_box_theme("#text_box_30_horizcenter"), manager=MANAGER
            )
        self.update_cat_images_buttons()
        self.update_button()

    def run_patrol_start(self):
        """Runs patrol start. To be run in a seperate thread.  """
        try:
            self.display_text = self.patrol_obj.setup_patrol(self.current_patrol, self.patrol_type)
        except RuntimeError:
            self.display_text = None

    def open_patrol_event_screen(self):
        """Open the patrol event screen. This sets up the patrol starting"""
        self.clear_page()
        self.clear_cat_buttons()
        self.patrol_stage = 'patrol_events'

        if self.display_text is None:
            # No patrol events were found. 
            self.change_screen("camp screen")
            return

        # Layout images
        self.elements['event_bg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((762, 330), (708, 540))),
                                                                pygame.transform.scale(
                                                                    pygame.image.load(
                                                                        "resources/images/patrol_event_frame.png").convert_alpha(),
                                                                    (708, 540)
                                                                ), manager=MANAGER)
        self.elements['event_bg'].disable()
        self.elements['info_bg'] = pygame_gui.elements.UIImage(scale(pygame.Rect((180, 912), (840, 408))),
                                                               pygame.transform.scale(
                                                                   pygame.image.load(
                                                                       "resources/images/patrol_info.png").convert_alpha(),
                                                                   (840, 408)
                                                               ), manager=MANAGER)
        self.elements['image_frame'] = pygame_gui.elements.UIImage(scale(pygame.Rect((130, 280), (640, 640))),
                                                                   pygame.transform.scale(
                                                                       pygame.image.load(
                                                                           "resources/images/patrol_sprite_frame.png").convert_alpha(),
                                                                       (640, 640)
                                                                   ), manager=MANAGER)

        self.elements['intro_image'] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((150, 300), (600, 600))),
            pygame.transform.scale(
                self.patrol_obj.get_patrol_art(), (600, 600))
        )

        # Prepare Intro Text
        # adjusting text for solo patrols
        # intro_text = adjust_patrol_text(intro_text, self.patrol_obj)
        self.elements["patrol_text"] = pygame_gui.elements.UITextBox(self.display_text,
                                                                     scale(pygame.Rect((770, 345), (670, 500))),
                                                                     object_id="#text_box_30_horizleft_pad_10_10_spacing_95",
                                                                     manager=MANAGER)
        # Patrol Info
        # TEXT CATEGORIES AND CHECKING FOR REPEATS
        members = []
        skills = []
        traits = []
        for x in self.patrol_obj.patrol_cats:
            if x != self.patrol_obj.patrol_leader:
                members.append(str(x.name))
        for x in self.patrol_obj.patrol_cats:
            if x.personality.trait not in traits:
                traits.append(x.personality.trait)

            if x.skills.primary and x.skills.primary.get_short_skill() not in skills:
                skills.append(x.skills.primary.get_short_skill())

            if x.skills.secondary and x.skills.secondary.get_short_skill() not in skills:
                skills.append(x.skills.secondary.get_short_skill())

        self.elements['patrol_info'] = pygame_gui.elements.UITextBox(
            f'patrol leader: {str(self.patrol_obj.patrol_leader.name)} \n'
            f'patrol members: {self.get_list_text(members)} \n'
            f'patrol skills: {self.get_list_text(skills)} \n'
            f'patrol traits: {self.get_list_text(traits)}',
            scale(pygame.Rect((210, 920), (480, 400))),
            object_id="#text_box_22_horizleft",
            manager=MANAGER)

        # Draw Patrol Cats
        pos_x = 800
        pos_y = 950
        for u in range(6):
            if u < len(self.patrol_obj.patrol_cats):
                self.elements["cat" + str(u)] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                    self.patrol_obj.patrol_cats[u].sprite,
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
                                                    object_id="#antagonize_button",
                                                    manager=MANAGER,
                                                    sound_id="antagonize")
        if not self.patrol_obj.patrol_event.antag_success_outcomes:
            self.elements["antagonize"].hide()

    def run_patrol_proceed(self, user_input):
        """Proceeds the patrol - to be run in the seperate thread. """

        if user_input in ["nopro", "notproceed"]:
            self.display_text, self.results_text, self.outcome_art = self.patrol_obj.proceed_patrol("decline")
        elif user_input in ["antag", "antagonize"]:
            self.display_text, self.results_text, self.outcome_art = self.patrol_obj.proceed_patrol("antag")
        else:
            self.display_text, self.results_text, self.outcome_art = self.patrol_obj.proceed_patrol("proceed")

    def open_patrol_complete_screen(self):
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

        # Update patrol art, if needed.
        if self.outcome_art is not None and self.elements.get('intro_image') is not None:
            self.elements['intro_image'].set_image(self.outcome_art)

        self.elements["patrol_results"] = pygame_gui.elements.UITextBox("",
                                                                        scale(pygame.Rect((1100, 1000), (344, 300))),
                                                                        object_id=get_text_box_theme(
                                                                            "#text_box_22_horizcenter_spacing_95"),
                                                                        manager=MANAGER)
        self.elements["patrol_results"].set_text(self.results_text)

        self.elements["patrol_text"].set_text(self.display_text)

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
            if not the_cat.dead and the_cat.in_camp and the_cat.ID not in game.patrolled and the_cat.status not in [
                'elder', 'kitten', 'mediator', 'mediator apprentice'
            ] and not the_cat.outside and the_cat not in self.current_patrol and not the_cat.not_working():
                if the_cat.status == 'newborn' or game.config['fun']['all_cats_are_newborn']:
                    if game.config['fun']['newborns_can_patrol']:
                        self.able_cats.append(the_cat)
                else:
                    self.able_cats.append(the_cat)

        if not self.able_cats:
            all_pages = []
        else:
            all_pages = self.chunks(self.able_cats, 15)

        self.current_page = max(1, min(self.current_page, len(all_pages)))

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
            if game.clan.clan_settings["show fav"] and cat.favourite:
                self.fav[str(i)] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                    pygame.transform.scale(
                        pygame.image.load(
                            f"resources/images/fav_marker.png").convert_alpha(),
                        (100, 100))
                )
                self.fav[str(i)].disable()
            self.cat_buttons["able_cat" + str(i)] = UISpriteButton(scale(pygame.Rect((pos_x, pos_y), (100, 100))),
                                                                   pygame.transform.scale(cat.sprite, (100, 100))
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
                                                                         pygame.transform.scale(cat.sprite,
                                                                                                (100, 100)),
                                                                         cat_object=cat, manager=MANAGER)
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
                if x.skills.primary and x.skills.primary.get_short_skill() not in patrol_skills:
                    patrol_skills.append(x.skills.primary.get_short_skill())

                if x.skills.secondary and x.skills.secondary.get_short_skill() not in patrol_skills:
                    patrol_skills.append(x.skills.secondary.get_short_skill())

                if x.personality.trait not in patrol_traits:
                    patrol_traits.append(x.personality.trait)

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
        if 'cycle_mate_left_button' in self.elements:
            self.elements['cycle_mate_left_button'].kill()
            del self.elements['cycle_mate_left_button']
        if 'cycle_mate_right_button' in self.elements:
            self.elements['cycle_mate_right_button'].kill()
            del self.elements['cycle_mate_right_button']

        if self.selected_cat is not None:
            # Now, if the selected cat is not None, we rebuild everything with the correct cat info
            # Selected Cat Image
            self.elements["selected_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((640, 350), (300, 300))),
                                                                          pygame.transform.scale(
                                                                              self.selected_cat.sprite,
                                                                              (300, 300)),
                                                                          manager=MANAGER)

            name = str(self.selected_cat.name)  # get name
            short_name = shorten_text_to_fit(name, 350, 30)

            self.elements['selected_name'] = pygame_gui.elements.UITextBox(short_name,
                                                                           scale(pygame.Rect((600, 650), (400, 80))),
                                                                           object_id=get_text_box_theme(
                                                                               "#text_box_30_horizcenter"),
                                                                           manager=MANAGER)

            self.elements['selected_bio'] = pygame_gui.elements.UITextBox(str(self.selected_cat.status) +
                                                                          "\n" + str(
                self.selected_cat.personality.trait) +
                                                                          "\n" + str(
                self.selected_cat.skills.skill_string(short=True)) +
                                                                          "\n" + str(
                self.selected_cat.experience_level) +
                                                                          (f' ({str(self.selected_cat.experience)})' if
                                                                           game.clan.clan_settings['showxp'] else ''),
                                                                          scale(pygame.Rect((600, 700), (400, 150))),
                                                                          object_id=get_text_box_theme(
                                                                              "#text_box_22_horizcenter_spacing_95"),
                                                                          manager=MANAGER)

            # Show Cat's Mate, if they have one
            if len(self.selected_cat.mate) > 0:
                if self.selected_mate_index > len(self.selected_cat.mate) - 1:
                    self.selected_mate_index = 0
                self.mate = Cat.fetch_cat(self.selected_cat.mate[self.selected_mate_index])
                self.elements['mate_frame'] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((280, 380), (332, 340))),
                    self.mate_frame)
                self.elements['mate_image'] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((300, 400), (200, 200))),
                    pygame.transform.scale(
                        self.mate.sprite, (200, 200))
                    , manager=MANAGER)
                # Check for name length
                name = str(self.mate.name)  # get name
                short_name = shorten_text_to_fit(name, 145, 22)
                self.elements['mate_name'] = pygame_gui.elements.ui_label.UILabel(
                    scale(pygame.Rect((306, 600), (190, 60))),
                    short_name,
                    object_id=get_text_box_theme())
                self.elements['mate_info'] = pygame_gui.elements.UITextBox(
                    "mate",
                    scale(pygame.Rect((300, 650), (200, 60))),
                    object_id=get_text_box_theme("#text_box_22_horizcenter"))
                self.elements['mate_button'] = UIImageButton(scale(pygame.Rect((296, 712), (208, 52))), "",
                                                             object_id="#patrol_select_button", manager=MANAGER)
                # Disable mate_button if the cat is not able to go on a patrol
                if self.mate not in self.able_cats:
                    self.elements['mate_button'].disable()

                # Buttons to cycle between mates
                if len(self.selected_cat.mate) > 1:
                    self.elements['cycle_mate_left_button'] = UIImageButton(
                        scale(pygame.Rect((296, 780), (68, 68))),
                        "",
                        object_id="#arrow_left_button",
                        manager=MANAGER)
                    self.elements['cycle_mate_right_button'] = UIImageButton(
                        scale(pygame.Rect((436, 780), (68, 68))),
                        "",
                        object_id="#arrow_right_button",
                        manager=MANAGER)
                    self.update_button()

            # Draw mentor or apprentice
            relation = "should not display"
            if self.selected_cat.status in ['medicine cat apprentice',
                                            'apprentice'] or self.selected_cat.apprentice != []:
                self.elements['app_mentor_frame'] = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((990, 380), (332, 340))),
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
                    short_name = shorten_text_to_fit(name, 145, 22)
                    self.elements['app_mentor_name'] = pygame_gui.elements.ui_label.UILabel(
                        scale(pygame.Rect((1106, 600), (190, 60))),
                        short_name,
                        object_id=get_text_box_theme(), manager=MANAGER)
                    self.elements['app_mentor_info'] = pygame_gui.elements.UITextBox(
                        relation,
                        scale(pygame.Rect((1100, 650), (200, 60))),
                        object_id=get_text_box_theme("#text_box_22_horizcenter"))
                    self.elements['app_mentor_image'] = pygame_gui.elements.UIImage(
                        scale(pygame.Rect((1100, 400), (200, 200))),
                        pygame.transform.scale(
                            self.app_mentor.sprite,
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
                        self.elements['cycle_app_mentor_left_button'] = UIImageButton(
                            scale(pygame.Rect((1096, 780), (68, 68))),
                            "",
                            object_id="#arrow_left_button",
                            manager=MANAGER)
                        self.elements['cycle_app_mentor_right_button'] = UIImageButton(
                            scale(pygame.Rect((1236, 780), (68, 68))), "", object_id="#arrow_right_button",
                            manager=MANAGER)
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
        for marker in self.fav:
            self.fav[marker].kill()
        self.fav = {}

    def exit_screen(self):
        self.clear_page()
        self.clear_cat_buttons()
        self.hide_menu_buttons()

    def on_use(self):

        self.loading_screen_on_use(self.start_patrol_thread, self.open_patrol_event_screen, (700, 500))
        self.loading_screen_on_use(self.proceed_patrol_thread, self.open_patrol_complete_screen, (350, 500))

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]

    def get_list_text(self, patrol_list):
        if not patrol_list:
            return "None"
        # Removes duplicates.
        patrol_set = list(patrol_list)
        return ", ".join(patrol_set)
