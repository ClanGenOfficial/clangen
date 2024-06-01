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
import pygame_gui
from ..game_structure.windows import PronounCreation
from scripts.game_structure.image_button import UIImageButton, CatButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from ..housekeeping.datadir import get_data_dir

with open('resources/dicts/pronouns.json', 'r', encoding='utf-8') as f:
    pronouns_dict = ujson.load(f)


class ChangeGenderScreen(Screens):

    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat_button = None
        self.previous_cat_button = None
        self.back_button = None
        self.the_cat = None
        self.selected_cat_elements = {}
        self.buttons = {}
        self.next_cat = None
        self.previous_cat = None
        self.elements = {}
        self.windows = None
        self.removalboxes_text = {}
        self.removalbuttons = {}
        self.deletebuttons = {}
        self.addbuttons = {}
        self.pronoun_template = [
            {
                "subject": "",
                "object": "",
                "poss": "",
                "inposs": "",
                "self": "",
                "conju": 1
            }
        ]
        self.remove_button = {}
        self.removalboxes_text = {}
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
                # else:
                # print("invalid next cat", self.next_cat)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches["cat"] = self.previous_cat
                    self.update_selected_cat()
                # else:
                # print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.buttons["save"]:
                if self.are_boxes_full():
                    gender_identity = self.get_new_identity()
                    self.the_cat.genderalign = gender_identity
                    print("New Gender Identity Unlocked!")
                    self.selected_cat_elements["identity_changed"].show()
                    self.selected_cat_elements["cat_gender"].kill()
                    self.selected_cat_elements["cat_gender"] = pygame_gui.elements.UITextBox(
                        f"{self.the_cat.genderalign}",
                        scale(pygame.Rect((252, 500), (500, 500))),
                        object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
                        manager=MANAGER
                    )

            elif event.ui_element == self.buttons["add_pronouns"]:
                PronounCreation(self.the_cat)
                self.previous_cat_button.disable()
                self.next_cat_button.disable()
                self.back_button.disable()

            elif type(event.ui_element) is CatButton:
                if event.ui_element.cat_id == "add":
                    if event.ui_element.cat_object not in self.the_cat.pronouns:
                        self.the_cat.pronouns.append(event.ui_element.cat_object)
                elif event.ui_element.cat_id == "remove":
                    if event.ui_element.cat_object in self.the_cat.pronouns and len(self.the_cat.pronouns) > 1:
                        self.the_cat.pronouns.remove(event.ui_element.cat_object)
                elif event.ui_element.cat_id == "delete":
                    if event.ui_element.cat_object in game.clan.custom_pronouns:
                        game.clan.custom_pronouns.remove(event.ui_element.cat_object)
                
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

    def get_new_identity(self):
        new_gender_identity = [""]

        if sub(r'[^A-Za-z0-9 ]+', '', self.selected_cat_elements["gender"].get_text()) != '':
            new_gender_identity = sub(
                r'[^A-Za-z0-9 ]+', '', self.selected_cat_elements["gender"].get_text())

        return new_gender_identity

    def is_box_full(self, entry):
        if entry.get_text() == "":
            return False
        else:
            return True

    def are_boxes_full(self):
        values = []
        values.append(self.is_box_full(self.selected_cat_elements["gender"]))
        for value in values:
            if value is False:
                return False
        return True

    def get_sample_text(self, pronouns):
        text = ""
        text += f"Demo: {pronouns['ID']} <br>"
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
        self.reset_buttons_and_boxes()

        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        if not self.the_cat:
            return

        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((100, 200), (1398, 1040))),
            pygame.transform.scale(pygame.image.load("resources/images/gender_framing.png").convert_alpha(), (699, 520)),
            manager=MANAGER
        )
        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((360, 210), (300, 300))),
            pygame.transform.scale(
                self.the_cat.sprite, (300, 300)),
            manager=MANAGER
        )
        
        # In what case would a cat have no genderalign? -key
        if not self.the_cat.genderalign:
            text = f"{self.the_cat.gender}"
        else:
            text = f"{self.the_cat.genderalign}"

        self.selected_cat_elements["cat_gender"] = pygame_gui.elements.UITextBox(text,
                                                                                 scale(pygame.Rect((260, 500),
                                                                                                   (500, 500))),
                                                                                 object_id=get_text_box_theme(
                                                                                     "#text_box_30_horizcenter_spacing_95"),
                                                                                 manager=MANAGER
                                                                                 )

        name = str(self.the_cat.name)
        header = "Change " + name + "'s Gender"
        self.selected_cat_elements["header"] = pygame_gui.elements.UILabel(scale(pygame.Rect((490, 125), (650, 64))),
                                                                           header,
                                                                           object_id=get_text_box_theme(
                                                                               "#text_box_40_horizcenter")
                                                                           )


        # Save Confirmation
        self.selected_cat_elements["identity_changed"] = pygame_gui.elements.UITextBox("Gender identity changed!",
                                                                                       scale(pygame.Rect(
                                                                                           (770, 495), (800, 80))),
                                                                                       visible=False,
                                                                                       object_id="#text_box_30_horizleft",
                                                                                       manager=MANAGER)

        self.selected_cat_elements["description"] = pygame_gui.elements.UITextBox(
            f"<br> You can set this to anything! "f"Gender identity does not affect gameplay.",
            scale(pygame.Rect(
                (625, 265), (660, 150))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER)
        self.buttons["add_pronouns"] = UIImageButton(scale(pygame.Rect((640, 1290), (324, 56))), "",
                                                     object_id="#add_pronouns_button"
                                                     , manager=MANAGER)
        self.selected_cat_elements["gender"] = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((700, 440), (330, 60))),
            placeholder_text=self.the_cat.genderalign,
            manager=MANAGER)
        self.buttons["save"] = UIImageButton(scale(pygame.Rect((1065, 440), (146, 60))), "",
                                             object_id="#save_button_pronoun",
                                             starting_height=2, manager=MANAGER)
        self.determine_previous_and_next_cat()
        self.pronoun_update()
        self.preset_update()
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

    def pronoun_update(self):
        # List the various pronouns
        self.removalboxes_text["container_general"] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=scale(pygame.Rect((100, 660), (675, 540))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)

        self.removalboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Current Pronouns",
            scale(pygame.Rect((280, 595), (350, 65))),
            object_id="#text_box_34_horizleft_dark",
            manager=MANAGER)

        n = 0
        ycoor = 8
        pronoun_frame = "resources/images/pronoun_frame.png"

        for pronounset in self.the_cat.pronouns:
            displayname = f"{pronounset['subject']}/{pronounset['object']}/" \
                          f"{pronounset['inposs']}/{pronounset['self']}"
            short_name = shorten_text_to_fit(displayname, 360, 26)

            # Create block for each pronounset with dynamic ycoor
            block_rect = scale(pygame.Rect((75, ycoor), (544, 88)))
            self.elements[f"cat_pronouns_{n}"] = pygame_gui.elements.UIImage(
                block_rect,
                pygame.transform.scale(pygame.image.load(pronoun_frame).convert_alpha(), (272, 44)),
                container=self.removalboxes_text["container_general"], manager=MANAGER
            )

            # Create remove button for each pronounset with dynamic ycoor
            button_rect = scale(pygame.Rect((550, ycoor + 18), (48, 48)))
            self.removalbuttons[f"cat_pronouns_{n}"] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="remove",
                container=self.removalboxes_text["container_general"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER)

            # Create UITextBox for pronoun display with clickable remove button
            text_box_rect = scale(pygame.Rect((100, ycoor + 4), (400, 78)))
            self.removalboxes_text[f"cat_pronouns_{n}"] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.removalboxes_text["container_general"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER)

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            self.buttons[f"{n}_tooltip_cat_pronouns"] = UIImageButton(
                text_box_rect,
                "",
                object_id="#blank_button_small",
                container=self.removalboxes_text["container_general"],
                tool_tip_text=displayname if short_name != displayname else None,
                manager=MANAGER,
                starting_height=2
            )
    
            n += 1
            ycoor += 104

        # Disable removing is a cat has only one pronoun. 
        if n == 1:
            for button_id in self.removalbuttons:
                self.removalbuttons[button_id].disable()

        min_scrollable_height = max(100, n * 65)

        if game.settings['fullscreen']:
            self.removalboxes_text["container_general"].set_scrollable_area_dimensions(
                (310 * 2, min_scrollable_height * 2))
        else:
            self.removalboxes_text["container_general"].set_scrollable_area_dimensions((310, min_scrollable_height))

    def preset_update(self):
        # List the various pronouns
        self.removalboxes_text["container_general2"] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=scale(pygame.Rect((795, 660), (675, 540))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)

        self.removalboxes_text['instr2'] = pygame_gui.elements.UITextBox(
            "Saved Pronouns",
            scale(pygame.Rect((1000, 595), (350, 65))),
            object_id="#text_box_34_horizleft_dark",
            manager=MANAGER)

        n = 0
        ycoor = 8
        pronoun_frame = "resources/images/pronoun_frame.png"

        for pronounset in pronouns_dict["default_pronouns"]:
            displayname = f"{pronounset['subject']}/{pronounset['object']}/" \
                          f"{pronounset['inposs']}/{pronounset['self']}"
            short_name = shorten_text_to_fit(displayname, 280, 26)

            # Create block for each pronounset with dynamic ycoor
            block_rect = scale(pygame.Rect((75, ycoor), (544, 88)))
            self.elements[f"{n}"] = pygame_gui.elements.UIImage(
                block_rect,
                pygame.transform.scale(pygame.image.load(pronoun_frame).convert_alpha(), (272, 44)),
                container=self.removalboxes_text["container_general2"], manager=MANAGER
            )

            button_rect = scale(pygame.Rect((425, ycoor + 14), (112, 56)))
            self.addbuttons[f"default_pronouns_{n}"] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="add",
                container=self.removalboxes_text["container_general2"],
                object_id="#add_button",
                starting_height=2,
                manager=MANAGER)
            
            if pronounset in self.the_cat.pronouns:
                self.addbuttons[f"default_pronouns_{n}"].disable()

            # Create UITextBox for pronoun display and create tooltip for full pronoun display
            button_rect = scale(pygame.Rect((550, ycoor + 18), (48, 48)))
            text_box_rect = scale(pygame.Rect((100, ycoor + 4), (400, 78)))
            self.removalboxes_text[f"default_pronouns_{n}"] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.removalboxes_text["container_general2"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER)
            
            self.removalboxes_text[f"default_pronouns_{n}"].disable()

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            self.buttons[f"{n}_tooltip_default_pronouns"] = UIImageButton(
                text_box_rect,
                "",
                object_id="#blank_button_small",
                container=self.removalboxes_text["container_general2"],
                tool_tip_text=displayname if short_name != displayname else None,
                manager=MANAGER,
                starting_height=2
            )

            # Create remove button for each pronounset with dynamic ycoor
            self.deletebuttons[f"default_pronouns_{n}"] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="delete",
                container=self.removalboxes_text["container_general2"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER)
            # though we've made the remove button visible, it needs to be disabled so that the user cannnot remove
            # the defaults.  button is only visible here for UI consistency
            self.deletebuttons[f"default_pronouns_{n}"].disable()

            n += 1
            ycoor += 104
        
        
        n = 0
        for pronounset in game.clan.custom_pronouns:
            displayname = f"{pronounset['subject']}/{pronounset['object']}/" \
                          f"{pronounset['inposs']}/{pronounset['self']}"
            short_name = shorten_text_to_fit(displayname, 280, 26)

            # Create block for each pronounset with dynamic ycoor
            block_rect = scale(pygame.Rect((75, ycoor), (544, 88)))
            self.elements[f"custom_pronouns_{n}"] = pygame_gui.elements.UIImage(
                block_rect,
                pygame.transform.scale(pygame.image.load(pronoun_frame).convert_alpha(), (272, 44)),
                container=self.removalboxes_text["container_general2"], manager=MANAGER
            )

            # Create UITextBox for pronoun display with clickable remove button

            # Create remove button for each pronounset with dynamic ycoor
            button_rect = scale(pygame.Rect((550, ycoor + 18), (48, 48)))
            self.deletebuttons[f"custom_pronouns_{n}"] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="delete",
                container=self.removalboxes_text["container_general2"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER)

            button_rect = scale(pygame.Rect((425, ycoor + 14), (112, 56)))
            self.addbuttons[f"custom_pronouns_{n}"] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="add",
                container=self.removalboxes_text["container_general2"],
                object_id="#add_button",
                starting_height=2,
                manager=MANAGER)
            
            if pronounset in self.the_cat.pronouns:
                self.addbuttons[f"custom_pronouns_{n}"].disable()

            text_box_rect = scale(pygame.Rect((100, ycoor + 4), (400, 78)))
            self.removalboxes_text[f"custom_pronouns_{n}"] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.removalboxes_text["container_general2"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER)
            
            self.removalboxes_text[f"custom_pronouns_{n}"].disable()

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            self.buttons[f"{n}_tooltip_custom_pronouns"] = UIImageButton(
                text_box_rect,
                "",
                object_id="#blank_button_small",
                container=self.removalboxes_text["container_general2"],
                tool_tip_text=displayname if short_name != displayname else None,
                manager=MANAGER,
                starting_height=2
            )

            n += 1
            ycoor += 104

        min_scrollable_height = max(100, (n + 3) * 65)

        if game.settings['fullscreen']:
            self.removalboxes_text["container_general2"].set_scrollable_area_dimensions(
                (310 * 2, min_scrollable_height * 2))
        else:
            self.removalboxes_text["container_general2"].set_scrollable_area_dimensions((310, min_scrollable_height))

    def reset_buttons_and_boxes(self):
        # kills everything when switching cats
        for ele in self.elements:
            self.elements[ele].kill()
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        for ele in self.buttons:
            self.buttons[ele].kill()
        for ele in self.removalboxes_text:
            self.removalboxes_text[ele].kill()
        for ele in self.removalbuttons:
            self.removalbuttons[ele].kill()
        for ele in self.deletebuttons:
            self.deletebuttons[ele].kill()
        for ele in self.addbuttons:
            self.addbuttons[ele].kill()

        self.selected_cat_elements = {}
        self.removalboxes_text = {}
        self.addbuttons = {}
        self.elements = {}
        self.removalbuttons = {}
        self.deletebuttons = {}

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
        # kill everything
        self.back_button.kill()
        del self.back_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.elements["cat_frame"].kill()
        del self.elements["cat_frame"]
        
        self.reset_buttons_and_boxes()
