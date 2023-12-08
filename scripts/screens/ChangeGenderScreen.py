#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
import pygame

from scripts.utility import scale

from .Screens import Screens

from scripts.utility import get_text_box_theme, shorten_text_to_fit
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
import pygame_gui
from pygame_gui.elements import UIWindow
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from ..game_structure.windows import SpecifyCatPronouns, PronounTester

class ChangeGenderScreen(Screens):
    the_cat = None
    selected_cat_elements = {}
    buttons = {}
    next_cat = None
    previous_cat = None
    elements = {}
    windows = None
    checkboxes_text = {}
    new_pronouns = None
    sample = None
    pronoun_template = [
        {
            "name": "Custom",
            "subject": "",
            "object": "",
            "poss": "",
            "inposs": "",
            "self": "",
            "conju": 1
        }
    ]
    remove_button = {}
    checkboxes_text = {}

    def handle_event(self, event):

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.update_selected_cat()
                    self.new_pronouns.are_boxes_full()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_selected_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.buttons["test_pronouns"]:
                print("update pronoun window")
                if self.new_pronouns.are_boxes_full():
                    temp = self.new_pronouns.get_new_pronouns()
                    new_dict = temp[0]
                    self.sample.update_sample(new_dict)
            elif event.ui_element == self.buttons["add_pronouns"]:
                print("add new pronouns dict")
                if self.new_pronouns.are_boxes_full():
                    temp = self.new_pronouns.get_new_pronouns()
                    new_dict = temp[0]
                    self.the_cat.pronouns.append(new_dict)
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
        self.update_selected_cat()

    def update_selected_cat(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        for ele in self.elements:
            self.elements[ele].kill()
        for ele in self.checkboxes_text:
            self.checkboxes_text[ele].kill()
        for ele in self.buttons:
            self.buttons[ele].kill()
        
        self.selected_cat_elements = {}
        checkboxes_text = {}
        buttons ={}
        self.elements = {}

        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        if not self.the_cat:
            return

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1090, 320), (300, 300))),
            pygame.transform.scale(
                self.the_cat.sprite, (300, 300)),
            manager=MANAGER
        )

        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 300, 26)
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(scale(pygame.Rect((1065, 225), (350, -1))),
                                                                             short_name,
                                                                             object_id=get_text_box_theme())

        text = f"<b>{self.the_cat.genderalign}</b>\n{self.the_cat.gender}\n"

        self.selected_cat_elements["cat_details"] = UITextBoxTweaked(text, scale(pygame.Rect((1090, 630), (320, 288))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_22_horizcenter"),
                                                                     manager=MANAGER, line_spacing=0.95)
        main_dir = "resources/images/"
        paths = {
            "female": "female_big.png",
            "male": "male_big.png",
            "transmasc": "transmasc_big.png",
            "transfem": "transfem_big.png",
            "nonbinary": "nonbinary_big.png",
        }
        
        self.buttons["test_pronouns"] = UIImageButton(scale(pygame.Rect((1090, 1190), (306, 60))), "", object_id="#test_pronouns_button"
                                             , manager=MANAGER)
        self.buttons["add_pronouns"] = UIImageButton(scale(pygame.Rect((1090, 1280), (306, 60))), "", object_id="#add_pronouns_button"
                                             , manager=MANAGER)
        self.buttons["load_presets"] = UIImageButton(scale(pygame.Rect((1090, 1100), (306, 60))), "", object_id="#load_presets_button"
                                             , manager=MANAGER)
            
        self.new_pronouns = SpecifyCatPronouns(self.the_cat)
        self.sample = PronounTester(self.the_cat)
        
        cat_frame_pronoun = "resources/images/patrol_cat_frame.png"
        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1040, 300), (425, 435))),
            pygame.transform.scale(pygame.image.load(cat_frame_pronoun).convert_alpha(), (300, 300)),
            manager=MANAGER
        )
        
        self.determine_previous_and_next_cat()
        self.update_disabled_buttons()
        self.checkboxes_text[
            "container_general"] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((120,160), (845, 525))), manager=MANAGER)

        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Current Pronouns",
            scale(pygame.Rect((170, 120), (845, 525))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER)
        n=0
        checkname = ""
        displayname = ""
        ycoor = 78

        for pronounset in self.the_cat.pronouns:
            checkname = self.the_cat.pronouns[n]['name']
            displayname = f"{self.the_cat.pronouns[n]['name']} :   "
            displayname += f"{self.the_cat.pronouns[n]['subject']}/"
            displayname += f"{self.the_cat.pronouns[n]['object']}\n"

            # Create UITextBox for pronoun display
            text_box_rect = scale(pygame.Rect((100, ycoor), (800, 78)))
            self.checkboxes_text[checkname] = pygame_gui.elements.UITextBox(
                displayname,
                text_box_rect,
                container=self.checkboxes_text["container_general"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER)
            
            # Create remove button for each pronounset with dynamic ycoor
            button_rect = scale(pygame.Rect((text_box_rect.right + 100, ycoor), (55, 55)))
            self.buttons[f"remove_button_{checkname}"] = UIImageButton(
                button_rect, 
                "",
                container = self.checkboxes_text["container_general"],
                object_id="#exit_window_button",
                manager=MANAGER)
           
            self.checkboxes_text[checkname].disable()
            n += 1
            ycoor += 50
            
        self.checkboxes_text[
            "container_general"].set_scrollable_area_dimensions(
            (400, n*100))
        
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

    def determine_previous_and_next_cat(self):
        """Determines where the next and previous buttons point to."""

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
        
        for ele in self.buttons:
            self.buttons[ele].kill()
        
        self.elements["cat_frame"].kill()
        del self.elements["cat_frame"]
        self.checkboxes_text["container_general"].kill()
        del self.checkboxes_text["container_general"]
        self.checkboxes_text['instr'].kill()
        del self.checkboxes_text['instr']

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}
