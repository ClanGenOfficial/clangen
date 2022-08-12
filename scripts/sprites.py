import pygame
from .game_essentials import *

class Sprites(object):
    def __init__(self, original_size, new_size=None):
        self.size = original_size  # size of a single sprite in a spritesheet
        if new_size is None:
            self.new_size = self.size * 2
        else:
            self.new_size = new_size  # size that the sprites will be transformed to
        self.spritesheets = {}
        self.images = {}
        self.groups = {}
        self.sprites = {}

    def spritesheet(self, a_file, name):
        self.spritesheets[name] = pygame.image.load(a_file)

    def image(self, a_file, name):
        self.images[name] = pygame.image.load(a_file)

    def find_sprite(self, group_name, x, y):
        # find singular sprite from group
        # pixels will be calculated automatically, so for x and y, just use 0, 1, 2, 3 etc.
        new_sprite = pygame.Surface((self.size, self.size), pygame.HWSURFACE | pygame.SRCALPHA)
        new_sprite.blit(self.groups[group_name], (0, 0),
                        (x * self.size, y * self.size, (x + 1) * self.size, (y + 1) * self.size))
        return new_sprite

    def make_group(self, spritesheet, pos, name, sprites_x=3, sprites_y=3):  # pos = ex. (2, 3), no single pixels
        # divide sprites on a sprite-sheet into groups of sprites that are easily accessible

        # making the group
        new_group = pygame.Surface((self.size * sprites_x, self.size * sprites_y), pygame.HWSURFACE | pygame.SRCALPHA)
        new_group.blit(self.spritesheets[spritesheet], (0, 0),
                       (pos[0] * sprites_x * self.size, pos[1] * sprites_y * self.size,
                        (pos[0] + sprites_x) * self.size, (pos[1] + sprites_y) * self.size))
        self.groups[name] = new_group

        # splitting group into singular sprites and storing into self.sprites section
        x_spr = 0
        y_spr = 0
        for x in range(sprites_x * sprites_y):
            new_sprite = pygame.Surface((self.size, self.size), pygame.HWSURFACE | pygame.SRCALPHA)
            new_sprite.blit(new_group, (0, 0), (x_spr * self.size, y_spr * self.size,
                                                (x_spr + 1) * self.size, (y_spr + 1) * self.size))
            self.sprites[name + str(x)] = new_sprite
            x_spr += 1
            if x_spr == sprites_x:
                x_spr = 0
                y_spr += 1

    def load_scars(self):
        # SCARS & MORE
        scars = 'scars'

        self.make_group(scars, (0, 0), 'scarsONE')
        self.make_group(scars, (1, 0), 'scarsTWO')
        self.make_group(scars, (2, 0), 'scarsTHREE')
        self.make_group(scars, (3, 0), 'scarsLEFTEAR')
        self.make_group(scars, (4, 0), 'scarsRIGHTEAR')
        self.make_group(scars, (5, 0), 'scarsNOTAIL')

        self.make_group(scars + 'extra', (0, 0), 'scarsextraONE', sprites_y=2)
        self.make_group(scars + 'extra', (1, 0), 'scarsextraTWO', sprites_y=2)
        self.make_group(scars + 'extra', (2, 0), 'scarsextraTHREE', sprites_y=2)
        self.make_group(scars + 'extra', (3, 0), 'scarsextraLEFTEAR', sprites_y=2)
        self.make_group(scars + 'extra', (4, 0), 'scarsextraRIGHTEAR', sprites_y=2)
        self.make_group(scars + 'extra', (5, 0), 'scarsextraNOTAIL', sprites_y=2)

        a = 0
        for i in ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"]:
            sprites.make_group('collars', (a, 0), 'scars' + i)
            sprites.make_group('collarsextra', (a, 0), 'scarsextra' + i, sprites_y=2)
            a += 1

        a = 0
        for i in ["GREEN", "RAINBOW", "BLACK", "SPIKES"]:
            sprites.make_group('collars', (a, 1), 'scars' + i)
            sprites.make_group('collarsextra', (a, 1), 'scarsextra' + i, sprites_y=2)
            a += 1

        a = 0
        for i in ["PINK", "PURPLE", "MULTI"]:
            sprites.make_group('collars', (a, 2), 'scars' + i)
            sprites.make_group('collarsextra', (a, 2), 'scarsextra' + i, sprites_y=2)
            a += 1

        a = 0
        for i in ["CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL", "LIMEBELL"]:
            sprites.make_group('bellcollars', (a, 0), 'scars' + i)
            sprites.make_group('bellcollarsextra', (a, 0), 'scarsextra' + i, sprites_y=2)
            a += 1

        a = 0
        for i in ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL"]:
            sprites.make_group('bellcollars', (a, 1), 'scars' + i)
            sprites.make_group('bellcollarsextra', (a, 1), 'scarsextra' + i, sprites_y=2)
            a += 1

        a = 0
        for i in ["PINKBELL", "PURPLEBELL", "MULTIBELL"]:
            sprites.make_group('bellcollars', (a, 2), 'scars' + i)
            sprites.make_group('bellcollarsextra', (a, 2), 'scarsextra' + i, sprites_y=2)
            a += 1

        a = 0
        for i in ["CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW", "LIMEBOW"]:
            sprites.make_group('bowcollars', (a, 0), 'scars' + i)
            sprites.make_group('bowcollarsextra', (a, 0), 'scarsextra' + i, sprites_y=2)
            a += 1

        a = 0
        for i in ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW"]:
            sprites.make_group('bowcollars', (a, 1), 'scars' + i)
            sprites.make_group('bowcollarsextra', (a, 1), 'scarsextra' + i, sprites_y=2)
            a += 1

        a = 0
        for i in ["PINKBOW", "PURPLEBOW", "MULTIBOW"]:
            sprites.make_group('bowcollars', (a, 2), 'scars' + i)
            sprites.make_group('bowcollarsextra', (a, 2), 'scarsextra' + i, sprites_y=2)
            a += 1

