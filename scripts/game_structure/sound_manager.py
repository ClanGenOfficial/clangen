import pygame
import logging
try:
    import ujson as json
except ImportError:
    import json
logger = logging.getLogger(__name__)


class _SoundManager():

    def __init__(self, volume: int = 50):
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

        self._volume = volume

    def play(self, sound):
        try:
            pygame.mixer.Sound.play(self.sounds[sound])
        except KeyError:
            logger.exception(f"Could not find sound {sound}")
        except:
            logger.exception(f"Could not play sound {sound}")

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, a):
        if (a > 100):
            new_volume = 100
        elif (a < 0):
            new_volume = 0
        new_volume = a / 100

        for _, sound in self.sounds.items():
            sound.set_volume(new_volume)


sound_manager = _SoundManager()
