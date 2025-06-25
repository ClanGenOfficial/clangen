import logging
from math import ceil

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements import UIImage

import scripts.game_structure.screen_settings
from scripts.clan import Clan
from scripts.game_structure.game_essentials import (
    game,
)
from scripts.game_structure.ui_elements import UIImageButton, UISurfaceImageButton
from scripts.game_structure.windows import DeleteCheck
from scripts.utility import (
    get_text_box_theme,
    ui_scale,
    ui_scale_dimensions,
    ui_scale_value,
    ui_scale_offset,
)
from .Screens import Screens
from ..game_structure.game.save_load import read_clans
from ..game_structure.game.settings import game_setting_get
from ..game_structure.screen_settings import MANAGER
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon

logger = logging.getLogger(__name__)


class SwitchClanScreen(Screens):
    """
    TODO: DOCS
    """

    def handle_event(self, event):
        """
        TODO: DOCS
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element == self.main_menu:
                self.change_screen("start screen")
            elif event.ui_element == self.next_page_button:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page_button:
                self.page -= 1
                self.update_page()
            else:
                for page in self.delete_buttons:
                    if event.ui_element in page:
                        DeleteCheck(
                            self.change_screen,
                            self.clan_name[self.page][page.index(event.ui_element)],
                        )

                        return

                for page in self.clan_buttons:
                    if event.ui_element in page:
                        self.change_screen("start screen")
                        Clan.switch_clans(
                            self.clan_name[self.page][page.index(event.ui_element)],
                            False,
                        )

        elif event.type == pygame.KEYDOWN and game_setting_get("keybinds"):
            if event.key == pygame.K_ESCAPE:
                self.change_screen("start screen")

    def exit_screen(self):
        """
        TODO: DOCS
        """
        self.main_menu.kill()
        del self.main_menu
        self.current_clan.kill()
        del self.current_clan

        self.clans_frame.kill()
        del self.clans_frame

        # del self.screen  # No need to keep that in memory.

        for page in self.clan_buttons:
            for button in page:
                button.kill()
                del button  # pylint: disable=modified-iterating-list

        for page in self.delete_buttons:
            for button in page:
                button.kill()
                del button  # pylint: disable=modified-iterating-list

        self.next_page_button.kill()
        del self.next_page_button
        self.previous_page_button.kill()
        del self.previous_page_button
        self.page_number.kill()
        del self.page_number

        self.clan_buttons = [[]]
        self.delete_buttons = [[]]
        self.clan_name = [[]]

    def screen_switches(self):
        """
        TODO: DOCS
        """
        super().screen_switches()
        self.set_bg("default", "mainmenu_bg")
        self.show_mute_buttons()
        self.screen = pygame.transform.scale(
            pygame.image.load("resources/images/clan_saves_frame.png").convert_alpha(),
            ui_scale_dimensions((220, 368)),
        )
        self.main_menu = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.main_menu",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            manager=MANAGER,
            object_id="@buttonstyles_squoval",
            starting_height=1,
        )

        self.current_clan = pygame_gui.elements.UITextBox(
            "screens.switch_clan.current_clan",
            ui_scale(pygame.Rect((0, 100), (600, 40))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={"centerx": "centerx"},
            text_kwargs={
                "clan": game.clan.name if game.clan else "",
                "count": 1 if game.clan else 0,
            },
        )
        self.clan_list = read_clans()

        self.clan_buttons = [[]]
        self.clan_name = [[]]
        self.delete_buttons = [[]]

        # cursed math o clock!
        # i am exceedingly sorry for this abomination
        core_frame_dimensions = 375 - 49
        core = ceil(ui_scale_value(core_frame_dimensions) / 8) * 8
        item_height = core / 8
        clan_frame_height = core + ui_scale_value(49)

        self.clans_frame = UIImage(
            pygame.Rect(
                ui_scale_offset((0, 151)), (ui_scale_value(220), clan_frame_height)
            ),
            self.screen,
            anchors={"centerx": "centerx"},
            starting_height=0,
        )
        self.clans_frame.disable()

        i = 0
        for clan in self.clan_list[1:]:
            self.clan_name[-1].append(clan)
            self.clan_buttons[-1].append(
                UISurfaceImageButton(
                    pygame.Rect(
                        (
                            (0, 0)
                            if len(self.clan_buttons[-1]) % 8 != 0
                            else ui_scale_offset((0, 190))
                        ),
                        (ui_scale_value(200), item_height),
                    ),
                    clan + "Clan",
                    get_button_dict(
                        ButtonStyles.DROPDOWN,
                        (
                            200,
                            item_height
                            / scripts.game_structure.screen_settings.screen_scale,
                        ),
                    ),
                    object_id=ObjectID("#text_box_34_horizcenter_vertcenter", "#dark"),
                    manager=MANAGER,
                    anchors=(
                        {
                            "centerx": "centerx",
                            "top_target": self.clan_buttons[-1][-1],
                        }
                        if len(self.clan_buttons[-1]) % 8 != 0
                        else {"centerx": "centerx"}
                    ),
                )
            )

            # welcome to another bit of jank that I am embarrassed to put my name to!
            self.delete_buttons[-1].append(
                UIImageButton(
                    pygame.Rect(
                        (
                            ui_scale_value(470),
                            -0.5 * (item_height + ui_scale_value(22)),
                        ),
                        ui_scale_dimensions((22, 22)),
                    ),
                    "",
                    object_id="#exit_window_button",
                    manager=MANAGER,
                    starting_height=2,
                    anchors={"top_target": self.clan_buttons[-1][-1]},
                )
            )

            i += 1
            if i % 8 == 0 and i != 0:
                self.clan_buttons.append([])
                self.clan_name.append([])
                self.delete_buttons.append([])

        self.next_page_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((456, 540), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.previous_page_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((310, 540), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
        )
        self.page_number = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((0, 540), (110, 35))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
            anchors={
                "left": "left",
                "right": "right",
                "left_target": self.previous_page_button,
                "right_target": self.next_page_button,
            },
        )
        self.page = 0

        self.update_page()

    def update_page(self):
        """
        TODO: DOCS
        """

        if self.page == 0:
            self.previous_page_button.disable()
        else:
            self.previous_page_button.enable()

        if self.page >= len(self.clan_buttons) - 1:
            self.next_page_button.disable()
        else:
            self.next_page_button.enable()

        self.page_number.set_text(f"Page {self.page + 1} of {len(self.clan_buttons)}")

        for page in self.clan_buttons:
            for button in page:
                button.hide()
        for page in self.delete_buttons:
            for button in page:
                button.hide()

        for button in self.clan_buttons[self.page]:
            button.show()

        for button in self.delete_buttons[self.page]:
            button.show()

    def on_use(self):
        """
        TODO: DOCS
        """
        super().on_use()
