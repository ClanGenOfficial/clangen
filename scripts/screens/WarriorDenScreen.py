import i18n
import pygame
import pygame_gui
import ujson
from pygame_gui.core import ObjectID

from scripts.cat.cats import Cat
from scripts.clan_package.settings.clan_settings import (
    set_clan_setting,
    get_clan_setting,
    switch_clan_setting,
)
from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get
from scripts.cat.enums import CatRank
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.game_structure.constants import DISPLAY_SETTINGS, CONFIG
from scripts.ui.windows.select_focus_clans import SelectFocusClansWindow
from scripts.screens.Screens import Screens
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.theme import get_text_box_theme
from scripts.events_module.text_adjust import adjust_list_text
from scripts.ui.scale import ui_scale
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank

settings_dict = DISPLAY_SETTINGS["clan"]


class WarriorDenScreen(Screens):
    """
    The screen to change the focus of the Clan, which gives bonuses.
    """

    def __init__(self, name=None):
        super().__init__(name)
        # BG image assets - not interactable
        self.help_button = None
        self.focus_frame = None
        self.base_image = None
        self.focus_text = None

        self.focus = {}
        self.focus_buttons = {}
        self.focus_information = {}
        self.back_button = None
        self.save_button = None
        self.active_code = None
        self.original_focus_code = None
        self.other_clan_settings = [
            "sabotage_other_clans",
            "aid_other_clans",
            "raid_other_clans",
        ]

        self.has_mediators = True
        self.has_meddies = True

    def handle_event(self, event):
        """
        Here are button presses / events are handled.
        """
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            if event.ui_element in self.focus_buttons.values():
                for code, value in self.focus_buttons.items():
                    if value == event.ui_element:
                        self.active_code = code

                        # only enable the save button if a focus switch is possible
                        if (
                            game.clan.last_focus_change is None
                            or game.clan.last_focus_change
                            + constants.CONFIG["focus"]["duration"]
                            <= game.clan.age
                        ):
                            self.save_button.enable()

                        # deactivate save button if the focus didn't change or if rank prevents it
                        if (
                            self.active_code == self.original_focus_code
                            and self.save_button.is_enabled
                        ):
                            self.save_button.disable()

                        self.update_buttons()
                        self.update_visual()
                        self.create_side_info()
                        break

            elif event.ui_element == self.save_button:
                if self.active_code in self.other_clan_settings:
                    SelectFocusClansWindow()
                else:
                    # change the setting
                    switch_clan_setting(self.original_focus_code)
                    switch_clan_setting(self.active_code)
                    game.clan.last_focus_change = game.clan.age
                    self.original_focus_code = self.active_code

                    self.save_button.disable()
                    self.update_buttons()
                    self.create_top_info()

    def screen_switches(self):
        """
        Handle everything when it is switched to that screen.
        """
        super().screen_switches()

        self.has_mediators = (
            len(
                find_alive_cats_with_rank(
                    Cat, [CatRank.MEDIATOR, CatRank.MEDIATOR_APPRENTICE], working=True
                )
            )
            > 0
        )
        self.has_meddies = (
            len(
                find_alive_cats_with_rank(
                    Cat,
                    [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE],
                    working=True,
                )
            )
            > 0
        )

        self.hide_menu_buttons()
        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.help_button = UIImageButton(
            ui_scale(pygame.Rect((725, 25), (34, 34))),
            "",
            object_id=ObjectID("#help_button", "@image_button"),
            manager=MANAGER,
            tool_tip_text="screens.warrior_den.help_tooltip",
        )

        self.focus_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 190), (700, 460))),
            pygame.image.load("resources/images/warrior_den_frame.png").convert_alpha(),
            object_id="#focus_frame",
            starting_height=1,
            manager=MANAGER,
        )

        self.save_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((150, 592), (139, 30))),
            "screens.warrior_den.change_focus",
            get_button_dict(ButtonStyles.SQUOVAL, (139, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.save_button.disable()
        self.create_buttons()
        self.create_top_info()
        self.create_side_info()
        self.update_visual()

    def update_visual(self):
        """
        handles the creation and updates of the speech bubble visual
        """

        if self.base_image:
            self.base_image.kill()

        if game_setting_get("dark mode"):
            image = "base_image_dark"
        else:
            image = "base_image"

        self.base_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((442, 84), (264, 348))),
            pygame.image.load(
                f"resources/images/warrior_den/{image}.png"
            ).convert_alpha(),
            manager=MANAGER,
        )

        # check for a focus visual already onscreen and kill it, so we can update the visual. if it isn't onscreen,
        # then we display the visual of the old focus (this should trigger when the screen is first opened)
        if "focus_visual" in self.focus_information:
            self.focus_information["focus_visual"].kill()

            self.focus_information["focus_visual"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((442, 84), (264, 348))),
                pygame.image.load(
                    f"resources/images/warrior_den/{self.active_code}.png"
                ).convert_alpha(),
                manager=MANAGER,
            )

        else:
            self.focus_information["focus_visual"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((442, 84), (264, 348))),
                pygame.image.load(
                    f"resources/images/warrior_den/{self.original_focus_code}.png"
                ).convert_alpha(),
                manager=MANAGER,
            )

    def exit_screen(self):
        """
        Handles to delete everything when the screen is switched to another one.
        """
        self.back_button.kill()
        self.save_button.kill()
        self.focus_frame.kill()
        self.focus_text.kill()
        self.base_image.kill()
        self.help_button.kill()

        for button in self.focus_buttons:
            self.focus_buttons[button].kill()
        for ele in self.focus_information:
            self.focus_information[ele].kill()
        self.focus_information = {}
        for ele in self.focus:
            self.focus[ele].kill()
            self.focus = {}
        # if the focus wasn't changed, reset to the previous focus
        if self.original_focus_code != self.active_code:
            for code in settings_dict["clan_focus"].keys():
                set_clan_setting(code, code == self.original_focus_code)

    def update_buttons(self):
        for name, button in self.focus_buttons.items():
            # check mediator-related buttons
            if (
                not self.has_mediators
                and name in constants.CONFIG["focus"]["requires_mediator"]
            ):
                self.focus_buttons[name].disable()
                self.focus_buttons[name].set_text(f"settings.requires_mediator")
            # check meddie related buttons
            elif (
                not self.has_meddies
                and name in constants.CONFIG["focus"]["requires_medicine_cat"]
            ):
                self.focus_buttons[name].disable()
                self.focus_buttons[name].set_text(f"settings.requires_medicine_cat")
            # check chosen button
            elif self.active_code == name:
                self.focus_buttons[name].disable()
            # enable everyone else
            else:
                self.focus_buttons[name].enable()

    def create_buttons(self):
        """
        create the buttons for the different focuses
        """
        self.focus["button_container"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((100, 260), (250, 300))),
            manager=MANAGER,
        )

        anchor = {"top": "top"}
        for name, value in settings_dict["clan_focus"].items():
            if (
                game.clan.game_mode == "classic"
                and name in constants.CONFIG["focus"]["classic_disallows"]
            ):
                continue

            self.focus_buttons[name] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, 2), (250, 28))),
                f"settings.{name}",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (250, 28)),
                object_id=ObjectID(None, "@buttonstyles_rounded_rect"),
                container=self.focus["button_container"],
                starting_height=2,
                manager=MANAGER,
                anchors=anchor,
            )

            anchor = {"top_target": self.focus_buttons[name]}
            if get_clan_setting(name):
                self.active_code = name
                self.original_focus_code = name

            self.update_buttons()

    def create_top_info(self):
        """
        Create the top display text.
        """
        # delete previous created text if possible
        if "current_focus" in self.focus_information:
            self.focus_information["current_focus"].kill()
        if "time" in self.focus_information:
            self.focus_information["time"].kill()
        if self.focus_text:
            self.focus_text.kill()

        # create the new info text
        desc = " "
        name = i18n.t(f"settings.{self.original_focus_code}")
        if self.original_focus_code in self.other_clan_settings:
            desc = i18n.t(
                "screens.warrior_den.involved_clans",
                clans=adjust_list_text(
                    [f"{clan}clan" for clan in game.clan.clans_in_focus]
                ),
            )
        last_change_text = ""
        next_change = ""
        if game.clan.last_focus_change:
            last_change_text = i18n.t(
                "general.moon_date", moon=str(game.clan.last_focus_change)
            )
            moons = (
                game.clan.last_focus_change
                + constants.CONFIG["focus"]["duration"]
                - game.clan.age
            )
            moons = moons if moons > 0 else 0
            next_change = i18n.t(
                "screens.warrior_den.next_change",
                moons=i18n.t("general.moons_age", count=moons),
                count=moons,
            )

        focus = [
            i18n.t("screens.warrior_den.current_focus", name=name, desc=desc),
            i18n.t(
                "screens.warrior_den.focus_last_changed",
                last_changed=last_change_text,
                next_change=next_change,
            ),
        ]
        self.focus_information["current_focus"] = pygame_gui.elements.UITextBox(
            "\n".join(focus),
            ui_scale(pygame.Rect((50, 72), (355, 40))),
            wrap_to_height=True,
            object_id=get_text_box_theme(
                "#text_box_30_horizcenter_vertcenter_spacing_95"
            ),
            manager=MANAGER,
        )
        del focus
        self.focus_text = pygame_gui.elements.UITextBox(
            "screens.warrior_den.what_to_focus",
            ui_scale(pygame.Rect((92, 214), (272, 15))),
            wrap_to_height=True,
            object_id="#text_box_30_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
        )

    def create_side_info(self):
        """
        Creates the side information text.
        """
        # delete previous created text if possible
        if "side_text" in self.focus_information:
            self.focus_information["side_text"].kill()

        # create the new info text
        self.focus_information["side_text"] = pygame_gui.elements.UITextBox(
            "screens.warrior_den.selected_info",
            ui_scale(pygame.Rect((415, 466), (318, 130))),
            wrap_to_height=True,
            object_id="#text_box_30_horizcenter_vertcenter_spacing_95",
            manager=MANAGER,
            text_kwargs={"info": i18n.t(f"settings.{self.active_code}_tooltip")},
        )

    def save_focus(self):
        """
        Saves the focus when the clan to focus on in screen 'SelectFocusClan' are selected.
        """
        if len(game.clan.clans_in_focus) > 0:
            game.clan.last_focus_change = game.clan.age
            self.original_focus_code = self.active_code
