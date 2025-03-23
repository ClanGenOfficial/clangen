from random import choice

import ujson
import logging
import pygame

from scripts.game_structure.game_essentials import game

logger = logging.getLogger(__name__)

class MusicManager:
    def __init__(self):
        self.waiting = False
        self.channel_used = None

        self.current_track_name = None
        self.last_track_name = None

        self.loaded_track = None

        self.available_music: dict = {}

        self.volume = game.settings["music_volume"] / 100

        self.load_possible_tracks()

    def get_busy(self) -> bool:
        """
        checks if music is currently playing
        """
        if not self.channel_used and not self.waiting:
            return False

        if self.channel_used.get_busy():
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
                    self.available_music[tracks].append(
                        "resources/audio/music/" + path
                    )
            except:
                logger.exception("Failed to load music lists")

    def load_music(self, track):
        """
        loads the given track into memory for playing
        """
        try:
            self.loaded_track = pygame.mixer.Sound(track)
            self.current_track_name = track
        except:
            logger.exception("Failed to load music")

    def del_music(self):
        """
        removes music from memory to avoid excessive memory use, this should be done before new music
        is loaded
        """
        self.last_track_name = self.current_track_name

        del self.loaded_track

        self.loaded_track = None

    def choose_music(self, screen="start screen"):
        """
        chooses music from the appropriate playlists and sends it to be loaded
        """
        playlist = []

        if screen in game.main_menu_screens:
            playlist = self.available_music.get("menu_playlist")
        else:
            playlist.append(self.available_music.get("general_playlist"))
            playlist.append(self.available_music.get(f"{game.clan.current_season.caselock()}_playlist"))
            playlist.append(self.available_music.get(f"{game.clan.biome.caselock()}_playlist"))

        if not playlist:
            logger.error("Music track list is empty, check the music.json!")
            chosen_track = "resources/audio/music/Generations.mp3"  # making this default just in case
        elif len(playlist) == 1:
            chosen_track = playlist[0]
        else:
            playlist.remove(self.last_track_name)
            chosen_track = choice(playlist)

        self.load_music(chosen_track)

    def check_music(self, screen):
        """
        checks if loaded music is appropriate for the given screen and stops playback if needed
        """
        if screen in game.main_menu_screens and self.current_track_name not in self.available_music["menu_playlist"]:
            self.stop_music()
        elif screen not in game.main_menu_screens and self.current_track_name in self.available_music["menu_playlist"]:
            self.stop_music()

    def play_music(self):
        """plays the loaded track"""
        # .play returns used channel, so we grab that here
        self.channel_used = pygame.mixer.Sound.play(self.loaded_track)

    def stop_music(self):
        """
        stops and deletes currently loaded track
        """
        self.fade_out_music()
        self.del_music()

    def mute_music(self):
        """
        pauses the playing track
        """
        self.channel_used.pause()

    def unmute_music(self, screen):
        """
        unpauses the current music track
        :param screen: the screen that the player is currently viewing
        """
        self.check_music(screen)

        if self.loaded_track:
            self.channel_used.unpause()

    def fade_out_music(self, fadeout=2000):
        """
        fades the music out, default fade is 2 seconds
        """
        if self.channel_used.get_busy():
            self.channel_used.fadeout(fadeout)

    def set_timer(self):
        """
        sets a timer for the next track to play
        """
        pygame.time.set_timer(pygame.USEREVENT + 5, millis=300000)
        self.waiting = True


music_manager = MusicManager()
