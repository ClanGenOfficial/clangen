from random import randrange, choice

import pygame
import pygame_gui

from scripts.cat.cats import create_cat, create_example_cats
from scripts.cat.enums import CatRank
from scripts.cat.sprites.load_sprites import sprites
from scripts.game_structure import image_cache
from scripts.game_structure.game import Switch
from scripts.game_structure.game.settings import game_setting_set
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.ui.elements.checkbox import UICheckbox
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme


class ChooseModeScreen(MakeClanScreenBase):
    def __init__(self, name="choose_mode_screen"):
        super().__init__(name)

        self.game_mode = "classic"

    def screen_switches(self):
        # Reset variables
        switch_set_value(Switch.possible_cats, create_example_cats())

        super().screen_switches()
        self.elements["previous_step"].disable()
        self.elements["next_step"].enable()

        self.set_mute_button_position("topright")
        self.show_mute_buttons()
        self.set_bg("default", "mainmenu_bg")

        # MODE DESCRIPTION
        text_box = image_cache.load_image(
            "resources/images/game_mode_text_box.png"
        ).convert_alpha()
        self.elements["game_mode_background"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((325, 130), (399, 461))),
            pygame.transform.scale(text_box, ui_scale_dimensions((399, 461))),
            manager=MANAGER,
        )

        # Create all the elements.
        self.elements["classic_mode_button"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((109, 240), (132, 30))),
            "screens.make_clan.classic_label",
            get_button_dict(ButtonStyles.SQUOVAL, (132, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )
        self.elements["expanded_mode_button"] = UIImageButton(
            ui_scale(pygame.Rect((94, 320), (162, 34))),
            "screens.make_clan.expanded_label",
            object_id="#expanded_mode_button",
            manager=MANAGER,
        )
        self.elements["cruel_season_mode_button"] = UIImageButton(
            ui_scale(pygame.Rect((100, 400), (150, 30))),
            "screens.make_clan.cruel_season_label",
            object_id="#cruel_season_mode_button",
            manager=MANAGER,
        )

        self.elements["game_mode_warning"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.game_mode_warning",
            ui_scale(pygame.Rect((100, 581), (600, 40))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        self.elements["random_clan_checkbox"] = UICheckbox(
            (560, -32),
            manager=MANAGER,
            tool_tip_text="screens.make_clan.quick_start_tooltip",
            anchors={"top_target": self.elements["previous_step"]},
        )

        self.elements["random_clan_checkbox_label"] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((5, -28), (-1, -1))),
            "screens.make_clan.quick_start",
            manager=MANAGER,
            object_id=get_text_box_theme("#text_box_30_horizleft"),
            anchors={
                "left_target": self.elements["random_clan_checkbox"],
                "top_target": self.elements["random_clan_checkbox"],
            },
        )
        self.elements["mode_details"] = UITextBoxTweaked(
            "",
            ui_scale(pygame.Rect((345, 180), (365, 360))),
            object_id="#text_box_30_horizleft",
            manager=MANAGER,
        )

        self.elements["mode_name"] = pygame_gui.elements.UITextBox(
            "",
            ui_scale(pygame.Rect((425, 135), (200, 27))),
            object_id="#text_box_30_horizcenter_light",
            manager=MANAGER,
        )

        self.refresh_text_and_buttons()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["classic_mode_button"]:
                self.game_mode = "classic"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["expanded_mode_button"]:
                self.game_mode = "expanded"
                self.refresh_text_and_buttons()
            elif event.ui_element == self.elements["cruel_season_mode_button"]:
                self.game_mode = "cruel season"
                self.refresh_text_and_buttons()

            # Logic for when to quick-start clan
            elif event.ui_element == self.elements["next_step"]:
                game_setting_set("game_mode", self.game_mode)
                self.clan_info.game_mode = self.game_mode
                if self.elements["random_clan_checkbox"].checked:
                    self.random_quick_start()
                    self.save_clan()
                    self.change_screen(GameScreen.MAKE_CLAN_CLAN_CREATED)
                else:
                    self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_NAME)
            elif event.ui_element == self.elements["random_clan_checkbox"]:
                if self.elements["random_clan_checkbox"].checked:
                    self.elements["random_clan_checkbox"].uncheck()
                elif not self.elements["random_clan_checkbox"].checked:
                    self.elements["random_clan_checkbox"].check()

        return super().handle_event(event)

    def refresh_text_and_buttons(self):
        """Refreshes the button states and text boxes"""
        # Set the mode explanation text
        if self.game_mode == "classic":
            display_text = "screens.make_clan.classic_info"
            display_name = "screens.make_clan.classic_label"
        elif self.game_mode == "expanded":
            display_text = "screens.make_clan.expanded_info"
            display_name = "screens.make_clan.expanded_label"
        elif self.game_mode == "cruel season":
            display_text = "screens.make_clan.cruel_season_info"
            display_name = "screens.make_clan.cruel_season_label"
        else:
            display_text = ""
            display_name = "ERROR"

        self.elements["mode_details"].set_text(display_text)
        self.elements["mode_name"].set_text(display_name)

        # Update the enabled buttons for the game selection
        if self.game_mode == "classic":
            self.elements["classic_mode_button"].disable()
            self.elements["expanded_mode_button"].enable()
            self.elements["cruel_season_mode_button"].enable()
        elif self.game_mode == "expanded":
            self.elements["classic_mode_button"].enable()
            self.elements["expanded_mode_button"].disable()
            self.elements["cruel_season_mode_button"].enable()
        elif self.game_mode == "cruel season":
            self.elements["classic_mode_button"].enable()
            self.elements["expanded_mode_button"].enable()
            self.elements["cruel_season_mode_button"].disable()
        else:
            self.elements["classic_mode_button"].enable()
            self.elements["expanded_mode_button"].enable()
            self.elements["cruel_season_mode_button"].enable()

    def random_quick_start(self):
        self.clan_info.name = self.random_clan_name()
        self.clan_info.biome = self.random_biome_selection()
        self.clan_info.camp_bg = f"camp{randrange(1, 5)}"

        # SYMBOL
        if f"symbol{self.clan_info.name.upper()}0" in sprites.clan_symbols:
            # Use recommended symbol if it exists
            symbol = f"symbol{self.clan_info.name.upper()}0"
        else:
            symbol = choice(sprites.clan_symbols)

        self.clan_info.symbol = symbol

        # MEMBERS
        self.clan_info.leader = create_cat(CatRank.WARRIOR)
        self.clan_info.deputy = create_cat(CatRank.WARRIOR)
        self.clan_info.medicine_cat = create_cat(CatRank.WARRIOR)
        members = []
        for _ in range(randrange(4, 8)):
            random_rank = choice(
                [
                    CatRank.KITTEN,
                    CatRank.APPRENTICE,
                    CatRank.WARRIOR,
                    CatRank.WARRIOR,
                    CatRank.ELDER,
                ]
            )
            members.append(create_cat(rank=random_rank))

        self.clan_info.starting_members = members
