import random

import pygame
import logging

import ujson

from scripts.game_structure.image_button import UIImageButton
from scripts.game_structure.game_essentials import game

logger = logging.getLogger(__name__)

menu_screens = ['settings screen', 'start screen', 'switch clan screen']
creation_screens = ['make clan screen']


class MusicManager():

    def __init__(self):
        self.playlists = {}
        self.current_playlist = []
        self.biome_playlist = []
        self.number_of_tracks = len(self.current_playlist)
        self.volume = game.settings["music_volume"] / 100
        self.muted = False
        self.current_track = None
        self.queued_track = None

        # loading playlists
        try:
            with open("resources/audio/music.json", "r") as f:
                music_data = ujson.load(f)
        except:
            logger.exception("Failed to load playlist index")
            return
        for playlist in music_data:
            try:
                self.playlists[playlist] = music_data[playlist]
            except:
                logger.exception("Failed to load playlist")

    def check_music(self, screen):
        """
        checks if playlist currently playing is appropriate for the given screen and changes the playlist if needed
        """
        if self.muted:
            return

        self.biome_playlist = self.get_biome_music()
        # print(f"biome playlist is {self.biome_playlist}, current playlist is {self.current_playlist}")
        # print(f"screen is {screen}")
        # print(f"menu playlist is {self.playlists['menu_playlist']}")

        # menu screen
        if screen in menu_screens and self.current_playlist != self.playlists["menu_playlist"]:
            # print("menu screen")
            if pygame.mixer.get_busy():
                pygame.mixer.music.stop()
            self.play_playlist(self.playlists["menu_playlist"])

        # clan creation screen
        elif screen in creation_screens and self.current_playlist != self.playlists["creation_playlist"]:
            # print("creation screen")
            if pygame.mixer.get_busy():
                pygame.mixer.music.stop()
            self.play_playlist(self.playlists["creation_playlist"])

        # other screens
        elif screen not in menu_screens and screen not in creation_screens and self.current_playlist != self.biome_playlist:
            # print("biome screen")
            self.fade_music()
            self.play_playlist(self.biome_playlist)

    def play_playlist(self, playlist):
        """
        loads and plays random file from playlist, queues up next track
        set loops to -1 to loop the chosen file
        setting loops to number above zero will play the track that number of times before playing the queued track
        """
        self.current_playlist = playlist

        if not self.current_playlist:  # don't play an empty playlist
            return

        self.number_of_tracks = len(self.current_playlist)
        if self.number_of_tracks == 1:
            self.play_music(random.choice(playlist), -1)
        else:
            self.play_music(random.choice(playlist))

        self.queued_track = None  # clear queue
        self.queue_music()

    def play_music(self, track, loops=0):
        """
        plays the given track and sets volume
        set loops to -1 to loop the chosen file
        setting loops to number above zero will play the track that number of times before playing the queued track
        """
        self.current_track = track
        pygame.mixer.music.load(self.current_track)
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(loops)
        # print(f"playing music:{self.current_track}")

    def queue_music(self):
        """
        queues up the next music track, this track is chosen randomly from self.current_playlist but WILL NOT be the
        current track
        """
        #  if playlist is empty or has a single track, don't attempt queueing
        if self.number_of_tracks < 2:
            print(f"playlist only has {self.number_of_tracks} tracks, cannot queue")
            return

        # otherwise we pick a new track and queue it
        if self.current_track:
            playlist_copy = self.current_playlist.copy()
            # print(f"playlist: {playlist_copy}, removing track: {self.current_track}")
            playlist_copy.remove(self.current_track)  # don't want to repeat current track, so we take it out
            options = playlist_copy
            # print(f"final list: {options}")
        else:
            options = self.current_playlist

        self.queued_track = random.choice(options)
        print(f"queueing music: current track is {self.current_track}, new track is {self.queued_track}")

    def play_queued(self):
        """
        Plays the currently queued track then queues the next track
        """
        if not self.queued_track:
            return

        self.play_music(self.queued_track)
        self.queue_music()

    def fade_music(self, fadeout=2000):
        """
        fades the music out, by default the fade is 2 seconds
        """
        if pygame.mixer.get_busy():
            pygame.mixer.music.fadeout(fadeout)

    def mute_music(self):
        """
        pauses current music track
        """
        self.muted = True
        pygame.mixer.music.pause()

    def unmute_music(self, screen):
        """
        unpauses current music track, then double checks if the track is appropriate for the screen before changing
        if necessary
        """
        self.muted = False
        pygame.mixer.music.unpause()
        self.check_music(screen)

    def change_volume(self, new_volume):
        """ changes the volume, int given should be between 0 and 100"""
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

    def get_biome_music(self):
        """
        Finds the clan's biome and returns the appropriate playlist
        """
        biome = game.clan.biome
        new_playlist = []

        if biome == 'Forest':
            new_playlist = self.playlists["forest_playlist"]
        elif biome == 'Plains':
            new_playlist = self.playlists["plains_playlist"]
        elif biome == 'Mountainous':
            new_playlist = self.playlists["beach_playlist"]
        elif biome == 'Beach':
            new_playlist = self.playlists["mountainous_playlist"]

        return new_playlist


music_manager = MusicManager()


class _SoundManager():

    def __init__(self):
        self.sounds = {}
        self.volume = game.settings["sound_volume"] / 100

        # open up the sound dictionary
        try:
            with open("resources/audio/sounds.json", "r") as f:
                sound_data = ujson.load(f)
        except:
            logger.exception("Failed to load sound index")
            return
        for sound in sound_data:

            try:
                self.sounds[sound] = []
                for path in sound_data[sound]:
                    self.sounds[sound].append(pygame.mixer.Sound("resources/audio/sounds/" +
                                                                 path))

                for each in self.sounds[sound]:
                    pygame.mixer.Sound.set_volume(each, self.volume)
            except:
                logger.exception("Failed to load sound")

    def play(self, sound=list, button=None):
        """ plays the given sound, if an ImageButton is passed through then the sound_id of the ImageButton will be
        used instead """
        if game.settings["audio_mute"]:
            return

        if button and button.__class__ == UIImageButton:
            try:
                if button.return_sound_id():
                    sound = button.return_sound_id()
            except AttributeError:
                logger.exception(f"That ui_element has no sound_id.")

        try:
            pygame.mixer.Sound.play(random.choice(self.sounds[sound]))
        except KeyError:
            logger.exception(f"Could not find sound {sound}")

    def change_volume(self, new_volume):
        """ changes the volume, int given should be between 0 and 100"""
        # make sure given volume is between 0 and 100
        if new_volume > 100:
            new_volume = 100
        if new_volume < 0:
            new_volume = 0

        # convert to a float and change volume accordingly
        self.volume = new_volume / 100
        game.settings["sound_volume"] = new_volume
        for sound in self.sounds:
            for each in self.sounds[sound]:
                pygame.mixer.Sound.set_volume(each, self.volume)


sound_manager = _SoundManager()
