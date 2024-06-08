from math import ceil

import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.game_structure.ui_elements import UIImageButton, UIDropDownContainer, UINamedCatListDisplay
from scripts.screens.Screens import Screens
from scripts.utility import scale, get_text_box_theme


class NewListScreen(Screens):
    current_page = 1
    previous_search_text = ""

    def __init__(self, name=None):
        super().__init__(name)
        self.filter_options_visible = True
        self.group_options_visible = False
        self.death_status = "living"
        self.current_group = "clan"
        self.full_cat_list = []

        self.list_screen_container = None

        self.cat_list_bar = None
        self.cat_list_bar_elements = {}

        self.dead_groups_container = None
        self.choose_dead_dropdown = None
        self.living_groups_container = None
        self.choose_living_dropdown = None
        self.choose_group_buttons = {}

        self.sort_by_button_container = None
        self.sort_by_dropdown = None
        self.sort_by_buttons = {}

        self.cat_display_container = None
        self.cat_display = None
        self.display_container_elements = {}

    def handle_event(self, event):
        pass

    def screen_switches(self):

        self.set_disabled_menu_buttons(["catlist_screen"])
        self.show_menu_buttons()

        # SCREEN CONTAINER - everything should come back to here
        self.list_screen_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((0, 0), (0, 0))),
            object_id="#list_screen",
            starting_height=1,
            manager=MANAGER,
            visible=True,
        )

        # BAR CONTAINER
        self.cat_list_bar = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((209, 268), (0, 0))),
            object_id="#cat_list_bar",
            manager=MANAGER
        )

        # need to use add_element instead of specifying container in self.cat_list_bar
        # to prevent blinking on screen switch
        self.list_screen_container.add_element(self.cat_list_bar)

        # FAVORITE CAT TOGGLE
        self.cat_list_bar_elements["fav_toggle"] = UIImageButton(
            scale(pygame.Rect((0, 0), (76, 68))),
            "",
            object_id="#fav_cat_toggle_on" if game.clan.clan_settings["show fav"] else "#fav_cat_toggle_off",
            container=self.cat_list_bar,
            tool_tip_text="hide favorite cat indicators" if game.clan.clan_settings["show fav"]
            else "show favorite cat indicators",
            starting_height=1
        )

        # SEARCH BAR
        self.cat_list_bar_elements["search_bar"] = pygame_gui.elements.UIImage(
            scale(pygame.Rect((72, 0), (276, 68))),
            pygame.image.load("resources/images/search_bar.png").convert_alpha(),
            container=self.cat_list_bar,
            object_id="#search_bar",
            manager=MANAGER,
            starting_height=1
        )

        self.cat_list_bar_elements["search_bar_entry"] = pygame_gui.elements.UITextEntryLine(
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
            object_id="#show_dead_button" if self.death_status != "dead" else "#show_living_button",
            container=self.cat_list_bar,
            tool_tip_text="view cats in the afterlife" if self.death_status != "dead"
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
            starting_height=1
        )

        # living groups
        self.living_groups_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((546, 64), (0, 0))),
            container=self.cat_list_bar,
            object_id="#choose_group_container",
            manager=MANAGER,
            starting_height=1
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
            manager=MANAGER
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
            visible=False
        )

        for object_id in ["#view_starclan_button", "#view_unknown_residence_button", "#view_dark_forest_button"]:
            self.choose_group_buttons[object_id.strip("#")] = UIImageButton(
                scale(pygame.Rect((0, y_pos), (380, 68))),
                "",
                container=self.dead_groups_container,
                object_id=object_id,
                starting_height=2,
                manager=MANAGER,
                visible=False
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
            manager=MANAGER
        )

        self.choose_dead_dropdown.close()

        self.cat_list_bar_elements["sort_by_button"] = UIImageButton(
            scale(pygame.Rect((922, 0), (276, 68))),
            "",
            container=self.cat_list_bar,
            object_id=f"#filter_by_{game.sort_type}_button",
            starting_height=1,
            manager=MANAGER
        )

        self.sort_by_button_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((1070, 64), (0, 0))),
            container=self.cat_list_bar,
            object_id="#sort_by_button_container",
            starting_height=2,
            manager=MANAGER
        )

        y_pos = 0
        for object_id in ["#filter_rank_button", "#filter_age_button", "#filter_age_reverse_button",
                          "#filter_id_button", "#filter_exp_button", "#filter_death_button"]:
            self.sort_by_buttons[object_id.strip("#")] = UIImageButton(
                scale(pygame.Rect((0, y_pos), (128, 68))),
                "",
                object_id=object_id,
                container=self.sort_by_button_container,
                starting_height=1,
                manager=MANAGER
            )
            y_pos += 64

        self.sort_by_dropdown = UIDropDownContainer(
            scale(pygame.Rect((1070, 62), (0, 0))),
            container=self.cat_list_bar,
            object_id="#sort_by_dropdown",
            starting_height=2,
            parent_button=self.cat_list_bar_elements["sort_by_button"],
            child_button_container=self.sort_by_button_container,
            manager=MANAGER
        )

        self.sort_by_dropdown.close()

        # CAT DISPLAY
        self.cat_display_container = pygame_gui.elements.UIAutoResizingContainer(
            scale(pygame.Rect((30, 170), (0, 0))),
            object_id="#cat_display_container",
            container=self.list_screen_container,
            manager=MANAGER
        )
        # prev/next page buttons
        self.display_container_elements["previous_page_button"] = UIImageButton(
            scale(pygame.Rect((590, 1030), (68, 68))),
            "",
            container=self.cat_display_container,
            object_id="#arrow_left_button",
            manager=MANAGER,
        )
        self.display_container_elements["next_page_button"] = UIImageButton(
            scale(pygame.Rect((882, 1030), (68, 68))),
            "",
            container=self.cat_display_container,
            object_id="#arrow_right_button",
            manager=MANAGER,
        )
        # page number
        self.display_container_elements["page_number"] = pygame_gui.elements.UITextBox(
            "",
            scale(pygame.Rect((680, 1190), (220, 60))),
            container=self.cat_display_container,
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )  # Text will be filled in later

        # Determine the starting list of cats.
        self.get_cat_list()
        self.update_cat_list()

    def exit_screen(self):
        self.list_screen_container.kill()

    def on_use(self):
        pass

    def update_cat_list(self, search_text=""):
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
            for cat in self.full_cat_list:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = self.full_cat_list.copy()

        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 20.0))
            if len(self.current_listed_cats) > 20
            else 1
        )

        Cat.ordered_cat_list = self.current_listed_cats
        self.update_cat_display()

    def update_cat_display(self):

        # update title
        if self.current_group == "clan":
            self.update_heading_text(f"{game.clan.name}Clan")
        elif self.current_group == "cotc":
            self.update_heading_text(f"Cats Outside the Clan")
        elif self.current_group == "sc":
            self.update_heading_text(f"StarClan")
        elif self.current_group == "ur":
            self.update_heading_text(f"Unknown Residence")
        elif self.current_group == "df":
            self.update_heading_text(f"Dark Forest")

        self.cat_display = UINamedCatListDisplay(
            scale(pygame.Rect((0, 0), (0, 0))),
            container=self.cat_display_container,
            object_id="#cat_list_display",
            starting_height=1,
            cat_list=self.current_listed_cats,
            cats_displayed=20,
            x_px_between=240,
            y_px_between=200,
            columns=5,
            prev_button=self.display_container_elements["previous_page_button"],
            next_button=self.display_container_elements["next_page_button"],
            current_page=self.current_page,
            text_theme=get_text_box_theme("#text_box_30_horizcenter") if self.death_status == "living"
            else "#text_box_30_horizcenter_light",
            manager=MANAGER
        )

    def get_cat_list(self):
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
        self.current_group = "clan"
        self.death_status = "living"
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and not the_cat.outside:
                self.full_cat_list.append(the_cat)

    def get_cotc_cats(self):
        self.current_group = "cotc"
        self.death_status = "living"
        self.full_cat_list = []
        for the_cat in Cat.all_cats_list:
            if not the_cat.dead and the_cat.outside and not the_cat.driven_out:
                self.full_cat_list.append(the_cat)

    def get_sc_cats(self):
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
