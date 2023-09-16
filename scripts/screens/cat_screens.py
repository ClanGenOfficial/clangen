#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
from random import choice, randint

import pygame

from ..cat.history import History
from ..housekeeping.datadir import get_save_dir
from ..game_structure.windows import ChangeCatName, SpecifyCatGender, KillCat, SaveAsImage

import ujson

from scripts.utility import event_text_adjust, scale, ACC_DISPLAY, process_text, chunks

from .base_screens import Screens

from scripts.utility import get_text_box_theme, scale_dimentions, generate_sprite, shorten_text_to_fit
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.game_structure import image_cache
import pygame_gui
from re import sub
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER, screen
from scripts.cat.names import names, Name
from scripts.clan_resources.freshkill import FRESHKILL_ACTIVE


# ---------------------------------------------------------------------------- #
#             change how accessory info displays on cat profiles               #
# ---------------------------------------------------------------------------- #
def accessory_display_name(cat):
    accessory = cat.pelt.accessory

    if accessory is None:
        return ''
    acc_display = accessory.lower()

    if accessory in Pelt.collars:
        collar_colors = {'crimson': 'red', 'blue': 'blue', 'yellow': 'yellow', 'cyan': 'cyan',
                         'red': 'orange', 'lime': 'lime', 'green': 'green', 'rainbow': 'rainbow',
                         'black': 'black', 'spikes': 'spiky', 'white': 'white', 'pink': 'pink',
                         'purple': 'purple', 'multi': 'multi', 'indigo': 'indigo'}
        collar_color = next((color for color in collar_colors if acc_display.startswith(color)), None)

        if collar_color:
            if acc_display.endswith('bow') and not collar_color == 'rainbow':
                acc_display = collar_colors[collar_color] + ' bow'
            elif acc_display.endswith('bell'):
                acc_display = collar_colors[collar_color] + ' bell collar'
            else:
                acc_display = collar_colors[collar_color] + ' collar'

    elif accessory in Pelt.wild_accessories:
        if acc_display == 'blue feathers':
            acc_display = 'crow feathers'
        elif acc_display == 'red feathers':
            acc_display = 'cardinal feathers'

    return acc_display


# ---------------------------------------------------------------------------- #
#               assigns backstory blurbs to the backstory                      #
# ---------------------------------------------------------------------------- #
def bs_blurb_text(cat):
    backstory = cat.backstory
    backstory_text = BACKSTORIES["backstories"][backstory]
    
    if cat.status in ['kittypet', 'loner', 'rogue', 'former Clancat']:
        return f"This cat is a {cat.status} and currently resides outside of the Clans."
    
    return backstory_text

# ---------------------------------------------------------------------------- #
#             change how backstory info displays on cat profiles               #
# ---------------------------------------------------------------------------- #
def backstory_text(cat):
    backstory = cat.backstory
    if backstory is None:
        return ''
    bs_category = None
    
    for category in BACKSTORIES["backstory_categories"]:
        if backstory in category:
            bs_category = category
            break
    bs_display = BACKSTORIES["backstory_display"][bs_category]

    return bs_display

