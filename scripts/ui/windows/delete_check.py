import os
import shutil

import i18n
import pygame
import pygame_gui

from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.housekeeping.datadir import get_save_dir
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.windows.window_base_class import GameWindow
from scripts.ui.scale import ui_scale


class CheckDeletionWindow(GameWindow):
    def __init__(self, reloadscreen, clan_id, clan_display_name):
        super().__init__(
            ui_scale(pygame.Rect((250, 200), (300, 250))),
        )
        self.clan_name = clan_id
        self.reloadscreen = reloadscreen

        self.delete_check_message = UITextBoxTweaked(
            "windows.delete_check_message",
            ui_scale(pygame.Rect((20, 20), (260, -1))),
            line_spacing=1,
            object_id="#text_box_30_horizcenter",
            container=self,
            text_kwargs={
                "clan": i18n.t("general.clan", name=clan_display_name),
                "clan_id": clan_id,
            },
        )

        self.delete_it_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((71, 125), (153, 30))),
            "windows.delete_yes",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            container=self,
        )
        self.go_back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((71, 170), (153, 30))),
            "windows.delete_no",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            container=self,
        )

        self.go_back_button.enable()
        self.delete_it_button.enable()

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.delete_it_button:
                rempath = get_save_dir() + "/" + self.clan_name
                shutil.rmtree(rempath)
                if os.path.exists(rempath + "clan.json"):
                    os.remove(rempath + "clan.json")
                elif os.path.exists(rempath + "clan.txt"):
                    os.remove(rempath + "clan.txt")
                else:
                    print("No clan.json/txt???? Clan prolly wasnt initalized kekw")
                self.kill()
                self.reloadscreen(GameScreen.SWITCH_CLAN)

            elif event.ui_element == self.go_back_button:
                self.kill()
        return super().process_event(event)
