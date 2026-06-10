import logging
import random
from typing import Optional

import pygame
import ujson

from scripts.game_structure import constants, game
from scripts.game_structure.audio.timer import AudioTimer
from scripts.game_structure.game.settings import game_setting_get, game_setting_set
from scripts.game_structure.game.switches import switch_get_value, Switch

logger = logging.getLogger(__name__)


class Ambiance:
    def __init__(self):
        self.camp_playing: Optional[str] = None
        """The camp that determined the current sounds"""
        self.season_playing: Optional[str] = None
        """The season that determined the current sounds"""
        self.season_sound: Optional[pygame.Sound] = None
        self.camp_sound: Optional[pygame.Sound] = None

        self.camp_timer: Optional[AudioTimer] = None
        self.season_timer: Optional[AudioTimer] = None
        self.camp_silence_timer: Optional[AudioTimer] = None
        self.season_silence_timer: Optional[AudioTimer] = None

        self.playlist_dict: dict = {}

        self.current_playlist: list = []

        self.biome_playlist: list = []
        self.season_overlay_playlist: list = []
        self.camp_overlay_playlist: list = []

        self.volume = game_setting_get("ambiance_volume") / 100
        self.number_of_tracks: int = len(self.current_playlist)
        self.current_track = None
        self.queued_track = None

        self.load_playlists()

    def load_playlists(self):
        """
        Loads the ambiance playlists
        """
        # loading playlists
        try:
            with open("resources/audio/ambiance.json", "r", encoding="utf-8") as f:
                self.playlist_dict = ujson.load(f)
        except ValueError:
            logger.exception("Failed to load ambiance data")
            return

        self.playlist_dict["menu_playlist"] = [
            "resources/audio/ambiance/" + track
            for track in self.playlist_dict["menu_playlist"]
        ]

    def check(self):
        """
        Checks if playlist currently playing is appropriate for the given screen and changes the playlist if needed
        """
        self._find_ambiance()
        screen = switch_get_value(Switch.cur_screen)
        # default to menu playlist
        playlist = self.playlist_dict["menu_playlist"]
        changed = False

        # menu screen
        if (
            screen in constants.MENU_SCREENS
            and self.current_playlist != self.playlist_dict["menu_playlist"]
        ):
            playlist = self.playlist_dict["menu_playlist"]
            self.stop_overlay()
            changed = True

        # other screens
        elif (
            screen not in constants.MENU_SCREENS
            and self.current_playlist != self.biome_playlist
        ):
            playlist = self.biome_playlist
            changed = True
            self.start_overlay()

        if changed:
            self.ready_playlist(playlist)
            self.fade_out()

    def ready_playlist(self, playlist: list):
        """
        loads and plays random file from playlist, queues up next track
        :param playlist: List of track filepaths to choose from. This will become the self.current_playlist and queuing process will begin.
        """
        self.current_playlist = playlist
        self.queued_track = None  # clear queue

        if not self.current_playlist:  # don't play an empty playlist
            return

        self.number_of_tracks = len(self.current_playlist)

        self.set_queued()

    def start_overlay(self):
        """
        Starts randomized countdowns and begins playing the overlays at the end of the countdown.
        """
        if self.camp_overlay_playlist:
            self._start_camp_overlay_silence_timer()
        if self.season_overlay_playlist:
            self._start_season_overlay_silence_timer()

    def stop_overlay(self, should_fade_out: bool = True):
        """
        Stops any overlay sounds from playing
        :param should_fade_out: set True if playing sounds should fade, False if they should stop immediately
        """
        fade_ms = 300 if should_fade_out else 0
        if self.camp_timer and self.camp_timer.is_alive():
            self.camp_sound.fadeout(fade_ms)
            self.camp_timer.cancel()
        elif self.camp_silence_timer:
            self.camp_silence_timer.cancel()
        if self.season_timer and self.season_timer.is_alive():
            self.season_sound.fadeout(fade_ms)
            self.season_timer.cancel()
        elif self.camp_silence_timer:
            self.season_silence_timer.cancel()

    def play(self, track, fade_ms=1000):
        """
        plays the given track and sets volume
        :param track: The filepath for the track to play
        :param fade_ms: Fade-in time in milliseconds
        """
        self.current_track = track
        pygame.mixer.music.load(self.current_track)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(fade_ms=fade_ms)

    def set_queued(self):
        """
        queues up the next ambiance track, this track is chosen randomly from self.current_playlist but WILL NOT be the
        current track
        """
        # if playlist is empty or has a single track, don't attempt queueing
        if self.number_of_tracks == 0:
            return

        # otherwise we pick a new track and queue it
        if self.current_track in self.current_playlist and self.number_of_tracks > 1:
            playlist_copy = self.current_playlist.copy()
            playlist_copy.remove(
                self.current_track
            )  # don't want to repeat current track, so we take it out
            options = playlist_copy
        else:
            options = self.current_playlist

        try:
            self.queued_track = random.choice(options)

        except IndexError:
            logger.warning("Playlist is empty")
            self.queued_track = None

    def play_queued(self):
        """
        Plays the currently queued track then queues the next track
        """
        if not self.queued_track:
            return

        self.play(self.queued_track, fade_ms=3000)
        self.set_queued()

    @staticmethod
    def fade_out(fade_ms=2000):
        """
        fades the ambiance out, by default the fade is 2 seconds
        :param fade_ms: Fade-out time in milliseconds
        """
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fade_ms)

    def mute(self):
        """
        pauses current ambiance track
        """
        pygame.mixer.music.pause()
        self.stop_overlay(should_fade_out=False)

    def unmute(self):
        """
        unpauses current ambiance track, then double checks if the track is appropriate for the screen before changing
        if necessary
        """
        pygame.mixer.music.unpause()
        self.check()

    def change_volume(self, new_volume: int):
        """
        changes the volume of the ambiance
        :param new_volume: New volume to change to, int given should be between 0 and 100
        """
        # make sure given volume is between 0 and 100
        if new_volume > 100:
            new_volume = 100
        if new_volume < 0:
            new_volume = 0

        # convert to a float and change volume accordingly
        self.volume = new_volume / 100
        game_setting_set("ambiance_volume", new_volume)
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.volume)
        if self.season_sound:
            self.season_sound.set_volume(self.overlay_volume)
        if self.camp_sound:
            self.camp_sound.set_volume(self.overlay_volume)

    def _find_ambiance(self):
        """
        Finds the clan's biome and returns the appropriate playlist
        """
        try:
            biome = game.clan.biome
        except AttributeError:
            biome = "Forest"

        try:
            camp: str = game.clan.camp_bg
            index = int([x for x in camp if x.isdigit()][0]) - 1
            camp = constants.CAMPS[biome][index]
        except AttributeError:
            camp = constants.CAMPS[biome][0]

        try:
            season = game.clan.current_season
        except AttributeError:
            season = "Newleaf"

        self.biome_playlist = [
            "resources/audio/ambiance/" + track
            for track in self.playlist_dict[biome.casefold()]["base"]
        ]

        # find if we have any camp specific sounds
        if not self.camp_overlay_playlist or camp != self.camp_playing:
            self.camp_playing = camp
            camp_name = camp.casefold().replace(" ", "_")
            if self.playlist_dict[f"{biome.casefold()}"].get(camp_name):
                for path in self.playlist_dict[biome.casefold()][camp_name]:
                    self.camp_overlay_playlist.append(
                        pygame.mixer.Sound(f"resources/audio/ambiance/" + path)
                    )

                for each in self.camp_overlay_playlist:
                    each.set_volume(self.volume)

        # then grab season specific sounds
        if not self.season_overlay_playlist or season != self.season_playing:
            self.season_playing = season
            self.season_overlay_playlist = []
            for path in self.playlist_dict["seasonal"][f"{season.casefold()}"]:
                self.season_overlay_playlist.append(
                    pygame.mixer.Sound("resources/audio/ambiance/" + path)
                )

    @staticmethod
    def get_busy() -> bool:
        """
        Check if ambiance is playing.
        """
        return pygame.mixer.music.get_busy()

    @property
    def overlay_volume(self):
        """
        Handles the volume for the ambiance overlay (not the base ambiance, but the short sounds relating to season/camp which we play intermittently). This just allows us to fine-tune the volume relationship between the two types of ambiance. This volume will still be affected by the overall ambiance volume assigned by the player.
        """
        return int((self.volume * 100) / 2.5) / 100

    def _start_season_overlay_timer(self, duration):
        """
        Starts a timer thread for the given duration. When the thread finishes, the silence timer will begin.
        :param duration: This should be the duration of the currently playing season overlay sound
        """
        if self.season_timer and self.season_timer.is_alive():
            return
        self.season_timer = AudioTimer(
            duration, self._start_season_overlay_silence_timer
        )
        self.season_timer.daemon = True
        self.season_timer.start()

    def _start_season_overlay_silence_timer(self):
        """
        Starts a timer thread for a random amount of silence. When thread finishes, a new season overlay sound will play.
        """
        if self.season_silence_timer and self.season_silence_timer.is_alive():
            return
        self.season_silence_timer = AudioTimer(
            random.randint(20, 50), self.play_season_overlay
        )
        self.season_silence_timer.daemon = True
        self.season_silence_timer.start()

    def play_season_overlay(self):
        """
        Plays the season overlay and begins its timer.
        """
        self.season_sound = random.choice(self.season_overlay_playlist)
        self.season_sound.set_volume(self.overlay_volume)
        if pygame.mixer.find_channel():
            logger.info("played season overlay")
            self.season_sound.play(fade_ms=4000)
            self._start_season_overlay_timer(self.season_sound.get_length())
        # TODO: what happens if no channel found?

    def _start_camp_overlay_timer(self, duration):
        """
        Starts a timer thread for the given duration. When the thread finishes, the silence timer will begin.
        :param duration: This should be the duration of the currently playing season overlay sound
        """
        if self.camp_timer and self.camp_timer.is_alive():
            return
        self.camp_timer = AudioTimer(duration, self._start_camp_overlay_silence_timer)
        self.camp_timer.daemon = True
        self.camp_timer.start()

    def _start_camp_overlay_silence_timer(self):
        """
        Starts a timer thread for a random amount of silence. When thread finishes, a new season overlay sound will play.
        """
        if self.camp_silence_timer and self.camp_silence_timer.is_alive():
            return
        self.camp_silence_timer = AudioTimer(
            random.randint(20, 50), self.play_camp_overlay
        )
        self.camp_silence_timer.daemon = True
        self.camp_silence_timer.start()

    def play_camp_overlay(self):
        """
        Plays the camp overlay and begins its timer.
        """
        self.camp_sound = random.choice(self.camp_overlay_playlist)
        self.camp_sound.set_volume(self.overlay_volume)
        if pygame.mixer.find_channel():
            logger.info("played camp overlay")
            self.camp_sound.play(fade_ms=4000)
            self._start_camp_overlay_timer(self.camp_sound.get_length())

        # TODO: what happens if no channel found?
