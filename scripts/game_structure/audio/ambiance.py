import logging
import random

import pygame
import ujson

from scripts.game_structure import constants
from scripts.game_structure.game.settings import game_setting_get, game_setting_set
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure.game_essentials import game

logger = logging.getLogger(__name__)


class Ambiance:
    def __init__(self):
        self.playlist_dict = {}
        self.current_playlist = []
        self.biome_playlist = []
        self.number_of_tracks = len(self.current_playlist)
        self.volume = game_setting_get("ambiance_volume") / 100
        self.current_track = None
        self.queued_track = None

        self.load_playlists()

    def load_playlists(self):
        # loading playlists
        try:
            with open("resources/audio/ambiance.json", "r", encoding="utf-8") as f:
                audio_data = ujson.load(f)
        except:
            logger.exception("Failed to load ambiance data")
            return

        for playlist in audio_data:
            try:
                self.playlist_dict[playlist] = []
                for path in audio_data[playlist]:
                    self.playlist_dict[playlist].append(
                        "resources/audio/ambiance/" + path
                    )
            except:
                logger.exception("Failed to load ambiance playlist")

    def check(self):
        """
        checks if playlist currently playing is appropriate for the given screen and changes the playlist if needed
        """
        screen = switch_get_value(Switch.cur_screen)

        # menu screen
        if screen in constants.MENU_SCREENS:
            if self.current_playlist != self.playlist_dict["menu_playlist"]:
                self.ready_playlist(self.playlist_dict["menu_playlist"])
            self.play_queued()

        # other screens
        elif screen not in constants.MENU_SCREENS and self.get_busy():
            self.current_playlist = None
            self.fade_out()

    def ready_playlist(self, playlist):
        """
        loads and plays random file from playlist, queues up next track
        set loops to -1 to loop the chosen file
        setting loops to number above zero will play the track that number of times before playing the queued track
        """
        self.current_playlist = playlist
        self.queued_track = None  # clear queue

        if not self.current_playlist:  # don't play an empty playlist
            return

        self.number_of_tracks = len(self.current_playlist)

        self.set_queued()

    def play(self, track, loops=0, fade_ms=1000):
        """
        plays the given track and sets volume
        set loops to -1 to loop the chosen file
        setting loops to number above zero will play the track that number of times before playing the queued track
        """
        self.current_track = track
        pygame.mixer.music.load(self.current_track)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(loops, fade_ms=fade_ms)

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
            print("WARNING: playlist is empty")
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
    def fade_out(fadeout=2000):
        """
        fades the ambiance out, by default the fade is 2 seconds
        """
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fadeout)

    @staticmethod
    def mute():
        """
        pauses current ambiance track
        """
        pygame.mixer.music.pause()

    def unmute(self):
        """
        unpauses current ambiance track, then double checks if the track is appropriate for the screen before changing
        if necessary
        """
        pygame.mixer.music.unpause()
        self.check()

    def change_volume(self, new_volume):
        """changes the volume, int given should be between 0 and 100"""
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

    def get_world_ambiance(self) -> list:
        """
        Finds the clan's biome and returns the appropriate playlist
        """
        try:
            biome = game.clan.biome
        except AttributeError:
            biome = "Forest"

        try:
            season = game.clan.current_season
        except AttributeError:
            season = "Newleaf"

        new_playlist = self.playlist_dict["general_playlist"].copy()
        new_playlist.extend(self.playlist_dict[f"{biome.casefold()}_playlist"])

        new_playlist.extend(
            self.playlist_dict.get(f"{season.lower().replace('-', '')}_playlist", [])
        )

        return new_playlist

    @staticmethod
    def get_busy() -> bool:
        return pygame.mixer.music.get_busy()
