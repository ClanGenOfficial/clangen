from random import choice

import i18n
import pygame
import pygame_gui

from scripts.cat.cats import Cat
from scripts.cat.enums import CatSocial, CatStanding, CatThought
from scripts.game_structure import game
from scripts.game_structure.screen_settings import MANAGER
from scripts.ui.elements.checkbox import UICheckbox
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.cat.sprites.display_sprites import update_sprite
from scripts.events_module.text_adjust import process_text
from scripts.ui.scale import ui_scale


class LeaveClanWindow(GameWindow):
    """This window allows the user to send the selected cat away from the Clan"""

    def __init__(self, cat: Cat):
        super().__init__(
            ui_scale(pygame.Rect((250, 225), (300, 330))),
        )

        self.checkboxes = {}
        self.the_cat = cat
        self.chosen_social = None
        self.chosen_clan = None
        self.clan_choice = False

        self.heading = pygame_gui.elements.UITextBox(
            "windows.leave_clan",
            ui_scale(pygame.Rect((0, 10), (300, -1))),
            object_id="#text_box_30_horizcenter_spacing_95",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

        prev_element = self.heading
        for social in (
            CatSocial.LONER,
            CatSocial.ROGUE,
            CatSocial.KITTYPET,
            CatSocial.CLANCAT,
        ):
            self.checkboxes[social] = UICheckbox(
                position=(-40, 18),
                manager=MANAGER,
                container=self,
                anchors={"top_target": prev_element, "centerx": "centerx"},
            )

            self.checkboxes[f"{social}_text"] = pygame_gui.elements.UITextBox(
                f"general.{social}",
                ui_scale(pygame.Rect((0, 18), (100, -1))),
                object_id="#text_box_30_horizleft_spacing_95",
                manager=MANAGER,
                container=self,
                text_kwargs={"count": 1},
                anchors={
                    "top_target": prev_element,
                    "left_target": self.checkboxes[social],
                },
            )
            prev_element = self.checkboxes[social]

        self.done_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 280), (77, 30))),
            "buttons.done_lower",
            get_button_dict(ButtonStyles.SQUOVAL, (77, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
            container=self,
            anchors={"centerx": "centerx"},
        )

    def create_clan_checkboxes(self):
        self.clan_choice = True
        self.heading.set_text("windows.join_clan")

        for name in self.checkboxes:
            self.checkboxes[name].kill()

        self.checkboxes = {}
        prev_element = self.heading
        for other_clan in game.clan.all_other_clans:
            self.checkboxes[other_clan] = UICheckbox(
                position=(-50, 10),
                manager=MANAGER,
                container=self,
                anchors={"top_target": prev_element, "centerx": "centerx"},
            )
            self.checkboxes[f"{other_clan}_text"] = pygame_gui.elements.UITextBox(
                f"{other_clan.name}",
                ui_scale(pygame.Rect((0, 10), (150, -1))),
                object_id="#text_box_30_horizleft_spacing_95",
                manager=MANAGER,
                container=self,
                text_kwargs={"count": 1},
                anchors={
                    "top_target": prev_element,
                    "left_target": self.checkboxes[other_clan],
                },
            )
            prev_element = self.checkboxes[other_clan]

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.done_button:
                if self.clan_choice == True:
                    self.handle_clan_choice()
                else:
                    self.the_cat.leave_clan(self.chosen_social)
                game.all_screens[GameScreen.PROFILE].exit_screen()
                game.all_screens[GameScreen.PROFILE].screen_switches()
                self.kill()

            for name, button in self.checkboxes.items():
                if event.ui_element == button:
                    for _b in self.checkboxes.values():
                        if isinstance(_b, UICheckbox):
                            _b.uncheck()
                    if button.checked:
                        button.uncheck()
                    else:
                        button.check()
                        if self.clan_choice == True:
                            self.chosen_clan = name.group_ID
                        elif name == "clancat":
                            self.create_clan_checkboxes()
                        else:
                            self.chosen_social = CatSocial(name)
        return super().process_event(event)

    def handle_clan_choice(self):
        if not self.chosen_clan:
            self.chosen_clan = choice(game.clan.other_clan_IDs)

        self.the_cat.assign_thought(CatThought.ON_RANK_CHANGE)
        self.the_cat.status.add_to_group(
            new_group_ID=self.chosen_clan,
            standing_with_past_group=CatStanding.LEFT,
        )
