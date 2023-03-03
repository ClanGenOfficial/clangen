#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
from random import choice

import pygame
try:
    import ujson
except ImportError:
    import json as ujson

from scripts.utility import update_sprite, event_text_adjust, scale

from .base_screens import Screens, cat_profiles

from scripts.utility import get_text_box_theme
from scripts.cat.cats import Cat
from scripts.cat.pelts import collars, wild_accessories
from scripts.game_structure import image_cache
import pygame_gui
from re import sub
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked  # , UIImageTextBox, UISpriteButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from scripts.cat.names import names
from scripts.clan_resources.freshkill import FRESHKILL_ACTIVE


# ---------------------------------------------------------------------------- #
#             change how accessory info displays on cat profiles               #
# ---------------------------------------------------------------------------- #
def accessory_display_name(cat):
    accessory = cat.accessory

    if accessory is None:
        return ''
    acc_display = accessory.lower()

    if accessory in collars:
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

    elif accessory in wild_accessories:
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
    if cat.status in ['kittypet', 'loner', 'rogue']:
        return f"This cat is a {cat.status} and currently resides outside of the Clans."
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
        'refugee5': "This cat got washed away from their former territory in a flood that destroyed their home but was glad to find a new home in their new Clan here.",
        'disgraced2': "This cat was exiled from their old Clan for something they didn't do and came here to seek safety.",
        'disgraced3': "This cat once held a high rank in another Clan but was exiled for reasons they refuse to share.",
        'other_clan1': "This cat grew up in another Clan but chose to leave that life and join the Clan they now live in."
        
    }
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
        'clanborn': 'clanborn',
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
        'refugee3': 'formerly a kittypet',
        'tragedy_survivor3': 'formerly a kittypet',
        'guided1': 'formerly a kittypet',
        'rogue1': 'formerly a rogue',
        'rogue2': 'formerly a rogue',
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
        'orphaned5': 'orphaned'
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
            if event.ui_element == self.back_button:
                self.close_current_tab()
                self.change_screen(game.last_screen_forProfile)
            elif event.ui_element == self.previous_cat_button:
                self.clear_profile()
                game.switches['cat'] = self.previous_cat
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.next_cat_button:
                self.clear_profile()
                game.switches['cat'] = self.next_cat
                self.build_profile()
                self.update_disabled_buttons_and_text()
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
                    if game.settings['favorite sub tab'] is None:
                        self.open_sub_tab = 'life events'
                    else:
                        self.open_sub_tab = game.settings['favorite sub tab']

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
            else:
                self.handle_tab_events(event)

            if self.the_cat.dead and game.settings["fading"]:
                if event.ui_element == self.checkboxes["prevent_fading"]:
                    if self.the_cat.prevent_fading:
                        self.the_cat.prevent_fading = False
                    else:
                        self.the_cat.prevent_fading = True
                    update_sprite(self.the_cat)  # This will remove the transparency on the cat.
                    self.clear_profile()
                    self.build_profile()

    def handle_tab_events(self, event):
        # Relations Tab
        if self.open_tab == 'relations':
            if event.ui_element == self.see_family_button:
                self.change_screen('see kits screen')
            elif event.ui_element == self.see_relationships_button:
                self.change_screen('relationship screen')
            elif event.ui_element == self.choose_mate_button:
                self.change_screen('choose mate screen')
            elif event.ui_element == self.change_mentor_button:
                self.change_screen('choose mentor screen')
        # Roles Tab
        elif self.open_tab == 'roles':
            if event.ui_element == self.manage_roles:
                self.change_screen('role screen')
        # Personal Tab
        elif self.open_tab == 'personal':
            if event.ui_element == self.change_name_button:
                self.change_screen('change name screen')
            elif event.ui_element == self.specify_gender_button:
                self.change_screen('change gender screen')
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
                if self.the_cat.status == 'leader':
                    game.clan.leader_lives -= 10
                self.the_cat.die()
                update_sprite(self.the_cat)
                self.clear_profile()
                self.build_profile()
                self.update_disabled_buttons_and_text()
            elif event.ui_element == self.exile_cat_button:
                if not self.the_cat.dead and not self.the_cat.exiled:
                    self.the_cat.exiled = True
                    self.the_cat.outside = True
                    self.the_cat.thought = "Is shocked that they have been exiled"
                    for app in self.the_cat.apprentice:
                        Cat.fetch_cat(app).update_mentor()
                    self.the_cat.update_mentor()
                    self.clear_profile()
                    self.build_profile()
                    self.update_disabled_buttons_and_text()
                if self.the_cat.dead:
                    if self.the_cat.df is True:
                        self.the_cat.df = False
                        game.clan.add_to_starclan(self.the_cat)
                        self.the_cat.thought = "Is relieved to once again hunt in StarClan"
                    else:
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
                game.settings['favorite sub tab'] = None
                self.fav_tab.hide()
                self.not_fav_tab.show()
            elif event.ui_element == self.not_fav_tab:
                game.settings['favorite sub tab'] = self.open_sub_tab
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
        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "", object_id="#previous_cat_button"
                                                 , manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 120), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.relations_tab_button = UIImageButton(scale(pygame.Rect((96, 840), (352, 60))), "",
                                                  object_id="#relations_tab_button", manager=MANAGER)
        self.roles_tab_button = UIImageButton(scale(pygame.Rect((448, 840), (352, 60))), "", object_id="#roles_tab_button"
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
        cat_profiles()
        self.update_platform()
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
        if self.the_cat.dead:
            cat_name += " (dead)"  # A dead cat will have the (dead) sign next to their name
        if is_sc_instructor:
            self.the_cat.thought = "Hello. I am here to guide the dead cats of " + game.clan.name + "Clan into StarClan."
        if is_df_instructor:
            self.the_cat.thought = "Hello. I am here to drag the dead cats of " + game.clan.name + "Clan into the Dark Forest."

        # Write cat name
        self.profile_elements["cat_name"] = pygame_gui.elements.UITextBox(cat_name, scale(pygame.Rect((50, 280), (1500, 80))),
                                                                          object_id=get_text_box_theme(
                                                                              "#cat_profile_name_box"), manager=MANAGER)

        # Write cat thought
        self.profile_elements["cat_thought"] = pygame_gui.elements.UITextBox(self.the_cat.thought,
                                                                             scale(pygame.Rect((200, 340), (1200, 80))),
                                                                             wrap_to_height=True,
                                                                             object_id=get_text_box_theme(
                                                                                 "#cat_profile_thoughts_box")
                                                                             , manager=MANAGER)

        self.profile_elements["cat_info_column1"] = UITextBoxTweaked(self.generate_column1(self.the_cat),
                                                                     scale(pygame.Rect((600, 460), (360, 360))),
                                                                     object_id=get_text_box_theme(
                                                                         "#cat_profile_info_box"),
                                                                     line_spacing=0.95, manager=MANAGER)
        self.profile_elements["cat_info_column2"] = UITextBoxTweaked(self.generate_column2(self.the_cat),
                                                                     scale(pygame.Rect((980, 460), (460, 360))),
                                                                     object_id=get_text_box_theme(
                                                                         "#cat_profile_info_box"),
                                                                     line_spacing=0.95, manager=MANAGER)

        # Set the cat backgrounds.
        self.update_platform()
        if game.settings['backgrounds']:
            if game.clan.current_season == 'Newleaf':
                self.profile_elements["background"] = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 400), (480, 420))),
                                                                                  self.newleaf_plt, manager=MANAGER)
                self.profile_elements["background"].disable()
            elif game.clan.current_season == 'Greenleaf':
                self.profile_elements["background"] = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 400), (480, 420))),
                                                                                  self.greenleaf_plt, manager=MANAGER)
                self.profile_elements["background"].disable()
            elif game.clan.current_season == 'Leaf-bare':
                self.profile_elements["background"] = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 400), (480, 420))),
                                                                                  self.leafbare_plt, manager=MANAGER)
                self.profile_elements["background"].disable()
            elif game.clan.current_season == 'Leaf-fall':
                self.profile_elements["background"] = pygame_gui.elements.UIImage(scale(pygame.Rect((110, 400), (480, 420))),
                                                                                  self.leaffall_plt, manager=MANAGER)
                self.profile_elements["background"].disable()

        # Create cat image object
        self.profile_elements["cat_image"] = pygame_gui.elements.UIImage(scale(pygame.Rect((200, 400), (300, 300))),
                                                                         pygame.transform.scale(
                                                                             self.the_cat.large_sprite,
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
                    object_id=get_text_box_theme("#cat_profile_info_box"), manager=MANAGER)
            elif is_df_instructor:
                self.profile_elements["prevent_fading_text"] = pygame_gui.elements.UILabel(
                    scale(pygame.Rect((160, 780), (-1, 60))),
                    "The Dark Forest Guide will never fade",
                    object_id=get_text_box_theme("#cat_profile_info_box"), manager=MANAGER)
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
        elif the_cat.age == 'elder':
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
        output += 'accessory: ' + str(accessory_display_name(the_cat))
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
        if the_cat.mate is not None and not the_cat.dead:
            # NEWLINE ----------
            output += "\n"
            if the_cat.mate in Cat.all_cats:
                if Cat.all_cats.get(
                        the_cat.mate
                ).dead:
                    output += 'former mate: ' + str(Cat.all_cats[the_cat.mate].name)
                else:
                    output += 'mate: ' + str(Cat.all_cats[the_cat.mate].name)
            else:
                output += 'Error: mate: ' + str(the_cat.mate) + " not found"

        if not the_cat.dead:
            # NEWLINE ----------
            output += "\n"

        return output

    def generate_column2(self, the_cat):
        """Generate the right column information"""
        output = ""

        # STATUS
        if the_cat.outside and not the_cat.exiled and not the_cat.status in ['kittypet', 'loner', 'rogue']:
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
            output += "mentor: " + str(mentor_ob.name) + "\n"

        # CURRENT APPRENTICES
        # Optional - only shows up if the cat has an apprentice currently
        if the_cat.apprentice:
            app_count = len(the_cat.apprentice)
            if app_count == 1:
                output += 'apprentice: ' + str(Cat.fetch_cat(the_cat.apprentice[0]).name)
            elif app_count > 1:
                output += 'apprentice: ' + ", ".join([str(Cat.fetch_cat(i).name) for i in the_cat.apprentice])

            # NEWLINE ----------
            output += "\n"

        # FORMER APPRENTICES
        # Optional - Only shows up if the cat has previous apprentice(s)
        if len(the_cat.former_apprentices
               ) != 0 and the_cat.former_apprentices[0] is not None:

            if len(the_cat.former_apprentices) == 1:
                output += 'former apprentice: ' + str(
                    Cat.fetch_cat(the_cat.former_apprentices[0]).name)

            elif len(the_cat.former_apprentices) > 1:
                output += 'former apprentices: ' + ", ".join(
                    [str(Cat.fetch_cat(i).name) for i in the_cat.former_apprentices])

            # NEWLINE ----------
            output += "\n"

        # CHARACTER TRAIT
        output += the_cat.trait
        # NEWLINE ----------
        output += "\n"

        # SPECIAL SKILL
        output += the_cat.skill
        # NEWLINE ----------
        output += "\n"

        # EXPERIENCE
        output += 'experience: ' + str(the_cat.experience_level)
        # NEWLINE ----------
        output += "\n"

        # BACKSTORY
        if the_cat.status in ['kittypet', 'loner', 'rogue']:
            output += 'backstory: ' + the_cat.status
        elif the_cat.backstory is not None:
            bs_text = backstory_text(the_cat)
            output += 'backstory: ' + bs_text
        else:
            output += 'backstory: ' + 'clanborn'

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
                tool_tip_text='un-favorite this tab', manager=MANAGER
            )
            self.not_fav_tab = UIImageButton(
                scale(pygame.Rect((105, 960), (56, 56))),
                "",
                object_id="#not_fav_star",
                tool_tip_text='favorite this tab', manager=MANAGER
            )

            if self.open_sub_tab != 'life events':
                self.toggle_history_sub_tab()
            else:
                # This will be overwritten in update_disabled_buttons_and_text()
                self.history_text_box = pygame_gui.elements.UITextBox("", scale(pygame.Rect((80, 480), (615, 142)))
                                                                      , manager=MANAGER)
                self.update_disabled_buttons_and_text()

    def toggle_user_notes_tab(self):
        """Opens the User Notes portion of the History Tab"""
        self.load_user_notes()
        if self.user_notes is None:
            self.user_notes = 'Click the check mark to enter notes about your cat!'

        self.notes_entry = pygame_gui.elements.UITextEntryBox(
            scale(pygame.Rect((200, 946), (1200, 298))),
            initial_text=self.user_notes,
            object_id='#history_tab_text_box', manager=MANAGER
        )

        self.display_notes = UITextBoxTweaked(self.user_notes,
                                              scale(pygame.Rect((200, 946), (120, 298))),
                                              object_id="#history_tab_text_box",
                                              line_spacing=1, manager=MANAGER)

        self.update_disabled_buttons_and_text()

    def save_user_notes(self):
        """Saves user-entered notes. """
        clanname = game.clan.name

        notes = self.user_notes

        notes_directory = 'saves/' + clanname + '/notes'
        notes_file_path = notes_directory + '/' + self.the_cat.ID + '_notes.json'

        if not os.path.exists(notes_directory):
            os.makedirs(notes_directory)

        if notes is None or notes == 'Click the check mark to enter notes about your cat!':
            return

        new_notes = {str(self.the_cat.ID): notes}

        try:
            with open(notes_file_path, 'w') as rel_file:
                json_string = ujson.dumps(new_notes, indent=2)
                rel_file.write(json_string)

        except:
            print(f"WARNING: Saving notes of cat #{self.the_cat.ID} didn't work.")

    def load_user_notes(self):
        """Loads user-entered notes. """
        clanname = game.clan.name

        notes_directory = 'saves/' + clanname + '/notes'
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
            life_history = [str(self.get_backstory_text())]
            body_history = []

            # now get mentor influence history and add that if any exists
            influence_history = self.get_influence_text()
            if influence_history:
                life_history.append(str(influence_history))

            # now go get the scar history and add that if any exists
            scar_history = self.get_scar_text()
            if scar_history:
                body_history.append(str(scar_history))

            if self.the_cat.dead or (self.the_cat.status == 'leader' and game.clan.leader_lives < 9):
                death_history = self.get_death_text()
                if death_history:
                    body_history.append(str(death_history))
                else:
                    body_history.append(f"The cause of {self.the_cat.name}'s death is unknown.")

            # join scar and death into one paragraph
            if body_history:
                life_history.append(" ".join(body_history))

            # join together history list with line breaks
            output = '\n\n'.join(life_history)
        return output

    def get_backstory_text(self):
        text = None
        bs_blurb = bs_blurb_text(self.the_cat)
        if bs_blurb is not None:
            adjust_text = str(bs_blurb).replace('This cat', str(self.the_cat.name))
            text = adjust_text
        else:
            text = f"{self.the_cat.name} was born into the Clan where they currently reside."
        return text

    def get_scar_text(self):
        scar_history = None

        if self.the_cat.scar_event:
            scar_text = self.the_cat.scar_event
            for x in range(len(self.the_cat.scar_event)):
                # first event in the list will keep the cat's name, so we don't want to permanently change the text in
                # the save else the name end up different later in the cat's life
                if x == 0:
                    scar_text[x] = event_text_adjust(Cat, self.the_cat.scar_event[x], self.the_cat)
                # however, for all other events we want to permanently alter the saved text as none of these events will
                # use the cat's name, rather they'll use one of the provided sentence beginners.  We don't want this
                # sentence beginning to change everytime this text is pulled, so we need to make it permanent.
                else:
                    self.the_cat.scar_event[x] = event_text_adjust(Cat, self.the_cat.scar_event[x], self.the_cat)

                sentence_beginners = [
                    "This cat",
                    "Then they",
                    "They also"
                ]

                # first event needs no adjustments, as it's keeping the cat's name. all other events are adjusted.
                if x != 0:
                    chosen = choice(sentence_beginners)
                    self.the_cat.scar_event[x] = str(self.the_cat.scar_event[x]).replace(f'{self.the_cat.name}',
                                                                                         chosen, 1)
                    if chosen != 'This cat':
                        self.the_cat.scar_event[x] = str(self.the_cat.scar_event[x]).replace(f' was ', ' were ', 1)
                    scar_text[x] = self.the_cat.scar_event[x]
            scar_history = ' '.join(scar_text)

        return scar_history

    def get_influence_text(self):
        influence_history = None
        if self.the_cat.status in ['kittypet', 'loner', 'rogue']:
            return ""
        # check if cat has any mentor influence, else assign None
        if len(self.the_cat.mentor_influence) >= 1:
            influenced_trait = str(self.the_cat.mentor_influence[0])
            if len(self.the_cat.mentor_influence) >= 2:
                influenced_skill = str(self.the_cat.mentor_influence[1])
            else:
                influenced_skill = None
        else:
            game.switches['sub_tab_group'] = 'life sub tab'
            influenced_trait = None
            influenced_skill = None

        # if they did have mentor influence, check if skill or trait influence actually happened and assign None
        if influenced_skill in ['None', 'none']:
            influenced_skill = None
        if influenced_trait in ['None', 'none']:
            influenced_trait = None

        # if cat had mentor influence then write history text for those influences and append to history
        # assign proper grammar to skills
        vowels = ['e', 'a', 'i', 'o', 'u']
        if influenced_skill in Cat.skill_groups.get('special'):
            adjust_skill = f'unlock their abilities as a {influenced_skill}'
            for y in vowels:
                if influenced_skill.startswith(y):
                    adjust_skill = adjust_skill.replace(' a ', ' an ')
                    break
            influenced_skill = adjust_skill
        elif influenced_skill in Cat.skill_groups.get('star'):
            adjust_skill = f'grow a {influenced_skill}'
            influenced_skill = adjust_skill
        elif influenced_skill in Cat.skill_groups.get('smart'):
            adjust_skill = f'become {influenced_skill}'
            influenced_skill = adjust_skill
        else:
            # for loop to assign proper grammar to all these groups
            become_group = ['heal', 'teach', 'mediate', 'hunt', 'fight', 'speak']
            for x in become_group:
                if influenced_skill in Cat.skill_groups.get(x):
                    adjust_skill = f'become a {influenced_skill}'
                    for y in vowels:
                        if influenced_skill.startswith(y):
                            adjust_skill = adjust_skill.replace(' a ', ' an ')
                            break
                    influenced_skill = adjust_skill
                    break
        if self.the_cat.former_mentor:
            former_mentor_ob = Cat.fetch_cat(self.the_cat.former_mentor[-1])
            mentor = former_mentor_ob.name
        else:
            mentor = None

        # append influence blurb to history
        if mentor is None:
            influence_history = "This cat either did not have a mentor, or their mentor is unknown."
            if self.the_cat.status == 'kitten':
                influence_history = 'This cat has not begun training.'
            if self.the_cat.status in ['apprentice', 'medicine cat apprentice']:
                influence_history = 'This cat has not finished training.'
        elif influenced_skill is not None and influenced_trait is None:
            influence_history = f"The influence of their mentor, {mentor}, caused this cat to {influenced_skill}."
        elif influenced_skill is None and influenced_trait is not None:
            if influenced_trait in ['Outgoing', 'Benevolent', 'Abrasive', 'Reserved']:
                influence_history = f"The influence of their mentor, {mentor}, caused this cat to become more {influenced_trait.lower()}."
            else:
                influence_history = f"This cat's mentor was {mentor}."
        elif influenced_trait is not None and influenced_skill is not None:
            influence_history = f"The influence of their mentor, {mentor}, caused this cat to become more {influenced_trait.lower()} as well as {influenced_skill}."
        else:
            influence_history = f"This cat's mentor was {mentor}."

        return influence_history

    def get_death_text(self):
        text = None
        if self.the_cat.died_by:
            if self.the_cat.status == 'leader':
                insert2 = f"lost their lives"
                if len(self.the_cat.died_by) > 2:
                    insert = f"{', '.join(self.the_cat.died_by[0:-1])}, and {self.the_cat.died_by[-1]}"
                elif len(self.the_cat.died_by) == 2:
                    insert = f"{self.the_cat.died_by[0]} and {self.the_cat.died_by[1]}"
                else:
                    insert = f"{self.the_cat.died_by[0]}"
                    if self.the_cat.dead:
                        insert2 = f'lost all their lives'
                    elif game.clan.leader_lives == 8:
                        insert2 = f"lost a life"
                    else:
                        insert2 = f"lost lives"
                text = f"{self.the_cat.name} {insert2} when they {insert}."
            else:
                text = str(self.the_cat.died_by[0]).replace(f"{self.the_cat.name} was", 'They were')
        return text

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
                    object_id="text_box",
                    container=container, manager=MANAGER
                )
                # details
                text = self.get_condition_details(condition)
                self.condition_detail_text = UITextBoxTweaked(
                    text,
                    scale(pygame.Rect((x_pos, y_adjust), (276, 276))),
                    line_spacing=.90,
                    object_id="#condition_details_text_box",
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
                    object_id="text_box",
                    container=container, manager=MANAGER
                )
                # details
                text = self.get_condition_details(injury)
                self.condition_detail_text = UITextBoxTweaked(
                    text,
                    scale(pygame.Rect((x_pos, y_adjust), (276, 276))),
                    line_spacing=.90,
                    object_id="#condition_details_text_box",
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
                    object_id="text_box",
                    container=container, manager=MANAGER
                )
                # details
                text = self.get_condition_details(illness)
                self.condition_detail_text = UITextBoxTweaked(
                    text,
                    scale(pygame.Rect((x_pos, y_adjust), (276, 276))),
                    line_spacing=.90,
                    object_id="#condition_details_text_box",
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
                text_list.append("They can't work with this condition")

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
                text_list.append("They can't work with this condition")

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
            self.see_family_button = UIImageButton(scale(pygame.Rect((100, 900), (344, 72))), "",
                                                   starting_height=2, object_id="#see_family_button", manager=MANAGER)
            self.see_relationships_button = UIImageButton(scale(pygame.Rect((100, 972), (344, 72))), "",
                                                          starting_height=2, object_id="#see_relationships_button"
                                                          , manager=MANAGER)
            self.choose_mate_button = UIImageButton(scale(pygame.Rect((100, 1044), (344, 72))), "",
                                                    starting_height=2, object_id="#choose_mate_button", manager=MANAGER)
            self.change_mentor_button = UIImageButton(scale(pygame.Rect((100, 1116), (344, 72))), "",
                                                      starting_height=2, object_id="#change_mentor_button"
                                                      , manager=MANAGER)
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
                tool_tip_text='This cannot be reversed.',
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

            if self.the_cat.age not in ['young adult', 'adult', 'senior adult', 'elder'
                                        ] or self.the_cat.dead or self.the_cat.exiled or self.the_cat.outside:
                self.choose_mate_button.disable()
            else:
                self.choose_mate_button.enable()

            if self.the_cat.status not in ['apprentice', 'medicine cat apprentice',
                                           'mediator apprentice'] or self.the_cat.dead \
                    or self.the_cat.outside:
                self.change_mentor_button.disable()
            else:
                self.change_mentor_button.enable()
        # Roles Tab
        elif self.open_tab == 'roles':
            if self.the_cat.dead or self.the_cat.outside:
                self.manage_roles.disable()
            else:
                self.manage_roles.enable()


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
            if self.the_cat.age in ['young adult', 'adult', 'senior adult', 'elder'] and not self.the_cat.dead:
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

            if not self.the_cat.dead and not self.the_cat.exiled and not self.the_cat.outside:
                self.kill_cat_button.enable()
            else:
                self.kill_cat_button.disable()
        # History Tab:
        elif self.open_tab == 'history':
            # show/hide fav tab star
            if self.open_sub_tab == game.settings['favorite sub tab']:
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
                                                         object_id="#history_tab_text_box",
                                                         line_spacing=1, manager=MANAGER)
            elif self.open_sub_tab == 'user notes':
                self.sub_tab_1.enable()
                self.sub_tab_2.disable()
                if self.history_text_box:
                    self.history_text_box.kill()
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
                        object_id='#history_tab_entry_box', manager=MANAGER
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
                                                          object_id="#history_tab_text_box",
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
            self.see_family_button.kill()
            self.see_relationships_button.kill()
            self.choose_mate_button.kill()
            self.change_mentor_button.kill()
        elif self.open_tab == 'roles':
            self.manage_roles.kill()
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
    def update_platform(self):
        the_cat = Cat.all_cats.get(game.switches['cat'],
                                   game.clan.instructor)

        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        platform_base_dir = 'resources/images/platforms/'
        leaves = ["newleaf", "greenleaf", "leafbare", "leaffall"]

        available_biome = ['Forest', 'Mountainous', 'Plains', 'Beach']
        biome = game.clan.biome

        if biome not in available_biome:
            biome = available_biome[0]

        biome = biome.lower()

        all_platforms = []
        if the_cat.df:
            dead_platform = [f'{platform_base_dir}darkforestplatform_{light_dark}.png']
            all_platforms = dead_platform * 4
        elif the_cat.dead or game.clan.instructor.ID == the_cat.ID:
            dead_platform = [f'{platform_base_dir}/starclanplatform_{light_dark}.png']
            all_platforms = dead_platform * 4
        else:
            for leaf in leaves:
                platform_dir = f'{platform_base_dir}/{biome}/{leaf}_{light_dark}.png'
                all_platforms.append(platform_dir)

        self.newleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[0]).convert_alpha(), (240, 210))
        self.greenleaf_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[1]).convert_alpha(), (240, 210))
        self.leafbare_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[2]).convert_alpha(), (240, 210))
        self.leaffall_plt = pygame.transform.scale(
            pygame.image.load(all_platforms[3]).convert_alpha(), (240, 210))

    def on_use(self):
        pass


