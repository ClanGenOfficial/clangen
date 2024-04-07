import pygame

from scripts.game_structure.game_essentials import game

menu_screens = ['settings screen', 'start screen', 'switch clan screen', 'make clan screen']

menu_music = "resources/audio/music/Generations.ogg"
forest_music = []
plains_music = []
beach_music = []
mountain_music = []


class Audio():

    def __init__(self, current_music=None, playlist=None):
        self.current_music = current_music
        self.playlist = playlist

    def check_music(self, screen):
        """
        checks if music currently playing is appropriate for the given screen and changes the music if needed
        """
        # this should only occur when the game has just opened
        if not self.current_music and screen == 'start screen':
            self.play_music(menu_music, -1)
        # otherwise we're checking is the screen is or isn't the menu and changing music accordingly
        elif screen in menu_screens:
            if not self.current_music == menu_music:
                self.fade_music()
                # self.play_music(self.get_biome_music)
            elif not pygame.mixer.music.get_busy():
                self.play_music(menu_music, -1)
        elif screen not in menu_screens:
            if self.current_music == menu_music:
                self.fade_music()
                # self.play_music(self.get_biome_music)
            elif not pygame.mixer.music.get_busy():
                self.play_music(menu_music, -1)

    def play_music(self, music, loops=0):
        """
        loads and plays given music file, sets self.current_music to given music file
        """
        self.current_music = music
        pygame.mixer.music.load(music)
        pygame.mixer.music.play(loops)

    def fade_music(self, fadeout=2000):
        """
        fades the music out, by default the fade is 2 seconds
        """
        pygame.mixer.music.fadeout(fadeout)

    def get_biome_music(self):
        """
        use this to find the starting biome music and biome
        not currently used as we have no biome music, but this should work when we do
        """
        if game.clan.biome == 'Forest':
            self.playlist = forest_music
            return forest_music[0]
        elif game.clan.biome == 'Plains':
            self.playlist = plains_music
            return plains_music[0]
        elif game.clan.biome == 'Mountainous':
            self.playlist = mountain_music
            return mountain_music[0]
        elif game.clan.biome == 'Beach':
            self.playlist = beach_music
            return beach_music[0]

    def queue_biome_music(self):
        """
        use this to start a queue of biome music after loading the first biome music file
        leaving this be for now until we actually have a playlist to experiment with
        """
        # pygame.mixer.music.queue()



audio = Audio()
