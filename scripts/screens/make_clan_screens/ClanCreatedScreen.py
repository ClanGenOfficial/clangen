import pygame
import pygame_gui

from scripts.cat.sprites.load_sprites import sprites
from scripts.game_structure import game
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.screen_settings import MANAGER
from scripts.screens.enums import GameScreen
from scripts.screens.make_clan_screens.MakeClanScreenBase import MakeClanScreenBase
from scripts.ui.elements.surface_image_button import UISurfaceImageButton
from scripts.ui.generate_button import ButtonStyles, get_button_dict
from scripts.ui.scale import ui_scale, ui_scale_dimensions
from scripts.ui.theme import get_text_box_theme


class ClanCreatedScreen(MakeClanScreenBase):
    def __init__(self, name="clan_created_screen"):
        super().__init__(name)

    def screen_switches(self):
        super().screen_switches()
        self.elements["menu_warning"].hide()
        self.elements["main_menu"].hide()
        self.elements["previous_step"].hide()
        self.elements["next_step"].hide()

        self.elements["selected_symbol"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((350, 105), (100, 100))),
            pygame.transform.scale(
                sprites.get_symbol(self.clan_info.symbol),
                ui_scale_dimensions((100, 100)),
            ).convert_alpha(),
            object_id="#selected_symbol",
            starting_height=1,
            manager=MANAGER,
        )

        self.elements["leader_image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((350, 125), (100, 100))),
            pygame.transform.scale(
                game.clan.leader.sprite, ui_scale_dimensions((100, 100))
            ),
            starting_height=1,
            manager=MANAGER,
        )
        self.elements["continue"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((346, 250), (102, 30))),
            "buttons.continue",
            get_button_dict(ButtonStyles.SQUOVAL, (102, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="save",
        )
        self.elements["save_confirm"] = pygame_gui.elements.UITextBox(
            "screens.make_clan.save_confirm",
            ui_scale(pygame.Rect((100, 70), (600, 30))),
            object_id=get_text_box_theme("#text_box_30_horizcenter"),
            manager=MANAGER,
        )

        self.get_camp_bg()

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.elements["continue"]:
                self.set_mute_button_position("bottomright")
                self.change_screen(GameScreen.CAMP)

        super().handle_event(event)

    def exit_screen(self):
        super().exit_screen()

        self.clan_info.clear()
        switch_set_value(Switch.clan_creation_info, self.clan_info.get_dict())
