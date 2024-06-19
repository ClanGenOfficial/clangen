import pygame

from scripts.cat.sprites import sprites


class DeadClan:
    """
    The ClanGen afterlife!
    """

    forgotten_stages = {
        0: [0, 100],
        10: [101, 200],
        30: [201, 300],
        60: [301, 400],
        90: [401, 500],
        100: [501, 502],
    }  # Tells how faded the cat will be in StarClan by moons spent
    dead_cats = {}

    def __init__(self):
        """
        Initialise Starclan
        """
        self.instructor = None

    def fade(self, cat):
        """
        Handles the visual fading of cats in StarClan
        """
        white = pygame.Surface((sprites.size, sprites.size))
        fade_level = 0
        if cat.dead:
            for f in self.forgotten_stages:  # pylint: disable=consider-using-dict-items
                if cat.dead_for in range(
                        self.forgotten_stages[f][0], self.forgotten_stages[f][1]
                ):
                    fade_level = f
        white.fill((255, 255, 255, fade_level))
        return white