sprites = Sprites(50)
for x in ['lineart', 'singlecolours', 'speckledcolours', 'tabbycolours', 'whitepatches', 'tortiecolours', 'eyes',
          'singleextra', 'tabbyextra', 'speckledextra', 'whiteextra', 'eyesextra', 'tortiesextra',
          'skin', 'skinextra', 'scars', 'scarsextra', 'whitenewextra', 'whitepatchesnew', 'scarsdark', 'scarsdarkextra',
          'collars', 'collarsextra', 'bellcollars', 'bellcollarsextra', 'bowcollars', 'bowcollarsextra']:
    sprites.spritesheet("sprites/" + x + ".png", x)

# Line art
sprites.make_group('lineart', (0, 0), 'lines', sprites_y=5)

# Eyes
a = 0
for i in ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE']:
    sprites.make_group('eyes', (a, 0), 'eyes' + i)
    sprites.make_group('eyesextra', (a, 0), 'eyesextra' + i, sprites_y=2)
    a += 1

sprites.make_group('eyes', (0, 1), 'eyesDARKBLUE')
sprites.make_group('eyes', (1, 1), 'eyesBLUEYELLOW')
sprites.make_group('eyes', (2, 1), 'eyesBLUEGREEN')

sprites.make_group('eyesextra', (0, 1), 'eyesextraDARKBLUE', sprites_y=2)
sprites.make_group('eyesextra', (1, 1), 'eyesextraBLUEYELLOW', sprites_y=2)
sprites.make_group('eyesextra', (2, 1), 'eyesextraBLUEGREEN', sprites_y=2)

# WHITE patches
a = 1
for i in ['ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN', 'ANY2']:
    sprites.make_group('whitepatches', (a, 0), 'white' + i)
    sprites.make_group('whiteextra', (a, 0), 'whiteextra' + i, sprites_y=2)
    a += 1

# MORE white patches
a = 0
for i in ['ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO']:
    sprites.make_group('whitepatchesnew', (a, 0), 'white' + i)
    sprites.make_group('whitenewextra', (a, 0), 'whiteextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY', 'VANCREAMY', 'ANY2CREAMY']:
    sprites.make_group('whitepatches', (a, 1), 'white' + i)
    sprites.make_group('whiteextra', (a, 1), 'whiteextra' + i, sprites_y=2)
    a += 1
# extra
sprites.make_group('whitepatches', (0, 2), 'whiteEXTRA')
sprites.make_group('whiteextra', (0, 2), 'whiteextraEXTRA', sprites_y=2)

