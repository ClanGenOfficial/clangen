import pygame

try:
    import ujson
except ImportError:
    import json as ujson


class Sprites():
    cat_tints = {}
    white_patches_tints = {}

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

        try:
            with open("sprites/dicts/white_patches_tint.json", 'r') as read_file:
                Sprites.white_patches_tints = ujson.loads(read_file.read())
        except:
            print("ERROR: Reading White Patches Tints")

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

        for a, i in enumerate(["RAT BLACK", "RAT BROWN", "RAT CREAM"]):
            sprites.make_group('ratcessories', (a, 0), f'acc_wild{i}')
            sprites.make_group('ratcessoriesextra', (a, 0), f'acc_wildextra{i}', sprites_y=2)
        for a, i in enumerate(["RAT WHITE", "RAT GREY", "RAT HOODED"]):
            sprites.make_group('ratcessories', (a, 1), f'acc_wild{i}')
            sprites.make_group('ratcessoriesextra', (a, 1), f'acc_wildextra{i}', sprites_y=2) 

        for a, i in enumerate(["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"]):
            sprites.make_group('collars', (a, 0), f'collars{i}')
            sprites.make_group('collarsextra', (a, 0),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["GREEN", "RAINBOW", "BLACK", "SPIKES", "WHITE"]):
            sprites.make_group('collars', (a, 1), f'collars{i}')
            sprites.make_group('collarsextra', (a, 1),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINK", "PURPLE", "MULTI", "INDIGO"]):
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
                ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL"]):
            sprites.make_group('bellcollars', (a, 1), f'collars{i}')
            sprites.make_group('bellcollarsextra', (a, 1),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINKBELL", "PURPLEBELL", "MULTIBELL", "INDIGOBELL"]):
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
                ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW"]):
            sprites.make_group('bowcollars', (a, 1), f'collars{i}')
            sprites.make_group('bowcollarsextra', (a, 1),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW"]):
            sprites.make_group('bowcollars', (a, 2), f'collars{i}')
            sprites.make_group('bowcollarsextra', (a, 2),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate([
            "CRIMSONNYLON", "BLUENYLON", "YELLOWNYLON", "CYANNYLON", "REDNYLON",
            "LIMENYLON"
        ]):
            sprites.make_group('nyloncollars', (a, 0), f'collars{i}')
            sprites.make_group('nyloncollarsextra', (a, 0),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(
                ["GREENNYLON", "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON"]):
            sprites.make_group('nyloncollars', (a, 1), f'collars{i}')
            sprites.make_group('nyloncollarsextra', (a, 1),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINKNYLON", "PURPLENYLON", "MULTINYLON", "INDIGONYLON"]):
            sprites.make_group('nyloncollars', (a, 2), f'collars{i}')
            sprites.make_group('nyloncollarsextra', (a, 2),
                               f'collarsextra{i}',
                               sprites_y=2)

        for a, i in enumerate([
            "CRIMSONBC", "BLUEBC", "YELLOWBC", "CYANBC", "REDBC",
            "LIMEBC"
        ]):
            sprites.make_group('bloodcollars', (a, 0), f'collars{i}')
            sprites.make_group('bloodcollarsextra', (a, 0),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(
                ["GREENBC", "RAINBOWBC", "BLACKBC", "SPIKESBC"]):
            sprites.make_group('bloodcollars', (a, 1), f'collars{i}')
            sprites.make_group('bloodcollarsextra', (a, 1),
                               f'collarsextra{i}',
                               sprites_y=2)
        for a, i in enumerate(["PINKBC", "PURPLEBC", "MULTIBC"]):
            sprites.make_group('bloodcollars', (a, 2), f'collars{i}')
            sprites.make_group('bloodcollarsextra', (a, 2),
                               f'collarsextra{i}',
                               sprites_y=2)  

sprites = Sprites(50)
#tiles = Sprites(64)

for x in [
    'lineart','eyes', 'eyes2', 'eyesextra', 'eyes2extra', 'skin', 'skinextra', 'skin2', 'skin2extra', 'skin_sphynx', 'skinextra_sphynx',
    'scars', 'scarsextra', 'scarsdark', 'scarsdarkextra', 'Newscars', 'Newscarsextra', 'shaders', 'lineartdead',
    'lineartdf', 'eyes_df', 'eyesextra_df', 'singleB', 'singleBextra', 'singleR', 'singleRextra', 'singleWB', 'singleWBextra', 
    'shadersnewwhite', 'lightingnew', 'fademask', 'fadestarclan', 'fadedarkforest'

]:
    sprites.spritesheet(f"sprites/{x}.png", x)    
    
for x in [
    'whiteextra', 'whitenewextra', 'whitepatchesnew', 'whitepatches',
    'whitepatches3', 'whitepatches3extra', 'whitepatches4', 'whitepatches4extra',
    'whitepatchesmoss', 'whitemossextra', 'blackpatches', 'blackextra', 'blackpatchesnew',
    'blacknewextra', 'blackpatches3', 'blackpatches4', 'blackpatches3extra', 
    'blackpatches4extra', 'blackpatchesmoss', 'blackpatchesmossextra', 'skelepatches', 
    'skelepatchesextra', 'tortiepatchesmasks', 'tortiepatchesmasksB'

]:
    sprites.spritesheet(f"sprites/patches/{x}.png", x)   

for x in [
    'collars', 'collarsextra',
    'bellcollars', 'bellcollarsextra', 'bowcollars', 'bowcollarsextra',
    'medcatherbs', 'medcatherbsextra', 'bloodcollars', 'bloodcollarsextra',
    'ratcessories', 'ratcessoriesextra', 'nyloncollars', 'nyloncollarsextra'

]:
    sprites.spritesheet(f"sprites/accessories/{x}.png", x)    
    
for x in [
    'dobermanB', 'dobermanBextra', 'skeleB', 'skeleBextra', 'smokeB', 'smokeBextra', 'dobermanR', 'dobermanRextra', 
    'skeleR', 'skeleRextra', 'smokeR', 'smokeRextra', 'dobermanWB', 'dobermanWBextra', 'smokeWB', 
    'smokeWBextra', 'skeleWB', 'skeleWBextra', 'stainB', 'stainBextra', 'stainR', 'stainRextra', 'stainWB', 'stainWBextra',
    'ratR', 'ratRextra', 'ratB', 'ratBextra', 'ratWB', 'ratWBextra', 'skittyB', 'skittyBextra', 'skittyR', 'skittyRextra',
    'skittyWB', 'skittyWBextra'

]:
    sprites.spritesheet(f"sprites/solidbase/{x}.png", x)    
    
for x in [
    'bengalB', 'bengalBextra', 'mottledB', 'mottledBextra', 'rosetteB', 'rosetteBextra', 'snowflakeB', 
    'snowflakeBextra','speckledB', 'speckledBextra', 'bengalR', 'bengalRextra', 'mottledR', 'mottledRextra',
    'rosetteR', 'rosetteRextra', 'snowflakeR', 'snowflakeRextra', 'speckledR', 'speckledRextra', 'bengalWB', 'bengalWBextra', 
    'mottledWB', 'mottledWBextra', 'rosetteWB', 'rosetteWBextra', 'snowflakeWB', 'snowflakeWBextra', 'speckledWB', 'speckledWBextra'

]:
    sprites.spritesheet(f"sprites/speckled/{x}.png", x)    
    
for x in [
    'ghostB', 'ghostBextra', 'marbleB', 'marbleBextra', 'merleB', 'merleBextra', 'tabbyB', 'tabbyBextra', 
    'tickedB', 'tickedBextra', 'ghostR', 'ghostRextra', 'marbleR', 'marbleRextra', 'merleR', 'merleRextra', 
    'tabbyR', 'tabbyRextra', 'tickedR', 'tickedRextra', 'ghostWB', 'ghostWBextra', 'marbleWB', 'marbleWBextra', 
    'merleWB', 'merleWBextra', 'tabbyWB', 'tabbyWBextra', 'tickedWB', 'tickedWBextra', 'classicB', 'classicBextra',
    'classicR', 'classicRextra', 'classicWB', 'classicWBextra', 'mackerelB', 'mackerelBextra', 'mackerelR', 
    'mackerelRextra', 'mackerelWB', 'mackerelWBextra', 'sokokeB', 'sokokeBextra', 'sokokeR', 'sokokeRextra',
    'sokokeWB', 'sokokeWBextra', 'agoutiB', 'agoutiBextra', 'agoutiR', 'agoutiRextra', 'agoutiWB', 'agoutiWBextra',
    'charcoalB', 'charcoalBextra', 'charcoalR', 'charcoalRextra', 'charcoalWB', 'charcoalWBextra', 'backedB', 'backedBextra',
    'backedR', 'backedRextra', 'backedWB', 'backedWBextra', 'hoodedB', 'hoodedBextra', 'hoodedR', 'hoodedRextra', 'hoodedWB',
    'hoodedWBextra'

]:
    sprites.spritesheet(f"sprites/tabby/{x}.png", x)  

for sprite in [
    'Paralyzed_lineart', 'singleparalyzed', 'speckledparalyzed',
    'tabbyparalyzed', 'whiteallparalyzed', 'eyesparalyzed',
    'tabbyparalyzed', 'tortiesparalyzed', 'scarsparalyzed', 'skinparalyzed',
    'medcatherbsparalyzed'

]:
    sprites.spritesheet(f"sprites/paralyzed/{sprite}.png", sprite)

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

# Fading Fog
sprites.make_group('fademask', (0, 0), 'fademask', sprites_y=15)
sprites.make_group('fadestarclan', (0, 0), 'fadestarclan', sprites_y=15)
sprites.make_group('fadedarkforest', (0, 0), 'fadedf', sprites_y=15)

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

# white patches + black patches
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
for a, i in enumerate(['FULLBLACK', 'BLACKANY', 'BLACKTUXEDO', 'BLACKLITTLE', 'BLACKCOLOURPOINT', 'BLACKVAN', 'BLACKANY2']):
    sprites.make_group('blackpatches', (a, 0), f'white{i}')
    sprites.make_group('blackextra', (a, 0), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate(['BONEEAR', 'BLACKBROKEN', 'BLACKLIGHTTUXEDO', 'BLACKBUZZARDFANG', 'BAGDOLL',
        'BLACKLIGHTSONG', 'BLACKVITILIGO']):
    sprites.make_group('blackpatches', (a, 1), f'white{i}')
    sprites.make_group('blackextra', (a, 1), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate(['BLACKANYCREAMY', 'BLACKTUXEDOCREAMY', 'BLACKLITTLECREAMY', 'BLACKCOLOURPOINTCREAMY', 'BLACKVANCREAMY', 'BLACKANY2CREAMY']):
    sprites.make_group('blackpatchesnew', (a, 0), f'white{i}')
    sprites.make_group('blacknewextra', (a, 0), f'whiteextra{i}', sprites_y=2)
    
# extra
sprites.make_group('whitepatches', (0, 2), 'whiteEXTRA')
sprites.make_group('whiteextra', (0, 2), 'whiteextraEXTRA', sprites_y=2)
sprites.make_group('blackpatches', (0, 2), 'whiteBLACKEXTRA')
sprites.make_group('blackextra', (0, 2), 'whiteextraBLACKEXTRA', sprites_y=2)

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
for a, i in enumerate(
        ['BLACKTIP', 'BLACKFANCY', 'BLACKFRECKLES', 'BLACKRINGTAIL', 'BLACKHALFFACE', 'BLACKPANTS2', 'BLACKGOATEE', 'BLACKVITILIGO2']):
    sprites.make_group('blackpatches3', (a, 0), f'white{i}')
    sprites.make_group('blackpatches3extra', (a, 0), f'whiteextra{i}', sprites_y=2)    
for a, i in enumerate(['BLACKTAIL', 'BLACKBLAZE', 'BLACKPRINCE', 'BLACKBIB', 'BLACKVEE', 'BLACKUNDERS', 'BLACKPAWS', 'BLACKMITAINE']):
    sprites.make_group('blackpatches3', (a, 1), f'white{i}')
    sprites.make_group('blackpatches3extra', (a, 1), f'whiteextra{i}', sprites_y=2) 
for a, i in enumerate(
        ['BLACKFAROFA', 'BLACKDAMIEN', 'BLACKMISTER', 'BLACKBELLY', 'BLACKTAILTIP', 'BLACKTOES', 'BLACKBROKENBLAZE', 'BLACKSCOURGE']):
    sprites.make_group('blackpatches3', (a, 2), f'white{i}')
    sprites.make_group('blackpatches3extra', (a, 2), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate(
        ['BLACKAPRON', 'BLACKCAPSADDLE', 'BLACKMASKMANTLE', 'BLACKSQUEAKS', 'STARBLACK', 'BLACKTOESTAIL', 'BLACKRAVENPAW', 'BLACKHONEY']):
    sprites.make_group('blackpatches3', (a, 3), f'white{i}')
    sprites.make_group('blackpatches3extra', (a, 3), f'whiteextra{i}', sprites_y=2)    

# beejeans white patches + perrio's point marks
for a, i in enumerate(['PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'PIEBALD', 'CURVED']):
    sprites.make_group('whitepatches4', (a, 0), 'white' + i)
    sprites.make_group('whitepatches4extra', (a, 0), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['HEART', 'LILTWO', 'GLASS', 'MOORISH', 'SEPIAPOINT', 'MINKPOINT', 'SEALPOINT']):
    sprites.make_group('whitepatches4', (a, 1), 'white' + i)
    sprites.make_group('whitepatches4extra', (a, 1), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['MAO', 'LUNA', 'CHESTSPECK', 'WINGS', 'PAINTED', 'HEART2', 'BLACKSTAR']):
    sprites.make_group('whitepatches4', (a, 2), 'white' + i)
    sprites.make_group('whitepatches4extra', (a, 2), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['BLACKPANTS', 'BLACKREVERSEPANTS', 'BLACKSKUNK', 'BLACKKARPATI', 'HALFBLACK', 'BLACKAPPALOOSA', 'BLACKPIEBALD', 'BLACKCURVED']):
    sprites.make_group('blackpatches4', (a, 0), 'white' + i)
    sprites.make_group('blackpatches4extra', (a, 0), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['BLACKHEART', 'BLACKLILTWO', 'BLACKGLASS', 'BLACKMOORISH', 'BLACKPOINTMARK']):
    sprites.make_group('blackpatches4', (a, 1), 'white' + i)
    sprites.make_group('blackpatches4extra', (a, 1), 'whiteextra' + i, sprites_y=2)     
for a, i in enumerate(['BLACKMAO', 'BLACKLUNA', 'BLACKCHESTSPECK', 'WINGSBLACK', 'BLACKPAINTED', 'BLACKHEART2', 'REVBLACKSTAR']):
    sprites.make_group('blackpatches4', (a, 2), 'white' + i)
    sprites.make_group('blackpatches4extra', (a, 2), 'whiteextra' + i, sprites_y=2)    
    
#skeletons
for a, i in enumerate(['SKELEBLACK', 'SKELEWHITE']):
    sprites.make_group('skelepatches', (a, 0), f'white{i}')
    sprites.make_group('skelepatchesextra', (a, 0), f'whiteextra{i}', sprites_y=2) 
    
# moss white patches
for a, i in enumerate(['SNOWSHOE', 'VENUS', 'SNOWBOOT', 'CHANCE', 'MOSSCLAW', 'DAPPLED', 'NIGHTMIST', 'HAWK']):
    sprites.make_group('whitepatchesmoss', (a, 0), 'white' + i)
    sprites.make_group('whitemossextra', (a, 0), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['SHADOWSIGHT', 'TWIST', 'RETSUKO', 'OKAPI', 'FRECKLEMASK', 'MOTH']):
    sprites.make_group('whitepatchesmoss', (a, 1), 'white' + i)
    sprites.make_group('whitemossextra', (a, 1), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['SOOTSHOE', 'BLACKVENUS', 'SOOTBOOT', 'BLACKCHANCE', 'BLACKMOSSCLAW', 'BLACKDAPPLED', 'BLACKNIGHTMIST', 'BLACKHAWK']):
    sprites.make_group('blackpatchesmoss', (a, 0), 'white' + i)
    sprites.make_group('blackpatchesmossextra', (a, 0), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['BLACKSHADOWSIGHT', 'BLACKTWIST', 'BLACKRETSUKO', 'BLACKOKAPI', 'BLACKFRECKLEMASK', 'BLACKMOTH']):
    sprites.make_group('blackpatchesmoss', (a, 1), 'white' + i)
    sprites.make_group('blackpatchesmossextra', (a, 1), 'whiteextra' + i, sprites_y=2)    

# single (solid)
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('singleB', (a, 0), f'single{i}')
    sprites.make_group('singleBextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('singleB', (a, 1), f'single{i}')
    sprites.make_group('singleBextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('singleB', (a, 2), f'single{i}')
    sprites.make_group('singleBextra', (a, 2), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('singleB', (a, 3), f'single{i}')
    sprites.make_group('singleBextra', (a, 3), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('singleR', (a, 0), f'single{i}')
    sprites.make_group('singleRextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('singleR', (a, 1), f'single{i}')
    sprites.make_group('singleRextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('singleR', (a, 2), f'single{i}')
    sprites.make_group('singleRextra', (a, 2), f'singleextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('singleR', (a, 3), f'single{i}')
    sprites.make_group('singleRextra', (a, 3), f'singleextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('singleWB', (a, 0), f'single{i}')
    sprites.make_group('singleWBextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('singleWB', (a, 1), f'single{i}')
    sprites.make_group('singleWBextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('singleWB', (a, 2), f'single{i}')
    sprites.make_group('singleWBextra', (a, 2), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('singleWB', (a, 3), f'single{i}')
    sprites.make_group('singleWBextra', (a, 3), f'singleextra{i}', sprites_y=2)
# tabby
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('tabbyB', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyBextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('tabbyB', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyBextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('tabbyB', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyBextra', (a, 2), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('tabbyB', (a, 3), f'tabby{i}')
    sprites.make_group('tabbyBextra', (a, 3), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('tabbyR', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyRextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('tabbyR', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyRextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('tabbyR', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyRextra', (a, 2), f'tabbyextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('tabbyR', (a, 3), f'tabby{i}')
    sprites.make_group('tabbyRextra', (a, 3), f'tabbyextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('tabbyWB', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyWBextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('tabbyWB', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyWBextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('tabbyWB', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyWBextra', (a, 2), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('tabbyWB', (a, 3), f'tabby{i}')
    sprites.make_group('tabbyWBextra', (a, 3), f'tabbyextra{i}', sprites_y=2)
# marbled
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('marbleB', (a, 0), f'marbled{i}')
    sprites.make_group('marbleBextra', (a, 0), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('marbleB', (a, 1), f'marbled{i}')
    sprites.make_group('marbleBextra', (a, 1), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('marbleB', (a, 2), f'marbled{i}')
    sprites.make_group('marbleBextra', (a, 2), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('marbleB', (a, 3), f'marbled{i}')
    sprites.make_group('marbleBextra', (a, 3), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('marbleR', (a, 0), f'marbled{i}')
    sprites.make_group('marbleRextra', (a, 0), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('marbleR', (a, 1), f'marbled{i}')
    sprites.make_group('marbleRextra', (a, 1), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('marbleR', (a, 2), f'marbled{i}')
    sprites.make_group('marbleRextra', (a, 2), f'marbledextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('marbleR', (a, 3), f'marbled{i}')
    sprites.make_group('marbleRextra', (a, 3), f'marbledextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('marbleWB', (a, 0), f'marbled{i}')
    sprites.make_group('marbleWBextra', (a, 0), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('marbleWB', (a, 1), f'marbled{i}')
    sprites.make_group('marbleWBextra', (a, 1), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('marbleWB', (a, 2), f'marbled{i}')
    sprites.make_group('marbleWBextra', (a, 2), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('marbleWB', (a, 3), f'marbled{i}')
    sprites.make_group('marbleWBextra', (a, 3), f'marbledextra{i}', sprites_y=2)
# rosette
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('rosetteB', (a, 0), f'rosette{i}')
    sprites.make_group('rosetteBextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('rosetteB', (a, 1), f'rosette{i}')
    sprites.make_group('rosetteBextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('rosetteB', (a, 2), f'rosette{i}')
    sprites.make_group('rosetteBextra', (a, 2), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('rosetteB', (a, 3), f'rosette{i}')
    sprites.make_group('rosetteBextra', (a, 3), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('rosetteR', (a, 0), f'rosette{i}')
    sprites.make_group('rosetteRextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('rosetteR', (a, 1), f'rosette{i}')
    sprites.make_group('rosetteRextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('rosetteR', (a, 2), f'rosette{i}')
    sprites.make_group('rosetteRextra', (a, 2), f'rosetteextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('rosetteR', (a, 3), f'rosette{i}')
    sprites.make_group('rosetteRextra', (a, 3), f'rosetteextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('rosetteWB', (a, 0), f'rosette{i}')
    sprites.make_group('rosetteWBextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('rosetteWB', (a, 1), f'rosette{i}')
    sprites.make_group('rosetteWBextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('rosetteWB', (a, 2), f'rosette{i}')
    sprites.make_group('rosetteWBextra', (a, 2), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('rosetteWB', (a, 3), f'rosette{i}')
    sprites.make_group('rosetteWBextra', (a, 3), f'rosetteextra{i}', sprites_y=2)
# smoke
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('smokeB', (a, 0), f'smoke{i}')
    sprites.make_group('smokeBextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('smokeB', (a, 1), f'smoke{i}')
    sprites.make_group('smokeBextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('smokeB', (a, 2), f'smoke{i}')
    sprites.make_group('smokeBextra', (a, 2), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('smokeB', (a, 3), f'smoke{i}')
    sprites.make_group('smokeBextra', (a, 3), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('smokeR', (a, 0), f'smoke{i}')
    sprites.make_group('smokeRextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('smokeR', (a, 1), f'smoke{i}')
    sprites.make_group('smokeRextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('smokeR', (a, 2), f'smoke{i}')
    sprites.make_group('smokeRextra', (a, 2), f'smokeextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('smokeR', (a, 3), f'smoke{i}')
    sprites.make_group('smokeRextra', (a, 3), f'smokeextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('smokeWB', (a, 0), f'smoke{i}')
    sprites.make_group('smokeWBextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('smokeWB', (a, 1), f'smoke{i}')
    sprites.make_group('smokeWBextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('smokeWB', (a, 2), f'smoke{i}')
    sprites.make_group('smokeWBextra', (a, 2), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('smokeWB', (a, 3), f'smoke{i}')
    sprites.make_group('smokeWBextra', (a, 3), f'smokeextra{i}', sprites_y=2)
# ticked
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('tickedB', (a, 0), f'ticked{i}')
    sprites.make_group('tickedBextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('tickedB', (a, 1), f'ticked{i}')
    sprites.make_group('tickedBextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('tickedB', (a, 2), f'ticked{i}')
    sprites.make_group('tickedBextra', (a, 2), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('tickedB', (a, 3), f'ticked{i}')
    sprites.make_group('tickedBextra', (a, 3), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('tickedR', (a, 0), f'ticked{i}')
    sprites.make_group('tickedRextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('tickedR', (a, 1), f'ticked{i}')
    sprites.make_group('tickedRextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('tickedR', (a, 2), f'ticked{i}')
    sprites.make_group('tickedRextra', (a, 2), f'tickedextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('tickedR', (a, 3), f'ticked{i}')
    sprites.make_group('tickedRextra', (a, 3), f'tickedextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('tickedWB', (a, 0), f'ticked{i}')
    sprites.make_group('tickedWBextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('tickedWB', (a, 1), f'ticked{i}')
    sprites.make_group('tickedWBextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('tickedWB', (a, 2), f'ticked{i}')
    sprites.make_group('tickedWBextra', (a, 2), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('tickedWB', (a, 3), f'ticked{i}')
    sprites.make_group('tickedWBextra', (a, 3), f'tickedextra{i}', sprites_y=2)
# speckled
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('speckledB', (a, 0), f'speckled{i}')
    sprites.make_group('speckledBextra', (a, 0), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('speckledB', (a, 1), f'speckled{i}')
    sprites.make_group('speckledBextra', (a, 1), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('speckledB', (a, 2), f'speckled{i}')
    sprites.make_group('speckledBextra', (a, 2), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('speckledB', (a, 3), f'speckled{i}')
    sprites.make_group('speckledBextra', (a, 3), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('speckledR', (a, 0), f'speckled{i}')
    sprites.make_group('speckledRextra', (a, 0), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('speckledR', (a, 1), f'speckled{i}')
    sprites.make_group('speckledRextra', (a, 1), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('speckledR', (a, 2), f'speckled{i}')
    sprites.make_group('speckledRextra', (a, 2), f'speckledextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('speckledR', (a, 3), f'speckled{i}')
    sprites.make_group('speckledRextra', (a, 3), f'speckledextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('speckledWB', (a, 0), f'speckled{i}')
    sprites.make_group('speckledWBextra', (a, 0), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('speckledWB', (a, 1), f'speckled{i}')
    sprites.make_group('speckledWBextra', (a, 1), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('speckledWB', (a, 2), f'speckled{i}')
    sprites.make_group('speckledWBextra', (a, 2), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('speckledWB', (a, 3), f'speckled{i}')
    sprites.make_group('speckledWBextra', (a, 3), f'speckledextra{i}', sprites_y=2)
# bengal
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('bengalB', (a, 0), f'bengal{i}')
    sprites.make_group('bengalBextra', (a, 0), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('bengalB', (a, 1), f'bengal{i}')
    sprites.make_group('bengalBextra', (a, 1), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('bengalB', (a, 2), f'bengal{i}')
    sprites.make_group('bengalBextra', (a, 2), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('bengalB', (a, 3), f'bengal{i}')
    sprites.make_group('bengalBextra', (a, 3), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('bengalR', (a, 0), f'bengal{i}')
    sprites.make_group('bengalRextra', (a, 0), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('bengalR', (a, 1), f'bengal{i}')
    sprites.make_group('bengalRextra', (a, 1), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('bengalR', (a, 2), f'bengal{i}')
    sprites.make_group('bengalRextra', (a, 2), f'bengalextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('bengalR', (a, 3), f'bengal{i}')
    sprites.make_group('bengalRextra', (a, 3), f'bengalextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('bengalWB', (a, 0), f'bengal{i}')
    sprites.make_group('bengalWBextra', (a, 0), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('bengalWB', (a, 1), f'bengal{i}')
    sprites.make_group('bengalWBextra', (a, 1), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('bengalWB', (a, 2), f'bengal{i}')
    sprites.make_group('bengalWBextra', (a, 2), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('bengalWB', (a, 3), f'bengal{i}')
    sprites.make_group('bengalWBextra', (a, 3), f'bengalextra{i}', sprites_y=2)
# mackerel
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('mackerelB', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelBextra', (a, 0), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('mackerelB', (a, 1), f'mackerel{i}')
    sprites.make_group('mackerelBextra', (a, 1), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('mackerelB', (a, 2), f'mackerel{i}')
    sprites.make_group('mackerelBextra', (a, 2), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('mackerelB', (a, 3), f'mackerel{i}')
    sprites.make_group('mackerelBextra', (a, 3), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('mackerelR', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelRextra', (a, 0), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('mackerelR', (a, 1), f'mackerel{i}')
    sprites.make_group('mackerelRextra', (a, 1), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('mackerelR', (a, 2), f'mackerel{i}')
    sprites.make_group('mackerelRextra', (a, 2), f'mackerelextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('mackerelR', (a, 3), f'mackerel{i}')
    sprites.make_group('mackerelRextra', (a, 3), f'mackerelextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('mackerelWB', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelWBextra', (a, 0), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('mackerelWB', (a, 1), f'mackerel{i}')
    sprites.make_group('mackerelWBextra', (a, 1), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('mackerelWB', (a, 2), f'mackerel{i}')
    sprites.make_group('mackerelWBextra', (a, 2), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('mackerelWB', (a, 3), f'mackerel{i}')
    sprites.make_group('mackerelWBextra', (a, 3), f'mackerelextra{i}', sprites_y=2)
# classic
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('classicB', (a, 0), f'classic{i}')
    sprites.make_group('classicBextra', (a, 0), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('classicB', (a, 1), f'classic{i}')
    sprites.make_group('classicBextra', (a, 1), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('classicB', (a, 2), f'classic{i}')
    sprites.make_group('classicBextra', (a, 2), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('classicB', (a, 3), f'classic{i}')
    sprites.make_group('classicBextra', (a, 3), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('classicR', (a, 0), f'classic{i}')
    sprites.make_group('classicRextra', (a, 0), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('classicR', (a, 1), f'classic{i}')
    sprites.make_group('classicRextra', (a, 1), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('classicR', (a, 2), f'classic{i}')
    sprites.make_group('classicRextra', (a, 2), f'classicextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('classicR', (a, 3), f'classic{i}')
    sprites.make_group('classicRextra', (a, 3), f'classicextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('classicWB', (a, 0), f'classic{i}')
    sprites.make_group('classicWBextra', (a, 0), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('classicWB', (a, 1), f'classic{i}')
    sprites.make_group('classicWBextra', (a, 1), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('classicWB', (a, 2), f'classic{i}')
    sprites.make_group('classicWBextra', (a, 2), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('classicWB', (a, 3), f'classic{i}')
    sprites.make_group('classicWBextra', (a, 3), f'classicextra{i}', sprites_y=2)
# sokoke
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('sokokeB', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokeBextra', (a, 0), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('sokokeB', (a, 1), f'sokoke{i}')
    sprites.make_group('sokokeBextra', (a, 1), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('sokokeB', (a, 2), f'sokoke{i}')
    sprites.make_group('sokokeBextra', (a, 2), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('sokokeB', (a, 3), f'sokoke{i}')
    sprites.make_group('sokokeBextra', (a, 3), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('sokokeR', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokeRextra', (a, 0), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('sokokeR', (a, 1), f'sokoke{i}')
    sprites.make_group('sokokeRextra', (a, 1), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('sokokeR', (a, 2), f'sokoke{i}')
    sprites.make_group('sokokeRextra', (a, 2), f'sokokeextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('sokokeR', (a, 3), f'sokoke{i}')
    sprites.make_group('sokokeRextra', (a, 3), f'sokokeextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('sokokeWB', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokeWBextra', (a, 0), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('sokokeWB', (a, 1), f'sokoke{i}')
    sprites.make_group('sokokeWBextra', (a, 1), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('sokokeWB', (a, 2), f'sokoke{i}')
    sprites.make_group('sokokeWBextra', (a, 2), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('sokokeWB', (a, 3), f'sokoke{i}')
    sprites.make_group('sokokeWBextra', (a, 3), f'sokokeextra{i}', sprites_y=2)
# agouti
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('agoutiB', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiBextra', (a, 0), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('agoutiB', (a, 1), f'agouti{i}')
    sprites.make_group('agoutiBextra', (a, 1), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('agoutiB', (a, 2), f'agouti{i}')
    sprites.make_group('agoutiBextra', (a, 2), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('agoutiB', (a, 3), f'agouti{i}')
    sprites.make_group('agoutiBextra', (a, 3), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('agoutiR', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiRextra', (a, 0), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('agoutiR', (a, 1), f'agouti{i}')
    sprites.make_group('agoutiRextra', (a, 1), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('agoutiR', (a, 2), f'agouti{i}')
    sprites.make_group('agoutiRextra', (a, 2), f'agoutiextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('agoutiR', (a, 3), f'agouti{i}')
    sprites.make_group('agoutiRextra', (a, 3), f'agoutiextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('agoutiWB', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiWBextra', (a, 0), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('agoutiWB', (a, 1), f'agouti{i}')
    sprites.make_group('agoutiWBextra', (a, 1), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('agoutiWB', (a, 2), f'agouti{i}')
    sprites.make_group('agoutiWBextra', (a, 2), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('agoutiWB', (a, 3), f'agouti{i}')
    sprites.make_group('agoutiWBextra', (a, 3), f'agoutiextra{i}', sprites_y=2)
# backed
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('backedB', (a, 0), f'backed{i}')
    sprites.make_group('backedBextra', (a, 0), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('backedB', (a, 1), f'backed{i}')
    sprites.make_group('backedBextra', (a, 1), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('backedB', (a, 2), f'backed{i}')
    sprites.make_group('backedBextra', (a, 2), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('backedB', (a, 3), f'backed{i}')
    sprites.make_group('backedBextra', (a, 3), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('backedR', (a, 0), f'backed{i}')
    sprites.make_group('backedRextra', (a, 0), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('backedR', (a, 1), f'backed{i}')
    sprites.make_group('backedRextra', (a, 1), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('backedR', (a, 2), f'backed{i}')
    sprites.make_group('backedRextra', (a, 2), f'backedextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('backedR', (a, 3), f'backed{i}')
    sprites.make_group('backedRextra', (a, 3), f'backedextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('backedWB', (a, 0), f'backed{i}')
    sprites.make_group('backedWBextra', (a, 0), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('backedWB', (a, 1), f'backed{i}')
    sprites.make_group('backedWBextra', (a, 1), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('backedWB', (a, 2), f'backed{i}')
    sprites.make_group('backedWBextra', (a, 2), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('backedWB', (a, 3), f'backed{i}')
    sprites.make_group('backedWBextra', (a, 3), f'backedextra{i}', sprites_y=2)
#doberman
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('dobermanB', (a, 0), f'doberman{i}')
    sprites.make_group('dobermanBextra', (a, 0), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('dobermanB', (a, 1), f'doberman{i}')
    sprites.make_group('dobermanBextra', (a, 1), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('dobermanB', (a, 2), f'doberman{i}')
    sprites.make_group('dobermanBextra', (a, 2), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('dobermanB', (a, 3), f'doberman{i}')
    sprites.make_group('dobermanBextra', (a, 3), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('dobermanR', (a, 0), f'doberman{i}')
    sprites.make_group('dobermanRextra', (a, 0), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('dobermanR', (a, 1), f'doberman{i}')
    sprites.make_group('dobermanRextra', (a, 1), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('dobermanR', (a, 2), f'doberman{i}')
    sprites.make_group('dobermanRextra', (a, 2), f'dobermanextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('dobermanR', (a, 3), f'doberman{i}')
    sprites.make_group('dobermanRextra', (a, 3), f'dobermanextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('dobermanWB', (a, 0), f'doberman{i}')
    sprites.make_group('dobermanWBextra', (a, 0), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('dobermanWB', (a, 1), f'doberman{i}')
    sprites.make_group('dobermanWBextra', (a, 1), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('dobermanWB', (a, 2), f'doberman{i}')
    sprites.make_group('dobermanWBextra', (a, 2), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('dobermanWB', (a, 3), f'doberman{i}')
    sprites.make_group('dobermanWBextra', (a, 3), f'dobermanextra{i}', sprites_y=2)
# skele
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('skeleB', (a, 0), f'skele{i}')
    sprites.make_group('skeleBextra', (a, 0), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('skeleB', (a, 1), f'skele{i}')
    sprites.make_group('skeleBextra', (a, 1), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('skeleB', (a, 2), f'skele{i}')
    sprites.make_group('skeleBextra', (a, 2), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('skeleB', (a, 3), f'skele{i}')
    sprites.make_group('skeleBextra', (a, 3), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('skeleR', (a, 0), f'skele{i}')
    sprites.make_group('skeleRextra', (a, 0), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('skeleR', (a, 1), f'skele{i}')
    sprites.make_group('skeleRextra', (a, 1), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('skeleR', (a, 2), f'skele{i}')
    sprites.make_group('skeleRextra', (a, 2), f'skeleextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('skeleR', (a, 3), f'skele{i}')
    sprites.make_group('skeleRextra', (a, 3), f'skeleextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('skeleWB', (a, 0), f'skele{i}')
    sprites.make_group('skeleWBextra', (a, 0), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('skeleWB', (a, 1), f'skele{i}')
    sprites.make_group('skeleWBextra', (a, 1), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('skeleWB', (a, 2), f'skele{i}')
    sprites.make_group('skeleWBextra', (a, 2), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('skeleWB', (a, 3), f'skele{i}')
    sprites.make_group('skeleWBextra', (a, 3), f'skeleextra{i}', sprites_y=2)
#stain
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('stainB', (a, 0), f'stain{i}')
    sprites.make_group('stainBextra', (a, 0), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('stainB', (a, 1), f'stain{i}')
    sprites.make_group('stainBextra', (a, 1), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('stainB', (a, 2), f'stain{i}')
    sprites.make_group('stainBextra', (a, 2), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('stainB', (a, 3), f'stain{i}')
    sprites.make_group('stainBextra', (a, 3), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('stainR', (a, 0), f'stain{i}')
    sprites.make_group('stainRextra', (a, 0), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('stainR', (a, 1), f'stain{i}')
    sprites.make_group('stainRextra', (a, 1), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('stainR', (a, 2), f'stain{i}')
    sprites.make_group('stainRextra', (a, 2), f'stainextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('stainR', (a, 3), f'stain{i}')
    sprites.make_group('stainRextra', (a, 3), f'stainextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('stainWB', (a, 0), f'stain{i}')
    sprites.make_group('stainWBextra', (a, 0), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('stainWB', (a, 1), f'stain{i}')
    sprites.make_group('stainWBextra', (a, 1), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('stainWB', (a, 2), f'stain{i}')
    sprites.make_group('stainWBextra', (a, 2), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('stainWB', (a, 3), f'stain{i}')
    sprites.make_group('stainWBextra', (a, 3), f'stainextra{i}', sprites_y=2)
#mottled
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('mottledB', (a, 0), f'mottled{i}')
    sprites.make_group('mottledBextra', (a, 0), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('mottledB', (a, 1), f'mottled{i}')
    sprites.make_group('mottledBextra', (a, 1), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('mottledB', (a, 2), f'mottled{i}')
    sprites.make_group('mottledBextra', (a, 2), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('mottledB', (a, 3), f'mottled{i}')
    sprites.make_group('mottledBextra', (a, 3), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('mottledR', (a, 0), f'mottled{i}')
    sprites.make_group('mottledRextra', (a, 0), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('mottledR', (a, 1), f'mottled{i}')
    sprites.make_group('mottledRextra', (a, 1), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('mottledR', (a, 2), f'mottled{i}')
    sprites.make_group('mottledRextra', (a, 2), f'mottledextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('mottledR', (a, 3), f'mottled{i}')
    sprites.make_group('mottledRextra', (a, 3), f'mottledextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('mottledWB', (a, 0), f'mottled{i}')
    sprites.make_group('mottledWBextra', (a, 0), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('mottledWB', (a, 1), f'mottled{i}')
    sprites.make_group('mottledWBextra', (a, 1), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('mottledWB', (a, 2), f'mottled{i}')
    sprites.make_group('mottledWBextra', (a, 2), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('mottledWB', (a, 3), f'mottled{i}')
    sprites.make_group('mottledWBextra', (a, 3), f'mottledextra{i}', sprites_y=2)
# snowflake
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('snowflakeB', (a, 0), f'snowflake{i}')
    sprites.make_group('snowflakeBextra', (a, 0), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('snowflakeB', (a, 1), f'snowflake{i}')
    sprites.make_group('snowflakeBextra', (a, 1), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('snowflakeB', (a, 2), f'snowflake{i}')
    sprites.make_group('snowflakeBextra', (a, 2), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('snowflakeB', (a, 3), f'snowflake{i}')
    sprites.make_group('snowflakeBextra', (a, 3), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('snowflakeR', (a, 0), f'snowflake{i}')
    sprites.make_group('snowflakeRextra', (a, 0), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('snowflakeR', (a, 1), f'snowflake{i}')
    sprites.make_group('snowflakeRextra', (a, 1), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('snowflakeR', (a, 2), f'snowflake{i}')
    sprites.make_group('snowflakeRextra', (a, 2), f'snowflakeextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('snowflakeR', (a, 3), f'snowflake{i}')
    sprites.make_group('snowflakeRextra', (a, 3), f'snowflakeextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('snowflakeWB', (a, 0), f'snowflake{i}')
    sprites.make_group('snowflakeWBextra', (a, 0), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('snowflakeWB', (a, 1), f'snowflake{i}')
    sprites.make_group('snowflakeWBextra', (a, 1), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('snowflakeWB', (a, 2), f'snowflake{i}')
    sprites.make_group('snowflakeWBextra', (a, 2), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('snowflakeWB', (a, 3), f'snowflake{i}')
    sprites.make_group('snowflakeWBextra', (a, 3), f'snowflakeextra{i}', sprites_y=2)
#charcoal
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('charcoalB', (a, 0), f'charcoal{i}')
    sprites.make_group('charcoalBextra', (a, 0), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('charcoalB', (a, 1), f'charcoal{i}')
    sprites.make_group('charcoalBextra', (a, 1), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('charcoalB', (a, 2), f'charcoal{i}')
    sprites.make_group('charcoalBextra', (a, 2), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('charcoalB', (a, 3), f'charcoal{i}')
    sprites.make_group('charcoalBextra', (a, 3), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('charcoalR', (a, 0), f'charcoal{i}')
    sprites.make_group('charcoalRextra', (a, 0), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('charcoalR', (a, 1), f'charcoal{i}')
    sprites.make_group('charcoalRextra', (a, 1), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('charcoalR', (a, 2), f'charcoal{i}')
    sprites.make_group('charcoalRextra', (a, 2), f'charcoalextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('charcoalR', (a, 3), f'charcoal{i}')
    sprites.make_group('charcoalRextra', (a, 3), f'charcoalextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('charcoalWB', (a, 0), f'charcoal{i}')
    sprites.make_group('charcoalWBextra', (a, 0), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('charcoalWB', (a, 1), f'charcoal{i}')
    sprites.make_group('charcoalWBextra', (a, 1), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('charcoalWB', (a, 2), f'charcoal{i}')
    sprites.make_group('charcoalWBextra', (a, 2), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('charcoalWB', (a, 3), f'charcoal{i}')
    sprites.make_group('charcoalWBextra', (a, 3), f'charcoalextra{i}', sprites_y=2)
#ghost
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('ghostB', (a, 0), f'ghost{i}')
    sprites.make_group('ghostBextra', (a, 0), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('ghostB', (a, 1), f'ghost{i}')
    sprites.make_group('ghostBextra', (a, 1), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('ghostB', (a, 2), f'ghost{i}')
    sprites.make_group('ghostBextra', (a, 2), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('ghostB', (a, 3), f'ghost{i}')
    sprites.make_group('ghostBextra', (a, 3), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('ghostR', (a, 0), f'ghost{i}')
    sprites.make_group('ghostRextra', (a, 0), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('ghostR', (a, 1), f'ghost{i}')
    sprites.make_group('ghostRextra', (a, 1), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('ghostR', (a, 2), f'ghost{i}')
    sprites.make_group('ghostRextra', (a, 2), f'ghostextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('ghostR', (a, 3), f'ghost{i}')
    sprites.make_group('ghostRextra', (a, 3), f'ghostextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('ghostWB', (a, 0), f'ghost{i}')
    sprites.make_group('ghostWBextra', (a, 0), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('ghostWB', (a, 1), f'ghost{i}')
    sprites.make_group('ghostWBextra', (a, 1), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('ghostWB', (a, 2), f'ghost{i}')
    sprites.make_group('ghostWBextra', (a, 2), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('ghostWB', (a, 3), f'ghost{i}')
    sprites.make_group('ghostWBextra', (a, 3), f'ghostextra{i}', sprites_y=2)
#merle
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('merleB', (a, 0), f'merle{i}')
    sprites.make_group('merleBextra', (a, 0), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('merleB', (a, 1), f'merle{i}')
    sprites.make_group('merleBextra', (a, 1), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('merleB', (a, 2), f'merle{i}')
    sprites.make_group('merleBextra', (a, 2), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('merleB', (a, 3), f'merle{i}')
    sprites.make_group('merleBextra', (a, 3), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('merleR', (a, 0), f'merle{i}')
    sprites.make_group('merleRextra', (a, 0), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('merleR', (a, 1), f'merle{i}')
    sprites.make_group('merleRextra', (a, 1), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('merleR', (a, 2), f'merle{i}')
    sprites.make_group('merleRextra', (a, 2), f'merleextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('merleR', (a, 3), f'merle{i}')
    sprites.make_group('merleRextra', (a, 3), f'merleextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('merleWB', (a, 0), f'merle{i}')
    sprites.make_group('merleWBextra', (a, 0), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('merleWB', (a, 1), f'merle{i}')
    sprites.make_group('merleWBextra', (a, 1), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('merleWB', (a, 2), f'merle{i}')
    sprites.make_group('merleWBextra', (a, 2), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('merleWB', (a, 3), f'merle{i}')
    sprites.make_group('merleWBextra', (a, 3), f'merleextra{i}', sprites_y=2)
# rat
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('ratB', (a, 0), f'rat{i}')
    sprites.make_group('ratBextra', (a, 0), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('ratB', (a, 1), f'rat{i}')
    sprites.make_group('ratBextra', (a, 1), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('ratB', (a, 2), f'rat{i}')
    sprites.make_group('ratBextra', (a, 2), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('ratB', (a, 3), f'rat{i}')
    sprites.make_group('ratBextra', (a, 3), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('ratR', (a, 0), f'rat{i}')
    sprites.make_group('ratRextra', (a, 0), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('ratR', (a, 1), f'rat{i}')
    sprites.make_group('ratRextra', (a, 1), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('ratR', (a, 2), f'rat{i}')
    sprites.make_group('ratRextra', (a, 2), f'ratextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('ratR', (a, 3), f'rat{i}')
    sprites.make_group('ratRextra', (a, 3), f'ratextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('ratWB', (a, 0), f'rat{i}')
    sprites.make_group('ratWBextra', (a, 0), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('ratWB', (a, 1), f'rat{i}')
    sprites.make_group('ratWBextra', (a, 1), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('ratWB', (a, 2), f'rat{i}')
    sprites.make_group('ratWBextra', (a, 2), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('ratWB', (a, 3), f'rat{i}')
    sprites.make_group('ratWBextra', (a, 3), f'ratextra{i}', sprites_y=2)
#hooded
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('hoodedB', (a, 0), f'hooded{i}')
    sprites.make_group('hoodedBextra', (a, 0), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('hoodedB', (a, 1), f'hooded{i}')
    sprites.make_group('hoodedBextra', (a, 1), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('hoodedB', (a, 2), f'hooded{i}')
    sprites.make_group('hoodedBextra', (a, 2), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('hoodedB', (a, 3), f'hooded{i}')
    sprites.make_group('hoodedBextra', (a, 3), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('hoodedR', (a, 0), f'hooded{i}')
    sprites.make_group('hoodedRextra', (a, 0), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('hoodedR', (a, 1), f'hooded{i}')
    sprites.make_group('hoodedRextra', (a, 1), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('hoodedR', (a, 2), f'hooded{i}')
    sprites.make_group('hoodedRextra', (a, 2), f'hoodedextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('hoodedR', (a, 3), f'hooded{i}')
    sprites.make_group('hoodedRextra', (a, 3), f'hoodedextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('hoodedWB', (a, 0), f'hooded{i}')
    sprites.make_group('hoodedWBextra', (a, 0), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('hoodedWB', (a, 1), f'hooded{i}')
    sprites.make_group('hoodedWBextra', (a, 1), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('hoodedWB', (a, 2), f'hooded{i}')
    sprites.make_group('hoodedWBextra', (a, 2), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('hoodedWB', (a, 3), f'hooded{i}')
    sprites.make_group('hoodedWBextra', (a, 3), f'hoodedextra{i}', sprites_y=2)
# skitty
for a, i in enumerate(['BEIGE', 'MEERKAT', 'KHAKI', 'CAPPUCCINO', 'ECRU', 'ASHBROWN']):
    sprites.make_group('skittyB', (a, 0), f'skitty{i}')
    sprites.make_group('skittyBextra', (a, 0), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK']):
    sprites.make_group('skittyB', (a, 1), f'skitty{i}')
    sprites.make_group('skittyBextra', (a, 1), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA']):
    sprites.make_group('skittyB', (a, 2), f'skitty{i}')
    sprites.make_group('skittyBextra', (a, 2), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['COFFEE', 'TAUPE', 'UMBER']):
    sprites.make_group('skittyB', (a, 3), f'skitty{i}')
    sprites.make_group('skittyBextra', (a, 3), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['PALECREAM', 'CREAM', 'ROSE', 'GINGER', 'SUNSET', 'RUFOUS']):
    sprites.make_group('skittyR', (a, 0), f'skitty{i}')
    sprites.make_group('skittyRextra', (a, 0), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['SAND', 'WOOD', 'FIRE', 'BRICK', 'RED', 'SCARLET']):
    sprites.make_group('skittyR', (a, 1), f'skitty{i}')
    sprites.make_group('skittyRextra', (a, 1), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT']):
    sprites.make_group('skittyR', (a, 2), f'skitty{i}')
    sprites.make_group('skittyRextra', (a, 2), f'skittyextra{i}', sprites_y=2)    
for a, i in enumerate(['CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD']):
    sprites.make_group('skittyR', (a, 3), f'skitty{i}')
    sprites.make_group('skittyRextra', (a, 3), f'skittyextra{i}', sprites_y=2)   
for a, i in enumerate(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'MARENGO', 'BATTLESHIP']):
    sprites.make_group('skittyWB', (a, 0), f'skitty{i}')
    sprites.make_group('skittyWBextra', (a, 0), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'SOOT']):
    sprites.make_group('skittyWB', (a, 1), f'skitty{i}')
    sprites.make_group('skittyWBextra', (a, 1), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['DARKGREY', 'ANCHOR', 'CHARCOAL']):
    sprites.make_group('skittyWB', (a, 2), f'skitty{i}')
    sprites.make_group('skittyWBextra', (a, 2), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['COAL', 'BLACK']):
    sprites.make_group('skittyWB', (a, 3), f'skitty{i}')
    sprites.make_group('skittyWBextra', (a, 3), f'skittyextra{i}', sprites_y=2)

# sphynxes
sprites.make_group('skin_sphynx', (0, 0), 'skinS_BLACK')
sprites.make_group('skin_sphynx', (1, 0), 'skinS_RED')
sprites.make_group('skin_sphynx', (2, 0), 'skinS_PINK')
sprites.make_group('skin_sphynx', (3, 0), 'skinS_DARKBROWN')
sprites.make_group('skin_sphynx', (4, 0), 'skinS_BROWN')
sprites.make_group('skin_sphynx', (5, 0), 'skinS_LIGHTBROWN')
sprites.make_group('skin_sphynx', (0, 1), 'skinS_DARK')
sprites.make_group('skin_sphynx', (1, 1), 'skinS_DARKGREY')
sprites.make_group('skin_sphynx', (2, 1), 'skinS_GREY')
sprites.make_group('skin_sphynx', (3, 1), 'skinS_DARKSALMON')
sprites.make_group('skin_sphynx', (4, 1), 'skinS_SALMON')
sprites.make_group('skin_sphynx', (5, 1), 'skinS_PEACH')
sprites.make_group('skin_sphynx', (0, 2), 'skinS_DARKMARBLED')
sprites.make_group('skin_sphynx', (1, 2), 'skinS_MARBLED')
sprites.make_group('skin_sphynx', (2, 2), 'skinS_LIGHTMARBLED')
sprites.make_group('skin_sphynx', (3, 2), 'skinS_DARKBLUE')
sprites.make_group('skin_sphynx', (4, 2), 'skinS_BLUE')
sprites.make_group('skin_sphynx', (5, 2), 'skinS_LIGHTBLUE')
sprites.make_group('skin2', (0, 2), 'skinS_ALBINOPINK')
sprites.make_group('skin2', (1, 2), 'skinS_ALBINOBLUE')
sprites.make_group('skin2', (2, 2), 'skinS_ALBINORED')
sprites.make_group('skin2', (3, 2), 'skinS_ALBINOVIOLET')
sprites.make_group('skin2', (3, 1), 'skinS_MELANISTICLIGHT')
sprites.make_group('skin2', (4, 1), 'skinS_MELANISTIC')
sprites.make_group('skin2', (5, 1), 'skinS_MELANISTICDARK')
sprites.make_group('skinextra_sphynx', (0, 0), 'skinextraS_BLACK', sprites_y=2)
sprites.make_group('skinextra_sphynx', (1, 0), 'skinextraS_RED', sprites_y=2)
sprites.make_group('skinextra_sphynx', (2, 0), 'skinextraS_PINK', sprites_y=2)
sprites.make_group('skinextra_sphynx', (3, 0), 'skinextraS_DARKBROWN', sprites_y=2)
sprites.make_group('skinextra_sphynx', (4, 0), 'skinextraS_BROWN', sprites_y=2)
sprites.make_group('skinextra_sphynx', (5, 0), 'skinextraS_LIGHTBROWN', sprites_y=2)
sprites.make_group('skinextra_sphynx', (0, 1), 'skinextraS_DARK', sprites_y=2)
sprites.make_group('skinextra_sphynx', (1, 1), 'skinextraS_DARKGREY', sprites_y=2)
sprites.make_group('skinextra_sphynx', (2, 1), 'skinextraS_GREY', sprites_y=2)
sprites.make_group('skinextra_sphynx', (3, 1), 'skinextraS_DARKSALMON', sprites_y=2)
sprites.make_group('skinextra_sphynx', (4, 1), 'skinextraS_SALMON', sprites_y=2)
sprites.make_group('skinextra_sphynx', (5, 1), 'skinextraS_PEACH', sprites_y=2)
sprites.make_group('skinextra_sphynx', (0, 2), 'skinextraS_DARKMARBLED', sprites_y=2)
sprites.make_group('skinextra_sphynx', (1, 2), 'skinextraS_MARBLED', sprites_y=2)
sprites.make_group('skinextra_sphynx', (2, 2), 'skinextraS_LIGHTMARBLED', sprites_y=2)
sprites.make_group('skinextra_sphynx', (3, 2), 'skinextraS_DARKBLUE', sprites_y=2)
sprites.make_group('skinextra_sphynx', (4, 2), 'skinextraS_BLUE', sprites_y=2)
sprites.make_group('skinextra_sphynx', (5, 2), 'skinextraS_LIGHTBLUE', sprites_y=2)
sprites.make_group('skin2extra', (0, 2), 'skinextraS_ALBINOPINK', sprites_y=2)
sprites.make_group('skin2extra', (1, 2), 'skinextraS_ALBINOBLUE', sprites_y=2)
sprites.make_group('skin2extra', (2, 2), 'skinextraS_ALBINORED', sprites_y=2)
sprites.make_group('skin2extra', (3, 2), 'skinextraS_ALBINOVIOLET', sprites_y=2)
sprites.make_group('skin2extra', (3, 1), 'skinextraS_MELANISTICLIGHT', sprites_y=2)
sprites.make_group('skin2extra', (4, 1), 'skinextraS_MELANISTIC', sprites_y=2)
sprites.make_group('skin2extra', (5, 1), 'skinextraS_MELANISTICDARK', sprites_y=2)

# new new torties
for a, i in enumerate(['ONE', 'TWO', 'THREE', 'FOUR', 'REDTAIL', 'DELILAH']):
    sprites.make_group('tortiepatchesmasks', (a, 0), f"tortiemask{i}", sprites_y=7)
for a, i in enumerate(['MINIMAL1', 'MINIMAL2', 'MINIMAL3', 'MINIMAL4', 'OREO', 'SWOOP']):
    sprites.make_group('tortiepatchesmasks', (a, 1), f"tortiemask{i}", sprites_y=7)
for a, i in enumerate(['MOTTLED', 'SIDEMASK', 'EYEDOT', 'BANDANA', 'PACMAN', 'STREAMSTRIKE']):
    sprites.make_group('tortiepatchesmasks', (a, 2), f"tortiemask{i}", sprites_y=7)
for a, i in enumerate(['ORIOLE', 'ROBIN', 'BRINDLE', 'PAIGE']):
    sprites.make_group('tortiepatchesmasks', (a, 3), f"tortiemask{i}", sprites_y=7)
for a, i in enumerate(['COMBO', 'BLENDED', 'SCATTER', 'LIGHT']):
    sprites.make_group('tortiepatchesmasksB', (a, 3), f"tortiemask{i}", sprites_y=5)

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
sprites.make_group('skin2', (0, 0), 'skinALBINOPINK')
sprites.make_group('skin2', (1, 0), 'skinALBINOBLUE')
sprites.make_group('skin2', (2, 0), 'skinALBINORED')
sprites.make_group('skin2', (3, 0), 'skinALBINOVIOLET')
sprites.make_group('skin2', (0, 1), 'skinMELANISTICLIGHT')
sprites.make_group('skin2', (1, 1), 'skinMELANISTIC')
sprites.make_group('skin2', (2, 1), 'skinMELANISTICDARK')


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
sprites.make_group('skin2extra', (0, 0), 'skinextraALBINOPINK', sprites_y=2)
sprites.make_group('skin2extra', (1, 0), 'skinextraALBINOBLUE', sprites_y=2)
sprites.make_group('skin2extra', (2, 0), 'skinextraALBINORED', sprites_y=2)
sprites.make_group('skin2extra', (3, 0), 'skinextraALBINOVIOLET', sprites_y=2)
sprites.make_group('skin2extra', (0, 1), 'skinextraMELANISTICLIGHT', sprites_y=2)
sprites.make_group('skin2extra', (1, 1), 'skinextraMELANISTIC', sprites_y=2)
sprites.make_group('skin2extra', (2, 1), 'skinextraMELANISTICDARK', sprites_y=2)

# tiles.make_group('dithered', (0, 0), 'terrain')
# tiles.make_group('dithered', (1, 0), 'terraintwo')

sprites.load_scars()
