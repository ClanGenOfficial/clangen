from math import ceil
from random import choice

import i18n
import pygame.transform
import pygame_gui.elements
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from scripts.game_structure import image_cache, game
from scripts.ui.elements.cat_list_display import UICatListDisplay
from ..ui.elements.relation_display import UIRelationDisplay
from ..ui.elements.sprite_button import UISpriteButton
from ..ui.elements.image_button import UIImageButton
from ..ui.elements.surface_image_button import UISurfaceImageButton
from ..ui.theme import get_text_box_theme
from ..events_module.text_adjust import shorten_text_to_fit
from ..ui.scale import ui_scale, ui_scale_dimensions
from .Screens import Screens
from .enums import GameScreen
from ..clan_package.settings import get_clan_setting
from ..game_structure.game.settings import game_setting_get
from ..game_structure.game.switches import switch_get_value, Switch
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_box import get_box, BoxStyles
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon
from scripts.cat_relations.enums import RelType, RelTier, rel_type_tiers


class RelationshipEditorScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.back_button = None
        self.selected_cat_1 = None
        self.selected_cat_2 = None
        self.search_bar = None
        self.search_bar_image = None
        self.rel_type_box = {}
        self.rel_type_buttons = {}
        self.rel_type_text = {}
        self.rel_change_inc = {}
        self.rel_change_dec = {}
        self.cat_buttons = []
        self.cat_display = None
        self.page = 1
        self.all_pages = 1
        self.selected_cat_elements = {}
        self.allow_romance = True
        self.current_listed_cats = None
        self.previous_search_text = ""

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.next_page:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page:
                self.page -= 1
                self.update_page()
            elif event.ui_element == self.deselect_1:
                self.selected_cat_1 = None
                self.update_selected_cats()
            elif event.ui_element == self.deselect_2:
                self.selected_cat_2 = None
                self.update_selected_cats()

            elif event.ui_element == self.rel_change_inc["like_increase"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.LIKE
                )
                self.update_selected_cats()
            elif event.ui_element == self.rel_change_dec["like_decrease"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.LIKE,
                    decrease=True
                )
                self.update_selected_cats()

            elif event.ui_element == self.rel_change_inc["respect_increase"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.RESPECT
                )
                self.update_selected_cats()
            elif event.ui_element == self.rel_change_dec["respect_decrease"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.RESPECT,
                    decrease=True
                )
                self.update_selected_cats()

            elif event.ui_element == self.rel_change_inc["trust_increase"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.TRUST
                )
                self.update_selected_cats()
            elif event.ui_element == self.rel_change_dec["trust_decrease"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.TRUST,
                    decrease=True
                )
                self.update_selected_cats()

            elif event.ui_element == self.rel_change_inc["comfort_increase"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.COMFORT
                )
                self.update_selected_cats()
            elif event.ui_element == self.rel_change_dec["comfort_decrease"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.COMFORT,
                    decrease=True
                )
                self.update_selected_cats()

            elif event.ui_element == self.rel_change_inc["romance_increase"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.ROMANCE
                )
                self.update_selected_cats()
            elif event.ui_element == self.rel_change_dec["romance_decrease"]:
                Cat.edit_relationship(
                    self.selected_cat_1,
                    self.selected_cat_2,
                    self.allow_romance,
                    rel_edit_type=RelType.ROMANCE,
                    decrease=True
                )
                self.update_selected_cats()

            elif event.ui_element == self.random1:
                self.selected_cat_1 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_2 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element == self.random2:
                self.selected_cat_2 = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.selected_cat_1 = self.random_cat()
                self.update_selected_cats()
            elif event.ui_element in self.cat_buttons:
                if event.ui_element.return_cat_object() not in (
                    self.selected_cat_1,
                    self.selected_cat_2,
                ):
                    if (
                        pygame.key.get_mods() & pygame.KMOD_SHIFT
                        or not self.selected_cat_1
                    ):
                        self.selected_cat_1 = event.ui_element.return_cat_object()
                    else:
                        self.selected_cat_2 = event.ui_element.return_cat_object()
                    self.update_selected_cats()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

        self.page = 1

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.selected_frame_1 = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 80), (200, 350))),
            get_box(BoxStyles.ROUNDED_BOX, (200, 350)),
        )
        self.selected_frame_1.disable()
        self.selected_frame_2 = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((550, 80), (200, 350))),
            get_box(BoxStyles.ROUNDED_BOX, (200, 350)),
        )
        self.selected_frame_2.disable()

        self.cat_bg = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 470), (700, 150))),
            get_box(BoxStyles.ROUNDED_BOX, (700, 150)),
        )
        self.cat_bg.disable()


        self.next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((433, 619), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.previous_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((333, 619), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )

        self.deselect_1 = UISurfaceImageButton(
            ui_scale(pygame.Rect((68, 434), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.deselect_2 = UISurfaceImageButton(
            ui_scale(pygame.Rect((605, 434), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (127, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.results = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 385), (229, 100))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.error = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((280, 37), (229, 57))),
            object_id=get_text_box_theme("#text_box_22_horizcenter_spacing_95"),
            manager=MANAGER,
        )

        self.random1 = UISurfaceImageButton(
            ui_scale(pygame.Rect((198, 432), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        self.random2 = UISurfaceImageButton(
            ui_scale(pygame.Rect((568, 432), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )

        self.search_bar_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((55, 625), (118, 34))),
            pygame.image.load("resources/images/search_bar.png").convert_alpha(),
            manager=MANAGER,
        )
        self.search_bar = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((60, 629), (115, 27))),
            object_id="#search_entry_box",
            placeholder_text="general.name_search",
            manager=MANAGER,
        )

        self.update_list_cats()
        self.update_rel_choices()

    def random_cat(self):
        if self.selected_cat_list():
            random_list = [
                i for i in self.all_cats_list if i.ID not in self.selected_cat_list()
            ]
        else:
            random_list = self.all_cats_list
        return choice(random_list)

    def update_rel_choices(self):
        for ele in self.rel_type_buttons:
            self.rel_type_buttons[ele].kill()
        self.rel_type_buttons = {}
        for ele in self.rel_type_text:
            self.rel_type_text[ele].kill()
        self.rel_type_text = {}
        for ele in self.rel_change_inc:
            self.rel_change_inc[ele].kill()
        self.rel_change_inc = {}
        for ele in self.rel_change_dec:
            self.rel_change_dec[ele].kill()
        self.rel_change_dec = {}


        self.rel_type_buttons["rel_choices_frame"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((275, 80), (252, 252))),
                get_box(BoxStyles.ROUNDED_BOX, (252, 252)),
            )

        self.rel_button_container = UIContainer(
                ui_scale(pygame.Rect((275, 80), (252, 252))),
                manager=MANAGER,
            )
        self.rel_type_box["like"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 36), (126, 36))),
            "Like",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 36))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
        )
        self.rel_change_inc["like_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 36), (48, 36))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 36)),
                object_id="@buttonstyles_profile_right",
                anchors={"right": "right", "right_target": self.rel_type_box["like"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["like_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,36), (48, 36))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 36)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["like"]},
                container=self.rel_button_container,
            )

        self.rel_type_box["respect"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 72), (126, 36))),
            "Respect",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 36))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
        )
        self.rel_change_inc["respect_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 72), (48, 36))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 36)),
                object_id="@buttonstyles_profile_right",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.rel_type_box["respect"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["respect_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,72), (48, 36))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 36)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["respect"]},
                container=self.rel_button_container,
            )


        self.rel_type_box["trust"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 108), (126, 36))),
            "Trust",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 36))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
        )
        self.rel_change_inc["trust_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 108), (48, 36))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 36)),
                object_id="@buttonstyles_profile_right",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.rel_type_box["trust"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["trust_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,108), (48, 36))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 36)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["trust"]},
                container=self.rel_button_container,
            )


        self.rel_type_box["comfort"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 144), (126, 36))),
            "Comfort",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 36))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
        )
        self.rel_change_inc["comfort_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 144), (48, 36))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 36)),
                object_id="@buttonstyles_profile_right",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.rel_type_box["comfort"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["comfort_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,144), (48, 36))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 36)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["comfort"]},
                container=self.rel_button_container,
            )


        self.rel_type_box["romance"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 180), (126, 46))),
            "Romantic Interest",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 46))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
        )
        self.rel_change_inc["romance_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 180), (48, 46))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 46)),
                object_id="@buttonstyles_profile_right",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.rel_type_box["romance"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["romance_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,180), (48, 46))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 46)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["romance"]},
                container=self.rel_button_container,
            )

        self.update_list_cats()

    def update_list_cats(self):
        self.all_cats_list = [
            i
            for i in Cat.all_cats_list
            if i.status.alive_in_player_clan
        ]
        self.all_cats = self.chunks(self.all_cats_list, 24)
        self.current_listed_cats = self.all_cats_list
        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )
        self.update_page()

    def update_page(self):
        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []
        if self.page > self.all_pages:
            self.page = self.all_pages
        elif self.page < 1:
            self.page = 1

        if self.page >= self.all_pages:
            self.next_page.disable()
        else:
            self.next_page.enable()

        if self.page <= 1:
            self.previous_page.disable()
        else:
            self.previous_page.enable()

        x = 65
        y = 485
        chunked_cats = self.chunks(self.current_listed_cats, 24)
        if chunked_cats:
            for cat in chunked_cats[self.page - 1]:
                if get_clan_setting("show fav") and cat.favourite:
                    _temp = pygame.transform.scale(
                        pygame.image.load(
                            f"resources/images/fav_marker.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((50, 50)),
                    )

                    self.cat_buttons.append(
                        pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((x, y), (50, 50))), _temp
                        )
                    )

                self.cat_buttons.append(
                    UISpriteButton(
                        ui_scale(pygame.Rect((x, y), (50, 50))),
                        cat.sprite,
                        cat_object=cat,
                    )
                )
                x += 55
                if x > 700:
                    y += 55
                    x = 65

    def update_selected_cats(self):
        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.draw_info_block(self.selected_cat_1, (50, 80))
        self.draw_info_block(self.selected_cat_2, (550, 80))


    def draw_info_block(self, cat, starting_pos: tuple):
        if not cat:
            return

        other_cat = [Cat.fetch_cat(i) for i in self.selected_cat_list() if i != cat.ID]
        if other_cat:
            other_cat = other_cat[0]
        else:
            other_cat = None

        tag = str(starting_pos)

        x = starting_pos[0]
        y = starting_pos[1]

        self.selected_cat_elements["cat_image" + tag] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x + 50, y + 7), (100, 100))),
            pygame.transform.scale(cat.sprite, ui_scale_dimensions((100, 100))),
        )

        name = str(cat.name)
        short_name = shorten_text_to_fit(name, 62, 7)
        self.selected_cat_elements["name" + tag] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((x, y + 100), (200, 30))),
            short_name,
            object_id="#text_box_30_horizcenter",
        )

        # Gender
        if cat.genderalign == "female":
            gender_icon = image_cache.load_image(
                "resources/images/female_big.png"
            ).convert_alpha()
        elif cat.genderalign == "male":
            gender_icon = image_cache.load_image(
                "resources/images/male_big.png"
            ).convert_alpha()
        elif cat.genderalign == "trans female":
            gender_icon = image_cache.load_image(
                "resources/images/transfem_big.png"
            ).convert_alpha()
        elif cat.genderalign == "trans male":
            gender_icon = image_cache.load_image(
                "resources/images/transmasc_big.png"
            ).convert_alpha()
        else:
            # Everyone else gets the nonbinary icon
            gender_icon = image_cache.load_image(
                "resources/images/nonbi_big.png"
            ).convert_alpha()

        self.selected_cat_elements["gender" + tag] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x + 160, y + 12), (25, 25))),
            pygame.transform.scale(gender_icon, ui_scale_dimensions((25, 25))),
        )

        related = False
        # MATE
        if other_cat and len(cat.mate) > 0 and other_cat.ID in cat.mate:
            self.selected_cat_elements["mate_icon" + tag] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x + 14, y + 14), (22, 20))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((44, 40)),
                ),
            )
        elif other_cat:
            # FAMILY DOT
            # Only show family dot on cousins if first cousin mates are disabled.
            if get_clan_setting("first cousin mates"):
                check_cousins = False
            else:
                check_cousins = other_cat.is_cousin(cat)

            if (
                other_cat.is_uncle_aunt(cat)
                or cat.is_uncle_aunt(other_cat)
                or other_cat.is_grandparent(cat)
                or cat.is_grandparent(other_cat)
                or other_cat.is_parent(cat)
                or cat.is_parent(other_cat)
                or other_cat.is_sibling(cat)
                or check_cousins
            ):
                related = True
                self.selected_cat_elements[
                    "relation_icon" + tag
                ] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((x + 14, y + 14), (18, 18))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/dot_big.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((18, 18)),
                    ),
                )

        col1 = i18n.t("general.moons_age", count=cat.moons)
        t = i18n.t(f"cat.personality.{cat.personality.trait}")
        if len(t) > 15:
            col1 += "\n" + t[:12] + "..."
        else:
            col1 += "\n" + t
        self.selected_cat_elements["col1" + tag] = pygame_gui.elements.UITextBox(
            col1,
            ui_scale(pygame.Rect((x + 21, y + 126), (90, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )
        self.selected_cat_elements["col1" + tag].disable()

        mates = False
        if len(cat.mate) > 0:
            col2 = i18n.t("general.has_a_mate")
            if other_cat:
                if other_cat.ID in cat.mate:
                    mates = True
                    col2 = i18n.t("general.cats_mate", name=other_cat.name)
        else:
            col2 = i18n.t("general.mate_none")

        self.selected_cat_elements["col2" + tag] = pygame_gui.elements.UITextBox(
            col2,
            ui_scale(pygame.Rect((x + 110, y + 126), (80, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )
        self.selected_cat_elements["col2" + tag].disable()

        # Relation info:
        if related and other_cat and not mates:
            relation = ""
            if cat.is_uncle_aunt(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.niece"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.nephew"
                else:
                    relation = "general.siblings_child"
            elif other_cat.is_uncle_aunt(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.aunt"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.uncle"
                else:
                    relation = "general.parents_sibling"
            elif other_cat.is_grandparent(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.grandmother"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.grandfather"
                else:
                    relation = "general.grandparent"
            elif cat.is_grandparent(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.granddaughter"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.grandson"
                else:
                    relation = "general.grandchild"
            elif other_cat.is_parent(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.mother"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.father"
                else:
                    relation = "general.parent"
            elif cat.is_parent(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.daughter"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.son"
                else:
                    relation = "general.child"
            elif other_cat.is_sibling(cat) or cat.is_sibling(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.sister"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.brother"
                else:
                    relation = "general.sibling"

                if other_cat.is_littermate(cat) or cat.is_littermate(other_cat):
                    relation = i18n.t(
                        "general.sibling_littermate", relation=i18n.t(relation)
                    )
            elif not get_clan_setting("first cousin mates") and other_cat.is_cousin(
                cat
            ):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.cousin_female"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.cousin_male"
                else:
                    relation = "general.cousin_nb"

            self.selected_cat_elements[
                "col2_relation" + tag
            ] = pygame_gui.elements.UITextBox(
                i18n.t("general.related_text"),
                ui_scale(pygame.Rect((x + 110, -15), (80, -1))),
                starting_height=3,
                object_id="#text_box_22_horizleft_spacing_95",
                manager=MANAGER,
                anchors={"top_target": self.selected_cat_elements["col2" + tag]},
            )
            self.selected_cat_elements["col2_relation" + tag].set_tooltip(
                text=i18n.t(relation)
            )
            self.selected_cat_elements["col2_relation" + tag].tool_tip_delay = 0
            self.selected_cat_elements["col2_relation" + tag].disable()

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        if other_cat:
            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 68, 11)

            self.selected_cat_elements[
                f"relation_heading{tag}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x + 20, y + 160), (160, -1))),
                "screens.mediation.cat_feelings",
                object_id="#text_box_22_horizcenter",
                text_kwargs={"name": short_name, "m_c": cat},
            )

            if other_cat.ID in cat.relationships:
                the_relationship = cat.relationships[other_cat.ID]
            else:
                the_relationship = cat.create_one_relationship(other_cat)

            # ROMANTIC LOVE
            # CHECK AGE DIFFERENCE
            same_age = the_relationship.cat_to.age == cat.age
            both_adult = (
                cat.age.can_have_mate() and the_relationship.cat_to.age.can_have_mate()
            )
            check_age = both_adult or same_age

            # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
            # even if they somehow have some. They should not be able to get any, but it never hurts to check.
            if not check_age or related:
                allow_romance = False
                self.rel_type_box["romance"].disable()
                self.rel_change_inc["romance_increase"].disable()
                self.rel_change_dec["romance_decrease"].disable()
                # Print, just for bug checking. Again, they should not be able to get love towards their relative.
                if the_relationship.romance and related:
                    print(
                        f"WARNING: {cat.name} has {the_relationship.romance} romantic love towards their relative, {the_relationship.cat_to.name}"
                    )
            else:
                allow_romance = True
                self.rel_type_box["romance"].enable()
                self.rel_change_inc["romance_increase"].enable()
                self.rel_change_dec["romance_decrease"].enable()

            self.selected_cat_elements[f"display{tag}"] = UIRelationDisplay(
                position=(x + 50, 0),
                relationship=the_relationship,
                romance=allow_romance,
                manager=MANAGER,
                anchors={
                    "top_target": self.selected_cat_elements[f"relation_heading{tag}"]
                },
            )

    def selected_cat_list(self):
        output = []
        if self.selected_cat_1:
            output.append(self.selected_cat_1.ID)
        if self.selected_cat_2:
            output.append(self.selected_cat_2.ID)

        return output

    def update_search_cats(self, search_text):
        """Run this function when the search text changes, or when the screen is switched to."""
        self.current_listed_cats = []
        Cat.sort_cats(self.all_cats_list)

        search_text = search_text.strip()
        if search_text not in (""):
            for cat in self.all_cats_list:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = self.all_cats_list.copy()

        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )

        Cat.ordered_cat_list = self.current_listed_cats
        self.update_page()

    def exit_screen(self):
        self.selected_cat_1 = None
        self.selected_cat_2 = None



        for ele in self.rel_type_buttons:
            self.rel_type_buttons[ele].kill()
        self.rel_type_buttons = {}

        for ele in self.rel_type_box:
            self.rel_type_box[ele].kill()
        self.rel_type_box = {}

        for ele in self.rel_change_inc:
            self.rel_change_inc[ele].kill()
        self.rel_change_inc = {}
        for ele in self.rel_change_dec:
            self.rel_change_dec[ele].kill()
        self.rel_change_dec = {}

        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}


        self.back_button.kill()
        del self.back_button
        self.selected_frame_1.kill()
        del self.selected_frame_1
        self.selected_frame_2.kill()
        del self.selected_frame_2
        self.cat_bg.kill()
        del self.cat_bg
        self.deselect_1.kill()
        del self.deselect_1
        self.deselect_2.kill()
        del self.deselect_2
        self.next_page.kill()
        del self.next_page
        self.previous_page.kill()
        del self.previous_page
        self.results.kill()
        del self.results
        self.random1.kill()
        del self.random1
        self.random2.kill()
        del self.random2
        self.error.kill()
        del self.error
        self.search_bar_image.kill()
        del self.search_bar_image
        self.search_bar.kill()
        del self.search_bar

    def on_use(self):
        super().on_use()
        # Only update the positions if the search text changes
        if self.search_bar.is_focused and self.search_bar.get_text() == "name search":
            self.search_bar.set_text("")
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()
