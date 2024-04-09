import pygame
import logging
import ujson
logger = logging.getLogger(__name__)

from scripts.game_structure.game_essentials import game

menu_screens = ['settings screen', 'start screen', 'switch clan screen', 'make clan screen']

menu_music = "resources/audio/music/Generations.wav"
forest_music = []
plains_music = []
beach_music = []
mountain_music = []


class MusicManager():

    def __init__(self):
        self.current_music = None
        self.playlist = None
        self.muted = False
        self.volume = game.settings["music_volume"]/100

    def check_music(self, screen):
        """
        checks if music currently playing is appropriate for the given screen and changes the music if needed
        """
        if self.muted:
            return

        # this should only occur when the game has just opened
        if not self.current_music and screen == 'start screen':
            self.play_music(menu_music, -1)

        # otherwise we're checking is the screen is or isn't the menu and changing music accordingly
        elif screen in menu_screens:
            if not self.current_music == menu_music:
                self.fade_music()
                # self.play_music(self.get_biome_music)
            elif not pygame.mixer.music.get_busy():
                self.play_music(menu_music, -1)
        elif screen not in menu_screens:
            if self.current_music == menu_music:
                self.fade_music()
                # self.play_music(self.get_biome_music)
            elif not pygame.mixer.music.get_busy():
                self.play_music(menu_music, -1)

    def play_music(self, music, loops=0):
        """
        loads and plays given music file, sets self.current_music to given music file
        """
        self.current_music = music
        pygame.mixer.music.load(music)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(loops)

    def fade_music(self, fadeout=2000):
        """
        fades the music out, by default the fade is 2 seconds
        """
        pygame.mixer.music.fadeout(fadeout)

    def mute_music(self):
        """
        stops all music, current and future
        """
        pygame.mixer.music.stop()
        self.muted = True

    def unmute_music(self, screen):
        """
        unmutes, allowing current and future music to play
        must pass current screen name to ensure correct music plays when unmuted
        """
        self.muted = False
        self.check_music(screen)

    def change_volume(self, volume):
        """ changes the volume, int given should be between 0 and 100"""
        # make sure given volume is between 0 and 100
        if volume > 100:
            volume = 100
        if volume < 0:
            volume = 0

        # convert to a float and change volume accordingly
        self.volume = volume/100
        game.settings["music_volume"] = volume
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.volume)

    def get_biome_music(self):
        """
        use this to find the starting biome music and biome
        not currently used as we have no biome music, but this should work when we do
        """
        if game.clan.biome == 'Forest':
            self.playlist = forest_music
            return forest_music[0]
        elif game.clan.biome == 'Plains':
            self.playlist = plains_music
            return plains_music[0]
        elif game.clan.biome == 'Mountainous':
            self.playlist = mountain_music
            return mountain_music[0]
        elif game.clan.biome == 'Beach':
            self.playlist = beach_music
            return beach_music[0]

    def queue_biome_music(self):
        """
        use this to start a queue of biome music after loading the first biome music file
        leaving this be for now until we actually have a playlist to experiment with
        """
        # pygame.mixer.music.queue()


music_manager = MusicManager()

# old soundmanager class, i'll come back to this when we have sound effects to implement
"""class _SoundManager():

    def __init__(self, volume: int = 50):
        self.sounds = {}

        try:
            pygame.mixer.init()
        except:
            logger.exception("Failed to initialize sound mixer")
            return

        try:
            with open("resources/audio.py/sounds.json", "r") as f:
                sound_data = ujson.load(f)
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


sound_manager = _SoundManager()"""
