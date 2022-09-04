import pygame
from .game_essentials import *


class Sprites(object):

    def __init__(self, original_size, new_size=None):
        self.size = original_size  # size of a single sprite in a spritesheet
        self.new_size = self.size * 2 if new_size is None else new_size
        self.spritesheets = {}
        self.images = {}
        self.groups = {}
        self.sprites = {}

    def spritesheet(self, a_file, name):
        self.spritesheets[name] = pygame.image.load(a_file).convert_alpha()

    def image(self, a_file, name):
        self.images[name] = pygame.image.load(a_file).convert_alpha()

    def find_sprite(self, group_name, x, y):
        # find singular sprite from group
        # pixels will be calculated automatically, so for x and y, just use 0, 1, 2, 3 etc.
        new_sprite = pygame.Surface((self.size, self.size),
                                    pygame.HWSURFACE | pygame.SRCALPHA)
        new_sprite.blit(self.groups[group_name], (0, 0),
                        (x * self.size, y * self.size, (x + 1) * self.size,
                         (y + 1) * self.size))
        return new_sprite

    def make_group(self,
                   spritesheet,
                   pos,
                   name,
                   sprites_x=3,
                   sprites_y=3):  # pos = ex. (2, 3), no single pixels
        # divide sprites on a sprite-sheet into groups of sprites that are easily accessible

        # making the group
        new_group = pygame.Surface(
            (self.size * sprites_x, self.size * sprites_y),
            pygame.HWSURFACE | pygame.SRCALPHA)
        new_group.blit(
            self.spritesheets[spritesheet], (0, 0),
            (pos[0] * sprites_x * self.size, pos[1] * sprites_y * self.size,
             (pos[0] + sprites_x) * self.size,
             (pos[1] + sprites_y) * self.size))

        self.groups[name] = new_group

        # splitting group into singular sprites and storing into self.sprites section
        x_spr = 0
        y_spr = 0
        for x in range(sprites_x * sprites_y):
            new_sprite = pygame.Surface((self.size, self.size),
                                        pygame.HWSURFACE | pygame.SRCALPHA)
            new_sprite.blit(new_group, (0, 0),
                            (x_spr * self.size, y_spr * self.size,
                             (x_spr + 1) * self.size, (y_spr + 1) * self.size))
            self.sprites[name + str(x)] = new_sprite
            x_spr += 1
            if x_spr == sprites_x:
                x_spr = 0
                y_spr += 1

    def load_scars(self):
        scars = 'scars'
        self.make_group(scars, (0, 0), 'scarsONE')
        self.make_group(scars, (1, 0), 'scarsTWO')
        self.make_group(scars, (2, 0), 'scarsTHREE')
        self.make_group(scars, (3, 0), 'scarsLEFTEAR')
        self.make_group(scars, (4, 0), 'scarsRIGHTEAR')
        self.make_group(scars, (5, 0), 'scarsNOTAIL')
        self.make_group(f'{scars}extra', (0, 0), 'scarsextraONE', sprites_y=2)
        self.make_group(f'{scars}extra', (1, 0), 'scarsextraTWO', sprites_y=2)
        self.make_group(f'{scars}extra', (2, 0),
                        'scarsextraTHREE',
                        sprites_y=2)
        self.make_group(f'{scars}extra', (3, 0),
                        'scarsextraLEFTEAR',
                        sprites_y=2)
        self.make_group(f'{scars}extra', (4, 0),
                        'scarsextraRIGHTEAR',
                        sprites_y=2)
        self.make_group(f'{scars}extra', (5, 0),
                        'scarsextraNOTAIL',
                        sprites_y=2)
        for a, i in enumerate(
            ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"]):
            sprites.make_group('collars', (a, 0), f'scars{i}')
            sprites.make_group('collarsextra', (a, 0),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["GREEN", "RAINBOW", "BLACK", "SPIKES"]):
            sprites.make_group('collars', (a, 1), f'scars{i}')
            sprites.make_group('collarsextra', (a, 1),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINK", "PURPLE", "MULTI"]):
            sprites.make_group('collars', (a, 2), f'scars{i}')
            sprites.make_group('collarsextra', (a, 2),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate([
                "CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL",
                "LIMEBELL"
        ]):
            sprites.make_group('bellcollars', (a, 0), f'scars{i}')
            sprites.make_group('bellcollarsextra', (a, 0),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(
            ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL"]):
            sprites.make_group('bellcollars', (a, 1), f'scars{i}')
            sprites.make_group('bellcollarsextra', (a, 1),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINKBELL", "PURPLEBELL", "MULTIBELL"]):
            sprites.make_group('bellcollars', (a, 2), f'scars{i}')
            sprites.make_group('bellcollarsextra', (a, 2),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate([
                "CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW",
                "LIMEBOW"
        ]):
            sprites.make_group('bowcollars', (a, 0), f'scars{i}')
            sprites.make_group('bowcollarsextra', (a, 0),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(
            ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW"]):
            sprites.make_group('bowcollars', (a, 1), f'scars{i}')
            sprites.make_group('bowcollarsextra', (a, 1),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINKBOW", "PURPLEBOW", "MULTIBOW"]):
            sprites.make_group('bowcollars', (a, 2), f'scars{i}')
            sprites.make_group('bowcollarsextra', (a, 2),
                               f'scarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["TAILSCAR", "SNOUT", "CHEEK", "SIDE", "THROAT", "TAILBASE"]):
            sprites.make_group('Newscars_white', (a, 0), f'scars{i}')
            sprites.make_group('Newscarsextra_white', (a, 0), f'scarsextra{i}', sprites_y=2)
        for a, i in enumerate(["BELLY", "TOETRAP", "SNAKE"]):
            sprites.make_group('Newscars_white', (a, 1), f'scars{i}')
            sprites.make_group('Newscarsextra_white', (a, 1), f'scarsextra{i}', sprites_y=2)




sprites = Sprites(50)
tiles = Sprites(64)

for x in [
        'lineart', 'singlecolours', 'speckledcolours', 'tabbycolours',
        'whitepatches', 'tortiecolours', 'eyes', 'singleextra', 'tabbyextra',
        'speckledextra', 'whiteextra', 'eyesextra', 'tortiesextra', 'skin',
        'skinextra', 'scars', 'scarsextra', 'whitenewextra', 'whitepatchesnew',
        'scarsdark', 'scarsdarkextra', 'collars', 'collarsextra',
        'bellcollars', 'bellcollarsextra', 'bowcollars', 'bowcollarsextra',
        'speckledcolours2', 'speckledextra2', 'tabbycolours2', 'tabbyextra2',
        'tortiecolours2', 'tortiesextra2', 'rosettecolours', 'rosetteextra',
        'smokecolours', 'smokeextra', 'tickedcolors', 'tickedextra',
        'whitepatchesryos', 'whitepatchesryosextra', 'whitepatchesbeejeans', 'whitepatchesbeejeansextra',
        'Newscars_white', 'Newscarsextra_white', 'shaders', 'lineartdead'
]:
    sprites.spritesheet(f"sprites/{x}.png", x)

for sprite in [
        'Paralyzed_lineart', 'singleparalyzed', 'speckledparalyzed',
        'tabbyparalyzed', 'whiteallparalyzed', 'eyesparalyzed',
        'tabbyparalyzed', 'tortiesparalyzed', 'scarsparalyzed', 'skinparalyzed'
]:
    sprites.spritesheet(f"sprites/paralyzed/{sprite}.png", sprite)

for x in ['dithered']:
    tiles.spritesheet(f"sprites/{x}.png", x)

# Line art
sprites.make_group('lineart', (0, 0), 'lines', sprites_y=5)
sprites.make_group('Paralyzed_lineart', (0, 0),
                   'p_lines',
                   sprites_x=1,
                   sprites_y=1)
sprites.make_group('shaders', (0, 0), 'shaders', sprites_y=5)
sprites.make_group('lineartdead', (0, 0), 'lineartdead', sprites_y=5)



for a, i in enumerate(
    ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE']):
    sprites.make_group('eyes', (a, 0), f'eyes{i}')
    sprites.make_group('eyesextra', (a, 0), f'eyesextra{i}', sprites_y=2)
sprites.make_group('eyes', (0, 1), 'eyesDARKBLUE')
sprites.make_group('eyes', (1, 1), 'eyesBLUEYELLOW')
sprites.make_group('eyes', (2, 1), 'eyesBLUEGREEN')
sprites.make_group('eyesextra', (0, 1), 'eyesextraDARKBLUE', sprites_y=2)
sprites.make_group('eyesextra', (1, 1), 'eyesextraBLUEYELLOW', sprites_y=2)
sprites.make_group('eyesextra', (2, 1), 'eyesextraBLUEGREEN', sprites_y=2)

for a, i in enumerate(
    ['ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN', 'ANY2'], start=1):
    sprites.make_group('whitepatches', (a, 0), f'white{i}')
    sprites.make_group('whiteextra', (a, 0), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate([
        'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL',
        'LIGHTSONG', 'VITILIGO'
]):
    sprites.make_group('whitepatchesnew', (a, 0), f'white{i}')
    sprites.make_group('whitenewextra', (a, 0), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate([
        'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY',
        'VANCREAMY', 'ANY2CREAMY'
]):
    sprites.make_group('whitepatches', (a, 1), f'white{i}')
    sprites.make_group('whiteextra', (a, 1), f'whiteextra{i}', sprites_y=2)
# extra
sprites.make_group('whitepatches', (0, 2), 'whiteEXTRA')
sprites.make_group('whiteextra', (0, 2), 'whiteextraEXTRA', sprites_y=2)

for a, i in enumerate(
    ['TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE']):
    sprites.make_group('whitepatchesryos', (a, 0), f'white{i}')
    sprites.make_group('whitepatchesryosextra', (a, 0), f'whiteextra{i}', sprites_y=2)

for a, i in enumerate(['TAIL', 'BLAZE', 'PRINCE', 'BIB', 'VEE', 'UNDERS', 'PAWS']):
    sprites.make_group('whitepatchesryos', (a, 1), f'white{i}')
    sprites.make_group('whitepatchesryosextra', (a, 1), f'whiteextra{i}', sprites_y=2)

for a, i in enumerate(
    ['FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TAILTIP','TOES', 'BROKENBLAZE']):
    sprites.make_group('whitepatchesryos', (a, 2), f'white{i}')
    sprites.make_group('whitepatchesryosextra', (a, 2), f'whiteextra{i}', sprites_y=2)

#beejeans white patches    
for a, i in enumerate(['PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'PIEBALD', 'CURVED']):
    sprites.make_group('whitepatchesbeejeans', (a, 0), 'white' + i)
    sprites.make_group('whitepatchesbeejeansextra', (a, 0), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['HEART', 'LILTWO', 'GLASS', 'MOORISH', 'POINTMARK']):
    sprites.make_group('whitepatchesbeejeans', (a, 1), 'white' + i)
    sprites.make_group('whitepatchesbeejeansextra', (a, 1), 'whiteextra' + i, sprites_y=2)


for a, i in enumerate(
    ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']):
    sprites.make_group('singlecolours', (a, 0), f'single{i}')
    sprites.make_group('singleextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']):
    sprites.make_group('singlecolours', (a, 1), f'single{i}')
    sprites.make_group('singleextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN']):
    sprites.make_group('singlecolours', (a, 2), f'single{i}')
    sprites.make_group('singleextra', (a, 2), f'singleextra{i}', sprites_y=2)

for a, i in enumerate(
    ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']):
    sprites.make_group('tabbycolours', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']):
    sprites.make_group('tabbycolours', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN']):
    sprites.make_group('tabbycolours', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyextra', (a, 2), f'tabbyextra{i}', sprites_y=2)

for a, i in enumerate(
    ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']):
    sprites.make_group('tabbycolours2', (a, 0), f'tabby2{i}')
    sprites.make_group('tabbyextra2', (a, 0), f'tabby2extra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']):
    sprites.make_group('tabbycolours2', (a, 1), f'tabby2{i}')
    sprites.make_group('tabbyextra2', (a, 1), f'tabby2extra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN']):
    sprites.make_group('tabbycolours2', (a, 2), f'tabby2{i}')
    sprites.make_group('tabbyextra2', (a, 2), f'tabby2extra{i}', sprites_y=2)

for a, i in enumerate(
    ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']):
    sprites.make_group('rosettecolours', (a, 0), f'rosette{i}')
    sprites.make_group('rosetteextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']):
    sprites.make_group('rosettecolours', (a, 1), f'rosette{i}')
    sprites.make_group('rosetteextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN']):
    sprites.make_group('rosettecolours', (a, 2), f'rosette{i}')
    sprites.make_group('rosetteextra', (a, 2), f'rosetteextra{i}', sprites_y=2)

for a, i in enumerate(
    ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']):
    sprites.make_group('smokecolours', (a, 0), f'smoke{i}')
    sprites.make_group('smokeextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']):
    sprites.make_group('smokecolours', (a, 1), f'smoke{i}')
    sprites.make_group('smokeextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN']):
    sprites.make_group('smokecolours', (a, 2), f'smoke{i}')
    sprites.make_group('smokeextra', (a, 2), f'smokeextra{i}', sprites_y=2)

for a, i in enumerate(
    ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']):
    sprites.make_group('tickedcolors', (a, 0), f'ticked{i}')
    sprites.make_group('tickedextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']):
    sprites.make_group('tickedcolors', (a, 1), f'ticked{i}')
    sprites.make_group('tickedextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN']):
    sprites.make_group('tickedcolors', (a, 2), f'ticked{i}')
    sprites.make_group('tickedextra', (a, 2), f'tickedextra{i}', sprites_y=2)

for a, i in enumerate(
    ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']):
    sprites.make_group('speckledcolours', (a, 0), f'speckled{i}')
    sprites.make_group('speckledextra', (a, 0),
                       f'speckledextra{i}',
                       sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']):
    sprites.make_group('speckledcolours', (a, 1), f'speckled{i}')
    sprites.make_group('speckledextra', (a, 1),
                       f'speckledextra{i}',
                       sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN']):
    sprites.make_group('speckledcolours', (a, 2), f'speckled{i}')
    sprites.make_group('speckledextra', (a, 2),
                       f'speckledextra{i}',
                       sprites_y=2)

for a, i in enumerate(
    ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK']):
    sprites.make_group('speckledcolours2', (a, 0), f'speckled2{i}')
    sprites.make_group('speckledextra2', (a, 0),
                       f'speckled2extra{i}',
                       sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER']):
    sprites.make_group('speckledcolours2', (a, 1), f'speckled2{i}')
    sprites.make_group('speckledextra2', (a, 1),
                       f'speckled2extra{i}',
                       sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN']):
    sprites.make_group('speckledcolours2', (a, 2), f'speckled2{i}')
    sprites.make_group('speckledextra2', (a, 2),
                       f'speckled2extra{i}',
                       sprites_y=2)

for a, i in enumerate(['ONE', 'TWO']):
    sprites.make_group('tortiecolours', (a, 0), f'tortie{i}')
    sprites.make_group('tortiesextra', (a, 0), f'tortieextra{i}', sprites_y=2)
for a, i in enumerate(['FADEDONE', 'FADEDTWO']):
    sprites.make_group('tortiecolours', (a, 2), f'tortie{i}')
    sprites.make_group('tortiesextra', (a, 2), f'tortieextra{i}', sprites_y=2)
for a, i in enumerate(['BLUEONE', 'BLUETWO']):
    sprites.make_group('tortiecolours', (a, 1), f'tortie{i}')
    sprites.make_group('tortiesextra', (a, 1), f'tortieextra{i}', sprites_y=2)
for a, i in enumerate(['ONE', 'TWO', 'THREE', 'FOUR'], start=2):
    sprites.make_group('tortiecolours', (a, 0), f'calico{i}')
    sprites.make_group('tortiesextra', (a, 0), f'calicoextra{i}', sprites_y=2)
for a, i in enumerate(['FADEDONE', 'FADEDTWO', 'FADEDTHREE', 'FADEDFOUR'],
                      start=2):
    sprites.make_group('tortiecolours', (a, 2), f'calico{i}')
    sprites.make_group('tortiesextra', (a, 2), f'calicoextra{i}', sprites_y=2)
for a, i in enumerate(['BLUEONE', 'BLUETWO', 'BLUETHREE', 'BLUEFOUR'],
                      start=2):
    sprites.make_group('tortiecolours', (a, 1), f'calico{i}')
    sprites.make_group('tortiesextra', (a, 1), f'calicoextra{i}', sprites_y=2)

for a, i in enumerate(['ONE', 'TWO']):
    sprites.make_group('tortiecolours2', (a, 0), f'tortie2{i}')
    sprites.make_group('tortiesextra2', (a, 0),
                       f'tortie2extra{i}',
                       sprites_y=2)
for a, i in enumerate(['FADEDONE', 'FADEDTWO']):
    sprites.make_group('tortiecolours2', (a, 2), f'tortie2{i}')
    sprites.make_group('tortiesextra2', (a, 2),
                       f'tortie2extra{i}',
                       sprites_y=2)
for a, i in enumerate(['BLUEONE', 'BLUETWO']):
    sprites.make_group('tortiecolours2', (a, 1), f'tortie2{i}')
    sprites.make_group('tortiesextra2', (a, 1),
                       f'tortie2extra{i}',
                       sprites_y=2)
for a, i in enumerate(['ONE', 'TWO', 'THREE', 'FOUR'], start=2):
    sprites.make_group('tortiecolours2', (a, 0), f'calico2{i}')
    sprites.make_group('tortiesextra2', (a, 0), f'calico2extra{i}', sprites_y=2)
for a, i in enumerate(['FADEDONE', 'FADEDTWO', 'FADEDTHREE', 'FADEDFOUR'],
                      start=2):
    sprites.make_group('tortiecolours2', (a, 2), f'calico2{i}')
    sprites.make_group('tortiesextra2', (a, 2), f'calico2extra{i}', sprites_y=2)
for a, i in enumerate(['BLUEONE', 'BLUETWO', 'BLUETHREE', 'BLUEFOUR'],
                      start=2):
    sprites.make_group('tortiecolours2', (a, 1), f'calico2{i}')
    sprites.make_group('tortiesextra2', (a, 1), f'calico2extra{i}', sprites_y=2)

# SKINS
sprites.make_group('skin', (0, 0), 'skinBLACK')
sprites.make_group('skin', (1, 0), 'skinRED')
sprites.make_group('skin', (2, 0), 'skinPINK')
sprites.make_group('skinparalyzed', (0, 0),
                   'skinparalyzedPINK',
                   sprites_x=1,
                   sprites_y=1)
sprites.make_group('skinparalyzed', (1, 0),
                   'skinparalyzedRED',
                   sprites_x=1,
                   sprites_y=1)
sprites.make_group('skinparalyzed', (2, 0),
                   'skinparalyzedBLACK',
                   sprites_x=1,
                   sprites_y=1)

sprites.make_group('skinextra', (0, 0), 'skinextraBLACK', sprites_y=2)
sprites.make_group('skinextra', (1, 0), 'skinextraRED', sprites_y=2)
sprites.make_group('skinextra', (2, 0), 'skinextraPINK', sprites_y=2)

tiles.make_group('dithered', (0, 0), 'terrain')
tiles.make_group('dithered', (1, 0), 'terraintwo')

sprites.load_scars()
