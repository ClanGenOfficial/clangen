import i18n
import logging
import ujson
from math import ceil

from scripts.cat.sprites.load_sprites import sprites
from scripts.clan import Clan
from scripts.game_structure import game, image_cache
from scripts.game_structure.game.save_load import read_clans, get_clan_json
from scripts.game_structure.screen_settings import MANAGER
from scripts.housekeeping.datadir import get_save_dir

import pygame
import pygame_gui

from scripts.screens.enums import GameScreen
from scripts.screens.Screens import Screens
from scripts.screens.screens_core.screens_core import rebuild_core
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme
from scripts.ui.windows.delete_check import CheckDeletionWindow

logger = logging.getLogger(__name__)

class SwitchClanScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)

        self.main_menu_button = None
        self.current_clan = None
        self.main_container = None

        self.current_page = 1
        self.previous_page_button = None
        self.next_page_button = None
        self.page_number_text = None

        self.clan_list = []
        self.clan_list_frame = None
        self.clan_list_nameplates = []
        self.clan_button_container = None
        self.clan_buttons = []

        self.selected_clan = None
        self.selected_clan_info = {
            "save_id": "",
            "displayname": "",
            "clanage": "",
            "biome": "",
            "camp_bg": "",
            "clan_symbol": None,
            "gamemode": ""
        }
        self.info_frame = None
        self.info_frame_bg = None
        self.info_container = None
        self.info_body = {}

        self.load_save_button = None
        self.delete_save_button = None
        self.current_clan_text = None


    def handle_event(self, event):
        """
        Handles button presses / events
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            # EXIT
            if event.ui_element == self.main_menu_button:
                self.change_screen(GameScreen.START)
                return

            # CHANGE PAGE
            elif event.ui_element == self.previous_page_button:
                self.current_page -= 1
                self.update_screen()
                return
            elif event.ui_element == self.next_page_button:
                self.current_page += 1
                self.update_screen()
                return

            # SELECT CLAN
            elif event.ui_element in self.clan_buttons:
                for index, button in enumerate(self.clan_buttons):
                    if button == event.ui_element:
                        # loop index + one to skip current clan + page offset
                        clan_index = index + 1 + (8 * (self.current_page - 1))
                        self.selected_clan = self.clan_list[clan_index]
                        self.update_screen()
                        return

            # LOAD CLAN
            elif event.ui_element == self.load_save_button:
                self.change_screen(GameScreen.START)
                Clan.switch_clans(self.selected_clan, False)
                # rebuild to update menu scheme differences between game modes
                # rebuild_core()

            # DELETE CLAN
            elif event.ui_element == self.delete_save_button:
                CheckDeletionWindow(
                    self.change_screen,
                    self.selected_clan,
                    self.selected_clan_info["displayname"]
                )

        # EXIT
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_screen(GameScreen.START)
                return

        # DESELECT CLAN
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.selected_clan = self.current_clan
                self.update_screen()

    def screen_switches(self):
        """
        Handles creating new elements when switching to this screen
        """
        super().screen_switches()

        self.set_bg("default", "mainmenu_bg")
        self.show_mute_buttons()

        self.current_clan = game.clan.save_id
        self.selected_clan = self.current_clan
        self.clan_list = read_clans()

        self.main_menu_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.main_menu",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            starting_height=1,
            manager=MANAGER,
        )

        self.main_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((0, 0), (570, 450))),
            manager=MANAGER,
            anchors={
                "centerx": "centerx",
                "centery": "centery",
            },
        )

        self.create_clan_list_display()
        self.create_info_display()

        self.update_screen()

    def exit_screen(self):
        """
        Deletes all elements when this screen is closed
        """
        self.main_menu_button.kill()
        self.main_container.kill()
        self.current_page = 1
        self.clan_list.clear()
        self.clan_list_nameplates.clear()

    def create_clan_list_display(self):
        """
        Handles creation of permanent clan list elements
        """
        # CLAN LIST
        self.clan_list_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, -5), (220, 348))),
            get_box(BoxStyles.FRAME, (220, 338)),
            starting_height=2,
            container=self.main_container,
            manager=MANAGER,
            anchors={
                "left": "left",
                "centery": "centery",
            },
        )
        self.clan_list_header = UISurfaceImageButton(
            ui_scale(pygame.Rect((50, 19), (121, 35))),
            "screens.switch_clan.your_clans",
            get_button_dict(ButtonStyles.HORIZONTAL_TAB, (121, 35)),
            object_id="@buttonstyles_horizontal_tab",
            manager=MANAGER,
            container=self.main_container,
            anchors={
                "left": "left",
                "bottom_target": self.clan_list_frame,
            },
        )
        self.clan_list_header.disable()
        for i in range(8):
            self.clan_list_nameplates.append(
                pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect(
                        (8, -2) if len(self.clan_list_nameplates) > 0 else (8, 2),
                        (205, 43))
                    ),
                    get_box(BoxStyles.NAMEPLATE, (205, 43)),
                    starting_height=0,
                    container=self.main_container,
                    manager=MANAGER,
                    anchors={
                        "top_target": self.clan_list_nameplates[-1],
                        "left": "left",
                    } if len(self.clan_list_nameplates) > 0
                    else {
                        "top_target": self.clan_list_header,
                        "left": "left",
                    },
                )
            )

        # PAGE ELEMENTS
        self.previous_page_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((22, -52), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            container=self.main_container,
            anchors={
                "left": "left",
                "top_target": self.clan_list_frame,
                "bottom": "bottom",
            },
        )
        self.next_page_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((110, -52), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            container=self.main_container,
            anchors={
                "left_target": self.previous_page_button,
                "top_target": self.clan_list_frame,
                "bottom": "bottom",
            },
        )
        self.page_number_text = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, -52), (110, 49))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            container=self.main_container,
            anchors={
                "left_target": self.previous_page_button,
                "right_target": self.next_page_button,
                "top_target": self.clan_list_frame,
                "bottom": "bottom",
            },
        )

    def create_clan_buttons(self):
        """
        Handles creation of clan buttons
        """
        if self.clan_button_container:
            self.clan_button_container.kill()
            self.clan_buttons.clear()
        self.clan_button_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((10, -5), (200, 328))),
            manager=MANAGER,
            container=self.main_container,
            anchors={
                "left": "left",
                "centery": "centery",
            },
        )

        # each page is 8 buttons
        # add one because loaded clan is always index 0
        end = self.current_page * 9
        start = end - 8

        for clan in (self.clan_list[start:end]):
            clan_button_name = self._get_clan_values(clan, nameonly=True)
            if not clan_button_name:
                continue

            self.clan_buttons.append(UISurfaceImageButton(
                ui_scale(pygame.Rect((0, 0), (200, 41))),
                "general.clan",
                get_button_dict(ButtonStyles.DROPDOWN, (200, 41)),
                text_kwargs={"name": clan_button_name},
                object_id=pygame_gui.core.ObjectID("#text_box_34_horizcenter_vertcenter", "#dark"),
                manager=MANAGER,
                container=self.clan_button_container,
                anchors=(
                    {"top_target": self.clan_buttons[-1]}
                    if len(self.clan_buttons) % 8 != 0
                    else {"top": "top"}
                ),
            ))

    def create_info_display(self):
        """
        Handles creation of permanent information display elements
        """
        # INFO BOX
        self.info_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 0), (350, 450))),
            get_box(BoxStyles.FRAME, (350, 450)),
            starting_height=2,
            container=self.main_container,
            manager=MANAGER,
            anchors={
                "left_target": self.clan_list_frame,
                "centery": "centery",
            },
        )
        self.info_frame_bg = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((4, 0), (342, 442))),
            get_box(BoxStyles.INNER_BOX, (342, 442)),
            starting_height=0,
            container=self.main_container,
            manager=MANAGER,
            anchors={
                "left_target": self.clan_list_frame,
                "centery": "centery",
            },
        )

        # SAVE ELEMENTS
        self.load_save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((35, -51), (153, 30))),
            "buttons.load_save",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            starting_height=1,
            container=self.main_container,
            manager=MANAGER,
            anchors={
                "bottom": "bottom",
                "centerx": "centerx",
            },
        )
        self.delete_save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((15, -51), (133, 30))),
            "buttons.delete",
            get_button_dict(ButtonStyles.SQUOVAL, (133, 30)),
            object_id="@buttonstyles_squoval",
            starting_height=1,
            container=self.main_container,
            manager=MANAGER,
            anchors={
                "left_target": self.load_save_button,
                "bottom": "bottom",
            },
        )
        self.current_clan_text = pygame_gui.elements.UITextBox(
            "screens.switch_clan.current_clan",
            ui_scale(pygame.Rect((27, -62), (334, 55))),
            object_id="#text_box_30_horizcenter",
            manager=MANAGER,
            container=self.main_container,
            anchors={
                "left_target": self.next_page_button,
                "bottom": "bottom"
            },
        )

    def create_info_body(self):
        """
        Handles creation of selected clan information elements
        """
        if self.info_container:
            self.info_container.kill()
        self.info_container = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((8, 0), (334, 436))),
            manager=MANAGER,
            container=self.main_container,
            anchors={
                "left_target": self.clan_list_frame,
                "centery": "centery",
            },
        )

        self.info_body["symbol"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((0, 16), (100, 100))),
            pygame.transform.scale(
                sprites.get_symbol(self.selected_clan_info["clan_symbol"]),
                ui_scale_dimensions((100, 100)),
            ).convert_alpha(),
            object_id="#selected_symbol",
            starting_height=1,
            manager=MANAGER,
            container=self.info_container,
            anchors={
                "top": "top",
                "centerx": "centerx",
            },
        )
        self.info_body["displayname"] = pygame_gui.elements.UITextBox(
            "general.clan",
            ui_scale(pygame.Rect((0, 4), (334, 42))),
            text_kwargs={"name": self.selected_clan_info["displayname"]},
            object_id="#text_box_40_horizcenter",
            starting_height=1,
            manager=MANAGER,
            container=self.info_container,
            anchors={
                "top_target": self.info_body["symbol"],
                "centerx": "centerx",
            },
        )
        self.info_body["save_id"] = pygame_gui.elements.UITextBox(
            f"ID: {self.selected_clan_info["save_id"]}",
            ui_scale(pygame.Rect((0, 0), (320, 29))),
            object_id="#text_box_26_horizleft",
            starting_height=1,
            manager=MANAGER,
            container=self.info_container,
            anchors={
                "top_target": self.info_body["displayname"],
                "centerx": "centerx",
            },
        )
        self.info_body["gamemode"] = pygame_gui.elements.UITextBox(
            "screens.switch_clan.game_mode",
            ui_scale(pygame.Rect((0, 3), (320, 33))),
            text_kwargs={
                "gamemode": i18n.t(
                    f"screens.make_clan.{self.selected_clan_info["gamemode"]}_label"
                )
            },
            object_id="#text_box_30_horizleft",
            starting_height=1,
            manager=MANAGER,
            container=self.info_container,
            anchors={
                "top_target": self.info_body["save_id"],
                "centerx": "centerx",
            },
        )
        self.info_body["biome"] = pygame_gui.elements.UITextBox(
            "screens.switch_clan.biome",
            ui_scale(pygame.Rect((0, 0), (320, 33))),
            text_kwargs={
                "biome": i18n.t(
                    f"screens.make_clan.{self.selected_clan_info["biome"]}"
                )
            },
            object_id="#text_box_30_horizleft",
            starting_height=1,
            manager=MANAGER,
            container=self.info_container,
            anchors={
                "top_target": self.info_body["gamemode"],
                "centerx": "centerx",
            },
        )
        self.info_body["camp"] = pygame_gui.elements.UITextBox(
            "screens.switch_clan.camp",
            ui_scale(pygame.Rect((0, 0), (320, 33))),
            text_kwargs={
                "camp": i18n.t(
                    f"screens.make_clan.{self._get_camp_name()}"
                )
            },
            object_id="#text_box_30_horizleft",
            starting_height=1,
            manager=MANAGER,
            container=self.info_container,
            anchors={
                "top_target": self.info_body["biome"],
                "centerx": "centerx",
            },
        )
        self.info_body["clanage"] = pygame_gui.elements.UITextBox(
            "screens.switch_clan.clan_age",
            ui_scale(pygame.Rect((0, 0), (320, 33))),
            text_kwargs={
                "age": self.selected_clan_info["clanage"],
                "count": int(self.selected_clan_info["clanage"]),
            },
            object_id="#text_box_30_horizleft",
            starting_height=1,
            manager=MANAGER,
            container=self.info_container,
            anchors={
                "top_target": self.info_body["camp"],
                "centerx": "centerx",
            },
        )
        # spare room for last date played info TODO in a future enhancement
        
    def update_screen(self):
        """
        Updates screen elements and selected clan info
        """
        if not self.selected_clan_info["save_id"] == self.selected_clan:
            self.selected_clan_info = self._get_clan_values(self.selected_clan)

        self.update_page()
        self.create_clan_buttons()
        self.create_info_body()

        # can't delete or load current clan
        if self.selected_clan == self.current_clan:
            self.load_save_button.hide()
            self.delete_save_button.hide()
            self.current_clan_text.show()
        else:
            self.load_save_button.show()
            self.delete_save_button.show()
            self.current_clan_text.hide()

    def update_page(self):
        """
        Updates current page and relevant elements
        """
        if self.current_page == 1:
            self.previous_page_button.disable()
        else:
            self.previous_page_button.enable()

        if self.current_page >= ceil(len(self.clan_list) / 8):
            self.next_page_button.disable()
        else:
            self.next_page_button.enable()

        self.page_number_text.set_text(
            "screens.switch_clan.page_number_text",
            text_kwargs={
                "current_page": self.current_page,
                "total_page": ceil(len(self.clan_list) / 8),
            }
        )

    def _get_clan_values(self, clan, nameonly=False) -> dict | str:
        """
        Loads displayed clan information
        """
        try:
            with open(get_clan_json(clan)) as read_file:
                data = ujson.load(read_file)
                if nameonly:
                    return data.get("displayname", clan)
                dictionary = {}
                for key in self.selected_clan_info:
                    dictionary[key] = data.get(key)
                return dictionary
        except:
            logger.warning(
                "Failed to read save information of clan with ID %s",
                clan,
                exc_info=True,
            )
            return None

    def _get_camp_name(self) -> str:
        """
        Gets camp background name from the camp number
        """
        # hardcoded ew
        camp_names = {
            "Forest": ["classic", "gully", "grotto", "lakeside"],
            "Mountainous": ["cliff", "cavern", "crystal_river", "ruins"],
            "Plains": ["grasslands", "tunnels", "wastelands", "bridge"],
            "Beach": ["tidepools", "tidal_cave", "shipwreck", "fjord"]
        }

        index = int(self.selected_clan_info["camp_bg"].replace("camp", ""))
        index -= 1 # camps count from 1
        return "_".join(("camp", camp_names[self.selected_clan_info["biome"]][index]))