# ---------------------------------------------------------------------------- #
#                             change name screen                               #
# ---------------------------------------------------------------------------- #
class ChangeNameScreen(Screens):
    the_cat = ''

    def screen_switches(self):
        self.hide_menu_buttons()

        self.the_cat = Cat.all_cats.get(game.switches['cat'])

        self.heading = pygame_gui.elements.UITextBox("-Change Name-", scale(pygame.Rect((200, 260), (1200, 80))),
                                                     object_id=get_text_box_theme(), manager=MANAGER)

        self.name_changed = pygame_gui.elements.UITextBox("Name Changed!", scale(pygame.Rect((200, 700), (1200, 80))),
                                                          visible=False,
                                                          object_id=get_text_box_theme(), manager=MANAGER)

        self.done_button = UIImageButton(scale(pygame.Rect((730, 564), (154, 60))), "",
                                         object_id="#done_button", manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                         object_id="#back_button", manager=MANAGER)

        self.prefix_entry_box = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((440, 400), (360, 60))),
                                                                    placeholder_text=self.the_cat.name.prefix
                                                                    , manager=MANAGER)
        if self.the_cat.name.status in ["apprentice", "leader", "medicine cat apprentice", "kitten"]:
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((800, 400), (360, 60))),
                                                                        placeholder_text=
                                                                        self.the_cat.name.special_suffixes[
                                                                            self.the_cat.name.status]
                                                                        , manager=MANAGER)
            self.suffix_entry_box.disable()  # You can't change a special suffix
        elif self.the_cat.name.status in ['kittypet', 'loner', 'rogue']:
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((800, 400), (360, 60))),
                                                                        placeholder_text=
                                                                        ""
                                                                        , manager=MANAGER)
            self.suffix_entry_box.disable()  # You can't change a special suffix
        else:
            self.suffix_entry_box = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((800, 400), (360, 60))),
                                                                        placeholder_text=self.the_cat.name.suffix
                                                                        , manager=MANAGER)

    def exit_screen(self):
        self.prefix_entry_box.kill()
        del self.prefix_entry_box
        self.suffix_entry_box.kill()
        del self.suffix_entry_box
        self.done_button.kill()
        del self.done_button
        self.back_button.kill()
        del self.back_button
        self.heading.kill()
        del self.heading
        self.name_changed.kill()
        del self.name_changed

    def on_use(self):
        pass

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                if sub(r'[^A-Za-z0-9 ]+', '', self.prefix_entry_box.get_text()) != '':
                    self.the_cat.name.prefix = sub(r'[^A-Za-z0-9 ]+', '', self.prefix_entry_box.get_text())
                    self.name_changed.show()
                if sub(r'[^A-Za-z0-9 ]+', '', self.suffix_entry_box.get_text()) != '':
                    self.the_cat.name.suffix = sub(r'[^A-Za-z0-9 ]+', '', self.suffix_entry_box.get_text())
                    self.name_changed.show()
            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')


