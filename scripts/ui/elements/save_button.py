import traceback
from typing import Tuple, Optional, Union, Dict

import pygame
from pygame_gui.core import IContainerLikeInterface, UIElement

from scripts.cat.cats import Cat
from scripts.cat.save_load import save_cats
from scripts.game_structure import image_cache, game
from scripts.game_structure.game import switch_get_value, Switch
from scripts.game_structure.game.settings import game_settings_save
from scripts.game_structure.game.switches import switch_set_value
from scripts.game_structure.ui_elements import UISurfaceImageButton
from scripts.screens.enums import GameScreen
from scripts.ui.generate_button import get_button_dict, ButtonStyles
from scripts.ui.scale import ui_scale_dimensions, ui_scale
from scripts.ui.windows.save_error import SaveErrorWindow


class UISaveButton:
    DIMENSIONS = (114, 30)

    def __init__(
        self,
        position: Tuple[int, int],
        container: Optional[IContainerLikeInterface] = None,
        starting_height: int = 1,
        anchors: Dict[str, Union[str, UIElement]] = None,
        visible: int = 1,
    ):
        """
        Creates a save button with unsaved, saving, and saved visual states.
        :param position: The UNSCALED position of the button.
        :param container: The container of the button.
        :param starting_height: The layer height of the button.
        :param anchors: The anchor dictionary.
        :param visible: The visible state of the button.
        """
        self.unsaved_state_dict = get_button_dict(ButtonStyles.SQUOVAL, self.DIMENSIONS)
        # this needs to be here to that the scaling is updated properly
        self.unsaved_state_dict["normal"] = pygame.transform.scale(
            image_cache.load_image("resources/images/buttons/save_clan.png"),
            ui_scale_dimensions(self.DIMENSIONS),
        )

        self.unsaved_state = UISurfaceImageButton(
            ui_scale(pygame.Rect(position, self.DIMENSIONS)),
            "buttons.save_clan",
            self.unsaved_state_dict,
            object_id="@buttonstyles_squoval",
            sound_id="save",
            container=container,
            starting_height=starting_height,
            anchors=anchors,
            visible=visible,
        )
        self.unsaved_state.enable()
        self.saving_state = UISurfaceImageButton(
            ui_scale(pygame.Rect(position, self.DIMENSIONS)),
            "buttons.saving",
            {
                "normal": get_button_dict(ButtonStyles.SQUOVAL, self.DIMENSIONS)[
                    "normal"
                ]
            },
            object_id="@buttonstyles_squoval",
            container=container,
            starting_height=starting_height,
            anchors=anchors,
        )
        self.saving_state.hide()
        self.saving_state.disable()
        self.saved_state = UISurfaceImageButton(
            ui_scale(pygame.Rect(position, self.DIMENSIONS)),
            "buttons.clan_saved",
            {
                "normal": pygame.transform.scale(
                    image_cache.load_image("resources/images/save_clan_saved.png"),
                    ui_scale_dimensions(self.DIMENSIONS),
                )
            },
            object_id="@buttonstyles_squoval",
            container=container,
            starting_height=starting_height,
            anchors=anchors,
        )
        self.saved_state.hide()
        self.saved_state.disable()

    def kill(self):
        """
        Kills all elements in this button.
        """
        self.unsaved_state.kill()
        self.saving_state.kill()
        self.saved_state.kill()

    def update_state(self):
        """
        Updates visual state of the buttons to match the game's current save state.
        """
        if switch_get_value(Switch.saved_clan):
            self.unsaved_state.disable()
            self.saving_state.hide()
            self.saved_state.show()
        else:
            self.unsaved_state.enable()
            self.saving_state.hide()
            self.saved_state.hide()

    def save_game(self, current_screen):
        """
        Saves the game and updates visual state of this button. If save fails, save error window is created and game is thrown to the main menu screen.
        :param current_screen: object for the current game screen
        """
        try:
            self.unsaved_state.disable()
            self.saving_state.show()
            save_cats(switch_get_value(Switch.clan_name), Cat, game)
            game.clan.save_clan()
            game.clan.save_pregnancy(game.clan)
            game.save_events()
            game_settings_save(current_screen),
            switch_set_value(Switch.saved_clan, True)
            self.update_state()
        except RuntimeError:
            SaveErrorWindow(traceback.format_exc())
            switch_set_value(Switch.cur_screen, GameScreen.START)
            game.last_screen_forupdate = current_screen
            game.switch_screens = True

    def reset_save(self):
        """
        Resets the saved_clan switch and updates visual state of this button.
        """
        switch_set_value(Switch.saved_clan, False)
        self.update_state()