# SINGLE colours
a = 0
for i in ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']:
    sprites.make_group('singlecolours', (a, 0), 'single' + i)
    sprites.make_group('singleextra', (a, 0), 'singleextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']:
    sprites.make_group('singlecolours', (a, 1), 'single' + i)
    sprites.make_group('singleextra', (a, 1), 'singleextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['LIGHTBROWN', 'BROWN', 'DARKBROWN']:
    sprites.make_group('singlecolours', (a, 2), 'single' + i)
    sprites.make_group('singleextra', (a, 2), 'singleextra' + i, sprites_y=2)
    a += 1

# TABBY colours
a = 0
for i in ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']:
    sprites.make_group('tabbycolours', (a, 0), 'tabby' + i)
    sprites.make_group('tabbyextra', (a, 0), 'tabbyextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']:
    sprites.make_group('tabbycolours', (a, 1), 'tabby' + i)
    sprites.make_group('tabbyextra', (a, 1), 'tabbyextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['LIGHTBROWN', 'BROWN', 'DARKBROWN']:
    sprites.make_group('tabbycolours', (a, 2), 'tabby' + i)
    sprites.make_group('tabbyextra', (a, 2), 'tabbyextra' + i, sprites_y=2)
    a += 1

# SPECKLED colours
a = 0
for i in ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']:
    sprites.make_group('speckledcolours', (a, 0), 'speckled' + i)
    sprites.make_group('speckledextra', (a, 0), 'speckledextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']:
    sprites.make_group('speckledcolours', (a, 1), 'speckled' + i)
    sprites.make_group('speckledextra', (a, 1), 'speckledextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['LIGHTBROWN', 'BROWN', 'DARKBROWN']:
    sprites.make_group('speckledcolours', (a, 2), 'speckled' + i)
    sprites.make_group('speckledextra', (a, 2), 'speckledextra' + i, sprites_y=2)
    a += 1

# Tortie colours
a = 0
for i in ['ONE', 'TWO']:
    sprites.make_group('tortiecolours', (a, 0), 'tortie' + i)
    sprites.make_group('tortiesextra', (a, 0), 'tortieextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['FADEDONE', 'FADEDTWO']:
    sprites.make_group('tortiecolours', (a, 2), 'tortie' + i)
    sprites.make_group('tortiesextra', (a, 2), 'tortieextra' + i, sprites_y=2)
    a += 1

a = 0
for i in ['BLUEONE', 'BLUETWO']:
    sprites.make_group('tortiecolours', (a, 1), 'tortie' + i)
    sprites.make_group('tortiesextra', (a, 1), 'tortieextra' + i, sprites_y=2)
    a += 1

# Calico colours
a = 2
for i in ['ONE', 'TWO', 'THREE', 'FOUR']:
    sprites.make_group('tortiecolours', (a, 0), 'calico' + i)
    sprites.make_group('tortiesextra', (a, 0), 'calicoextra' + i, sprites_y=2)
    a += 1

a = 2
for i in ['FADEDONE', 'FADEDTWO', 'FADEDTHREE', 'FADEDFOUR']:
    sprites.make_group('tortiecolours', (a, 2), 'calico' + i)
    sprites.make_group('tortiesextra', (a, 2), 'calicoextra' + i, sprites_y=2)
    a += 1

a = 2
for i in ['BLUEONE', 'BLUETWO', 'BLUETHREE', 'BLUEFOUR']:
    sprites.make_group('tortiecolours', (a, 1), 'calico' + i)
    sprites.make_group('tortiesextra', (a, 1), 'calicoextra' + i, sprites_y=2)
    a += 1

# SKINS
sprites.make_group('skin', (0, 0), 'skinBLACK')
sprites.make_group('skin', (1, 0), 'skinRED')
sprites.make_group('skin', (2, 0), 'skinPINK')

sprites.make_group('skinextra', (0, 0), 'skinextraBLACK', sprites_y=2)
sprites.make_group('skinextra', (1, 0), 'skinextraRED', sprites_y=2)
sprites.make_group('skinextra', (2, 0), 'skinextraPINK', sprites_y=2)

sprites.load_scars()