# ---------------------------------------------------------------------------- #
#                               Profile Screen                                 #
# ---------------------------------------------------------------------------- #
class ProfileScreen(Screens):
    # UI Images
    backstory_tab = image_cache.load_image("resources/images/backstory_bg.png").convert_alpha()
    conditions_tab = image_cache.load_image("resources/images/conditions_tab_backdrop.png").convert_alpha()
    condition_details_box = image_cache.load_image("resources/images/condition_details_box.png").convert_alpha()

    # Keep track of current tabs open. Can be used to keep tabs open when pages are switched, and
    # helps with exiting the screen
    open_tab = None

    def __init__(self, name=None):
        super().__init__(name)
        self.show_moons = None
        self.no_moons = None
        self.help_button = None
        self.open_sub_tab = None
        self.editing_notes = False
        self.user_notes = None
        self.save_text = None
        self.not_fav_tab = None
        self.fav_tab = None
        self.edit_text = None
        self.sub_tab_4 = None
        self.sub_tab_3 = None
        self.sub_tab_2 = None
        self.sub_tab_1 = None
        self.backstory_background = None
        self.history_text_box = None
        self.conditions_tab_button = None
        self.condition_container = None
        self.left_conditions_arrow = None
        self.right_conditions_arrow = None
        self.conditions_background = None
        self.previous_cat = None
        self.next_cat = None
        self.cat_image = None
        self.background = None
        self.cat_info_column2 = None
        self.cat_info_column1 = None
        self.cat_thought = None
        self.cat_name = None
        self.placeholder_tab_4 = None
        self.placeholder_tab_3 = None
        self.placeholder_tab_2 = None
        self.your_tab = None
        self.backstory_tab_button = None
        self.dangerous_tab_button = None
        self.personal_tab_button = None
        self.roles_tab_button = None
        self.relations_tab_button = None
        self.back_button = None
        self.previous_cat_button = None
        self.next_cat_button = None
        self.the_cat = None
        self.prevent_fading_text = None
        self.checkboxes = {}
        self.profile_elements = {}
        self.join_df_button = None
        self.exit_df_button = None

    def handle_event(self, event):

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:

            if game.switches['window_open']:
                pass
            elif event.ui_element == self.back_button:
                self.close_current_tab()
                self.change_screen(game.last_screen_forProfile)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    self.clear_profile()
                    game.switches['cat'] = self.previous_cat
                    self.build_profile()
                    self.update_disabled_buttons_and_text()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    self.clear_profile()
                    game.switches['cat'] = self.next_cat
                    self.build_profile()
                    self.update_disabled_buttons_and_text()
                else:
                    print("invalid next cat", self.previous_cat)
            elif event.ui_element == self.inspect_button:
                self.close_current_tab()
                self.change_screen("sprite inspect screen")
            elif self.the_cat.ID == game.clan.your_cat.ID and event.ui_element == self.profile_elements["change_cat"]:
                self.close_current_tab()
                self.change_screen("choose reborn screen")
            elif event.ui_element == self.relations_tab_button:
                self.toggle_relations_tab()
            elif event.ui_element == self.roles_tab_button:
                self.toggle_roles_tab()
            elif event.ui_element == self.personal_tab_button:
                self.toggle_personal_tab()
            elif event.ui_element == self.your_tab:
                self.toggle_your_tab()
            elif event.ui_element == self.dangerous_tab_button:
                self.toggle_dangerous_tab()
            elif event.ui_element == self.backstory_tab_button:
                if self.open_sub_tab is None:
                    if game.switches['favorite_sub_tab'] is None:
                        self.open_sub_tab = 'life events'
                    else:
                        self.open_sub_tab = game.switches['favorite_sub_tab']

                self.toggle_history_tab()
            elif event.ui_element == self.conditions_tab_button:
                self.toggle_conditions_tab()
            elif "leader_ceremony" in self.profile_elements and \
                    event.ui_element == self.profile_elements["leader_ceremony"]:
                self.change_screen('ceremony screen')
            elif "talk" in self.profile_elements and \
                    event.ui_element == self.profile_elements["talk"]:
                self.the_cat.talked_to = True
                self.the_cat.relationships[game.clan.your_cat.ID].platonic_like += randint(1,5)
                game.clan.your_cat.relationships[self.the_cat.ID].platonic_like += randint(1,5)
                self.change_screen('talk screen')
            elif "insult" in self.profile_elements and \
                    event.ui_element == self.profile_elements["insult"]:
                self.the_cat.insulted = True
                if game.clan.your_cat.status != "kitten":
                    self.the_cat.relationships[game.clan.your_cat.ID].dislike += randint(1,10)
                    self.the_cat.relationships[game.clan.your_cat.ID].platonic_like -= randint(1,5)
                    self.the_cat.relationships[game.clan.your_cat.ID].comfortable -= randint(1,5)
                    self.the_cat.relationships[game.clan.your_cat.ID].trust -= randint(1,5)
                    self.the_cat.relationships[game.clan.your_cat.ID].admiration -= randint(1,5)
                self.change_screen('insult screen')
            elif "flirt" in self.profile_elements and \
                    event.ui_element == self.profile_elements["flirt"]:
                self.the_cat.flirted = True
                self.change_screen('flirt screen')
            elif event.ui_element == self.profile_elements["med_den"]:
                self.change_screen('med den screen')
            elif "mediation" in self.profile_elements and event.ui_element == self.profile_elements["mediation"]:
                self.change_screen('mediation screen')
            elif event.ui_element == self.profile_elements["favourite_button"]:
                self.the_cat.favourite = False
                self.profile_elements["favourite_button"].hide()
                self.profile_elements["not_favourite_button"].show()
            elif event.ui_element == self.profile_elements["not_favourite_button"]:
                self.the_cat.favourite = True
                self.profile_elements["favourite_button"].show()
                self.profile_elements["not_favourite_button"].hide()
            else:
                self.handle_tab_events(event)

            if game.switches['window_open']:
                pass
            elif self.the_cat.dead and game.settings["fading"]:
                if event.ui_element == self.checkboxes["prevent_fading"]:
                    if self.the_cat.prevent_fading:
                        self.the_cat.prevent_fading = False
                    else:
                        self.the_cat.prevent_fading = True
                    self.clear_profile()
                    self.build_profile()

        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if game.switches['window_open']:
                pass

            elif event.key == pygame.K_LEFT:
                self.clear_profile()
                game.switches['cat'] = self.previous_cat
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.key == pygame.K_RIGHT:
                self.clear_profile()
                game.switches['cat'] = self.next_cat
                self.build_profile()
                self.update_disabled_buttons_and_text()
            
            elif event.key == pygame.K_ESCAPE:
                self.close_current_tab()
                self.change_screen(game.last_screen_forProfile)

    def handle_tab_events(self, event):
        # Relations Tab
        if self.open_tab == 'relations':
            if event.ui_element == self.family_tree_button:
                self.change_screen('see kits screen')
            elif event.ui_element == self.see_relationships_button:
                self.change_screen('relationship screen')
            elif event.ui_element == self.choose_mate_button:
                self.change_screen('choose mate screen')
            elif event.ui_element == self.change_adoptive_parent_button:
                self.change_screen('choose adoptive parent screen')

        # Roles Tab
        elif self.open_tab == 'roles':
            if event.ui_element == self.manage_roles:
                self.change_screen('role screen')
            elif event.ui_element == self.change_mentor_button:
                self.change_screen('choose mentor screen')
        # Personal Tab
        elif self.open_tab == 'personal':
            if event.ui_element == self.change_name_button:
                ChangeCatName(self.the_cat)
            elif event.ui_element == self.specify_gender_button:
                SpecifyCatGender(self.the_cat)
                '''if self.the_cat.genderalign in ["female", "trans female"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[1].copy()]
                elif self.the_cat.genderalign in ["male", "trans male"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[2].copy()]
                else: self.the_cat.pronouns = [self.the_cat.default_pronouns[0].copy()]'''
            #when button is pressed...
            elif event.ui_element == self.cis_trans_button:
                #if the cat is anything besides m/f/transm/transf then turn them back to cis
                if self.the_cat.genderalign not in ["female", "trans female", "male", "trans male"]:
                    self.the_cat.genderalign = self.the_cat.gender
                elif self.the_cat.gender == "male" and self.the_cat.genderalign == 'female':
                    self.the_cat.genderalign = self.the_cat.gender
                elif self.the_cat.gender == "female" and self.the_cat.genderalign == 'male':
                    self.the_cat.genderalign = self.the_cat.gender
                #if the cat is cis (gender & gender align are the same) then set them to trans
                #cis males -> trans female first
                elif self.the_cat.gender == "male" and self.the_cat.genderalign == 'male':
                    self.the_cat.genderalign = 'trans female'
                #cis females -> trans male
                elif self.the_cat.gender == "female" and self.the_cat.genderalign == 'female':
                    self.the_cat.genderalign = 'trans male'
                #if the cat is trans then set them to nonbinary
                elif self.the_cat.genderalign in ["trans female", "trans male"]:
                    self.the_cat.genderalign = 'nonbinary'
                '''#pronoun handler
                if self.the_cat.genderalign in ["female", "trans female"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[1].copy()]
                elif self.the_cat.genderalign in ["male", "trans male"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[2].copy()]
                elif self.the_cat.genderalign in ["nonbinary"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[0].copy()]
                elif self.the_cat.genderalign not in ["female", "trans female", "male", "trans male"]:
                    self.the_cat.pronouns = [self.the_cat.default_pronouns[0].copy()]'''
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.toggle_kits:
                if self.the_cat.no_kits:
                    self.the_cat.no_kits = False
                else:
                    self.the_cat.no_kits = True
                self.update_disabled_buttons_and_text()
        elif self.open_tab == 'your tab':
            if event.ui_element == self.have_kits_button:
                if 'have kits' not in game.switches:
                    game.switches['have kits'] = True
                if game.switches.get('have kits'):
                    game.clan.your_cat.no_kits = False
                    relation = Pregnancy_Events()
                    relation.handle_having_kits(game.clan.your_cat, game.clan)
                    game.switches['have kits'] = False
                    self.have_kits_button.disable()
            if event.ui_element == self.request_apprentice_button:
                if 'request apprentice' not in game.switches:
                    game.switches['request apprentice'] = False
                if not game.switches['request apprentice']:
                    game.switches['request apprentice'] = True
                    self.request_apprentice_button.disable()
            if event.ui_element == self.change_accessory_button:
                self.change_screen("accessory screen")
        # Dangerous Tab
        elif self.open_tab == 'dangerous':
            if event.ui_element == self.kill_cat_button:
                KillCat(self.the_cat)
            elif event.ui_element == self.murder_cat_button:
                self.change_screen('murder screen')
            elif event.ui_element == self.join_df_button:
                game.clan.your_cat.joined_df = True
                self.join_df_button.disable()
            elif event.ui_element == self.exit_df_button:
                game.clan.your_cat.joined_df = False
                self.exit_df_button.disable()
            elif event.ui_element == self.exile_cat_button:
                if not self.the_cat.dead and not self.the_cat.exiled:
                    Cat.exile(self.the_cat)
                    self.clear_profile()
                    self.build_profile()
                    self.update_disabled_buttons_and_text()
                if self.the_cat.dead:
                    if self.the_cat.df is True:
                        self.the_cat.outside, self.the_cat.exiled = False, False
                        self.the_cat.df = False
                        game.clan.add_to_starclan(self.the_cat)
                        self.the_cat.thought = "Is relieved to once again hunt in StarClan"
                    else:
                        self.the_cat.outside, self.the_cat.exiled = False, False
                        self.the_cat.df = True
                        game.clan.add_to_darkforest(self.the_cat)
                        self.the_cat.thought = "Is distraught after being sent to the Place of No Stars"

                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
        # History Tab
        elif self.open_tab == 'history':
            if event.ui_element == self.sub_tab_1:
                if self.open_sub_tab == 'user notes':
                    self.notes_entry.kill()
                    self.display_notes.kill()
                    if self.edit_text:
                        self.edit_text.kill()
                    if self.save_text:
                        self.save_text.kill()
                    self.help_button.kill()
                self.open_sub_tab = 'life events'
                self.toggle_history_sub_tab()
            elif event.ui_element == self.sub_tab_2:
                if self.open_sub_tab == 'life events':
                    self.history_text_box.kill()
                self.open_sub_tab = 'user notes'
                self.toggle_history_sub_tab()
            elif event.ui_element == self.fav_tab:
                game.switches['favorite_sub_tab'] = None
                self.fav_tab.hide()
                self.not_fav_tab.show()
            elif event.ui_element == self.not_fav_tab:
                game.switches['favorite_sub_tab'] = self.open_sub_tab
                self.fav_tab.show()
                self.not_fav_tab.hide()
            elif event.ui_element == self.save_text:
                self.user_notes = sub(r"[^A-Za-z0-9<->/.()*'&#!?,| ]+", "", self.notes_entry.get_text())
                self.save_user_notes()
                self.editing_notes = False
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.edit_text:
                self.editing_notes = True
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.no_moons:
                game.switches["show_history_moons"] = True
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.show_moons:
                game.switches["show_history_moons"] = False
                self.update_disabled_buttons_and_text()

        # Conditions Tab
        elif self.open_tab == 'conditions':
            if event.ui_element == self.right_conditions_arrow:
                self.conditions_page += 1
                self.display_conditions_page()
            if event.ui_element == self.left_conditions_arrow:
                self.conditions_page -= 1
                self.display_conditions_page()
        

    def screen_switches(self):
        self.the_cat = Cat.all_cats.get(game.switches['cat'])

        # Set up the menu buttons, which appear on all cat profile images.
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "", object_id="#next_cat_button"
                                             , manager=MANAGER)
        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button"
                                                 , manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 120), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.inspect_button = UIImageButton(scale(pygame.Rect((1482, 120),(68,68))), "", 
                                            object_id="#magnify_button",
                                            manager=MANAGER)
        self.relations_tab_button = UIImageButton(scale(pygame.Rect((96, 840), (352, 60))), "",
                                                  object_id="#relations_tab_button", manager=MANAGER)
        self.roles_tab_button = UIImageButton(scale(pygame.Rect((448, 840), (352, 60))), "",
                                              object_id="#roles_tab_button"
                                              , manager=MANAGER)
        self.personal_tab_button = UIImageButton(scale(pygame.Rect((800, 840), (352, 60))), "",
                                                 object_id="#personal_tab_button", manager=MANAGER)
        self.dangerous_tab_button = UIImageButton(scale(pygame.Rect((1152, 840), (352, 60))), "",
                                                  object_id="#dangerous_tab_button", manager=MANAGER)

        self.backstory_tab_button = UIImageButton(scale(pygame.Rect((96, 1244), (352, 60))), "",
                                                  object_id="#backstory_tab_button", manager=MANAGER)

        self.conditions_tab_button = UIImageButton(
            scale(pygame.Rect((448, 1244), (352, 60))),
            "",
            object_id="#conditions_tab_button", manager=MANAGER
        )


        self.placeholder_tab_3 = UIImageButton(scale(pygame.Rect((800, 1244), (352, 60))), "",
                                               object_id="#cat_tab_3_blank_button", starting_height=1, manager=MANAGER)
        self.placeholder_tab_3.disable()

        self.placeholder_tab_4 = UIImageButton(scale(pygame.Rect((1152, 1244), (352, 60))), "",
                                               object_id="#cat_tab_4_blank_button", manager=MANAGER)
        self.placeholder_tab_4.disable()
        
        if 'have kits' not in game.switches:
            game.switches['have kits'] = True

        self.build_profile()

        self.hide_menu_buttons()  # Menu buttons don't appear on the profile screen
        if game.last_screen_forProfile == 'med den screen':
            self.toggle_conditions_tab()

    def clear_profile(self):
        """Clears all profile objects. """
        for ele in self.profile_elements:
            self.profile_elements[ele].kill()
        self.profile_elements = {}

        if self.user_notes:
            self.user_notes = 'Click the check mark to enter notes about your cat!'

        for box in self.checkboxes:
            self.checkboxes[box].kill()
        self.checkboxes = {}

    def exit_screen(self):
        self.clear_profile()
        self.back_button.kill()
        self.next_cat_button.kill()
        self.previous_cat_button.kill()
        self.relations_tab_button.kill()
        self.roles_tab_button.kill()
        self.personal_tab_button.kill()
        self.dangerous_tab_button.kill()
        self.backstory_tab_button.kill()
        self.conditions_tab_button.kill()
        self.placeholder_tab_3.kill()
        self.placeholder_tab_4.kill()
        self.inspect_button.kill()
        self.close_current_tab()

    def build_profile(self):
        """Rebuild builds the cat profile. Run when you switch cats
            or for changes in the profile."""
        self.the_cat = Cat.all_cats.get(game.switches["cat"])

        # use these attributes to create differing profiles for StarClan cats etc.
        is_sc_instructor = False
        is_df_instructor = False
        if self.the_cat is None:
            return
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID and self.the_cat.df is False:
            is_sc_instructor = True
        elif self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID and self.the_cat.df is True:
            is_df_instructor = True

        # Info in string
        cat_name = str(self.the_cat.name)
        cat_name = shorten_text_to_fit(cat_name, 425, 40)
        if self.the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        if is_sc_instructor:
            self.the_cat.thought = "Hello. I am here to guide the dead cats of " + game.clan.name + "Clan into StarClan."
        if is_df_instructor:
            self.the_cat.thought = "Hello. I am here to drag the dead cats of " + game.clan.name + "Clan into the Dark Forest."


        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(cat_name,
                                                                          scale(pygame.Rect((50, 280), (-1, 80))),
                                                                          object_id=get_text_box_theme(
                                                                              "#text_box_40_horizcenter"),
                                                                          manager=MANAGER)
        name_text_size = self.profile_elements["cat_name"].get_relative_rect()

        self.profile_elements["cat_name"].kill()

        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(cat_name,
                                                                          scale(pygame.Rect(
                                                                              (800 - name_text_size.width, 280),
                                                                              (name_text_size.width * 2, 80))),
                                                                          object_id=get_text_box_theme(
                                                                              "#text_box_40_horizcenter"),
                                                                          manager=MANAGER)

        # Write cat thought
        self.profile_elements["cat_thought"] = pygame_gui.elements.UITextBox(self.the_cat.thought,
                                                                             scale(pygame.Rect((200, 340), (1200, 80))),
                                                                             wrap_to_height=True,
                                                                             object_id=get_text_box_theme(
                                                                                 "#text_box_30_horizcenter_spacing_95")
                                                                             , manager=MANAGER)

        self.profile_elements["cat_info_column1"] = UITextBoxTweaked(self.generate_column1(self.the_cat),
                                                                     scale(pygame.Rect((600, 460), (360, 380))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_22_horizleft"),
                                                                     line_spacing=0.95, manager=MANAGER)
        self.profile_elements["cat_info_column2"] = UITextBoxTweaked(self.generate_column2(self.the_cat),
                                                                     scale(pygame.Rect((980, 460), (500, 360))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_22_horizleft"),
                                                                     line_spacing=0.95, manager=MANAGER)

        # Set the cat backgrounds.
        if game.settings['backgrounds']:
            self.profile_elements["background"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((110, 400), (480, 420))),
                pygame.transform.scale(self.get_platform(), scale_dimentions((480, 420))), 
                manager=MANAGER)
            self.profile_elements["background"].disable()

        # Create cat image object
        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((200, 400), (300, 300))),

                                                                         pygame.transform.scale(
                                                                             self.the_cat.sprite,
                                                                             (300, 300)), manager=MANAGER)
        self.profile_elements["cat_image"].disable()

        # if cat is a med or med app, show button for their den
        self.profile_elements["med_den"] = UIImageButton(scale(pygame.Rect
                                                               ((200, 760), (302, 56))),
                                                         "",
                                                         object_id="#med_den_button",
                                                         manager=MANAGER,
                                                         starting_height=2)
        if not (self.the_cat.dead or self.the_cat.outside) and (
                self.the_cat.status in ['medicine cat', 'medicine cat apprentice'] or
                self.the_cat.is_ill() or
                self.the_cat.is_injured()):
            self.profile_elements["med_den"].show()
        else:
            self.profile_elements["med_den"].hide()

        # Fullscreen
        if game.settings['fullscreen']:
            x_pos = 745 - name_text_size.width//2
        else:
            x_pos = 740 - name_text_size.width

        self.profile_elements["favourite_button"] = UIImageButton(scale(pygame.Rect
                                                                        ((x_pos, 287), (56, 56))),
                                                                  "",
                                                                  object_id="#fav_cat",
                                                                  manager=MANAGER,
                                                                  tool_tip_text='Remove favorite status',
                                                                  starting_height=2)

        self.profile_elements["not_favourite_button"] = UIImageButton(scale(pygame.Rect
                                                                            ((x_pos, 287),
                                                                             (56, 56))),
                                                                      "",
                                                                      object_id="#not_fav_cat",
                                                                      manager=MANAGER,
                                                                      tool_tip_text='Mark as favorite',
                                                                      starting_height=2)

        if self.the_cat.favourite:
            self.profile_elements["favourite_button"].show()
            self.profile_elements["not_favourite_button"].hide()
        else:
            self.profile_elements["favourite_button"].hide()
            self.profile_elements["not_favourite_button"].show()

        # Determine where the next and previous cat buttons lead
        self.determine_previous_and_next_cat()

        # Disable and enable next and previous cat buttons as needed.
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

        if self.open_tab == "history" and self.open_sub_tab == 'user notes':
            self.load_user_notes()
        
        if not game.clan.your_cat:
            print("Are you playing a normal ClanGen save? Switch to a LifeGen save or create a new cat!")
            print("Choosing random cat to play...")
            game.clan.your_cat = Cat.all_cats[choice(game.clan.clan_cats)]
            counter = 0
            while game.clan.your_cat.dead or game.clan.your_cat.outside:
                if counter == 25:
                    break
                game.clan.your_cat = Cat.all_cats[choice(game.clan.clan_cats)]
                counter+=1
                
            print("Chose " + str(game.clan.your_cat.name))
            
        if self.the_cat.ID == game.clan.your_cat.ID:
            self.profile_elements["change_cat"] = UIImageButton(scale(pygame.Rect((1400, 120),(68,68))), "", 
                                            object_id="#random_dice_button",
                                            tool_tip_text='Switch MC',
                                            manager=MANAGER)
        
        if self.the_cat.ID != game.clan.your_cat.ID and not self.the_cat.dead and not self.the_cat.outside and not game.clan.your_cat.dead and not game.clan.your_cat.outside and not game.clan.your_cat.moons < 0:    
            if not self.the_cat.dead and not self.the_cat.outside and self.the_cat.status not in ['leader', 'mediator', 'mediator apprentice']:
                self.profile_elements["talk"] = UIImageButton(scale(pygame.Rect(
                    (726, 220), (68, 68))),
                    "",
                    object_id="#talk_button",
                    tool_tip_text="Talk to this Cat", manager=MANAGER
                )
                if self.the_cat.talked_to:
                    self.profile_elements["talk"].disable()
                else:
                    self.profile_elements["talk"].enable()
            elif not self.the_cat.dead and not self.the_cat.outside and self.the_cat.status in ['leader', 'mediator', 'mediator apprentice']:
                self.profile_elements["talk"] = UIImageButton(scale(pygame.Rect(
                    (662, 220), (68, 68))),
                    "",
                    object_id="#talk_button",
                    tool_tip_text="Talk to this Cat", manager=MANAGER
                )
                if self.the_cat.talked_to:
                    self.profile_elements["talk"].disable()
                else:
                    self.profile_elements["talk"].enable()
        if self.the_cat.ID != game.clan.your_cat.ID and not self.the_cat.dead and not self.the_cat.outside and not game.clan.your_cat.dead and not game.clan.your_cat.outside and not game.clan.your_cat.moons < 0:    
            if not self.the_cat.dead and not self.the_cat.outside and self.the_cat.status not in ['leader', 'mediator', 'mediator apprentice']:
                self.profile_elements["insult"] = UIImageButton(scale(pygame.Rect(
                    (806, 220), (68, 68))),
                    "",
                    object_id="#insult_button",
                    tool_tip_text="Insult this Cat", manager=MANAGER
                )
                if self.the_cat.insulted:
                    self.profile_elements["insult"].disable()
                else:
                    self.profile_elements["insult"].enable()
            elif not self.the_cat.dead and not self.the_cat.outside and self.the_cat.status in ['leader', 'mediator', 'mediator apprentice']:
                self.profile_elements["insult"] = UIImageButton(scale(pygame.Rect(
                    (830, 220), (68, 68))),
                    "",
                    object_id="#insult_button",
                    tool_tip_text="Insult this Cat", manager=MANAGER
                )
                if self.the_cat.insulted:
                    self.profile_elements["insult"].disable()
                else:
                    self.profile_elements["insult"].enable()
            
            if (self.the_cat.ID not in game.clan.your_cat.get_relatives() and self.the_cat.moons >= 12 and self.the_cat.moons < game.clan.your_cat.moons + 40 and self.the_cat.moons > game.clan.your_cat.moons - 40 and game.clan.your_cat.moons >= 12) or self.the_cat.ID in game.clan.your_cat.mate:
                if not self.the_cat.dead and not self.the_cat.outside and self.the_cat.status not in ['leader', 'mediator', 'mediator apprentice']:
                    self.profile_elements["flirt"] = UIImageButton(scale(pygame.Rect(
                        (646, 220), (68, 68))),
                        "",
                        object_id="#flirt_button",
                        tool_tip_text="Flirt with this Cat", manager=MANAGER
                    )
                    if self.the_cat.flirted:
                        self.profile_elements["flirt"].disable()
                    else:
                        self.profile_elements["flirt"].enable()
                elif not self.the_cat.dead and not self.the_cat.outside and self.the_cat.status in ['leader', 'mediator', 'mediator apprentice']:
                    self.profile_elements["flirt"] = UIImageButton(scale(pygame.Rect(
                        (910, 220), (68, 68))),
                        "",
                        object_id="#flirt_button",
                        tool_tip_text="Flirt with this Cat", manager=MANAGER
                    )
                    if self.the_cat.flirted:
                        self.profile_elements["flirt"].disable()
                    else:
                        self.profile_elements["flirt"].enable()
            elif self.the_cat.ID not in game.clan.your_cat.get_relatives() and game.clan.your_cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"] and self.the_cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"]:
                if not self.the_cat.dead and not self.the_cat.outside and self.the_cat.status not in ['mediator apprentice']:
                    self.profile_elements["flirt"] = UIImageButton(scale(pygame.Rect(
                        (646, 220), (68, 68))),
                        "",
                        object_id="#flirt_button",
                        tool_tip_text="Flirt with this Cat", manager=MANAGER
                    )
                    if self.the_cat.flirted:
                        self.profile_elements["flirt"].disable()
                    else:
                        self.profile_elements["flirt"].enable()
                elif not self.the_cat.dead and not self.the_cat.outside and self.the_cat.status in ['mediator apprentice']:
                    self.profile_elements["flirt"] = UIImageButton(scale(pygame.Rect(
                        (910, 220), (68, 68))),
                        "",
                        object_id="#flirt_button",
                        tool_tip_text="Flirt with this Cat", manager=MANAGER
                    )
                    if self.the_cat.flirted:
                        self.profile_elements["flirt"].disable()
                    else:
                        self.profile_elements["flirt"].enable()
        
        if self.the_cat.ID == game.clan.your_cat.ID and not game.clan.your_cat.dead and not game.clan.your_cat.outside:
            self.placeholder_tab_3.kill()
            self.profile_elements['your_tab'] = UIImageButton(scale(pygame.Rect((800, 1244), (352, 60))), "",
                                               object_id="#your_tab", starting_height=1, manager=MANAGER)
            self.your_tab = self.profile_elements['your_tab']
        else:
            if self.open_tab == 'your tab':
                self.close_current_tab()
            self.placeholder_tab_3.kill()
            self.placeholder_tab_3 = None
            self.placeholder_tab_3 = UIImageButton(scale(pygame.Rect((800, 1244), (352, 60))), "",
                                            object_id="#cat_tab_3_blank_button", starting_height=1, manager=MANAGER)


        if self.the_cat.status == 'leader' and not self.the_cat.dead:
            self.profile_elements["leader_ceremony"] = UIImageButton(scale(pygame.Rect(
                (746, 220), (68, 68))),
                "",
                object_id="#leader_ceremony_button",
                tool_tip_text="Leader Ceremony", manager=MANAGER
            )
        elif self.the_cat.status in ["mediator", "mediator apprentice"]:
            self.profile_elements["mediation"] = UIImageButton(scale(pygame.Rect(
                (746, 220), (68, 68))),
                "",
                object_id="#mediation_button", manager=MANAGER
            )
            if self.the_cat.dead or self.the_cat.outside:
                self.profile_elements["mediation"].disable()

        if game.settings["fading"]:
            if is_sc_instructor:
                self.profile_elements["prevent_fading_text"] = pygame_gui.elements.UILabel(
                    scale(pygame.Rect((170, 780), (-1, 60))),
                    "The StarClan Guide will never fade",
                    object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER)
            elif is_df_instructor:
                self.profile_elements["prevent_fading_text"] = pygame_gui.elements.UILabel(
                    scale(pygame.Rect((160, 780), (-1, 60))),
                    "The Dark Forest Guide will never fade",
                    object_id=get_text_box_theme("#text_box_22_horizleft"), manager=MANAGER)
            elif self.the_cat.dead:
                self.profile_elements["prevent_fading_text"] = pygame_gui.elements.UILabel(
                    scale(pygame.Rect((272, 774), (-1, 60))),
                    "Prevent Fading",
                    object_id=get_text_box_theme(), manager=MANAGER)

        self.update_toggle_buttons()

    def update_toggle_buttons(self):
        """Updates the image for all toggle buttons. """
        for box in self.checkboxes:
            self.checkboxes[box].kill()
        self.checkboxes = {}

        if self.the_cat.dead and game.settings["fading"]:
            if self.the_cat.prevent_fading:
                box_type = "#checked_checkbox"
            else:
                box_type = "#unchecked_checkbox"

            self.checkboxes["prevent_fading"] = UIImageButton(scale(pygame.Rect((200, 770), (68, 68))), "",
                                                              starting_height=2,
                                                              tool_tip_text="Prevents a cat from fading away."
                                                                            " If unchecked, and the cat has been dead "
                                                                            "for longer than 202 moons, they will fade "
                                                                            "on the next timeskip.",
                                                              object_id=box_type, manager=MANAGER)
            if game.clan.instructor.ID == self.the_cat.ID:
                self.checkboxes["prevent_fading"].hide()

    def determine_previous_and_next_cat(self):
        """'Determines where the next and previous buttons point too."""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        current_cat_found = 0
        if self.the_cat.dead and not is_instructor and self.the_cat.df == game.clan.instructor.df and \
                not (self.the_cat.outside or self.the_cat.exiled):
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            current_cat_found = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                current_cat_found = 1
            else:
                if current_cat_found == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead \
                        and check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded and check_cat.moons > -1:
                    previous_cat = check_cat.ID

                elif current_cat_found == 1 and check_cat != self.the_cat.ID and check_cat.dead == self.the_cat.dead \
                        and check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded and check_cat.moons > -1:
                    next_cat = check_cat.ID
                    break

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

    def generate_column1(self, the_cat):
        """Generate the left column information"""
        output = ""
        # SEX/GENDER
        if the_cat.genderalign is None or the_cat.genderalign == the_cat.gender:
            output += str(the_cat.gender)
        else:
            output += str(the_cat.genderalign)
        # NEWLINE ----------
        output += "\n"

        # AGE
        if the_cat.age == 'kitten':
            output += 'young'
        elif the_cat.age == 'senior':
            output += 'senior'
        else:
            output += the_cat.age
        # NEWLINE ----------
        output += "\n"

        # EYE COLOR
        output += 'eyes: ' + str(the_cat.describe_eyes())
        # NEWLINE ----------
        output += "\n"

        # PELT TYPE
        output += 'pelt: ' + the_cat.pelt.name.lower()
        # NEWLINE ----------
        output += "\n"

        # PELT LENGTH
        output += 'fur length: ' + the_cat.pelt.length
        # NEWLINE ----------

        # ACCESSORY
        if the_cat.pelt.accessories and the_cat.ID == game.clan.your_cat.ID:
            if len(the_cat.pelt.accessories) > 0:
                output += "\n"
                output += 'accessories: ' + str(ACC_DISPLAY[the_cat.pelt.accessories[0]]["default"])
            if len(the_cat.pelt.accessories) > 1:
                output += ' and ' + str(len(the_cat.pelt.accessories) - 1) + ' more'
        elif the_cat.pelt.accessory:
            output += "\n"
            output += 'accessory: ' + str(ACC_DISPLAY[the_cat.pelt.accessory]["default"])
            # NEWLINE ----------

        # PARENTS
        all_parents = [Cat.fetch_cat(i) for i in the_cat.get_parents()]
        if all_parents: 
            output += "\n"
            if len(all_parents) == 1:
                output += "parent: " + str(all_parents[0].name)
            elif len(all_parents) > 2:
                output += "parents: " + ", ".join([str(i.name) for i in all_parents[:2]]) + f", and {len(all_parents) - 2} "
                if len(all_parents) - 2 == 1:
                    output += "other"
                else:
                    output += "others"
            else:
                output += "parents: " + ", ".join([str(i.name) for i in all_parents])

        
        # MOONS
        output += "\n"
        if the_cat.dead:
            output += str(the_cat.moons)
            if the_cat.moons == 1:
                output += ' moon (in life)\n'
            elif the_cat.moons != 1:
                output += ' moons (in life)\n'

            output += str(the_cat.dead_for)
            if the_cat.dead_for == 1:
                output += ' moon (in death)'
            elif the_cat.dead_for != 1:
                output += ' moons (in death)'
        else:
            if the_cat.moons == -1:
                output += 'Unborn'
            else:
                output += str(the_cat.moons)
                if the_cat.moons == 1:
                    output += ' moon'
                elif the_cat.moons != 1:
                    output += ' moons'

        # MATE
        if len(the_cat.mate) > 0:
            output += "\n"
            
            
            mate_names = []
            # Grab the names of only the first two, since that's all we will display
            for _m in the_cat.mate[:2]:
                mate_ob = Cat.fetch_cat(_m)
                if not isinstance(mate_ob, Cat):
                    continue
                if mate_ob.dead != self.the_cat.dead:
                    if the_cat.dead:
                        former_indicate = "(living)"
                    else:
                        former_indicate = "(dead)"
                    
                    mate_names.append(f"{str(mate_ob.name)} {former_indicate}")
                elif mate_ob.outside != self.the_cat.outside:
                    mate_names.append(f"{str(mate_ob.name)} (away)")
                else:
                    mate_names.append(f"{str(mate_ob.name)}")
                    
            if len(the_cat.mate) == 1:
                output += "mate: " 
            else:
                output += "mates: "
            
            output += ", ".join(mate_names)
            
            if len(the_cat.mate) > 2:
                output += f", and {len(the_cat.mate) - 2}"
                if len(the_cat.mate) - 2 > 1:
                    output += " others"
                else:
                    output += " other"

        if not the_cat.dead:
            # NEWLINE ----------
            output += "\n"

        return output

    def generate_column2(self, the_cat):
        """Generate the right column information"""
        output = ""

        # STATUS
        if the_cat.outside and not the_cat.exiled and the_cat.status not in ['kittypet', 'loner', 'rogue',
                                                                             'former Clancat']:
            output += "<font color='#FF0000'>lost</font>"
        elif the_cat.exiled:
            output += "<font color='#FF0000'>exiled</font>"
        else:
            output += the_cat.status

        # NEWLINE ----------
        output += "\n"

        # LEADER LIVES:
        # Optional - Only shows up for leaders
        if not the_cat.dead and 'leader' in the_cat.status:
            output += 'remaining lives: ' + str(game.clan.leader_lives)
            # NEWLINE ----------
            output += "\n"

        # MENTOR
        # Only shows up if the cat has a mentor.
        if the_cat.mentor:
            mentor_ob = Cat.fetch_cat(the_cat.mentor)
            if mentor_ob:
                output += "mentor: " + str(mentor_ob.name) + "\n"

        # CURRENT APPRENTICES
        # Optional - only shows up if the cat has an apprentice currently
        if the_cat.apprentice:
            app_count = len(the_cat.apprentice)
            if app_count == 1 and Cat.fetch_cat(the_cat.apprentice[0]):
                output += 'apprentice: ' + str(Cat.fetch_cat(the_cat.apprentice[0]).name)
            elif app_count > 1:
                output += 'apprentice: ' + ", ".join([str(Cat.fetch_cat(i).name) for i in the_cat.apprentice if Cat.fetch_cat(i)])

            # NEWLINE ----------
            output += "\n"

        # FORMER APPRENTICES
        # Optional - Only shows up if the cat has previous apprentice(s)
        if the_cat.former_apprentices:
            
            apprentices = [Cat.fetch_cat(i) for i in the_cat.former_apprentices if isinstance(Cat.fetch_cat(i), Cat)]
            
            if len(apprentices) > 2:
                output += 'former apprentices: ' + ", ".join([str(i.name) for i in apprentices[:2]]) + \
                    ", and " + str(len(apprentices) - 2) 
                if len(apprentices) - 2 > 1:
                    output += " others"
                else:
                    output += " other"
            else:
                if len(apprentices) > 1:
                    output += 'former apprentices: '
                else:
                    output += 'former apprentice: '
                output += ", ".join(str(i.name) for i in apprentices)

            # NEWLINE ----------
            output += "\n"

        # CHARACTER TRAIT
        output += the_cat.personality.trait
        # NEWLINE ----------
        output += "\n"
        # CAT SKILLS

        if the_cat.moons < 6:
            output += "???"
        else:
            output += the_cat.skills.skill_string()
        # NEWLINE ----------
        output += "\n"

        # EXPERIENCE
        output += 'experience: ' + str(the_cat.experience_level)

        if game.settings['showxp']:
            output += ' (' + str(the_cat.experience) + ')'
        # NEWLINE ----------
        output += "\n"

        # BACKSTORY
        bs_text = 'this should not appear'
        if the_cat.status in ['kittypet', 'loner', 'rogue', 'former Clancat']:
            bs_text = the_cat.status
        else:
            if the_cat.backstory:
                #print(the_cat.backstory)
                for category in BACKSTORIES["backstory_categories"]:
                    if the_cat.backstory in BACKSTORIES["backstory_categories"][category]:
                        bs_text = BACKSTORIES["backstory_display"][category]
                        break
            else:
                bs_text = 'Clanborn'
        output += f"backstory: {bs_text}"
        # NEWLINE ----------
        output += "\n"

        # NUTRITION INFO (if the game is in the correct mode)
        if game.clan.game_mode in ["expanded", "cruel season"] and the_cat.is_alive() and FRESHKILL_ACTIVE:
            nutr = None
            if the_cat.ID in game.clan.freshkill_pile.nutrition_info:
                nutr = game.clan.freshkill_pile.nutrition_info[the_cat.ID]
            if nutr:
                output += f"nutrition status: {round(nutr.percentage, 1)}%\n"
            else:
                output += f"nutrition status: 100%\n"

        if the_cat.is_disabled():
            for condition in the_cat.permanent_condition:
                if the_cat.permanent_condition[condition]['born_with'] is True and \
                        the_cat.permanent_condition[condition]["moons_until"] != -2:
                    continue
                output += 'has a permanent condition'

                # NEWLINE ----------
                output += "\n"
                break

        if the_cat.is_injured():
            if "recovering from birth" in the_cat.injuries:
                output += 'recovering from birth!'
            elif "pregnant" in the_cat.injuries:
                output += 'pregnant!'
            else:
                output += "injured!"
        elif the_cat.is_ill():
            if "grief stricken" in the_cat.illnesses:
                output += 'grieving!'
            elif "fleas" in the_cat.illnesses:
                output += 'flea-ridden!'
            else:
                output += 'sick!'

        return output

    def toggle_history_tab(self, sub_tab_switch=False):
        """Opens the history tab
        param sub_tab_switch should be set to True if switching between sub tabs within the History tab
        """
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open at a time
        self.close_current_tab()

        if previous_open_tab == 'history' and sub_tab_switch is False:
            '''If the current open tab is history and we aren't switching between sub tabs,
             just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'history'
            self.backstory_background = pygame_gui.elements.UIImage(scale(pygame.Rect((178, 930), (1240, 314))),
                                                                    self.backstory_tab)
            self.backstory_background.disable()
            self.sub_tab_1 = UIImageButton(scale(pygame.Rect((1418, 950), (84, 60))), "", object_id="#sub_tab_1_button"
                                           , manager=MANAGER)
            self.sub_tab_1.disable()
            self.sub_tab_2 = UIImageButton(scale(pygame.Rect((1418, 1024), (84, 60))), "", object_id="#sub_tab_2_button"
                                           , manager=MANAGER)
            self.sub_tab_2.disable()
            self.sub_tab_3 = UIImageButton(scale(pygame.Rect((1418, 1098), (84, 60))), "", object_id="#sub_tab_3_button"
                                           , manager=MANAGER)
            self.sub_tab_3.disable()
            self.sub_tab_4 = UIImageButton(scale(pygame.Rect((1418, 1172), (84, 60))), "", object_id="#sub_tab_4_button"
                                           , manager=MANAGER)
            self.sub_tab_4.disable()
            self.fav_tab = UIImageButton(
                scale(pygame.Rect((105, 960), (56, 56))),
                "",
                object_id="#fav_star",
                tool_tip_text='un-favorite this sub tab',
                manager=MANAGER
            )
            self.not_fav_tab = UIImageButton(
                scale(pygame.Rect((105, 960), (56, 56))),
                "",
                object_id="#not_fav_star",
                tool_tip_text='favorite this sub tab - it will be the default sub tab displayed when History is viewed',
                manager=MANAGER
            )

            if self.open_sub_tab != 'life events':
                self.toggle_history_sub_tab()
            else:
                # This will be overwritten in update_disabled_buttons_and_text()
                self.history_text_box = pygame_gui.elements.UITextBox("", scale(pygame.Rect((80, 480), (615, 142)))
                                                                      , manager=MANAGER)
                self.no_moons = UIImageButton(scale(pygame.Rect(
                    (104, 1028), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    tool_tip_text='Show the Moon that certain history events occurred on', manager=MANAGER
                )
                self.show_moons = UIImageButton(scale(pygame.Rect(
                    (104, 1028), (68, 68))),
                    "",
                    object_id="#checked_checkbox",
                    tool_tip_text='Stop showing the Moon that certain history events occurred on', manager=MANAGER
                )

                self.update_disabled_buttons_and_text()

    def toggle_user_notes_tab(self):
        """Opens the User Notes portion of the History Tab"""
        self.load_user_notes()
        if self.user_notes is None:
            self.user_notes = 'Click the check mark to enter notes about your cat!'

        self.notes_entry = pygame_gui.elements.UITextEntryBox(
            scale(pygame.Rect((200, 946), (1200, 298))),
            initial_text=self.user_notes,
            object_id='#text_box_26_horizleft_pad_10_14',
            manager=MANAGER
        )

        self.display_notes = UITextBoxTweaked(self.user_notes,
                                              scale(pygame.Rect((200, 946), (120, 298))),
                                              object_id="#text_box_26_horizleft_pad_10_14",
                                              line_spacing=1, manager=MANAGER)

        self.update_disabled_buttons_and_text()

    def save_user_notes(self):
        """Saves user-entered notes. """
        clanname = game.clan.name

        notes = self.user_notes

        notes_directory = get_save_dir() + '/' + clanname + '/notes'
        notes_file_path = notes_directory + '/' + self.the_cat.ID + '_notes.json'

        if not os.path.exists(notes_directory):
            os.makedirs(notes_directory)

        if notes is None or notes == 'Click the check mark to enter notes about your cat!':
            return

        new_notes = {str(self.the_cat.ID): notes}

        game.safe_save(notes_file_path, new_notes)

    def load_user_notes(self):
        """Loads user-entered notes. """
        clanname = game.clan.name

        notes_directory = get_save_dir() + '/' + clanname + '/notes'
        notes_file_path = notes_directory + '/' + self.the_cat.ID + '_notes.json'

        if not os.path.exists(notes_file_path):
            return

        try:
            with open(notes_file_path, 'r') as read_file:
                rel_data = ujson.loads(read_file.read())
                self.user_notes = 'Click the check mark to enter notes about your cat!'
                if str(self.the_cat.ID) in rel_data:
                    self.user_notes = rel_data.get(str(self.the_cat.ID))
        except Exception as e:
            print(f"ERROR: there was an error reading the Notes file of cat #{self.the_cat.ID}.\n", e)

    def toggle_history_sub_tab(self):
        """To toggle the history-sub-tab"""

        if self.open_sub_tab == 'life events':
            self.toggle_history_tab(sub_tab_switch=True)

        elif self.open_sub_tab == 'user notes':
            self.toggle_user_notes_tab()

    def get_all_history_text(self):
        """Generates a string with all important history information."""
        output = ""
        if self.open_sub_tab == 'life events':
            # start our history with the backstory, since all cats get one
            if self.the_cat.status not in ["rogue", "kittypet", "loner", "former Clancat"]:
                life_history = [str(self.get_backstory_text())]
            else:
                life_history = []

            # now get apprenticeship history and add that if any exists
            app_history = self.get_apprenticeship_text()
            if app_history:
                life_history.append(app_history)
                
            #Get mentorship text if it exists
            mentor_history = self.get_mentorship_text()
            if mentor_history:
                life_history.append(mentor_history)

            # now go get the scar history and add that if any exists
            body_history = []
            scar_history = self.get_scar_text()
            if scar_history:
                body_history.append(scar_history)
            death_history = self.get_death_text()
            if death_history:
                body_history.append(death_history)
            # join scar and death into one paragraph
            if body_history:
                life_history.append(" ".join(body_history))

            murder = self.get_murder_text()
            if murder:
                life_history.append(murder)

            # join together history list with line breaks
            output = '\n\n'.join(life_history)
        return output

    def get_backstory_text(self):
        """
        returns the backstory blurb
        """
        cat_dict = {
            "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
        }
        bs_blurb = None
        if self.the_cat.backstory:
            bs_blurb = BACKSTORIES["backstories"][self.the_cat.backstory]
        if self.the_cat.status in ['kittypet', 'loner', 'rogue', 'former Clancat']:
            bs_blurb = f"This cat is a {self.the_cat.status} and currently resides outside of the Clans."

        if bs_blurb is not None:
            adjust_text = str(bs_blurb).replace('This cat', str(self.the_cat.name))
            text = adjust_text
        else:
            text = str(self.the_cat.name) + " was born into the Clan where {PRONOUN/m_c/subject} currently reside."

        beginning = History.get_beginning(self.the_cat)
        if beginning:
            if beginning['clan_born']:
                text += " {PRONOUN/m_c/subject/CAP} {VERB/m_c/were/was} born on Moon " + str(
                    beginning['moon']) + " during " + str(beginning['birth_season']) + "."
            else:
                text += " {PRONOUN/m_c/subject/CAP} joined the Clan on Moon " + str(
                    beginning['moon']) + " at the age of " + str(beginning['age']) + " Moons."

        text = process_text(text, cat_dict)
        return text

    def get_scar_text(self):
        """
        returns the adjusted scar text
        """
        scar_text = []
        scar_history = History.get_death_or_scars(self.the_cat, scar=True)
        if game.switches['show_history_moons']:
            moons = True
        else:
            moons = False

        if scar_history:
            i = 0
            for scar in scar_history:
                # base adjustment to get the cat's name and moons if needed
                new_text = (event_text_adjust(Cat,
                                              scar["text"],
                                              self.the_cat,
                                              Cat.fetch_cat(scar["involved"])))
                if moons:
                    new_text += f" (Moon {scar['moon']})"

                # checking to see if we can throw out a duplicate
                if new_text in scar_text:
                    i += 1
                    continue

                # the first event keeps the cat's name, consecutive events get to switch it up a bit
                if i != 0:
                    sentence_beginners = [
                        "This cat",
                        "Then {PRONOUN/m_c/subject} {VERB/m_c/were/was}",
                        "{PRONOUN/m_c/subject/CAP} {VERB/m_c/were/was} also",
                        "Also, {PRONOUN/m_c/subject} {VERB/m_c/were/was}",
                        "As well as",
                        "{PRONOUN/m_c/subject/CAP} {VERB/m_c/were/was} then"
                    ]
                    chosen = choice(sentence_beginners)
                    if chosen == 'This cat':
                        new_text = new_text.replace(str(self.the_cat.name), chosen, 1)
                    else:
                        new_text = new_text.replace(f"{self.the_cat.name} was", f"{chosen}", 1)
                cat_dict = {
                    "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
                }
                new_text = process_text(new_text, cat_dict)
                scar_text.append(new_text)
                i += 1

            scar_history = ' '.join(scar_text)

        return scar_history

    def get_apprenticeship_text(self):
        """
        returns adjusted apprenticeship history text (mentor influence and app ceremony)
        """
        if self.the_cat.status in ['kittypet', 'loner', 'rogue', 'former Clancat']:
            return ""

        mentor_influence = History.get_mentor_influence(self.the_cat)
        influence_history = ""
        
        #First, just list the mentors:
        if self.the_cat.status in ['kitten', 'newborn']:
                influence_history = 'This cat has not begun training.'
        elif self.the_cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"]:
            influence_history = 'This cat has not finished training.'
        else:
            valid_formor_mentors = [Cat.fetch_cat(i) for i in self.the_cat.former_mentor if 
                                    isinstance(Cat.fetch_cat(i), Cat)]
            if valid_formor_mentors:
                influence_history += "{PRONOUN/m_c/subject/CAP} {VERB/m_c/were/was} mentored by "
                if len(valid_formor_mentors) > 1:
                    influence_history += ", ".join([str(i.name) for i in valid_formor_mentors[:-1]]) + " and " + \
                        str(valid_formor_mentors[-1].name) + ". "
                else:
                    influence_history += str(valid_formor_mentors[0].name) + ". "
            else:
                influence_history += "This cat either did not have a mentor, or {PRONOUN/m_c/poss} mentor is unknown. "
            
            # Second, do the facet/personality effect
            trait_influence = []
            if "trait" in mentor_influence and mentor_influence["trait"] != None:
                if ("Benevolent" or "Abrasive" or "Reserved" or "Outgoing") in mentor_influence["trait"]:
                    mentor_influence["trait"] = {}
                    return
                for _mentor in mentor_influence["trait"]:
                    #If the strings are not set (empty list), continue. 
                    if not mentor_influence["trait"][_mentor].get("strings"):
                        continue
                    
                    ment_obj = Cat.fetch_cat(_mentor)
                    #Continue of the mentor is invalid too.
                    if not isinstance(ment_obj, Cat):
                        continue
                    
                    if len(mentor_influence["trait"][_mentor].get("strings")) > 1:
                        string_snippet = ", ".join(mentor_influence["trait"][_mentor].get("strings")[:-1]) + \
                            " and " + mentor_influence["trait"][_mentor].get("strings")[-1]
                    else:
                        string_snippet = mentor_influence["trait"][_mentor].get("strings")[0]
                        
                    
                    trait_influence.append(str(ment_obj.name) +  \
                                        " influenced {PRONOUN/m_c/object} to be more likely to " + string_snippet + ". ")
                    
                    

            influence_history += " ".join(trait_influence)
            
            
            skill_influence = []
            if "skill" in mentor_influence and mentor_influence["skill"] != None:
                for _mentor in mentor_influence["skill"]:
                    #If the strings are not set (empty list), continue. 
                    if not mentor_influence["skill"][_mentor].get("strings"):
                        continue
                    
                    ment_obj = Cat.fetch_cat(_mentor)
                    #Continue of the mentor is invalid too.
                    if not isinstance(ment_obj, Cat):
                        continue
                    
                    if len(mentor_influence["skill"][_mentor].get("strings")) > 1:
                        string_snippet = ", ".join(mentor_influence["skill"][_mentor].get("strings")[:-1]) + \
                            " and " + mentor_influence["skill"][_mentor].get("strings")[-1]
                    else:
                        string_snippet = mentor_influence["skill"][_mentor].get("strings")[0]
                        
                    
                    skill_influence.append(str(ment_obj.name) +  \
                                        " helped {PRONOUN/m_c/object} become better at " + string_snippet + ". ")
                    
                    

            influence_history += " ".join(skill_influence)

        app_ceremony = History.get_app_ceremony(self.the_cat)

        graduation_history = ""
        if app_ceremony:
            graduation_history = "When {PRONOUN/m_c/subject} graduated, {PRONOUN/m_c/subject} {VERB/m_c/were/was} honored for {PRONOUN/m_c/poss} " +  app_ceremony['honor'] + "."

            grad_age = app_ceremony["graduation_age"]
            if int(grad_age) < 11:
                graduation_history += " {PRONOUN/m_c/poss/CAP} training went so well that {PRONOUN/m_c/subject} graduated early at " + str(
                    grad_age) + " moons old."
            elif int(grad_age) > 13:
                graduation_history += " {PRONOUN/m_c/subject/CAP} graduated late at " + str(grad_age) + " moons old."
            else:
                graduation_history += " {PRONOUN/m_c/subject/CAP} graduated at " + str(grad_age) + " moons old."

            if game.switches['show_history_moons']:
                graduation_history += f" (Moon {app_ceremony['moon']})"
        cat_dict = {
            "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
        }
        apprenticeship_history = influence_history + " " + graduation_history
        apprenticeship_history = process_text(apprenticeship_history, cat_dict)
        return apprenticeship_history


    def get_mentorship_text(self):
        """
        
        returns full list of previously mentored apprentices. 
        
        """
        
        text = ""
        # Doing this is two steps 
        all_real_apprentices = [Cat.fetch_cat(i) for i in self.the_cat.former_apprentices if isinstance(Cat.fetch_cat(i), Cat)]
        if all_real_apprentices:
            text = "{PRONOUN/m_c/subject/CAP} mentored "
            if len(all_real_apprentices) > 2:
                text += ', '.join([str(i.name) for i in all_real_apprentices[:-1]]) + ", and " + str(all_real_apprentices[-1].name) + "."
            elif len(all_real_apprentices) == 2:
                text += str(all_real_apprentices[0].name) + " and " + str(all_real_apprentices[1].name) + "."
            elif len(all_real_apprentices) == 1:
                text += str(all_real_apprentices[0].name) + "."
            
            cat_dict = {
            "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
            }   
            
            text = process_text(text, cat_dict)
        
        return text
        

    # def get_text_for_murder_event(self, event, death):
    #     ''' returns the adjusted murder history text for the victim '''
        
    #     if event["text"] == death["text"] and event["moon"] == death["moon"]:
    #         if event["revealed"] is True: 
    #             final_text = event_text_adjust(Cat, event["text"], self.the_cat, Cat.fetch_cat(death["involved"]))
    #             if event.get("revelation_text"):
    #                 final_text = final_text + event["revelation_text"]
    #             return final_text
    #         else:
    #             return event_text_adjust(Cat, event["unrevealed_text"], self.the_cat, Cat.fetch_cat(death["involved"]))
    #     return None


    def get_death_text(self):
        """
        returns adjusted death history text
        """
        text = None
        death_history = self.the_cat.history.get_death_or_scars(self.the_cat, death=True)
        murder_history = self.the_cat.history.get_murders(self.the_cat)
        if game.switches['show_history_moons']:
            moons = True
        else:
            moons = False

        if death_history:
            all_deaths = []
            death_number = len(death_history)
            for index, death in enumerate(death_history):
                found_murder = False  # Add this line to track if a matching murder event is found
                if "is_victim" in murder_history:
                    for event in murder_history["is_victim"]:
                        text = None
                        # text = self.get_text_for_murder_event(event, death)
                        if text is not None:
                            found_murder = True  # Update the flag if a matching murder event is found
                            break

                if found_murder and text is not None and not event["revealed"]:
                    # text = "This cat was murdered."
                    text = event_text_adjust(Cat, event["unrevealed_text"], self.the_cat, Cat.fetch_cat(death["involved"]))
                elif not found_murder:
                    # text = "This cat was murdered."

                    text = event_text_adjust(Cat, death["text"], self.the_cat, Cat.fetch_cat(death["involved"]))

                if self.the_cat.status == 'leader':
                    if index == death_number - 1 and self.the_cat.dead:
                        if death_number == 9:
                            life_text = "lost {PRONOUN/m_c/poss} final life"
                        elif death_number == 1:
                            life_text = "lost all of {PRONOUN/m_c/poss} lives"
                        else:
                            life_text = "lost the rest of {PRONOUN/m_c/poss} lives"
                    else:
                        life_text = "lost a life"
                elif death_number > 1:
                    #for retired leaders
                    if index == death_number - 1 and self.the_cat.dead:
                        life_text = "lost {PRONOUN/m_c/poss} last remaining life"
                        # added code
                        if "This cat was" in text:
                            text = text.replace("This cat was", "{VERB/m_c/were/was}")
                        else:
                            text = text[0].lower() + text[1:]
                    else:
                        life_text = "lost a life"
                else:
                    life_text = ""

                if text:
                    if life_text:
                        text = f"{life_text} when {{PRONOUN/m_c/subject}} {text}"
                    else:
                        text = f"{text}"

                    if moons:
                        text += f" (Moon {death['moon']})"
                    all_deaths.append(text)

            if self.the_cat.status == 'leader' or death_number > 1:
                if death_number > 2:
                    filtered_deaths = [death for death in all_deaths if death is not None]
                    deaths = f"{', '.join(filtered_deaths[0:-1])}, and {filtered_deaths[-1]}"
                elif death_number == 2:
                    deaths = " and ".join(all_deaths)
                else:
                    deaths = all_deaths[0]

                if not deaths.endswith('.'):
                    deaths += "."

                text = str(self.the_cat.name) + " " + deaths

            else:
                text = all_deaths[0]

            cat_dict = {
                "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
            }
            text = process_text(text, cat_dict)

        return text

    def get_murder_text(self):
        """
        returns adjusted murder history text FOR THE MURDERER

        """
        murder_history = History.get_murders(self.the_cat)
        victim_text = ""

        if game.switches['show_history_moons']:
            moons = True
        else:
            moons = False
        victims = []
        if murder_history:
            if 'is_murderer' in murder_history:
                victims = murder_history["is_murderer"]                

        if len(victims) > 0:
            victim_names = {}
            name_list = []
            reveal_text = None

            for victim in victims:
                if not Cat.fetch_cat(victim["victim"]):
                    continue 
                name = str(Cat.fetch_cat(victim["victim"]).name)

                if victim["revealed"]:
                    victim_names[name] = []
                    if victim.get("revelation_text"):
                        reveal_text = str(victim["revelation_text"])
                    if moons:
                        victim_names[name].append(victim["moon"])

            if victim_names:
                for name in victim_names:
                    if not moons:
                        name_list.append(name)
                    else:
                        name_list.append(name + f" (Moon {', '.join(victim_names[name])})")

                if len(name_list) == 1:
                    victim_text = f"{self.the_cat.name} murdered {name_list[0]}."
                elif len(victim_names) == 2:
                    victim_text = f"{self.the_cat.name} murdered {' and '.join(name_list)}."
                else:
                    victim_text = f"{self.the_cat.name} murdered {', '.join(name_list[:-1])}, and {name_list[-1]}."

            if reveal_text:
                cat_dict = {
                        "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
                    }
                victim_text = f'{victim_text} {process_text(reveal_text, cat_dict)}'

        return victim_text

    def toggle_conditions_tab(self):
        """Opens the conditions tab"""
        previous_open_tab = self.open_tab
        # This closes the current tab, so only one can be open at a time
        self.close_current_tab()

        if previous_open_tab == 'conditions':
            '''If the current open tab is conditions, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'conditions'
            self.conditions_page = 0
            self.right_conditions_arrow = UIImageButton(
                scale(pygame.Rect((1418, 1080), (68, 68))),
                "",
                object_id='#arrow_right_button', manager=MANAGER
            )
            self.left_conditions_arrow = UIImageButton(
                scale(pygame.Rect((118, 1080), (68, 68))),
                "",
                object_id='#arrow_left_button'
            )
            self.conditions_background = pygame_gui.elements.UIImage(
                scale(pygame.Rect((178, 942), (1248, 302))),
                self.conditions_tab
            )

            # This will be overwritten in update_disabled_buttons_and_text()
            self.update_disabled_buttons_and_text()

    def display_conditions_page(self):
        # tracks the position of the detail boxes
        if self.condition_container: 
            self.condition_container.kill()
            
        self.condition_container = pygame_gui.core.UIContainer(
            scale(pygame.Rect((178, 942), (1248, 302))),
            MANAGER)
        
        # gather a list of all the conditions and info needed.
        all_illness_injuries = [(i, self.get_condition_details(i)) for i in self.the_cat.permanent_condition if
                                not (self.the_cat.permanent_condition[i]['born_with'] and self.the_cat.permanent_condition[i]["moons_until"] != -2)]
        all_illness_injuries.extend([(i, self.get_condition_details(i)) for i in self.the_cat.injuries])
        all_illness_injuries.extend([(i, self.get_condition_details(i)) for i in self.the_cat.illnesses if
                                    i not in ("an infected wound", "a festering wound")])
        all_illness_injuries = chunks(all_illness_injuries, 4)
        
        if not all_illness_injuries:
            self.conditions_page = 0
            self.right_conditions_arrow.disable()
            self.left_conditions_arrow.disable()
            return
        
        # Adjust the page number if it somehow goes out of range. 
        if self.conditions_page < 0:
            self.conditions_page = 0
        elif self.conditions_page > len(all_illness_injuries) - 1:
            self.conditions_page = len(all_illness_injuries) - 1
            
        # Disable the arrow buttons
        if self.conditions_page == 0:
            self.left_conditions_arrow.disable()
        else:
            self.left_conditions_arrow.enable()
        
        if self.conditions_page >= len(all_illness_injuries) - 1:
            self.right_conditions_arrow.disable()
        else:
            self.right_conditions_arrow.enable()

        x_pos = 30
        for con in all_illness_injuries[self.conditions_page]:
            
            # Background Box
            pygame_gui.elements.UIImage(
                    scale(pygame.Rect((x_pos, 25), (280, 276))),
                    self.condition_details_box, manager=MANAGER,
                    container=self.condition_container)
            
            y_adjust = 60
            
            name = UITextBoxTweaked(
                    con[0],
                    scale(pygame.Rect((x_pos, 26), (272, -1))),
                    line_spacing=.90,
                    object_id="#text_box_30_horizcenter",
                    container=self.condition_container, manager=MANAGER)
            
            y_adjust = name.get_relative_rect().height
            details_rect = scale(pygame.Rect((x_pos, 0), (276, -1)))
            details_rect.y = y_adjust
            
            UITextBoxTweaked(
                    con[1],
                    details_rect,
                    line_spacing=.90,
                    object_id="#text_box_22_horizcenter_pad_20_20",
                    container=self.condition_container, manager=MANAGER)
            
            
            x_pos += 304
        
        return
        
    def get_condition_details(self, name):
        """returns the relevant condition details as one string with line breaks"""
        text_list = []
        cat_name = self.the_cat.name

        # collect details for perm conditions
        if name in self.the_cat.permanent_condition:
            # display if the cat was born with it
            if self.the_cat.permanent_condition[name]["born_with"] is True:
                text_list.append(f"born with this condition")
            else:
                # moons with the condition if not born with condition
                moons_with = game.clan.age - self.the_cat.permanent_condition[name]["moon_start"]
                if moons_with != 1:
                    text_list.append(f"has had this condition for {moons_with} moons")
                else:
                    text_list.append(f"has had this condition for 1 moon")

            # is permanent
            text_list.append('permanent condition')

            # infected or festering
            complication = self.the_cat.permanent_condition[name].get("complication", None)
            if complication is not None:
                if 'a festering wound' in self.the_cat.illnesses:
                    complication = 'festering'
                text_list.append(f'is {complication}!')

        # collect details for injuries
        if name in self.the_cat.injuries:
            # moons with condition
            keys = self.the_cat.injuries[name].keys()
            moons_with = game.clan.age - self.the_cat.injuries[name]["moon_start"]
            insert = 'has been hurt for'
            
            if name == 'recovering from birth':
                insert = 'has been recovering for'
            elif name == 'pregnant':
                insert = 'has been pregnant for'
            
            if moons_with != 1:
                text_list.append(f"{insert} {moons_with} moons")
            else:
                text_list.append(f"{insert} 1 moon")
            
            # infected or festering
            if 'complication' in keys:
                complication = self.the_cat.injuries[name]["complication"]
                if complication is not None:
                    if 'a festering wound' in self.the_cat.illnesses:
                        complication = 'festering'
                    text_list.append(f'is {complication}!')
            
            # can or can't patrol
            if self.the_cat.injuries[name]["severity"] != 'minor':
                text_list.append("Can't work with this condition")

        # collect details for illnesses
        if name in self.the_cat.illnesses:
            # moons with condition
            moons_with = game.clan.age - self.the_cat.illnesses[name]["moon_start"]
            insert = "has been sick for"
            
            if name == 'grief stricken':
                insert = 'has been grieving for'
            
            if moons_with != 1:
                text_list.append(f"{insert} {moons_with} moons")
            else:
                text_list.append(f"{insert} 1 moon")
            
            if self.the_cat.illnesses[name]['infectiousness'] != 0:
                text_list.append("infectious!")
            
            # can or can't patrol
            if self.the_cat.illnesses[name]["severity"] != 'minor':
                text_list.append("Can't work with this condition")

        text = "<br><br>".join(text_list)
        return text

    def toggle_relations_tab(self):
        """Opens relations tab"""
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'relations':
            '''If the current open tab is relations, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'relations'
            self.family_tree_button = UIImageButton(scale(pygame.Rect((100, 900), (344, 72))), "",
                                                   starting_height=2, object_id="#family_tree_button", manager=MANAGER)
            self.change_adoptive_parent_button = UIImageButton(scale(pygame.Rect((100, 972), (344, 72))), "",
                                                      starting_height=2, object_id="#adoptive_parents", manager=MANAGER)
            self.see_relationships_button = UIImageButton(scale(pygame.Rect((100, 1044), (344, 72))), "",
                                                          starting_height=2, object_id="#see_relationships_button", manager=MANAGER)
            self.choose_mate_button = UIImageButton(scale(pygame.Rect((100, 1116), (344, 72))), "",
                                                    starting_height=2, object_id="#choose_mate_button", manager=MANAGER)
            self.update_disabled_buttons_and_text()
    
    def toggle_your_tab(self):
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'your tab':
            '''If the current open tab is relations, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'your tab'
            self.have_kits_button = None
            self.request_apprentice_button = None
            self.change_accessory_button = None
            self.update_disabled_buttons_and_text()

    def toggle_roles_tab(self):
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'roles':
            '''If the current open tab is roles, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'roles'

            self.manage_roles = UIImageButton(scale(pygame.Rect((452, 900), (344, 72))),
                                              "", object_id="#manage_roles_button",
                                              starting_height=2
                                              , manager=MANAGER)
            self.change_mentor_button = UIImageButton(scale(pygame.Rect((452, 972), (344, 72))), "",
                                                      starting_height=2, object_id="#change_mentor_button", manager=MANAGER)
            self.update_disabled_buttons_and_text()

    def toggle_personal_tab(self):
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'personal':
            '''If the current open tab is personal, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'personal'
            self.change_name_button = UIImageButton(scale(pygame.Rect((804, 900), (344, 72))), "",
                                                    starting_height=2,
                                                    object_id="#change_name_button", manager=MANAGER)
            self.specify_gender_button = UIImageButton(scale(pygame.Rect((804, 1076), (344, 72))), "",
                                                       starting_height=2,
                                                       object_id="#specify_gender_button", manager=MANAGER)

            # These are a placeholders, to be killed and recreated in self.update_disabled_buttons().
            #   This it due to the image switch depending on the cat's status, and the location switch the close button
            #    If you can think of a better way to do this, please fix! 
            self.cis_trans_button = None
            self.toggle_kits = None
            self.update_disabled_buttons_and_text()

    def toggle_dangerous_tab(self):
        # Save what is previously open, for toggle purposes.
        previous_open_tab = self.open_tab

        # This closes the current tab, so only one can be open as a time
        self.close_current_tab()

        if previous_open_tab == 'dangerous':
            '''If the current open tab is dangerous, just close the tab and do nothing else. '''
            pass
        else:
            self.open_tab = 'dangerous'
            self.kill_cat_button = UIImageButton(
                scale(pygame.Rect((1156, 972), (344, 72))),
                "",
                object_id="#kill_cat_button",
                tool_tip_text='This will open a confirmation window and allow you to input a death reason',
                starting_height=2, manager=MANAGER
            )
            self.murder_cat_button = UIImageButton(
                scale(pygame.Rect((1156, 1045), (344, 72))),
                "",
                object_id="#murder_button",
                tool_tip_text='Choose to murder one of your clanmates',
                starting_height=2, manager=MANAGER
            )
            if game.clan.murdered:
                self.murder_cat_button.disable()
            
            
            if game.clan.your_cat.joined_df:
                self.exit_df_button = UIImageButton(
                scale(pygame.Rect((1156, 1118), (344, 72))),
                "",
                object_id="#exit_df_button",
                tool_tip_text='Leave the Dark Forest',
                starting_height=2, manager=MANAGER
                )
            else:
                self.join_df_button = UIImageButton(
                scale(pygame.Rect((1156, 1118), (344, 72))),
                "",
                object_id="#join_df_button",
                tool_tip_text='Join the Dark Forest',
                starting_height=2, manager=MANAGER
            )

            # These are a placeholders, to be killed and recreated in self.update_disabled_buttons_and_text().
            #   This it due to the image switch depending on the cat's status, and the location switch the close button
            #    If you can think of a better way to do this, please fix! 
            self.exile_cat_button = None
            self.update_disabled_buttons_and_text()

    def update_disabled_buttons_and_text(self):
        """Sets which tab buttons should be disabled. This is run when the cat is switched. """
        if self.open_tab is None:
            pass
        elif self.open_tab == 'relations':
            if self.the_cat.dead:
                self.see_relationships_button.disable()
                self.change_adoptive_parent_button.disable()
            else:
                self.see_relationships_button.enable()
                self.change_adoptive_parent_button.enable()

            if self.the_cat.age not in ['young adult', 'adult', 'senior adult', 'senior'
                                        ] or self.the_cat.exiled or self.the_cat.outside:
                self.choose_mate_button.disable()
            else:
                self.choose_mate_button.enable()

        # Roles Tab
        elif self.open_tab == 'roles':
            if self.the_cat.dead or self.the_cat.outside:
                self.manage_roles.disable()
            else:
                self.manage_roles.enable()
            if self.the_cat.status not in ['apprentice', 'medicine cat apprentice', 'mediator apprentice', "queen's apprentice"] \
                                            or self.the_cat.dead or self.the_cat.outside:
                self.change_mentor_button.disable()
            else:
                self.change_mentor_button.enable()

        elif self.open_tab == "personal":

            # Button to trans or cis the cats.
            if self.cis_trans_button:
                self.cis_trans_button.kill()
            if self.the_cat.gender == "male" and self.the_cat.genderalign == "male":
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_trans_female_button",
                                                      manager=MANAGER)
            elif self.the_cat.gender == "female" and self.the_cat.genderalign == "female":
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_trans_male_button",
                                                      manager=MANAGER)
            elif self.the_cat.genderalign in ['trans female', 'trans male']:
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_nonbi_button",
                                                      manager=MANAGER)
            elif self.the_cat.genderalign not in ['female', 'trans female', 'male', 'trans male']:
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_cis_button",
                                                      manager=MANAGER)
            elif self.the_cat.gender == "male" and self.the_cat.genderalign == "female":
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_cis_button",
                                                      manager=MANAGER)
            elif self.the_cat.gender == "female" and self.the_cat.genderalign == "male":
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_cis_button",
                                                      manager=MANAGER)
            elif self.the_cat.genderalign:
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_cis_button",
                                                      manager=MANAGER)
            else:
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_cis_button",
                                                      manager=MANAGER)
                self.cis_trans_button.disable()

            # Button to prevent kits:
            if self.toggle_kits:
                self.toggle_kits.kill()
            if self.the_cat.age in ['young adult', 'adult', 'senior adult', 'senior'] and not self.the_cat.dead:
                if self.the_cat.no_kits:
                    self.toggle_kits = UIImageButton(scale(pygame.Rect((804, 1148), (344, 72))), "",
                                                     starting_height=2, object_id="#allow_kits_button",
                                                     manager=MANAGER)
                else:
                    self.toggle_kits = UIImageButton(scale(pygame.Rect((804, 1148), (344, 72))), "",
                                                     starting_height=2, object_id="#prevent_kits_button",
                                                     manager=MANAGER)
            else:
                self.toggle_kits = UIImageButton(scale(pygame.Rect((804, 1148), (344, 72))), "",
                                                 starting_height=2, object_id="#prevent_kits_button",
                                                 manager=MANAGER)
                self.toggle_kits.disable()
        elif self.open_tab == 'your tab':
            if self.the_cat.age in ['young adult', 'adult', 'senior adult', 'senior'] and not self.the_cat.dead and not self.the_cat.outside and game.switches['have kits']:
                self.have_kits_button = UIImageButton(scale(pygame.Rect((804, 1172), (344, 72))), "",
                                                    starting_height=2, object_id="#have_kits_button", tool_tip_text='You will be more likely to have kits the next moon.',
                                                    manager=MANAGER)
            else:
                self.have_kits_button = UIImageButton(scale(pygame.Rect((804, 1172), (344, 72))), "",
                                                 starting_height=2, object_id="#have_kits_button",
                                                 manager=MANAGER)
                self.have_kits_button.disable()
                
            self.change_accessory_button = UIImageButton(scale(pygame.Rect((804, 1100), (344, 72))), "",
                                                 starting_height=2, object_id="#change_accessory_button",
                                                 manager=MANAGER)
            if self.the_cat.status in ['leader', 'deputy', 'medicine cat', 'mediator', 'queen', 'warrior']:
                self.request_apprentice_button = UIImageButton(scale(pygame.Rect((804, 1028), (344, 72))), "",
                                                               tool_tip_text='You will be more likely to recieve an apprentice.',
                                                    starting_height=2, object_id="#request_apprentice_button",
                                                    manager=MANAGER)
            else:
                self.request_apprentice_button = UIImageButton(scale(pygame.Rect((804, 1028), (344, 72))), "",
                                                    starting_height=2, 
                                                    tool_tip_text='You will be more likely to recieve an apprentice.', object_id="#request_apprentice_button",
                                                    manager=MANAGER)
                self.request_apprentice_button.disable()
            if 'request apprentice' in game.switches:
                if game.switches['request apprentice']:
                    self.request_apprentice_button.disable()
            
        # Dangerous Tab
        elif self.open_tab == 'dangerous':

            # Button to exile cat
            if self.exile_cat_button:
                self.exile_cat_button.kill()
            if not self.the_cat.dead:
                self.exile_cat_button = UIImageButton(
                    scale(pygame.Rect((1156, 900), (344, 72))),
                    "",
                    object_id="#exile_cat_button",
                    tool_tip_text='This cannot be reversed.',
                    starting_height=2, manager=MANAGER)
                if self.the_cat.exiled or self.the_cat.outside:
                    self.exile_cat_button.disable()
            elif self.the_cat.dead:
                object_id = "#exile_df_button"
                if self.the_cat.df:
                    object_id = "#guide_sc_button"
                if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
                    self.exile_cat_button = UIImageButton(scale(pygame.Rect((1156, 900), (344, 92))),
                                                          "",
                                                          object_id=object_id,
                                                          tool_tip_text='Changing where this cat resides will change '
                                                                        'where your Clan goes after death. ',
                                                          starting_height=2, manager=MANAGER)
                else:
                    self.exile_cat_button = UIImageButton(scale(pygame.Rect((1156, 900), (344, 92))),
                                                          "",
                                                          object_id=object_id,
                                                          starting_height=2, manager=MANAGER)
            else:
                self.exile_cat_button = UIImageButton(
                    scale(pygame.Rect((1156, 900), (344, 72))),
                    "",
                    object_id="#exile_cat_button",
                    tool_tip_text='This cannot be reversed.',
                    starting_height=2, manager=MANAGER)
                self.exile_cat_button.disable()

            if not self.the_cat.dead:
                self.kill_cat_button.enable()
            else:
                self.kill_cat_button.disable()
                
            if self.the_cat.ID != game.clan.your_cat.ID:
                self.murder_cat_button.hide()
                if self.join_df_button:
                    self.join_df_button.hide()
                if self.exit_df_button:
                    self.exit_df_button.hide()
            else:
                self.murder_cat_button.show()
                if self.join_df_button:
                    self.join_df_button.show()
                if self.exit_df_button:
                    self.exit_df_button.show()
                if game.clan.your_cat.dead or game.clan.your_cat.outside:
                    self.murder_cat_button.disable()
                    if self.join_df_button:
                        self.join_df_button.disable()
                    if self.exit_df_button:
                        self.exit_df_button.disable()

            if game.clan.your_cat.status == 'kitten':
                if self.join_df_button:
                    self.join_df_button.hide()
                elif self.exit_df_button:
                    self.exit_df_button.hide()
        # History Tab:
        elif self.open_tab == 'history':
            # show/hide fav tab star
            if self.open_sub_tab == game.switches['favorite_sub_tab']:
                self.fav_tab.show()
                self.not_fav_tab.hide()
            else:
                self.fav_tab.hide()
                self.not_fav_tab.show()

            if self.open_sub_tab == 'life events':
                self.sub_tab_1.disable()
                self.sub_tab_2.enable()
                self.history_text_box.kill()
                self.history_text_box = UITextBoxTweaked(self.get_all_history_text(),
                                                         scale(pygame.Rect((200, 946), (1200, 298))),
                                                         object_id="#text_box_26_horizleft_pad_10_14",
                                                         line_spacing=1, manager=MANAGER)

                self.no_moons.kill()
                self.show_moons.kill()
                self.no_moons = UIImageButton(scale(pygame.Rect(
                    (104, 1028), (68, 68))),
                    "",
                    object_id="#unchecked_checkbox",
                    tool_tip_text='Show the Moon that certain history events occurred on', manager=MANAGER
                )
                self.show_moons = UIImageButton(scale(pygame.Rect(
                    (104, 1028), (68, 68))),
                    "",
                    object_id="#checked_checkbox",
                    tool_tip_text='Stop showing the Moon that certain history events occurred on', manager=MANAGER
                )
                if game.switches["show_history_moons"]:
                    self.no_moons.kill()
                else:
                    self.show_moons.kill()
            elif self.open_sub_tab == 'user notes':
                self.sub_tab_1.enable()
                self.sub_tab_2.disable()
                if self.history_text_box:
                    self.history_text_box.kill()
                    self.no_moons.kill()
                    self.show_moons.kill()
                if self.save_text:
                    self.save_text.kill()
                if self.notes_entry:
                    self.notes_entry.kill()
                if self.edit_text:
                    self.edit_text.kill()
                if self.display_notes:
                    self.display_notes.kill()
                if self.help_button:
                    self.help_button.kill()

                self.help_button = UIImageButton(scale(pygame.Rect(
                    (104, 1168), (68, 68))),
                    "",
                    object_id="#help_button", manager=MANAGER,
                    tool_tip_text="The notes section has limited html capabilities.<br>"
                                  "Use the following commands with < and > in place of the apostrophes.<br>"
                                  "-'br' to start a new line.<br>"
                                  "-Encase text between 'b' and '/b' to bold.<br>"
                                  "-Encase text between 'i' and '/i' to italicize.<br>"
                                  "-Encase text between 'u' and '/u' to underline.<br><br>"
                                  "The following font related codes can be used, "
                                  "but keep in mind that not all font faces will work.<br>"
                                  "-Encase text between 'font face = name of font you wish to use' and '/font' to change the font face.<br>"
                                  "-Encase text between 'font color= #hex code of the color' and '/font' to change the color of the text.<br>"
                                  "-Encase text between 'font size=number of size' and '/font' to change the text size.",

                )
                if self.editing_notes is True:
                    self.save_text = UIImageButton(scale(pygame.Rect(
                        (104, 1028), (68, 68))),
                        "",
                        object_id="#unchecked_checkbox",
                        tool_tip_text='lock and save text', manager=MANAGER
                    )

                    self.notes_entry = pygame_gui.elements.UITextEntryBox(
                        scale(pygame.Rect((200, 946), (1200, 298))),
                        initial_text=self.user_notes,
                        object_id='#text_box_26_horizleft_pad_10_14', manager=MANAGER
                    )
                else:
                    self.edit_text = UIImageButton(scale(pygame.Rect(
                        (104, 1028), (68, 68))),
                        "",
                        object_id="#checked_checkbox_smalltooltip",
                        tool_tip_text='edit text', manager=MANAGER
                    )

                    self.display_notes = UITextBoxTweaked(self.user_notes,
                                                          scale(pygame.Rect((200, 946), (1200, 298))),
                                                          object_id="#text_box_26_horizleft_pad_10_14",
                                                          line_spacing=1, manager=MANAGER)

        # Conditions Tab
        elif self.open_tab == 'conditions':
            self.display_conditions_page()

    def close_current_tab(self):
        """Closes current tab. """
        if self.open_tab is None:
            pass
        elif self.open_tab == 'relations':
            self.family_tree_button.kill()
            self.see_relationships_button.kill()
            self.choose_mate_button.kill()
            self.change_adoptive_parent_button.kill()
        elif self.open_tab == 'roles':
            self.manage_roles.kill()
            self.change_mentor_button.kill()
        elif self.open_tab == 'personal':
            self.change_name_button.kill()
            self.specify_gender_button.kill()
            if self.cis_trans_button:
                self.cis_trans_button.kill()
            if self.toggle_kits:
                self.toggle_kits.kill()
        elif self.open_tab == 'dangerous':
            self.kill_cat_button.kill()
            self.exile_cat_button.kill()
            self.murder_cat_button.kill()
            if self.join_df_button:
                self.join_df_button.kill()
            if self.exit_df_button:
                self.exit_df_button.kill()
        elif self.open_tab == 'history':
            self.backstory_background.kill()
            self.sub_tab_1.kill()
            self.sub_tab_2.kill()
            self.sub_tab_3.kill()
            self.sub_tab_4.kill()
            self.fav_tab.kill()
            self.not_fav_tab.kill()
            if self.open_sub_tab == 'user notes':
                if self.edit_text:
                    self.edit_text.kill()
                if self.save_text:
                    self.save_text.kill()
                if self.notes_entry:
                    self.notes_entry.kill()
                if self.display_notes:
                    self.display_notes.kill()
                self.help_button.kill()
            elif self.open_sub_tab == 'life events':
                if self.history_text_box:
                    self.history_text_box.kill()
                self.show_moons.kill()
                self.no_moons.kill()
        elif self.open_tab == 'your tab':
            if self.have_kits_button:
                self.have_kits_button.kill()
            if self.change_accessory_button:
                self.change_accessory_button.kill()
            if self.request_apprentice_button:
                self.request_apprentice_button.kill()
        elif self.open_tab == 'conditions':
            self.left_conditions_arrow.kill()
            self.right_conditions_arrow.kill()
            self.conditions_background.kill()
            self.condition_container.kill()

        self.open_tab = None

    # ---------------------------------------------------------------------------- #
    #                               cat platforms                                  #
    # ---------------------------------------------------------------------------- #
    def get_platform(self):
        the_cat = Cat.all_cats.get(game.switches['cat'],
                                   game.clan.instructor)

        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome

        if biome not in available_biome:
            biome = available_biome[0]
        if the_cat.age == 'newborn' or the_cat.not_working():
            biome = 'nest'

        biome = biome.lower()

        platformsheet = pygame.image.load('resources/images/platforms.png').convert_alpha()

        order = ['beach', 'forest', 'mountainous', 'nest', 'plains', 'SC/DF']


        biome_platforms = platformsheet.subsurface(pygame.Rect(0, order.index(biome) * 70, 640, 70)).convert_alpha()
        
        
        biome_platforms = platformsheet.subsurface(pygame.Rect(0, order.index(biome) * 70, 640, 70)).convert_alpha()

        offset = 0
        if light_dark == "light":
            offset = 80
        
        season_subsurfaces = {
            "greenleaf": 0 + offset,
            "leafbare": 160 + offset,
            "leaffall": 320 + offset,
            "newleaf": 480 + offset
        }
        
        if the_cat.df:
            biome_platforms = platformsheet.subsurface(pygame.Rect(0, order.index('SC/DF') * 70, 640, 70))
            return pygame.transform.scale(biome_platforms.subsurface(pygame.Rect(0 + offset, 0, 80, 70)), (240, 210))
        elif the_cat.dead or game.clan.instructor.ID == the_cat.ID:
            biome_platforms = platformsheet.subsurface(pygame.Rect(0, order.index('SC/DF') * 70, 640, 70))
            return pygame.transform.scale(biome_platforms.subsurface(pygame.Rect(160 + offset, 0, 80, 70)), (240, 210))
        else:
            biome_platforms = platformsheet.subsurface(pygame.Rect(0, order.index(biome) * 70, 640, 70)).convert_alpha()
            season_x = {
                "greenleaf": 0 + offset,
                "leaf-bare": 160 + offset,
                "leaf-fall": 320 + offset,
                "newleaf": 480 + offset
            }
            
            return pygame.transform.scale(biome_platforms.subsurface(pygame.Rect(
                season_x.get(game.clan.current_season.lower(), season_x["greenleaf"]), 0, 80, 70)), (240, 210))

    def on_use(self):
        pass


