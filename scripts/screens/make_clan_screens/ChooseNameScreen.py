import pygame
import pygame_gui
from pygame_gui.core import UIContainer

from scripts.game_structure import image_cache
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.ui.elements.modified_image import UIModifiedImage
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.icon import Icon
from scripts.ui.scale import ui_scale, ui_scale_dimensions

from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase


class ChooseNameScreen(MakeClanScreenBase):
    def __init__(self, name="choose_name_screen"):
        super().__init__(name)

    def screen_switches(self):
        super().screen_switches()

        name_backdrop = image_cache.load_image(
            "resources/images/pick_clan_screen/name_clan_light.png"
        ).convert_alpha()
        self.elements["game_mode_background"] = UIModifiedImage(
            ui_scale(pygame.Rect((0, 0), (800, 700))),
            pygame.transform.scale(name_backdrop, ui_scale_dimensions((800, 700))),
            manager=MANAGER,
        )
        self.elements["game_mode_background"].disable()

        self.elements["title"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.name_clan_title",
            ui_scale(pygame.Rect((0, 495), (300, 40))),
            object_id="@clangen_32",
            anchors={"centerx": "centerx"},
        )
        self.elements["subtitle"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.name_clan_subtitle",
            ui_scale(pygame.Rect((0, -5), (300, 30))),
            object_id="@buttonstyles_rounded_rect",
            anchors={"centerx": "centerx", "top_target": self.elements["title"]},
        )

        self.elements["entry_container"] = UIContainer(
            ui_scale(pygame.Rect((224, 565), (400, 100))), manager=MANAGER
        )

        self.elements["random"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((0, 0), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            container=self.elements["entry_container"],
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
        )
        self.elements["name_entry"] = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((41, 2), (140, 29))),
            container=self.elements["entry_container"],
            manager=MANAGER,
            initial_text=self.clan_info.display_name
            if self.clan_info.display_name
            else None,
        )
        self.elements["name_entry"].set_forbidden_characters("forbidden_file_path")
        self.elements["name_entry"].set_text_length_limit(11)
        self.elements["clan"] = pygame_gui.elements.UITextBox(
            "general.clan",
            ui_scale(pygame.Rect((151, 5), (100, 25))),
            container=self.elements["entry_container"],
            object_id="#text_box_30_horizcenter_light",
            text_kwargs={"name": "-"},
            manager=MANAGER,
        )
        self.elements["reset_name"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((231, 0), (134, 30))),
            "screens.make_clan.reset_name",
            get_button_dict(ButtonStyles.SQUOVAL, (134, 30)),
            container=self.elements["entry_container"],
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["random"]:
                self.elements["name_entry"].set_text(self.random_clan_name())
            elif event.ui_element == self.elements["reset_name"]:
                self.elements["name_entry"].set_text("")
            elif event.ui_element == self.elements["next_step"]:
                self.clan_info.display_name = (
                    self.elements["name_entry"].get_text().strip()
                )
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_CATS)
            elif event.ui_element == self.elements["previous_step"]:
                self.change_screen(GameScreen.MAKE_CLAN_CHOOSE_MODE)

        return super().handle_event(event)

    def on_use(self):
        super().on_use()

        # Don't allow someone to enter no name for their clan
        if self.elements["name_entry"].get_text() == "":
            self.elements["next_step"].disable()
        elif self.elements["name_entry"].get_text().startswith(" "):
            self.elements["next_step"].disable()
        else:
            self.elements["next_step"].enable()
