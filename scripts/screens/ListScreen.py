from math import ceil
from typing import Union, Dict

import pygame
import pygame_gui
from pygame_gui.core import ObjectID

from scripts.cat.cats import Cat
from scripts.clan_package.settings import switch_clan_setting
from scripts.clan_package.settings.clan_settings import (
    set_clan_setting,
    get_clan_setting,
)
from scripts.game_structure.game.settings import game_setting_get
from scripts.game_structure.game.switches import (
    switch_set_value,
    switch_get_value,
    Switch,
)
from scripts.cat.enums import CatGroup
from scripts.game_structure.game_essentials import game
from scripts.game_structure.screen_settings import game_screen_size, MANAGER
from scripts.game_structure.ui_elements import (
    UIImageButton,
    UICatListDisplay,
    UISurfaceImageButton,
    UIDropDown,
)
from scripts.screens.Screens import Screens
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.utility import ui_scale, get_text_box_theme, ui_scale_value


class ListScreen(Screens):
    current_page = 1
    previous_search_text = ""
    clan_name = "ErrorClan"

    dead_filter_names = (
        "screens.list.filter_rank",
        "screens.list.filter_age",
        "screens.list.filter_reverse_age",
        "screens.list.filter_id",
        "screens.list.filter_exp",
        "screens.list.filter_death",
    )
    living_filter_names = (
        "screens.list.filter_rank",
        "screens.list.filter_age",
        "screens.list.filter_reverse_age",
        "screens.list.filter_id",
        "screens.list.filter_exp",
    )

    living_group_names = ("general.your_clan", "general.cotc")
    dead_group_names = (
        "general.starclan",
        "general.unknown_residence",
        "general.dark_forest",
    )

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
        self.current_group = "your_clan"
        self.full_cat_list = []
        self.current_listed_cats = []

        self.list_screen_container = None

        self.cat_list_bar = None
        self.cat_list_bar_elements: Dict[
            str,
            Union[
                UIImageButton,
                UISurfaceImageButton,
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
            "sort_by_label": None,
        }

        self.choose_group_dropdown = None

        self.sort_by_dropdown = None

        self.cat_display = None
        self.display_container_elements: Dict[
            str,
            Union[
                UIImageButton,
                UISurfaceImageButton,
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
        if event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            if event.ui_element == self.cat_list_bar_elements["sort_by_label"]:
                self.cat_list_bar_elements["sort_by_button"].on_hovered()

        elif event.type == pygame_gui.UI_BUTTON_ON_UNHOVERED:
            if event.ui_element == self.cat_list_bar_elements["sort_by_label"]:
                self.cat_list_bar_elements["sort_by_button"].on_unhovered()
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            element = event.ui_element

            # FAV TOGGLE
            if element == self.cat_list_bar_elements["fav_toggle"]:
                switch_clan_setting("show fav")
                if "#fav_cat_toggle_on" in event.ui_element.get_object_ids():
                    element.change_object_id("#fav_cat_toggle_off")
                    element.set_tooltip("screens.list.favorite_show_tooltip")
                else:
                    element.change_object_id("#fav_cat_toggle_on")
                    element.set_tooltip("screens.list.favorite_hide_tooltip")
                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )

            # VIEW DEAD/LIVING
            elif element == self.cat_list_bar_elements["view_button"]:
                self.current_page = 1

                if event.ui_element.text == "screens.list.view_dead":
                    # changing dropdown options
                    self.choose_group_dropdown.new_item_list(self.dead_group_names)
                    self.choose_group_dropdown.set_selected_list(["general.starclan"])
                    self.sort_by_dropdown.new_item_list(self.dead_filter_names)
                    self.sort_by_dropdown.disable_child(
                        f"screens.list.filter_{switch_get_value(Switch.sort_type)}"
                    )

                    # switch button text
                    element.set_text("screens.list.view_living")
                    element.set_tooltip("screens.list.view_living_tooltip")
                    self.death_status = "dead"
                    self.get_sc_cats()
                else:
                    # changing dropdown options
                    self.choose_group_dropdown.new_item_list(self.living_group_names)
                    self.choose_group_dropdown.set_selected_list(["general.your_clan"])
                    self.sort_by_dropdown.new_item_list(self.dead_filter_names)
                    if switch_get_value(Switch.sort_type) == "death":
                        switch_set_value(Switch.sort_type, "rank")
                    self.sort_by_dropdown.disable_child(
                        f"screens.list.filter_{switch_get_value(Switch.sort_type)}"
                    )
                    self.sort_by_dropdown.parent_button.set_text(
                        f"screens.list.filter_{switch_get_value(Switch.sort_type)}"
                    )

                    # switch button text
                    element.set_text("screens.list.view_dead")
                    element.set_tooltip("screens.list.view_dead_tooltip")
                    self.death_status = "living"
                    self.get_your_clan_cats()

                self.update_cat_list(
                    self.cat_list_bar_elements["search_bar_entry"].get_text()
                )

                self.cat_list_bar_elements["view_button"].on_hovered()

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
                switch_set_value(Switch.cat, element.return_cat_id())
                game.last_list_forProfile = self.current_group
                self.change_screen("profile screen")

            # MENU BUTTONS
            else:
                self.menu_button_pressed(event)
                self.mute_button_pressed(event)

        elif event.type == pygame.KEYDOWN and game_setting_get("keybinds"):
            if self.cat_list_bar_elements["search_bar_entry"].is_focused:
                return
            if event.key == pygame.K_LEFT:
                self.change_screen("camp screen")
            elif event.key == pygame.K_RIGHT:
                self.change_screen("patrol screen")

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()
        self.clan_name = game.clan.displayname + "Clan"

        self.set_disabled_menu_buttons(["catlist_screen"])
        self.show_menu_buttons()

        # SCREEN CONTAINER - everything should come back to here
        self.list_screen_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((0, 0), (800, 700))),
            object_id="#list_screen",
            starting_height=1,
            manager=MANAGER,
            visible=True,
        )

        # BAR CONTAINER
        self.cat_list_bar = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((104, 134), (700, 400))),
            object_id="#cat_list_bar",
            starting_height=3,
            manager=MANAGER,
        )

        # need to use add_element instead of specifying container in self.cat_list_bar
        # to prevent blinking on screen switch
        self.list_screen_container.add_element(self.cat_list_bar)

        # FAVORITE CAT TOGGLE
        self.cat_list_bar_elements["fav_toggle"] = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (38, 34))),
            "",
            object_id=(
                "#fav_cat_toggle_on"
                if get_clan_setting("show fav")
                else "#fav_cat_toggle_off"
            ),
            container=self.cat_list_bar,
            tool_tip_text=(
                "screens.list.favorite_hide_tooltip"
                if get_clan_setting("show fav")
                else "screens.list.favorite_show_tooltip"
            ),
            starting_height=1,
        )

        # SEARCH BAR
        self.cat_list_bar_elements["search_bar_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((36, 0), (138, 34))),
            self.search_bar_image,
            container=self.cat_list_bar,
            object_id="#search_bar",
            manager=MANAGER,
            starting_height=1,
        )

        self.cat_list_bar_elements[
            "search_bar_entry"
        ] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((45, 4), (122, 27))),
            object_id="#search_entry_box",
            placeholder_text="general.name_search",
            container=self.cat_list_bar,
            manager=MANAGER,
        )

        # SHOW LIVING/DEAD
        self.cat_list_bar_elements["view_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((172, 0), (103, 34))),
            (
                "screens.list.view_dead"
                if self.death_status != "dead"
                else "screens.list.view_living"
            ),
            get_button_dict(ButtonStyles.DROPDOWN, (103, 34)),
            object_id="@buttonstyles_dropdown",
            container=self.cat_list_bar,
            tool_tip_text=(
                "screens.list.view_dead_tooltip"
                if self.death_status != "dead"
                else "screens.list.view_living_tooltip"
            ),
            manager=MANAGER,
            starting_height=1,
        )

        if (
            self.death_status != "dead"
            and switch_get_value(Switch.sort_type) == "death"
        ):
            switch_set_value(Switch.sort_type, "rank")

        # CHOOSE GROUP DROPDOWN
        starting_select = f"general.{self.current_group}"
        self.choose_group_dropdown = UIDropDown(
            pygame.Rect((-2, 0), (190, 34)),
            parent_text="screens.list.choose_group",
            item_list=self.living_group_names
            if self.death_status == "living"
            else self.dead_group_names,
            manager=MANAGER,
            container=self.cat_list_bar,
            starting_selection=[starting_select],
            anchors={"left_target": self.cat_list_bar_elements["view_button"]},
        )

        # SORT BY
        self.cat_list_bar_elements["sort_by_label"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((-2, 0), (75, 34))),
            f"screens.list.filter_label",
            {
                "normal": get_button_dict(ButtonStyles.DROPDOWN, (77, 34))[
                    "normal"
                ].subsurface(
                    (0, 0), (75, 34)
                )  # this horrific thing gets rid of the double-thick line
            },
            object_id="@buttonstyles_dropdown",
            container=self.cat_list_bar,
            starting_height=1,
            manager=MANAGER,
            anchors={"left_target": self.choose_group_dropdown},
        )

        self.cat_list_bar_elements["sort_by_button"] = UIImageButton(
            ui_scale(pygame.Rect((0, 0), (63, 34))),
            f"screens.list.filter_{switch_get_value(Switch.sort_type)}",
            object_id=ObjectID("#filter_by_button", "@buttonstyles_dropdown"),
            container=self.cat_list_bar,
            starting_height=1,
            manager=MANAGER,
            anchors={"left_target": self.cat_list_bar_elements["sort_by_label"]},
        )

        self.sort_by_dropdown = UIDropDown(
            pygame.Rect((-2, 0), (63, 34)),
            f"screens.list.filter_{switch_get_value(Switch.sort_type)}",
            item_list=self.living_filter_names,
            manager=MANAGER,
            container=self.cat_list_bar,
            parent_override=self.cat_list_bar_elements["sort_by_button"],
            starting_selection=["screens.list.filter_rank"],
            anchors={"left_target": self.cat_list_bar_elements["sort_by_label"]},
        )

        # BG IMAGES
        self.add_bgs(
            {
                "unknown_residence": pygame.transform.scale(
                    self.ur_bg_image,
                    game_screen_size,
                ),
                "dark_forest": pygame.transform.scale(
                    self.df_bg_image,
                    game_screen_size,
                ),
            },
            radius=10,
        )
        self.add_bgs(
            {
                "starclan": pygame.transform.scale(
                    self.sc_bg_image,
                    game_screen_size,
                ),
            },
            radius=2,
        )

        # CAT DISPLAY
        # first/prev/next/last page buttons
        self.display_container_elements["first_page_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((285, 600), (34, 34))),
            Icon.ARROW_DOUBLELEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.list_screen_container,
            manager=MANAGER,
        )
        self.display_container_elements["previous_page_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((310, 600), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.list_screen_container,
            manager=MANAGER,
        )
        self.display_container_elements["last_page_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((481, 600), (34, 34))),
            Icon.ARROW_DOUBLERIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.list_screen_container,
            manager=MANAGER,
        )
        self.display_container_elements["next_page_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((456, 600), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            container=self.list_screen_container,
            manager=MANAGER,
        )
        # page number
        self.display_container_elements[
            "page_entry"
        ] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((370, 604), (30, 27))),
            container=self.list_screen_container,
            placeholder_text=str(self.current_page),
            object_id=(
                get_text_box_theme("#page_entry_box")
                if self.death_status == "living"
                else ObjectID("#dark", "#page_entry_box")
            ),
            manager=MANAGER,
        )
        self.display_container_elements["page_number"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((365, 602), (100, 30))),
            container=self.list_screen_container,
            object_id=(
                get_text_box_theme("#text_box_30_horizleft")
                if self.death_status == "living"
                else "#text_box_30_horizleft_light"
            ),
            manager=MANAGER,
        )  # Text will be filled in later

        # this speeds up the load time 1000%
        # don't ask why
        MANAGER.update(1)

        # Determine the starting list of cats.
        self.get_cat_list()
        self.update_cat_list()

    def display_change_save(self) -> Dict:
        variable_dict = super().display_change_save()

        variable_dict["current_group"] = self.current_group
        variable_dict["death_status"] = self.death_status

        return variable_dict

    def exit_screen(self):
        self.cat_display.clear_display()
        self.cat_display = None
        self.list_screen_container.kill()
        self.update_heading_text(self.clan_name)

    def on_use(self):
        super().on_use()
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

        # GROUP DROPDOWN
        if (
            self.choose_group_dropdown
            and self.choose_group_dropdown.selected_list[0].replace("general.", "")
            != self.current_group
        ):
            self.current_page = 1
            new_group = self.choose_group_dropdown.selected_list[0].replace(
                "general.", ""
            )
            if new_group == "your_clan":
                self.get_your_clan_cats()
            elif new_group == "cotc":
                self.get_cotc_cats()
            elif new_group == "starclan":
                self.get_sc_cats()
            elif new_group == "unknown_residence":
                self.get_ur_cats()
            elif new_group == "dark_forest":
                self.get_df_cats()
            self.update_cat_list(
                self.cat_list_bar_elements["search_bar_entry"].get_text()
            )

        # SORT BY DROPDOWN
        if self.sort_by_dropdown and self.sort_by_dropdown.selected_list[0].replace(
            "screens.list.filter_", ""
        ) != switch_get_value(Switch.sort_type):
            sort_type = self.sort_by_dropdown.selected_list[0].replace(
                "screens.list.filter_", ""
            )
            switch_set_value(Switch.sort_type, sort_type)
            self.sort_by_dropdown.parent_button.set_text(
                f"screens.list.filter_{switch_get_value(Switch.sort_type)}"
            )
            self.update_cat_list(
                self.cat_list_bar_elements["search_bar_entry"].get_text()
            )

    def update_cat_list(self, search_text=""):
        """
        updates the cat list and display, search text is taken into account
        """
        self.current_listed_cats = []

        # make sure cat list is the same everywhere else in the game.
        Cat.sort_cats(self.full_cat_list)
        Cat.sort_cats(Cat.all_cats_list)

        # adding in the guide if necessary, this ensures the guide isn't affected by sorting as we always want them to
        # be the first cat on the list
        if (
            self.current_group == "dark_forest"
            and game.clan.instructor.status.group == CatGroup.DARK_FOREST
        ) or (
            self.current_group == "starclan"
            and game.clan.instructor.status.group == CatGroup.STARCLAN
        ):
            if game.clan.instructor in self.full_cat_list:
                self.full_cat_list.remove(game.clan.instructor)
            self.full_cat_list.insert(0, game.clan.instructor)

        search_text = search_text.strip()
        if search_text not in ("", "name search"):
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
            else ObjectID("#dark", "#page_entry_box")
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
                ui_scale(pygame.Rect((0, 0), (600, 400))),
                container=self.list_screen_container,
                object_id="#cat_list_display",
                starting_height=1,
                cat_list=self.current_listed_cats,
                cats_displayed=20,
                x_px_between=ui_scale_value(240),
                y_px_between=ui_scale_value(200),
                columns=5,
                prev_button=self.display_container_elements["previous_page_button"],
                next_button=self.display_container_elements["next_page_button"],
                first_button=self.display_container_elements["first_page_button"],
                last_button=self.display_container_elements["last_page_button"],
                current_page=self.current_page,
                show_names=True,
                text_theme=(
                    get_text_box_theme("#text_box_30_horizcenter")
                    if self.death_status == "living"
                    else "#text_box_30_horizcenter_light"
                ),
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
        if self.current_group == "your_clan":
            self.set_bg(None)
            self.update_heading_text(self.clan_name)
        elif self.current_group == "cotc":
            self.set_bg(None)
            self.update_heading_text("general.cotc")
        elif self.current_group == "starclan":
            self.set_bg("starclan")
            self.update_heading_text("general.starclan")
        elif self.current_group == "unknown_residence":
            self.set_bg("unknown_residence")
            self.update_heading_text("general.unknown_residence")
        elif self.current_group == "dark_forest":
            self.set_bg("dark_forest")
            self.update_heading_text("general.dark_forest")

    def get_cat_list(self):
        """
        grabs the correct cat list for current group
        """
        if game.last_list_forProfile:
            if game.last_list_forProfile == "starclan":
                self.get_sc_cats()
            elif game.last_list_forProfile == "dark_forest":
                self.get_df_cats()
            elif game.last_list_forProfile == "unknown_residence":
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
        self.current_group = "your_clan"
        self.death_status = "living"
        self.full_cat_list = [
            cat for cat in Cat.all_cats_list if cat.status.alive_in_player_clan
        ]

    def get_cotc_cats(self):
        """
        grabs cats outside the clan
        """
        self.current_group = "cotc"
        self.death_status = "living"
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if (
                not the_cat.dead
                and (the_cat.status.is_outsider or the_cat.status.is_other_clancat)
                and the_cat.status.is_near(CatGroup.PLAYER_CLAN)
            ):
                self.full_cat_list.append(the_cat)

    def get_sc_cats(self):
        """
        grabs starclan cats
        """
        self.current_group = "starclan"
        self.death_status = "dead"
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if (
                the_cat.ID != game.clan.instructor.ID
                and the_cat.status.group == CatGroup.STARCLAN
                and not the_cat.faded
            ):
                self.full_cat_list.append(the_cat)

    def get_df_cats(self):
        """
        grabs dark forest cats
        """
        self.current_group = "dark_forest"
        self.death_status = "dead"
        self.full_cat_list = []

        for the_cat in Cat.all_cats_list:
            if (
                the_cat.ID != game.clan.instructor.ID
                and the_cat.status.group == CatGroup.DARK_FOREST
                and not the_cat.faded
            ):
                self.full_cat_list.append(the_cat)

    def get_ur_cats(self):
        """
        grabs unknown residence cats
        """
        self.current_group = "unknown_residence"
        self.death_status = "dead"
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if (
                the_cat.ID != game.clan.instructor.ID
                and the_cat.status.group == CatGroup.UNKNOWN_RESIDENCE
                and not the_cat.faded
                and the_cat.status.is_near(CatGroup.PLAYER_CLAN)
            ):
                self.full_cat_list.append(the_cat)
