from typing import Optional

import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure import image_cache, game, constants
from scripts.game_structure.game import switch_get_value, Switch
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.Screens import Screens
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.search_bar import UISearchBar
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import BoxStyles, get_box
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions, ui_scale_offset
from scripts.ui.theme import get_text_box_theme


class RelationshipScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)

        self.previous_cat = None
        self.next_cat = None
        self.filtered_cats = None
        self.all_relations = None
        self.current_page: int = 0
        self.main_cat: Optional[Cat] = None
        self.elements: dict = {}

    def handle_event(self, event):
        super().handle_event(event)

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

        interactable_elements = []

        # NEXT/PREV CAT
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
            sound_id="page_flip",
            manager=MANAGER,
        )

        back_rect = ui_scale(pygame.Rect((0, 0), (105, 30)))
        back_rect.bottomleft = ui_scale_offset((25, -25))
        self.elements["back_button"] = UISurfaceImageButton(
            back_rect,
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            anchors={"bottom": "bottom", "left": "left"},
        )

        interactable_elements.extend(
            [
                self.elements["next_cat_button"],
                self.elements["previous_cat_button"],
                self.elements["back_button"],
            ]
        )

        # MAIN CAT INFO
        self.elements["cat_info_container"] = UIContainer(
            ui_scale(pygame.Rect((50, 65), (500, 70))),
            manager=MANAGER,
        )

        self.main_cat = Cat.all_cats.get(
            switch_get_value(Switch.cat), game.clan.instructor
        )
        self.elements["cat_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (50, 50))),
            self.main_cat.sprite,
            container=self.elements["cat_info_container"],
        )
        self.elements["cat_header"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, 0), (400, -1))),
            object_id=get_text_box_theme("#text_box_34_horizleft"),
            container=self.elements["cat_info_container"],
            anchors={"left_target": self.elements["cat_image"]},
        )
        self.elements["cat_details"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((10, -10), (400, -1))),
            object_id=get_text_box_theme("#text_box_22_horizleft"),
            container=self.elements["cat_info_container"],
            anchors={
                "left_target": self.elements["cat_image"],
                "top_target": self.elements["cat_header"],
            },
        )
        self.elements["cat_header"].disable()
        self.elements["cat_details"].disable()

        # SEARCH BAR
        self.elements["search_bar"] = UISearchBar(
            (500, 90),
        )
        interactable_elements.append(self.elements["search_bar"].text_entry)

        # BACKDROP
        self.elements["backdrop"] = UIModifiedImage(
            ui_scale(pygame.Rect((50, 0), (700, 480))),
            get_box(BoxStyles.DARK_ROUNDED_BOX, (700, 480)),
            anchors={
                "top_target": self.elements["search_bar"],
            },
            manager=MANAGER,
        )

        # PAGES
        self.elements["page_number"] = pygame_gui.elements.UITextBox(
            "test/test",
            ui_scale(pygame.Rect((0, -7), (100, 34))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            anchors={"centerx": "centerx", "top_target": self.elements["backdrop"]},
        )

        rect = ui_scale(pygame.Rect((0, 0), (34, 34)))
        rect.topright = ui_scale_offset((-25, -8))
        self.elements["previous_page_button"] = UISurfaceImageButton(
            rect,
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            anchors={
                "right": "right",
                "top": "top",
                "top_target": self.elements["backdrop"],
                "right_target": self.elements["page_number"],
            },
            starting_height=-1,
        )
        del rect

        self.elements["next_page_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, -8), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            anchors={
                "left_target": self.elements["page_number"],
                "top_target": self.elements["backdrop"],
            },
            starting_height=-1,
        )

        self.update_focus_cat()

    def update_focus_cat(self):
        if self.main_cat.ID != switch_get_value(Switch.cat):
            self.main_cat = Cat.all_cats.get(
                switch_get_value(Switch.cat), game.clan.instructor
            )

        self.current_page = 1

        # Keep a list of all the relations
        if constants.CONFIG["sorting"]["sort_by_rel_total"]:
            self.all_relations = sorted(
                self.main_cat.relationships.values(),
                key=lambda x: x.total_abs_relationship_value,
                reverse=True,
            )
        else:
            self.all_relations = list(self.main_cat.relationships.values()).copy()

        self.elements["cat_header"].set_text(
            "screens.relationship.heading", text_kwargs={"m_c": self.main_cat}
        )

        self.elements["cat_details"].set_text(
            self.main_cat.get_info_block(relationship=True)
        )
        self.elements["cat_image"].set_image(self.main_cat.sprite)

        (
            self.next_cat,
            self.previous_cat,
        ) = self.main_cat.determine_next_and_previous_cats()

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

        self.apply_cat_filter(self.elements["search_bar"].text_entry.get_text())
        # self.update_cat_page()

    def apply_cat_filter(self, search_text=""):
        # Filter for dead or empty cats
        self.filtered_cats = self.all_relations.copy()
        if not get_clan_setting("show dead relation"):
            self.filtered_cats = list(
                filter(lambda rel: not rel.cat_to.dead, self.filtered_cats)
            )

        if not get_clan_setting("show empty relation"):
            self.filtered_cats = list(
                filter(
                    lambda rel: rel.total_abs_relationship_value != 0,
                    self.filtered_cats,
                )
            )

        # Filter for search
        search_cats = []
        if search_text.strip() != "":
            for cat in self.filtered_cats:
                if search_text.lower() in str(cat.cat_to.name).lower():
                    search_cats.append(cat)
            self.filtered_cats = search_cats

    def update_relationships(self):
        chunks = self.get_list_chunks(self.filtered_cats, items_allowed_in_chunk=8)
