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
from scripts.game_structure.ui_elements import (
    UIImageButton,
    CatButton,
    UISurfaceImageButton,
)
from scripts.utility import (
    get_text_box_theme,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale_value,
    ui_scale_offset,
)
from scripts.utility import ui_scale
from .Screens import Screens
from ..game_structure import localization as pronouns
from ..game_structure.game.switches import switch_get_value, switch_set_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..game_structure.windows import PronounCreation
from ..ui.generate_button import get_button_dict, ButtonStyles


class ChangeGenderScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.pronouns_dict = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.back_button = None
        self.the_cat = None
        self.selected_cat_elements = {}
        self.buttons = {}
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
        self.removalboxes_text = {}
        self.removalbuttons = {}
        self.deletebuttons = {}
        self.addbuttons = {}
        self.pronoun_template = pronouns.get_new_pronouns("default")
        self.remove_button = {}
        self.removalboxes_text = {}
        self.boxes = {}
        self.box_labels = {}
        self.conju = 2
        self.current_container = None
        self.saved_container = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen("profile screen")
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
                    self.selected_cat_elements["identity_changed"].show()
                    self.selected_cat_elements["cat_gender"].kill()
                    self.selected_cat_elements[
                        "cat_gender"
                    ] = pygame_gui.elements.UITextBox(
                        self.the_cat.get_genderalign_string(),
                        ui_scale(pygame.Rect((126, 250), (250, 250))),
                        object_id=get_text_box_theme(
                            "#text_box_30_horizcenter_spacing_95"
                        ),
                        manager=MANAGER,
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
                    if (
                        event.ui_element.cat_object in self.the_cat.pronouns
                        and len(self.the_cat.pronouns) > 1
                    ):
                        self.the_cat.pronouns.remove(event.ui_element.cat_object)
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

        self.current_container = UIContainer(
            ui_scale(pygame.Rect((50, 285), (350, 335))),
            manager=MANAGER,
            starting_height=5,
        )

        self.saved_container = UIContainer(
            ui_scale(pygame.Rect((0, 285), (350, 335))),
            manager=MANAGER,
            starting_height=5,
            anchors={"left": "left", "left_target": self.current_container},
        )

        self.update_selected_cat()
        self.set_cat_location_bg(self.the_cat)

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

        self.elements["cat_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 100), (699, 520))),
            pygame.transform.scale(
                pygame.image.load(
                    "resources/images/gender_framing.png"
                ).convert_alpha(),
                ui_scale_dimensions((699, 520)),
            ),
            manager=MANAGER,
        )
        self.selected_cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((180, 105), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        # In what case would a cat have no genderalign? -key
        if not self.the_cat.genderalign:
            text = self.the_cat.get_gender_string()
        else:
            text = self.the_cat.get_genderalign_string()

        self.selected_cat_elements["cat_gender"] = pygame_gui.elements.UITextBox(
            text,
            ui_scale(pygame.Rect((130, 250), (250, 30))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.selected_cat_elements["header"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 62), (325, 32))),
            "screens.change_gender.heading",
            text_kwargs={"name": str(self.the_cat.name), "m_c": self.the_cat},
            object_id=get_text_box_theme("#text_box_40_horizcenter"),
            anchors={"centerx": "centerx"},
        )

        # Save Confirmation
        self.selected_cat_elements["identity_changed"] = pygame_gui.elements.UITextBox(
            "screens.change_gender.identity_changed_confirmation",
            ui_scale(pygame.Rect((385, 247), (400, 40))),
            visible=False,
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
        )

        self.selected_cat_elements["description"] = pygame_gui.elements.UITextBox(
            "screens.change_gender.description",
            ui_scale(pygame.Rect((332, 132), (290, 75))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
        )
        self.buttons["add_pronouns"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((320, 645), (162, 30))),
            "screens.change_gender.add_pronouns",
            get_button_dict(ButtonStyles.SQUOVAL, (162, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.selected_cat_elements["gender"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((350, 220), (165, 30))),
            placeholder_text=self.the_cat.get_genderalign_string(),
            manager=MANAGER,
        )
        self.buttons["save"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((532, 220), (73, 30))),
            "buttons.save",
            get_button_dict(ButtonStyles.SQUOVAL, (73, 30)),
            object_id="@buttonstyles_squoval",
            starting_height=2,
            manager=MANAGER,
        )
        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()
        self.pronoun_update()
        self.preset_update()
        self.update_previous_next_cat_buttons()

    def pronoun_update(self):
        self.removalboxes_text["instr"] = pygame_gui.elements.UITextBox(
            "screens.change_gender.current_pronouns",
            ui_scale(pygame.Rect((0, 10), (175, 32))),
            object_id=ObjectID("#text_box_34_horizcenter", "#dark"),
            manager=MANAGER,
            container=self.current_container,
            anchors={"centerx": "centerx"},
        )

        # List the various pronouns
        self.removalboxes_text[
            "container_general"
        ] = pygame_gui.elements.UIScrollingContainer(
            ui_scale(pygame.Rect((0, 5), (337, 270))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER,
            allow_scroll_x=False,
            container=self.current_container,
            anchors={
                "centerx": "centerx",
                "top_target": self.removalboxes_text["instr"],
            },
        )
        pronoun_frame = "resources/images/pronoun_frame.png"
        n = 0
        for pronounset in self.the_cat.pronouns:
            displayname = (
                f"{pronounset['subject']}/{pronounset['object']}/"
                f"{pronounset['inposs']}/{pronounset['self']}"
            )
            short_name = shorten_text_to_fit(displayname, 170, 13)

            # Create block for each pronounset
            block_rect = ui_scale(pygame.Rect((0, 0), (272, 45)))
            self.elements[f"cat_pronouns_{n}"] = pygame_gui.elements.UIPanel(
                block_rect,
                container=self.removalboxes_text["container_general"],
                manager=MANAGER,
                anchors=(
                    {
                        "centerx": "centerx",
                        "top_target": self.elements[f"cat_pronouns_{n - 1}"],
                    }
                    if n > 0
                    else {"centerx": "centerx"}
                ),
                margins={"left": 0, "right": 0, "top": ui_scale_value(2), "bottom": 0},
            )
            self.elements[
                f"cat_pronouns_{n}"
            ].background_image = pygame.transform.scale(
                pygame.image.load(pronoun_frame).convert_alpha(),
                ui_scale_dimensions((272, 44)),
            )
            self.elements[f"cat_pronouns_{n}"].rebuild()

            # Create remove button
            button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
            button_rect.topright = ui_scale_offset((-10, 0))
            self.removalbuttons[f"cat_pronouns_{n}"] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="remove",
                container=self.elements[f"cat_pronouns_{n}"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER,
                anchors={"centery": "centery", "right": "right"},
            )

            # Create UITextBox for pronoun display with clickable remove button
            text_box_rect = ui_scale(pygame.Rect((-20, 0), (200, -1)))
            self.removalboxes_text[f"cat_pronouns_{n}"] = pygame_gui.elements.UITextBox(
                short_name,
                text_box_rect,
                container=self.elements[f"cat_pronouns_{n}"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER,
                anchors={"center": "center"},
            )

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            self.buttons[f"{n}_tooltip_cat_pronouns"] = UIImageButton(
                self.removalboxes_text[f"cat_pronouns_{n}"].rect,
                "",
                object_id="#blank_button_small",
                container=self.elements[f"cat_pronouns_{n}"],
                tool_tip_text=displayname if short_name != displayname else None,
                manager=MANAGER,
                starting_height=2,
            )

            n += 1

        # Disable removing is a cat has only one pronoun.
        if n == 1:
            for button_id in self.removalbuttons:
                self.removalbuttons[button_id].disable()

        min_scrollable_height = ui_scale_value(max(100, n * 65))

        self.removalboxes_text["container_general"].set_scrollable_area_dimensions(
            ui_scale_dimensions((310, min_scrollable_height))
        )

    def preset_update(self):
        self.removalboxes_text["instr2"] = pygame_gui.elements.UITextBox(
            "screens.change_gender.saved_pronouns",
            ui_scale(pygame.Rect((0, 10), (175, 32))),
            object_id=ObjectID("#text_box_34_horizleft", "#dark"),
            manager=MANAGER,
            container=self.saved_container,
            anchors={"centerx": "centerx"},
        )
        # List the various pronouns
        self.removalboxes_text[
            "container_general2"
        ] = pygame_gui.elements.UIScrollingContainer(
            relative_rect=ui_scale(pygame.Rect((0, 5), (337, 270))),
            object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
            manager=MANAGER,
            allow_scroll_x=False,
            container=self.saved_container,
            anchors={
                "centerx": "centerx",
                "top_target": self.removalboxes_text["instr2"],
            },
        )

        n = 0
        pronoun_frame = "resources/images/pronoun_frame.png"

        all_pronouns = self.pronouns_dict + [
            x
            for x in pronouns.get_custom_pronouns()
            if x not in pronouns.get_default_pronouns().values()
        ]
        for pronounset in all_pronouns:
            displayname = (
                f"{pronounset['subject']}/{pronounset['object']}/"
                f"{pronounset['inposs']}/{pronounset['self']}"
            )
            short_name = shorten_text_to_fit(displayname, 140, 13)

            if pronounset in self.pronouns_dict:
                dict_name_core = f"default_pronouns_{n}"
            else:
                dict_name_core = f"custom_pronouns_{n}"

            # Create block for each pronounset
            block_rect = ui_scale(pygame.Rect((0, 0), (272, 45)))
            self.elements[f"{n}"] = pygame_gui.elements.UIPanel(
                block_rect,
                container=self.removalboxes_text["container_general2"],
                manager=MANAGER,
                anchors=(
                    {
                        "centerx": "centerx",
                        "top_target": self.elements[f"{n - 1}"],
                    }
                    if n > 0
                    else {"centerx": "centerx"}
                ),
                margins={"left": 0, "right": 0, "top": ui_scale_value(2), "bottom": 0},
            )
            self.elements[f"{n}"].background_image = pygame.transform.scale(
                pygame.image.load(pronoun_frame).convert_alpha(),
                ui_scale_dimensions((272, 44)),
            )
            self.elements[f"{n}"].rebuild()

            # Create remove button for each pronounset with dynamic ycoor
            button_rect = ui_scale(pygame.Rect((0, 0), (24, 24)))
            button_rect.topright = ui_scale_offset((-10, 0))
            self.deletebuttons[dict_name_core] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="delete",
                container=self.elements[f"{n}"],
                object_id="#exit_window_button",
                starting_height=2,
                manager=MANAGER,
                anchors={"centery": "centery", "right": "right"},
            )
            # though we've made the remove button visible, it needs to be disabled so that the user cannnot remove
            # the defaults.  button is only visible here for UI consistency
            if pronounset in self.pronouns_dict:
                self.deletebuttons[dict_name_core].disable()

            # the "add" button
            button_rect = ui_scale(pygame.Rect((0, 0), (56, 28)))
            button_rect.topright = ui_scale_dimensions((-5, 0))
            # TODO: update this to use UISurfaceImageButton
            self.addbuttons[dict_name_core] = CatButton(
                button_rect,
                "",
                cat_object=pronounset,
                cat_id="add",
                container=self.elements[f"{n}"],
                object_id="#add_button",
                starting_height=2,
                manager=MANAGER,
                anchors={
                    "centery": "centery",
                    "right": "right",
                    "right_target": self.deletebuttons[dict_name_core],
                },
            )

            if pronounset in self.the_cat.pronouns:
                self.addbuttons[dict_name_core].disable()

            # Create UITextBox for pronoun display and create tooltip for full pronoun display
            self.removalboxes_text[dict_name_core] = pygame_gui.elements.UITextBox(
                short_name,
                ui_scale(pygame.Rect((-20, 0), (200, -1))),
                container=self.elements[f"{n}"],
                object_id="#text_box_30_horizleft_pad_0_8",
                manager=MANAGER,
                anchors={"center": "center"},
            )

            self.removalboxes_text[dict_name_core].disable()

            # check if the pronoun set text had to be shortened, if it did then create a tooltip containing full
            # pronoun set text
            self.buttons["tooltip_" + dict_name_core] = UIImageButton(
                self.removalboxes_text[dict_name_core].rect,
                "",
                object_id="#blank_button_small",
                container=self.elements[f"{n}"],
                tool_tip_text=displayname if short_name != displayname else None,
                manager=MANAGER,
                starting_height=2,
            )

            n += 1

        min_scrollable_height = max(100, n * 65)

        self.removalboxes_text["container_general2"].set_scrollable_area_dimensions(
            (
                self.removalboxes_text["container_general2"].rect[2],
                ui_scale_value(min_scrollable_height),
            ),
        )

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
