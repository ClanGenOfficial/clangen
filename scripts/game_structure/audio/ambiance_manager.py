import logging
import random

import pygame
import ujson

from scripts.game_structure.audio.sound_manager import sound_manager
from scripts.game_structure.game_essentials import game
from scripts.screens.all_screens import main_menu_screens

logger = logging.getLogger(__name__)


class AmbianceManager:
    def __init__(self):

        self.current_playlist = []
        self.biome_playlist = []
        self.number_of_tracks = len(self.current_playlist)
        self.volume = game.settings["music_volume"] / 100
        self.muted = False
        self.audio_disabled = False
        self.current_track = None
        self.queued_track = None

        self.load_playlists()

    def load_playlists(self):
        self.playlists = {}
        # loading playlists
        try:
            with open("resources/audio/ambiance.json", "r", encoding="utf-8") as f:
                audio_data = ujson.load(f)
        except:
            logger.exception("Failed to load playlist index")
            return
        for playlist in audio_data:
            try:
                self.playlists[playlist] = []
                for path in audio_data[playlist]:
                    self.playlists[playlist].append(
                        "resources/audio/ambiance/" + path
                    )
            except:
                logger.exception("Failed to load playlist")

    def check_ambiance(self, screen):
        """
        checks if playlist currently playing is appropriate for the given screen and changes the playlist if needed
        """
        if self.muted or self.audio_disabled:
            return

        self.biome_playlist = self.get_world_ambiance()
        # print(f"biome playlist is {self.biome_playlist}, current playlist is {self.current_playlist}")
        # print(f"screen is {screen}")
        # print(f"menu playlist is {self.playlists['menu_playlist']}")

        # menu screen
        if (
                screen in main_menu_screens
                and self.current_playlist != self.playlists["menu_playlist"]
        ):
            # print("menu screen")
            self.fade_out_ambiance()
            self.play_playlist(self.playlists["menu_playlist"])

        # other screens
        elif (
                screen not in main_menu_screens
                and self.current_playlist != self.biome_playlist
        ):
            # print("biome screen")
            self.fade_out_ambiance()
            self.play_playlist(self.biome_playlist)

    def play_playlist(self, playlist):
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

        self.queue_music()

    def play_ambiance(self, track, loops=0, fade_ms=1000):
        """
        plays the given track and sets volume
        set loops to -1 to loop the chosen file
        setting loops to number above zero will play the track that number of times before playing the queued track
        """
        self.current_track = track
        pygame.mixer.music.load(self.current_track)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(loops, fade_ms=fade_ms)
        # print(f"playing music:{self.current_track}")

    def queue_music(self):
        """
        queues up the next music track, this track is chosen randomly from self.current_playlist but WILL NOT be the
        current track
        """
        # TODO: MOVE TO MUSIC MANAGER
        #  if playlist is empty or has a single track, don't attempt queueing
        if self.number_of_tracks == 0:
            return

        # otherwise we pick a new track and queue it
        if self.current_track in self.current_playlist and self.number_of_tracks > 1:
            playlist_copy = self.current_playlist.copy()
            # print(f"playlist: {playlist_copy}, removing track: {self.current_track}")
            playlist_copy.remove(
                self.current_track
            )  # don't want to repeat current track, so we take it out
            options = playlist_copy
            # print(f"final list: {options}")
        else:
            options = self.current_playlist

        try:
            self.queued_track = random.choice(options)
            print(
                f"queueing music: current track is {self.current_track}, new track is {self.queued_track}"
            )
        except IndexError:
            print("WARNING: playlist is empty")
            self.queued_track = None

    def play_queued(self):
        """
        Plays the currently queued track then queues the next track
        """
        # TODO: MOVE TO MUSIC MANAGER
        if not self.queued_track:
            return

        self.play_ambiance(self.queued_track, fade_ms=3000)
        self.queue_music()

    def fade_out_ambiance(self, fadeout=2000):
        """
        fades the music out, by default the fade is 2 seconds
        """
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.fadeout(fadeout)

    def mute_music(self):
        """
        pauses current music track
        """
        pygame.mixer.music.pause()

    def unmute_music(self, screen):
        """
        unpauses current music track, then double checks if the track is appropriate for the screen before changing
        if necessary
        """
        pygame.mixer.music.unpause()
        self.check_ambiance(screen)
        return True

    def change_volume(self, new_volume):
        """changes the volume, int given should be between 0 and 100"""
        # make sure given volume is between 0 and 100
        if new_volume > 100:
            new_volume = 100
        if new_volume < 0:
            new_volume = 0

        # convert to a float and change volume accordingly
        self.volume = new_volume / 100
        game.settings["music_volume"] = new_volume
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.volume)

    def get_world_ambiance(self):
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

        new_playlist = self.playlists["general_playlist"].copy()

        if biome == "Forest":
            new_playlist.extend(self.playlists["forest_playlist"])
        elif biome == "Plains":
            new_playlist.extend(self.playlists["plains_playlist"])
        elif biome == "Mountainous":
            new_playlist.extend(self.playlists["mountainous_playlist"])
        elif biome == "Beach":
            new_playlist.extend(self.playlists["beach_playlist"])

        new_playlist.extend(self.playlists.get(f"{season.lower().replace('-', '')}_playlist", []))

        return new_playlist


ambiance_manager = AmbianceManager()
