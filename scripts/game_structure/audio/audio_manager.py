import pygame.mixer

from scripts.game_structure.audio.ambiance import Ambiance
from scripts.game_structure.audio.music import Music
from scripts.game_structure.audio.sound import Sound


class AudioManager:
    """
    This class allows control over audio as a whole.
    """

    def __init__(self):
        self.ambiance = Ambiance()
        self.sound = Sound()
        self.music = Music()
        self.disabled = False
        self.muted = False

    def start(self):
        """
        Begins background audio playback if necessary.
        """
        if not pygame.mixer.music.get_busy():
            self.ambiance.play_queued()

        if not self.music.get_busy() and not self.music.live:
            self.music.choose_music()
            self.music.play_music()

    def check(self, screen):
        """
        Checks that background audio is appropriate for the given screen
        """
        self.music.check_music(screen)
        self.ambiance.check_ambiance(screen)

    def mute(self):
        """
        Pauses background audio tracks and mutes sound effects
        """
        self.muted = True
        if not self.disabled:
            self.ambiance.mute_ambiance()
            self.music.mute_music()
            self.sound.muted = True

    def unmute(self, screen):
        """
        Unpauses background audio tracks and unmutes sound effects. This will also check if the current background
        tracks are appropriate for the current screen.
        """
        if self.disabled:
            try:
                pygame.mixer.init()
                self.ambiance.load_playlists()
                self.sound.load_sounds()
                self.music.load_possible_tracks()
                self.disabled = False
                self.muted = False
            except pygame.error:
                self.muted = True
                self.disabled = True
        else:
            self.muted = False

        self.ambiance.unmute_ambiance(screen)
        self.music.unmute_music(screen)
        self.sound.muted = False
