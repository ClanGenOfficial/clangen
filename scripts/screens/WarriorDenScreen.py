import pygame
import pygame_gui
import ujson

from scripts.cat.cats import Cat
from scripts.game_structure.windows import SelectFocusClans
from scripts.screens.Screens import Screens
from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.game_essentials import game, screen_x, screen_y, MANAGER
from scripts.utility import get_med_cats, scale, get_text_box_theme

with open('resources/clansettings.json', 'r', encoding='utf-8') as f:
    settings_dict = ujson.load(f)


class WarriorDenScreen(Screens):
    """
    The screen to change the focus of the Clan, which gives bonuses.
    """

    def __init__(self, name=None):
        super().__init__(name)
        # BG image assets - not interactable
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
        self.other_clan_settings = ["sabotage other clans", "aid other clans", "raid other clans"]
        self.not_classic_codes = ["hunting", "raid other clans", "hoarding"]

    def handle_event(self, event):
        """
        Here are button presses / events are handled.
        """
        if game.switches['window_open']:
            pass
        elif event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            if event.ui_element in self.focus_buttons.values():
                for code, value in self.focus_buttons.items():
                    if value == event.ui_element:
                        description = settings_dict["clan_focus"][code][1]

                        game.clan.switch_setting(self.active_code)
                        game.clan.switch_setting(code)
                        self.active_code = code

                        # un-switch the old checkbox
                        game.clan.switch_setting(self.active_code)
                        # switch the new checkbox
                        game.clan.switch_setting(code)
                        self.active_code = code
                        # only enable the save button if a focus switch is possible
                        if game.clan.last_focus_change is None or \
                                game.clan.last_focus_change + game.config["focus"]["duration"] <= game.clan.age:
                            self.save_button.enable()

                        # deactivate save button if the focus didn't change or if rank prevents it
                        if self.active_code == self.original_focus_code and self.save_button.is_enabled:
                            self.save_button.disable()
                        if "mediator" in description and self.save_button.is_enabled:
                            # only create the mediator list if needed to check
                            mediator_list = list(filter(
                                lambda x: x.status == "mediator" and not x.dead and not x.outside, Cat.all_cats_list
                            ))
                            if len(mediator_list) < 1:
                                self.save_button.disable()
                        elif "medicine cat" in description and self.save_button.is_enabled:
                            meds = get_med_cats(Cat, working=False)
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
        self.hide_menu_buttons()
        self.back_button = UIImageButton(scale(pygame.Rect((50, 50), (210, 60))), "", object_id="#back_button"
                                         , manager=MANAGER)
        self.help_button = UIImageButton(scale(pygame.Rect(
            (1450, 50), (68, 68))),
            "",
            object_id="#help_button", manager=MANAGER,
            tool_tip_text="This screen allows you to manage your warriors more effectively! You can give them a "
                          "specific focus, which will provide some benefits (and possibly some negatives) to your "
                          "Clan.  Some focuses are not available in classic mode.  Click on each focus to see a "
                          "description of what they will do.  Focuses that target other Clans will allow you to "
                          "choose which Clans you target.  Your focus can only be changed every 3 moons, "
                          "so choose carefully.",

        )

        self.focus_frame = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                             ((100, 380), (1400, 920))),
                                                       pygame.image.load(
                                                           "resources/images/warrior_den_frame.png").convert_alpha(),
                                                       manager=MANAGER)
        self.focus_frame.disable()


        self.save_button = UIImageButton(scale(pygame.Rect((300, 1184), (278, 60))),
                                         "",
                                         object_id="#change_focus_button",
                                         manager=MANAGER)
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

        if game.settings["dark mode"]:
            image = "base_image_dark"
        else:
            image = "base_image"

        self.base_image = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                            ((885, 169), (528, 696))),
                                                      pygame.image.load(
                                                          f"resources/images/warrior_den/{image}.png").convert_alpha(),
                                                      manager=MANAGER)

        # check for a focus visual already onscreen and kill it so we can update the visual. if it isn't onscreen,
        # then we display the visual of the old focus (this should trigger when the screen is first opened)
        if "focus_visual" in self.focus_information:
            self.focus_information["focus_visual"].kill()

            path = settings_dict["clan_focus"][self.active_code][3]
            self.focus_information["focus_visual"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                                       ((885, 169), (528, 696))),
                                                                                 pygame.image.load(
                                                                                     f"resources/images/warrior_den/{path}.png").convert_alpha(),
                                                                                 manager=MANAGER)

        else:
            path = settings_dict["clan_focus"][self.original_focus_code][3]
            self.focus_information["focus_visual"] = pygame_gui.elements.UIImage(scale(pygame.Rect
                                                                                       ((885, 169), (528, 696))),
                                                                                 pygame.image.load(
                                                                                     f"resources/images/warrior_den/{path}.png").convert_alpha(),
                                                                                 manager=MANAGER)

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
        # if the focus wasn't changed, reset to the previous focus
        if self.original_focus_code != self.active_code:
            for code in settings_dict["clan_focus"].keys():
                if code == self.original_focus_code:
                    game.clan.clan_settings[code] = True
                else:
                    game.clan.clan_settings[code] = False

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
        self.focus["button_container"] = pygame_gui.elements.UIScrollingContainer(
            scale(pygame.Rect((200, 520), (700, 800))), manager=MANAGER
        )

        # n increments the y placement
        n = 0

        for code, desc in settings_dict["clan_focus"].items():

            self.focus_buttons[code] = UIImageButton(scale(pygame.Rect(
                (0, n * 62), (500, 56))),
                "",
                object_id=desc[4],
                container=self.focus["button_container"],
                manager=MANAGER)

            if game.clan.clan_settings[code]:
                self.focus_buttons[code].disable()
                self.original_focus_code = code
                self.active_code = code
            else:
                self.focus_buttons[code].enable()
            if game.clan.game_mode == "classic" and code in self.not_classic_codes:
                self.focus_buttons[code].disable()

            n += 1

        # create scrollbar
        self.focus["button_container"].set_scrollable_area_dimensions(
            (500 / 1600 * screen_x, (n * 62 + 200) / 1600 * screen_y)
        )

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
        name = settings_dict["clan_focus"][self.original_focus_code][0]
        if self.original_focus_code in self.other_clan_settings:
            desc = "<br><b>Involved Clans:</b> "
            if len(game.clan.clans_in_focus) == 1:
                desc += f"{game.clan.clans_in_focus[0]}clan"
            if len(game.clan.clans_in_focus) == 2:
                desc += f"{game.clan.clans_in_focus[0]}clan and {game.clan.clans_in_focus[1]}clan"
            elif len(game.clan.clans_in_focus) > 2:
                desc += "clan, ".join(game.clan.clans_in_focus[:-1])
                desc += f"clan and {game.clan.clans_in_focus[-1]}clan"

        last_change_text = "unknown"
        next_change = "0 moons"
        if game.clan.last_focus_change:
            last_change_text = "moon " + str(game.clan.last_focus_change)
            moons = game.clan.last_focus_change + game.config["focus"]["duration"] - game.clan.age
            if moons == 1:
                next_change = f"{moons} moon"
            elif moons > 0:
                next_change = f"{moons} moons"
            else:
                next_change = f"0 moons"

        self.focus_information["current_focus"] = pygame_gui.elements.UITextBox(
            f"<b>Current Focus:</b> {name}{desc}<br><b>Focus Last Changed:</b> {last_change_text}<br>(next change in {next_change})",
            scale(pygame.Rect((100, 145), (710, 80))),
            wrap_to_height=True,
            object_id=get_text_box_theme("#text_box_30_horizcenter_vertcenter_spacing_95"),
            manager=MANAGER
        )
        self.focus_text = pygame_gui.elements.UITextBox(
            f"What should your warriors focus on?",
            scale(pygame.Rect((184, 428), (544, 30))),
            wrap_to_height=True,
            object_id="#text_box_30_horizcenter_vertcenter_spacing_95",
            manager=MANAGER
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
            f"<b>Selected information:</b><br>" + settings_dict["clan_focus"][self.active_code][1],
            scale(pygame.Rect((830, 932), (636, 260))),
            wrap_to_height=True,
            object_id="#text_box_30_horizcenter_vertcenter_spacing_95",
            manager=MANAGER
        )

    def save_focus(self):
        """
        Saves the focus when the clan to focus on in screen 'SelectFocusClan' are selected.
        """
        if len(game.clan.clans_in_focus) > 0:
            game.clan.last_focus_change = game.clan.age
            self.original_focus_code = self.active_code
