from random import choice

import i18n
import pygame
import pygame_gui

from scripts.cat.sprites.load_sprites import sprites
from scripts.game_structure.game import Switch, switch_get_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_box import get_box, BoxStyles
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme
from scripts.ui.windows.symbol_filter import SymbolFilterWindow


class ChooseSymbolScreen(MakeClanScreenBase):
    def __init__(self, name="choose_symbol_screen"):
        super().__init__(name)
        self.tag_list_len = 0
        self.current_page = 1
        self.symbol_buttons = {}
        self.text = {}

    def screen_switches(self):
        super().screen_switches()
        self.elements["next_step"].hide()
        self.elements["done_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 620), (147, 30))),
            "buttons.done",
            get_button_dict(ButtonStyles.MENU_RIGHT, (147, 30)),
            object_id="@buttonstyles_menu_right",
            manager=MANAGER,
            starting_height=2,
            anchors={"left_target": self.elements["previous_step"]},
        )
        self.elements["done_button"].disable()

        # create screen specific elements
        self.elements["text_container"] = pygame_gui.elements.UIAutoResizingContainer(
            ui_scale(pygame.Rect((85, 90), (0, 0))),
            object_id="text_container",
            starting_height=1,
            manager=MANAGER,
        )
        self.text["clan_name"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 0), (-1, -1))),
            text="general.clan",
            text_kwargs={"name": self.clan_info.display_name},
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_40"),
            manager=MANAGER,
            anchors={"left": "left"},
        )
        self.text["biome"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 5), (-1, -1))),
            text=f"screens.make_clan.{self.clan_info.biome}",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            anchors={
                "top_target": self.text["clan_name"],
            },
        )
        self.text["leader"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 5), (-1, -1))),
            text="screens.make_clan.symbol_leader",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            text_kwargs={"prefix": self.clan_info.leader.name.prefix},
            anchors={
                "top_target": self.text["biome"],
            },
        )
        self.text["recommend"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 5), (-1, -1))),
            text="screens.make_clan.symbol_recommended",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            text_kwargs={
                "symbol": (
                    f"{self.clan_info.display_name.upper()}0"
                    if f"symbol{self.clan_info.display_name.upper()}0"
                    in sprites.clan_symbols
                    else i18n.t("screens.make_clan.not_applicable")
                )
            },
            anchors={
                "top_target": self.text["leader"],
            },
        )
        self.text["selected"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((0, 15), (-1, -1))),
            text=f"screens.make_clan.symbol_selected",
            container=self.elements["text_container"],
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            manager=MANAGER,
            text_kwargs={"symbol": i18n.t("screens.make_clan.not_applicable")},
            anchors={
                "top_target": self.text["recommend"],
            },
        )

        self.elements["random_symbol_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((496, 196), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )

        self.elements["symbol_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((540, 90), (169, 166))),
            get_box(BoxStyles.FRAME, (169, 166), sides=(True, True, False, True)),
            object_id="@boxstyles_frame",
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["page_left"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((47, 404), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["page_right"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((719, 404), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["filters_tab"] = UIImageButton(
            ui_scale(pygame.Rect((100, 609), (78, 30))),
            "",
            object_id="#filters_tab_button",
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["symbol_list_frame"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((76, 240), (650, 370))),
            get_box(BoxStyles.ROUNDED_BOX, (650, 370)),
            object_id="#symbol_list_frame",
            starting_height=2,
            manager=MANAGER,
        )

        if not self.clan_info.symbol:
            if f"symbol{self.clan_info.display_name.upper()}0" in sprites.clan_symbols:
                self.clan_info.symbol = f"symbol{self.clan_info.display_name.upper()}0"

                self.text["selected"].set_text(
                    "screens.make_clan.symbol_selected",
                    text_kwargs={"symbol": f"{self.clan_info.display_name.upper()}0"},
                )

        if self.clan_info.symbol:
            symbol_name = self.clan_info.symbol.replace("symbol", "")
            self.text["selected"].set_text(
                "screens.make_clan.symbol_selected", text_kwargs={"symbol": symbol_name}
            )

            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((573, 117), (100, 100))),
                pygame.transform.scale(
                    sprites.get_symbol(self.clan_info.symbol),
                    ui_scale_dimensions((100, 100)),
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=2,
                manager=MANAGER,
            )
            self.refresh_symbol_list()
            while self.clan_info.symbol not in self.symbol_buttons:
                self.current_page += 1
                self.refresh_symbol_list()
            self.elements["done_button"].enable()
        else:
            self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((573, 117), (100, 100))),
                pygame.transform.scale(
                    sprites.sprites["symbolADDER0"],
                    ui_scale_dimensions((100, 100)),
                ).convert_alpha(),
                object_id="#selected_symbol",
                starting_height=2,
                manager=MANAGER,
                visible=False,
            )
            self.refresh_symbol_list()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["previous_step"]:
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_CAMP)
            elif event.ui_element == self.elements["page_right"]:
                self.current_page += 1
                self.refresh_symbol_list()
            elif event.ui_element == self.elements["page_left"]:
                self.current_page -= 1
                self.refresh_symbol_list()
            elif event.ui_element == self.elements["done_button"]:
                self.save_clan()
                self.change_screen(GameScreen.MAKE_CLAN_CLAN_CREATED)
            elif event.ui_element == self.elements["random_symbol_button"]:
                if self.clan_info.symbol:
                    if self.clan_info.symbol in self.symbol_buttons:
                        self.symbol_buttons[self.clan_info.symbol].enable()
                self.clan_info.symbol = choice(sprites.clan_symbols)
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["filters_tab"]:
                SymbolFilterWindow()
            else:
                for symbol_id, element in self.symbol_buttons.items():
                    if event.ui_element == element:
                        if self.clan_info.symbol:
                            if self.clan_info.symbol in self.symbol_buttons:
                                self.symbol_buttons[self.clan_info.symbol].enable()
                        self.clan_info.symbol = symbol_id
                        self.refresh_text_and_buttons()

        super().handle_event(event)

    def exit_screen(self):
        super().exit_screen()
        for ele in self.symbol_buttons.values():
            ele.kill()
        for ele in self.text.values():
            ele.kill()

    def on_use(self):
        super().on_use()

        # refreshes symbol list when filters are changed
        # - done here bc refresh_symbol_list cannot be called from windows.py
        if len(switch_get_value(Switch.disallowed_symbol_tags)) != self.tag_list_len:
            self.tag_list_len = len(switch_get_value(Switch.disallowed_symbol_tags))
            self.refresh_symbol_list()

    def refresh_text_and_buttons(self):
        """Refreshes the button states and text boxes"""
        if self.clan_info.symbol:
            if self.clan_info.symbol in self.symbol_buttons:
                self.symbol_buttons[self.clan_info.symbol].disable()
            # refresh selected symbol image
            self.elements["selected_symbol"].set_image(
                pygame.transform.scale(
                    sprites.get_symbol(self.clan_info.symbol),
                    ui_scale_dimensions((100, 100)),
                ).convert_alpha()
            )
            symbol_name = self.clan_info.symbol.replace("symbol", "")
            self.text["selected"].set_text(
                "screens.make_clan.symbol_selected",
                text_kwargs={"symbol": symbol_name},
            )
            self.elements["selected_symbol"].show()
            self.elements["done_button"].enable()

    def refresh_symbol_list(self):
        # get symbol list
        symbol_list = sprites.clan_symbols.copy()
        symbol_attributes = sprites.symbol_dict

        # filtering out tagged symbols
        for symbol in sprites.clan_symbols:
            index = symbol[-1]
            name = symbol.strip("symbol1234567890")
            tags = symbol_attributes[name.capitalize()][f"tags{index}"]
            for tag in tags:
                if tag in switch_get_value(Switch.disallowed_symbol_tags):
                    if symbol in symbol_list:
                        symbol_list.remove(symbol)

        # separate list into chunks for pages
        symbol_chunks = self.chunks(symbol_list, 45)

        # clamp current page to a valid page number
        self.current_page = max(1, min(self.current_page, len(symbol_chunks)))

        # handles which arrow buttons are clickable
        if len(symbol_chunks) <= 1:
            self.elements["page_left"].disable()
            self.elements["page_right"].disable()
        elif self.current_page >= len(symbol_chunks):
            self.elements["page_left"].enable()
            self.elements["page_right"].disable()
        elif self.current_page == 1 and len(symbol_chunks) > 1:
            self.elements["page_left"].disable()
            self.elements["page_right"].enable()
        else:
            self.elements["page_left"].enable()
            self.elements["page_right"].enable()

        display_symbols = []
        if symbol_chunks:
            display_symbols = symbol_chunks[self.current_page - 1]

        # Kill all currently displayed symbols
        symbol_images = [ele for ele in self.elements if ele in sprites.clan_symbols]
        for ele in symbol_images:
            self.elements[ele].kill()
            if self.symbol_buttons:
                self.symbol_buttons[ele].kill()

        x_pos = 96
        y_pos = 260
        for symbol in display_symbols:
            self.elements[f"{symbol}"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x_pos, y_pos), (50, 50))),
                sprites.sprites[symbol],
                object_id=f"#{symbol}",
                starting_height=3,
                manager=MANAGER,
            )
            self.symbol_buttons[f"{symbol}"] = UIImageButton(
                ui_scale(pygame.Rect((x_pos - 12, y_pos - 12), (74, 74))),
                "",
                object_id=f"#symbol_select_button",
                starting_height=4,
                manager=MANAGER,
            )
            x_pos += 70
            if x_pos >= 715:
                x_pos = 96
                y_pos += 70

        if self.clan_info.symbol in self.symbol_buttons:
            self.symbol_buttons[self.clan_info.symbol].disable()
