#!/usr/bin/env python3
# -*- coding: ascii -*-
from re import sub

import i18n
import pygame
import pygame_gui
from pygame_gui.core import ObjectID, UIContainer

from scripts.cat.cats import Cat
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource
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

        self.pronouns_dict = {}
        self.cat_image = None

        self.cat_pronoun_elements = []
        self.saved_pronoun_elements = []
        self.cat_pronoun_removal_buttons = []
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
            elif event.ui_element == self.gender_save_button:
                if self.gender_entry_box.get_text():
                    self.the_cat.genderalign = self.gender_entry_box.get_text()
                    self.identity_change_confirmation.show()
                    self.update_selected_cat()

            elif event.ui_element == self.add_pronoun_button:
                PronounCreationWindow(self.the_cat)

            elif event.ui_element in self.saved_pronoun_add_buttons:
                pro = self.pronouns_dict + pronouns.get_custom_pronouns()

                index = self.saved_pronoun_add_buttons.index(event.ui_element)
                self.the_cat.pronouns.append(pro[index])
                self.the_cat.assign_thought()
                self.update_selected_cat()

            elif event.ui_element in self.cat_pronoun_removal_buttons:
                index = self.cat_pronoun_removal_buttons.index(event.ui_element)
                del self.the_cat.pronouns[index]
                self.update_selected_cat()

            elif event.ui_element in self.saved_pronoun_removal_buttons:
                index = self.saved_pronoun_removal_buttons.index(event.ui_element)
                del game.clan.custom_pronouns[i18n.config.get("locale")][index]
                self.preset_update()

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
            get_box(
                BoxStyles.ROUNDED_BOX, (298, 165), sides=(True, True, False, False)
            ),
            manager=MANAGER,
        )

        self.cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((170, 100), (170, 185))),
            get_box(BoxStyles.FRAME, (170, 185), sides=(True, True, False, True)),
        )

        self.pronoun_background = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 285), (699, 335))),
            get_box(BoxStyles.DARK_ROUNDED_BOX, (699, 335)),
        )

        divider = pygame.transform.scale(
            pygame.image.load("resources/images/vertical_bar.png"), (10, 331)
        )
        self.divider_bar = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect(0, 2, 10, 331)),
            divider,
            anchors={
                "centerx": "centerx",
                "centerx_target": self.pronoun_background,
                "bottom": "bottom",
                "bottom_target": self.pronoun_background,
            },
        )

        self.current_pronoun_heading = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((56, 291), (337, 32))),
            "screens.change_gender.current_pronouns",
            object_id=ObjectID("#text_box_34_horizcenter", "#dark"),
            manager=MANAGER,
        )

        self.help_button = UIImageButton(
            ui_scale(pygame.Rect((-34, 5), (34, 34))),
            "",
            object_id="#help_button",
            manager=MANAGER,
            tool_tip_text="screens.change_gender.help",
            anchors={
                "top": "top",
                "top_target": self.next_cat_button,
                "left": "left",
                "left_target": self.next_cat_button,
            },
        )

        self.current_pronoun_scrolling_container = (
            pygame_gui.elements.UIScrollingContainer(
                ui_scale(pygame.Rect((0, 5), (337, 270))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
                allow_scroll_x=False,
                anchors={
                    "centerx": "centerx",
                    "centerx_target": self.current_pronoun_heading,
                    "top_target": self.current_pronoun_heading,
                },
            )
        )

        self.saved_pronoun_heading = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((407, 291), (337, 32))),
            "screens.change_gender.saved_pronouns",
            object_id=ObjectID("#text_box_34_horizcenter", "#dark"),
            manager=MANAGER,
        )

        self.saved_pronoun_scrolling_container = (
            pygame_gui.elements.UIScrollingContainer(
                relative_rect=ui_scale(pygame.Rect((0, 5), (337, 270))),
                object_id=get_text_box_theme("#text_box_30_horizleft_pad_0_8"),
                manager=MANAGER,
                allow_scroll_x=False,
                anchors={
                    "centerx": "centerx",
                    "centerx_target": self.saved_pronoun_heading,
                    "top_target": self.saved_pronoun_heading,
                },
            )
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
            ui_scale(pygame.Rect((170, 250), (170, 35))),
            object_id=get_text_box_theme("#text_box_30_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.current_cat_gender_tooltip = UIImageButton(
            ui_scale(pygame.Rect((170, 250), (170, 35))),
            "",
            object_id="#blank_button",
            manager=MANAGER,
            visible=False,
        )

        self.gender_entry_box = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((350, 220), (165, 30))),
            manager=MANAGER,
        )
        self.gender_entry_box.set_text_length_limit(50)

        self.gender_save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((532, 220), (73, 30))),
            "buttons.save",
            get_button_dict(ButtonStyles.SQUOVAL, (73, 30)),
            object_id="@buttonstyles_squoval",
            starting_height=2,
            manager=MANAGER,
        )

        self.update_selected_cat()
        self.preset_update()

    def update_selected_cat(self):
        """Updated all elements when involved with the currently selected cat. Called when switching cats."""

        self.reset_cat_buttons_and_boxes()

        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        if not self.the_cat:
            return

        self.header.set_text(
            "screens.change_gender.heading",
            text_kwargs={"name": str(self.the_cat.name)},
        )

        # This is the one element I can't create at
        # screen creation, since it requires an image.
        if self.cat_image is not None:
            self.cat_image.kill()

        self.cat_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((180, 105), (150, 150))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((150, 150))
            ),
            manager=MANAGER,
        )

        self.gender_entry_box.placeholder_text = self.the_cat.genderalign_string
        self.gender_entry_box.rebuild()

        gender_text = shorten_text_to_fit(self.the_cat.genderalign_string, 230, 30)
        self.current_cat_gender.set_text(gender_text)
        if gender_text != self.the_cat.genderalign_string:
            self.current_cat_gender_tooltip.tool_tip_text = (
                self.the_cat.genderalign_string
            )
            self.current_cat_gender_tooltip.rebuild()
            self.current_cat_gender_tooltip.show()
        else:
            self.current_cat_gender_tooltip.hide()

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()

        self.pronoun_update()
        self.update_previous_next_cat_buttons()

    def pronoun_update(self):
        """Updates the cat's list of current pronouns."""

        number_of_pronouns = len(self.the_cat.pronouns)

        for pronounset in self.the_cat.pronouns:
            pro_container = self._generate_pronoun_box(
                pronounset,
                self.current_pronoun_scrolling_container,
                self.cat_pronoun_elements[-1] if self.cat_pronoun_elements else None,
            )

            self.cat_pronoun_elements.append(pro_container)

            if number_of_pronouns > 1:
                remove_butt = self._generate_removal_button(pro_container)
                self.cat_pronoun_removal_buttons.append(remove_butt)

        min_scrollable_height = ui_scale_value(
            max(100, len(self.the_cat.pronouns) * 45 + 5)
        )

        self.current_pronoun_scrolling_container.set_scrollable_area_dimensions(
            ui_scale_dimensions((310, min_scrollable_height))
        )

    def preset_update(self):
        """Updates the list of preset pronouns."""

        self.reset_preset_buttons_and_boxes()

        all_pronouns = self.pronouns_dict + pronouns.get_custom_pronouns()

        number_of_default = len(self.pronouns_dict)

        for n, pronounset in enumerate(all_pronouns):
            pro_container = self._generate_pronoun_box(
                pronounset,
                self.saved_pronoun_scrolling_container,
                self.saved_pronoun_elements[-1]
                if self.saved_pronoun_elements
                else None,
            )

            self.saved_pronoun_elements.append(pro_container)

            # Create remove button

            remove_butt = None
            if n >= number_of_default:
                remove_butt = self._generate_removal_button(pro_container)
                self.saved_pronoun_removal_buttons.append(remove_butt)

            add_butt = self._generate_add_button(pro_container, remove_butt)
            self.saved_pronoun_add_buttons.append(add_butt)

        min_scrollable_height = ui_scale_value(max(100, len(all_pronouns) * 45 + 5))

        self.saved_pronoun_scrolling_container.set_scrollable_area_dimensions(
            ui_scale_dimensions((310, min_scrollable_height))
        )

    @classmethod
    def _generate_pronoun_box(cls, pronoun_dict, container, above_box):
        displayname = cls.pronoun_get_cases(pronoun_dict)
        short_name = shorten_text_to_fit(displayname, 182, 15)

        # Create block for each pronounset
        block_size = (290, 45)
        block_rect = ui_scale(pygame.Rect((0, 0), block_size))

        if above_box is None:
            anchors = {"centerx": "centerx"}
        else:
            anchors = {
                "centerx": "centerx",
                "top_target": above_box,
            }

        pronoun_container = UIContainer(
            block_rect, container=container, manager=MANAGER, anchors=anchors
        )

        pygame_gui.elements.UIImage(
            block_rect,
            get_box(BoxStyles.INNER_BOX, block_size),
            container=pronoun_container,
            manager=MANAGER,
        )

        text_box_rect = ui_scale(pygame.Rect((15, 0), (190, 45)))
        pygame_gui.elements.UILabel(
            text_box_rect,
            short_name,
            object_id="#text_box_30_horizleft_pad_0_8",
            container=pronoun_container,
            manager=MANAGER,
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
    def _generate_add_button(container, right_anchor):
        x_pos = -65
        anchors = {"centery": "centery", "right": "right"}
        if right_anchor is not None:
            x_pos = -60
            anchors["right_target"] = right_anchor

        add_butt = UISurfaceImageButton(
            ui_scale(pygame.Rect((x_pos, 0), (56, 28))),
            "screens.change_gender.add_button",
            get_button_dict(ButtonStyles.SQUOVAL, (56, 28)),
            object_id="@buttonstyles_squoval",
            container=container,
            manager=MANAGER,
            anchors=anchors,
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

    def reset_cat_buttons_and_boxes(self):
        for i in self.cat_pronoun_elements:
            i.kill()

        self.cat_pronoun_elements = []
        self.cat_pronoun_removal_buttons = []

    def reset_preset_buttons_and_boxes(self):
        for i in self.saved_pronoun_elements:
            i.kill()

        self.saved_pronoun_elements = []
        self.saved_pronoun_removal_buttons = []
        self.saved_pronoun_add_buttons = []

    def exit_screen(self):
        # kill everything
        self.back_button.kill()
        self.back_button = None
        self.next_cat_button.kill()
        self.next_cat_button = None
        self.previous_cat_button.kill()
        self.previous_cat_button = None
        self.gender_box.kill()
        self.gender_box = None
        self.cat_frame.kill()
        self.cat_frame = None
        self.pronoun_background.kill()
        self.pronoun_background = None
        self.divider_bar.kill()
        self.divider_bar = None
        self.add_pronoun_button.kill()
        self.divider_bar = None
        self.current_cat_gender.kill()
        self.current_cat_gender = None
        self.gender_entry_box.kill()
        self.gender_entry_box = None
        self.gender_save_button.kill()
        self.gender_entry_box = None
        self.description.kill()
        self.description = None
        self.cat_image.kill()
        self.cat_image = None
        self.current_pronoun_heading.kill()
        self.current_pronoun_heading = None
        self.saved_pronoun_heading.kill()
        self.saved_pronoun_heading = None
        self.help_button.kill()
        self.help_button = None
        self.header.kill()
        self.header = None
        self.identity_change_confirmation.kill()
        self.identity_change_confirmation = None
        self.current_cat_gender_tooltip.kill()
        self.current_cat_gender_tooltip = None

        self.current_pronoun_scrolling_container.kill()
        self.saved_pronoun_scrolling_container.kill()
        self.reset_cat_buttons_and_boxes()
        self.reset_preset_buttons_and_boxes()