# ---------------------------------------------------------------------------- #
#                           change gender screen                               #
# ---------------------------------------------------------------------------- #
class ChangeGenderScreen(Screens):

    def screen_switches(self):
        self.hide_menu_buttons()

        self.header = pygame_gui.elements.UITextBox("-Change Gender-\nYou can set this to anything. "
                                                    "Gender alignment does not effect gameplay. ",
                                                    scale(pygame.Rect((200, 260), (1200, -1))),
                                                    object_id=get_text_box_theme(), manager=MANAGER)
        self.gender_changed = pygame_gui.elements.UITextBox("Gender Changed!",
                                                            scale(pygame.Rect((200, 480), (1200, 80))),
                                                            object_id=get_text_box_theme(),
                                                            visible=False, manager=MANAGER)
        self.the_cat = Cat.all_cats.get(game.switches['cat'])

        self.done_button = UIImageButton(scale(pygame.Rect((730, 564), (154, 70))), "",
                                         object_id="#done_button", manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                         object_id="#back_button", manager=MANAGER)

        self.gender_entry_box = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((600, 400), (400, 60))),
                                                                    placeholder_text=self.the_cat.genderalign
                                                                    , manager=MANAGER)

    def exit_screen(self):
        self.header.kill()
        del self.header
        self.gender_changed.kill()
        del self.gender_changed
        self.gender_entry_box.kill()
        del self.gender_entry_box
        self.done_button.kill()
        del self.done_button
        self.back_button.kill()
        del self.back_button

    def on_use(self):
        pass

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                if sub(r'[^A-Za-z0-9 ]+', "", self.gender_entry_box.get_text()) != "":
                    self.the_cat.genderalign = sub(r'[^A-Za-z0-9 ]+', "", self.gender_entry_box.get_text())
                    self.gender_changed.show()
            elif event.ui_element == self.back_button:
                self.change_screen('profile screen')
        return


