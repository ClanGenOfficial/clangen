import pygame

from scripts.game_structure.game_essentials import *
try:
    import ujson
except ImportError:
    import json as ujson


class Sprites():
    cat_tints = {}

    def __init__(self, original_size, new_size=None):
        self.size = original_size  # size of a single sprite in a spritesheet
        self.new_size = self.size * 2 if new_size is None else new_size
        self.spritesheets = {}
        self.images = {}
        self.groups = {}
        self.sprites = {}

        self.load_tints()

    def load_tints(self):
        try:
            with open("sprites/dicts/tint.json", 'r') as read_file:
                Sprites.cat_tints = ujson.loads(read_file.read())
        except:
            print("ERROR: Reading Tints")

    def spritesheet(self, a_file, name):
        """
        Add spritesheet called name from a_file.

        Parameters:
        a_file -- Path to the file to create a spritesheet from.
        name -- Name to call the new spritesheet.
        """
        self.spritesheets[name] = pygame.image.load(a_file).convert_alpha()

    def find_sprite(self, group_name, x, y):
        """
        Find singular sprite from a group.

        Parameters:
        group_name -- Name of Pygame group to find sprite from.
        x -- X-offset of the sprite to get. NOT pixel offset, but offset of other sprites.
        y -- Y-offset of the sprite to get. NOT pixel offset, but offset of other sprites.
        """
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
        """
        Divide sprites on a sprite-sheet into groups of sprites that are easily accessible.

        Parameters:
        spritesheet -- Name of spritesheet.
        pos -- (x,y) tuple of offsets. NOT pixel offset, but offset of other sprites.
        name -- Name of group to make.
        
        Keyword Arguments
        sprites_x -- Number of sprites horizontally (default: 3)
        sprites_y -- Number of sprites vertically (default: 3)
        """

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
        """
        Loads scar sprites and puts them into groups.
        """
        scars = 'scars'

        for a, i in enumerate(
                ["ONE", "TWO", "THREE", "LEFTEAR", "RIGHTEAR", "NOTAIL"]):
            sprites.make_group('scars', (a, 0), f'scars{i}')
            sprites.make_group('scarsextra', (a, 0),
                               f'scarsextra{i}',
                               sprites_y=2)

        for a, i in enumerate(
                ["MANLEG", "BRIGHTHEART", "MANTAIL", "NOLEFTEAR", "NORIGHTEAR", "NOEAR"]):
            sprites.make_group('scars', (a, 1), f'scars{i}')
            sprites.make_group('scarsextra', (a, 1),
                               f'scarsextra{i}',
                               sprites_y=2)

        for a, i in enumerate(
                ["BRIDGE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND", "BURNPAWS", "BURNTAIL"]):
            sprites.make_group('scars', (a, 2), f'scars{i}')
            sprites.make_group('scarsextra', (a, 2),
                               f'scarsextra{i}',
                               sprites_y=2)

        for a, i in enumerate(
                ["BURNBELLY", "BEAKCHEEK", "BEAKLOWER", "BURNRUMP", "CATBITE", "RATBITE"]):
            sprites.make_group('scars', (a, 3), f'scars{i}')
            sprites.make_group('scarsextra', (a, 3),
                               f'scarsextra{i}',
                               sprites_y=2)

        for a, i in enumerate(
                ["TAILSCAR", "SNOUT", "CHEEK", "SIDE", "THROAT", "TAILBASE"]):
            sprites.make_group('Newscars', (a, 0), f'scars{i}')
            sprites.make_group('Newscarsextra', (a, 0),
                               f'scarsextra{i}',
                               sprites_y=2)

        for a, i in enumerate(["BELLY", "TOETRAP", "SNAKE"]):
            sprites.make_group('Newscars', (a, 1), f'scars{i}')
            sprites.make_group('Newscarsextra', (a, 1),
                               f'scarsextra{i}',
                               sprites_y=2)

        for a, i in enumerate(["LEGBITE", "NECKBITE", "FACE", "HALFTAIL", "NOPAW"]):
            sprites.make_group('Newscars', (a, 2), f'scars{i}')
            sprites.make_group('Newscarsextra', (a, 2),
                               f'scarsextra{i}',
                               sprites_y=2)

        for a, i in enumerate(["FROSTFACE", "FROSTTAIL", "FROSTMITT", "FROSTSOCK", "QUILLCHUNK", "QUILLSCRATCH"]):
            sprites.make_group('Newscars', (a, 3), f'scars{i}')
            sprites.make_group('Newscarsextra', (a, 3),
                               f'scarsextra{i}',
                               sprites_y=2)

            # Accessories
        for a, i in enumerate([
            "MAPLE LEAF", "HOLLY", "BLUE BERRIES", "FORGET ME NOTS", "RYE STALK", "LAUREL"]):
            sprites.make_group('medcatherbs', (a, 0), f'acc_herbs{i}')
            sprites.make_group('medcatherbsextra', (a, 0), f'acc_herbsextra{i}', sprites_y=2)
        for a, i in enumerate([
            "BLUEBELLS", "NETTLE", "POPPY", "LAVENDER", "HERBS", "PETALS"]):
            sprites.make_group('medcatherbs', (a, 1), f'acc_herbs{i}')
            sprites.make_group('medcatherbsextra', (a, 1), f'acc_herbsextra{i}', sprites_y=2)
        for a, i in enumerate([
            "OAK LEAVES", "CATMINT", "MAPLE SEED", "JUNIPER"]):
            sprites.make_group('medcatherbs', (a, 3), f'acc_herbs{i}')
            sprites.make_group('medcatherbsextra', (a, 3), f'acc_herbsextra{i}', sprites_y=2)
        sprites.make_group('medcatherbs', (5, 2), 'acc_herbsDRY HERBS')
        sprites.make_group('medcatherbsextra', (5, 2), 'acc_herbsextraDRY HERBS', sprites_y=2)

        for a, i in enumerate([
            "RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS", "MOTH WINGS", "CICADA WINGS"]):
            sprites.make_group('medcatherbs', (a, 2), f'acc_wild{i}')
            sprites.make_group('medcatherbsextra', (a, 2), f'acc_wildextra{i}', sprites_y=2)
        for a, i in enumerate(["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"]):
            sprites.make_group('collars', (a, 0), f'collars{i}')
            sprites.make_group('collarsextra', (a, 0),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["GREEN", "RAINBOW", "BLACK", "SPIKES"]):
            sprites.make_group('collars', (a, 1), f'collars{i}')
            sprites.make_group('collarsextra', (a, 1),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINK", "PURPLE", "MULTI"]):
            sprites.make_group('collars', (a, 2), f'collars{i}')
            sprites.make_group('collarsextra', (a, 2),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate([
            "CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL",
            "LIMEBELL"
        ]):
            sprites.make_group('bellcollars', (a, 0), f'collars{i}')
            sprites.make_group('bellcollarsextra', (a, 0),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(
                ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL"]):
            sprites.make_group('bellcollars', (a, 1), f'collars{i}')
            sprites.make_group('bellcollarsextra', (a, 1),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINKBELL", "PURPLEBELL", "MULTIBELL"]):
            sprites.make_group('bellcollars', (a, 2), f'collars{i}')
            sprites.make_group('bellcollarsextra', (a, 2),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate([
            "CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW",
            "LIMEBOW"
        ]):
            sprites.make_group('bowcollars', (a, 0), f'collars{i}')
            sprites.make_group('bowcollarsextra', (a, 0),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(
                ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW"]):
            sprites.make_group('bowcollars', (a, 1), f'collars{i}')
            sprites.make_group('bowcollarsextra', (a, 1),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINKBOW", "PURPLEBOW", "MULTIBOW"]):
            sprites.make_group('bowcollars', (a, 2), f'collars{i}')
            sprites.make_group('bowcollarsextra', (a, 2),
                               f'collarsextra{i}',
                               sprites_y=2)


sprites = Sprites(50)
#tiles = Sprites(64)

for x in [
    'lineart', 'singlecolours', 'speckledcolours', 'tabbycolours',
    'whitepatches', 'eyes', 'singleextra', 'tabbyextra', 'eyes2',
    'speckledextra', 'whiteextra', 'eyesextra', 'eyes2extra', 'skin',
    'skinextra', 'scars', 'scarsextra', 'whitenewextra', 'whitepatchesnew',
    'scarsdark', 'scarsdarkextra', 'collars', 'collarsextra',
    'bellcollars', 'bellcollarsextra', 'bowcollars', 'bowcollarsextra',
    'speckledcolours2', 'speckledextra2', 'tabbycolours2', 'tabbyextra2',
    'rosettecolours', 'rosetteextra', 'smokecolours', 'smokeextra', 'tickedcolours', 'tickedextra',
    'mackerelcolours', 'classiccolours', 'sokokecolours', 'agouticolours', 'singlestripecolours',
    'mackerelextra', 'classicextra', 'sokokeextra', 'agoutiextra', 'singlestripeextra',
    'whitepatches3', 'whitepatches3extra', 'whitepatches4', 'whitepatches4extra',
    'Newscars', 'Newscarsextra', 'shadersnewwhite', 'lineartdead',
    'tortiecolourssolid', 'tortiecolourstabby', 'tortiecoloursbengal', 'tortiecoloursmarbled',
    'tortiecoloursticked', 'tortiecolourssmoke', 'tortiecoloursrosette', 'tortiecoloursspeckled',
    'tortiecoloursmackerel', 'tortiecoloursclassic', 'tortiecolourssokoke', 'tortiecoloursagouti',
    'tortiesextrasolid', 'tortiesextratabby', 'tortiesextrabengal', 'tortiesextramarbled', 'tortiesextraticked',
    'tortiesextrasmoke', 'tortiesextrarosette', 'tortiesextraspeckled',
    'tortiesextramackerel', 'tortiesextraclassic', 'tortiesextrasokoke', 'tortiesextraagouti',
    'medcatherbs', 'medcatherbsextra', 'lineartdf', 'eyes_df', 'eyesextra_df', 'lightingnew'

]:
    sprites.spritesheet(f"sprites/{x}.png", x)

for sprite in [
    'Paralyzed_lineart', 'singleparalyzed', 'speckledparalyzed',
    'tabbyparalyzed', 'whiteallparalyzed', 'eyesparalyzed',
    'tabbyparalyzed', 'tortiesparalyzed', 'scarsparalyzed', 'skinparalyzed',
    'medcatherbsparalyzed'

]:
    sprites.spritesheet(f"sprites/paralyzed/{sprite}.png", sprite)

# for x in ['dithered']:
#     tiles.spritesheet(f"sprites/{x}.png", x)

# Line art
sprites.make_group('lineart', (0, 0), 'lines', sprites_y=5)
sprites.make_group('Paralyzed_lineart', (0, 0),
                   'p_lines',
                   sprites_x=1,
                   sprites_y=1)
sprites.make_group('shadersnewwhite', (0, 0), 'shaders', sprites_y=5)
sprites.make_group('lightingnew', (0, 0), 'lighting', sprites_y=5)

sprites.make_group('lineartdead', (0, 0), 'lineartdead', sprites_y=5)
sprites.make_group('lineartdf', (0, 0), 'lineartdf', sprites_y=5)

for a, i in enumerate(
        ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE']):
    sprites.make_group('eyes', (a, 0), f'eyes{i}')
    sprites.make_group('eyesextra', (a, 0), f'eyesextra{i}', sprites_y=2)
    sprites.make_group('eyes2', (a, 0), f'eyes2{i}')
    sprites.make_group('eyes2extra', (a, 0), f'eyes2extra{i}', sprites_y=2)
for a, i in enumerate(
        ['DARKBLUE', 'GREY', 'CYAN', 'EMERALD', 'HEATHERBLUE', 'SUNLITICE']):
    sprites.make_group('eyes', (a, 1), f'eyes{i}')
    sprites.make_group('eyesextra', (a, 1), f'eyesextra{i}', sprites_y=2)
    sprites.make_group('eyes2', (a, 1), f'eyes2{i}')
    sprites.make_group('eyes2extra', (a, 1), f'eyes2extra{i}', sprites_y=2)
for a, i in enumerate(
        ['COPPER', 'SAGE', 'BLUE2', 'PALEBLUE', 'BLUEYELLOW', 'BLUEGREEN']):
    sprites.make_group('eyes', (a, 2), f'eyes{i}')
    sprites.make_group('eyesextra', (a, 2), f'eyesextra{i}', sprites_y=2)
    sprites.make_group('eyes2', (a, 2), f'eyes2{i}')
    sprites.make_group('eyes2extra', (a, 2), f'eyes2extra{i}', sprites_y=2)
for a, i in enumerate(
        ['PALEYELLOW', 'GOLD', 'GREENYELLOW']):
    sprites.make_group('eyes', (a, 3), f'eyes{i}')
    sprites.make_group('eyesextra', (a, 3), f'eyesextra{i}', sprites_y=2)
    sprites.make_group('eyes2', (a, 3), f'eyes2{i}')
    sprites.make_group('eyes2extra', (a, 3), f'eyes2extra{i}', sprites_y=2)

# white patches
for a, i in enumerate(['FULLWHITE', 'ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN', 'ANY2']):
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

# ryos white patches
for a, i in enumerate(
        ['TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'VITILIGO2']):
    sprites.make_group('whitepatches3', (a, 0), f'white{i}')
    sprites.make_group('whitepatches3extra', (a, 0), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate(['TAIL', 'BLAZE', 'PRINCE', 'BIB', 'VEE', 'UNDERS', 'PAWS', 'MITAINE']):
    sprites.make_group('whitepatches3', (a, 1), f'white{i}')
    sprites.make_group('whitepatches3extra', (a, 1), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate(
        ['FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TAILTIP', 'TOES', 'BROKENBLAZE', 'SCOURGE']):
    sprites.make_group('whitepatches3', (a, 2), f'white{i}')
    sprites.make_group('whitepatches3extra', (a, 2), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate(
        ['APRON', 'CAPSADDLE', 'MASKMANTLE', 'SQUEAKS', 'STAR', 'TOESTAIL', 'RAVENPAW', 'HONEY']):
    sprites.make_group('whitepatches3', (a, 3), f'white{i}')
    sprites.make_group('whitepatches3extra', (a, 3), f'whiteextra{i}', sprites_y=2)

# beejeans white patches + perrio's point marks
for a, i in enumerate(['PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'PIEBALD', 'CURVED']):
    sprites.make_group('whitepatches4', (a, 0), 'white' + i)
    sprites.make_group('whitepatches4extra', (a, 0), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['HEART', 'LILTWO', 'GLASS', 'MOORISH', 'SEPIAPOINT', 'MINKPOINT', 'SEALPOINT']):
    sprites.make_group('whitepatches4', (a, 1), 'white' + i)
    sprites.make_group('whitepatches4extra', (a, 1), 'whiteextra' + i, sprites_y=2)

# single (solid)
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('singlecolours', (a, 0), f'single{i}')
    sprites.make_group('singleextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('singlecolours', (a, 1), f'single{i}')
    sprites.make_group('singleextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('singlecolours', (a, 2), f'single{i}')
    sprites.make_group('singleextra', (a, 2), f'singleextra{i}', sprites_y=2)
# tabby
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('tabbycolours', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('tabbycolours', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('tabbycolours', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyextra', (a, 2), f'tabbyextra{i}', sprites_y=2)
# marbled
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('tabbycolours2', (a, 0), f'marbled{i}')
    sprites.make_group('tabbyextra2', (a, 0), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('tabbycolours2', (a, 1), f'marbled{i}')
    sprites.make_group('tabbyextra2', (a, 1), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('tabbycolours2', (a, 2), f'marbled{i}')
    sprites.make_group('tabbyextra2', (a, 2), f'marbledextra{i}', sprites_y=2)
# rosette
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('rosettecolours', (a, 0), f'rosette{i}')
    sprites.make_group('rosetteextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('rosettecolours', (a, 1), f'rosette{i}')
    sprites.make_group('rosetteextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('rosettecolours', (a, 2), f'rosette{i}')
    sprites.make_group('rosetteextra', (a, 2), f'rosetteextra{i}', sprites_y=2)
# smoke
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('smokecolours', (a, 0), f'smoke{i}')
    sprites.make_group('smokeextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('smokecolours', (a, 1), f'smoke{i}')
    sprites.make_group('smokeextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('smokecolours', (a, 2), f'smoke{i}')
    sprites.make_group('smokeextra', (a, 2), f'smokeextra{i}', sprites_y=2)
# ticked
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('tickedcolours', (a, 0), f'ticked{i}')
    sprites.make_group('tickedextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('tickedcolours', (a, 1), f'ticked{i}')
    sprites.make_group('tickedextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('tickedcolours', (a, 2), f'ticked{i}')
    sprites.make_group('tickedextra', (a, 2), f'tickedextra{i}', sprites_y=2)
# speckled
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('speckledcolours', (a, 0), f'speckled{i}')
    sprites.make_group('speckledextra', (a, 0), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('speckledcolours', (a, 1), f'speckled{i}')
    sprites.make_group('speckledextra', (a, 1), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('speckledcolours', (a, 2), f'speckled{i}')
    sprites.make_group('speckledextra', (a, 2), f'speckledextra{i}', sprites_y=2)
# bengal
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('speckledcolours2', (a, 0), f'bengal{i}')
    sprites.make_group('speckledextra2', (a, 0), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('speckledcolours2', (a, 1), f'bengal{i}')
    sprites.make_group('speckledextra2', (a, 1), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('speckledcolours2', (a, 2), f'bengal{i}')
    sprites.make_group('speckledextra2', (a, 2), f'bengalextra{i}', sprites_y=2)
# mackerel
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('mackerelcolours', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelextra', (a, 0), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('mackerelcolours', (a, 1), f'mackerel{i}')
    sprites.make_group('mackerelextra', (a, 1), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('mackerelcolours', (a, 2), f'mackerel{i}')
    sprites.make_group('mackerelextra', (a, 2), f'mackerelextra{i}', sprites_y=2)
# classic
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('classiccolours', (a, 0), f'classic{i}')
    sprites.make_group('classicextra', (a, 0), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('classiccolours', (a, 1), f'classic{i}')
    sprites.make_group('classicextra', (a, 1), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('classiccolours', (a, 2), f'classic{i}')
    sprites.make_group('classicextra', (a, 2), f'classicextra{i}', sprites_y=2)
# sokoke
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('sokokecolours', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokeextra', (a, 0), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('sokokecolours', (a, 1), f'sokoke{i}')
    sprites.make_group('sokokeextra', (a, 1), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('sokokecolours', (a, 2), f'sokoke{i}')
    sprites.make_group('sokokeextra', (a, 2), f'sokokeextra{i}', sprites_y=2)
# agouti
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('agouticolours', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiextra', (a, 0), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('agouticolours', (a, 1), f'agouti{i}')
    sprites.make_group('agoutiextra', (a, 1), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('agouticolours', (a, 2), f'agouti{i}')
    sprites.make_group('agoutiextra', (a, 2), f'agoutiextra{i}', sprites_y=2)
# singlestripe
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('singlestripecolours', (a, 0), f'singlestripe{i}')
    sprites.make_group('singlestripeextra', (a, 0), f'singlestripeextra{i}', sprites_y=2)
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('singlestripecolours', (a, 1), f'singlestripe{i}')
    sprites.make_group('singlestripeextra', (a, 1), f'singlestripeextra{i}', sprites_y=2)
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('singlestripecolours', (a, 2), f'singlestripe{i}')
    sprites.make_group('singlestripeextra', (a, 2), f'singlestripeextra{i}', sprites_y=2)
# new torties
# solids
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecolourssolid', (a, 0), f'tortiesolid{i}')
    sprites.make_group('tortiesextrasolid', (a, 0), f'tortiesolidextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecolourssolid', (a, 1), f'tortiesolid{i}')
    sprites.make_group('tortiesextrasolid', (a, 1), f'tortiesolidextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecolourssolid', (a, 2), f'tortiesolid{i}')
    sprites.make_group('tortiesextrasolid', (a, 2), f'tortiesolidextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecolourssolid', (a, 3), f'tortiesolid{i}')
    sprites.make_group('tortiesextrasolid', (a, 3), f'tortiesolidextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecolourssolid', (a, 4), f'tortiesolid{i}')
    sprites.make_group('tortiesextrasolid', (a, 4), f'tortiesolidextra{i}', sprites_y=2)
# tabby
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecolourstabby', (a, 0), f'tortietabby{i}')
    sprites.make_group('tortiesextratabby', (a, 0), f'tortietabbyextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecolourstabby', (a, 1), f'tortietabby{i}')
    sprites.make_group('tortiesextratabby', (a, 1), f'tortietabbyextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecolourstabby', (a, 2), f'tortietabby{i}')
    sprites.make_group('tortiesextratabby', (a, 2), f'tortietabbyextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecolourstabby', (a, 3), f'tortietabby{i}')
    sprites.make_group('tortiesextratabby', (a, 3), f'tortietabbyextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecolourstabby', (a, 4), f'tortietabby{i}')
    sprites.make_group('tortiesextratabby', (a, 4), f'tortietabbyextra{i}', sprites_y=2)
# bengal
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecoloursbengal', (a, 0), f'tortiebengal{i}')
    sprites.make_group('tortiesextrabengal', (a, 0), f'tortiebengalextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecoloursbengal', (a, 1), f'tortiebengal{i}')
    sprites.make_group('tortiesextrabengal', (a, 1), f'tortiebengalextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecoloursbengal', (a, 2), f'tortiebengal{i}')
    sprites.make_group('tortiesextrabengal', (a, 2), f'tortiebengalextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecoloursbengal', (a, 3), f'tortiebengal{i}')
    sprites.make_group('tortiesextrabengal', (a, 3), f'tortiebengalextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecoloursbengal', (a, 4), f'tortiebengal{i}')
    sprites.make_group('tortiesextrabengal', (a, 4), f'tortiebengalextra{i}', sprites_y=2)
# marbled
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecoloursmarbled', (a, 0), f'tortiemarbled{i}')
    sprites.make_group('tortiesextramarbled', (a, 0), f'tortiemarbledextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecoloursmarbled', (a, 1), f'tortiemarbled{i}')
    sprites.make_group('tortiesextramarbled', (a, 1), f'tortiemarbledextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecoloursmarbled', (a, 2), f'tortiemarbled{i}')
    sprites.make_group('tortiesextramarbled', (a, 2), f'tortiemarbledextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecoloursmarbled', (a, 3), f'tortiemarbled{i}')
    sprites.make_group('tortiesextramarbled', (a, 3), f'tortiemarbledextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecoloursmarbled', (a, 4), f'tortiemarbled{i}')
    sprites.make_group('tortiesextramarbled', (a, 4), f'tortiemarbledextra{i}', sprites_y=2)
# ticked
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecoloursticked', (a, 0), f'tortieticked{i}')
    sprites.make_group('tortiesextraticked', (a, 0), f'tortietickedextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecoloursticked', (a, 1), f'tortieticked{i}')
    sprites.make_group('tortiesextraticked', (a, 1), f'tortietickedextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecoloursticked', (a, 2), f'tortieticked{i}')
    sprites.make_group('tortiesextraticked', (a, 2), f'tortietickedextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecoloursticked', (a, 3), f'tortieticked{i}')
    sprites.make_group('tortiesextraticked', (a, 3), f'tortietickedextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecoloursticked', (a, 4), f'tortieticked{i}')
    sprites.make_group('tortiesextraticked', (a, 4), f'tortietickedextra{i}', sprites_y=2)
# smoke
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecolourssmoke', (a, 0), f'tortiesmoke{i}')
    sprites.make_group('tortiesextrasmoke', (a, 0), f'tortiesmokeextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecolourssmoke', (a, 1), f'tortiesmoke{i}')
    sprites.make_group('tortiesextrasmoke', (a, 1), f'tortiesmokeextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecolourssmoke', (a, 2), f'tortiesmoke{i}')
    sprites.make_group('tortiesextrasmoke', (a, 2), f'tortiesmokeextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecolourssmoke', (a, 3), f'tortiesmoke{i}')
    sprites.make_group('tortiesextrasmoke', (a, 3), f'tortiesmokeextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecolourssmoke', (a, 4), f'tortiesmoke{i}')
    sprites.make_group('tortiesextrasmoke', (a, 4), f'tortiesmokeextra{i}', sprites_y=2)
# rosette
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecoloursrosette', (a, 0), f'tortierosette{i}')
    sprites.make_group('tortiesextrarosette', (a, 0), f'tortierosetteextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecoloursrosette', (a, 1), f'tortierosette{i}')
    sprites.make_group('tortiesextrarosette', (a, 1), f'tortierosetteextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecoloursrosette', (a, 2), f'tortierosette{i}')
    sprites.make_group('tortiesextrarosette', (a, 2), f'tortierosetteextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecoloursrosette', (a, 3), f'tortierosette{i}')
    sprites.make_group('tortiesextrarosette', (a, 3), f'tortierosetteextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecoloursrosette', (a, 4), f'tortierosette{i}')
    sprites.make_group('tortiesextrarosette', (a, 4), f'tortierosetteextra{i}', sprites_y=2)
# speckled
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecoloursspeckled', (a, 0), f'tortiespeckled{i}')
    sprites.make_group('tortiesextraspeckled', (a, 0), f'tortiespeckledextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecoloursspeckled', (a, 1), f'tortiespeckled{i}')
    sprites.make_group('tortiesextraspeckled', (a, 1), f'tortiespeckledextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecoloursspeckled', (a, 2), f'tortiespeckled{i}')
    sprites.make_group('tortiesextraspeckled', (a, 2), f'tortiespeckledextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecoloursspeckled', (a, 3), f'tortiespeckled{i}')
    sprites.make_group('tortiesextraspeckled', (a, 3), f'tortiespeckledextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecoloursspeckled', (a, 4), f'tortiespeckled{i}')
    sprites.make_group('tortiesextraspeckled', (a, 4), f'tortiespeckledextra{i}', sprites_y=2)
# mackerel
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecoloursmackerel', (a, 0), f'tortiemackerel{i}')
    sprites.make_group('tortiesextramackerel', (a, 0), f'tortiemackerelextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecoloursmackerel', (a, 1), f'tortiemackerel{i}')
    sprites.make_group('tortiesextramackerel', (a, 1), f'tortiemackerelextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecoloursmackerel', (a, 2), f'tortiemackerel{i}')
    sprites.make_group('tortiesextramackerel', (a, 2), f'tortiemackerelextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecoloursmackerel', (a, 3), f'tortiemackerel{i}')
    sprites.make_group('tortiesextramackerel', (a, 3), f'tortiemackerelextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecoloursmackerel', (a, 4), f'tortiemackerel{i}')
    sprites.make_group('tortiesextramackerel', (a, 4), f'tortiemackerelextra{i}', sprites_y=2)
# classic
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecoloursclassic', (a, 0), f'tortieclassic{i}')
    sprites.make_group('tortiesextraclassic', (a, 0), f'tortieclassicextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecoloursclassic', (a, 1), f'tortieclassic{i}')
    sprites.make_group('tortiesextraclassic', (a, 1), f'tortieclassicextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecoloursclassic', (a, 2), f'tortieclassic{i}')
    sprites.make_group('tortiesextraclassic', (a, 2), f'tortieclassicextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecoloursclassic', (a, 3), f'tortieclassic{i}')
    sprites.make_group('tortiesextraclassic', (a, 3), f'tortieclassicextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecoloursclassic', (a, 4), f'tortieclassic{i}')
    sprites.make_group('tortiesextraclassic', (a, 4), f'tortieclassicextra{i}', sprites_y=2)
# sokoke
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecolourssokoke', (a, 0), f'tortiesokoke{i}')
    sprites.make_group('tortiesextrasokoke', (a, 0), f'tortiesokokeextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecolourssokoke', (a, 1), f'tortiesokoke{i}')
    sprites.make_group('tortiesextrasokoke', (a, 1), f'tortiesokokeextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecolourssokoke', (a, 2), f'tortiesokoke{i}')
    sprites.make_group('tortiesextrasokoke', (a, 2), f'tortiesokokeextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecolourssokoke', (a, 3), f'tortiesokoke{i}')
    sprites.make_group('tortiesextrasokoke', (a, 3), f'tortiesokokeextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecolourssokoke', (a, 4), f'tortiesokoke{i}')
    sprites.make_group('tortiesextrasokoke', (a, 4), f'tortiesokokeextra{i}', sprites_y=2)
# agouti
for a, i in enumerate(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR']):
    sprites.make_group('tortiecoloursagouti', (a, 0), f'tortieagouti{i}')
    sprites.make_group('tortiesextraagouti', (a, 0), f'tortieagoutiextra{i}', sprites_y=2)
for a, i in enumerate(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR']):
    sprites.make_group('tortiecoloursagouti', (a, 1), f'tortieagouti{i}')
    sprites.make_group('tortiesextraagouti', (a, 1), f'tortieagoutiextra{i}', sprites_y=2)
for a, i in enumerate(['GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR']):
    sprites.make_group('tortiecoloursagouti', (a, 2), f'tortieagouti{i}')
    sprites.make_group('tortiesextraagouti', (a, 2), f'tortieagoutiextra{i}', sprites_y=2)
for a, i in enumerate(['DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR']):
    sprites.make_group('tortiecoloursagouti', (a, 3), f'tortieagouti{i}')
    sprites.make_group('tortiesextraagouti', (a, 3), f'tortieagoutiextra{i}', sprites_y=2)
for a, i in enumerate(['CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR']):
    sprites.make_group('tortiecoloursagouti', (a, 4), f'tortieagouti{i}')
    sprites.make_group('tortiesextraagouti', (a, 4), f'tortieagoutiextra{i}', sprites_y=2)

# SKINS
sprites.make_group('skin', (0, 0), 'skinBLACK')
sprites.make_group('skin', (1, 0), 'skinRED')
sprites.make_group('skin', (2, 0), 'skinPINK')
sprites.make_group('skin', (3, 0), 'skinDARKBROWN')
sprites.make_group('skin', (4, 0), 'skinBROWN')
sprites.make_group('skin', (5, 0), 'skinLIGHTBROWN')
sprites.make_group('skin', (0, 1), 'skinDARK')
sprites.make_group('skin', (1, 1), 'skinDARKGREY')
sprites.make_group('skin', (2, 1), 'skinGREY')
sprites.make_group('skin', (3, 1), 'skinDARKSALMON')
sprites.make_group('skin', (4, 1), 'skinSALMON')
sprites.make_group('skin', (5, 1), 'skinPEACH')
sprites.make_group('skin', (0, 2), 'skinDARKMARBLED')
sprites.make_group('skin', (1, 2), 'skinMARBLED')
sprites.make_group('skin', (2, 2), 'skinLIGHTMARBLED')
sprites.make_group('skin', (3, 2), 'skinDARKBLUE')
sprites.make_group('skin', (4, 2), 'skinBLUE')
sprites.make_group('skin', (5, 2), 'skinLIGHTBLUE')
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
sprites.make_group('skinextra', (3, 0), 'skinextraDARKBROWN', sprites_y=2)
sprites.make_group('skinextra', (4, 0), 'skinextraBROWN', sprites_y=2)
sprites.make_group('skinextra', (5, 0), 'skinextraLIGHTBROWN', sprites_y=2)
sprites.make_group('skinextra', (0, 1), 'skinextraDARK', sprites_y=2)
sprites.make_group('skinextra', (1, 1), 'skinextraDARKGREY', sprites_y=2)
sprites.make_group('skinextra', (2, 1), 'skinextraGREY', sprites_y=2)
sprites.make_group('skinextra', (3, 1), 'skinextraDARKSALMON', sprites_y=2)
sprites.make_group('skinextra', (4, 1), 'skinextraSALMON', sprites_y=2)
sprites.make_group('skinextra', (5, 1), 'skinextraPEACH', sprites_y=2)
sprites.make_group('skinextra', (0, 2), 'skinextraDARKMARBLED', sprites_y=2)
sprites.make_group('skinextra', (1, 2), 'skinextraMARBLED', sprites_y=2)
sprites.make_group('skinextra', (2, 2), 'skinextraLIGHTMARBLED', sprites_y=2)
sprites.make_group('skinextra', (3, 2), 'skinextraDARKBLUE', sprites_y=2)
sprites.make_group('skinextra', (4, 2), 'skinextraBLUE', sprites_y=2)
sprites.make_group('skinextra', (5, 2), 'skinextraLIGHTBLUE', sprites_y=2)

# tiles.make_group('dithered', (0, 0), 'terrain')
# tiles.make_group('dithered', (1, 0), 'terraintwo')

sprites.load_scars()