# ---------------------------------------------------------------------------- #
#                           ceremony screen                                    #
# ---------------------------------------------------------------------------- #
class CeremonyScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.text = None
        self.scroll_container = None
        self.life_text = None
        self.header = None
        self.the_cat = None

    def screen_switches(self):
        self.hide_menu_buttons()
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        if self.the_cat.status == 'leader':
            self.header = pygame_gui.elements.UITextBox(str(self.the_cat.name) + '\'s Leadership Ceremony',
                                                        scale(pygame.Rect((200, 180), (1200, -1))),
                                                        object_id=get_text_box_theme(), manager=MANAGER)
        else:
            self.header = pygame_gui.elements.UITextBox(str(self.the_cat.name) + ' has no ceremonies to view.',
                                                        scale(pygame.Rect((200, 180), (1200, -1))),
                                                        object_id=get_text_box_theme(), manager=MANAGER)
        if self.the_cat.status == 'leader' and not self.the_cat.dead:
            self.life_text = History.get_lead_ceremony(self.the_cat)

        else:
            self.life_text = ""

        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((100, 300), (1400, 1000))))
        self.text = pygame_gui.elements.UITextBox(self.life_text,
                                                  scale(pygame.Rect((0, 0), (1100, -1))),
                                                  object_id=get_text_box_theme("#text_box_30_horizleft"),
                                                  container=self.scroll_container, manager=MANAGER)
        self.text.disable()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                         object_id="#back_button", manager=MANAGER)
        self.scroll_container.set_scrollable_area_dimensions((1360 / 1600 * screen_x, self.text.rect[3]))

    def exit_screen(self):
        self.header.kill()
        del self.header
        self.text.kill()
        del self.text
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button

    def on_use(self):
        pass

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('profile screen')
        return


