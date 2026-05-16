import pygame.mixer

from scripts.game_structure.audio.ambiance import Ambiance
from scripts.game_structure.audio.music import Music
from scripts.game_structure.audio.sound import Sound
from scripts.game_structure.game import game_setting_get


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
        if game_setting_get("audio_mute") == True and not self.muted:
            self.mute()

        if self.muted:
            return

        if not self.ambiance.get_busy():
            self.ambiance.check()
            self.ambiance.play_queued()

        if not self.music.get_busy():
            self.music.check()

    def check(self, should_fade_out: bool = False):
        """
        Checks that background audio is appropriate for the current screen
        :param should_fade_out: Set True if audio should fade out, if False, audio will stop abruptly
        """
        if self.muted:
            return

        self.music.check(should_fade_out)
        self.ambiance.check()

    def mute(self):
        """
        Pauses background audio tracks and mutes sound effects
        """
        self.muted = True
        if not self.disabled:
            self.ambiance.mute()
            self.music.mute()
            self.sound.muted = True

    def unmute(self):
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

        self.ambiance.unmute()
        self.music.unmute()
        self.sound.muted = False
