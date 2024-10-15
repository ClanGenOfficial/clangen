#!/usr/bin/env python3
# -*- coding: ascii -*-
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game
from scripts.game_structure.ui_elements import UIImageButton, UISurfaceImageButton
from scripts.utility import (
    generate_sprite,
    shorten_text_to_fit,
    ui_scale_dimensions,
    ui_scale_offset,
    get_text_box_theme,
)
from scripts.utility import ui_scale
from .Screens import Screens
from ..game_structure.screen_settings import MANAGER
from ..game_structure.windows import SaveAsImage
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.get_arrow import get_arrow


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

        # Image Settings:
        self.platform_shown = None
        self.displayed_lifestage = None
        self.scars_shown = True
        self.override_dead_lineart = False
        self.acc_shown = True
        self.override_not_working = False

        super().__init__(name)

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

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
                self.displayed_life_stage = min(
                    self.displayed_life_stage + 1, len(self.valid_life_stages) - 1
                )
                self.update_disabled_buttons()
                self.make_cat_image()
            elif event.ui_element == self.save_image_button:
                SaveAsImage(self.generate_image_to_save(), str(self.the_cat.name))
            elif event.ui_element == self.previous_life_stage:
                self.displayed_life_stage = max(self.displayed_life_stage - 1, 0)
                self.update_disabled_buttons()
                self.make_cat_image()
            elif event.ui_element == self.checkboxes["platform_shown"]:
                if self.platform_shown:
                    self.platform_shown = False
                else:
                    self.platform_shown = True

                self.set_background_visibility()
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
                self.the_cat.favourite = not self.the_cat.favourite
                self.cat_elements["favourite_button"].change_object_id(
                    "#fav_star" if self.the_cat.favourite else "#not_fav_star"
                )
                self.cat_elements["favourite_button"].set_tooltip(
                    "Remove favorite" if self.the_cat.favourite else "Mark as favorite"
                )

        return super().handle_event(event)

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "Next Cat " + get_arrow(3, arrow_left=False),
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            sound_id="page_flip",
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            get_arrow(2, arrow_left=True) + " Previous Cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            sound_id="page_flip",
        )
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            get_arrow(2) + " Back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.previous_life_stage = UIImageButton(
            ui_scale(pygame.Rect((75, 275), (38, 50))),
            "",
            object_id="#arrow_right_fancy",
            starting_height=2,
        )

        self.next_life_stage = UIImageButton(
            ui_scale(pygame.Rect((687, 275), (38, 50))),
            "",
            object_id="#arrow_left_fancy",
            starting_height=2,
        )

        self.save_image_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 95), (135, 30))),
            "Save as Image",
            get_button_dict(ButtonStyles.SQUOVAL, (135, 30)),
            object_id="@buttonstyles_squoval",
        )

        # Toggle Text:
        self.platform_shown_text = pygame_gui.elements.UITextBox(
            "Show Platform",
            ui_scale(pygame.Rect((150, 580), (-1, 50))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
        )
        self.scars_shown_text = pygame_gui.elements.UITextBox(
            "Show Scar(s)",
            ui_scale(pygame.Rect((350, 580), (-1, 50))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
        )
        self.acc_shown_text = pygame_gui.elements.UITextBox(
            "Show Accessory",
            ui_scale(pygame.Rect((545, 580), (-1, 50))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
        )
        self.override_dead_lineart_text = pygame_gui.elements.UITextBox(
            "Show as Living",
            ui_scale(pygame.Rect((250, 630), (-1, 50))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
        )
        self.override_not_working_text = pygame_gui.elements.UITextBox(
            "Show as Healthy",
            ui_scale(pygame.Rect((450, 630), (-1, 100))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
        )

        if game.clan.clan_settings["backgrounds"]:
            self.platform_shown = True
        else:
            self.platform_shown = False

        self.cat_setup()

    def cat_setup(self):
        """Sets up all the elements related to the cat"""
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}

        self.the_cat = Cat.fetch_cat(game.switches["cat"])

        self.cat_elements["platform"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((120, 100), (560, 490))),
            pygame.transform.scale(
                self.get_platform(), ui_scale_dimensions((560, 350))
            ),
            manager=MANAGER,
        )
        self.set_background_visibility()

        # Gather list of current and previous life states
        # "young adult", "adult", and "senior adult" all look the same: collapse to adult
        # This is not the best way to do it, so if we make them have difference appearances, this will
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

        # Store the index of the currently displayed life stage.
        self.displayed_life_stage = len(self.valid_life_stages) - 1

        # Reset all the toggles
        self.lifestage = None
        self.scars_shown = True
        self.override_dead_lineart = False
        self.acc_shown = True
        self.override_not_working = False

        # Make the cat image
        self.make_cat_image()

        cat_name = str(self.the_cat.name)  # name
        if self.the_cat.dead:
            cat_name += (
                " (dead)"  # A dead cat will have the (dead) sign next to their name
            )
        short_name = shorten_text_to_fit(cat_name, 195, 20)

        self.cat_elements["cat_name"] = pygame_gui.elements.UITextBox(
            cat_name,
            ui_scale(pygame.Rect((0, 0), (-1, 40))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            anchors={"centerx": "centerx"},
        )
        self.cat_elements["cat_name"].set_relative_position(ui_scale_offset((0, 60)))

        favorite_button_rect = ui_scale(pygame.Rect((0, 0), (28, 28)))
        favorite_button_rect.topright = ui_scale_offset((-10, 63))
        self.cat_elements["favourite_button"] = UIImageButton(
            favorite_button_rect,
            "",
            object_id="#fav_star" if self.the_cat.favourite else "#not_fav_star",
            manager=MANAGER,
            tool_tip_text="Remove favorite"
            if self.the_cat.favourite
            else "Mark as favorite",
            starting_height=2,
            anchors={"right": "right", "right_target": self.cat_elements["cat_name"]},
        )
        del favorite_button_rect

        # Write the checkboxes. The text is set up in switch_screens.
        self.update_checkboxes()

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()
        self.update_disabled_buttons()

    def update_checkboxes(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

        # "Show Platform"
        self.make_one_checkbox(
            ui_scale_offset((100, 575)), "platform_shown", self.platform_shown
        )

        # "Show Scars"
        self.make_one_checkbox(
            ui_scale_offset((300, 575)),
            "scars_shown",
            self.scars_shown,
            self.the_cat.pelt.scars,
        )

        # "Show accessories"
        self.make_one_checkbox(
            ui_scale_offset((500, 575)),
            "acc_shown",
            self.acc_shown,
            self.the_cat.pelt.accessory,
        )

        # "Show as living"
        self.make_one_checkbox(
            ui_scale_offset((200, 625)),
            "override_dead_lineart",
            self.override_dead_lineart,
            self.the_cat.dead,
            disabled_object_id="@checked_checkbox",
        )

        # "Show as healthy"
        self.make_one_checkbox(
            ui_scale_offset((400, 625)),
            "override_not_working",
            self.override_not_working,
            self.the_cat.not_working(),
            disabled_object_id="@checked_checkbox",
        )

    def make_one_checkbox(
        self,
        location: tuple,
        name: str,
        stored_bool: bool,
        cat_value_to_allow=True,
        disabled_object_id="@unchecked_checkbox",
    ):
        """Makes a single checkbox. So I don't have to copy and paste this 5 times.
        if cat_value_to_allow evaluates to False, then the unchecked checkbox is always used the the checkbox
        is disabled"""

        if not cat_value_to_allow:
            self.checkboxes[name] = UIImageButton(
                pygame.Rect(location, ui_scale_dimensions((50, 50))),
                "",
                object_id=disabled_object_id,
                starting_height=2,
            )
            self.checkboxes[name].disable()
        elif stored_bool:
            self.checkboxes[name] = UIImageButton(
                pygame.Rect(location, ui_scale_dimensions((50, 50))),
                "",
                object_id="@checked_checkbox",
                starting_height=2,
            )
        else:
            self.checkboxes[name] = UIImageButton(
                pygame.Rect(location, ui_scale_dimensions((50, 50))),
                "",
                object_id="@unchecked_checkbox",
                starting_height=2,
            )

    def make_cat_image(self):
        """Makes the cat image"""
        if "cat_image" in self.cat_elements:
            self.cat_elements["cat_image"].kill()

        self.cat_image = generate_sprite(
            self.the_cat,
            life_state=self.valid_life_stages[self.displayed_life_stage],
            scars_hidden=not self.scars_shown,
            acc_hidden=not self.acc_shown,
            always_living=self.override_dead_lineart,
            no_not_working=self.override_not_working,
        )

        self.cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((225, 100), (350, 350))),
            pygame.transform.scale(self.cat_image, ui_scale_dimensions((450, 450))),
        )

    def set_background_visibility(self):
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
        the_cat = Cat.all_cats.get(game.switches["cat"], game.clan.instructor)

        light_dark = "light"
        if game.settings["dark mode"]:
            light_dark = "dark"

        available_biome = ["Forest", "Mountainous", "Plains", "Beach"]
        biome = game.clan.biome

        if biome not in available_biome:
            biome = available_biome[0]
        if the_cat.age == "newborn" or the_cat.not_working():
            biome = "nest"

        biome = biome.lower()

        platformsheet = pygame.image.load(
            "resources/images/platforms.png"
        ).convert_alpha()

        order = ["beach", "forest", "mountainous", "nest", "plains", "SC/DF"]

        offset = 0
        if light_dark == "light":
            offset = 80

        if the_cat.df:
            biome_platforms = platformsheet.subsurface(
                pygame.Rect(0, order.index("SC/DF") * 70, 640, 70)
            )
            return biome_platforms.subsurface(pygame.Rect(0 + offset, 0, 80, 70))
        elif the_cat.dead or game.clan.instructor.ID == the_cat.ID:
            biome_platforms = platformsheet.subsurface(
                pygame.Rect(0, order.index("SC/DF") * 70, 640, 70)
            )
            return biome_platforms.subsurface(pygame.Rect(160 + offset, 0, 80, 70))
        else:
            biome_platforms = platformsheet.subsurface(
                pygame.Rect(0, order.index(biome) * 70, 640, 70)
            ).convert_alpha()
            season_x = {
                "greenleaf": 0 + offset,
                "leafbare": 160 + offset,
                "leaffall": 320 + offset,
                "newleaf": 480 + offset,
            }

            return biome_platforms.subsurface(
                pygame.Rect(
                    season_x.get(
                        game.clan.current_season.lower(), season_x["greenleaf"]
                    ),
                    0,
                    80,
                    70,
                )
            )

    def generate_image_to_save(self):
        """Generates the image to save, with platform if needed."""
        if self.platform_shown:
            full_image = self.get_platform()
            full_image.blit(self.cat_image, (15, 0))
            return full_image
        else:
            return self.cat_image