# ---------------------------------------------------------------------------- #
#                               Role Screen                                    #
# ---------------------------------------------------------------------------- #
class RoleScreen(Screens):
    the_cat = None
    selected_cat_elements = {}
    buttons = {}
    next_cat = None
    previous_cat = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.update_selected_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_selected_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.promote_leader:
                if self.the_cat == game.clan.deputy:
                    game.clan.deputy = None
                game.clan.new_leader(self.the_cat)
                if game.sort_type == "rank":
                    Cat.sort_cats()
                self.update_selected_cat()
            elif event.ui_element == self.promote_deputy:
                game.clan.deputy = self.the_cat
                self.the_cat.status_change("deputy", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_warrior:
                self.the_cat.status_change("warrior", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_med_cat:
                self.the_cat.status_change("medicine cat", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.retire:
                self.the_cat.status_change("elder", resort=True)
                # Since you can't "unretire" a cat, apply the skill and trait change
                # here
                self.update_selected_cat()
            elif event.ui_element == self.switch_mediator:
                self.the_cat.status_change("mediator", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_warrior_app:
                self.the_cat.status_change("apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_med_app:
                self.the_cat.status_change("medicine cat apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_mediator_app:
                self.the_cat.status_change("mediator apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_queen_app:
                self.the_cat.status_change("queen's apprentice", resort=True)
                self.update_selected_cat()
            elif event.ui_element == self.switch_queen:
                self.the_cat.status_change("queen", resort=True)
                self.update_selected_cat()
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen("profile screen")
            elif event.key == pygame.K_RIGHT:
                game.switches["cat"] = self.next_cat
                self.update_selected_cat()
            elif event.key == pygame.K_LEFT:
                game.switches["cat"] = self.previous_cat
                self.update_selected_cat()

    def screen_switches(self):

        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "", object_id="#next_cat_button"
                                             , manager=MANAGER)
        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button"
                                                 , manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 120), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)

        # Create the buttons
        self.bar = pygame_gui.elements.UIImage(scale(pygame.Rect((96, 700), (1408, 20))),
                                               pygame.transform.scale(
                                                   image_cache.load_image("resources/images/bar.png"),
                                                   (1408 / 1600 * screen_x, 20 / 1400 * screen_y)
                                               ), manager=MANAGER)

        self.blurb_background = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                  ((100, 390), (1400, 300))),
                                                            pygame.transform.scale(
                                                                pygame.image.load(
                                                                    "resources/images/mediation_selection_bg.png").convert_alpha(),
                                                                (1400, 300))
                                                            )

        # LEADERSHIP
        self.promote_leader = UIImageButton(scale(pygame.Rect((96, 720), (344, 72))), "",
                                            object_id="#promote_leader_button",
                                            manager=MANAGER)
        self.promote_deputy = UIImageButton(scale(pygame.Rect((96, 792), (344, 72))), "",
                                            object_id="#promote_deputy_button",
                                            manager=MANAGER)

        # ADULT CAT ROLES
        self.switch_warrior = UIImageButton(scale(pygame.Rect((451, 720), (344, 72))), "",
                                            object_id="#switch_warrior_button",
                                            manager=MANAGER)
        self.retire = UIImageButton(scale(pygame.Rect((451, 792), (334, 72))), "",
                                    object_id="#retire_button",
                                    manager=MANAGER)
        self.switch_med_cat = UIImageButton(scale(pygame.Rect((805, 720), (344, 104))), "",
                                            object_id="#switch_med_cat_button",
                                            manager=MANAGER)
        self.switch_mediator = UIImageButton(scale(pygame.Rect((805, 824), (344, 72))), "",
                                             object_id="#switch_mediator_button",
                                             manager=MANAGER)
        self.switch_queen = UIImageButton(scale(pygame.Rect((805, 895), (344, 104))), "",
                                             object_id="#switch_queen_button",
                                             manager=MANAGER)

        # In-TRAINING ROLES:
        self.switch_warrior_app = UIImageButton(scale(pygame.Rect((1159, 720), (344, 104))), "",
                                                object_id="#switch_warrior_app_button",
                                                manager=MANAGER)
        self.switch_med_app = UIImageButton(scale(pygame.Rect((1159, 824), (344, 104))), "",
                                            object_id="#switch_med_app_button",
                                            manager=MANAGER)
        self.switch_mediator_app = UIImageButton(scale(pygame.Rect((1159, 928), (344, 104))), "",
                                                 object_id="#switch_mediator_app_button",
                                                 manager=MANAGER)
        self.switch_queen_app = UIImageButton(scale(pygame.Rect((1159, 1032), (344, 104))), "",
                                             object_id="#switch_queen_app_button",
                                             manager=MANAGER)


        self.update_selected_cat()

    def update_selected_cat(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        if not self.the_cat:
            return

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((490, 80), (300, 300))),
            pygame.transform.scale(
                self.the_cat.sprite, (300, 300)),
            manager=MANAGER
        )

        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 300, 26)
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(scale(pygame.Rect((775, 140), (350, -1))),
                                                                             short_name,
                                                                             object_id=get_text_box_theme())

        text = f"<b>{self.the_cat.status}</b>\n{self.the_cat.personality.trait}\n"

        text += f"{self.the_cat.moons} "

        if self.the_cat.moons == 1:
            text += "moon  |  "
        else:
            text += "moons  |  "

        text += self.the_cat.genderalign + "\n"

        if self.the_cat.mentor:
            text += "mentor: "
            mentor = Cat.fetch_cat(self.the_cat.mentor)
            if mentor:
                text += str(mentor.name)

        if self.the_cat.apprentice:
            if len(self.the_cat.apprentice) > 1:
                text += "apprentices: "
            else:
                text += "apprentice: "

            text += ", ".join([str(Cat.fetch_cat(x).name) for x in
                               self.the_cat.apprentice if Cat.fetch_cat(x)])

        self.selected_cat_elements["cat_details"] = UITextBoxTweaked(text, scale(pygame.Rect((790, 200), (320, 188))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_22_horizcenter"),
                                                                     manager=MANAGER, line_spacing=0.95)

        self.selected_cat_elements["role_blurb"] = pygame_gui.elements.UITextBox(self.get_role_blurb(),
                                                                                 scale(pygame.Rect((340, 400),
                                                                                                   (1120, 270))),
                                                                                 object_id="#text_box_26_horizcenter_vertcenter_spacing_95",
                                                                                 manager=MANAGER)

        main_dir = "resources/images/"
        paths = {
            "leader": "leader_icon.png",
            "deputy": "deputy_icon.png",
            "medicine cat": "medic_icon.png",
            "medicine cat apprentice": "medic_app_icon.png",
            "mediator": "mediator_icon.png",
            "mediator apprentice": "mediator_app_icon.png",
            "queen": "elder_icon.png",
            "queen's apprentice": "kit_icon.png",
            "warrior": "warrior_icon.png",
            "apprentice": "warrior_app_icon.png",
            "kitten": "kit_icon.png",
            "newborn": "kit_icon.png",
            "elder": "elder_icon.png",
        }

        if self.the_cat.status in paths:
            icon_path = os.path.join(main_dir, paths[self.the_cat.status])
        else:
            icon_path = os.path.join(main_dir, "buttonrank.png")

        self.selected_cat_elements["role_icon"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((165, 462), (156, 156))),
            pygame.transform.scale(
                image_cache.load_image(icon_path),
                (156 / 1600 * screen_x, 156 / 1400 * screen_y)
            ))

        self.determine_previous_and_next_cat()
        self.update_disabled_buttons()

    def update_disabled_buttons(self):
        # Previous and next cat button
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

        if game.clan.leader:
            leader_invalid = game.clan.leader.dead or game.clan.leader.outside
        else:
            leader_invalid = True

        if game.clan.deputy:
            deputy_invalid = game.clan.deputy.dead or game.clan.deputy.outside
        else:
            deputy_invalid = True

        if self.the_cat.status == "apprentice":
            # LEADERSHIP
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.switch_queen.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.enable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.enable()
            self.switch_queen_app.enable()
        elif self.the_cat.status == "warrior":
            # LEADERSHIP
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            if deputy_invalid:
                self.promote_deputy.enable()
            else:
                self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.enable()
            self.switch_mediator.enable()
            self.switch_queen.enable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.disable()

        elif self.the_cat.status == "deputy":
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.enable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.switch_queen.disable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.disable()
            
        elif self.the_cat.status == "medicine cat":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            self.switch_warrior.enable()
            self.switch_med_cat.disable()
            self.switch_mediator.enable()
            self.switch_queen.enable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.disable()
        elif self.the_cat.status == "queen":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            self.switch_warrior.enable()
            self.switch_med_cat.enable()
            self.switch_mediator.enable()
            self.switch_queen.disable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.disable()
        elif self.the_cat.status == "mediator":
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            if deputy_invalid:
                self.promote_deputy.enable()
            else:
                self.promote_deputy.disable()

            self.switch_warrior.enable()
            self.switch_med_cat.enable()
            self.switch_mediator.disable()
            self.switch_queen.enable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.disable()
        elif self.the_cat.status == "elder":
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            if deputy_invalid:
                self.promote_deputy.enable()
            else:
                self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.enable()
            self.switch_med_cat.enable()
            self.switch_mediator.enable()
            self.switch_queen.enable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.disable()
        elif self.the_cat.status == "medicine cat apprentice":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.switch_queen.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.enable()
            self.switch_queen_app.enable()
        elif self.the_cat.status == "medicine cat apprentice":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.switch_queen.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.enable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.enable()
            self.switch_queen_app.disable()
        elif self.the_cat.status == "mediator apprentice":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.switch_queen.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.enable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.enable()
        
        elif self.the_cat.status == "queen's apprentice":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.switch_queen.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.enable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.enable()
            self.switch_queen_app.disable()
        elif self.the_cat.status == "leader":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.enable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.switch_queen.disable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.disable()
        else:
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.switch_queen.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
            self.switch_queen_app.disable()

    def get_role_blurb(self):
        if self.the_cat.status == "warrior":
            output = f"{self.the_cat.name} is a <b>warrior</b>. Warriors are adult cats who feed and protect their " \
                     f"Clan. They are trained to hunt and fight in addition to the ways of the warrior code. " \
                     f"Warriors are essential to the survival of a Clan, and usually make up the bulk of it's members. "
        elif self.the_cat.status == "leader":
            output = f"{self.the_cat.name} is the <b>leader</b> of {game.clan.name}Clan. The guardianship of all " \
                     f"Clan cats has been entrusted to them by StarClan. The leader is the highest " \
                     f"authority in the Clan. The leader holds Clan meetings, determines mentors for " \
                     f"new apprentices, and names new warriors. To help them protect the Clan, " \
                     f"StarClan has given them nine lives. They typically take the suffix \"star\"."
        elif self.the_cat.status == "deputy":
            output = f"{self.the_cat.name} is {game.clan.name}Clan's <b>deputy</b>. " \
                     f"The deputy is the second in command, " \
                     f"just below the leader. They advise the leader and organize daily patrols, " \
                     f"alongside normal warrior duties. Typically, a deputy is personally appointed by the current " \
                     f"leader. As dictated by the Warrior Code, all deputies must train at least one apprentice " \
                     f"before appointment.  " \
                     f"The deputy succeeds the leader if they die or retire. "
        elif self.the_cat.status == "medicine cat":
            output = f"{self.the_cat.name} is a <b>medicine cat</b>. Medicine cats are the healers of the Clan. " \
                     f"They treat " \
                     f"injuries and illnesses with herbal remedies. Unlike warriors, medicine cats are not expected " \
                     f"to hunt and fight for the Clan. In addition to their healing duties, medicine cats also have " \
                     f"a special connection to StarClan. Every half-moon, they travel to their Clan's holy place " \
                     f"to commune with StarClan. "
        elif self.the_cat.status == "mediator":
            output = f"{self.the_cat.name} is a <b>mediator</b>. Mediators are not typically required " \
                     f"to hunt or fight for " \
                     f"the Clan. Rather, mediators are charged with handling disagreements between " \
                     f"Clanmates and disputes between Clans. Some mediators train as apprentices to serve their Clan, " \
                     f"while others may choose to become mediators later in life. "
        elif self.the_cat.status == "queen":
            output = f"{self.the_cat.name} is a <b>queen</b>. Permanent queens dedicate their lives to " \
                    f"caring for and nurturing the kits of the Clan, ensuring their safety and early education. " \
                    f"While most queens return to their warrior duties once their kits grow, permanent queens remain " \
                    f"in the nursery, offering guidance to new parents and providing a steady presence for the Clan's young. "
        elif self.the_cat.status == "elder":
            output = f"{self.the_cat.name} is an <b>elder</b>. They have spent many moons serving their Clan, " \
                     f"and have earned " \
                     f"many moons of rest. Elders are essential to passing down the oral tradition of the Clan. " \
                     f"Sometimes, cats may retire due to disability or injury. Whatever the " \
                     f"circumstance of their retirement, elders are held in high esteem in the Clan, and always eat " \
                     f"before Warriors and Medicine Cats. "
        elif self.the_cat.status == "apprentice":
            output = f"{self.the_cat.name} is an <b>apprentice</b>, in training to become a warrior. " \
                     f"Kits can be made warrior apprentices at six moons of age, where they will learn how " \
                     f"to hunt and fight for their Clan. Typically, the training of an apprentice is entrusted " \
                     f"to an single warrior - their mentor. To build character, apprentices are often assigned " \
                     f"the unpleasant and grunt tasks of Clan life. Apprentices take the suffix \"paw\", " \
                     f"to represent the path their paws take towards adulthood. "
        elif self.the_cat.status == "medicine cat apprentice":
            output = f"{self.the_cat.name} is a <b>medicine cat apprentice</b>, training to become a full medicine cat. " \
                     f"Kits can be made medicine cat apprentices at six moons of age, where they will learn how to " \
                     f"heal their Clanmates and commune with StarClan. Medicine cat apprentices are typically chosen " \
                     f"for their interest in healing and/or their connecting to StarClan. Apprentices take the suffix " \
                     f"-paw, to represent the path their paws take towards adulthood."
        elif self.the_cat.status == "mediator apprentice":
            output = f"{self.the_cat.name} is a <b>mediator apprentice</b>, training to become a full mediator. " \
                     f"Mediators are in charge of handling disagreements both within the Clan and between Clans. " \
                     f"Mediator apprentices are often chosen for their quick thinking and steady personality. " \
                     f"Apprentices take the suffix \"paw\", " \
                     f"to represent the path their paws take towards adulthood. "
        elif self.the_cat.status == "queen's apprentice":
            output = f"{self.the_cat.name} is a <b>queen's apprentice</b>. A queen's apprentice is trained under the guidance " \
                    f"of a permanent queen to learn the intricacies of caring for and nurturing kits. These apprentices " \
                    f"learn about the basic needs of kits, early Clan teachings, and the importance of the nursery environment. " \
                    f"They assist in keeping the nursery safe and comfortable, mediating between kits, and ensuring their " \
                    f"general wellbeing. "
        elif self.the_cat.status == "kitten":
            output = f"{self.the_cat.name} is a <b>kitten</b>. All cats below the age of six moons are " \
                     f"considered kits. Kits " \
                     f"are prohibited from leaving camp in order to protect them from the dangers of the wild. " \
                     f"Although they don't have any official duties in the Clan, they are expected to learn the " \
                     f"legends and traditions of their Clan. They are protected by every cat in the Clan and always " \
                     f"eat first. Kits take the suffix \"kit\"."
        elif self.the_cat.status == "newborn":
            output = f"{self.the_cat.name} is a <b>newborn kitten</b>. All cats below the age of six moons are " \
                     f"considered kits. Kits " \
                     f"are prohibited from leaving camp in order to protect them from the dangers of the wild. " \
                     f"Although they don't have any official duties in the Clan, they are expected to learn the " \
                     f"legends and traditions of their Clan. They are protected by every cat in the Clan and always " \
                     f"eat first. Kits take the suffix \"kit\"."
        else:
            output = f"{self.the_cat.name} has an unknown rank. I guess they want to make their own way in life! "

        return output

    def determine_previous_and_next_cat(self):
        """'Determines where the next and previous buttons point too."""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and self.the_cat.df == game.clan.instructor.df and \
                not (self.the_cat.outside or self.the_cat.exiled):
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead \
                        and check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    previous_cat = check_cat.ID

                elif next_cat == 1 and check_cat != self.the_cat.ID and check_cat.dead == self.the_cat.dead \
                        and check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

    def exit_screen(self):
        self.back_button.kill()
        del self.back_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.bar.kill()
        del self.bar
        self.promote_leader.kill()
        del self.promote_leader
        self.promote_deputy.kill()
        del self.promote_deputy
        self.switch_warrior.kill()
        del self.switch_warrior
        self.switch_med_cat.kill()
        del self.switch_med_cat
        self.switch_queen.kill()
        del self.switch_queen
        self.switch_queen_app.kill()
        del self.switch_queen_app
        self.switch_mediator.kill()
        del self.switch_mediator
        self.retire.kill()
        del self.retire
        self.switch_med_app.kill()
        del self.switch_med_app
        self.switch_warrior_app.kill()
        del self.switch_warrior_app
        self.switch_mediator_app.kill()
        del self.switch_mediator_app
        self.blurb_background.kill()
        del self.blurb_background

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

