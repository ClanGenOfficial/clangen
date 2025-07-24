from random import choice
from threading import Timer

import ujson
import logging
import pygame

from scripts.game_structure import constants
from scripts.game_structure.audio.timer import AudioTimer
from scripts.game_structure.game.settings import game_setting_get, game_setting_set
from scripts.game_structure.game.switches import switch_get_value, Switch

logger = logging.getLogger(__name__)


class Music:
    def __init__(self):
        self.remaining_time_of_paused_track = None
        self.live = False

        self.music_timer = None
        self.silence_timer = None

        self.channel = None

        self.current_playlist = []
        self.current_track_name = None
        self.last_track_name = None

        self.loaded_track = None

        self.available_music: dict = {}

        self.volume = game_setting_get("music_volume") / 100

        self.load_possible_tracks()

    def get_busy(self) -> bool:
        """
        checks if music is currently playing
        """
        if not self.music_timer or not self.music_timer.is_alive():
            return False

        elif self.silence_timer and self.silence_timer.is_alive():
            return False

        return True

    def load_possible_tracks(self):
        """
        loads up the available_music dict
        """
        self.available_music = {}

        try:
            with open("resources/audio/music.json", "r", encoding="utf=8") as f:
                music_data = ujson.load(f)
        except:
            logger.exception("Failed to load music index")
            return

        for tracks in music_data:
            try:
                self.available_music[tracks] = []
                for path in music_data[tracks]:
                    self.available_music[tracks].append("resources/audio/music/" + path)
            except:
                logger.exception("Failed to load music lists")

    def load(self, track):
        """
        loads the given track into memory for playing
        """
        try:
            self.loaded_track = pygame.mixer.Sound(track)
            self.current_track_name = track
        except:
            logger.exception("Failed to load music")

    def _clear(self):
        """
        removes music from memory to avoid excessive memory use, this should be done before new music
        is loaded
        """
        self.last_track_name = self.current_track_name
        self.current_track_name = None

        del self.loaded_track

        self.loaded_track = None

    def choose(self):
        """
        chooses music from the appropriate playlists and sends it to be loaded
        """
        screen = switch_get_value(Switch.cur_screen)
        self.live = True
        self.current_playlist = []

        if screen in constants.MENU_SCREENS:
            self.current_playlist = self.available_music.get("menu_playlist")

            if not self.current_playlist:
                logger.error("Music track list is empty, check the music.json!")
                chosen_track = "resources/audio/music/Generations.mp3"  # making this default just in case
            elif len(self.current_playlist) == 1:
                chosen_track = self.current_playlist[0]
            else:
                if self.last_track_name in self.current_playlist:
                    self.current_playlist.remove(self.last_track_name)
                chosen_track = choice(self.current_playlist)
                print(chosen_track)

            self.load(chosen_track)

    def check(self):
        """
        checks if loaded music is appropriate for the given screen and stops playback if needed
        """
        screen = switch_get_value(Switch.cur_screen)
        # starts music when we return to main menu
        if (
            screen in constants.MENU_SCREENS
            and self.current_track_name not in self.current_playlist
        ):
            self.choose()
            self.play()

        # ends music when we leave main menu
        elif screen not in constants.MENU_SCREENS and self.channel:
            self.stop()

    def play(self):
        """plays the loaded track"""
        self.loaded_track.set_volume(self.volume)
        if not self.channel:
            self.channel = self.loaded_track.play(fade_ms=3000)
        else:
            self.channel.play(self.loaded_track, fade_ms=3000)
        self._start_music_timer()

    def stop(self):
        """
        Stops music entirely
        """
        self.channel.fadeout(3000)
        self.channel = None
        self._clear()
        self._stop_timers()

    def mute(self):
        """
        pauses the playing track
        """
        self.channel.pause()
        if self.music_timer.is_alive():
            self.remaining_time_of_paused_track = self.music_timer.remaining()
            self.music_timer.cancel()
        elif self.silence_timer and self.silence_timer.is_alive():
            self.silence_timer.cancel()

    def unmute(self):
        """
        unpauses the current music track
        """
        # this just acts a bit weird on consecutive mutes/unmutes, not sure why, but if players aren't spam clicking
        # the mute button it likely won't be noticeable
        self.check()

        if self.loaded_track:
            self.channel.unpause()
            # making sure all timers are cleared first
            self._stop_timers()
            self._start_music_timer(self.remaining_time_of_paused_track)

    def fade_out(self, fadeout: int = 2000):
        """
        Fades out the music
        :param fadeout: length of fadeout in milliseconds, by default this is 2 seconds
        """
        if self.channel and self.channel.get_busy():
            self.channel.fadeout(fadeout)
            self._start_silence_timer()
            self.music_timer.cancel()

    def change_volume(self, new_volume):
        """
        changes the volume
        :param new_volume: integer between 0 and 100
        """
        if new_volume > 100:
            new_volume = 100
        elif new_volume < 0:
            new_volume = 0

        self.volume = new_volume / 100
        game_setting_set("music_volume", new_volume)
        self.loaded_track.set_volume(self.volume)

    def _start_music_timer(self, duration=None):
        """
        sets a timer for the length of the track.  When the timer ends, silence timer is activated.
        """
        if not duration:
            duration = self.loaded_track.get_length()
        self.music_timer = AudioTimer(duration, self._start_silence_timer)
        self.music_timer.daemon = True
        self.music_timer.start()

    def _start_silence_timer(self, duration=2):
        """
        Clears old music, then sets a timer for the next track to play.  When the timer ends, new music begins.
        """
        # waiting should already be true, but we'll just make certain
        self._clear()
        self.silence_timer = AudioTimer(duration, self._reset)
        self.silence_timer.daemon = True
        self.silence_timer.start()

    def _stop_timers(self):
        """
        Stops any alive timer thread
        """
        if self.music_timer and self.music_timer.is_alive():
            self.music_timer.cancel()
        if self.silence_timer and self.silence_timer.is_alive():
            self.silence_timer.cancel()

    def _reset(self):
        self.choose()
        self.play()
