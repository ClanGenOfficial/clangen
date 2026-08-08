from typing import Optional

import i18n
import pygame
import pygame_gui
from pygame_gui.core import UIContainer


from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship
from scripts.clan_package.settings import (
    get_clan_setting,
    switch_clan_setting,
)
from scripts.events_module.text_adjust import shorten_text_to_fit
from scripts.game_structure import game, constants, image_cache
from scripts.game_structure.game import switch_get_value, Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.Screens import Screens
from scripts.screens.enums import GameScreen
from scripts.ui.elements.checkbox import UICheckbox
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.relation_display import UIRelationDisplay
from scripts.ui.elements.search_bar import UISearchBar
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import BoxStyles, get_box
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_offset, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme
from scripts.ui.windows.relationship_log import RelationshipLogWindow


class RelationshipScreen(Screens):
    settings = [
        "show_family_only",
        "show_romance_only",
        "show_dead_relation",
        "show_positive",
        "show_negative",
        "show_neutral_relation",
    ]
    mate_indicator = pygame.transform.scale(
        image_cache.load_image(
            "resources/images/relationship_screen/mate_indicator.png"
        ).convert_alpha(),
        ui_scale_dimensions((10, 10)),
    )
    ex_mate_indicator = pygame.transform.scale(
        image_cache.load_image(
            "resources/images/relationship_screen/ex_mate_indicator.png"
        ).convert_alpha(),
        ui_scale_dimensions((10, 10)),
    )
    related_indicator = pygame.transform.scale(
        image_cache.load_image(
            "resources/images/relationship_screen/related_indicator.png"
        ).convert_alpha(),
        ui_scale_dimensions((10, 10)),
    )

    def __init__(self, name=None):
        super().__init__(name)

        self.previous_search_text = None
        self.previous_cat = None
        self.next_cat = None
        self.filtered_cats: list[Relationship] = []
        self.all_relations: list[Relationship] = []
        self.current_page: int = 0
        self.main_cat: Optional[Cat] = None

        self.elements: dict = {}
        self.relation_elements: dict = {}
        self.switch_buttons: dict = {}
        self.log_buttons: dict = {}
        self.profile_buttons: dict = {}

        self.chunks: list[list[Relationship]] = []
        self.prior_chunk: list[Relationship] = []

    def handle_event(self, event):
        # SEARCH BAR
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if (
                self.elements["search_bar"].text_entry.get_text()
                != self.previous_search_text
            ):
                self.current_page = 1
                self.apply_cat_filter(self.elements["search_bar"].text_entry.get_text())
                self.previous_search_text = self.elements[
                    "search_bar"
                ].text_entry.get_text()

        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            # BACK
            if event.ui_element == self.elements["back_button"]:
                self.change_screen(game.last_screen_forupdate)
            # PREV/NEXT CAT
            elif event.ui_element == self.elements["next_cat_button"]:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    self.update_main_cat()
                else:
                    print("invalid next cat", self.next_cat)
            elif event.ui_element == self.elements["previous_cat_button"]:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    self.update_main_cat()
                else:
                    print("invalid previous cat", self.previous_cat)
            # PAGE BUTTONS
            elif event.ui_element == self.elements["previous_page_button"]:
                self.current_page -= 1
                self.update_relationships()
            elif event.ui_element == self.elements["next_page_button"]:
                self.current_page += 1
                self.update_relationships()
            # SWITCH CAT
            elif event.ui_element in self.switch_buttons.values():
                index = list(self.switch_buttons.values()).index(event.ui_element)
                switch_set_value(
                    Switch.cat, self.chunks[self.current_page - 1][index].cat_to.ID
                )
                self.update_main_cat()
            # OPEN LOG
            elif event.ui_element in self.log_buttons.values():
                index = list(self.log_buttons.values()).index(event.ui_element)
                RelationshipLogWindow(self.chunks[self.current_page - 1][index])
            # VIEW PROFILE
            elif event.ui_element in self.profile_buttons.values():
                index = list(self.profile_buttons.values()).index(event.ui_element)
                switch_set_value(
                    Switch.cat, self.chunks[self.current_page - 1][index].cat_to.ID
                )
                self.change_screen(GameScreen.PROFILE)
            # CHANGE SETTINGS
            else:
                for setting in self.settings:
                    if event.ui_element == self.elements[f"checkbox_{setting}"]:
                        self.current_page = 1
                        event.ui_element.toggle()
                        if (
                            setting == "show_family_only"
                            and self.elements[f"checkbox_show_romance_only"].checked
                            and event.ui_element.checked
                        ):
                            switch_clan_setting("show_romance_only")
                            self.elements[f"checkbox_show_romance_only"].toggle()
                        elif (
                            setting == "show_romance_only"
                            and self.elements[f"checkbox_show_family_only"].checked
                            and event.ui_element.checked
                        ):
                            switch_clan_setting("show_family_only")
                            self.elements[f"checkbox_show_family_only"].toggle()

                        switch_clan_setting(setting)
                        self.apply_cat_filter()

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
            ui_scale(pygame.Rect((60, 60), (500, 70))),
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
            (500, 80),
        )
        interactable_elements.append(self.elements["search_bar"].text_entry)

        # BACKDROP
        self.elements["backdrop"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 0), (680, 515))),
            get_box(BoxStyles.DARK_ROUNDED_BOX, (700, 515)),
            anchors={"top_target": self.elements["search_bar"], "centerx": "centerx"},
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

        interactable_elements.extend(
            [self.elements["next_page_button"], self.elements["previous_page_button"]]
        )

        prev_element = None
        for box in self.settings:
            self.elements[f"checkbox_{box}"] = UICheckbox(
                (5, 0 if prev_element else 5),
                anchors={
                    "left_target": self.elements["backdrop"],
                    "top_target": prev_element
                    if prev_element
                    else self.elements["search_bar"],
                },
                tool_tip_text=f"screens.relationship.{box}_checkbox",
                check=get_clan_setting(box),
            )
            prev_element = self.elements[f"checkbox_{box}"]
            interactable_elements.append(self.elements[f"checkbox_{box}"])

        self.add_to_map(interactable_elements)
        self.update_main_cat()

    def update_main_cat(self):
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

    def apply_cat_filter(self, search_text=""):
        self.filtered_cats = self.all_relations.copy()

        # NAME SEARCH
        search_cats = []
        if search_text.strip():
            for cat in self.filtered_cats:
                if search_text.lower() in str(cat.cat_to.name).lower():
                    search_cats.append(cat)
            self.filtered_cats = search_cats

        # FILTER TOGGLES
        if not get_clan_setting("show_dead_relation"):
            self.filtered_cats = list(
                filter(lambda rel: not rel.cat_to.dead, self.filtered_cats)
            )
        if not get_clan_setting("show_neutral_relation"):
            self.filtered_cats = [
                r
                for r in self.filtered_cats
                if not all([t.is_neutral for t in r.get_reltype_tiers()])
            ]
        if get_clan_setting("show_family_only"):
            self.filtered_cats = [
                r
                for r in self.filtered_cats
                if r.cat_from.is_related(r.cat_to, exclude_cousins=False)
            ]
        elif get_clan_setting("show_romance_only"):
            self.filtered_cats = [
                r for r in self.filtered_cats if self.romance_allowed(r)
            ]
        if not get_clan_setting("show_positive"):
            self.filtered_cats = [
                r for r in self.filtered_cats if r.total_relationship_value < 0
            ]
        if not get_clan_setting("show_negative"):
            self.filtered_cats = [
                r for r in self.filtered_cats if r.total_relationship_value > 0
            ]

        self.chunks = self.get_list_chunks(self.filtered_cats, items_allowed_in_chunk=8)

        self.update_relationships()

    def update_relationships(self):
        # reset and return if no chunks
        if not self.chunks:
            if self.relation_elements:
                self.kill_relation_buttons()
            self.prior_chunk.clear()
            return

        # PAGE ARROWS
        self.elements["page_number"].set_text(f"{self.current_page}/{len(self.chunks)}")
        if self.current_page == len(self.chunks):
            self.elements["next_page_button"].disable()
        else:
            self.elements["next_page_button"].enable()
        if self.current_page == 1:
            self.elements["previous_page_button"].disable()
        else:
            self.elements["previous_page_button"].enable()

        # find our chunk
        current_chunk = self.chunks[self.current_page - 1]

        if current_chunk == self.prior_chunk:
            # we don't need to make it all again if they're the same
            return

        # now the real reset
        if self.relation_elements:
            self.kill_relation_buttons()

        self.prior_chunk = current_chunk.copy()

        BOX_HEIGHT = 245
        self.relation_elements["relationships_top_row_container"] = UIContainer(
            ui_scale(pygame.Rect((10, 10), (680, BOX_HEIGHT))),
            manager=MANAGER,
            anchors={"top_target": self.elements["search_bar"], "centerx": "centerx"},
        )
        self.relation_elements["relationships_bottom_row_container"] = UIContainer(
            ui_scale(pygame.Rect((10, 5), (680, BOX_HEIGHT))),
            manager=MANAGER,
            anchors={
                "top_target": self.relation_elements["relationships_top_row_container"],
                "centerx": "centerx",
            },
        )

        prev_element = None
        for i, relationship in enumerate(current_chunk):
            if i >= 4:
                container = self.relation_elements["relationships_bottom_row_container"]
            else:
                container = self.relation_elements["relationships_top_row_container"]

            if i in [0, 4]:
                INTERVAL = 0
            else:
                INTERVAL = 13

            if self.relation_elements.get(f"rel{i}_backdrop"):
                # don't remake something that already exists
                continue

            self.relation_elements[f"rel{i}_backdrop"] = UIModifiedImage(
                ui_scale(pygame.Rect((6 + INTERVAL, 0), (120, BOX_HEIGHT))),
                get_box(BoxStyles.INNER_BOX, (120, BOX_HEIGHT)),
                container=container,
                anchors={"left_target": prev_element} if prev_element else None,
                manager=MANAGER,
            )
            self.relation_elements[f"rel{i}_nameplate"] = UIModifiedImage(
                ui_scale(pygame.Rect((0 + INTERVAL, 0), (130, 30))),
                get_box(BoxStyles.NAMEPLATE, (130, 30)),
                container=container,
                anchors={"left_target": prev_element} if prev_element else None,
                manager=MANAGER,
            )

            if relationship.cat_to.ID in self.main_cat.mate:
                self.relation_elements[f"rel_indicator{i}"] = UIModifiedImage(
                    ui_scale(pygame.Rect((-115, 35), (10, 10))),
                    self.mate_indicator,
                    container=container,
                    anchors={
                        "left_target": self.relation_elements[f"rel{i}_nameplate"]
                    },
                    manager=MANAGER,
                    object_id="#rel_indicator",
                )
                self.relation_elements[f"rel_indicator{i}"].set_tooltip(
                    i18n.t("general.mate", count=1)
                )

            elif relationship.cat_to.ID in self.main_cat.previous_mates:
                self.relation_elements[f"rel_indicator{i}"] = UIModifiedImage(
                    ui_scale(pygame.Rect((-115, 35), (10, 10))),
                    self.ex_mate_indicator,
                    container=container,
                    anchors={
                        "left_target": self.relation_elements[f"rel{i}_nameplate"]
                    },
                    manager=MANAGER,
                    object_id="#rel_indicator",
                )
                self.relation_elements[f"rel_indicator{i}"].set_tooltip(
                    i18n.t("general.ex_mate", count=1)
                )

            elif self.main_cat.is_related(relationship.cat_to, exclude_cousins=False):
                self.relation_elements[f"rel_indicator{i}"] = UIModifiedImage(
                    ui_scale(pygame.Rect((-25, 35), (10, 10))),
                    self.related_indicator,
                    container=container,
                    anchors={
                        "left_target": self.relation_elements[f"rel{i}_nameplate"]
                    },
                    manager=MANAGER,
                    object_id="#rel_indicator",
                )
                self.relation_elements[f"rel_indicator{i}"].set_tooltip(
                    i18n.t("general.related_text", count=1)
                )

            if f"rel_indicator{i}" in self.relation_elements:
                self.relation_elements[f"rel_indicator{i}"].tool_tip_delay = 0

            self.relation_elements[f"rel{i}_name_text"] = pygame_gui.elements.UITextBox(
                shorten_text_to_fit(str(relationship.cat_to.name), 100, 13),
                ui_scale(pygame.Rect((0 + INTERVAL, -3), (130, -1))),
                object_id="#text_box_30_horizcenter",
                container=container,
                anchors={"left_target": prev_element} if prev_element else None,
            )
            self.relation_elements[f"rel{i}_sprite"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((40 + INTERVAL, 0), (50, 50))),
                relationship.cat_to.sprite,
                container=container,
                anchors={
                    "top_target": self.relation_elements[f"rel{i}_nameplate"],
                    "left_target": prev_element,
                }
                if prev_element
                else {"top_target": self.relation_elements[f"rel{i}_nameplate"]},
                manager=MANAGER,
            )
            self.relation_elements[f"rel{i}_rel_display"] = UIRelationDisplay(
                (17 + INTERVAL, -3),
                relationship=relationship,
                romance=self.romance_allowed(relationship),
                container=container,
                anchors={
                    "top_target": self.relation_elements[f"rel{i}_sprite"],
                    "left_target": prev_element,
                }
                if prev_element
                else {"top_target": self.relation_elements[f"rel{i}_sprite"]},
                manager=MANAGER,
            )

            self.switch_buttons[f"rel{i}_main_cat_switch"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-6, 5), (36, 36))),
                Icon.ARROW_RIGHT,
                get_button_dict(ButtonStyles.ICON_TAB_LEFT, (36, 36)),
                object_id="@buttonstyles_icon_tab_left",
                manager=MANAGER,
                container=container,
                anchors={
                    "left_target": self.relation_elements[f"rel{i}_backdrop"],
                    "top_target": self.relation_elements[f"rel{i}_nameplate"],
                },
                tool_tip_text="screens.relationship.switch_cat",
            )
            self.log_buttons[f"rel{i}_open_log"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-6, 5), (36, 36))),
                Icon.NOTEPAD,
                get_button_dict(ButtonStyles.ICON_TAB_LEFT, (36, 36)),
                object_id="@buttonstyles_icon_tab_left",
                manager=MANAGER,
                container=container,
                anchors={
                    "left_target": self.relation_elements[f"rel{i}_backdrop"],
                    "top_target": self.switch_buttons[f"rel{i}_main_cat_switch"],
                },
                tool_tip_text="screens.relationship.view_log",
            )
            if relationship.cat_to.dead:
                self.log_buttons[f"rel{i}_open_log"].disable()
            self.profile_buttons[f"rel{i}_view_profile"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-6, 5), (36, 36))),
                Icon.CAT_HEAD,
                get_button_dict(ButtonStyles.ICON_TAB_LEFT, (36, 36)),
                object_id="@buttonstyles_icon_tab_left",
                manager=MANAGER,
                container=container,
                anchors={
                    "left_target": self.relation_elements[f"rel{i}_backdrop"],
                    "top_target": self.log_buttons[f"rel{i}_open_log"],
                },
                tool_tip_text="screens.relationship.profile",
            )
            prev_element = (
                self.profile_buttons[f"rel{i}_view_profile"] if i != 3 else None
            )
        self.add_to_map(list(self.switch_buttons.values()))
        self.add_to_map(list(self.log_buttons.values()))
        self.add_to_map(list(self.profile_buttons.values()))

    def kill_relation_buttons(self):
        self.remove_from_map(list(self.relation_elements.values()))
        self.relation_elements["relationships_top_row_container"].kill()
        self.relation_elements["relationships_bottom_row_container"].kill()
        self.relation_elements.clear()

        ele_to_remove = (
            list(self.switch_buttons.values())
            + list(self.log_buttons.values())
            + list(self.profile_buttons.values())
        )
        self.remove_from_map(ele_to_remove)
        for ele in ele_to_remove:
            ele.kill()
        self.switch_buttons.clear()
        self.log_buttons.clear()
        self.profile_buttons.clear()

    def romance_allowed(self, relationship: Relationship) -> bool:
        same_age = relationship.cat_to.age == self.main_cat.age
        adult_ages = ["young adult", "adult", "senior adult", "senior"]
        both_adult = (
            relationship.cat_to.age in adult_ages and self.main_cat.age in adult_ages
        )
        check_age = both_adult or same_age

        # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
        # even if they somehow have some. They should not be able to get any, but it never hurts to check.
        if not check_age or self.main_cat.is_related(
            relationship.cat_to, get_clan_setting("first cousin mates")
        ):
            return False
        else:
            return True

    def exit_screen(self):
        for ele_dict in [
            self.elements,
            self.relation_elements,
            self.switch_buttons,
            self.log_buttons,
            self.profile_buttons,
        ]:
            for ele in ele_dict.values():
                ele.kill()
            ele_dict.clear()

        self.prior_chunk.clear()
        self.chunks.clear()

        super().exit_screen()