# ---------------------------------------------------------------------------- #
#                            SpriteInspectScreen                               #
# ---------------------------------------------------------------------------- #

class SpriteInspectScreen(Screens):
    cat_life_stages = ["newborn", "kitten", "adolescent", "adult", "senior"]
    
    def __init__(self, name=None):
        self.back_button = None
        self.previous_cat_button = None
        self.previous_cat = None
        self.next_cat_button = None
        self.next_cat = None
        self.the_cat = None
        self.cat_image = None
        self.cat_elements = {}
        self.checkboxes = {}
        self.platform_shown_text = None
        self.scars_shown = None
        self.acc_shown_text = None
        self.override_dead_lineart_text = None
        self.override_not_working_text = None
        self.save_image_button = None
        
        #Image Settings: 
        self.platform_shown = None
        self.displayed_lifestage = None
        self.scars_shown = True
        self.override_dead_lineart = False
        self.acc_shown = True
        self.override_not_working = False
        
        super().__init__(name)
    
    def handle_event(self, event):
        # Don't handle the events if a window is open.     
        if game.switches['window_open']:
            return
        
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.cat_setup()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.cat_setup()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_life_stage:
                self.displayed_life_stage = min(self.displayed_life_stage + 1, 
                                                len(self.valid_life_stages) - 1)
                self.update_disabled_buttons()
                self.make_cat_image()
            elif event.ui_element == self.save_image_button:
                SaveAsImage(self.generate_image_to_save(), str(self.the_cat.name))
            elif event.ui_element == self.previous_life_stage:
                self.displayed_life_stage = max(self.displayed_life_stage - 1, 
                                                0)
                self.update_disabled_buttons()
                self.make_cat_image()
            elif event.ui_element == self.checkboxes["platform_shown"]:
                if self.platform_shown:
                    self.platform_shown = False
                else:
                    self.platform_shown = True
                
                self.set_background_visablity()
                self.update_checkboxes()
            elif event.ui_element == self.checkboxes["scars_shown"]:
                if self.scars_shown:
                    self.scars_shown = False
                else:
                    self.scars_shown = True
                
                self.make_cat_image()
                self.update_checkboxes()
            elif event.ui_element == self.checkboxes["acc_shown"]:
                if self.acc_shown:
                    self.acc_shown = False
                else:
                    self.acc_shown = True
                
                self.make_cat_image()
                self.update_checkboxes()
            elif event.ui_element == self.checkboxes["override_dead_lineart"]:
                if self.override_dead_lineart:
                    self.override_dead_lineart = False
                else:
                    self.override_dead_lineart = True
                
                self.make_cat_image()
                self.update_checkboxes()
            elif event.ui_element == self.checkboxes["override_not_working"]:
                if self.override_not_working:
                    self.override_not_working = False
                else:
                    self.override_not_working = True
                
                self.make_cat_image()
                self.update_checkboxes()
            elif event.ui_element == self.cat_elements["favourite_button"]:
                self.the_cat.favourite = False
                self.cat_elements["favourite_button"].hide()
                self.cat_elements["not_favourite_button"].show()
            elif event.ui_element == self.cat_elements["not_favourite_button"]:
                self.the_cat.favourite = True
                self.cat_elements["favourite_button"].show()
                self.cat_elements["not_favourite_button"].hide()
    
        return super().handle_event(event)
    
    def screen_switches(self):        
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "", object_id="#next_cat_button"
                                             , manager=MANAGER)
        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button"
                                                 , manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 120), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        
        self.previous_life_stage = UIImageButton(scale(pygame.Rect((150, 550), (76, 100))), "", object_id="#arrow_right_fancy",
                                                 starting_height=2)
        
        self.next_life_stage = UIImageButton(scale(pygame.Rect((1374, 550), (76, 100))), "", object_id="#arrow_left_fancy",
                                             starting_height=2)
        
        self.save_image_button = UIImageButton(scale(pygame.Rect((50, 190),(270, 60))), "", object_id="#save_image_button")
        
        # Toggle Text:
        self.platform_shown_text = pygame_gui.elements.UITextBox("Show Platform", scale(pygame.Rect((310, 1160), (290, 100))),
                                                                 object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                                 starting_height=2)
        self.scars_shown_text = pygame_gui.elements.UITextBox("Show Scar(s)", scale(pygame.Rect((710, 1160), (290, 100))),
                                                              object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                                 starting_height=2)
        self.acc_shown_text = pygame_gui.elements.UITextBox("Show Accessory", scale(pygame.Rect((1100, 1160), (290, 100))),
                                                            object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                            starting_height=2)
        self.override_dead_lineart_text = pygame_gui.elements.UITextBox("Show as Living", scale(pygame.Rect((510, 1260), (290, 100))),
                                                                        object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                                        starting_height=2)
        self.override_not_working_text = pygame_gui.elements.UITextBox("Show as Healthy", scale(pygame.Rect((910, 1260), (290, 100))),
                                                                 object_id=get_text_box_theme(
                                                                              "#text_box_34_horizcenter"), 
                                                                 starting_height=2)
        
        
        if game.settings['backgrounds']:
            self.platform_shown = True
        else:
            self.platform_shown = False
        
        self.cat_setup()
        return super().screen_switches()

    def cat_setup(self): 
        """Sets up all the elements related to the cat """
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}
        
        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        
        self.cat_elements["platform"] = pygame_gui.elements.UIImage(
                scale(pygame.Rect((240, 200), (1120, 980))),
                pygame.transform.scale(self.get_platform(), scale_dimentions((1120, 701))), 
                manager=MANAGER)
        self.set_background_visablity()
        
        # Gather list of current and previous life states
        # "young adult", "adult", and "senior adult" all look the same: collapse to adult
        # This is not the best way to do it, so if we make them have difference appearances, this will
        # need to be changed/removed. 
        if self.the_cat.age in ["young adult", "adult", "senior adult"]:
            current_life_stage = "adult"
        else:
            current_life_stage = self.the_cat.age
        
        self.valid_life_stages = []
        for life_stage in SpriteInspectScreen.cat_life_stages:
            self.valid_life_stages.append(life_stage)
            if life_stage == current_life_stage:
                break
        
        #Store the index of the currently displayed life stage. 
        self.displayed_life_stage = len(self.valid_life_stages) - 1
        
        #Reset all the toggles
        self.lifestage = None
        self.scars_shown = True
        self.override_dead_lineart = False
        self.acc_shown = True
        self.override_not_working = False
        
        # Make the cat image
        self.make_cat_image()
        
        cat_name = str(self.the_cat.name)  # name
        if self.the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        short_name = shorten_text_to_fit(cat_name, 390, 40)
        
        self.cat_elements["cat_name"] = pygame_gui.elements.UITextBox(short_name,
                                                                          scale(pygame.Rect((50, 120), (-1, 80))),
                                                                          object_id=get_text_box_theme(
                                                                              "#text_box_40_horizcenter"), manager=MANAGER)
        name_text_size = self.cat_elements["cat_name"].get_relative_rect()

        self.cat_elements["cat_name"].kill()

        self.cat_elements["cat_name"] = pygame_gui.elements.UITextBox(short_name,
                                                                      scale(pygame.Rect(
                                                                        (800 - name_text_size.width, 120),
                                                                        (name_text_size.width * 2, 80))),
                                                                       object_id=get_text_box_theme(
                                                                        "#text_box_40_horizcenter"), manager=MANAGER)
        
        # Fullscreen
        if game.settings['fullscreen']:
            x_pos = 745 - name_text_size.width//2
        else:
            x_pos = 740 - name_text_size.width
        self.cat_elements["favourite_button"] = UIImageButton(scale(pygame.Rect
                                                                ((x_pos, 127), (56, 56))),
                                                              "",
                                                              object_id="#fav_cat",
                                                              manager=MANAGER,
                                                              tool_tip_text='Remove favorite status',
                                                              starting_height=2)

        self.cat_elements["not_favourite_button"] = UIImageButton(scale(pygame.Rect
                                                                    ((x_pos, 127),
                                                                        (56, 56))),
                                                                 "",
                                                                 object_id="#not_fav_cat",
                                                                 manager=MANAGER,
                                                                 tool_tip_text='Mark as favorite',
                                                                 starting_height=2)  
        if self.the_cat.favourite:
            self.cat_elements["favourite_button"].show()
            self.cat_elements["not_favourite_button"].hide()
        else:
            self.cat_elements["favourite_button"].hide()
            self.cat_elements["not_favourite_button"].show()
        
        
        # Write the checkboxes. The text is set up in switch_screens.  
        self.update_checkboxes()
        
        
        self.determine_previous_and_next_cat()
        self.update_disabled_buttons()
    
    def update_checkboxes(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}
        
        # "Show Platform"
        self.make_one_checkbox((200, 1150), "platform_shown", self.platform_shown)
        
        # "Show Scars"
        self.make_one_checkbox((600, 1150), "scars_shown", self.scars_shown, self.the_cat.pelt.scars)
        
        # "Show accessories"
        self.make_one_checkbox((1000, 1150), "acc_shown", self.acc_shown, self.the_cat.pelt.accessory)
        
        # "Show as living"
        self.make_one_checkbox((400, 1250), "override_dead_lineart", self.override_dead_lineart, self.the_cat.dead,
                               disabled_object_id="#checked_checkbox")
        
        # "Show as healthy"
        self.make_one_checkbox((800, 1250), "override_not_working", self.override_not_working, self.the_cat.not_working(),
                               disabled_object_id="#checked_checkbox")
        
    def make_one_checkbox(self, location:tuple, name:str, stored_bool: bool, cat_value_to_allow=True,
                          disabled_object_id = "#unchecked_checkbox"):
        """Makes a single checkbox. So I don't have to copy and paste this 5 times. 
            if cat_value_to_allow evaluates to False, then the unchecked checkbox is always used the the checkbox 
            is disabled"""
        
        if not cat_value_to_allow:
            self.checkboxes[name] = UIImageButton(scale(pygame.Rect(location, (102, 102))), "" ,
                                                            object_id = disabled_object_id,
                                                            starting_height=2)
            self.checkboxes[name].disable()
        elif stored_bool:
            self.checkboxes[name] = UIImageButton(scale(pygame.Rect(location, (102, 102))), "" ,
                                                            object_id = "#checked_checkbox",
                                                            starting_height=2)
        else:
            self.checkboxes[name] = UIImageButton(scale(pygame.Rect(location, (102, 102))), "" ,
                                                            object_id = "#unchecked_checkbox",
                                                            starting_height=2)
    
    def make_cat_image(self):
        """Makes the cat image """
        if "cat_image" in self.cat_elements:
            self.cat_elements["cat_image"].kill()
        
        self.cat_image = generate_sprite(self.the_cat, life_state=self.valid_life_stages[self.displayed_life_stage], 
                                         scars_hidden=not self.scars_shown,
                                         acc_hidden=not self.acc_shown, always_living=self.override_dead_lineart, 
                                         no_not_working=self.override_not_working)
        
        self.cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((450, 200),(700, 700))),
            pygame.transform.scale(self.cat_image, scale_dimentions((700, 700)))
        )
      
    def determine_previous_and_next_cat(self):
        """'Determines where the next and previous buttons point too."""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and self.the_cat.df == game.clan.instructor.df and \
                not (self.the_cat.outside or self.the_cat.exiled):
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead \
                        and check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    previous_cat = check_cat.ID

                elif next_cat == 1 and check_cat != self.the_cat.ID and check_cat.dead == self.the_cat.dead \
                        and check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat
    
    def set_background_visablity(self):
        if "platform" not in self.cat_elements:
            return
        
        if self.platform_shown:
            self.cat_elements["platform"].show()
            self.cat_elements["platform"].disable()
        else:
            self.cat_elements["platform"].hide()
    
    def exit_screen(self):
        self.back_button.kill()
        self.back_button = None
        self.previous_cat_button.kill()
        self.previous_cat_button = None
        self.next_cat_button.kill()
        self.next_cat_button = None
        self.previous_life_stage.kill()
        self.previous_life_stage = None
        self.next_life_stage.kill()
        self.next_life_stage = None
        self.save_image_button.kill()
        self.save_image_button = None
        self.platform_shown_text.kill()
        self.platform_shown_text = None
        self.scars_shown_text.kill()
        self.scars_shown = None
        self.acc_shown_text.kill()
        self.acc_shown_text = None
        self.override_dead_lineart_text.kill()
        self.override_dead_lineart_text = None
        self.override_not_working_text.kill()
        self.override_not_working_text = None
        
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}
        return super().exit_screen()
    
    def update_disabled_buttons(self):
        # Previous and next cat button
        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()
            
        if self.displayed_life_stage >= len(self.valid_life_stages) - 1:
            self.next_life_stage.disable()
        else:
            self.next_life_stage.enable()
            
        if self.displayed_life_stage <= 0:
            self.previous_life_stage.disable()
        else:
            self.previous_life_stage.enable()
        
        
    def get_platform(self):
        the_cat = Cat.all_cats.get(game.switches['cat'],
                                   game.clan.instructor)

        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome

        if biome not in available_biome:
            biome = available_biome[0]
        if the_cat.age == 'newborn' or the_cat.not_working():
            biome = 'nest'

        biome = biome.lower()

        platformsheet = pygame.image.load('resources/images/platforms.png').convert_alpha()
        
        order = ['beach', 'forest', 'mountainous', 'nest', 'plains', 'SC/DF']
        
        offset = 0
        if light_dark == "light":
            offset = 80
        
        if the_cat.df:
            biome_platforms = platformsheet.subsurface(pygame.Rect(0, order.index('SC/DF') * 70, 640, 70))
            return biome_platforms.subsurface(pygame.Rect(0 + offset, 0, 80, 70))
        elif the_cat.dead or game.clan.instructor.ID == the_cat.ID:
            biome_platforms = platformsheet.subsurface(pygame.Rect(0, order.index('SC/DF') * 70, 640, 70))
            return biome_platforms.subsurface(pygame.Rect(160 + offset, 0, 80, 70))
        else:
            biome_platforms = platformsheet.subsurface(pygame.Rect(0, order.index(biome) * 70, 640, 70)).convert_alpha()
            season_x = {
                "greenleaf": 0 + offset,
                "leafbare": 160 + offset,
                "leaffall": 320 + offset,
                "newleaf": 480 + offset
            }
            
            
            return biome_platforms.subsurface(pygame.Rect(
                season_x.get(game.clan.current_season.lower(), season_x["greenleaf"]), 0, 80, 70))
            
    def generate_image_to_save(self):
        """Generates the image to save, with platform if needed. """
        if self.platform_shown:
            full_image = self.get_platform()
            full_image.blit(self.cat_image, (15, 0))
            return full_image
        else:
            return self.cat_image
        
        
class TalkScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.resource_dir = "resources/dicts/lifegen_talk/"
        self.texts = ""
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]

        self.scroll_container = None
        self.life_text = None
        self.header = None
        self.the_cat = None
        self.text_index = 0
        self.frame_index = 0
        self.typing_delay = 20
        self.next_frame_time = pygame.time.get_ticks() + self.typing_delay
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.text = None
        self.profile_elements = {}
        self.talk_box_img = None


    def screen_switches(self):
        self.update_camp_bg()
        self.hide_menu_buttons()
        self.text_index = 0
        self.frame_index = 0
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.profile_elements = {}
        self.clan_name_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((450, 875), (380, 70))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/clan_name_bg.png").convert_alpha(),
                (500, 870)),
            manager=MANAGER)
        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(str(self.the_cat.name),
                                                                          scale(pygame.Rect((500, 870), (-1, 80))),
                                                                          object_id="#text_box_34_horizcenter_light",
                                                                          manager=MANAGER)
        self.texts = self.get_possible_text(self.the_cat)
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        self.talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()

        self.talk_box = pygame_gui.elements.UIImage(
                scale(pygame.Rect((178, 942), (1248, 302))),
                self.talk_box_img
            )
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                        object_id="#back_button", manager=MANAGER)
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((500, 970), (900, 300))))
        self.text = pygame_gui.elements.UITextBox("", 
                                                  scale(pygame.Rect((0, 0), (900, -100))),
                                                  object_id="#text_box_30_horizleft",
                                                  container=self.scroll_container, manager=MANAGER)
        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((70, 900), (400, 400))),

                                                                         pygame.transform.scale(
                                                                             generate_sprite(self.the_cat),
                                                                             (400, 400)), manager=MANAGER)
        self.paw = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1370, 1180), (30, 30))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
        self.paw.visible = False


    def exit_screen(self):
        self.text.kill()
        del self.text
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button
        self.profile_elements["cat_image"].kill()
        self.profile_elements["cat_name"].kill()
        del self.profile_elements
        self.clan_name_bg.kill()
        del self.clan_name_bg
        self.talk_box.kill()
        del self.talk_box
        self.paw.kill()
        del self.paw

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
            pygame.image.load(all_backgrounds[0]).convert(), (screen_x, screen_y))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (screen_x, screen_y))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (screen_x, screen_y))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (screen_x, screen_y))
    
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
        now = pygame.time.get_ticks()
        if self.text_index < len(self.text_frames):
            if now >= self.next_frame_time and self.frame_index < len(self.text_frames[self.text_index]) - 1:
                self.frame_index += 1
                self.next_frame_time = now + self.typing_delay

        if self.text_index == len(self.text_frames) - 1:
            if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                self.paw.visible = True
        # Always render the current frame
        self.text.html_text = self.text_frames[self.text_index][self.frame_index]
        self.text.rebuild()
        self.clock.tick(60)

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('profile screen')
        elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1  # Go to the last frame
        return
    
    def get_cluster(self, trait):
        # Mapping traits to their respective clusters
        trait_to_clusters = {
            "assertive": ["troublesome", "fierce", "bold", "daring", "confident", "adventurous", "arrogant", "competitive", "rebellious", "impulsive", "noisy"],
            "brooding": ["bloodthirsty", "cold", "strict", "vengeful", "grumpy", "bullying"],
            "cool": ["charismatic", "sneaky", "cunning", "arrogant", "charming"],
            "upstanding": ["righteous", "ambitious", "strict", "competitive", "responsible", "bossy", "know-it-all"],
            "introspective": ["lonesome", "righteous", "calm", "gloomy", "wise", "thoughtful", "quiet", "daydreamer"],
            "neurotic": ["nervous", "insecure", "lonesome", "quiet"],
            "silly": ["troublesome", "childish", "playful", "careful", "strange", "noisy", "attention-seeker"],
            "stable": ["loyal", "responsible", "wise", "faithful"],
            "sweet": ["compassionate", "faithful", "loving", "oblivious", "sincere", "sweet", "polite", "daydreamer"],
            "unabashed": ["childish", "confident", "bold", "shameless", "strange", "oblivious", "flamboyant", "impulsive", "noisy"],
            "unlawful": ["troublesome", "bloodthirsty", "sneaky", "rebellious", "troublesome"]
        }

        clusters = [key for key, values in trait_to_clusters.items() if trait in values]

        # Assign cluster and second_cluster based on the length of clusters list
        cluster = clusters[0] if clusters else ""
        second_cluster = clusters[1] if len(clusters) > 1 else ""

        return cluster, second_cluster
    
    def get_cluster_list(self):
        return ["assertive", "brooding", "cool", "upstanding", "introspective", "neurotic", "silly", "stable", "sweet", "unabashed", "unlawful"]
    
    def get_cluster_list_you(self):
        return ["you_assertive", "you_brooding", "you_cool", "you_upstanding", "you_introspective", "you_neurotic", "you_silly", "you_stable", "you_sweet", "you_unabashed", "you_unlawful"]
    
    
    def relationship_check(self, talk, cat_relationship):
        relationship_conditions = {
            'hate': 50,
            'romantic_like': 30,
            'platonic_like': 30,
            'jealousy': 30,
            'dislike': 30,
            'comfort': 30,
            'respect': 30,
            'trust': 30
        }
        
        for key, value in relationship_conditions.items():
            if key in talk[0] and cat_relationship < value:
                return True
        return False
    
    def handle_random_cat(self, cat):
        random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
        counter = 0
        while random_cat.outside or random_cat.dead or random_cat.ID in [game.clan.your_cat.ID, cat.ID]:
            counter += 1
            if counter == 15:
                break
            random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
        return random_cat
        
    def get_possible_text(self, cat):
        text = ""
        texts_list = []
        you = game.clan.your_cat

        resource_dir = "resources/dicts/lifegen_talk/"
        possible_texts = None
        with open(f"{resource_dir}{cat.status}.json", 'r') as read_file:
            possible_texts = ujson.loads(read_file.read())
            
        if cat.status not in ['kitten', "newborn"] and you.status not in ['kitten', 'newborn']:
            with open(f"{resource_dir}general_no_kit.json", 'r') as read_file:
                possible_texts2 = ujson.loads(read_file.read())
                possible_texts.update(possible_texts2)
        
        if cat.status not in ['kitten', "newborn"] and you.status in ['kitten', 'newborn']:
            with open(f"{resource_dir}general_you_kit.json", 'r') as read_file:
                possible_texts3 = ujson.loads(read_file.read())
                possible_texts.update(possible_texts3)
        
        cluster1, cluster2 = self.get_cluster(cat.personality.trait)
        cluster3, cluster4 = self.get_cluster(you.personality.trait)
        
        their_trait_list = ['troublesome', 'fierce', 'bold', 'daring', 'confident', 'adventurous', 'arrogant', 'competitive', 'rebellious', 'bloodthirsty', 'cold', 'strict', 'vengeful', 'grumpy', 'charismatic', 'sneaky', 'cunning', 'arrogant', 'righteous', 'ambitious', 'strict', 'competitive', 'responsible', 'lonesome', 'righteous', 'calm', 'gloomy', 'wise', 'thoughtful', 'nervous', 'insecure', 'lonesome', 'troublesome', 'childish', 'playful', 'strange', 'loyal', 'responsible', 'wise', 'faithful', 'compassionate', 'faithful', 'loving', 'oblivious', 'sincere', 'childish', 'confident', 'bold', 'shameless', 'strange', 'oblivious', 'flamboyant', 'troublesome', 'bloodthirsty', 'sneaky', 'rebellious']
        you_trait_list = ['you_troublesome', 'you_fierce', 'you_bold', 'you_daring', 'you_confident', 'you_adventurous', 'you_arrogant', 'you_competitive', 'you_rebellious', 'you_bloodthirsty', 'you_cold', 'you_strict', 'you_vengeful', 'you_grumpy', 'you_charismatic', 'you_sneaky', 'you_cunning', 'you_arrogant', 'you_righteous', 'you_ambitious', 'you_strict', 'you_competitive', 'you_responsible', 'you_lonesome', 'you_righteous', 'you_calm', 'you_gloomy', 'you_wise', 'you_thoughtful', 'you_nervous', 'you_insecure', 'you_lonesome', 'you_troublesome', 'you_childish', 'you_playful', 'you_strange', 'you_loyal', 'you_responsible', 'you_wise', 'you_faithful', 'you_compassionate', 'you_faithful', 'you_loving', 'you_oblivious', 'you_sincere', 'you_childish', 'you_confident', 'you_bold', 'you_shameless', 'you_strange', 'you_oblivious', 'you_flamboyant', 'you_troublesome', 'you_bloodthirsty', 'you_sneaky', 'you_rebellious']
        you_backstory_list = [
            "you_clanfounder",
            "you_clanborn",
            "you_outsiderroots",
            "you_half-Clan",
            "you_formerlyloner",
            "you_formerlyrogue",
            "you_formerlykittypet",
            "you_formerlyoutsider",
            "you_originallyanotherclan",
            "you_orphaned",
            "you_abandoned"
        ]
        they_backstory_list = ["they_clanfounder",
            "they_clanborn",
            "they_outsiderroots",
            "they_half-Clan",
            "they_formerlyloner",
            "they_formerlyrogue",
            "they_formerlykittypet",
            "they_formerlyoutsider",
            "they_originallyanotherclan",
            "they_orphaned",
            "they_abandoned"
        ]
        skill_list = ['teacher', 'hunter', 'fighter', 'runner', 'climber', 'swimmer', 'speaker', 'mediator1', 'clever', 'insightful', 'sense', 'kit', 'story', 'lore', 'camp', 'healer', 'star', 'omen', 'dream', 'clairvoyant', 'prophet', 'ghost', 'explorer', 'tracker', 'artistan', 'guardian', 'tunneler', 'navigator', 'song', 'grace', 'clean', 'innovator', 'comforter', 'matchmaker', 'thinker', 'cooperative', 'scholar', 'time', 'treasure', 'fisher', 'language', 'sleeper']
        you_skill_list = ['you_teacher', 'you_hunter', 'you_fighter', 'you_runner', 'you_climber', 'you_swimmer', 'you_speaker', 'you_mediator1', 'you_clever', 'you_insightful', 'you_sense', 'you_kit', 'you_story', 'you_lore', 'you_camp', 'you_healer', 'you_star', 'you_omen', 'you_dream', 'you_clairvoyant', 'you_prophet', 'you_ghost', 'you_explorer', 'you_tracker', 'you_artistan', 'you_guardian', 'you_tunneler', 'you_navigator', 'you_song', 'you_grace', 'you_clean', 'you_innovator', 'you_comforter', 'you_matchmaker', 'you_thinker', 'you_cooperative', 'you_scholar', 'you_time', 'you_treasure', 'you_fisher', 'you_language', 'you_sleeper']
        for talk_key, talk in possible_texts.items():
            tags = talk[0]
            for i in range(len(tags)):
                tags[i] = tags[i].lower()
                
            if "insult" in tags:
                continue

            # Status tags
            if you.status not in tags and "any" not in tags and "young elder" not in tags and "no_kit" not in tags and "newborn" not in tags:
                continue
            elif "young elder" in tags and cat.status == 'elder' and cat.moons >= 100:
                continue
            elif "no_kit" in tags and you.status in ['kitten', 'newborn']:
                continue
            elif "newborn" in tags and you.moons != 0:
                continue
            
            if "they_grieving" not in tags and "grief stricken" in cat.illnesses:
                continue
            if "they_grieving" in tags and "grief stricken" not in cat.illnesses:
                continue
            
            # Cluster tags
            if any(i in self.get_cluster_list() for i in tags):
                if cluster1 not in tags and cluster2 not in tags:
                    continue
            if any(i in self.get_cluster_list_you() for i in tags):
                if ("you_"+cluster3) not in tags and ("you_"+cluster4) not in tags:
                    continue
            
            # Trait tags
            if any(i in you_trait_list for i in tags):
                ts = you_trait_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                if you.personality.trait not in ts:
                    continue
            if any(i in their_trait_list for i in tags):
                if cat.personality.trait not in tags:
                    continue
                
            # Backstory tags
            if any(i in you_backstory_list for i in tags):
                ts = you_backstory_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                if you.backstory not in ts:
                    continue
            if any(i in they_backstory_list for i in tags):
                ts = they_backstory_list
                for j in range(len(ts)):
                    ts[j] = ts[j][4:]
                if cat.backstory not in ts:
                    continue
                
            # Skill tags
            if any(i in you_skill_list for i in tags):
                ts = you_skill_list
                for j in range(len(ts)):
                    ts[j] = ts[j][3:]
                    ts[j] = ''.join([q for q in ts[j] if not q.isdigit()])
                if (you.skills.primary.path not in ts) or (you.skills.secondary.path not in ts):
                    continue
            if any(i in skill_list for i in tags):
                ts = skill_list
                for j in range(len(ts)):
                    ts[j] = ''.join([q for q in ts[j] if not q.isdigit()])
                if (cat.skills.primary.path not in ts) or (cat.skills.secondary.path not in ts):
                    continue
                
            # Season tags
            if ('leafbare' in talk[0] and game.clan.current_season != 'Leaf-bare') or ('newleaf' in talk[0] and game.clan.current_season != 'Newleaf') or ('leaffall' in talk[0] and game.clan.current_season != 'Leaf-bare') or ('greenleaf' in talk[0] and game.clan.current_season != 'Greenleaf'):
                continue
            
            # Biome tags
            if any(i in ['beach', 'forest', 'plains', 'mountainous', 'wetlands', 'desert'] for i in talk[0]):
                if game.clan.biome.lower() not in talk[0]:
                    continue
                
            # Injuries, grieving and illnesses tags
            
            if "you_pregnant" in tags and "pregnant" not in you.injuries:
                continue
            if "they_pregnant" in tags and "pregnant" not in cat.injuries:
                continue
            
            if "grief stricken" not in you.illnesses and "you_grieving" in tags:
                continue
            
            if any(i in ["you_ill", "you_injured"] for i in tags):
                ill_injured = False

                if you.is_ill() and "you_ill" in tags and "grief stricken" not in you.illnesses:
                    ill_injured = True
                if you.is_injured() and "you_injured" in tags and "pregnant" not in you.injuries:
                    ill_injured = True
                
                if not ill_injured:
                    continue 
            
            if any(i in ["they_ill", "they_injured"] for i in tags):
                ill_injured = False
                
                if cat.is_ill() and "they_ill" in tags and "grief stricken" not in cat.illnesses:
                    ill_injured = True
                if cat.is_injured() and "they_injured" in tags and "pregnant" not in cat.injuries:
                    ill_injured = True

                if not ill_injured:
                    continue 
            
            # Relationships
            # Family tags:
            if any(i in ["half sibling", "siblings_mate", "cousin", "adopted_sibling", "parents_siblings", "from_mentor", "from_your_apprentice", "from_mate", "from_parent", "adopted_parent", "from_kit", "sibling","from_adopted_kit"] for i in tags):
                
                fam = False
                if "from_mentor" in tags:
                    if you.mentor == cat.ID:
                        fam = True
                if "from_your_apprentice" in tags:
                    if cat.mentor == you.ID:
                        fam = True
                if "from_mate" in tags:
                    if cat.ID in you.mate:
                        fam = True   
                if "from_parent" in tags:
                    if you.parent1:
                        if you.parent1 == cat.ID:
                            fam = True
                    if you.parent2:
                        if you.parent2 == cat.ID:
                            fam = True
                if "adopted_parent" in tags:
                    if cat.ID in you.inheritance.get_no_blood_parents():
                        fam = True
                if "from_kit" in tags:
                    if cat.ID in you.inheritance.get_blood_kits():
                        fam = True
                if "from_adopted_kit" in tags:
                    if cat.ID in you.inheritance.get_not_blood_kits():
                        fam = True

                if "sibling" in tags:
                    if cat.ID in you.inheritance.get_siblings():
                        fam = True
                if "half sibling" in tags:
                    c_p1 = cat.parent1
                    if not c_p1:
                        c_p1 = "no_parent1_cat"
                    c_p2 = cat.parent2
                    if not c_p2:
                        c_p2 = "no_parent2_cat"
                    y_p1 = you.parent1
                    if not y_p1:
                        y_p1 = "no_parent1_you"
                    y_p2 = you.parent2
                    if not y_p2:
                        y_p2 = "no_parent2_you"
                    if ((c_p1 == y_p1 or c_p1 == y_p2) or (c_p2 == y_p1 or c_p2 == y_p2)) and not (c_p1 == y_p1 and c_p2 == y_p2) and not (c_p2 == y_p1 and c_p1 == y_p2) and not (c_p1 == y_p2 and c_p2 == y_p1):
                        fam = True
                if "adopted_sibling" in tags:
                    if cat.ID in you.inheritance.get_no_blood_siblings():
                        fam = True
                if "parents_siblings" in tags:
                    if cat.ID in you.inheritance.get_parents_siblings():
                        fam = True
                if "cousin" in tags:
                    if cat.ID in you.inheritance.get_cousins():
                        fam = True
                if "siblings_mate" in tags:
                    if cat.ID in you.inheritance.get_siblings_mates():
                        fam = True
                if not fam:
                    continue
                

            if "non-related" in tags:
                if cat.ID in you.inheritance.all_inheritances:
                    continue
                
            # If you have murdered someone and have been revealed
            if "murder" in talk[0]:
                if game.clan.your_cat.revealed:
                    if game.clan.your_cat.history:
                        if "is_murderer" in game.clan.your_cat.history.murder:
                            if len(game.clan.your_cat.history.murder["is_murderer"]) == 0:
                                continue
                            elif 'accomplices' in game.switches:
                                if cat.ID in game.switches['accomplices']:
                                    continue
                        else:
                            continue
                    else:
                        continue
                else:
                    continue
            
            if "war" in tags:
                if game.clan.war.get("at_war", False):
                    continue
        
            
            # Relationship conditions
            if you.ID in cat.relationships:
                if cat.relationships[you.ID].dislike < 30 and 'hate' in tags:
                    continue
                if cat.relationships[you.ID].romantic_love < 20 and 'romantic_like' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 20 and 'platonic_like' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 50 and 'platonic_love' in tags:
                    continue
                if cat.relationships[you.ID].jealousy < 5 and 'jealousy' in tags:
                    continue
                if cat.relationships[you.ID].dislike < 20 and 'dislike' in tags:
                    continue
                if cat.relationships[you.ID].comfortable < 5 and 'comfort' in tags:
                    continue
                if cat.relationships[you.ID].admiration < 5 and 'respect' in tags:
                    continue         
                if cat.relationships[you.ID].trust < 5 and 'trust' in tags:
                    continue
                if cat.relationships[you.ID].platonic_like < 10 and cat.relationships[you.ID].dislike < 10 and "neutral" in tags:
                    continue
            else:
                if any(i in ["hate","romantic_like","platonic_like","jealousy","dislike","comfort","respect","trust"] for i in tags):
                    continue
            
            if "talk_dead" in talk[0]:
                dead_cat = str(Cat.all_cats.get(choice(game.clan.starclan_cats)).name)
                text = [t1.replace("d_c", dead_cat) for t1 in talk[1]]
            
            if "random_cat" in talk[0]:
                random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
                counter = 0
                while random_cat.outside or random_cat.dead or random_cat.ID == you.ID or random_cat.ID == cat.ID:
                    counter+=1
                    if counter == 15:
                        continue
                    random_cat = Cat.all_cats.get(choice(game.clan.clan_cats))
                text = [t1.replace("r_c", str(random_cat.name)) for t1 in talk[1]]
                texts_list.append(text)
                continue
           
            texts_list.append(talk[1])
            
        if not texts_list:
            resource_dir = "resources/dicts/lifegen_talk/"
            possible_texts = None
            with open(f"{resource_dir}general.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())
            texts_list.append(possible_texts['general'][1])

        text = choice(texts_list)

        if any(abbrev in t for abbrev in ["r_k", "r_a", "r_w", "r_m", "r_d", "r_q", "r_e", "r_s", "r_i"] for t in text):
            living_meds = []
            living_mediators = []
            living_warriors = []
            living_apprentices = []
            living_queens = []
            living_kits = []
            living_elders = []
            sick_cats = []
            injured_cats = []
            
            for c in Cat.all_cats.values():
                if not c.dead and not c.outside and c.ID != you.ID and c.ID != cat.ID:
                    if c.status == "medicine cat":
                        living_meds.append(c)
                    elif c.status == "warrior":
                        living_warriors.append(c)
                    elif c.status == "mediator":
                        living_mediators.append(c)
                    elif c.status == 'queen':
                        living_queens.append(c)
                    elif c.status in ["apprentice", "medicine cat apprentice", "mediator apprentice", "queen's apprentice"]:
                        living_apprentices.append(c)
                    elif c.status in ["kitten", "newborn"]:
                        living_kits.append(c)
                    elif c.status == "elder":
                        living_elders.append(c)

            replace_mappings = {
                "r_k": living_kits,
                "r_a": living_apprentices,
                "r_w": living_warriors,
                "r_m": living_meds,
                "r_d": living_mediators,
                "r_q": living_queens,
                "r_e": living_elders
            }
            
            for abbrev, replace_list in replace_mappings.items():
                for idx, t in enumerate(text):
                    if abbrev in t:
                        text[idx] = t.replace(abbrev, str(choice(replace_list).name))
                        

        text = [t1.replace("c_n", game.clan.name) for t1 in text]
        text = [t1.replace("y_c", str(you.name)) for t1 in text]
        text = [t1.replace("t_c", str(cat.name)) for t1 in text]   
         
        other_clan = choice(game.clan.all_clans)
        if other_clan:
            text = [t1.replace("o_c", str(other_clan.name)) for t1 in text]
        if game.clan.leader:
            lead = game.clan.leader.name
            text = [t1.replace("l_n", str(lead)) for t1 in text]
        if game.clan.deputy:
            dep = game.clan.deputy.name
            text = [t1.replace("d_n", str(dep)) for t1 in text]
        if cat.mentor:
            mentor = Cat.all_cats.get(cat.mentor).name
            text = [t1.replace("tm_n", str(mentor)) for t1 in text]
        if you.mentor:
            mentor = Cat.all_cats.get(you.mentor).name
            text = [t1.replace("m_n", str(mentor)) for t1 in text]
        if "grief stricken" in cat.illnesses:
            try:
                dead_cat = Cat.all_cats.get(cat.illnesses['grief stricken'].get("grief_cat"))
                text = [t1.replace("d_c", str(dead_cat.name)) for t1 in text]  
            except:
                dead_cat = str(Cat.all_cats.get(game.clan.starclan_cats[-1]).name)
                text = [t1.replace("d_c", dead_cat) for t1 in text]    
        elif "grief stricken" in you.illnesses:
            try:
                dead_cat = Cat.all_cats.get(you.illnesses['grief stricken'].get("grief_cat"))
                text = [t1.replace("d_c", str(dead_cat.name)) for t1 in text]  
            except:
                dead_cat = str(Cat.all_cats.get(game.clan.starclan_cats[-1]).name)
                text = [t1.replace("d_c", dead_cat) for t1 in text]
        d_c_found = False
        for t in text:
            if "d_c" in t:
                d_c_found = True
        if d_c_found:
            dead_cat = str(Cat.all_cats.get(game.clan.starclan_cats[-1]).name)
            text = [t1.replace("d_c", dead_cat) for t1 in text]
        return text
        
        
class InsultScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.resource_dir = "resources/dicts/lifegen_talk/"
        self.texts = ""
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]

        self.scroll_container = None
        self.life_text = None
        self.header = None
        self.the_cat = None
        self.text_index = 0
        self.frame_index = 0
        self.typing_delay = 20
        self.next_frame_time = pygame.time.get_ticks() + self.typing_delay
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.text = None
        self.profile_elements = {}
        self.talk_box_img = None


    def screen_switches(self):
        self.update_camp_bg()
        self.hide_menu_buttons()
        self.text_index = 0
        self.frame_index = 0
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.profile_elements = {}
        self.clan_name_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((450, 875), (380, 70))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/clan_name_bg.png").convert_alpha(),
                (500, 870)),
            manager=MANAGER)
        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(str(self.the_cat.name),
                                                                          scale(pygame.Rect((500, 870), (-1, 80))),
                                                                          object_id="#text_box_34_horizcenter_light",
                                                                          manager=MANAGER)
        self.texts = self.get_possible_text(self.the_cat)
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        self.talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()

        self.talk_box = pygame_gui.elements.UIImage(
                scale(pygame.Rect((178, 942), (1248, 302))),
                self.talk_box_img
            )
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                        object_id="#back_button", manager=MANAGER)
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((500, 970), (900, 300))))
        self.text = pygame_gui.elements.UITextBox("", 
                                                  scale(pygame.Rect((0, 0), (900, -100))),
                                                  object_id="#text_box_30_horizleft",
                                                  container=self.scroll_container, manager=MANAGER)
        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((70, 900), (400, 400))),

                                                                         pygame.transform.scale(
                                                                             generate_sprite(self.the_cat),
                                                                             (400, 400)), manager=MANAGER)
        self.paw = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1370, 1180), (30, 30))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
        self.paw.visible = False


    def exit_screen(self):
        self.text.kill()
        del self.text
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button
        self.profile_elements["cat_image"].kill()
        self.profile_elements["cat_name"].kill()
        del self.profile_elements
        self.clan_name_bg.kill()
        del self.clan_name_bg
        self.talk_box.kill()
        del self.talk_box
        self.paw.kill()
        del self.paw

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
            pygame.image.load(all_backgrounds[0]).convert(), (screen_x, screen_y))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (screen_x, screen_y))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (screen_x, screen_y))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (screen_x, screen_y))
    
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
        now = pygame.time.get_ticks()
        if self.text_index < len(self.text_frames):
            if now >= self.next_frame_time and self.frame_index < len(self.text_frames[self.text_index]) - 1:
                self.frame_index += 1
                self.next_frame_time = now + self.typing_delay

        if self.text_index == len(self.text_frames) - 1:
            if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                self.paw.visible = True
        # Always render the current frame
        self.text.html_text = self.text_frames[self.text_index][self.frame_index]
        self.text.rebuild()
        self.clock.tick(60)

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('profile screen')
        elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1  # Go to the last frame
        return
    
    def get_possible_text(self, cat):
        status = cat.status
        trait = cat.personality.trait
        skill = cat.skills
        text = ""
        resource_dir = "resources/dicts/lifegen_talk/"
        possible_texts = None
        with open(f"{resource_dir}{status}.json", 'r') as read_file:
            possible_texts = ujson.loads(read_file.read())
            
        texts_list = []
        for talk in possible_texts.values():
            if "insult" not in talk[0]:
                continue
            if game.clan.your_cat.status not in talk[0] and "Any" not in talk[0]:
                continue
            if ('leafbare' in talk[0] and game.clan.current_season != 'Leaf-bare') or ('newleaf' in talk[0] and game.clan.current_season != 'Newleaf') or ('leaffall' in talk[0] and game.clan.current_season != 'Leaf-bare') or ('greenleaf' in talk[0] and game.clan.current_season != 'Greenleaf'):
                continue
            if any(i in ['bloodthirsty', 'cold', 'childish', 'faithful', 'strict', 'insecure', "nervous", "lonesome", "vengeful", "fierce"] for i in talk[0]):
                if trait not in talk[0]:
                    continue
            if any(i in ['beach', 'forest', 'plains', 'mountainous', 'wetlands'] for i in talk[0]):
                if game.clan.biome not in talk[0]:
                    continue
            if (not game.clan.your_cat.is_ill() and not game.clan.your_cat.is_injured()) and 'injured' in talk[0]:
                continue
            if (game.clan.your_cat.status == 'kitten') and 'no_kit' in talk[0]:
                continue
            if ("you_insecure" in talk[0]) and game.clan.your_cat.personality.trait != "insecure":
                continue
            if "from_mentor" in talk[0]:
                if game.clan.your_cat.mentor != cat.ID:
                    continue
            if "from_parent" in talk[0]:
                if game.clan.your_cat.parent1:
                    if game.clan.your_cat.parent1 != cat.ID:
                        continue
                if game.clan.your_cat.parent2:
                    if game.clan.your_cat.parent2 != cat.ID:
                        continue
            if "newborn" in talk[0]:
                if game.clan.your_cat.moons != 0:
                    continue
            if game.clan.your_cat.ID in cat.relationships:
                if cat.relationships[game.clan.your_cat.ID].dislike < 50 and 'hate' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].romantic_love < 30 and 'romantic_like' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].platonic_like < 30 and 'platonic_like' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].jealousy < 30 and 'jealousy' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].dislike < 30 and 'dislike' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].comfortable < 30 and 'comfort' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].admiration < 30 and 'respect' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].trust < 30 and 'trust' in talk[0]:
                    continue
                if "talk_dead" in talk[0]:
                    dead_cat = str(Cat.all_cats.get(choice(game.clan.starclan_cats)).name)
                    text = [t1.replace("d_c", dead_cat) for t1 in text]
                    texts_list.append(talk[1])
                    continue
                texts_list.append(talk[1])
            else:
                if any(i in ['hate', 'crush', 'romantic_like', 'platonic_like', 'jealousy', 'dislike', 'comfort', 'respect', 'trust'] for i in talk[0]):
                    continue
                if "talk_dead" in talk[0]:
                    dead_cat = str(Cat.all_cats.get(choice(game.clan.starclan_cats)).name)
                    text = [t1.replace("d_c", dead_cat) for t1 in text]
                    texts_list.append(talk[1])
                    continue
                texts_list.append(talk[1])
        if not texts_list:
            resource_dir = "resources/dicts/lifegen_talk/"
            possible_texts = None
            with open(f"{resource_dir}general.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())
            texts_list.append(possible_texts['general'][1])
        
        text = choice(texts_list)
        text = [t1.replace("c_n", game.clan.name) for t1 in text]
        text = [t1.replace("y_c", str(game.clan.your_cat.name)) for t1 in text]
        text = [t1.replace("r_c", str(Cat.all_cats[choice(game.clan.clan_cats)].name)) for t1 in text]

        

        return text

class FlirtScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.resource_dir = "resources/dicts/lifegen_talk/"
        self.texts = ""
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]

        self.scroll_container = None
        self.life_text = None
        self.header = None
        self.the_cat = None
        self.text_index = 0
        self.frame_index = 0
        self.typing_delay = 20
        self.next_frame_time = pygame.time.get_ticks() + self.typing_delay
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.text = None
        self.profile_elements = {}
        self.talk_box_img = None


    def screen_switches(self):
        self.update_camp_bg()
        self.hide_menu_buttons()
        self.text_index = 0
        self.frame_index = 0
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        self.profile_elements = {}
        self.clan_name_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((450, 875), (380, 70))),
            pygame.transform.scale(
                image_cache.load_image(
                    "resources/images/clan_name_bg.png").convert_alpha(),
                (500, 870)),
            manager=MANAGER)
        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(str(self.the_cat.name),
                                                                          scale(pygame.Rect((500, 870), (-1, 80))),
                                                                          object_id="#text_box_34_horizcenter_light",
                                                                          manager=MANAGER)
        self.texts = self.get_possible_text(self.the_cat)
        self.text_frames = [[text[:i+1] for i in range(len(text))] for text in self.texts]
        self.talk_box_img = image_cache.load_image("resources/images/talk_box.png").convert_alpha()

        self.talk_box = pygame_gui.elements.UIImage(
                scale(pygame.Rect((178, 942), (1248, 302))),
                self.talk_box_img
            )
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                        object_id="#back_button", manager=MANAGER)
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((500, 970), (900, 300))))
        self.text = pygame_gui.elements.UITextBox("", 
                                                  scale(pygame.Rect((0, 0), (900, -100))),
                                                  object_id="#text_box_30_horizleft",
                                                  container=self.scroll_container, manager=MANAGER)
        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((70, 900), (400, 400))),

                                                                         pygame.transform.scale(
                                                                             generate_sprite(self.the_cat),
                                                                             (400, 400)), manager=MANAGER)
        self.paw = pygame_gui.elements.UIImage(
                scale(pygame.Rect((1370, 1180), (30, 30))),
                image_cache.load_image("resources/images/cursor.png").convert_alpha()
            )
        self.paw.visible = False


    def exit_screen(self):
        self.text.kill()
        del self.text
        self.scroll_container.kill()
        del self.scroll_container
        self.back_button.kill()
        del self.back_button
        self.profile_elements["cat_image"].kill()
        self.profile_elements["cat_name"].kill()
        del self.profile_elements
        self.clan_name_bg.kill()
        del self.clan_name_bg
        self.talk_box.kill()
        del self.talk_box
        self.paw.kill()
        del self.paw

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
            pygame.image.load(all_backgrounds[0]).convert(), (screen_x, screen_y))
        self.greenleaf_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[1]).convert(), (screen_x, screen_y))
        self.leafbare_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[2]).convert(), (screen_x, screen_y))
        self.leaffall_bg = pygame.transform.scale(
            pygame.image.load(all_backgrounds[3]).convert(), (screen_x, screen_y))
    
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
        now = pygame.time.get_ticks()
        if self.text_index < len(self.text_frames):
            if now >= self.next_frame_time and self.frame_index < len(self.text_frames[self.text_index]) - 1:
                self.frame_index += 1
                self.next_frame_time = now + self.typing_delay

        if self.text_index == len(self.text_frames) - 1:
            if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                self.paw.visible = True
        # Always render the current frame
        self.text.html_text = self.text_frames[self.text_index][self.frame_index]
        self.text.rebuild()
        self.clock.tick(60)

    def handle_event(self, event):
        if game.switches['window_open']:
            pass
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
        
        elif event.type == pygame.KEYDOWN and game.settings['keybinds']:
            if event.key == pygame.K_ESCAPE:
                self.change_screen('profile screen')
        elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.frame_index == len(self.text_frames[self.text_index]) - 1:
                    if self.text_index < len(self.texts) - 1:
                        self.text_index += 1
                        self.frame_index = 0
                else:
                    self.frame_index = len(self.text_frames[self.text_index]) - 1  # Go to the last frame
        return
    
    def get_possible_text(self, cat):
        trait = cat.personality.trait
        cluster, second_cluster = self.get_cluster(trait)
        success = self.is_flirt_success(cat)
        text = ""
        resource_dir = "resources/dicts/lifegen_talk/"
        possible_texts = None
        with open(f"{resource_dir}flirt.json", 'r') as read_file:
            possible_texts = ujson.loads(read_file.read())
            
        texts_list = []
        for talk in possible_texts.values():
            if game.clan.your_cat.status not in talk[0] and "Any" not in talk[0]:
                continue
            if "heartbroken" not in cat.illnesses.keys() and "heartbroken" in talk[0]:
                continue
            elif not success and "reject" not in talk[0]:
                continue
            elif success and "reject" in talk[0]:
                continue
            if talk[0] and (cluster not in talk[0] and second_cluster not in talk[0]):
                if len(talk[0]) != 1 and len(talk[0]) != 2:
                    continue
                else:
                    if len(talk[0]) == 2 and "reject" not in talk[0]:
                        continue
            if "mate" in talk[0] and cat.ID not in game.clan.your_cat.mate:
                continue
            if ('leafbare' in talk[0] and game.clan.current_season != 'Leaf-bare') or ('newleaf' in talk[0] and game.clan.current_season != 'Newleaf') or ('leaffall' in talk[0] and game.clan.current_season != 'Leaf-bare') or ('greenleaf' in talk[0] and game.clan.current_season != 'Greenleaf'):
                continue
            if any(i in ['bloodthirsty', 'cold', 'gloomy', 'childish', 'faithful', 'strict', 'insecure', "nervous", "lonesome", "vengeful", "fierce"] for i in talk[0]):
                if trait not in talk[0]:
                    continue
            if any(i in ['beach', 'forest', 'plains', 'mountainous', 'wetlands'] for i in talk[0]):
                if game.clan.biome not in talk[0]:
                    continue
            if (not game.clan.your_cat.is_ill() and not game.clan.your_cat.is_injured()) and 'injured' in talk[0]:
                continue
            if (game.clan.your_cat.status == 'kitten') and 'no_kit' in talk[0]:
                continue
            if ("you_insecure" in talk[0]) and game.clan.your_cat.personality.trait != "insecure":
                continue
            if game.clan.your_cat.ID in cat.relationships:
                if cat.relationships[game.clan.your_cat.ID].dislike < 50 and 'hate' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].romantic_love < 30 and 'romantic_like' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].platonic_like < 30 and 'platonic_like' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].jealousy < 30 and 'jealousy' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].dislike < 30 and 'dislike' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].comfortable < 30 and 'comfort' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].admiration < 30 and 'respect' in talk[0]:
                    continue
                if cat.relationships[game.clan.your_cat.ID].trust < 30 and 'trust' in talk[0]:
                    continue
                texts_list.append(talk[1])
            else:
                if any(i in ['hate', 'crush', 'romantic_like', 'platonic_like', 'jealousy', 'dislike', 'comfort', 'respect', 'trust'] for i in talk[0]):
                    continue
                if "talk_dead" in talk[0]:
                    dead_cat = str(Cat.all_cats.get(choice(game.clan.starclan_cats)).name)
                    text = [t1.replace("d_c", dead_cat) for t1 in text]
                    texts_list.append(talk[1])
                    continue
                texts_list.append(talk[1])
        if not texts_list:
            resource_dir = "resources/dicts/lifegen_talk/"
            possible_texts = None
            with open(f"{resource_dir}general.json", 'r') as read_file:
                possible_texts = ujson.loads(read_file.read())
            texts_list.append(possible_texts['general'][1])
        
        text = choice(texts_list)
        text = [t1.replace("c_n", game.clan.name) for t1 in text]
        text = [t1.replace("y_c", str(game.clan.your_cat.name)) for t1 in text]
        text = [t1.replace("r_c", str(Cat.all_cats[choice(game.clan.clan_cats)].name)) for t1 in text]
        return text
    
    def get_cluster(self, trait):
        # Mapping traits to their respective clusters
        trait_to_clusters = {
            "assertive": ["troublesome", "fierce", "bold", "daring", "confident", "adventurous", "arrogant", "competitive", "rebellious"],
            "brooding": ["bloodthirsty", "cold", "strict", "vengeful", "grumpy"],
            "cool": ["charismatic", "sneaky", "cunning", "arrogant"],
            "upstanding": ["righteous", "ambitious", "strict", "competitive", "responsible"],
            "introspective": ["lonesome", "righteous", "calm", "gloomy", "wise", "thoughtful"],
            "neurotic": ["nervous", "insecure", "lonesome"],
            "silly": ["troublesome", "childish", "playful", "strange"],
            "stable": ["loyal", "responsible", "wise", "faithful"],
            "sweet": ["compassionate", "faithful", "loving", "oblivious", "sincere"],
            "unabashed": ["childish", "confident", "bold", "shameless", "strange", "oblivious", "flamboyant"],
            "unlawful": ["troublesome", "bloodthirsty", "sneaky", "rebellious"]
        }

        clusters = [key for key, values in trait_to_clusters.items() if trait in values]

        # Assign cluster and second_cluster based on the length of clusters list
        cluster = clusters[0] if clusters else ""
        second_cluster = clusters[1] if len(clusters) > 1 else ""

        return cluster, second_cluster
        
    def is_flirt_success(self, cat):
        cat_relationships = cat.relationships.get(game.clan.your_cat.ID)
        chance = 40
        if cat_relationships:
            if cat_relationships.romantic_love > 10:
                chance += 50
            if cat_relationships.platonic_like > 10:
                chance += 20
            if cat_relationships.comfortable > 10:
                chance += 20
            if cat_relationships.admiration > 10:
                chance += 20
            if cat_relationships.dislike > 10:
                chance -= 30
            r = randint(1,100) < chance
            if r:
                cat.relationships.get(game.clan.your_cat.ID).romantic_love += randint(1,10)
                game.clan.your_cat.relationships.get(cat.ID).romantic_love += randint(1,10)
            return r
        else:
            return False