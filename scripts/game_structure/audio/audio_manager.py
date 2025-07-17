import pygame.mixer

from scripts.game_structure.audio.ambiance import Ambiance
from scripts.game_structure.audio.music import Music
from scripts.game_structure.audio.sound import Sound

"""
I need this to be capable of controlling all the audio aspects within the game.

- Control master mute
- Signal when background music plays
- Hold global fade functions
- Hold global pause functions
"""


class AudioManager:
    """
    This class allows control over audio as a whole.
    """

    def __init__(self):
        self.ambiance = Ambiance()
        self.sound = Sound()
        self.music = Music()
        self.audio_disabled = False
        self.muted = False

    def start_background_audio(self):
        """
        Begins background audio playback if necessary.
        """
        if not pygame.mixer.music.get_busy():
            self.ambiance.play_queued()

        if not self.music.get_busy() and not self.music.live:
            self.music.choose_music()
            self.music.play_music()

    def check_background_audio(self, screen):
        """
        Checks that background audio is appropriate for the given screen
        """
        self.music.check_music(screen)
        self.ambiance.check_ambiance(screen)

    def mute_audio(self):
        """
        Pauses background audio tracks and mutes sound effects
        """
        self.muted = True
        if not self.audio_disabled:
            self.ambiance.mute_ambiance()
            self.music.mute_music()
            self.sound.muted = True

    def unmute_audio(self, screen):
        """
        Unpauses background audio tracks and unmutes sound effects. This will also check if the current background
        tracks are appropriate for the current screen.
        """
        if self.audio_disabled:
            try:
                pygame.mixer.init()
                self.ambiance.load_playlists()
                self.sound.load_sounds()
                self.music.load_possible_tracks()
                self.audio_disabled = False
                self.muted = False
            except pygame.error:
                self.muted = True
                self.audio_disabled = True
        else:
            self.muted = False

        self.ambiance.unmute_ambiance(screen)
        self.music.unmute_music(screen)
        self.sound.muted = False


audio_manager = AudioManager()
