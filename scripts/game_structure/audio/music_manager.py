from random import choice, randint
from threading import Timer

import ujson
import logging
import pygame

from scripts.game_structure.game_essentials import game

logger = logging.getLogger(__name__)


class MusicManager:
    def __init__(self):
        # live is used to denote that the music manager is working in some respect. Even if music is not currently
        # playing, the manager is stilled considered live as long as the silence timer is running.
        # essentially, the only time the manager shouldn't be live, is when the program first starts up.
        self.live = False

        self.music_timer = None
        self.silence_timer = None

        self.channel = None

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
        self.current_track_name = None

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
            playlist.extend(self.available_music.get("general_playlist"))

            try:
                biome = game.clan.biome
            except AttributeError:
                biome = "Forest"

            try:
                season = game.clan.current_season
            except AttributeError:
                season = "Newleaf"

            if self.available_music.get(f"{season.casefold().replace('-', '')}_playlist"):
                playlist.extend(self.available_music.get(f"{season.casefold().replace('-', '')}_playlist"))
            if self.available_music.get(f"{biome.casefold()}_playlist"):
                playlist.extend(self.available_music.get(f"{biome.casefold()}_playlist"))

        if not playlist:
            logger.error("Music track list is empty, check the music.json!")
            chosen_track = "resources/audio/music/Generations.mp3"  # making this default just in case
        elif len(playlist) == 1:
            chosen_track = playlist[0]
        else:
            if self.last_track_name in playlist:
                playlist.remove(self.last_track_name)
            chosen_track = choice(playlist)

        self.load_music(chosen_track)

    def check_music(self, screen):
        """
        checks if loaded music is appropriate for the given screen and stops playback if needed
        """
        if (
                screen in game.main_menu_screens
                and self.current_track_name not in self.available_music["menu_playlist"]
        ):
            self.fade_out_music()
            self.choose_music(screen)
            self.play_music()
        elif (
                screen not in game.main_menu_screens
                and self.current_track_name in self.available_music["menu_playlist"]
        ):
            self.fade_out_music()

    def play_music(self):
        """plays the loaded track"""
        self.live = True
        self.loaded_track.set_volume(self.volume)
        if not self.channel:
            self.channel = self.loaded_track.play()
        else:
            self.channel.play(self.loaded_track)
        self.start_music_timer()

    def mute_music(self):
        """
        pauses the playing track
        """
        self.channel.pause()
        if self.music_timer.is_alive():
            self.music_timer.cancel()
        elif self.silence_timer.is_alive():
            self.silence_timer.cancel()

    def unmute_music(self, screen):
        """
        unpauses the current music track
        :param screen: the screen that the player is currently viewing
        """
        self.check_music(screen)

        if self.loaded_track:
            self.channel.unpause()
            # a weird one here, we couldn't preserve the progress of the music timer
            # so instead, we start the silence timer and pray
            # the silence timer should always be longer than all possible music tracks, so this *should* be fine
            self.start_silence_timer()

    def fade_out_music(self, fadeout=2000):
        """
        fades the music out, default fade is 2 seconds
        """
        if self.channel.get_busy():
            self.channel.fadeout(fadeout)
            self.start_silence_timer()
            self.music_timer.cancel()

    def change_volume(self, new_volume):
        """
        changes the voume, int given should be between 0 and 100
        """
        if new_volume > 100:
            new_volume = 100
        elif new_volume < 0:
            new_volume = 0

        self.volume = new_volume / 100
        game.settings["music_volume"] = new_volume
        self.loaded_track.set_volume(self.volume)

    def start_music_timer(self):
        """
        sets a timer for the length of the track.  When the timer ends, silence timer is activated.
        """
        self.music_timer = Timer(self.loaded_track.get_length(), self.start_silence_timer)
        self.music_timer.daemon = True
        self.music_timer.start()

    def start_silence_timer(self):
        """
        Clears old music, then sets a timer for the next track to play.  When the timer ends, new music begins.
        """
        # waiting should already be true, but we'll just make certain
        self.del_music()
        self.silence_timer = Timer(randint(200, 400), self.reset_music)
        self.silence_timer.daemon = True
        self.silence_timer.start()

    def reset_music(self):
        self.choose_music(game.switches["cur_screen"])
        self.play_music()


music_manager = MusicManager()
