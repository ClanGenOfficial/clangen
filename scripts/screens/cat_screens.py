#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
from random import choice

import pygame

from ..cat.history import History
from ..housekeeping.datadir import get_save_dir
from ..game_structure.windows import ChangeCatName, SpecifyCatGender, KillCat, SaveAsImage

import ujson

from scripts.utility import event_text_adjust, scale, ACC_DISPLAY, process_text

from .base_screens import Screens

from scripts.utility import get_text_box_theme, scale_dimentions, generate_sprite
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.game_structure import image_cache
import pygame_gui
from re import sub
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
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
    backstory_text = {
        None: "This cat was born into the Clan where they currently reside.",
        'clan_founder': "This cat is one of the founding members of the Clan.",
        'clanborn': "This cat was born into the Clan where they currently reside.",
        'halfclan1': "This cat was born into the Clan, but one of their parents resides in another Clan.",
        'halfclan2': "This cat was born in another Clan, but chose to come to this Clan to be with their other parent.",
        'outsider_roots1': "This cat was born into the Clan, but one of their parents is an outsider that belongs to no Clan.",
        'outsider_roots2': "This cat was born outside the Clan, but came to live in the Clan with their parent at a young age.",
        'loner1': "This cat joined the Clan by choice after living life as a loner.",
        'loner2': "This cat used to live in a barn, but mostly stayed away from Twolegs. They decided clanlife might be an interesting change of pace.",
        'kittypet1': "This cat joined the Clan by choice after living life with Twolegs as a kittypet.",
        'kittypet2': 'This cat used to live on something called a "boat" with Twolegs, but decided to join the Clan.',
        'kittypet3': "This cat used be a kittypet. They got lost after wandering away, and when they returned home, they found their Twolegs were gone. They eventually found their way to the Clan.",
        'kittypet4': "This cat used to be a kittypet. One day, they got sick, and their Twolegs brought them into the belly of a monster. The Twolegs then left them to fend for themselves.",
        'rogue1': "This cat joined the Clan by choice after living life as a rogue.",
        'rogue2': "This cat used to live in a Twolegplace, scrounging for what they could find. They thought the Clan might offer them more security.",
        'rogue3': "This cat used to live alone in their own territory, but was chased out by something and eventually found the Clan.",
        'abandoned1': "This cat was found by the Clan as a kit and has been living with them ever since.",
        'abandoned2': "This cat was born outside of the Clan, but was brought to the Clan as a kit and has lived here ever since.",
        'abandoned3': "This cat was born into another Clan, but they were left here as a kit for the Clan to raise.",
        'abandoned4': "This cat was found and taken in after being abandoned by their Twolegs as a kit.",
        'medicine_cat': "This cat was once a medicine cat in another Clan.",
        'otherclan': "This cat was born into another Clan, but came to this Clan by choice.",
        'otherclan2': "This cat was unhappy in their old Clan and decided to come here instead.",
        'otherclan3': "This cat's Clan stayed with the Clan after a disaster struck their old one, and This cat decided to stay after the rest of their Clan returned home.",
        'ostracized_warrior': "This cat was ostracized from their old Clan, but no one really knows why.",
        'disgraced': "This cat was cast out of their old Clan for some transgression that they're not keen on talking about.",
        'retired_leader': "This cat used to be the leader of another Clan before deciding they needed a change of scenery after leadership became too much. They returned their nine lives and let their deputy take over before coming here.",
        'refugee': "This cat came to this Clan after fleeing from their former Clan and the tyrannical leader that had taken over.",
        'refugee2': "This cat used to live as a loner, but after another cat chased them from their home, they took refuge in the Clan.",
        'refugee3': "This cat used to be a kittypet, but joined the Clan after fleeing from their cruel Twoleg.",
        'refugee4': "This cat used to be in a rogue group, but joined the Clan after fleeing from the group's tyrannical leader.",
        'tragedy_survivor': "Something horrible happened to this cat's previous Clan. They refuse to speak about it.",
        'tragedy_survivor2': "This cat used to be part of a rogue group, but joined the Clan after something terrible happened to it.",
        'tragedy_survivor3': "This cat used to be a kittypet, but joined the Clan after something terrible happened to their Twolegs.",
        'tragedy_survivor4': "This cat used to be a loner, but joined the Clan after something terrible made them leave their old home behind.",
        'orphaned': "This cat was found with a deceased parent. The Clan took them in, but doesn't hide where they came from.",
        'orphaned2': "This cat was found with a deceased parent. The Clan took them in, but doesn't tell them where they really came from.",
        'wandering_healer1': "This cat used to wander, helping those where they could, and eventually found the Clan.",
        'wandering_healer2': "This cat used to live in a specific spot, offering help to all who wandered by, but eventually found their way to the Clan.",
        'guided1': "This cat used to be a kittypet, but after dreaming of starry-furred cats, they followed their whispers to the Clan.",
        'guided2': "This cat used to live a rough life as a rogue. While wandering, they found a set of starry pawprints, and followed them to the Clan.",
        'guided3': "This cat used to live as a loner. A starry-furred cat appeared to them one day, and then led them to the Clan.",
        'guided4': "This cat used to live in a different Clan, until a sign from StarClan told them to leave.",
        'orphaned3': "This cat was found as a kit among the wreckage of a Monster with no parents in sight and got brought to live in the Clan.",
        'orphaned4': "This cat was found as a kit hiding near a place of battle where there were no survivors and got brought to live in the Clan.",
        'orphaned5': "This cat was found as a kit hiding near their parent's bodies and got brought to live in the Clan.",
        'orphaned6': "This cat was found flailing in the ocean as a teeny kitten, no parent in sight.",
        'refugee5': "This cat got washed away from their former territory in a flood that destroyed their home but was glad to find a new home in their new Clan here.",
        'disgraced2': "This cat was exiled from their old Clan for something they didn't do and came here to seek safety.",
        'disgraced3': "This cat once held a high rank in another Clan but was exiled for reasons they refuse to share.",
        'other_clan1': "This cat grew up in another Clan but chose to leave that life and join the Clan they now live in.",
        'outsider': "This cat was born outside of a Clan.",
        'outsider2': "This cat was born outside of a Clan, but at their birth one parent was a member of a Clan.",
        'outsider3': "This cat was born outside of a Clan, while their parent was lost.",
    }
    
    if backstory != None and backstory in backstory_text:
        return backstory_text.get(backstory, "")
    if cat.status in ['kittypet', 'loner', 'rogue', 'former Clancat']:
            return f"This cat is a {cat.status} and currently resides outside of the Clans."
    
    return backstory_text.get(backstory, "")


