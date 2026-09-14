#!/usr/bin/env python3
# -*- coding: ascii -*-
from re import sub
from typing import Dict, Union

import i18n
import pygame
import pygame_gui
from pygame_gui.core import ObjectID, UIContainer

from scripts.cat.cats import Cat
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource
from ..ui.elements.cat_button import CatButton
from ..ui.elements.image_button import UIImageButton
from ..ui.elements.surface_image_button import UISurfaceImageButton
from ..ui.theme import get_text_box_theme
from ..events_module.text_adjust import shorten_text_to_fit
from ..cat import pronouns
from ..ui.scale import ui_scale, ui_scale_dimensions, ui_scale_offset, ui_scale_value
from .Screens import Screens
from .enums import GameScreen
from ..game_structure.game.switches import switch_get_value, switch_set_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.windows.pronoun_creation import PronounCreationWindow
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.generate_box import BoxStyles, get_box


class ChangeGenderScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.pronouns_dict = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.back_button = None
        self.the_cat = None
        self.next_cat = None
        self.previous_cat = None

        self.elements: Dict[
            str,
            Union[
                pygame_gui.elements.UIPanel,
                pygame_gui.core.UIElement,
                pygame_gui.core.IContainerLikeInterface,
            ],
        ] = {}
        self.windows = None


        self.cat_pronoun_elements = []
        self.cat_pronoun_removal_buttons = []

        self.saved_pronoun_elements = []
        self.saved_pronoun_removal_buttons = []
        self.saved_pronoun_add_buttons = []

        
        self.pronoun_template = pronouns.get_new_pronouns("default")
        self.current_pronouns = {}

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(GameScreen.PROFILE)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    self.update_selected_cat()
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    self.update_selected_cat()
            elif event.ui_element == self.buttons["save"]:
                if self.are_boxes_full():
                    gender_identity = self.get_new_identity()
                    self.the_cat.genderalign = gender_identity
                    self.the_cat.assign_thought()
                    self.selected_cat_elements["identity_changed"].show()
                    self.selected_cat_elements["cat_gender"].kill()
                    self.selected_cat_elements[
                        "cat_gender"
                    ] = pygame_gui.elements.UITextBox(
                        self.the_cat.genderalign_string,
                        ui_scale(pygame.Rect((126, 250), (250, 250))),
                        object_id=get_text_box_theme(
                            "#text_box_30_horizcenter_spacing_95"
                        ),
                        manager=MANAGER,
                    )

            elif event.ui_element == self.buttons["add_pronouns"]:
                PronounCreationWindow(self.the_cat)

            elif type(event.ui_element) is CatButton:
                if event.ui_element.cat_id == "add":
                    if event.ui_element.cat_object not in self.the_cat.pronouns:
                        self.the_cat.pronouns.append(event.ui_element.cat_object)
                        self.the_cat.assign_thought()
                elif event.ui_element.cat_id == "remove":
                    if (
                        event.ui_element.cat_object in self.the_cat.pronouns
                        and len(self.the_cat.pronouns) > 1
                    ):
                        self.the_cat.pronouns.remove(event.ui_element.cat_object)
                        self.the_cat.assign_thought()
                elif event.ui_element.cat_id == "delete":
                    if event.ui_element.cat_object in pronouns.get_custom_pronouns():
                        game.clan.custom_pronouns[i18n.config.get("locale")].remove(
                            event.ui_element.cat_object
                        )

                self.update_selected_cat()

    def screen_switches(self):
        super().screen_switches()

        temp = load_lang_resource("pronouns.{lang}.json")
        self.pronouns_dict = [
            pronoun_dict for pronoun_dict in temp[next(iter(temp))].values()
        ]

        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "buttons.next_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.previous_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.gender_box = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((336, 120), (298, 165))),
            get_box(BoxStyles.ROUNDED_BOX, (298, 165), sides=(True, True, False, False)),
            manager=MANAGER,
        )
        
        self.cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((170, 100), (170, 185))),
            get_box(BoxStyles.FRAME, (170, 185), sides=(True, True, False, True))
        )
        
        self.pronoun_background = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((50, 285), (699, 335))),
                get_box(BoxStyles.DARK_ROUNDED_BOX, (699, 335))
        )

        divider = pygame.transform.scale(
            pygame.image.load("resources/images/vertical_bar.png"),
            (10, 331)
        ) 

        self.divider_bar = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect(0, 2, 10, 331)),
            divider,
            anchors= {
                "centerx": "centerx",
                "centerx_target":  self.pronoun_background,
                "bottom": "bottom",
                "bottom_target": self.pronoun_background,
            }
        )

        self.current_pronoun_heading = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((56, 291), (337, 32))),
            "screens.change_gender.current_pronouns",
            object_id=ObjectID("#text_box_34_horizcenter", "#dark"),
            manager=MANAGER,
        )

        self.current_pronoun_scrolling_container = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((0, 5), (337, 270))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER,
            allow_scroll_x=False,
            anchors={
                "centerx": "centerx",
                "centerx_target": self.current_pronoun_heading,
                "top_target": self.current_pronoun_heading
            },
        )

        self.saved_pronoun_heading = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((407, 291), (337, 32))),
            "screens.change_gender.saved_pronouns",
            object_id=ObjectID("#text_box_34_horizcenter", "#dark"),
            manager=MANAGER
        )

        self.saved_pronoun_scrolling_container = pygame_gui.elements.UIScrollingContainer(
            relative_rect=ui_scale(pygame.Rect((0, 5), (337, 270))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER,
            allow_scroll_x=False,
            anchors={
                "centerx": "centerx",
                "centerx_target": self.saved_pronoun_heading,
                "top_target": self.saved_pronoun_heading
            },
        )

        self.description = pygame_gui.elements.UITextBox(
            "screens.change_gender.description",
            ui_scale(pygame.Rect((332, 132), (290, 75))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
        )

        self.add_pronoun_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((320, 645), (162, 30))),
            "screens.change_gender.add_pronouns",
            get_button_dict(ButtonStyles.SQUOVAL, (162, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.identity_change_confirmation = pygame_gui.elements.UITextBox(
            "screens.change_gender.identity_changed_confirmation",
            ui_scale(pygame.Rect((385, 247), (400, 40))),
            visible=False,
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
        )

        # Objects whose contents depend on the cat.. 

        # Includes cat's name - the text will be set with the rest of the cat's info. 
        self.header = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 62), (325, 32))),
            "",
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            anchors={"centerx": "centerx"},
        )

        self.current_cat_gender = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((130, 250), (250, 30))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.gender_entry_box = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((350, 220), (165, 30))),
            manager=MANAGER,
        )

        self.gender_save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((532, 220), (73, 30))),
            "buttons.save",
            get_button_dict(ButtonStyles.SQUOVAL, (73, 30)),
            object_id="@buttonstyles_squoval",
            starting_height=2,
            manager=MANAGER,
        )
        

        self.update_selected_cat()
        #self.set_cat_location_bg(self.the_cat)

    def display_change_save(self):
        variable_dict = super().display_change_save()
        variable_dict["cat_gender"] = self.selected_cat_elements["gender"].get_text()

        return variable_dict

    def display_change_load(self, variable_dict):
        super().display_change_load(variable_dict)
        self.selected_cat_elements["gender"].text = variable_dict["cat_gender"]

    def get_new_identity(self):
        new_gender_identity = [""]

        if (
            sub(r"[^A-Za-z0-9 ]+", "", self.selected_cat_elements["gender"].get_text())
            != ""
        ):
            new_gender_identity = sub(
                r"[^A-Za-z0-9 ]+", "", self.selected_cat_elements["gender"].get_text()
            )

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

    def update_selected_cat(self):
        self.reset_buttons_and_boxes()

        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        if not self.the_cat:
            return

        self.cat_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((180, 105), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        self.gender_entry_box.placeholder_text = self.the_cat.gender_string
        self.gender_entry_box.rebuild()

        self.current_cat_gender.set_text(self.the_cat.gender_string)

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()

        self.pronoun_update()
        self.preset_update()
        self.update_previous_next_cat_buttons()

    def pronoun_update(self):
        """ Updates the cat's list of current pronouns. """

        for pronounset in self.the_cat.pronouns:
            print(pronounset)

            pro_container =  self._generate_pronoun_box(pronounset, 
                                self.current_pronoun_scrolling_container,
                                self.cat_pronoun_elements[-1] if self.cat_pronoun_elements else None
                                )

            self.cat_pronoun_elements.append(pro_container)

            remove_butt = self._generate_removal_button(pro_container)
            self.cat_pronoun_removal_buttons.append(remove_butt)

        # Disable removing is a cat has only one pronoun.
        if len(self.the_cat.pronouns) <= 1:
            for button in self.cat_pronoun_removal_buttons:
                button.hide()

        """
        min_scrollable_height = ui_scale_value(max(100, len(self.the_cat.pronouns) * 65))

        self.current_pronouns["container_general"].set_scrollable_area_dimensions(
            ui_scale_dimensions((310, min_scrollable_height))
        )
        """

    def preset_update(self):

        all_pronouns = self.pronouns_dict + [
            x
            for x in pronouns.get_custom_pronouns()
            if x not in pronouns.get_default_pronouns().values()
        ]

        number_of_default = len(self.pronouns_dict)

        for n, pronounset in enumerate(all_pronouns):

            pro_container =  self._generate_pronoun_box(pronounset, 
                                            self.saved_pronoun_scrolling_container,
                                            self.saved_pronoun_elements[-1] if self.saved_pronoun_elements else None
                                            )
            
            self.saved_pronoun_elements.append(pro_container)

            # Create remove button
            remove_butt = None
            if n > number_of_default:
                remove_butt = self._generate_removal_button(pro_container)
                self.saved_pronoun_removal_buttons.append(remove_butt)

            add_butt = self._generate_add_button(pro_container)



        return

    @classmethod
    def _generate_pronoun_box(cls, pronoun_dict, container, above_box):

        displayname = cls.pronoun_get_cases(pronoun_dict)
        short_name = shorten_text_to_fit(displayname, 170, 13)

        # Create block for each pronounset
        block_size = (290, 45)
        block_rect = ui_scale(pygame.Rect((0, 0), (290, 45)))

        if above_box is None:
            anchors = {
                "centerx": "centerx"
            }
        else:
            anchors = {
                "centerx": "centerx",
                "top_target": above_box,
            }

        pronoun_container = UIContainer(
            block_rect,
            container=container,
            manager=MANAGER,
            anchors=anchors
        )

        pygame_gui.elements.UIImage(
            block_rect,
            get_box(BoxStyles.INNER_BOX, block_size),
            container=pronoun_container,
            manager=MANAGER,
        )

        text_box_rect = ui_scale(pygame.Rect((-20, 0), (200, -1)))
        pygame_gui.elements.UILabel(
            text_box_rect,
            short_name,
            object_id="#text_box_30_horizleft_pad_0_8",
            container=pronoun_container,
            manager=MANAGER,
            anchors={"center": "center"},
        )

        if short_name != displayname:
            UIImageButton(
                text_box_rect,
                "",
                object_id="#blank_button",
                container=pronoun_container,
                tool_tip_text=displayname,
                manager=MANAGER,
                starting_height=2,
                anchors={"center": "center"}
            )

        return pronoun_container

    @staticmethod
    def _generate_removal_button(container):

        button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
        button_rect.topright = ui_scale_offset((-10, 0))

        remove_butt = UIImageButton(
            button_rect,
            "",
            container=container,
            object_id="#exit_window_button",
            starting_height=2,
            manager=MANAGER,
            anchors={"centery": "centery", "right": "right"},
        )

        return remove_butt

    @staticmethod
    def _generate_add_button(container):

        button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
        button_rect.topright = ui_scale_offset((-10, 0))

        add_butt = UISurfaceImageButton(
                ui_scale(pygame.Rect((-59, 0), (56, 28))),
                "screens.change_gender.add_button",
                get_button_dict(ButtonStyles.SQUOVAL, (56, 28)),
                object_id="@buttonstyles_squoval",
                container=container,
                manager=MANAGER,
                anchors={
                    "centery": "centery",
                    "right": "right",
                }
            )

        return add_butt

    @staticmethod
    def pronoun_get_cases(pronounset) -> str:
        # Gets all pronoun cases in pronounset for display
        return "/".join(
            value
            for pronoun, value in pronounset.items()
            if pronoun not in ("conju", "gender", "ID")
        )

    def reset_buttons_and_boxes(self):
        # kills everything when switching cats
        for i in self.cat_pronoun_elements:
            i.kill()
        for i in self.saved_pronoun_elements:
            i.kill()


        self.cat_pronoun_elements = []
        self.cat_pronoun_removal_buttons = []

        self.saved_pronoun_elements = []
        self.saved_pronoun_removal_buttons = []
        self.saved_pronoun_add_buttons = []

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

        self.current_container.kill()
        self.saved_container.kill()
        self.reset_buttons_and_boxes()
