#!/usr/bin/env python3
# -*- coding: ascii -*-
import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure import game, image_cache
from ..ui.elements.image_button import UIImageButton
from ..ui.elements.checkbox import UICheckbox
from ..ui.elements.surface_image_button import UISurfaceImageButton
from ..ui.theme import get_text_box_theme
from ..ui.elements.text_box_tweaked import UITextBoxTweaked
from ..events_module.text_adjust import shorten_text_to_fit
from ..ui.scale import ui_scale, ui_scale_dimensions, ui_scale_offset
from .Screens import Screens
from .enums import GameScreen
from ..cat.sprites.load_sprites import sprites
from scripts.cat.sprites.display_sprites import generate_sprite
from .enums import GameScreen
from ..clan_package.settings import get_clan_setting
from ..game_structure.game.switches import switch_set_value, switch_get_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.windows.save_as_image import SaveAsImageWindow
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.generate_box import BoxStyles, get_box


from ..ui.icon import Icon


class SpriteInspectScreen(Screens):
    cat_life_stages = ["newborn", "kitten", "adolescent", "adult", "senior"]
    sprite_settings = [
        "save_image",
        "show_platform",
        "show_scars",
        "show_accessory",
        "change_sprite",
    ]

    def __init__(self, name=None):
        self.elements = {}
        self.previous_cat = None
        self.next_cat = None
        self.the_cat = None
        self.cat_image = None
        self.cat_elements = {}
        self.life_stage_elements = {}
        self.sprite_detail_elements = {}
        self.checkboxes = {}
        self.textboxes = {}
        self.platform_shown_text = None
        self.scars_shown = None
        self.acc_shown_text = None
        self.override_dead_lineart_text = None
        self.override_not_working_text = None
        self.open_tab = None

        # Image Settings:
        self.platform_shown = None
        self.displayed_life_stage = None
        self.scars_shown = True
        self.override_dead_lineart = False
        self.acc_shown = True
        self.override_not_working = False

        super().__init__(name)

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.elements["back_button"]:
                self.change_screen(GameScreen.PROFILE)
            elif event.ui_element == self.elements["next_cat_button"]:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    for ele in self.textboxes:
                        self.textboxes[ele].kill()
                    self.textboxes = {}
                    self.cat_setup()
                    if self.open_tab == self.elements["life_stages_tab"]:
                        self.update_disabled_life_stages()
                    elif self.open_tab == self.elements["sprite_details_tab"]:
                        self.update_disabled_buttons()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.elements["previous_cat_button"]:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    for ele in self.textboxes:
                        self.textboxes[ele].kill()
                    self.textboxes = {}
                    self.cat_setup()
                    if self.open_tab == self.elements["life_stages_tab"]:
                        self.update_disabled_life_stages()
                    elif self.open_tab == self.elements["sprite_details_tab"]:
                        self.update_disabled_buttons()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.elements["save_image_button"]:
                SaveAsImageWindow(self.generate_image_to_save(), str(self.the_cat.name))
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
                self.checkboxes["scars_shown"].toggle()
            elif event.ui_element == self.checkboxes["acc_shown"]:
                if self.acc_shown:
                    self.acc_shown = False
                else:
                    self.acc_shown = True

                self.make_cat_image()
                self.checkboxes["acc_shown"].toggle()
            elif event.ui_element == self.checkboxes["show_default_sprite"]:
                if self.the_cat.dead:
                    if self.override_dead_lineart:
                        self.override_dead_lineart = False
                    else:
                        self.override_dead_lineart = True
                else:
                    if self.override_not_working:
                        self.override_not_working = False
                    else:
                        self.override_not_working = True
                self.make_cat_image()
                self.checkboxes["show_default_sprite"].toggle()
            elif event.ui_element == self.cat_elements["favourite_button"]:
                self.the_cat.favourite = not self.the_cat.favourite
                self.cat_elements["favourite_button"].change_object_id(
                    "#fav_star" if self.the_cat.favourite else "#not_fav_star"
                )
                self.cat_elements["favourite_button"].set_tooltip(
                    "Remove favorite" if self.the_cat.favourite else "Mark as favorite"
                )
            elif event.ui_element == self.elements["sprite_details_tab"]:
                self.switch_tab_sprite_details()
            elif event.ui_element == self.elements["life_stages_tab"]:
                self.switch_tab_life_stages()
            if self.open_tab == self.elements["life_stages_tab"]:
                if event.ui_element == self.life_stage_elements["button_0"]:
                    self.displayed_life_stage = 0
                    self.make_cat_image()
                    self.update_disabled_life_stages()
                elif event.ui_element == self.life_stage_elements["button_1"]:
                    self.displayed_life_stage = 1
                    self.make_cat_image()
                    self.update_disabled_life_stages()
                elif event.ui_element == self.life_stage_elements["button_2"]:
                    self.displayed_life_stage = 2
                    self.make_cat_image()
                    self.update_disabled_life_stages()
                elif event.ui_element == self.life_stage_elements["button_3"]:
                    self.displayed_life_stage = 3
                    self.make_cat_image()
                    self.update_disabled_life_stages()
                elif event.ui_element == self.life_stage_elements["button_4"]:
                    self.displayed_life_stage = 4
                    self.make_cat_image()
                    self.update_disabled_life_stages()

        return super().handle_event(event)

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

        self.elements["next_cat_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "buttons.next_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            sound_id="page_flip",
        )
        self.elements["previous_cat_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.previous_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            sound_id="page_flip",
        )
        self.elements["back_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.elements["checkbox_frame_container"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((45, 480), (195, 176))),
            manager=MANAGER,
        )

        self.elements["checkbox_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((45, 480), (195, 176))),
            get_box(BoxStyles.FRAME, (226, 176)),
            manager=MANAGER,
        )

        self.elements["life_stages_container"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((10, 485), (483, 160))),
            anchors={"left_target": self.elements["checkbox_frame"]},
            manager=MANAGER,
        )

        self.elements["life_stages_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((10, 485), (491, 160))),
            get_box(BoxStyles.ROUNDED_BOX, (491, 160)),
            manager=MANAGER,
            anchors={"left_target": self.elements["checkbox_frame"]},
            starting_height=3,
        )
        self.elements["life_stages_frame"].disable()

        self.elements["life_stages_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((-130, -190), (120, 34))),
            "screens.sprite_inspect.life_stages",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (120, 34)),
            object_id="@buttonstyles_horizontal_tab",
            anchors={
                "top_target": self.elements["life_stages_frame"],
                "left_target": self.elements["life_stages_frame"],
            },
            starting_height=4,
        )
        self.elements["sprite_details_tab"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((-255, -190), (120, 34))),
            "screens.sprite_inspect.sprite_details",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (120, 34)),
            object_id="@buttonstyles_horizontal_tab",
            anchors={
                "top_target": self.elements["life_stages_frame"],
                "left_target": self.elements["life_stages_frame"],
            },
            starting_height=4,
        )

        self.elements["save_image_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((-135, 5), (135, 30))),
            "screens.sprite_inspect.save_image",
            get_button_dict(ButtonStyles.SQUOVAL, (135, 30)),
            object_id="@buttonstyles_squoval",
            anchors={
                "top_target": self.elements["next_cat_button"],
                "left_target": self.elements["next_cat_button"],
            },
        )

        self.platform_shown = get_clan_setting("backgrounds")
        self.cat_setup()

        if self.open_tab == self.elements["sprite_details_tab"]:
            self.switch_tab_sprite_details()
        else:
            self.switch_tab_life_stages()
            self.update_disabled_life_stages()

    def cat_setup(self):
        """Sets up all the elements related to the cat"""
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}

        self.the_cat = Cat.fetch_cat(switch_get_value(Switch.cat))

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()

        (
            self.elements["next_cat_button"].disable()
            if self.next_cat == 0
            else self.elements["next_cat_button"].enable()
        )
        (
            self.elements["previous_cat_button"].disable()
            if self.previous_cat == 0
            else self.elements["previous_cat_button"].enable()
        )

        self.cat_elements["container"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((94, 5), (600, 600))),
            manager=MANAGER,
        )

        self.cat_elements["platform"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (560, 490))),
            pygame.transform.scale(
                sprites.get_platform(
                    biome=game.clan.override_biome
                    if game.clan.override_biome
                    else game.clan.biome,
                    season=game.clan.current_season,
                    show_nest=self.the_cat.age == "newborn"
                    or self.the_cat.not_working(),
                    group=self.the_cat.status.group,
                ),
                ui_scale_dimensions((560, 350)),
            ),
            manager=MANAGER,
            anchors={"centerx": "centerx", "centery": "centery"},
            container=self.cat_elements["container"],
        )
        self.set_background_visibility()

        # Gather list of current and previous life states
        # "young adult", "adult", and "senior adult" all look the same: collapse to adult
        # This is not the best way to do it, so if we make them have difference appearances, this will
        # need to be changed/removed.
        if self.the_cat.age in ("young adult", "adult", "senior adult"):
            current_life_stage = "adult"
        else:
            current_life_stage = self.the_cat.age

        self.valid_life_stages = []
        for i, life_stage in enumerate(SpriteInspectScreen.cat_life_stages):
            if self.the_cat.dead:
                self.valid_life_stages.append(life_stage)
                if life_stage == current_life_stage:
                    self.displayed_life_stage = i
            else:
                self.valid_life_stages.append(life_stage)
                if life_stage == current_life_stage:
                    break

        # Store the index of the currently displayed life stage.
        if not self.the_cat.dead:
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
            cat_name = i18n.t("general.dead_label", name=cat_name)
        short_name = shorten_text_to_fit(cat_name, 195, 20)

        self.cat_elements["cat_name"] = pygame_gui.elements.UITextBox(
            cat_name,
            ui_scale(pygame.Rect((0, 0), (-1, 40))),
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            anchors={
                "centerx": "centerx",
                "bottom_target": self.cat_elements["platform"],
            },
            container=self.cat_elements["container"],
        )
        self.cat_elements["cat_name"].set_relative_position(ui_scale_offset((0, 20)))

        favorite_button_rect = ui_scale(pygame.Rect((0, 0), (28, 28)))
        favorite_button_rect.topright = ui_scale_offset((0, 23))
        self.cat_elements["favourite_button"] = UIImageButton(
            favorite_button_rect,
            "",
            object_id="#fav_star" if self.the_cat.favourite else "#not_fav_star",
            manager=MANAGER,
            tool_tip_text=(
                "general.remove_favorite"
                if self.the_cat.favourite
                else "general.mark_favorite"
            ),
            starting_height=2,
            anchors={"right": "right", "right_target": self.cat_elements["cat_name"]},
            container=self.cat_elements["container"],
        )
        del favorite_button_rect

        # Write the checkboxes. The text is set up in switch_screens.
        self.update_checkboxes()
        self.update_textboxes()

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats()
        if self.open_tab == self.elements["life_stages_tab"]:
            self.update_disabled_life_stages()
        self.update_disabled_buttons()

    def update_checkboxes(self):
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

        # "Show Platform"
        self.checkboxes["platform_shown"] = UICheckbox(
            position=(10, 15),
            manager=MANAGER,
            check=self.platform_shown,
            container=self.elements["checkbox_frame_container"],
        )

        # "Show Scars"
        self.checkboxes["scars_shown"] = UICheckbox(
            position=(10, 0),
            manager=MANAGER,
            check=self.scars_shown,
            container=self.elements["checkbox_frame_container"],
            anchors={"top_target": self.checkboxes["platform_shown"]},
        )
        if not self.the_cat.pelt.scars:
            self.checkboxes["scars_shown"].disable()

        # "Show accessories"
        self.checkboxes["acc_shown"] = UICheckbox(
            position=(10, 0),
            manager=MANAGER,
            check=self.acc_shown,
            container=self.elements["checkbox_frame_container"],
            anchors={"top_target": self.checkboxes["scars_shown"]},
        )
        if not self.the_cat.pelt.accessory:
            self.checkboxes["acc_shown"].disable()

        default_sprite_check = None
        if self.the_cat.is_alive():
            default_sprite_check = self.override_not_working
        else:
            default_sprite_check = self.override_dead_lineart

        # "Show as living"
        self.checkboxes["show_default_sprite"] = UICheckbox(
            position=(10, 0),
            manager=MANAGER,
            check=default_sprite_check,
            container=self.elements["checkbox_frame_container"],
            anchors={"top_target": self.checkboxes["acc_shown"]},
        )
        if not self.the_cat.dead:
            if not self.the_cat.not_working():
                self.checkboxes["show_default_sprite"].disable()

    def update_textboxes(self):
        # Toggle Text:
        self.textboxes["platform_shown_text"] = pygame_gui.elements.UITextBox(
            "screens.sprite_inspect.show_platform",
            ui_scale(pygame.Rect((-6, -36), (-1, 50))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
            container=self.elements["checkbox_frame_container"],
            anchors={
                "top_target": self.checkboxes["platform_shown"],
                "left_target": self.checkboxes["platform_shown"],
            },
        )
        self.textboxes["scars_shown_text"] = pygame_gui.elements.UITextBox(
            "screens.sprite_inspect.show_scars",
            ui_scale(pygame.Rect((-6, -36), (-1, 50))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
            container=self.elements["checkbox_frame_container"],
            anchors={
                "top_target": self.checkboxes["scars_shown"],
                "left_target": self.checkboxes["scars_shown"],
            },
        )
        self.textboxes["acc_shown_text"] = pygame_gui.elements.UITextBox(
            "screens.sprite_inspect.show_accessory",
            ui_scale(pygame.Rect((-6, -36), (-1, 50))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
            container=self.elements["checkbox_frame_container"],
            anchors={
                "top_target": self.checkboxes["acc_shown"],
                "left_target": self.checkboxes["acc_shown"],
            },
        )
        self.textboxes["show_defailt_sprite_text"] = pygame_gui.elements.UITextBox(
            "screens.sprite_inspect.show_healthy"
            if self.the_cat.is_alive()
            else "screens.sprite_inspect.show_living",
            ui_scale(pygame.Rect((-6, -36), (-1, 50))),
            object_id=get_text_box_theme("#text_box_34_horizcenter"),
            starting_height=2,
            container=self.elements["checkbox_frame_container"],
            anchors={
                "top_target": self.checkboxes["show_default_sprite"],
                "left_target": self.checkboxes["show_default_sprite"],
            },
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
            disable_sick_sprite=self.override_not_working,
        )

        self.cat_elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, -70), (350, 350))),
            pygame.transform.scale(self.cat_image, ui_scale_dimensions((450, 450))),
            anchors={
                "bottom_target": self.cat_elements["platform"],
                "centerx": "centerx",
                "centery": "centery",
            },
            container=self.cat_elements["container"],
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
        self.scars_shown = None

        for ele in self.elements:
            self.elements[ele].kill()
        self.elements = {}
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}
        for ele in self.textboxes:
            self.textboxes[ele].kill()

        return super().exit_screen()

    def update_disabled_buttons(self):
        for ele in self.sprite_detail_elements:
            self.sprite_detail_elements[ele].kill()
        self.sprite_detail_elements = {}
        self.update_previous_next_cat_buttons()

        if self.open_tab == self.elements["sprite_details_tab"]:
            self.sprite_detail_elements["textbox"] = UITextBoxTweaked(
                self.get_sprite_details(),
                ui_scale(pygame.Rect((8, 5), (480, 150))),
                object_id="#text_box_26_horizleft_pad_10_14",
                line_spacing=1,
                manager=MANAGER,
                starting_height=6,
                container=self.elements["life_stages_container"],
            )

    def switch_tab_life_stages(self):
        self.open_tab = self.elements["life_stages_tab"]
        self.elements["life_stages_tab"].disable()
        self.elements["sprite_details_tab"].enable()

        for ele in self.sprite_detail_elements:
            self.sprite_detail_elements[ele].kill()
        self.sprite_detail_elements = {}

        prev_container = None
        for i, age in enumerate(SpriteInspectScreen.cat_life_stages):
            self.life_stage_elements[f"container{i}"] = pygame_gui.core.UIContainer(
                ui_scale(pygame.Rect((0 if prev_container else 8, 0), (95, 160))),
                starting_height=1,
                container=self.elements["life_stages_container"],
                anchors={"left_target": prev_container} if prev_container else None,
                manager=MANAGER,
            )
            self.life_stage_elements[f"button_{i}"] = UIImageButton(
                ui_scale(pygame.Rect((0, 0), (93, 139))),
                "",
                object_id="#other_clan_select_button",
                starting_height=5,
                container=self.life_stage_elements[f"container{i}"],
                manager=MANAGER,
                anchors={"centerx": "centerx", "centery": "centery"},
            )

            self.life_stage_elements[f"age_frame{i}"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, 0), (97, 144))),
                get_box(BoxStyles.NAMEPLATE, (97, 144)),
                container=self.life_stage_elements[f"container{i}"],
                manager=MANAGER,
                anchors={"center": "center"},
            )

            self.life_stage_elements[f"age_symbol_box{i}"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, -30), (44, 44))),
                "",
                get_button_dict(ButtonStyles.ICON, (44, 44)),
                object_id="@buttonstyles_icon",
                container=self.life_stage_elements[f"container{i}"],
                manager=MANAGER,
                anchors={
                    "center": "center",
                },
            )

            self.life_stage_elements[f"age_symbol{i}"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((0, -30), (34, 34))),
                pygame.transform.scale(
                    image_cache.load_image(
                        f"resources/images/icon_spritescreen_age_{age}.png"
                    ),
                    ui_scale_dimensions((34, 34)),
                ),
                starting_height=2,
                container=self.life_stage_elements[f"container{i}"],
                manager=MANAGER,
                anchors={"center": "center"},
            )

            self.life_stage_elements[f"age_name{i}"] = pygame_gui.elements.UITextBox(
                f"screens.sprite_inspect.life_stage_{age}",
                ui_scale(pygame.Rect((0, 10), (95, -1))),
                object_id=get_text_box_theme("#text_box_26_horizcenter"),
                container=self.life_stage_elements[f"container{i}"],
                manager=MANAGER,
                anchors={
                    "centerx": "centerx",
                    "top_target": self.life_stage_elements[f"age_symbol{i}"],
                },
            )
            prev_container = self.life_stage_elements[f"container{i}"]
        self.update_disabled_life_stages()

    def update_disabled_life_stages(self):
        for i in range(len(SpriteInspectScreen.cat_life_stages)):
            if i == self.displayed_life_stage:
                self.life_stage_elements[f"age_symbol_box{i}"].enable()
                self.life_stage_elements[f"age_symbol{i}"].show()
                self.life_stage_elements[f"button_{i}"].disable()
                self.life_stage_elements[f"button_{i}"].show()
            elif i > (len(self.valid_life_stages) - 1):
                self.life_stage_elements[f"age_symbol_box{i}"].disable()
                self.life_stage_elements[f"age_symbol{i}"].hide()
                self.life_stage_elements[f"button_{i}"].disable()
                self.life_stage_elements[f"button_{i}"].hide()
            else:
                self.life_stage_elements[f"age_symbol_box{i}"].enable()
                self.life_stage_elements[f"age_symbol{i}"].show()
                self.life_stage_elements[f"button_{i}"].enable()
                self.life_stage_elements[f"button_{i}"].show()

    def switch_tab_sprite_details(self):
        self.open_tab = self.elements["sprite_details_tab"]
        self.elements["sprite_details_tab"].disable()
        self.elements["life_stages_tab"].enable()

        for ele in self.life_stage_elements:
            self.life_stage_elements[ele].kill()
        self.life_stage_elements = {}

        self.sprite_detail_elements["textbox"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, 0), (491, 160))),
            manager=MANAGER,
            container=self.elements["life_stages_container"],
        )

        self.update_disabled_buttons()

    def get_sprite_details(self):
        output = ""

        # PELT COLOR
        output += i18n.t("screens.sprite_inspect.pelt_color_label")
        output += self.the_cat.pelt.colour.lower()

        # TORTIE PATCH
        if self.the_cat.pelt.tortie_marking:
            output += "\n"
            output += i18n.t("screens.sprite_inspect.tortie_patch_label")
            output += self.the_cat.pelt.tortie_marking.lower()

        # PELT TINT
        if self.the_cat.pelt.tint:
            output += "\n"
            output += i18n.t("screens.sprite_inspect.tint_color_label")
            output += self.the_cat.pelt.tint

        # WHITE PATCH
        if self.the_cat.pelt.white_patches:
            output += "\n"
            output += i18n.t("screens.sprite_inspect.white_patches_label")
            output += self.the_cat.pelt.white_patches.lower()

        # WHITE PATCH TINT
        if self.the_cat.pelt.white_patches_tint:
            output += "\n"
            output += i18n.t("screens.sprite_inspect.white_patches_tint_label")
            output += self.the_cat.pelt.white_patches_tint.lower()

        # POINTS
        if self.the_cat.pelt.points:
            output += "\n"
            output += i18n.t("screens.sprite_inspect.points_label")
            output += self.the_cat.pelt.points.lower()

        # VITILIGO PATCH
        if self.the_cat.pelt.vitiligo:
            output += "\n"
            output += i18n.t("screens.sprite_inspect.vitiligo_patch_label")
            output += self.the_cat.pelt.vitiligo.lower()

        output += "\n"

        # SKIN COLOR
        output += i18n.t("screens.sprite_inspect.skin_color_label")
        output += self.the_cat.pelt.skin.lower()

        return output

    def generate_image_to_save(self):
        """Generates the image to save, with platform if needed."""
        if self.platform_shown:
            full_image = sprites.get_platform(
                biome=game.clan.override_biome
                if game.clan.override_biome
                else game.clan.biome,
                season=game.clan.current_season,
                show_nest=self.the_cat.age == "newborn" or self.the_cat.not_working(),
                group=self.the_cat.status.group,
            )
            full_image.blit(self.cat_image, (15, 0))
            return full_image
        else:
            return self.cat_image
