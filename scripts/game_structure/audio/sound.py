import logging
import random
from typing import Union

import pygame
import pygame_gui
import ujson

from scripts.game_structure.game.settings import game_setting_get, game_setting_set
from scripts.ui.elements.cat_button import CatButton
from scripts.ui.elements.image_button import UIImageButton
from scripts.ui.elements.sprite_button import UISpriteButton
from scripts.ui.elements.surface_image_button import UISurfaceImageButton

logger = logging.getLogger(__name__)


class Sound:
    def __init__(self):
        self.volume = game_setting_get("sound_volume") / 100
        self.pressed = None
        self.muted = False

        self.sound_dict = {}

    def load_sounds(self):
        # open up the sound dictionary
        try:
            with open("resources/audio/sounds.json", "r", encoding="utf-8") as f:
                sound_data = ujson.load(f)
        except:
            logger.exception("Failed to load sound index")
            return
        for sound in sound_data:
            try:
                self.sound_dict[sound] = []
                for path in sound_data[sound]:
                    self.sound_dict[sound].append(
                        pygame.mixer.Sound("resources/audio/sounds/" + path)
                    )

                for each in self.sound_dict[sound]:
                    each.set_volume(self.volume)
            except:
                logger.exception("Failed to load sound")

    def handle_sound_events(self, event):
        """
        assigns universal sound effects to event.type objects
        SHOULD NOT BE USED FOR INDIVIDUAL UNIQUE BUTTON SOUNDS
        UIImageButtons have a sound_id parameter for assigning unique sounds to individual buttons
        :param event: the event that is taking place
        """
        # This makes sounds play using UI_BUTTON_PRESSED, instead of UI_BUTTON_START_PRESS
        try:
            if event.ui_element.sound_id in ["timeskip"]:
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.play("button_press", event.ui_element)
                else:
                    return
        except AttributeError:
            pass

        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.pressed = event.ui_element
            self.play("button_press", event.ui_element)
        elif event.type == pygame_gui.UI_BUTTON_ON_HOVERED:
            if event.ui_element.__class__ not in [CatButton, UISpriteButton]:
                if self.pressed != event.ui_element:
                    self.play("button_hover")
            self.pressed = None

    def play(self, sound, button: Union[UISurfaceImageButton, UIImageButton] = None):
        """
        Plays the given sound, if an ImageButton is passed through then the sound_id of the ImageButton will be
        used instead
        :param sound: The sound to play
        :param button: If included, sound played will be the sound_id of the button
        """
        if self.muted:
            return

        if button and hasattr(button, "sound_id"):
            try:
                if button.sound_id is not None:
                    sound = button.sound_id
            except AttributeError:
                logger.exception(f"That ui_element has no sound_id.")

        try:
            if pygame.mixer.find_channel():
                chosen = random.choice(self.sound_dict[sound])
                chosen.play()
        except KeyError:
            logger.exception(f"Could not find sound {sound}")

    def change_volume(self, new_volume: int):
        """
        changes the volume
        :param new_volume: The new volume to set music to, int given should be between 0 and 100
        """
        # make sure given volume is between 0 and 100
        if new_volume > 100:
            new_volume = 100
        elif new_volume < 0:
            new_volume = 0

        # convert to a float and change volume accordingly
        self.volume = new_volume / 100
        game_setting_set("sound_volume", new_volume)
        for sound in self.sound_dict:
            for each in self.sound_dict[sound]:
                each.set_volume(self.volume)