# ---------------------------------------------------------------------------- #
#                           ceremony screen                                    #
# ---------------------------------------------------------------------------- #
class CeremonyScreen(Screens):

    def screen_switches(self):
        self.hide_menu_buttons()
        self.the_cat = Cat.all_cats.get(game.switches['cat'])
        if (self.the_cat.status == 'leader' and not self.the_cat.dead):
            self.header = pygame_gui.elements.UITextBox(str(self.the_cat.name) + '\'s Leadership Ceremony',
                                                        scale(pygame.Rect((200, 180), (1200, -1))),
                                                        object_id=get_text_box_theme(), manager=MANAGER)
        else:
            self.header = pygame_gui.elements.UITextBox(str(self.the_cat.name) + ' has no ceremonies to view.',
                                                        scale(pygame.Rect((200, 180), (1200, -1))),
                                                        object_id=get_text_box_theme(), manager=MANAGER)
        if (self.the_cat.status == 'leader' and not self.the_cat.dead):
            self.life_text = self.handle_leadership_ceremony(self.the_cat)
        else:
            self.life_text = ""
        self.scroll_container = pygame_gui.elements.UIScrollingContainer(scale(pygame.Rect((100, 300), (1400, 1000))))
        self.text = pygame_gui.elements.UITextBox(self.life_text,
                                                  scale(pygame.Rect((0, 0), (1100, -1))),
                                                  object_id=get_text_box_theme("#allegiances_box"),
                                                  container=self.scroll_container, manager=MANAGER)
        self.text.disable()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "",
                                         object_id="#back_button", manager=MANAGER)
        self.scroll_container.set_scrollable_area_dimensions((1360/1600 * screen_x, self.text.rect[3]))

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
            
    def create_leadership_ceremony(self, cat):
        queen = ""
        warrior = ""
        kit = ""
        warrior2 = ""
        app = ""
        elder = ""
        warrior3 = ""
        med_cat = ""
        prev_lead = ""
        known = None
        virtues = None
        if len(cat.life_givers) == 0:
            queen_virtues = ["affection", "compassion", "empathy", "duty", "protection", "pride"]
            warrior_virtues = ["acceptance", "bravery", "certainty", "clear judgement", "confidence"]
            kit_virtues = ["adventure", "curiosity", "forgiveness", "hope", "perspective", "protection"]
            warrior2_virtues = ["courage", "determination", "endurance", "sympathy"]
            app_virtues = ["happiness", "honesty", "humor", "justice", "mentoring", "trust"]
            elder_virtues = ["empathy", "grace", "humility", "integrity", "persistence", "resilience"]
            warrior3_virtues = ["farsightedness", "friendship", "instincts", "mercy", "strength", "unity"]
            med_cat_virtues = ["clear sight", "devotion", "faith", "healing", "patience", "selflessness", "wisdom"]
            prev_lead_virtues = ["endurance in the face of hardship", "knowing when to fight and when to choose peace",
                                 "leadership through the darkest times", "loyalty to their Clan",
                                 "the strength to overcome their fears", "tireless energy"]
            virtues = [choice(queen_virtues), choice(warrior_virtues), choice(kit_virtues), choice(warrior2_virtues),
                       choice(app_virtues), choice(elder_virtues), choice(warrior3_virtues), choice(med_cat_virtues),
                       choice(prev_lead_virtues)]
            known = [False, False, False, False, False, False, False, False, False]

            for i in reversed(game.clan.starclan_cats):
                c = Cat.all_cats[i]
                if c.dead and not c.outside and not c.df:
                    if not queen and c.status == 'queen':
                        queen = str(c.name)
                        known[0] = True
                        continue
                    elif not kit and c.status == 'kitten':
                        kit = str(c.name)
                        known[2] = True
                        continue
                    elif not app and c.status == 'apprentice':
                        app = str(c.name)
                        known[4] = True
                        continue
                    elif not prev_lead and c.status == 'leader':
                        prev_lead = str(c.name)
                        known[8] = True
                        continue
                    elif not elder and c.status == 'elder':
                        elder = str(c.name)
                        known[5] = True
                        continue
                    elif not warrior and c.status == 'warrior':
                        warrior = str(c.name)
                        known[1] = True
                        continue
                    elif not warrior2 and c.status == 'warrior':
                        warrior2 = str(c.name)
                        known[3] = True
                        continue
                    elif not warrior3 and c.status == 'warrior':
                        warrior3 = str(c.name)
                        known[6] = True
                        continue
                    elif not med_cat and (c.status == 'medicine cat' or c.status == 'medicine cat apprentice'):
                        med_cat = str(c.name)
                        known[7] = True
                        continue
                    if queen and warrior and kit and warrior2 and app and elder and warrior3 and med_cat and prev_lead:
                        break
            if not queen:
                queen = str(choice(names.normal_prefixes)) + str(choice(names.normal_suffixes))
            if not warrior:
                warrior = str(choice(names.normal_prefixes)) + str(choice(names.normal_suffixes))
            if not kit:
                kit = str(choice(names.normal_prefixes)) + "kit"
            if not warrior2:
                warrior2 = str(choice(names.normal_prefixes)) + str(choice(names.normal_suffixes))
            if not app:
                app = str(choice(names.normal_prefixes)) + "paw"
            if not elder:
                elder = str(choice(names.normal_prefixes)) + str(choice(names.normal_suffixes))
            if not warrior3:
                warrior3 = str(choice(names.normal_prefixes)) + str(choice(names.normal_suffixes))
            if not med_cat:
                med_cat = str(choice(names.normal_prefixes)) + str(choice(names.normal_suffixes))
            if not prev_lead:
                prev_lead = str(choice(names.normal_prefixes)) + "star"
            cat.life_givers.extend([queen, warrior, kit, warrior2, app, elder, warrior3, med_cat, prev_lead])
            cat.known_life_givers.extend(known)
            cat.virtues.extend(virtues)
        else:
            queen, warrior, kit, warrior2, app, elder, warrior3, med_cat, prev_lead = cat.life_givers[0], \
                                                                                      cat.life_givers[1], \
                                                                                      cat.life_givers[2], \
                                                                                      cat.life_givers[3], \
                                                                                      cat.life_givers[4], \
                                                                                      cat.life_givers[5], \
                                                                                      cat.life_givers[6], \
                                                                                      cat.life_givers[7], \
                                                                                      cat.life_givers[8]

    def handle_leadership_ceremony(self, cat):
        
        dep_name = str(cat.name.prefix) + str(cat.name.suffix)
        if cat.trait == "bloodthirsty":
            intro_text = dep_name + " leaves to speak with StarClan. They close their eyes and awaken under a vast, inky black sky. They turn around to see a wary group of cats approaching, stars dotting their fur." + "\n"
        else:
            intro_text = dep_name + " leaves to speak with StarClan. They close their eyes and are immediately surrounded by their loved ones, friends, and Clanmates who have passed on. Stars shine throughout their pelts, and their eyes are warm as they greet the new leader." + "\n"

        # as of right now, chooses random starclan cats to give lives
        # in the future, plan to have starclan cats with high relationships to give lives
        # if not enough cats to give lives, generate a new random cat name to give a life
        known = cat.known_life_givers
        virtues = cat.virtues
        if not known or not virtues:
            self.create_leadership_ceremony(cat)
        queen, warrior, kit, warrior2, app, elder, warrior3, med_cat, prev_lead = cat.life_givers[0], \
                                                                                      cat.life_givers[1], \
                                                                                      cat.life_givers[2], \
                                                                                      cat.life_givers[3], \
                                                                                      cat.life_givers[4], \
                                                                                      cat.life_givers[5], \
                                                                                      cat.life_givers[6], \
                                                                                      cat.life_givers[7], \
                                                                                      cat.life_givers[8]
        if known[0]:
            if cat.trait == "bloodthirsty":
                queen_text = queen + ' stalks up to the new leader first, eyes burning with unexpected ferocity. They touch their nose to ' + dep_name + '\'s head, giving them a life for ' + cat.virtues[0] + '. ' + dep_name + ' reels back with the emotion of the life that courses through them.'
            else:
                queen_text = queen + ' pads up to the new leader first, softly touching their nose to ' + dep_name + '\'s head. They give a life for ' + \
                            cat.virtues[0] + '.'
        else:
            if cat.trait == "bloodthirsty":
                queen_text = 'A queen introduces themself as ' + queen + '. They touch their nose to ' + dep_name + '\'s head, giving them a life for ' + cat.virtues[0] + '. Their eyes are slightly narrowed as they step back, turning away as ' + dep_name + ' struggles to gain the new life.'
            else:
                queen_text = 'A queen introduces themself as ' + queen + '. They softly touch their nose to ' + dep_name + '\'s head, giving them a life for ' + \
                         cat.virtues[0] + '.'
        if known[1]:
            if cat.trait == "bloodthirsty":
                warrior_text = warrior + ' walks up to ' + dep_name + ' next, giving them a life for ' + cat.virtues[
                    1] + '. They pause, then shake their head, heading back into the ranks of StarClan.'
            else:
                warrior_text = warrior + ' walks up to ' + dep_name + ' next, offering a life for ' + cat.virtues[
                    1] + '. They smile, and state that the Clan will do well under ' + dep_name + '\'s leadership.'
        else:
            if cat.trait == "bloodthirsty":
                warrior_text = 'An unknown warrior walks towards ' + dep_name + ' stating that their name is ' + warrior + '. They offer a life for ' + \
                           cat.virtues[1] + '. There is a sad look in their eyes.'
            else:
                warrior_text = 'An unknown warrior walks towards ' + dep_name + ' stating that their name is ' + warrior + '. They offer a life for ' + \
                            cat.virtues[1] + '.'
        if known[2]:
            if cat.trait == "bloodthirsty":
                kit_text = kit + ' hesitantly approaches the new leader, reaching up on their hind legs to give them a new life for ' + \
                       cat.virtues[2] + '. They lash their tail and head back to make room for the next cat.'
            else:
                kit_text = kit + ' bounds up to the new leader, reaching up on their hind legs to give them a new life for ' + \
                        cat.virtues[2] + '. They flick their tail and head back to make room for the next cat.'
        else:
            if cat.trait == "bloodthirsty":
                kit_text = kit + ' introduces themself and hesitantly approaches the new leader, reaching up on their hind legs to give them a new life for ' + \
                       cat.virtues[2] + '.'
            else:
                kit_text = kit + ' introduces themself and bounds up to the new leader, reaching up on their hind legs to give them a new life for ' + \
                        cat.virtues[2] + '.'
        if known[3]:
            if cat.trait == "bloodthirsty":
                warrior2_text = 'Another cat approaches. ' + warrior2 + ' steps forward to give ' + dep_name + ' a life for ' + \
                            cat.virtues[3] + '. ' + dep_name + ' yowls in pain as the life rushes into them.'
            else:
                warrior2_text = 'Another cat approaches. ' + warrior2 + ' steps forward to give ' + dep_name + ' a life for ' + \
                            cat.virtues[3] + '. ' + dep_name + ' grits their teeth as the life rushes into them.'
        else:
            if cat.trait == "bloodthirsty":
                warrior2_text = warrior2 + ' states their name and steps forward to give ' + dep_name + ' a life for ' + \
                            cat.virtues[3] + '. Their pelt does not gleam with starlight; instead, a black ooze drips from their fur.'
            else:
                warrior2_text = warrior2 + ' states their name and steps forward to give ' + dep_name + ' a life for ' + \
                                cat.virtues[3] + '.'
        if known[4]:
            if cat.trait == "bloodthirsty":
                app_text = 'A young cat is next to give a life. They hesitate, before an older cat nudges them forward, whispering something in their ear. ' + app + ' stretches up to give a life for ' + \
                       cat.virtues[4] + '.'
            else:
                app_text = 'A young cat is next to give a life. Starlight reflects off their youthful eyes. ' + app + ' stretches up to give a life for ' + \
                        cat.virtues[4] + '.'
        else:
            if cat.trait == "bloodthirsty":
                app_text = app + ', an unfamiliar apprentice, stretches up to give a life for ' + cat.virtues[
                4] + '. They start to growl something, but an older StarClan cat nudges them back into their ranks.'
            else:
                app_text = app + ', an unfamiliar apprentice, stretches up to give a life for ' + cat.virtues[
                    4] + '. Their eyes glimmer as they wish ' + dep_name + " well, and step back for the next cat."
        if known[5]:
            if cat.trait == "bloodthirsty":
                elder_text = elder + ' pads forward with a wary expression. They give a life for ' + \
                         cat.virtues[5] + '.'
            else:
                elder_text = elder + ' strides forward, an energy in their steps that wasn\'t present in their last moments. They give a life for ' + \
                            cat.virtues[5] + '.'
        else:
            if cat.trait == "bloodthirsty":
                elder_text = 'An elder pads forward with a wary expression. They do not introduce themself. They give a life for ' + \
                         cat.virtues[5] + '.'
            else:
                elder_text = elder + ', an elder, introduces themself and strides forward to give a new life for ' + \
                            cat.virtues[5] + '.'
        if known[6]:
            if cat.trait == "bloodthirsty":
                warrior3_text = warrior3 + ' approaches. Pain surges through ' + dep_name + '\'s pelt as they receive a life for ' + \
                                cat.virtues[6] + '. ' + warrior3 + ' watches dispassionately.'
            else:
                warrior3_text = warrior3 + ' dips their head in greeting. Energy surges through ' + dep_name + '\'s pelt as they receive a life for ' + \
                                cat.virtues[6] + '. They reassure ' + dep_name + ' that they are almost done.'
        else:
            if cat.trait == "bloodthirsty":
                warrior3_text = warrior3 + ', an unknown warrior, gives a life for ' + cat.virtues[
                    6] + '. The cat hurries back to take their place back in StarClan, leaving room for the next cat to give a life.'
            else:
                warrior3_text = warrior3 + ', an unknown warrior, gives a life for ' + cat.virtues[
                    6] + '. The cat turns around to take their place back in StarClan, leaving room for the next cat to give a life.'
        if known[7]:
            if cat.trait == "bloodthirsty":
                med_cat_text = med_cat + ' approaches next, a blank expression on their face. They offer a life for ' + \
                            cat.virtues[7] + ', whispering to not lose their way.'
            else:
                med_cat_text = med_cat + ' approaches next, a warm smile on their face. They offer a life for ' + \
                            cat.virtues[7] + ', whispering to take care of the Clan the best they can.'
        else:
            if cat.trait == "bloodthirsty":
                med_cat_text = med_cat + ' approaches next, a blank expression on their face. They offer a life for ' + \
                            cat.virtues[7] + '.'
            else:
                med_cat_text = 'The next cat is not familiar. They smell of catmint and other herbs, and have a noble look to them. The cat tells ' + dep_name + ' that their name is ' + med_cat + '. They offer a life for ' + \
                            cat.virtues[7] + '.'
        if known[8]:
            if cat.trait == "bloodthirsty":
                prev_lead_text = 'Finally, ' + prev_lead + ' steps forward. There is a conflicted expression on their face when they step forward and stare into ' + dep_name + '\'s eyes. They give a life for ' + \
                             cat.virtues[8] + '.'
            else:
                prev_lead_text = 'Finally, ' + prev_lead + ' steps forward. There is pride in their gaze as they stare into ' + dep_name + '\'s eyes. They give a life for ' + \
                             cat.virtues[8] + '.'
        else:
            if cat.trait == "bloodthirsty":
                prev_lead_text = prev_lead + ', one of StarClan\'s oldest leaders, looks at the new leader with a conflicted expression. They give a last life, the gift of ' + \
                             cat.virtues[8] + '.'
            else:
                prev_lead_text = prev_lead + ', one of StarClan\'s oldest leaders, looks at the new leader with pride. They give a last life, the gift of ' + \
                                cat.virtues[8] + '.'
        if known[8]:
            if cat.trait == "bloodthirsty":
                ending_text = prev_lead + " hails " + dep_name + " by their new name, " + str(
                cat.name.prefix) + "star, telling them that their old life is no more. They are granted guardianship of " + str(
                game.clan.name) + "Clan, and are told to use their new power wisely. StarClan is silent as the new leader begins to wake up. " + str(
                cat.name.prefix) + "star stands, feeling a new strength within their body, and grins."
            else:
                ending_text = prev_lead + " hails " + dep_name + " by their new name, " + str(
                    cat.name.prefix) + "star, telling them that their old life is no more. They are granted guardianship of " + str(
                    game.clan.name) + "Clan, and are told to use their new power wisely. The group of starry cats yowls " + str(
                    cat.name.prefix) + "star\'s name in support. " + str(
                    cat.name.prefix) + "star wakes up feeling a new strength within their body and know that they are now ready to lead the Clan."

        else:
            if cat.trait == "bloodthirsty":
                ending_text = "StarClan hails " + dep_name + " by their new name, " + str(
                cat.name.prefix) + "star, telling them that their old life is no more. They are granted guardianship of " + str(
                game.clan.name) + "Clan, and are told to use their new power wisely. StarClan is silent as the new leader begins to wake up. " + str(
                cat.name.prefix) + "star stands, feeling a new strength within their body, and grins."
            else:
                ending_text = "StarClan hails " + dep_name + " by their new name, " + str(
                    cat.name.prefix) + "star, telling them that their old life is no more. They are granted guardianship of " + str(
                    game.clan.name) + "Clan, and are told to use their new power wisely. The group of starry cats yowls " + str(
                    cat.name.prefix) + "star\'s name in support. " + str(
                    cat.name.prefix) + "star wakes up feeling a new strength within their body and know that they are now ready to lead the Clan."

        return intro_text + '\n' + queen_text + '\n\n' + warrior_text + '\n\n' + kit_text + '\n\n' + warrior2_text + '\n\n' + app_text + '\n\n' + elder_text + '\n\n' + warrior3_text + '\n\n' + med_cat_text + '\n\n' + prev_lead_text + '\n\n' + ending_text

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
        return

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
                game.switches["cat"] = self.next_cat
                self.update_selected_cat()
            elif event.ui_element == self.previous_cat_button:
                game.switches["cat"] = self.previous_cat
                self.update_selected_cat()
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
                                                   (1408/1600 * screen_x, 20/1400 * screen_y)
                                               ), manager=MANAGER)

        self.blurb_background = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                          ((100, 390), (1400, 300))),
                                                          pygame.transform.scale(
                                                              pygame.image.load(
                                                                  "resources/images/mediation_selection_bg.png").convert_alpha(),
                                                              (1400, 300))
                                                          )

        #LEADERSHIP
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


        #In-TRAINING ROLES:
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

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((490, 80), (300, 300))),
            pygame.transform.scale(
                self.the_cat.big_sprite, (300, 300)),
            manager=MANAGER
        )

        name = str(self.the_cat.name)
        if len(name) > 17:
            name = name[:14] + "..."
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(scale(pygame.Rect((790, 140), (320, -1))),
                                                                             name,
                                                                             object_id=get_text_box_theme())

        text = f"<b>{self.the_cat.status}</b>\n{self.the_cat.trait}\n"

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
                                                                     object_id=get_text_box_theme("#cat_patrol_info_box"),
                                                                     manager=MANAGER, line_spacing=0.95)

        self.selected_cat_elements["role_blurb"] = pygame_gui.elements.UITextBox(self.get_role_blurb(),
                                                                                 scale(pygame.Rect((340, 400),(1120, 270))),
                                                                                 object_id="#role_blurb",
                                                                                 manager=MANAGER)

        if self.the_cat.status == "leader":
            icon_path = "resources/images/leader_icon.png"
        elif self.the_cat.status == "deputy":
            icon_path = "resources/images/deputy_icon.png"
        elif self.the_cat.status == "medicine cat":
            icon_path = "resources/images/medic_icon.png"
        elif self.the_cat.status == "medicine cat apprentice":
            icon_path = "resources/images/medic_app_icon.png"
        else:
            icon_path = "resources/images/buttonrank.png"

        self.selected_cat_elements["role_icon"] = pygame_gui.elements.UIImage(scale(pygame.Rect((165, 462), (156, 156))),
                                                                              pygame.transform.scale(
                                                                                  image_cache.load_image(icon_path),
                                                                                  (156/1600 * screen_x, 156/1400 * screen_y)
                                                                              ))

        self.determine_previous_and_next_cat()
        self.update_disabled_buttons()

    def update_disabled_buttons(self):
        #Previous and next cat button
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
