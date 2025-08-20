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
from scripts.game_structure.ui_elements import UIImageButton, UISurfaceImageButton
from scripts.game_structure.windows import SelectFocusClans
from scripts.screens.Screens import Screens
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.utility import (
    ui_scale,
    find_alive_cats_with_rank,
    get_text_box_theme,
    adjust_list_text,
)

with open("resources/clansettings.json", "r", encoding="utf-8") as f:
    settings_dict = ujson.load(f)


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
            "sabotage other clans",
            "aid other clans",
            "raid other clans",
        ]
        self.not_classic_codes = ["hunting", "raid other clans", "hoarding"]

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
                        description = settings_dict["clan_focus"][code][1]

                        # TODO why is this here twice?
                        switch_clan_setting(self.active_code)
                        switch_clan_setting(code)
                        self.active_code = code

                        # un-switch the old checkbox
                        switch_clan_setting(self.active_code)
                        # switch the new checkbox
                        switch_clan_setting(code)
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
                        if "mediator" in description and self.save_button.is_enabled:
                            # only create the mediator list if needed to check
                            mediator_list = list(
                                filter(
                                    lambda x: x.status.rank == CatRank.MEDIATOR
                                    and x.status.alive_in_player_clan,
                                    Cat.all_cats_list,
                                )
                            )
                            if len(mediator_list) < 1:
                                self.save_button.disable()
                        elif (
                            "medicine cat" in description
                            and self.save_button.is_enabled
                        ):
                            meds = find_alive_cats_with_rank(
                                Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE]
                            )
                            if len(meds) < 1:
                                self.save_button.disable()

                        self.update_buttons()
                        self.update_visual()
                        self.create_side_info()
                        break

            elif event.ui_element == self.save_button:
                if self.active_code in self.other_clan_settings:
                    SelectFocusClans()
                else:
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

            path = settings_dict["clan_focus"][self.active_code][3]
            self.focus_information["focus_visual"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((442, 84), (264, 348))),
                pygame.image.load(
                    f"resources/images/warrior_den/{path}.png"
                ).convert_alpha(),
                manager=MANAGER,
            )

        else:
            path = settings_dict["clan_focus"][self.original_focus_code][3]
            self.focus_information["focus_visual"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((442, 84), (264, 348))),
                pygame.image.load(
                    f"resources/images/warrior_den/{path}.png"
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
        for code, button in self.focus_buttons.items():
            if self.active_code == code:
                button.disable()
            else:
                button.enable()
            if game.clan.game_mode == "classic" and code in self.not_classic_codes:
                button.disable()

    def create_buttons(self):
        """
        create the buttons for the different focuses
        """
        self.focus["button_container"] = pygame_gui.core.UIContainer(
            ui_scale(pygame.Rect((100, 260), (250, 300))),
            manager=MANAGER,
        )

        # n increments the y placement
        n = 0

        for i, (code, desc) in enumerate(settings_dict["clan_focus"].items()):
            self.focus_buttons[code] = UISurfaceImageButton(
                ui_scale(pygame.Rect((0, 2), (250, 28))),
                f"settings.{code}",
                get_button_dict(ButtonStyles.ROUNDED_RECT, (250, 28)),
                object_id=ObjectID(None, "@buttonstyles_rounded_rect"),
                container=self.focus["button_container"],
                starting_height=2,
                manager=MANAGER,
                anchors=(
                    {
                        "top_target": self.focus_buttons[
                            list(settings_dict["clan_focus"])[i - 1]
                        ]
                    }
                    if i > 0
                    else {"top": "top"}
                ),
            )

            if get_clan_setting(code):
                self.focus_buttons[code].disable()
                self.original_focus_code = code
                self.active_code = code
            else:
                self.focus_buttons[code].enable()
            if game.clan.game_mode == "classic" and code in self.not_classic_codes:
                self.focus_buttons[code].disable()

            n += 1

        # # create scrollbar
        # self.focus["button_container"].set_scrollable_area_dimensions(
        #     ui_scale_dimensions((250, (len(settings_dict["clan_focus"]) * 30 + 100)))
        # )

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
