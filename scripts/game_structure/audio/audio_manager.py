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
    """
    This class allows control over audio as a whole.
    """

    def __init__(self):
        self.audio_disabled = False
        self.muted = False

    @staticmethod
    def start_background_audio():
        """
        Begins background audio playback if necessary.
        """
        if not pygame.mixer.music.get_busy():
            ambiance_manager.play_queued()

        if not music_manager.get_busy() and not music_manager.live:
            music_manager.choose_music()
            music_manager.play_music()

    @staticmethod
    def check_background_audio(screen):
        """
        Checks that background audio is appropriate for the given screen
        """
        music_manager.check_music(screen)
        ambiance_manager.check_ambiance(screen)

    def mute_audio(self):
        """
        Pauses background audio tracks and mutes sound effects
        """
        self.muted = True
        if not self.audio_disabled:
            ambiance_manager.mute_ambiance()
            music_manager.mute_music()
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
                music_manager.load_possible_tracks()
                self.audio_disabled = False
                self.muted = False
            except pygame.error:
                self.muted = True
                self.audio_disabled = True
        else:
            self.muted = False

        ambiance_manager.unmute_ambiance(screen)
        music_manager.unmute_music(screen)
        sound_manager.muted = False


audio_manager = AudioManager()
