from random import choice, randint
from threading import Timer

import ujson
import logging
import pygame

from scripts.game_structure import constants, game
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
        if self.music_timer or self.silence_timer:
            return True
        return False

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
        self.find_playlist()

        if not self.current_playlist:
            raise Exception("Music track list is empty, check the music.json!")
        elif len(self.current_playlist) == 1:
            chosen_track = self.current_playlist[0]
        else:
            possible_tracks = self.current_playlist.copy()
            if self.last_track_name in self.current_playlist:
                possible_tracks.remove(self.last_track_name)
            chosen_track = choice(possible_tracks)

        self.loaded_track = pygame.mixer.Sound(chosen_track)
        self.current_track_name = chosen_track
        print(chosen_track)

    def find_playlist(self):
        """
        Sets `self.current_playlist` to an appropriate playlist for the season and biome.
        """
        screen = switch_get_value(Switch.cur_screen)
        self.current_playlist = []
        if screen in constants.MENU_SCREENS:
            self.current_playlist = self.available_music.get("menu_playlist")
        else:
            self.current_playlist.extend(self.available_music.get("general_playlist"))

            try:
                biome = game.clan.biome
            except AttributeError:
                biome = "Forest"

            try:
                season = game.clan.current_season
            except AttributeError:
                season = "Newleaf"

            if self.available_music.get(
                f"{season.casefold().replace('-', '')}_playlist"
            ):
                self.current_playlist.extend(
                    self.available_music.get(
                        f"{season.casefold().replace('-', '')}_playlist"
                    )
                )
            if self.available_music.get(f"{biome.casefold()}_playlist"):
                self.current_playlist.extend(
                    self.available_music.get(f"{biome.casefold()}_playlist")
                )

    def check(self, should_fade_out: bool = False):
        """
        checks if loaded music is appropriate for the given screen and stops playback if needed
        :param should_fade_out: Set True if music should fade out, if False, music will stop abruptly
        """
        screen = switch_get_value(Switch.cur_screen)
        # updates our current playlist
        self.find_playlist()

        # sees if the currently playing track is part of our current playlist, and changes it if not!
        if (
            screen in constants.MENU_SCREENS
            and self.current_track_name not in self.available_music["menu_playlist"]
        ):
            # switching music
            if self.current_track_name:
                self.fade_out(fadeout=3000)
                switch_timer = Timer(3, self.play)
                switch_timer.daemon = True
                switch_timer.start()
            else:
                # if no track was loaded, then we just play
                self.play()
        elif (
            screen not in constants.MENU_SCREENS
            and self.current_track_name
            and self.current_track_name not in self.current_playlist
        ):
            # stopping music
            self._stop_timers()
            if should_fade_out:
                self.fade_out()
            else:
                self.fade_out(fadeout=0)
            self.current_track_name = None

    def play(self):
        """Finds and plays appropriate track"""
        self.choose()
        self.loaded_track.set_volume(self.volume)
        if not self.channel:
            self.channel = self.loaded_track.play(fade_ms=3000)
        else:
            self.channel.play(self.loaded_track, fade_ms=3000)
        self._start_music_timer()
        if self.silence_timer:
            self.silence_timer.cancel()

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
        if not self.channel:
            return
        self.channel.pause()
        if self.music_timer.is_alive():
            self.remaining_time_of_paused_track = self.music_timer.remaining
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

    def fade_out(self, fadeout=2000, delay=None):
        """
        fades the music out and begins the silence timer to count down to next track play
        :param fadeout: length of fadeout in milliseconds
        :param delay: Dictates the seconds of silence between this track and the next one, including fade time. Default is random duration between 30 and 300 seconds.
        """
        if not delay:
            delay = randint(30, 250)
        if self.channel and self.channel.get_busy():
            self.channel.fadeout(fadeout)
            self._start_silence_timer(max(fadeout / 100, delay))
            self.music_timer.cancel()

    def change_volume(self, new_volume: int):
        """
        changes the volume
        :param new_volume: The new volume to set music to, int given should be between 0 and 100
        """
        if new_volume > 100:
            new_volume = 100
        elif new_volume < 0:
            new_volume = 0

        self.volume = new_volume / 100
        game_setting_set("music_volume", new_volume)
        if self.loaded_track:
            self.loaded_track.set_volume(self.volume)

    def _start_music_timer(self, duration=None):
        """
        sets a timer for the length of the track.  When the timer ends, silence timer is activated.
        :param duration: The duration, in seconds, that the music timer will count down. By default, this will be the length of the track.
        """
        if self.music_timer and self.music_timer.is_alive():
            return
        if not duration:
            duration = self.loaded_track.get_length()
        self.music_timer = AudioTimer(duration, self._start_silence_timer)
        self.music_timer.daemon = True
        self.music_timer.start()

    def _start_silence_timer(self, duration=None):
        """
        Clears old music, then sets a timer for the next track to play.  When the timer ends, new music begins.
        :param duration: length of silence in seconds, by default this is a random duration between 30 and 300 seconds
        """
        if self.silence_timer and self.silence_timer.is_alive():
            return

        if not duration:
            duration = randint(30, 250)
        self._clear()
        self.silence_timer = AudioTimer(duration, self.play)
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
