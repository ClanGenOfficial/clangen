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
from ..game_structure.windows import SpecifyCatGender
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked
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
                SpecifyCatGender(self.the_cat)
                self.previous_cat_button.disable()
                self.next_cat_button.disable()
                self.back_button.disable()

            else:
                with open('resources/dicts/pronouns.json', 'r', encoding='utf-8') as file:
                    pronouns_data = ujson.load(file)

                for pronounset in pronouns_data["default_pronouns"]:
                    add_button_id = f"add_button_{pronounset['name']}" + "preset"
                    if event.ui_element == self.buttons.get(add_button_id):
                        print("added")
                        for x in range(len(pronouns_data["default_pronouns"])):
                            if pronounset['name'] == pronouns_data["default_pronouns"][x]['name']:
                                print("in default")
                                if not self.is_duplicate(pronounset):
                                    self.the_cat.pronouns.append(pronounset)
                                    self.update_selected_cat()
                for pronounset in game.clan.custom_pronouns:
                    remove_button_id = f"remove_button_{pronounset['name']}" + "preset"
                    add_button_id = f"add_button_{pronounset['name']}" + "preset"
                    if event.ui_element == self.buttons.get(add_button_id):
                        print("added")
                        for x in range(len(game.clan.custom_pronouns)):
                            if pronounset['name'] == game.clan.custom_pronouns[x]['name']:
                                print("in custom")
                                if not self.is_duplicate(pronounset):
                                    self.the_cat.pronouns.append(pronounset)
                                    self.update_selected_cat()
                    elif event.ui_element == self.removalbuttons.get(remove_button_id):
                        game.clan.custom_pronouns.remove(pronounset)
                        self.update_selected_cat()
                for pronounset in self.the_cat.pronouns:
                    remove_button_id = f"remove_button_{pronounset['name']}"
                    if event.ui_element == self.removalbuttons.get(remove_button_id):
                        self.the_cat.pronouns.remove(pronounset)
                        self.update_selected_cat()
                        break

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
        self.reset_buttons_and_boxes()
        self.selected_cat_elements = {}
        self.checkboxes_text = {}
        self.buttons = {}
        self.elements = {}
        self.removalbuttons = {}

        self.the_cat = Cat.fetch_cat(game.switches['cat'])
        if not self.the_cat:
            return

        cat_frame_pronoun = "resources/images/gender_framing.png"
        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((100, 200), (1398, 1040))),
            pygame.transform.scale(pygame.image.load(cat_frame_pronoun).convert_alpha(), (699, 520)),
            manager=MANAGER
        )
        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((360, 210), (300, 300))),
            pygame.transform.scale(
                self.the_cat.sprite, (300, 300)),
            manager=MANAGER
        )
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

        # self.selected_cat_elements["cat_details"] = UITextBoxTweaked(text, scale(pygame.Rect((105, 480), (320, 288))),
        #                                                             object_id=get_text_box_theme(
        #                                                                 "#text_box_30_horizcenter"),
        #                                                             manager=MANAGER, line_spacing=0.95)

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
        self.pronoun_removal()
        self.preset_removal()
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
        with open('resources/dicts/pronouns.json', 'r', encoding='utf-8') as file:
            pronouns_data = ujson.load(file)
        for pronounset in pronouns_data["default_pronouns"]:
            add_button_id = f"add_button_{pronounset['name']}" + "preset"
            if self.is_duplicate(pronounset):
                self.buttons.get(add_button_id).disable()
            else:
                self.buttons.get(add_button_id).enable()
        for pronounset in game.clan.custom_pronouns:
            add_button_id = f"add_button_{pronounset['name']}" + "preset"
            if self.is_duplicate(pronounset):
                self.buttons.get(add_button_id).disable()
            else:
                self.buttons.get(add_button_id).enable()

    def pronoun_removal(self):
        # List the various pronouns
        self.checkboxes_text["container_general"] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=scale(pygame.Rect((100, 660), (675, 540))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)

        self.checkboxes_text['instr'] = pygame_gui.elements.UITextBox(
            "Current Pronouns",
            scale(pygame.Rect((280, 595), (350, 65))),
            object_id="#text_box_34_horizleft_dark",
            manager=MANAGER)

        n = 0
        ycoor = 8
        pronoun_frame = "resources/images/pronoun_frame.png"

        for pronounset in self.the_cat.pronouns:
            checkname = self.the_cat.pronouns[n]['name']
            displayname = f"{self.the_cat.pronouns[n]['subject']}/"
            displayname += f"{self.the_cat.pronouns[n]['object']}/"
            displayname += f"{self.the_cat.pronouns[n]['inposs']}/"
            displayname += f"{self.the_cat.pronouns[n]['self']}"
            short_name = shorten_text_to_fit(displayname, 360, 26)

            # Create block for each pronounset with dynamic ycoor
            block_rect = scale(pygame.Rect((75, ycoor), (544, 88)))
            self.elements[checkname] = pygame_gui.elements.UIImage(
                block_rect,
                pygame.transform.scale(pygame.image.load(pronoun_frame).convert_alpha(), (272, 44)),
                container=self.checkboxes_text["container_general"], manager=MANAGER
            )

            # Create remove button for each pronounset with dynamic ycoor
            button_rect = scale(pygame.Rect((550, ycoor + 18), (48, 48)))
            self.removalbuttons[f"remove_button_{checkname}"] = UIImageButton(
                button_rect,
                "",
                container=self.checkboxes_text["container_general"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER)

            # Create UITextBox for pronoun display with clickable remove button
            text_box_rect = scale(pygame.Rect((100, ycoor + 4), (400, 78)))
            self.checkboxes_text[checkname] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.checkboxes_text["container_general"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER)

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            if short_name != displayname:
                self.buttons[f"{checkname}_tooltip"] = UIImageButton(
                    text_box_rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.checkboxes_text["container_general"],
                    tool_tip_text=displayname,
                    manager=MANAGER,
                    starting_height=2
                )
            else:
                self.buttons[f"{checkname}_tooltip"] = UIImageButton(
                    text_box_rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.checkboxes_text["container_general"],
                    manager=MANAGER,
                    starting_height=2
                )

            n += 1
            ycoor += 104

        if n == 1:
            for pronounset in self.the_cat.pronouns:
                checkname = pronounset['name']
                button_id = f"remove_button_{checkname}"
                if button_id in self.removalbuttons:
                    self.removalbuttons[button_id].disable()

        min_scrollable_height = max(100, n * 65)

        if game.settings['fullscreen']:
            self.checkboxes_text["container_general"].set_scrollable_area_dimensions(
                (310 * 2, min_scrollable_height * 2))
        else:
            self.checkboxes_text["container_general"].set_scrollable_area_dimensions((310, min_scrollable_height))

    def preset_removal(self):
        # List the various pronouns
        self.checkboxes_text["container_general2"] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=scale(pygame.Rect((795, 660), (675, 540))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER)

        self.checkboxes_text['instr2'] = pygame_gui.elements.UITextBox(
            "Saved Pronouns",
            scale(pygame.Rect((1000, 595), (350, 65))),
            object_id="#text_box_34_horizleft_dark",
            manager=MANAGER)

        n = 0
        ycoor = 8
        pronoun_frame = "resources/images/pronoun_frame.png"

        for pronounset in pronouns_dict["default_pronouns"]:
            checkname = pronouns_dict["default_pronouns"][n]['name'] + "preset"
            displayname = f"{pronouns_dict['default_pronouns'][n]['subject']}/"
            displayname += f"{pronouns_dict['default_pronouns'][n]['object']}/"
            displayname += f"{pronouns_dict['default_pronouns'][n]['inposs']}/"
            displayname += f"{pronouns_dict['default_pronouns'][n]['self']}"
            short_name = shorten_text_to_fit(displayname, 280, 26)

            # Create block for each pronounset with dynamic ycoor
            block_rect = scale(pygame.Rect((75, ycoor), (544, 88)))
            self.elements[checkname] = pygame_gui.elements.UIImage(
                block_rect,
                pygame.transform.scale(pygame.image.load(pronoun_frame).convert_alpha(), (272, 44)),
                container=self.checkboxes_text["container_general2"], manager=MANAGER
            )

            button_rect = scale(pygame.Rect((425, ycoor + 14), (112, 56)))
            self.buttons[f"add_button_{checkname}"] = UIImageButton(
                button_rect,
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#add_button",
                starting_height=2,
                manager=MANAGER)

            # Create UITextBox for pronoun display and create tooltip for full pronoun display
            button_rect = scale(pygame.Rect((550, ycoor + 18), (48, 48)))
            text_box_rect = scale(pygame.Rect((100, ycoor + 4), (400, 78)))
            self.checkboxes_text[checkname] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.checkboxes_text["container_general2"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER)

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            if short_name != displayname:
                self.buttons[f"{checkname}_tooltip"] = UIImageButton(
                    text_box_rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.checkboxes_text["container_general2"],
                    tool_tip_text=displayname,
                    manager=MANAGER,
                    starting_height=2
                )
            else:
                self.buttons[f"{checkname}_tooltip"] = UIImageButton(
                    text_box_rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.checkboxes_text["container_general2"],
                    manager=MANAGER,
                    starting_height=2
                )

            # Create remove button for each pronounset with dynamic ycoor
            self.removalbuttons[f"remove_button_{checkname}"] = UIImageButton(
                button_rect,
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER)
            # though we've made the remove button visible, it needs to be disabled so that the user cannnot remove
            # the defaults.  button is only visible here for UI consistency
            self.removalbuttons[f"remove_button_{checkname}"].disable()

            self.checkboxes_text[checkname].disable()
            n += 1
            ycoor += 104
        n = 0
        for pronounset in game.clan.custom_pronouns:
            checkname = game.clan.custom_pronouns[n]['name'] + "preset"
            displayname = f"{game.clan.custom_pronouns[n]['subject']}/"
            displayname += f"{game.clan.custom_pronouns[n]['object']}/"
            displayname += f"{game.clan.custom_pronouns[n]['inposs']}/"
            displayname += f"{game.clan.custom_pronouns[n]['self']}"
            short_name = shorten_text_to_fit(displayname, 280, 26)

            # Create block for each pronounset with dynamic ycoor
            block_rect = scale(pygame.Rect((75, ycoor), (544, 88)))
            self.elements[checkname] = pygame_gui.elements.UIImage(
                block_rect,
                pygame.transform.scale(pygame.image.load(pronoun_frame).convert_alpha(), (272, 44)),
                container=self.checkboxes_text["container_general2"], manager=MANAGER
            )

            # Create UITextBox for pronoun display with clickable remove button

            # Create remove button for each pronounset with dynamic ycoor
            button_rect = scale(pygame.Rect((550, ycoor + 18), (48, 48)))
            self.removalbuttons[f"remove_button_{checkname}"] = UIImageButton(
                button_rect,
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER)

            button_rect = scale(pygame.Rect((425, ycoor + 14), (112, 56)))
            self.buttons[f"add_button_{checkname}"] = UIImageButton(
                button_rect,
                "",
                container=self.checkboxes_text["container_general2"],
                object_id="#add_button",
                starting_height=2,
                manager=MANAGER)

            text_box_rect = scale(pygame.Rect((100, ycoor + 4), (400, 78)))
            self.checkboxes_text[checkname] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.checkboxes_text["container_general2"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER)

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            if short_name != displayname:
                self.buttons[f"{checkname}_tooltip"] = UIImageButton(
                    text_box_rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.checkboxes_text["container_general2"],
                    tool_tip_text=displayname,
                    manager=MANAGER,
                    starting_height=2
                )
            else:
                self.buttons[f"{checkname}_tooltip"] = UIImageButton(
                    text_box_rect,
                    "",
                    object_id="#blank_button_small",
                    container=self.checkboxes_text["container_general2"],
                    manager=MANAGER,
                    starting_height=2
                )

            self.checkboxes_text[checkname].disable()
            n += 1
            ycoor += 104
        min_scrollable_height = max(100, (n + 3) * 65)

        if game.settings['fullscreen']:
            self.checkboxes_text["container_general2"].set_scrollable_area_dimensions(
                (310 * 2, min_scrollable_height * 2))
        else:
            self.checkboxes_text["container_general2"].set_scrollable_area_dimensions((310, min_scrollable_height))

    def is_duplicate(self, preset):
        # checks to see if a preset with the same name is already in the cats pronouns
        for pronounset in self.the_cat.pronouns:
            if preset["name"] == pronounset["name"]:
                return True
        return False

    def reset_buttons_and_boxes(self):
        # kills everything when switching cats
        for ele in self.elements:
            self.elements[ele].kill()
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        for ele in self.buttons:
            self.buttons[ele].kill()
        for ele in self.checkboxes_text:
            self.checkboxes_text[ele].kill()
        for ele in self.removalbuttons:
            self.removalbuttons[ele].kill()

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
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        for ele in self.buttons:
            self.buttons[ele].kill()
        for ele in self.checkboxes_text:
            self.checkboxes_text[ele].kill()
        for ele in self.removalbuttons:
            self.removalbuttons[ele].kill()
