from math import ceil
from typing import Union, Dict, Optional

import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game, MANAGER, screen
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UIDropDownContainer,
    UICatListDisplay,
)
from scripts.screens.Screens import Screens
from scripts.utility import scale, get_text_box_theme


class ListScreen(Screens):
    current_page = 1
    previous_search_text = ""
    clan_name = "ErrorClan"

    def __init__(self, name=None):
        super().__init__(name)
        self.ur_bg_image = pygame.image.load("resources/images/urbg.png").convert()
        self.sc_bg_image = pygame.image.load(
            "resources/images/starclanbg.png"
        ).convert_alpha()
        self.df_bg_image = pygame.image.load(
            "resources/images/darkforestbg.png"
        ).convert_alpha()
        self.search_bar_image = pygame.image.load(
            "resources/images/search_bar.png"
        ).convert_alpha()
        self.all_pages = None
        self.filter_options_visible = True
        self.group_options_visible = False
        self.death_status = "living"
        self.current_group = "clan"
        self.full_cat_list = []
        self.current_listed_cats = []

        self.list_screen_container = None

        self.cat_list_bar = None
        self.cat_list_bar_elements: Dict[
            str,
            Union[
                UIImageButton,
                pygame_gui.elements.UIImage,
                pygame_gui.elements.UITextEntryLine,
                None,
            ],
        ] = {
            "fav_toggle": None,
            "search_bar_image": None,
            "search_bar_entry": None,
            "view_button": None,
            "choose_group_button": None,
            "sort_by_button": None,
        }

        self.dead_groups_container = None
        self.choose_dead_dropdown = None
        self.living_groups_container = None
        self.choose_living_dropdown = None
        self.choose_group_buttons = {}

        self.sort_by_button_container = None
        self.sort_by_dropdown = None
        self.sort_by_buttons: Dict[str, Optional[UIImageButton]] = {
            "view_your_clan_button": None,
            "view_cotc_button": None,
            "view_starclan_button": None,
            "view_unknown_residence_button": None,
            "view_dark_forest_button": None,
        }

        self.cat_display = None
        self.display_container_elements: Dict[
            str,
            Union[
                UIImageButton,
                pygame_gui.elements.UITextEntryLine,
                pygame_gui.elements.UITextBox,
                None,
            ],
        ] = {
            "first_page_button": None,
            "previous_page_button": None,
            "last_page_button": None,
            "next_page_button": None,
            "page_entry": None,
            "page_number": None,
        }

        self.df_bg = None
        self.ur_bg = None
        self.sc_bg = None
        self.clan_name = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            element = event.ui_element

            # FAV TOGGLE
            if element == self.cat_list_bar_elements["fav_toggle"]:
                if "#fav_cat_toggle_on" in event.ui_element.get_object_ids():
                    element.change_object_id("#fav_cat_toggle_off")
                    element.tool_tip_text = "show favorite cat indicators"
                    game.clan.clan_settings["show fav"] = False
                else:
                    element.change_object_id("#fav_cat_toggle_on")
                    element.tool_tip_text = "hide favorite cat indicators"
                    game.clan.clan_settings["show fav"] = True
                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )

            # VIEW DEAD/LIVING
            elif element == self.cat_list_bar_elements["view_button"]:
                self.current_page = 1

                # closing these so they can reset in private
                self.sort_by_dropdown.close()
                self.choose_dead_dropdown.close()
                self.choose_living_dropdown.close()

                if "#show_dead_button" in event.ui_element.get_object_ids():
                    element.change_object_id("#show_living_button")
                    element.tool_tip_text = "view cats in the living world"
                    self.death_status = "dead"
                    self.get_sc_cats()
                else:
                    element.change_object_id("#show_dead_button")
                    element.tool_tip_text = "view cats in the afterlife"
                    self.death_status = "living"
                    if (
                        "#filter_by_death_button"
                        in self.cat_list_bar_elements["sort_by_button"].get_object_ids()
                    ):
                        game.sort_type = "rank"
                        self.cat_list_bar_elements["sort_by_button"].change_object_id(
                            "#filter_by_rank_button"
                        )
                    self.get_your_clan_cats()

                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )

                self.cat_list_bar_elements["view_button"].on_hovered()

            # CHOOSE GROUP
            elif (
                element == self.cat_list_bar_elements["choose_group_button"]
                and self.death_status == "living"
            ):
                if self.choose_living_dropdown.is_open:
                    self.choose_living_dropdown.close()
                else:
                    self.choose_living_dropdown.open()

            elif (
                element == self.cat_list_bar_elements["choose_group_button"]
                and self.death_status == "dead"
            ):
                if self.choose_dead_dropdown.is_open:
                    self.choose_dead_dropdown.close()
                else:
                    self.choose_dead_dropdown.open()

            elif element in self.choose_group_buttons.values():
                self.current_page = 1
                # close dropdowns
                self.choose_living_dropdown.close()
                self.choose_dead_dropdown.close()
                # get cat list for button pressed, then update
                if element == self.choose_group_buttons["view_your_clan_button"]:
                    self.get_your_clan_cats()
                elif element == self.choose_group_buttons["view_cotc_button"]:
                    self.get_cotc_cats()
                elif element == self.choose_group_buttons["view_starclan_button"]:
                    self.get_sc_cats()
                elif (
                    element
                    == self.choose_group_buttons["view_unknown_residence_button"]
                ):
                    self.get_ur_cats()
                elif element == self.choose_group_buttons["view_dark_forest_button"]:
                    self.get_df_cats()
                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )

            # SORT BY
            elif element == self.cat_list_bar_elements["sort_by_button"]:
                if self.sort_by_dropdown.is_open:
                    self.sort_by_dropdown.close()
                else:
                    self.sort_by_dropdown.open()
                    if self.death_status == "living":
                        self.sort_by_buttons["filter_death_button"].hide()
            elif element in self.sort_by_buttons.values():
                # close dropdowns
                self.sort_by_dropdown.close()
                # change sort setting and object_id
                sort_type = list(element.get_object_ids())[-1]
                sort_type = sort_type.replace("#filter_", "")
                sort_type = sort_type.replace("_button", "")
                game.sort_type = sort_type

                self.cat_list_bar_elements["sort_by_button"].change_object_id(
                    f"#filter_by_{sort_type}_button"
                )
                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )

            # PAGES
            elif element == self.display_container_elements["first_page_button"]:
                self.current_page = 1
                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )
            elif element == self.display_container_elements["previous_page_button"]:
                self.current_page -= 1
                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )
            elif element == self.display_container_elements["next_page_button"]:
                self.current_page += 1
                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )
            elif element == self.display_container_elements["last_page_button"]:
                self.current_page = self.all_pages
                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )

            # CAT SPRITES
            elif element in self.cat_display.cat_sprites.values():
                game.switches["cat"] = element.return_cat_id()
                game.last_list_forProfile = self.current_group
                self.change_screen("profile screen")

            # MENU BUTTONS
            else:
                self.menu_button_pressed(event)
                self.mute_button_pressed(event)


        elif event.type == pygame.KEYDOWN and game.settings["keybinds"]:
            if self.cat_list_bar_elements["search_bar_entry"].is_focused:
                return
            if event.key == pygame.K_LEFT:
                self.change_screen("camp screen")
            elif event.key == pygame.K_RIGHT:
                self.change_screen("patrol screen")

    def screen_switches(self):
        self.show_mute_buttons()
        self.clan_name = game.clan.name + "Clan"

        self.set_disabled_menu_buttons(["catlist_screen"])
        self.show_menu_buttons()
        screen.fill(
            game.config["theme"]["dark_mode_background"]
            if game.settings["dark mode"]
            else game.config["theme"]["light_mode_background"]
        )
        MANAGER.update(1)

        # SCREEN CONTAINER - everything should come back to here
        self.list_screen_container = pygame_gui.core.UIContainer(
            scale(pygame.Rect((0, 0), (1600, 1400))),
            object_id="#list_screen",
            starting_height=1,
            manager=MANAGER,
            visible=True,
        )

        # BAR CONTAINER
        self.cat_list_bar = pygame_gui.core.UIContainer(
            scale(pygame.Rect((209, 268), (1200, 450))),
            object_id="#cat_list_bar",
            starting_height=3,
            manager=MANAGER,
        )

        # need to use add_element instead of specifying container in self.cat_list_bar
        # to prevent blinking on screen switch
        self.list_screen_container.add_element(self.cat_list_bar)

        # FAVORITE CAT TOGGLE
        self.cat_list_bar_elements["fav_toggle"] = UIImageButton(
            scale(pygame.Rect((0, 0), (76, 68))),
            "",
            object_id="#fav_cat_toggle_on"
            if game.clan.clan_settings["show fav"]
            else "#fav_cat_toggle_off",
            container=self.cat_list_bar,
            tool_tip_text="hide favorite cat indicators"
            if game.clan.clan_settings["show fav"]
            else "show favorite cat indicators",
            starting_height=1,
        )

        # SEARCH BAR
        self.cat_list_bar_elements["search_bar_image"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((72, 0), (276, 68))),
            self.search_bar_image,
            container=self.cat_list_bar,
            object_id="#search_bar",
            manager=MANAGER,
            starting_height=1,
        )

        self.cat_list_bar_elements[
            "search_bar_entry"
        ] = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((90, 9), (245, 55))),
            object_id="#search_entry_box",
            placeholder_text="name search",
            container=self.cat_list_bar,
            manager=MANAGER,
        )

        # SHOW LIVING/DEAD
        self.cat_list_bar_elements["view_button"] = UIImageButton(
            scale(pygame.Rect((344, 0), (206, 68))),
            "",
            object_id="#show_dead_button"
            if self.death_status != "dead"
            else "#show_living_button",
            container=self.cat_list_bar,
            tool_tip_text="view cats in the afterlife"
            if self.death_status != "dead"
            else "view cats in the living world",
            manager=MANAGER,
            starting_height=1,
        )

        if self.death_status != "dead" and game.sort_type == "death":
            game.sort_type = "rank"

        # CHOOSE GROUP DROPDOWN
        self.cat_list_bar_elements["choose_group_button"] = UIImageButton(
            scale(pygame.Rect((546, 0), (380, 68))),
            "",
            container=self.cat_list_bar,
            object_id="#choose_group_button",
            manager=MANAGER,
            starting_height=1,
        )

        # living groups
        self.living_groups_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((546, 64), (0, 0))),
            container=self.cat_list_bar,
            object_id="#choose_group_container",
            manager=MANAGER,
            starting_height=1,
        )

        y_pos = 0
        for object_id in ["#view_your_clan_button", "#view_cotc_button"]:
            self.choose_group_buttons[object_id.strip("#")] = UIImageButton(
                scale(pygame.Rect((0, y_pos), (380, 68))),
                "",
                container=self.living_groups_container,
                object_id=object_id,
                starting_height=2,
                manager=MANAGER,
            )
            y_pos += 64

        self.choose_living_dropdown = UIDropDownContainer(
            self.living_groups_container.relative_rect,
            container=self.cat_list_bar,
            object_id="#choose_living_dropdown",
            starting_height=1,
            parent_button=self.cat_list_bar_elements["choose_group_button"],
            child_button_container=self.living_groups_container,
            manager=MANAGER,
        )

        self.choose_living_dropdown.close()
        self.choose_living_dropdown.show()

        # dead groups
        self.dead_groups_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((546, 64), (0, 0))),
            container=self.cat_list_bar,
            object_id="#choose_group_container",
            manager=MANAGER,
            starting_height=1,
            visible=False,
        )

        y_pos = 0
        for object_id in [
            "#view_starclan_button",
            "#view_unknown_residence_button",
            "#view_dark_forest_button",
        ]:
            self.choose_group_buttons[object_id.strip("#")] = UIImageButton(
                scale(pygame.Rect((0, y_pos), (380, 68))),
                "",
                container=self.dead_groups_container,
                object_id=object_id,
                starting_height=2,
                manager=MANAGER,
                visible=False,
            )
            y_pos += 64

        self.choose_dead_dropdown = UIDropDownContainer(
            scale(pygame.Rect((546, 0), (0, 0))),
            container=self.cat_list_bar,
            object_id="#choose_living_dropdown",
            starting_height=1,
            parent_button=self.cat_list_bar_elements["choose_group_button"],
            child_button_container=self.dead_groups_container,
            visible=False,
            manager=MANAGER,
        )

        self.choose_dead_dropdown.close()

        # SORT BY
        self.cat_list_bar_elements["sort_by_button"] = UIImageButton(
            scale(pygame.Rect((922, 0), (276, 68))),
            "",
            container=self.cat_list_bar,
            object_id=f"#filter_by_{game.sort_type}_button",
            starting_height=1,
            manager=MANAGER,
        )

        self.sort_by_button_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((1070, 64), (0, 0))),
            container=self.cat_list_bar,
            object_id="#sort_by_button_container",
            starting_height=2,
            manager=MANAGER,
        )

        y_pos = 0
        for object_id in [
            "#filter_rank_button",
            "#filter_age_button",
            "#filter_reverse_age_button",
            "#filter_id_button",
            "#filter_exp_button",
            "#filter_death_button",
        ]:
            self.sort_by_buttons[object_id.strip("#")] = UIImageButton(
                scale(pygame.Rect((0, y_pos), (128, 68))),
                "",
                object_id=object_id,
                container=self.sort_by_button_container,
                starting_height=1,
                manager=MANAGER,
            )
            y_pos += 64

        self.sort_by_dropdown = UIDropDownContainer(
            scale(pygame.Rect((1070, 62), (0, 0))),
            container=self.cat_list_bar,
            object_id="#sort_by_dropdown",
            starting_height=2,
            parent_button=self.cat_list_bar_elements["sort_by_button"],
            child_button_container=self.sort_by_button_container,
            manager=MANAGER,
        )

        self.sort_by_dropdown.close()

        # BG IMAGES
        self.sc_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (1600, 1400))),
            pygame.transform.scale(
                self.sc_bg_image,
                (1600, 1400),
            ),
            container=self.list_screen_container,
            starting_height=1,
            object_id="#starclan_bg",
            visible=False,
            manager=MANAGER,
        )
        self.ur_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (1600, 1400))),
            pygame.transform.scale(
                self.ur_bg_image,
                (1600, 1400),
            ),
            container=self.list_screen_container,
            starting_height=1,
            object_id="#unknown_residence_bg",
            visible=False,
            manager=MANAGER,
        )
        self.df_bg = pygame_gui.elements.UIImage(
            scale(pygame.Rect((0, 0), (1600, 1400))),
            pygame.transform.scale(
                self.df_bg_image,
                (1600, 1400),
            ),
            container=self.list_screen_container,
            starting_height=1,
            object_id="#dark_forest_bg",
            visible=False,
            manager=MANAGER,
        )

        # CAT DISPLAY
        # first/prev/next/last page buttons
        self.display_container_elements["first_page_button"] = UIImageButton(
            scale(pygame.Rect((570, 1200), (68, 68))),
            "",
            container=self.list_screen_container,
            object_id="#arrow_double_left_button",
            manager=MANAGER,
        )
        self.display_container_elements["previous_page_button"] = UIImageButton(
            scale(pygame.Rect((620, 1200), (68, 68))),
            "",
            container=self.list_screen_container,
            object_id="#arrow_left_button",
            manager=MANAGER,
        )
        self.display_container_elements["last_page_button"] = UIImageButton(
            scale(pygame.Rect((962, 1200), (68, 68))),
            "",
            container=self.list_screen_container,
            object_id="#arrow_double_right_button",
            manager=MANAGER,
        )
        self.display_container_elements["next_page_button"] = UIImageButton(
            scale(pygame.Rect((912, 1200), (68, 68))),
            "",
            container=self.list_screen_container,
            object_id="#arrow_right_button",
            manager=MANAGER,
        )
        # page number
        self.display_container_elements[
            "page_entry"
        ] = pygame_gui.elements.UITextEntryLine(
            scale(pygame.Rect((740, 1208), (60, 55))),
            container=self.list_screen_container,
            placeholder_text=str(self.current_page),
            object_id=get_text_box_theme("#page_entry_box")
            if self.death_status == "living"
            else "#page_entry_box_dark",
            manager=MANAGER,
        )
        self.display_container_elements["page_number"] = pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((730, 1204), (200, 60))),
            container=self.list_screen_container,
            object_id=get_text_box_theme("#text_box_30_horizleft")
            if self.death_status == "living"
            else "#text_box_30_horizleft_light",
            manager=MANAGER,
        )  # Text will be filled in later

        # this speeds up the load time 1000%
        # don't ask why
        MANAGER.update(1)

        # Determine the starting list of cats.
        self.get_cat_list()
        self.update_cat_list()

    def exit_screen(self):
        self.cat_display.clear_display()
        self.cat_display = None
        self.list_screen_container.kill()

    def on_use(self):
        # Only update the positions if the search text changes
        if (
            self.cat_list_bar_elements["search_bar_entry"].get_text()
            != self.previous_search_text
        ):
            self.update_cat_list(
                self.cat_list_bar_elements["search_bar_entry"].get_text()
            )
        self.previous_search_text = self.cat_list_bar_elements[
            "search_bar_entry"
        ].get_text()

        if self.display_container_elements["page_entry"].is_focused:
            if self.display_container_elements["page_entry"].get_text() != str(
                self.current_page
            ):
                if self.display_container_elements["page_entry"].get_text():
                    self.current_page = int(
                        self.display_container_elements["page_entry"].get_text()
                    )
                    self.update_cat_list(
                        self.cat_list_bar_elements["search_bar_entry"].get_text()
                    )

    def update_cat_list(self, search_text=""):
        """
        updates the cat list and display, search text is taken into account
        """
        self.current_listed_cats = []
        Cat.sort_cats(self.full_cat_list)

        # adding in the guide if necessary, this ensures the guide isn't affected by sorting as we always want them to
        # be the first cat on the list
        if (self.current_group == "df" and game.clan.instructor.df) or (
            self.current_group == "sc" and not game.clan.instructor.df
        ):
            if game.clan.instructor in self.full_cat_list:
                self.full_cat_list.remove(game.clan.instructor)
            self.full_cat_list.insert(0, game.clan.instructor)

        search_text = search_text.strip()
        if search_text not in ["", "name search"]:
            self.current_listed_cats = [
                cat
                for cat in self.full_cat_list
                if search_text.lower() in str(cat.name).lower()
            ]
        else:
            self.current_listed_cats = self.full_cat_list.copy()

        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 20.0))
            if len(self.current_listed_cats) > 20
            else 1
        )
        if self.current_page > self.all_pages:
            self.current_page = self.all_pages
        elif self.current_page < 1:
            self.current_page = 1

        Cat.ordered_cat_list = self.current_listed_cats
        self._update_cat_display()

    def _update_cat_display(self):
        """
        updates the cat display, includes the page number display
        """
        self.display_container_elements["page_entry"].change_object_id(
            get_text_box_theme("#page_entry_box")
            if self.death_status == "living"
            else "#page_entry_box_dark"
        )
        self.display_container_elements["page_entry"].set_text(str(self.current_page))
        self.display_container_elements["page_number"].change_object_id(
            get_text_box_theme("#text_box_30_horizcenter")
            if self.death_status == "living"
            else "#text_box_30_horizcenter_light"
        )
        self.display_container_elements["page_number"].set_text(f"/{self.all_pages}")

        if not self.cat_display:
            self.cat_display = UICatListDisplay(
                scale(pygame.Rect((0, 0), (1200, 800))),
                container=self.list_screen_container,
                object_id="#cat_list_display",
                starting_height=1,
                cat_list=self.current_listed_cats,
                cats_displayed=20,
                x_px_between=240,
                y_px_between=200,
                columns=5,
                prev_button=self.display_container_elements["previous_page_button"],
                next_button=self.display_container_elements["next_page_button"],
                first_button=self.display_container_elements["first_page_button"],
                last_button=self.display_container_elements["last_page_button"],
                current_page=self.current_page,
                show_names=True,
                text_theme=get_text_box_theme("#text_box_30_horizcenter")
                if self.death_status == "living"
                else "#text_box_30_horizcenter_light",
                manager=MANAGER,
                anchors={
                    "top_target": self.cat_list_bar_elements["search_bar_entry"],
                    "centerx": "centerx",
                },
            )
        else:
            if self.cat_display.prev_button is None:
                self.cat_display.prev_button = self.display_container_elements[
                    "previous_page_button"
                ]
                self.cat_display.next_button = self.display_container_elements[
                    "next_page_button"
                ]
                self.cat_display.first_button = self.display_container_elements[
                    "first_page_button"
                ]
                self.cat_display.last_button = self.display_container_elements[
                    "last_page_button"
                ]
            self.cat_display.text_theme = (
                get_text_box_theme("#text_box_30_horizcenter")
                if self.death_status == "living"
                else "#text_box_30_horizcenter_light"
            )
            self.cat_display.update_display(
                current_page=self.current_page, cat_list=self.current_listed_cats
            )

        self.set_bg_and_heading()

    def set_bg_and_heading(self):
        """
        sets the background and heading according to current group
        """
        if self.current_group == "clan":
            self.df_bg.hide()
            self.ur_bg.hide()
            self.sc_bg.hide()
            self.update_heading_text(self.clan_name)
        elif self.current_group == "cotc":
            self.df_bg.hide()
            self.ur_bg.hide()
            self.sc_bg.hide()
            self.update_heading_text("Cats Outside the Clan")
        elif self.current_group == "sc":
            self.df_bg.hide()
            self.ur_bg.hide()
            self.sc_bg.show()
            self.update_heading_text("StarClan")
        elif self.current_group == "ur":
            self.df_bg.hide()
            self.ur_bg.show()
            self.sc_bg.hide()
            self.update_heading_text("Unknown Residence")
        elif self.current_group == "df":
            self.df_bg.show()
            self.ur_bg.hide()
            self.sc_bg.hide()
            self.update_heading_text("Dark Forest")

    def get_cat_list(self):
        """
        grabs the correct cat list for current group
        """
        if game.last_list_forProfile:
            if game.last_list_forProfile == "sc":
                self.get_sc_cats()
            elif game.last_list_forProfile == "df":
                self.get_df_cats()
            elif game.last_list_forProfile == "ur":
                self.get_ur_cats()
            elif game.last_list_forProfile == "cotc":
                self.get_cotc_cats()
            else:
                self.get_your_clan_cats()
        else:
            self.get_your_clan_cats()

    def get_your_clan_cats(self):
        """
        grabs clan cats
        """
        self.current_group = "clan"
        self.death_status = "living"
        self.full_cat_list = [
            cat for cat in Cat.all_cats_list if not cat.dead and not cat.outside
        ]

    def get_cotc_cats(self):
        """
        grabs cats outside the clan
        """
        self.current_group = "cotc"
        self.death_status = "living"
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and the_cat.outside and not the_cat.driven_out:
                self.full_cat_list.append(the_cat)

    def get_sc_cats(self):
        """
        grabs starclan cats
        """
        self.current_group = "sc"
        self.death_status = "dead"
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if (
                the_cat.dead
                and the_cat.ID != game.clan.instructor.ID
                and not the_cat.outside
                and not the_cat.df
                and not the_cat.faded
            ):
                self.full_cat_list.append(the_cat)

    def get_df_cats(self):
        """
        grabs dark forest cats
        """
        self.current_group = "df"
        self.death_status = "dead"
        self.full_cat_list = []

        for the_cat in Cat.all_cats_list:
            if (
                the_cat.dead
                and the_cat.ID != game.clan.instructor.ID
                and the_cat.df
                and not the_cat.faded
            ):
                self.full_cat_list.append(the_cat)

    def get_ur_cats(self):
        """
        grabs unknown residence cats
        """
        self.current_group = "ur"
        self.death_status = "dead"
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if (
                the_cat.ID in game.clan.unknown_cats
                and not the_cat.faded
                and not the_cat.driven_out
            ):
                self.full_cat_list.append(the_cat)