# ---------------------------------------------------------------------------- #
#             change how backstory info displays on cat profiles               #
# ---------------------------------------------------------------------------- #
def backstory_text(cat):
    backstory = cat.backstory
    if backstory is None:
        return ''
    bs_display = backstory

    backstory_map = {
        'clanborn': 'Clanborn',
        'clan_founder': 'Clan founder',
        'halfclan1': 'half-Clan',
        'halfclan2': 'half-Clan',
        'outsider_roots1': 'outsider roots',
        'outsider_roots2': 'outsider roots',
        'loner1': 'formerly a loner',
        'loner2': 'formerly a loner',
        'refugee2': 'formerly a loner',
        'tragedy_survivor4': 'formerly a loner',
        'guided3': 'formerly a loner',
        'wandering_healer2': 'formerly a loner',
        'kittypet1': 'formerly a kittypet',
        'kittypet2': 'formerly a kittypet',
        'kittypet3': 'formerly a kittypet',
        'kittypet4': 'formerly a kittypet',
        'refugee3': 'formerly a kittypet',
        'tragedy_survivor3': 'formerly a kittypet',
        'guided1': 'formerly a kittypet',
        'rogue1': 'formerly a rogue',
        'rogue2': 'formerly a rogue',
        'rogue3': 'formerly a rogue',
        'refugee4': 'formerly a rogue',
        'tragedy_survivor2': 'formerly a rogue',
        'guided2': 'formerly a rogue',
        'wandering_healer1': 'formerly a rogue',
        'abandoned1': 'formerly abandoned',
        'abandoned2': 'formerly abandoned',
        'abandoned3': 'formerly abandoned',
        'abandoned4': 'formerly abandoned',
        'medicine_cat': 'formerly a medicine cat',
        'otherclan': 'formerly from another Clan',
        'otherclan2': 'formerly from another Clan',
        'otherclan3': 'formerly from another Clan',
        'refugee5': 'formerly from another Clan',
        'other_clan1': 'formerly from another Clan',
        'guided4': 'formerly from another Clan',
        'ostracized_warrior': 'ostracized warrior',
        'disgraced': 'disgraced',
        'disgraced2': 'disgraced',
        'disgraced3': 'disgraced',
        'retired_leader': 'retired leader',
        'refugee': 'refugee',
        'tragedy_survivor': 'survivor of a tragedy',
        'orphaned': 'orphaned',
        'orphaned2': 'orphaned',
        'orphaned3': 'orphaned',
        'orphaned4': 'orphaned',
        'orphaned5': 'orphaned',
        'outsider': 'outsider',
        'outsider2': 'outsider',
        'outsider3': 'outsider',
    }

    if bs_display in backstory_map:
        bs_display = backstory_map[bs_display]

    if bs_display == "disgraced":
        if cat.status == 'medicine cat':
            bs_display = 'disgraced medicine cat'
        elif cat.status in ['warrior', 'elder', "deputy", "leader", "mediator"]:
            bs_display = 'disgraced deputy'
    if bs_display is None:
        bs_display = None
    else:
        return bs_display

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
        self.alert_tool_tip = None
        self.alert_visible = None
        self.alert = None
        self.first_page = None
        self.second_page = None
        self.conditions_tab_button = None
        self.second_page_visible = None
        self.first_page_visible = None
        self.left_arrow = None
        self.right_arrow = None
        self.condition_detail_text = None
        self.condition_name_text = None
        self.condition_box = None
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
            elif event.ui_element == self.relations_tab_button:
                self.toggle_relations_tab()
            elif event.ui_element == self.roles_tab_button:
                self.toggle_roles_tab()
            elif event.ui_element == self.personal_tab_button:
                self.toggle_personal_tab()
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
            elif event.ui_element == self.cis_trans_button:
                if self.the_cat.genderalign != "female" and self.the_cat.genderalign != "male":
                    self.the_cat.genderalign = self.the_cat.gender
                elif self.the_cat.gender == "male" and self.the_cat.genderalign in ['male', 'female']:
                    self.the_cat.genderalign = 'trans female'
                elif self.the_cat.gender == "female" and self.the_cat.genderalign in ['male', 'female']:
                    self.the_cat.genderalign = 'trans male'
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.toggle_kits:
                if self.the_cat.no_kits:
                    self.the_cat.no_kits = False
                else:
                    self.the_cat.no_kits = True
                self.update_disabled_buttons_and_text()
        # Dangerous Tab
        elif self.open_tab == 'dangerous':
            if event.ui_element == self.kill_cat_button:
                KillCat(self.the_cat)
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
            if event.ui_element == self.right_arrow:
                self.first_page_visible = False
                self.second_page_visible = True
                self.left_arrow.enable()
                self.right_arrow.disable()
            if event.ui_element == self.left_arrow:
                self.second_page_visible = False
                self.first_page_visible = True
                self.right_arrow.enable()
                self.left_arrow.disable()

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

        # use these attributes to create differing profiles for starclan cats etc.
        is_sc_instructor = False
        is_df_instructor = False
        if self.the_cat is None:
            return
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID and self.the_cat.df is False:
            is_sc_instructor = True
        elif self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID and self.the_cat.df is True:
            is_df_instructor = True

        # Info in string
        cat_name = str(self.the_cat.name)  # name
        if len(cat_name) >= 40:
            cat_name = f"{cat_name[0:39]}..."
        if self.the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        if is_sc_instructor:
            self.the_cat.thought = "Hello. I am here to guide the dead cats of " + game.clan.name + "Clan into StarClan."
        if is_df_instructor:
            self.the_cat.thought = "Hello. I am here to drag the dead cats of " + game.clan.name + "Clan into the Dark Forest."

        # Write cat name
        self.og_name = self.the_cat.name
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
                                                         object_id="#med_den_button"
                                                         , manager=MANAGER)
        if not (self.the_cat.dead or self.the_cat.outside) and (
                self.the_cat.status in ['medicine cat', 'medicine cat apprentice'] or
                self.the_cat.is_ill() or
                self.the_cat.is_injured()):
            self.profile_elements["med_den"].show()
        else:
            self.profile_elements["med_den"].hide()

        # Fullscreen
        if game.settings['fullscreen']:
            x_pos = 740 - int(name_text_size.width * 7 / 15)
        else:
            x_pos = 740 - name_text_size.width
        # TODO: positioning is weird. closer to names on some, further on others
        # this only happens on fullscreen :waaaaaaa:
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

        if self.the_cat.status == 'leader' and not self.the_cat.dead:
            self.profile_elements["leader_ceremony"] = UIImageButton(scale(pygame.Rect(
                (766, 220), (68, 68))),
                "",
                object_id="#leader_ceremony_button",
                tool_tip_text="Leader Ceremony", manager=MANAGER
            )
        elif self.the_cat.status in ["mediator", "mediator apprentice"]:
            self.profile_elements["mediation"] = UIImageButton(scale(pygame.Rect(
                (766, 220), (68, 68))),
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
        output += "\n"

        # ACCESSORY
        if the_cat.pelt.accessory:
            output += 'accessory: ' + str(ACC_DISPLAY[the_cat.pelt.accessory]["default"])
            # NEWLINE ----------
            output += "\n"

        # PARENTS
        if the_cat.parent1 is None and the_cat.parent2 is None:
            output += 'parents: unknown'
        elif the_cat.parent1 and the_cat.parent2 is None:
            if the_cat.parent1 in Cat.all_cats:
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
            else:
                parent_ob = Cat.load_faded_cat(the_cat.parent1)
                if parent_ob:
                    par1 = str(parent_ob.name)
                else:
                    par1 = "Error: Cat#" + the_cat.parent1 + " not found"

            output += 'parent: ' + par1 + ", unknown"
        else:
            if the_cat.parent1 in Cat.all_cats:
                par1 = str(the_cat.all_cats[the_cat.parent1].name)
            else:
                parent_ob = Cat.load_faded_cat(the_cat.parent1)
                if parent_ob:
                    par1 = str(parent_ob.name)
                else:
                    par1 = "Error: Cat#" + the_cat.parent1 + " not found"

            if the_cat.parent2 in Cat.all_cats:
                par2 = str(the_cat.all_cats[the_cat.parent2].name)
            else:
                parent_ob = Cat.load_faded_cat(the_cat.parent2)
                if parent_ob:
                    par2 = str(parent_ob.name)
                else:
                    par2 = "Error: Cat#" + the_cat.parent2 + " not found"

            output += 'parents: ' + par1 + ' and ' + par2
        # NEWLINE ----------
        output += "\n"

        # MOONS
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
                
            #Get mentorshif text if it exists
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
                        "Then {PRONOUN/m_c/subject} were",
                        "{PRONOUN/m_c/subject/CAP} were also",
                        "Also, {PRONOUN/m_c/subject} were",
                        "As well as",
                        "{PRONOUN/m_c/subject/CAP} were then"
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

    '''def adjust_skill_change_text(self, skill, mentor):
        """
        adjust the skill text as needed.  if a mentor needs to be mentioned, set mentor to True
        """
        adjust_skill = 'this should not appear - skill text adjustments'
        vowels = ['e', 'a', 'i', 'o', 'u']
        skill_paths = SKILLS["paths"]
        skill_grammar_lists = {
            "grow_as": ['dream', 'prophet'],
            "grow_a": ['sense', 'star'],
            "gain_more": ['camp', "ghost"],
            "become": ['clever', 'clairvoyant'],
            "become_a": ['teacher', 'hunter', 'fighter', 'runner', 'climber', 'swimmer', 'speaker', 'mediator',
                         "kit", "story", "lore", "healer", "omen", "prophet"]
        }
        for group in skill_grammar_lists:
            # find which group it is to assign proper text
            if mentor:
                if group == 'grow_as':
                    adjust_skill = 'grow as a '
                elif group == 'grow_a':
                    adjust_skill = 'grow a '
                elif group == 'gain_more':
                    adjust_skill = "gain more skills with {PRONOUN/m_c/poss}"
                elif group == 'become':
                    adjust_skill = "become "
                else:
                    adjust_skill = 'become a '
            else:
                if group == 'grow_as':
                    adjust_skill = 'grew as a '
                elif group == 'grow_a':
                    adjust_skill = 'grew a '
                elif group == 'gain_more':
                    adjust_skill = "gained more skills with {PRONOUN/m_c/poss}"
                elif group == 'become':
                    adjust_skill = "became "
                else:
                    adjust_skill = 'became a '
            # now check if this is the group the skill fits in
            for path in skill_grammar_lists[group]:
                if skill in skill_paths.get(path):
                    adjust_skill += skill
                    # adjust a/an if need be
                    for y in vowels:
                        if 'a' not in adjust_skill:
                            break
                        if skill.startswith(y):
                            adjust_skill = adjust_skill.replace(' a ', ' an ')
                            break
        return adjust_skill'''

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
        elif self.the_cat.status in ['apprentice', 'medicine cat apprentice', 'mediator apprentice']:
            influence_history = 'This cat has not finished training.'
        else:
            valid_formor_mentors = [Cat.fetch_cat(i) for i in self.the_cat.former_mentor if 
                                    isinstance(Cat.fetch_cat(i), Cat)]
            if valid_formor_mentors:
                influence_history += "{PRONOUN/m_c/subject/CAP} was mentored by "
                if len(valid_formor_mentors) > 1:
                    influence_history += ", ".join([str(i.name) for i in valid_formor_mentors[:-1]]) + " and " + \
                        str(valid_formor_mentors[-1].name) + ". "
                else:
                    influence_history += str(valid_formor_mentors[0].name) + ". "
            else:
                influence_history += "This cat either did not have a mentor, or {PRONOUN/m_c/poss} mentor is unknown. "
            
            # Seocnd, do the facet/personality effect
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
        #print(app_ceremony)

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
        

    def get_death_text(self):
        """
        returns adjusted death history text
        """
        text = None
        death_history = History.get_death_or_scars(self.the_cat, death=True)
        murder_history = History.get_murders(self.the_cat)
        if game.switches['show_history_moons']:
            moons = True
        else:
            moons = False

        if death_history:
            all_deaths = []
            for death in death_history:
                if murder_history.get("is_victim"):
                    # TODO: this is gross, try to fix so it's not hella nested, seems like the only solution atm
                    for event in murder_history["is_victim"]:
                        if event["text"] == death["text"] and event["moon"] == death["moon"]:
                            if event["revealed"] is True:
                                text = event_text_adjust(Cat,
                                                         event["text"],
                                                         self.the_cat,
                                                         Cat.fetch_cat(death["involved"]))
                            else:
                                text = event_text_adjust(Cat,
                                                         event["unrevealed_text"],
                                                         self.the_cat,
                                                         Cat.fetch_cat(death["involved"]))
                else:
                    text = event_text_adjust(Cat,
                                             death["text"],
                                             self.the_cat,
                                             Cat.fetch_cat(death["involved"]))
                if moons:
                    text += f" (Moon {death['moon']})"
                all_deaths.append(text)

            death_number = len(all_deaths)

            if self.the_cat.status == 'leader' or death_number > 1:

                if death_number > 2:
                    deaths = f"{', '.join(all_deaths[0:-1])}, and {all_deaths[-1]}"
                elif death_number == 2:
                    deaths = " and ".join(all_deaths)
                else:
                    deaths = all_deaths[0]

                if self.the_cat.dead:
                    insert = ' lost all {PRONOUN/m_c/poss} lives'
                elif game.clan.leader_lives == 8:
                    insert = ' lost a life'
                else:
                    insert = ' lost {PRONOUN/m_c/poss} lives'

                text = str(self.the_cat.name) + insert + " when {PRONOUN/m_c/subject} " + deaths + "."
            else:
                text = all_deaths[0]
            cat_dict = {
                "m_c": (str(self.the_cat.name), choice(self.the_cat.pronouns))
            }
            text = process_text(text, cat_dict)
        return text

    def get_murder_text(self):
        """
        returns adjusted murder history text

        """
        murder_history = History.get_murders(self.the_cat)
        victim_text = ""
        murdered_text = ""

        if game.switches['show_history_moons']:
            moons = True
        else:
            moons = False
        if murder_history:
            if 'is_murderer' in murder_history:
                victims = murder_history["is_murderer"]
            else:
                victims = []

            # if "is_victim" in murder_history:
            #    murderers = murder_history["is_victim"]
            # else:
            #    murderers = []

            if victims:
                victim_names = {}
                name_list = []

                for victim in victims:
                    if not Cat.fetch_cat(victim["victim"]):
                        continue 
                    name = str(Cat.fetch_cat(victim["victim"]).name)

                    if victim["revealed"]:
                        victim_names[name] = []
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

        #print(victim_text)
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
            self.right_arrow = UIImageButton(
                scale(pygame.Rect((1418, 1080), (68, 68))),
                "",
                object_id='#arrow_right_button', manager=MANAGER
            )
            self.left_arrow = UIImageButton(
                scale(pygame.Rect((118, 1080), (68, 68))),
                "",
                object_id='#arrow_left_button'
            )
            self.conditions_background = pygame_gui.elements.UIImage(
                scale(pygame.Rect((178, 942), (1248, 302))),
                self.conditions_tab
            )

            self.first_page_visible = True
            self.first_page = pygame_gui.core.UIContainer(
                scale(pygame.Rect((178, 942), (1248, 302))),
                MANAGER,
                visible=self.first_page_visible)

            # holds next four conditions, displays only once arrow button is hit
            self.second_page_visible = False
            self.second_page = pygame_gui.core.UIContainer(
                scale(pygame.Rect((178, 942), (1248, 302))),
                MANAGER,
                visible=self.second_page_visible)
            # This will be overwritten in update_disabled_buttons_and_text()
            self.update_disabled_buttons_and_text()

    def get_conditions(self):
        self.the_cat = Cat.all_cats.get(game.switches['cat'])

        # tracks the position of the detail boxes
        x_pos = 28

        # tracks the number of boxes so that we don't go out of bounds
        count = 0
        next_injuries = []
        next_illnesses = []

        # holds first four conditions, default display
        self.first_page_visible = True
        self.first_page = pygame_gui.core.UIContainer(
            scale(pygame.Rect((178, 942), (1248, 302))),
            MANAGER,
            visible=self.first_page_visible)
        container = self.first_page

        # holds next four conditions, displays only once arrow button is hit
        self.second_page_visible = False
        self.second_page = pygame_gui.core.UIContainer(
            scale(pygame.Rect((178, 942), (1248, 302))),
            MANAGER,
            visible=self.second_page_visible)

        # check for permanent conditions and create their detail boxes
        if self.the_cat.is_disabled():
            for condition in self.the_cat.permanent_condition:
                if self.the_cat.permanent_condition[condition]['born_with'] is True and \
                        self.the_cat.permanent_condition[condition][
                            "moons_until"] != -2:
                    continue
                # move to second page if count gets too high
                if count < 4 and container != self.second_page:
                    container = self.first_page
                else:
                    container = self.second_page
                    x_pos = 28
                # display the detail box
                self.condition_box = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((x_pos, 25), (280, 276))),
                    self.condition_details_box, manager=MANAGER,
                    container=container)
                # display the detail text
                y_adjust = 60
                # title
                if len(str(condition)) > 17:
                    y_adjust += 38
                self.condition_name_text = UITextBoxTweaked(
                    condition,
                    scale(pygame.Rect((x_pos, 26), (276, -1))),
                    line_spacing=.90,
                    object_id="#text_box_30_horizcenter",
                    container=container, manager=MANAGER
                )
                # details
                text = self.get_condition_details(condition)
                self.condition_detail_text = UITextBoxTweaked(
                    text,
                    scale(pygame.Rect((x_pos, y_adjust), (276, 276))),
                    line_spacing=.90,
                    object_id="#text_box_22_horizcenter_pad_20_20",
                    container=container, manager=MANAGER
                )
                # adjust the x_pos for the next box
                x_pos += 304
                count += 1

        # check for injuries and display their detail boxes
        if self.the_cat.is_injured():
            for injury in self.the_cat.injuries:
                # move to second page if count gets too high
                if count < 4 and container != self.second_page:
                    container = self.first_page
                else:
                    container = self.second_page
                    x_pos = 28
                # display the detail box
                self.condition_box = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((x_pos, 26), (280, 276))),
                    self.condition_details_box,
                    container=container, manager=MANAGER
                )
                # display the detail text
                y_adjust = 60
                # title
                if len(str(injury)) > 17:
                    y_adjust += 38
                self.condition_name_text = UITextBoxTweaked(
                    injury,
                    scale(pygame.Rect((x_pos, 26), (276, -1))),
                    line_spacing=.90,
                    object_id="#text_box_30_horizcenter",
                    container=container, manager=MANAGER
                )
                # details
                text = self.get_condition_details(injury)
                self.condition_detail_text = UITextBoxTweaked(
                    text,
                    scale(pygame.Rect((x_pos, y_adjust), (276, 276))),
                    line_spacing=.90,
                    object_id="#text_box_22_horizcenter_pad_20_20",
                    container=container, manager=MANAGER
                )
                # adjust the x_pos for the next box
                x_pos += 304
                count += 1

        # check for illnesses and display their detail boxes
        if self.the_cat.is_ill():
            for illness in self.the_cat.illnesses:
                # don't display infected or festering as their own condition
                if illness in ['an infected wound', 'a festering wound']:
                    continue
                # move to second page if count gets too high
                if count < 4 and container != self.second_page:
                    container = self.first_page
                else:
                    container = self.second_page
                    x_pos = 28
                # display the detail box
                self.condition_box = pygame_gui.elements.UIImage(
                    scale(pygame.Rect((x_pos, 26), (280, 276))),
                    self.condition_details_box,
                    container=container, manager=MANAGER
                )
                # display the detail text
                y_adjust = 60
                # title
                if len(str(illness)) > 17:
                    y_adjust += 36
                self.condition_name_text = UITextBoxTweaked(
                    illness,
                    scale(pygame.Rect((x_pos, 26), (276, -1))),
                    line_spacing=.90,
                    object_id="#text_box_30_horizcenter",
                    container=container, manager=MANAGER
                )
                # details
                text = self.get_condition_details(illness)
                self.condition_detail_text = UITextBoxTweaked(
                    text,
                    scale(pygame.Rect((x_pos, y_adjust), (276, 276))),
                    line_spacing=.90,
                    object_id="#text_box_22_horizcenter_pad_20_20",
                    container=container, manager=MANAGER
                )
                # adjust the x_pos for the next box
                x_pos += 304
                count += 1

        if count > 4:
            self.right_arrow.enable()

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
                moons_with = self.the_cat.permanent_condition[name].get("moons_with", 1)
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
            if 'moons_with' in keys:  # need to check if it exists for older saves
                moons_with = self.the_cat.injuries[name]["moons_with"]
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
            keys = self.the_cat.illnesses[name].keys()
            if 'moons_with' in keys:  # need to check if it exists for older saves
                moons_with = self.the_cat.illnesses[name]["moons_with"]
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
            else:
                self.see_relationships_button.enable()

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
            if self.the_cat.status not in ['apprentice', 'medicine cat apprentice', 'mediator apprentice'] \
                                            or self.the_cat.dead or self.the_cat.outside:
                self.change_mentor_button.disable()
            else:
                self.change_mentor_button.enable()

        elif self.open_tab == "personal":

            # Button to trans or cis the cats.
            if self.cis_trans_button:
                self.cis_trans_button.kill()
            if self.the_cat.gender == "female" and self.the_cat.genderalign in ['male', 'female']:
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_trans_male_button",
                                                      manager=MANAGER)
            elif self.the_cat.gender == "male" and self.the_cat.genderalign in ['male', 'female']:
                self.cis_trans_button = UIImageButton(scale(pygame.Rect((804, 972), (344, 104))), "",
                                                      starting_height=2, object_id="#change_trans_female_button",
                                                      manager=MANAGER)
            elif self.the_cat.genderalign != "female" and self.the_cat.genderalign != "male":
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
            self.left_arrow.disable()
            self.right_arrow.disable()
            self.first_page.kill()
            self.second_page.kill()
            self.get_conditions()

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

        elif self.open_tab == 'conditions':
            self.first_page.kill()
            self.second_page.kill()
            self.left_arrow.kill()
            self.right_arrow.kill()
            self.conditions_background.kill()

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
                "leafbare": 160 + offset,
                "leaffall": 320 + offset,
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
                self.the_cat.update_traits()
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
                                    tool_tip_text="If a cat is retired, you will be "
                                                  "unable to switch them to warrior status. ",
                                    manager=MANAGER)
        self.switch_med_cat = UIImageButton(scale(pygame.Rect((805, 720), (344, 104))), "",
                                            object_id="#switch_med_cat_button",
                                            manager=MANAGER)
        self.switch_mediator = UIImageButton(scale(pygame.Rect((805, 824), (344, 72))), "",
                                             object_id="#switch_mediator_button",
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
        if len(name) > 17:
            name = name[:14] + "..."
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(scale(pygame.Rect((790, 140), (320, -1))),
                                                                             name,
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
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.enable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.enable()
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
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
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
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "medicine cat":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            # Keep cats that have retired due to health from being switched to warrior
            if self.the_cat.retired or self.the_cat.age == "elder":
                self.switch_warrior.disable()
            else:
                self.switch_warrior.enable()
            self.switch_med_cat.disable()
            self.switch_mediator.enable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "mediator":
            if leader_invalid:
                self.promote_leader.enable()
            else:
                self.promote_leader.disable()

            if deputy_invalid and self.the_cat.age != "elder":
                self.promote_deputy.enable()
            else:
                self.promote_deputy.disable()

            # ADULT CAT ROLES
            # Keep cats that have retired due to health from being switched to warrior
            if self.the_cat.retired or self.the_cat.age == "elder":
                self.switch_warrior.disable()
            else:
                self.switch_warrior.enable()
            self.switch_med_cat.enable()
            self.switch_mediator.disable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "elder":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.enable()
            self.switch_mediator.enable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "medicine cat apprentice":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.enable()
        elif self.the_cat.status == "mediator apprentice":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.enable()
            self.switch_warrior_app.enable()
            self.switch_mediator_app.disable()
        elif self.the_cat.status == "leader":
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            if self.the_cat.age != "elder":
                self.switch_warrior.enable()
            else:
                self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.enable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()
        else:
            self.promote_leader.disable()
            self.promote_deputy.disable()

            # ADULT CAT ROLES
            self.switch_warrior.disable()
            self.switch_med_cat.disable()
            self.switch_mediator.disable()
            self.retire.disable()

            # In-TRAINING ROLES:
            self.switch_med_app.disable()
            self.switch_warrior_app.disable()
            self.switch_mediator_app.disable()

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
        elif self.the_cat.status == "kitten":
            output = f"{self.the_cat.name} is a <b>kitten</b>. All cats below the age of six moons are " \
                     f"considered kits. Kits " \
                     f"are prohibited from leaving camp in order to protect them from the dangers of the wild. " \
                     f"Although they don't have any official duties in the Clan, they are expected to learn the " \
                     f"legends and traditions of their Clan. They are protected by every cat in the Clan and always " \
                     f"eat first. Kit take the suffix \"kit\"."
        elif self.the_cat.status == "newborn":
            output = f"{self.the_cat.name} is a <b>newborn kitten</b>. All cats below the age of six moons are " \
                     f"considered kits. Kits " \
                     f"are prohibited from leaving camp in order to protect them from the dangers of the wild. " \
                     f"Although they don't have any official duties in the Clan, they are expected to learn the " \
                     f"legends and traditions of their Clan. They are protected by every cat in the Clan and always " \
                     f"eat first. Kit take the suffix \"kit\"."
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
        # "young adult", "adult", and "senior adult" all look the same: collape to adult
        # This is not the best way to do it, so if we make them have difference apperences, this will
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
        if len(cat_name) >= 40:
            cat_name = f"{cat_name[0:39]}..."
        if self.the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        
        self.cat_elements["cat_name"] = pygame_gui.elements.UITextBox(cat_name,
                                                                          scale(pygame.Rect((50, 120), (-1, 80))),
                                                                          object_id=get_text_box_theme(
                                                                              "#text_box_40_horizcenter"), manager=MANAGER)
        name_text_size = self.cat_elements["cat_name"].get_relative_rect()

        self.cat_elements["cat_name"].kill()

        self.cat_elements["cat_name"] = pygame_gui.elements.UITextBox(cat_name,
                                                                      scale(pygame.Rect(
                                                                        (800 - name_text_size.width, 120),
                                                                        (name_text_size.width * 2, 80))),
                                                                       object_id=get_text_box_theme(
                                                                        "#text_box_40_horizcenter"), manager=MANAGER)
        
        # Fullscreen
        if game.settings['fullscreen']:
            x_pos = 740 - int(name_text_size.width * 7 / 15)
        else:
            x_pos = 740 - name_text_size.width
        # TODO: positioning is weird. closer to names on some, further on others
        # this only happens on fullscreen :waaaaaaa:
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
            if cat_value_to_allow evalates to False, then the unchecked checkbox is always used the the checkbox 
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
