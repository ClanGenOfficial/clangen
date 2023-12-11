#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
import pygame
import ujson

from scripts.utility import scale

from .Screens import Screens

from scripts.utility import get_text_box_theme, shorten_text_to_fit
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
import pygame_gui
from pygame_gui.elements import UIWindow
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from ..game_structure.windows import SpecifyCatPronouns, PronounPresets
from ..housekeeping.datadir import get_data_dir

with open('resources/dicts/pronouns.json', 'r', encoding='utf-8') as f:
    pronouns_dict = ujson.load(f)

class ChangeGenderScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.the_cat = None
        self.selected_cat_elements = {}
        self.buttons = {}
        self.next_cat = None
        self.previous_cat = None
        self.elements = {}
        self.windows = None
        self.checkboxes_text = {}
        self.new_pronouns = None
        self.presets = None
        self.removalbuttons = {}
        self.pronoun_template = [
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
        self.remove_button = {}
        self.checkboxes_text = {}

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
            elif event.ui_element == self.buttons["test_pronouns"]:
                print("update pronoun window")
                if self.new_pronouns.are_boxes_full():
                    temp = self.new_pronouns.get_new_pronouns()
                    self.selected_cat_elements["pronoun_sample"].kill()
                    pronouns=""
                    pronouns = self.get_sample_text(temp[0])
                    
                    self.selected_cat_elements["pronoun_sample"] = UITextBoxTweaked(pronouns, scale(pygame.Rect((1040, 755), (425, 350))),
                                                                                 object_id=get_text_box_theme(
                                                                                     "#text_box_22_horizcenter"),
                                                                       manager=MANAGER, line_spacing=0.95)
            elif event.ui_element == self.buttons["add_pronouns"]:
                print("add new pronouns dict")
                if self.new_pronouns.are_boxes_full():
                        temp = self.new_pronouns.get_new_pronouns()
                        new_dict = temp[0] 
                        if not self.new_pronouns.is_duplicate(new_dict):
                            self.the_cat.pronouns.append(new_dict)
                            self.update_selected_cat()
                    
            elif event.ui_element == self.buttons["customize"]:
                self.new_pronouns = SpecifyCatPronouns(self.the_cat)
                self.buttons["save_as_preset"].enable()
                self.buttons["add_pronouns"].enable()
                self.buttons["test_pronouns"].enable()
            
            elif event.ui_element == self.buttons["load_presets"]:
                self.presets = PronounPresets(self.the_cat)
                
            elif event.ui_element == self.buttons["save_as_preset"]:
                print("saving as preset")
                if self.new_pronouns.are_boxes_full():
                    temp = self.new_pronouns.get_new_pronouns()
                    new_dict = temp[0]
                    with open('resources/dicts/pronouns.json', 'r', encoding='utf-8') as file:
                        pronouns_dict = ujson.load(file)

                    # Add the new pronouns to the "custom_presets" array
                    pronouns_dict["custom_presets"].append(new_dict)

                    # Write the updated data back to 'resources/dicts/pronouns.json'
                    with open('resources/dicts/pronouns.json', 'w', encoding='utf-8') as file:
                        ujson.dump(pronouns_dict, file, indent=2)

            else:
                if len(self.removalbuttons) == len(self.the_cat.pronouns):
                    for pronounset in self.the_cat.pronouns:
                        remove_button_id = f"remove_button_{pronounset['name']}"
                        if event.ui_element == self.removalbuttons[remove_button_id]:
                            print(f"Remove button clicked for pronoun: {pronounset['name']}")
                            self.remove_pronounset(pronounset['name'])
                
                with open('resources/dicts/pronouns.json', 'r', encoding='utf-8') as file:
                    pronouns_data = ujson.load(file)

                for pronounset in pronouns_data["custom_presets"]:
                    remove_button_id = f"remove_button_{pronounset['name']}2"
                    if event.ui_element == self.buttons.get(remove_button_id):
                        print(f"Remove button clicked for pronoun: {pronounset['name']}")
                        self.remove_default_pronounset(pronounset['name'])
                
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
    
    def on_remove_button_click(self, pronoun_name):
        print(f"Remove button clicked for pronoun: {pronoun_name}")
        
    def get_sample_text(self, pronouns):
        text = ""
        text += f"Demo: {pronouns['name']} <br>"
        subject = f"{pronouns['subject']} are quick. <br>"
        if pronouns["conju"] == 2:
            subject = f"{pronouns['subject']} is quick. <br>"
        text += subject.capitalize()
        text += f"Everyone saw {pronouns['object']}. <br>"
        poss = f"{pronouns['poss']} paw slipped.<br>"
        text += poss.capitalize()
        text += f"That den is {pronouns['inposs']}. <br>"
        text += f"This cat hunts by {pronouns['self']}."
        return text

    def update_selected_cat(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        for ele in self.elements:
            self.elements[ele].kill()
        for ele in self.checkboxes_text:
            self.checkboxes_text[ele].kill()
        for ele in self.buttons:
            self.buttons[ele].kill()
        for ele in self.removalbuttons:
            self.removalbuttons[ele].kill()
        if not self.presets == None:
            self.presets.kill()
        if not self.new_pronouns == None:
            self.new_pronouns.kill()
        
        self.selected_cat_elements = {}
        self.checkboxes_text = {}
        self.buttons ={}
        self.elements = {}
        self.removalbuttons = {}

        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        if not self.the_cat:
            return

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1090, 300), (300, 300))),
            pygame.transform.scale(
                self.the_cat.sprite, (300, 300)),
            manager=MANAGER
        )

        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 300, 26)
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(scale(pygame.Rect((1065, 205), (350, 64))),
                                                                             short_name,
                                                                             object_id=get_text_box_theme()
                                                                             )

        text = f"<b>{self.the_cat.genderalign}</b>\n{self.the_cat.gender}\n"

        self.selected_cat_elements["cat_details"] = UITextBoxTweaked(text, scale(pygame.Rect((1090, 610), (320, 288))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_22_horizcenter"),
                                                                     manager=MANAGER, line_spacing=0.95)
        
        self.buttons["customize"] = UIImageButton(scale(pygame.Rect((350, 700), (256, 60))), "", object_id="#customize_button"
                                             , manager=MANAGER)
        
        self.buttons["test_pronouns"] = UIImageButton(scale(pygame.Rect((1090, 1190), (306, 60))), "", object_id="#test_pronouns_button"
                                             , manager=MANAGER)
        self.buttons["add_pronouns"] = UIImageButton(scale(pygame.Rect((1090, 1280), (306, 60))), "", object_id="#add_pronouns_button"
                                             , manager=MANAGER)
        self.buttons["load_presets"] = UIImageButton(scale(pygame.Rect((1090, 1100), (306, 60))), "", object_id="#load_presets_button"
                                             , manager=MANAGER)
        self.buttons["save_as_preset"] = UIImageButton(scale(pygame.Rect((1090, 1010), (306, 60))), "", object_id="#save_as_preset_button"
                                             , manager=MANAGER)
        self.selected_cat_elements["sample_pronouns_blurb"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                  ((1040, 705), (425, 280))),
                                                            pygame.transform.scale(
                                                                pygame.image.load(
                                                                    "resources/images/sample_pronouns_bg.png").convert_alpha(),
                                                                (1400, 300))
                                                            )
        pronouns=""
        pronouns = self.get_sample_text(self.the_cat.pronouns[0])
        
        self.selected_cat_elements["pronoun_sample"] = UITextBoxTweaked(pronouns, scale(pygame.Rect((1040, 735), (425, 350))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_22_horizcenter"),
                                                                     manager=MANAGER, line_spacing=0.95)
        
        cat_frame_pronoun = "resources/images/patrol_cat_frame.png"
        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1040, 280), (425, 435))),
            pygame.transform.scale(pygame.image.load(cat_frame_pronoun).convert_alpha(), (300, 300)),
            manager=MANAGER
        )
        
        self.determine_previous_and_next_cat()
        self.update_disabled_buttons()

        
        # List the various pronouns
        self.checkboxes_text["container_general"] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=scale(pygame.Rect((20, 160), (540, 530))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)
       
        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Current Pronouns",
            scale(pygame.Rect((165, 180), (350, 65))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)
        
        n = 0
        ycoor = 78

        for pronounset in self.the_cat.pronouns:
            checkname = self.the_cat.pronouns[n]['name']
            displayname = f"{self.the_cat.pronouns[n]['name']} :   "
            displayname += f"{self.the_cat.pronouns[n]['subject']}/"
            displayname += f"{self.the_cat.pronouns[n]['object']}"

            # Create remove button for each pronounset with dynamic ycoor
            button_rect = scale(pygame.Rect((50, ycoor+5), (55, 55)))
            self.removalbuttons[f"remove_button_{checkname}"] = UIImageButton(
                button_rect, 
                "",
                container=self.checkboxes_text["container_general"],
                object_id="#exit_window_button",
                manager=MANAGER)

            # Create UITextBox for pronoun display with clickable remove button
            text_box_rect = scale(pygame.Rect((100, ycoor), (400, 78))) 
            self.checkboxes_text[checkname] = pygame_gui.elements.UITextBox(
                displayname,
                text_box_rect,
                container=self.checkboxes_text["container_general"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER)

            self.checkboxes_text[checkname].disable()
            n += 1
            ycoor += 50

        if n == 1:
            for pronounset in self.the_cat.pronouns:
                checkname = pronounset['name']
                button_id = f"remove_button_{checkname}"
                if button_id in self.removalbuttons:
                    self.removalbuttons[button_id].disable()
        
        min_scrollable_height = max(100, n * 50) 

        self.checkboxes_text["container_general"].set_scrollable_area_dimensions((300, min_scrollable_height))
        self.buttons["save_as_preset"].disable()
        self.buttons["add_pronouns"].disable()
        self.buttons["test_pronouns"].disable()

        #Default Pronouns
        # List the various pronouns
        self.checkboxes_text["container_general2"] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=scale(pygame.Rect((350, 160), (640, 530))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)
        
        self.checkboxes_text['instr2'] = pygame_gui.elements.UITextBox(
            "Custom Pronoun Removal",
            scale(pygame.Rect((550, 180), (450, 65))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)
         
        n = 0
        ycoor = 78

        for pronounset in pronouns_dict["custom_presets"]:
            checkname = pronouns_dict["custom_presets"][n]['name']
            displayname = f"{pronouns_dict['custom_presets'][n]['name']} :   "
            displayname += f"{pronouns_dict['custom_presets'][n]['subject']}/"
            displayname += f"{pronouns_dict['custom_presets'][n]['object']}"


            # Create remove button for each pronounset with dynamic ycoor
            button_rect2 = scale(pygame.Rect((250, ycoor+5), (55, 55)))
            self.buttons[f"remove_button_{checkname}2"] = UIImageButton(
                button_rect2, 
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#exit_window_button",
                manager=MANAGER)

            # Create UITextBox for pronoun display with clickable remove button
            text_box_rect2 = scale(pygame.Rect((300, ycoor), (400, 78))) 
            self.checkboxes_text[checkname] = pygame_gui.elements.UITextBox(
                displayname,
                text_box_rect2,
                container=self.checkboxes_text["container_general2"],
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER)

            self.checkboxes_text[checkname].disable()
            n += 1
            ycoor += 50

        if n == 1:
            for pronounset in pronouns_dict["custom_presets"]:
                checkname = pronounset['name']
                button_id = f"remove_button_{checkname}2"
                if button_id in self.buttons:
                    self.buttons[button_id].disable()
        
        min_scrollable_height = max(100, n * 50) 

        self.checkboxes_text["container_general2"].set_scrollable_area_dimensions((300, min_scrollable_height))
        self.buttons["save_as_preset"].disable()
        self.buttons["add_pronouns"].disable()
        self.buttons["test_pronouns"].disable()
    def remove_pronounset(self, pronoun_name):
        # Remove the pronoun set from the list
        for pronounset in self.the_cat.pronouns:
            if pronounset['name'] == pronoun_name:
                self.the_cat.pronouns.remove(pronounset)
                break
    
        self.update_selected_cat()

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
    
    def remove_default_pronounset(self, pronoun_name):
        # Remove the pronoun set from the list
        for pronounset in pronouns_dict["custom_presets"]:
            if pronounset['name'] == pronoun_name:
                pronouns_dict["custom_presets"].remove(pronounset)
                break
    
        self.update_selected_cat()

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
        self.checkboxes_text["container_general2"].kill()
        del self.checkboxes_text["container_general2"]
        self.checkboxes_text['instr2'].kill()
        del self.checkboxes_text['instr2']

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}
