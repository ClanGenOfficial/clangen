import pygame
import logging
try:
    import ujson as json
except ImportError:
    import json
logger = logging.getLogger(__name__)


class _SoundManager():

    def __init__(self):
        self.sounds = {}

        try:
            pygame.mixer.init()
        except:
            logger.exception("Failed to initialize sound mixer")
            return

        try:
            with open("resources/audio/sounds.json", "r") as f:
                sound_data = json.load(f)
        except:
            logger.exception("Failed to load sound index")
            return

        for sound in sound_data:
            try:
                if "name" in sound:
                    self.sounds[sound["name"]] = pygame.mixer.Sound(
                        sound["path"])
                else:
                    self.sounds[sound["path"]] = pygame.mixer.Sound(
                        sound["path"])
            except:
                logger.exception("Failed to load sound")

    def play(self, sound):
        try:
            pygame.mixer.Sound.play(self.sounds[sound])
        except KeyError:
            logger.exception(f"Could not find sound {sound}")


sound_manager = _SoundManager()
