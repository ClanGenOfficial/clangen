#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
import pygame
import ujson

from scripts.utility import scale

from .Screens import Screens

from re import sub

from scripts.utility import get_text_box_theme, shorten_text_to_fit
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
import pygame_gui
from pygame_gui.elements import UIWindow
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
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
        self.boxes = {}
        self.box_labels = {}
        self.conju = 2

    def handle_event(self, event):

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches["cat"] = self.next_cat
                    self.update_selected_cat()
                #else:
                    #print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_selected_cat()
                #else:
                     #print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.buttons["test_pronouns"]:
                 #print("update pronoun window")
                if self.are_boxes_full():
                    temp = self.get_new_pronouns()

                    self.selected_cat_elements["pronoun_sample"].kill()
                    pronouns=""
                    pronouns = self.get_sample_text(temp[0])
                    

                    self.selected_cat_elements["pronoun_sample"] = UITextBoxTweaked(pronouns, scale(pygame.Rect((1065, 703), (425, 350))),
                                                                                 object_id=("#text_box_30_horizcenter"),
                                                                       manager=MANAGER, line_spacing=0.95)
            elif event.ui_element == self.buttons["add_pronouns"]:
                #print("add new pronouns dict")

                if self.are_boxes_full():
                    temp = self.get_new_pronouns()
                    new_dict = temp[0] 
                    if not self.is_duplicate(new_dict):
                        self.the_cat.pronouns.append(new_dict)
                        self.update_selected_cat()
                
            elif event.ui_element == self.buttons["save_as_preset"]:
                #print("saving as preset")
                if self.are_boxes_full():
                    temp = self.get_new_pronouns()
                    new_dict = temp[0]
                    print("Before update:", game.clan.custom_pronouns)
                    # Add the new pronouns to the "custom_presets" array
                    game.clan.add_pronouns(new_dict)
                    # Write the updated data back to 'resources/dicts/pronouns.json'
                    with open('resources/dicts/pronouns.json', 'w', encoding='utf-8') as file:
                        ujson.dump(pronouns_dict, file, indent=2)
                    self.update_custom_preset_removal()

                    print("After update:", game.clan.custom_pronouns)
                    self.update_selected_cat()
            elif event.ui_element == self.buttons["done"]:
                if sub(r'[^A-Za-z0-9 ]+', "", self.boxes["gender"].get_text()) != "":
                    self.the_cat.genderalign = sub(
                        r'[^A-Za-z0-9 ]+', "", self.boxes["gender"].get_text())
                    self.update_selected_cat()
            elif event.ui_element == self.buttons["singular"]:
                self.buttons["plural"].enable()
                self.buttons["singular"].disable()
                self.conju = 2
            elif event.ui_element == self.buttons["plural"]:
                self.buttons["singular"].enable()
                self.buttons["plural"].disable()
                self.conju = 1
            else:
                if len(self.removalbuttons) == len(self.the_cat.pronouns):
                    for pronounset in self.the_cat.pronouns:
                        remove_button_id = f"remove_button_{pronounset['name']}"
                        if event.ui_element == self.removalbuttons[remove_button_id]:
                            #print(f"Remove button clicked for current pronoun: {pronounset['name']}")
                            self.remove_pronounset(pronounset['name'])
                
            with open('resources/dicts/pronouns.json', 'r', encoding='utf-8') as file:
                    pronouns_data = ujson.load(file)
            
            for pronounset in pronouns_data["default_pronouns"]:
                remove_button_id = f"remove_button_{pronounset['name']}2"
                add_button_id = f"add_button_{pronounset['name']}2"
                if event.ui_element == self.buttons.get(add_button_id):
                    print("added")
                    for x in range(len(pronouns_data["default_pronouns"])):
                        if pronounset['name'] == pronouns_data["default_pronouns"][x]['name']:
                            print("in default")
                            self.the_cat.pronouns.append(pronounset)
                            self.update_selected_cat()

            for pronounset in game.clan.custom_pronouns:
                remove_button_id = f"remove_button_{pronounset['name']}2"
                add_button_id = f"add_button_{pronounset['name']}2"
                if event.ui_element == self.buttons.get(remove_button_id):
                    #print(f"Remove button clicked for pronoun preset: {pronounset['name']}")
                    game.clan.custom_pronouns.remove(pronounset)
                    with open('resources/dicts/pronouns.json', 'w', encoding='utf-8') as file:
                        ujson.dump(pronouns_data, file, ensure_ascii=False, indent=4)
                    self.remove_custom_preset(pronounset['name'])
                elif event.ui_element == self.buttons.get(add_button_id):
                    print("added")
                    for x in range(len(game.clan.custom_pronouns)):
                        if pronounset['name'] == game.clan.custom_pronouns[x]['name']:
                            print("in custom")
                            self.the_cat.pronouns.append(pronounset)
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
    
    '''def on_remove_button_click(self, pronoun_name):
        print(f"Remove button clicked for pronoun: {pronoun_name}")'''
        
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
    
    def reset_buttons_and_boxes(self):
        #kills everything when switching cats

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
        for ele in self.box_labels:
            self.box_labels[ele].kill()
        for ele in self.boxes:
            self.boxes[ele].kill()

    def update_selected_cat(self):
        self.reset_buttons_and_boxes()
        self.selected_cat_elements = {}
        self.checkboxes_text = {}
        self.buttons ={}
        self.elements = {}
        self.removalbuttons = {}

        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        if not self.the_cat:
            return

        self.selected_cat_elements["customize_blurb"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                  ((100, 730), (860, 615))),
                                                            pygame.transform.scale(
                                                                pygame.image.load(
                                                                    "resources/images/add_pronouns_bg.png").convert_alpha(),
                                                                (1400, 300))
                                                            )

        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1115, 280), (300, 300))),
            pygame.transform.scale(
                self.the_cat.sprite, (300, 300)),
            manager=MANAGER
        )

        self.selected_cat_elements["sample_pronouns_blurb"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                  ((1065, 685), (425, 310))),
                                                            pygame.transform.scale(
                                                                pygame.image.load(
                                                                    "resources/images/sample_pronouns_bg.png").convert_alpha(),
                                                                (1400, 300))
                                                            )
        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 300, 26)
        self.selected_cat_elements["cat_name"] = pygame_gui.elements.UILabel(scale(pygame.Rect((1090, 205), (350, 64))),
                                                                             short_name,
                                                                             object_id=get_text_box_theme("#text_box_40_horizcenter")
                                                                             )

        text = f"<b>{self.the_cat.genderalign}</b>\n{self.the_cat.gender}\n"


        self.selected_cat_elements["cat_details"] = UITextBoxTweaked(text, scale(pygame.Rect((1115, 580), (320, 288))),
                                                                     object_id=get_text_box_theme(
                                                                         "#text_box_30_horizcenter"),
                                                                     manager=MANAGER, line_spacing=0.95)
        

        self.buttons["test_pronouns"] = UIImageButton(scale(pygame.Rect((1100, 1050), (306, 60))), "", object_id="#test_pronouns_button"
                                             , manager=MANAGER)
        self.buttons["add_pronouns"] = UIImageButton(scale(pygame.Rect((1100, 1230), (306, 60))), "", object_id="#add_pronouns_button"
                                             , manager=MANAGER)
        self.buttons["save_as_preset"] = UIImageButton(scale(pygame.Rect((1100, 1140), (306, 60))), "", object_id="#save_as_preset_button"
                                             , manager=MANAGER)
        self.buttons["done"] = UIImageButton(scale(pygame.Rect((670, 930), (154, 60))), "",
                                             object_id="#done_button",
                                             manager=MANAGER)
        self.selected_cat_elements["header"] = pygame_gui.elements.UITextBox(f"-Change {self.the_cat.name}'s Gender-"
                                                         f"<br> You can set this to anything! "
                                                         f"Gender alignment does not affect gameplay.",
                                                         scale(pygame.Rect(
                                                             (135, 750), (760, 150))),
                                                         object_id="#text_box_30_horizcenter_spacing_95",
                                                         manager=MANAGER)
        self.box_labels["name"] = pygame_gui.elements.UITextBox("Name",
                                                         scale(pygame.Rect(
                                                             (125, 1030), (200, 60))),
                                                         object_id="#text_box_30_horizcenter_spacing_95",
                                                         manager=MANAGER)
        self.box_labels["subject"] = pygame_gui.elements.UITextBox("Subject",
                                                         scale(pygame.Rect(
                                                             (305, 1030), (200, 60))),
                                                         object_id="#text_box_30_horizcenter_spacing_95",
                                                         manager=MANAGER)
        self.box_labels["object"] = pygame_gui.elements.UITextBox("Object",
                                                         scale(pygame.Rect(
                                                             (485, 1030), (200, 60))),
                                                         object_id="#text_box_30_horizcenter_spacing_95",
                                                         manager=MANAGER)
        self.box_labels["poss"] = pygame_gui.elements.UITextBox("Poss",
                                                         scale(pygame.Rect(
                                                             (125, 1180), (200, 60))),
                                                         object_id="#text_box_30_horizcenter_spacing_95",
                                                         manager=MANAGER)
        self.box_labels["inposs"] = pygame_gui.elements.UITextBox("Inposs",
                                                         scale(pygame.Rect(
                                                             (305, 1180), (200, 60))),
                                                         object_id="#text_box_30_horizcenter_spacing_95",
                                                         manager=MANAGER)
        self.box_labels["self"] = pygame_gui.elements.UITextBox("Self",
                                                         scale(pygame.Rect(
                                                             (465, 1180), (200, 60))),
                                                         object_id="#text_box_30_horizcenter_spacing_95",
                                                         manager=MANAGER)
        self.gender_changed = pygame_gui.elements.UITextBox("Gender Alignment Changed!",
                                                                scale(pygame.Rect(
                                                                    (290,970), (800, 80))),
                                                                visible=False,
                                                                object_id="#text_box_30_horizleft",
                                                                manager=MANAGER)
            
        self.buttons["singular"] = UIImageButton(scale(pygame.Rect((720, 1090), (189, 60))), "",
                                             object_id="#singular_button",
                                             manager=MANAGER)
            
        self.buttons["plural"] = UIImageButton(scale(pygame.Rect((720, 1240), (189, 60))), "",
                                             object_id="#plural_button",
                                             manager=MANAGER)
        
        self.boxes["gender"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((235, 930), (400, 60))),
                                                                        placeholder_text=self.the_cat.genderalign,
                                                                        manager=MANAGER)
            
        self.boxes["name"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((145, 1090), (150, 60))),
                                                                        placeholder_text=self.the_cat.pronouns[0]["name"],
                                                                        manager=MANAGER)
            
        self.boxes["subject"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((335, 1090), (150, 60))),
                                                                        placeholder_text=self.the_cat.pronouns[0]["subject"],
                                                                        manager=MANAGER)
            
        self.boxes["object"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((525, 1090), (150, 60))),
                                                                        placeholder_text=self.the_cat.pronouns[0]["object"],
                                                                        manager=MANAGER)
                  
        self.boxes["poss"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((145, 1240), (150, 60))),
                                                                        placeholder_text=self.the_cat.pronouns[0]["poss"],
                                                                        manager=MANAGER)
            
        self.boxes["inposs"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((335, 1240), (150, 60))),
                                                                        placeholder_text=self.the_cat.pronouns[0]["inposs"],
                                                                        manager=MANAGER)
            
        self.boxes["self"] = pygame_gui.elements.UITextEntryLine(scale(pygame.Rect((525, 1240), (150, 60))),
                                                                        placeholder_text=self.the_cat.pronouns[0]["self"],
                                                                        manager=MANAGER)
            
        if self.the_cat.pronouns[0]["conju"] == 2:
            self.buttons["singular"].disable()
            self.conju = 2
        else:
            self.buttons["plural"].disable()
            self.conju = 1
        
        pronouns=""
        pronouns = self.get_sample_text(self.the_cat.pronouns[0])
        
        self.selected_cat_elements["pronoun_sample"] = UITextBoxTweaked(pronouns, scale(pygame.Rect((1065, 703), (425, 350))),
                                                                     object_id=("#text_box_30_horizcenter"),
                                                                     manager=MANAGER, line_spacing=0.95)
        
        cat_frame_pronoun = "resources/images/patrol_cat_frame.png"
        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((1065, 260), (425, 435))),
            pygame.transform.scale(pygame.image.load(cat_frame_pronoun).convert_alpha(), (300, 300)),
            manager=MANAGER
        )
        
        self.determine_previous_and_next_cat()
        self.update_disabled_buttons()
        self.pronoun_removal()
        self.custom_preset_removal()

    def pronoun_removal(self):
        # List the various pronouns
        self.checkboxes_text["container_general"] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=scale(pygame.Rect((20, 240), (540, 480))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)
       
        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Current Pronouns",
            scale(pygame.Rect((165, 180), (350, 65))),
            object_id=get_text_box_theme("#text_box_34_horizleft"),
            manager=MANAGER)
        
        n = 0
        ycoor = 78

        for pronounset in self.the_cat.pronouns:
            checkname = self.the_cat.pronouns[n]['name']
            displayname = f"{self.the_cat.pronouns[n]['name']} :   "
            displayname += f"{self.the_cat.pronouns[n]['subject']}/"
            displayname += f"{self.the_cat.pronouns[n]['object']}"

            # Create remove button for each pronounset with dynamic ycoor
            button_rect = scale(pygame.Rect((40, ycoor+5), (55, 55)))
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

        self.checkboxes_text["container_general"].set_scrollable_area_dimensions((250, min_scrollable_height))

    def update_pronoun_removal(self):
        self.update_pronoun_removal()
    
    def is_duplicate(self,preset):
        #checks to see if a preset with the same name is already in the cats pronouns
        for pronounset in self.the_cat.pronouns:
            if preset["name"] == pronounset["name"]:
                return True
        return False
    
    def get_new_pronouns(self):
        pronoun_template = [
            {
                "name": "",
                "subject": "",
                "object": "",
                "poss": "",
                "inposs": "",
                "self": "",
                "conju": 1
            }
        ]
        if sub(r'[^A-Za-z0-9 ]+', "", self.boxes["name"].get_text()) != "":
            pronoun_template[0]["name"] = sub(
                r'[^A-Za-z0-9 ]+', "", self.boxes["name"].get_text())
        if sub(r'[^A-Za-z0-9 ]+', "", self.boxes["subject"].get_text()) != "":
            pronoun_template[0]["subject"] = sub(
                r'[^A-Za-z0-9 ]+', "", self.boxes["subject"].get_text())
        if sub(r'[^A-Za-z0-9 ]+', "", self.boxes["object"].get_text()) != "":
            pronoun_template[0]["object"] = sub(
                r'[^A-Za-z0-9 ]+', "", self.boxes["object"].get_text())
        if sub(r'[^A-Za-z0-9 ]+', "", self.boxes["poss"].get_text()) != "":
            pronoun_template[0]["poss"] = sub(
                r'[^A-Za-z0-9 ]+', "", self.boxes["poss"].get_text())
        if sub(r'[^A-Za-z0-9 ]+', "", self.boxes["inposs"].get_text()) != "":
            pronoun_template[0]["inposs"] = sub(
                r'[^A-Za-z0-9 ]+', "", self.boxes["inposs"].get_text())
        if sub(r'[^A-Za-z0-9 ]+', "", self.boxes["self"].get_text()) != "":
            pronoun_template[0]["self"] = sub(
                r'[^A-Za-z0-9 ]+', "", self.boxes["self"].get_text())
        if self.conju == 2:
            pronoun_template[0]["conju"] = 2
        
        return pronoun_template

    def custom_preset_removal(self):
        # List the various pronouns
        self.checkboxes_text["container_general2"] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=scale(pygame.Rect((390, 240), (675, 480))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)
        
        self.checkboxes_text['instr2'] = pygame_gui.elements.UITextBox(
            "Custom Preset Removal",
            scale(pygame.Rect((550, 180), (450, 65))),
            object_id=get_text_box_theme("#text_box_34_horizleft"),
            manager=MANAGER)
        
        n = 0
        ycoor = 78
        
        for pronounset in pronouns_dict["default_pronouns"]:
            checkname = pronouns_dict["default_pronouns"][n]['name']
            displayname = f"{pronouns_dict['default_pronouns'][n]['name']} :   "
            displayname += f"{pronouns_dict['default_pronouns'][n]['subject']}/"
            displayname += f"{pronouns_dict['default_pronouns'][n]['object']}"


            # no removal for default pronouns sorry. you're stuck with them
            
            #Create add button for each pronounset with dynamic ycoor
            button_rect2 = scale(pygame.Rect((240, ycoor+5), (55, 55)))
            self.buttons[f"add_button_{checkname}2"] = UIImageButton(
                button_rect2, 
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#unchecked_checkbox",
                manager=MANAGER)
            
            if self.is_duplicate(pronounset):
                self.buttons[f"add_button_{checkname}2"] = UIImageButton(
                button_rect2, 
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#checked_checkbox",
                manager=MANAGER)
                self.buttons[f"add_button_{checkname}2"].disable()
            
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
         
        n = 0

        for pronounset in game.clan.custom_pronouns:
            checkname = game.clan.custom_pronouns[n]['name']
            displayname = f"{game.clan.custom_pronouns[n]['name']} :   "
            displayname += f"{game.clan.custom_pronouns[n]['subject']}/"
            displayname += f"{game.clan.custom_pronouns[n]['object']}"


            # Create remove button for each pronounset with dynamic ycoor
            button_rect2 = scale(pygame.Rect((175, ycoor+5), (55, 55)))
            self.buttons[f"remove_button_{checkname}2"] = UIImageButton(
                button_rect2, 
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#exit_window_button",
                manager=MANAGER)

            
            #Create add button for each pronounset with dynamic ycoor
            button_rect2 = scale(pygame.Rect((240, ycoor+5), (55, 55)))
            self.buttons[f"add_button_{checkname}2"] = UIImageButton(
                button_rect2, 
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#unchecked_checkbox",
                manager=MANAGER)
            
            if self.is_duplicate(pronounset):
                self.buttons[f"add_button_{checkname}2"] = UIImageButton(
                button_rect2, 
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#checked_checkbox",
                manager=MANAGER)
                self.buttons[f"add_button_{checkname}2"].disable()
            
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

            
        n +=3
        min_scrollable_height = max(100, n * 50) 

        self.checkboxes_text["container_general2"].set_scrollable_area_dimensions((300, min_scrollable_height))

    def update_custom_preset_removal(self):
        print("Updating custom preset removal...")
        print("Pronouns data:", game.clan.custom_pronouns)
        self.update_custom_preset_removal
        print("Update complete.")

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
    
    def remove_custom_preset(self, pronoun_name):
        # Remove the pronoun set from the list
        for pronounset in game.clan.custom_pronouns:
            if pronounset['name'] == pronoun_name:
                game.clan.custom_pronouns.remove(pronounset)
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

    
    def is_box_full(self, entry):
        if entry.get_text() == "":
            return False
        else:
            return True
        
    def are_boxes_full(self):
        values = []
        values.append(self.is_box_full(self.boxes["name"]))
        values.append(self.is_box_full(self.boxes["subject"]))
        values.append(self.is_box_full(self.boxes["object"]))
        values.append(self.is_box_full(self.boxes["poss"]))
        values.append(self.is_box_full(self.boxes["inposs"]))
        values.append(self.is_box_full(self.boxes["self"]))
        for value in values:
            if value is False:
                return False
        return True

    def exit_screen(self):
        #kill everything
        self.back_button.kill()
        del self.back_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button
        for ele in self.buttons:
            self.buttons[ele].kill()
        for ele in self.box_labels:
            self.box_labels[ele].kill()
        for ele in self.boxes:
            self.boxes[ele].kill()
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
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
