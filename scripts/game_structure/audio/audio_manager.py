import pygame.mixer

from scripts.game_structure.audio.sound_manager import sound_manager
from scripts.game_structure.audio.ambiance_manager import ambiance_manager
from scripts.game_structure.audio.music_manager import music_manager

"""
I need this to be capable of controlling all the audio aspects within the game.

- Control master mute
- Signal when background music plays
- Hold global fade functions
- Hold global pause functions
"""


class AudioManager:
    def __init__(self):
        self.audio_disabled = False
        self.muted = False

    def start_background_audio(self):
        if not pygame.mixer.music.get_busy():
            ambiance_manager.play_queued()

        if not music_manager.get_busy():
            music_manager.choose_music()
            music_manager.play_music()

    def mute_audio(self):
        """
        Pauses background audio tracks and mutes sound effects
        """
        self.muted = True
        if not self.audio_disabled:
            ambiance_manager.mute_ambiance()
            sound_manager.muted = True

    def unmute_audio(self, screen):
        """
        Unpauses background audio tracks and unmutes sound effects. This will also check if the current background
        tracks are appropriate for the current screen.
        """
        if self.audio_disabled:
            try:
                pygame.mixer.init()
                ambiance_manager.load_playlists()
                sound_manager.load_sounds()
                self.audio_disabled = False
                self.muted = False
            except pygame.error:
                self.muted = True
                self.audio_disabled = True
                return False
        else:
            self.muted = False

        ambiance_manager.unmute_ambiance(screen)
        sound_manager.muted = False

    def fade_out_audio(self, fadeout=2000):
        """
        Fades out all background audio
        """
        ambiance_manager.fade_out_ambiance(fadeout)


audio_manager = AudioManager()
