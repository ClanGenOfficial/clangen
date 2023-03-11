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
    'skin3', 'skin3extra', 'skin3_sphynx', 'skin3extra_sphynx', 'scars', 'scarsextra', 'scarsdark', 'scarsdarkextra', 'Newscars', 
    'Newscarsextra', 'shaders', 'lineartdead', 'lineartdf', 'eyes_df', 'eyesextra_df', 'singleB', 'singleBextra', 
    'singleR', 'singleRextra', 'singleWB', 'singleWBextra', 'shadersnewwhite', 'lightingnew',  'singleBl', 'singleBlextra', 'singlePu', 
    'singlePuextra', 'singleY', 'singleYextra', 'singleG', 'singleGextra', 'shadersnewwhite', 'lightingnew', 'fademask', 'fadestarclan', 'fadedarkforest'

]:
    sprites.spritesheet(f"sprites/{x}.png", x)    
    
for x in [
    'whiteextra', 'whitenewextra', 'whitepatchesnew', 'whitepatches',
    'whitepatches3', 'whitepatches3extra', 'whitepatches4', 'whitepatches4extra',
    'whitepatchesmoss', 'whitemossextra', 'tortiepatchesmasks', 'tortiepatchesmasksB'

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
    'dobermanB', 'dobermanBextra', 'ratB', 'ratBextra', 'skeleB', 'skeleBextra', 'skittyB', 'skittyBextra',
    'smokeB', 'stainB', 'stainBextra', 'smokeBextra', 'dobermanR', 'dobermanRextra', 
    'skeleR', 'skeleRextra', 'smokeR', 'smokeRextra', 'dobermanWB', 'dobermanWBextra', 'smokeWB', 
    'smokeWBextra', 'skeleWB', 'skeleWBextra',  'stainR', 'stainRextra', 'stainWB', 'stainWBextra',
    'ratR', 'ratRextra',  'ratWB', 'ratWBextra',  'skittyR', 'skittyRextra',
    'skittyWB', 'skittyWBextra', 'dobermanBl', 'dobermanBlextra', 'ratBl', 'ratBlextra', 'skeleBl', 'skeleBlextra', 'skittyBl', 'skittyBlextra',
    'smokeBl', 'smokeBlextra', 'stainBl', 'stainBlextra', 'dobermanPu', 'dobermanPuextra', 'ratPu', 'ratPuextra', 'skelePu', 'skelePuextra', 'skittyPu', 'skittyPuextra',
    'smokePu', 'smokePuextra', 'stainPu', 'stainPuextra', 'dobermanY', 'dobermanYextra', 'ratY', 'ratYextra', 'skeleY', 'skeleYextra', 'skittyY', 'skittyYextra',
    'smokeY', 'smokeYextra', 'stainY', 'stainYextra', 'dobermanG', 'dobermanGextra', 'ratG', 'ratGextra', 'skeleG', 'skeleGextra', 'skittyG', 'skittyGextra',
    'smokeG', 'smokeGextra', 'stainG', 'stainGextra'

]:
    sprites.spritesheet(f"sprites/solidbase/{x}.png", x)    
    
for x in [
    'bengalB', 'bengalBextra', 'mottledB', 'mottledBextra', 'rosetteB', 'rosetteBextra', 'snowflakeB', 
    'snowflakeBextra','speckledB', 'speckledBextra', 'bengalR', 'bengalRextra', 'mottledR', 'mottledRextra',
    'rosetteR', 'rosetteRextra', 'snowflakeR', 'snowflakeRextra', 'speckledR', 'speckledRextra', 'bengalWB', 'bengalWBextra', 
    'mottledWB', 'mottledWBextra', 'rosetteWB', 'rosetteWBextra', 'snowflakeWB', 'snowflakeWBextra', 'speckledWB', 'speckledWBextra',
    'bengalBl', 'bengalBlextra', 'mottledBl', 'mottledBlextra', 'rosetteBl', 'rosetteBlextra', 'snowflakeBl', 
    'snowflakeBlextra','speckledBl', 'speckledBlextra', 'bengalPu', 'bengalPuextra', 'mottledPu', 'mottledPuextra', 'rosettePu', 'rosettePuextra', 'snowflakePu', 
    'snowflakePuextra','speckledPu', 'speckledPuextra', 'bengalY', 'bengalYextra', 'mottledY', 'mottledYextra', 'rosetteY', 'rosetteYextra', 'snowflakeY', 
    'snowflakeYextra','speckledY', 'speckledYextra', 'bengalG', 'bengalGextra', 'mottledG', 'mottledGextra', 'rosetteG', 'rosetteGextra', 'snowflakeG', 
    'snowflakeGextra','speckledG', 'speckledGextra'

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
    'hoodedWBextra', 'agoutiBl', 'agoutiBlextra', 'backedBl', 'backedBlextra', 'charcoalBl', 'charcoalBlextra', 'classicBl',
    'classicBlextra', 'ghostBl', 'ghostBlextra', 'hoodedBl', 'hoodedBlextra', 'mackerelBl', 'mackerelBlextra', 'marbleBl', 
    'marbleBlextra', 'merleBl', 'merleBlextra', 'sokokeBl', 'sokokeBlextra', 'tabbyBl', 'tabbyBlextra', 'tickedBl', 
    'tickedBlextra', 'agoutiPu', 'agoutiPuextra', 'backedPu', 'backedPuextra', 'charcoalPu', 'charcoalPuextra', 'classicPu',
    'classicPuextra', 'ghostPu', 'ghostPuextra', 'hoodedPu', 'hoodedPuextra', 'mackerelPu', 'mackerelPuextra', 'marblePu', 
    'marblePuextra', 'merlePu', 'merlePuextra', 'sokokePu', 'sokokePuextra', 'tabbyPu', 'tabbyPuextra', 'tickedPu', 
    'tickedPuextra', 'agoutiY', 'agoutiYextra', 'backedY', 'backedYextra', 'charcoalY', 'charcoalYextra', 'classicY',
    'classicYextra', 'ghostY', 'ghostYextra', 'hoodedY', 'hoodedYextra', 'mackerelY', 'mackerelYextra', 'marbleY', 
    'marbleYextra', 'merleY', 'merleYextra', 'sokokeY', 'sokokeYextra', 'tabbyY', 'tabbyYextra', 'tickedY', 
    'tickedYextra', 'agoutiG', 'agoutiGextra', 'backedG', 'backedGextra', 'charcoalG', 'charcoalGextra', 'classicG',
    'classicGextra', 'ghostG', 'ghostGextra', 'hoodedG', 'hoodedGextra', 'mackerelG', 'mackerelGextra', 'marbleG', 
    'marbleGextra', 'merleG', 'merleGextra', 'sokokeG', 'sokokeGextra', 'tabbyG', 'tabbyGextra', 'tickedG', 
    'tickedGextra'

]:
    sprites.spritesheet(f"sprites/tabby/{x}.png", x) 

for x in [
    'agoutiP', 'agoutiPextra', 'backedP', 'backedPextra', 'bengalP', 'bengalPextra', 'charcoalP', 'charcoalPextra',
    'classicP', 'classicPextra', 'dobermanP', 'dobermanPextra', 'ghostP', 'ghostPextra', 'hoodedP', 'hoodedPextra',
    'mackerelP', 'mackerelPextra', 'marbleP', 'marblePextra', 'merleP', 'merlePextra', 'mottledP', 'mottledPextra', 
    'pridebase', 'pridebaseextra', 'ratP', 'ratPextra', 'rosetteP', 'rosettePextra', 'skeleP', 'skelePextra', 'skittyP', 
    'skittyPextra', 'smokeP', 'smokePextra', 'snowflakeP', 'snowflakePextra', 'sokokeP', 'sokokePextra', 'speckledP', 
    'speckledPextra', 'stainP', 'stainPextra', 'tabbyP', 'tabbyPextra', 'tickedP', 'tickedPextra'
]:
    sprites.spritesheet(f"sprites/pride/{x}.png", x)

for sprite in [
    'Paralyzed_lineart', 'singleparalyzed', 'speckledparalyzed',
    'tabbyparalyzed', 'whiteallparalyzed', 'eyesparalyzed',
    'tabbyparalyzed', 'tortiesparalyzed', 'scarsparalyzed', 'skinparalyzed',
    'medcatherbsparalyzed'

]:
    sprites.spritesheet(f"sprites/paralyzed/{sprite}.png", sprite)

for x in [
    'winglineart', 'winglineartdead', 'winglineartdf', 'wings', 'wingsextra', 'wings2',
    'wings2extra'
]:
    sprites.spritesheet(f"sprites/wings/{x}.png", x) 

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
sprites.make_group('winglineartdead', (0, 0), 'w_lineartdead', sprites_y=5)
sprites.make_group('winglineartdf', (0, 0), 'w_lineartdf', sprites_y=5)

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
for a, i in enumerate([ 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL',
    'LIGHTSONG', 'VITILIGO']):
    sprites.make_group('whitepatchesnew', (a, 0), f'white{i}')
    sprites.make_group('whitenewextra', (a, 0), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate(['ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY',
    'VANCREAMY', 'ANY2CREAMY']):
    sprites.make_group('whitepatches', (a, 1), f'white{i}')
    sprites.make_group('whiteextra', (a, 1), f'whiteextra{i}', sprites_y=2)
for a, i in enumerate(['SKELEWHITE', 'LIGHTPOINT']):
    sprites.make_group('whitepatchesnew', (a, 1), f'white{i}')
    sprites.make_group('whitenewextra', (a, 1), f'whiteextra{i}', sprites_y=2)
    
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
for a, i in enumerate(['MAO', 'LUNA', 'CHESTSPECK', 'WINGS', 'PAINTED', 'HEART2', 'BLACKSTAR']):
    sprites.make_group('whitepatches4', (a, 2), 'white' + i)
    sprites.make_group('whitepatches4extra', (a, 2), 'whiteextra' + i, sprites_y=2) 
    
# moss white patches
for a, i in enumerate(['SNOWSHOE', 'VENUS', 'SNOWBOOT', 'CHANCE', 'MOSSCLAW', 'DAPPLED', 'NIGHTMIST', 'HAWK']):
    sprites.make_group('whitepatchesmoss', (a, 0), 'white' + i)
    sprites.make_group('whitemossextra', (a, 0), 'whiteextra' + i, sprites_y=2)
for a, i in enumerate(['SHADOWSIGHT', 'TWIST', 'RETSUKO', 'OKAPI', 'FRECKLEMASK', 'MOTH']):
    sprites.make_group('whitepatchesmoss', (a, 1), 'white' + i)
    sprites.make_group('whitemossextra', (a, 1), 'whiteextra' + i, sprites_y=2) 

# single
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('singleBl', (a, 0), f'single{i}')
    sprites.make_group('singleBlextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('singleBl', (a, 1), f'single{i}')
    sprites.make_group('singleBlextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('singleBl', (a, 2), f'single{i}')
    sprites.make_group('singleBlextra', (a, 2), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('singlePu', (a, 0), f'single{i}')
    sprites.make_group('singlePuextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('singlePu', (a, 1), f'single{i}')
    sprites.make_group('singlePuextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('singlePu', (a, 2), f'single{i}')
    sprites.make_group('singlePuextra', (a, 2), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('singlePu', (a, 3), f'single{i}')
    sprites.make_group('singlePuextra', (a, 3), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('singleY', (a, 0), f'single{i}')
    sprites.make_group('singleYextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('singleY', (a, 1), f'single{i}')
    sprites.make_group('singleYextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('singleY', (a, 2), f'single{i}')
    sprites.make_group('singleYextra', (a, 2), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('singleY', (a, 3), f'single{i}')
    sprites.make_group('singleYextra', (a, 3), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('singleG', (a, 0), f'single{i}')
    sprites.make_group('singleGextra', (a, 0), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('singleG', (a, 1), f'single{i}')
    sprites.make_group('singleGextra', (a, 1), f'singleextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('singleG', (a, 2), f'single{i}')
    sprites.make_group('singleGextra', (a, 2), f'singleextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('singleG', (a, 3), f'single{i}')
    sprites.make_group('singleGextra', (a, 3), f'singleextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('tabbyBl', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyBlextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('tabbyBl', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyBlextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('tabbyBl', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyBlextra', (a, 2), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('tabbyPu', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyPuextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('tabbyPu', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyPuextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('tabbyPu', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyPuextra', (a, 2), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('tabbyPu', (a, 3), f'tabby{i}')
    sprites.make_group('tabbyPuextra', (a, 3), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('tabbyY', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyYextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('tabbyY', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyYextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('tabbyY', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyYextra', (a, 2), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('tabbyY', (a, 3), f'tabby{i}')
    sprites.make_group('tabbyYextra', (a, 3), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('tabbyG', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyGextra', (a, 0), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('tabbyG', (a, 1), f'tabby{i}')
    sprites.make_group('tabbyGextra', (a, 1), f'tabbyextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('tabbyG', (a, 2), f'tabby{i}')
    sprites.make_group('tabbyGextra', (a, 2), f'tabbyextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('tabbyG', (a, 3), f'tabby{i}')
    sprites.make_group('tabbyGextra', (a, 3), f'tabbyextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('marbleBl', (a, 0), f'marbled{i}')
    sprites.make_group('marbleBlextra', (a, 0), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('marbleBl', (a, 1), f'marbled{i}')
    sprites.make_group('marbleBlextra', (a, 1), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('marbleBl', (a, 2), f'marbled{i}')
    sprites.make_group('marbleBlextra', (a, 2), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('marblePu', (a, 0), f'marbled{i}')
    sprites.make_group('marblePuextra', (a, 0), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('marblePu', (a, 1), f'marbled{i}')
    sprites.make_group('marblePuextra', (a, 1), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('marblePu', (a, 2), f'marbled{i}')
    sprites.make_group('marblePuextra', (a, 2), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('marblePu', (a, 3), f'marbled{i}')
    sprites.make_group('marblePuextra', (a, 3), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('marbleY', (a, 0), f'marbled{i}')
    sprites.make_group('marbleYextra', (a, 0), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('marbleY', (a, 1), f'marbled{i}')
    sprites.make_group('marbleYextra', (a, 1), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('marbleY', (a, 2), f'marbled{i}')
    sprites.make_group('marbleYextra', (a, 2), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('marbleY', (a, 3), f'marbled{i}')
    sprites.make_group('marbleYextra', (a, 3), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('marbleG', (a, 0), f'marbled{i}')
    sprites.make_group('marbleGextra', (a, 0), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('marbleG', (a, 1), f'marbled{i}')
    sprites.make_group('marbleGextra', (a, 1), f'marbledextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('marbleG', (a, 2), f'marbled{i}')
    sprites.make_group('marbleGextra', (a, 2), f'marbledextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('marbleG', (a, 3), f'marbled{i}')
    sprites.make_group('marbleGextra', (a, 3), f'marbledextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('rosetteBl', (a, 0), f'rosette{i}')
    sprites.make_group('rosetteBlextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('rosetteBl', (a, 1), f'rosette{i}')
    sprites.make_group('rosetteBlextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('rosetteBl', (a, 2), f'rosette{i}')
    sprites.make_group('rosetteBlextra', (a, 2), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('rosettePu', (a, 0), f'rosette{i}')
    sprites.make_group('rosettePuextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('rosettePu', (a, 1), f'rosette{i}')
    sprites.make_group('rosettePuextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('rosettePu', (a, 2), f'rosette{i}')
    sprites.make_group('rosettePuextra', (a, 2), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('rosettePu', (a, 3), f'rosette{i}')
    sprites.make_group('rosettePuextra', (a, 3), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('rosetteY', (a, 0), f'rosette{i}')
    sprites.make_group('rosetteYextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('rosetteY', (a, 1), f'rosette{i}')
    sprites.make_group('rosetteYextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('rosetteY', (a, 2), f'rosette{i}')
    sprites.make_group('rosetteYextra', (a, 2), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('rosetteY', (a, 3), f'rosette{i}')
    sprites.make_group('rosetteYextra', (a, 3), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('rosetteG', (a, 0), f'rosette{i}')
    sprites.make_group('rosetteGextra', (a, 0), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('rosetteG', (a, 1), f'rosette{i}')
    sprites.make_group('rosetteGextra', (a, 1), f'rosetteextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('rosetteG', (a, 2), f'rosette{i}')
    sprites.make_group('rosetteGextra', (a, 2), f'rosetteextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('rosetteG', (a, 3), f'rosette{i}')
    sprites.make_group('rosetteGextra', (a, 3), f'rosetteextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('smokeBl', (a, 0), f'smoke{i}')
    sprites.make_group('smokeBlextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('smokeBl', (a, 1), f'smoke{i}')
    sprites.make_group('smokeBlextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('smokeBl', (a, 2), f'smoke{i}')
    sprites.make_group('smokeBlextra', (a, 2), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('smokePu', (a, 0), f'smoke{i}')
    sprites.make_group('smokePuextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('smokePu', (a, 1), f'smoke{i}')
    sprites.make_group('smokePuextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('smokePu', (a, 2), f'smoke{i}')
    sprites.make_group('smokePuextra', (a, 2), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('smokePu', (a, 3), f'smoke{i}')
    sprites.make_group('smokePuextra', (a, 3), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('smokeY', (a, 0), f'smoke{i}')
    sprites.make_group('smokeYextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('smokeY', (a, 1), f'smoke{i}')
    sprites.make_group('smokeYextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('smokeY', (a, 2), f'smoke{i}')
    sprites.make_group('smokeYextra', (a, 2), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('smokeY', (a, 3), f'smoke{i}')
    sprites.make_group('smokeYextra', (a, 3), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('smokeG', (a, 0), f'smoke{i}')
    sprites.make_group('smokeGextra', (a, 0), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('smokeG', (a, 1), f'smoke{i}')
    sprites.make_group('smokeGextra', (a, 1), f'smokeextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('smokeG', (a, 2), f'smoke{i}')
    sprites.make_group('smokeGextra', (a, 2), f'smokeextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('smokeG', (a, 3), f'smoke{i}')
    sprites.make_group('smokeGextra', (a, 3), f'smokeextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('tickedBl', (a, 0), f'ticked{i}')
    sprites.make_group('tickedBlextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('tickedBl', (a, 1), f'ticked{i}')
    sprites.make_group('tickedBlextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('tickedBl', (a, 2), f'ticked{i}')
    sprites.make_group('tickedBlextra', (a, 2), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('tickedPu', (a, 0), f'ticked{i}')
    sprites.make_group('tickedPuextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('tickedPu', (a, 1), f'ticked{i}')
    sprites.make_group('tickedPuextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('tickedPu', (a, 2), f'ticked{i}')
    sprites.make_group('tickedPuextra', (a, 2), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('tickedPu', (a, 3), f'ticked{i}')
    sprites.make_group('tickedPuextra', (a, 3), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('tickedY', (a, 0), f'ticked{i}')
    sprites.make_group('tickedYextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('tickedY', (a, 1), f'ticked{i}')
    sprites.make_group('tickedYextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('tickedY', (a, 2), f'ticked{i}')
    sprites.make_group('tickedYextra', (a, 2), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('tickedY', (a, 3), f'ticked{i}')
    sprites.make_group('tickedYextra', (a, 3), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('tickedG', (a, 0), f'ticked{i}')
    sprites.make_group('tickedGextra', (a, 0), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('tickedG', (a, 1), f'ticked{i}')
    sprites.make_group('tickedGextra', (a, 1), f'tickedextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('tickedG', (a, 2), f'ticked{i}')
    sprites.make_group('tickedGextra', (a, 2), f'tickedextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('tickedG', (a, 3), f'ticked{i}')
    sprites.make_group('tickedGextra', (a, 3), f'tickedextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('speckledBl', (a, 0), f'speckled{i}')
    sprites.make_group('speckledBlextra', (a, 0), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('speckledBl', (a, 1), f'speckled{i}')
    sprites.make_group('speckledBlextra', (a, 1), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('speckledBl', (a, 2), f'speckled{i}')
    sprites.make_group('speckledBlextra', (a, 2), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('speckledPu', (a, 0), f'speckled{i}')
    sprites.make_group('speckledPuextra', (a, 0), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('speckledPu', (a, 1), f'speckled{i}')
    sprites.make_group('speckledPuextra', (a, 1), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('speckledPu', (a, 2), f'speckled{i}')
    sprites.make_group('speckledPuextra', (a, 2), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('speckledPu', (a, 3), f'speckled{i}')
    sprites.make_group('speckledPuextra', (a, 3), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('speckledY', (a, 0), f'speckled{i}')
    sprites.make_group('speckledYextra', (a, 0), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('speckledY', (a, 1), f'speckled{i}')
    sprites.make_group('speckledYextra', (a, 1), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('speckledY', (a, 2), f'speckled{i}')
    sprites.make_group('speckledYextra', (a, 2), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('speckledY', (a, 3), f'speckled{i}')
    sprites.make_group('speckledYextra', (a, 3), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('speckledG', (a, 0), f'speckled{i}')
    sprites.make_group('speckledGextra', (a, 0), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('speckledG', (a, 1), f'speckled{i}')
    sprites.make_group('speckledGextra', (a, 1), f'speckledextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('speckledG', (a, 2), f'speckled{i}')
    sprites.make_group('speckledGextra', (a, 2), f'speckledextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('speckledG', (a, 3), f'speckled{i}')
    sprites.make_group('speckledGextra', (a, 3), f'speckledextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('bengalBl', (a, 0), f'bengal{i}')
    sprites.make_group('bengalBlextra', (a, 0), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('bengalBl', (a, 1), f'bengal{i}')
    sprites.make_group('bengalBlextra', (a, 1), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('bengalBl', (a, 2), f'bengal{i}')
    sprites.make_group('bengalBlextra', (a, 2), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('bengalPu', (a, 0), f'bengal{i}')
    sprites.make_group('bengalPuextra', (a, 0), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('bengalPu', (a, 1), f'bengal{i}')
    sprites.make_group('bengalPuextra', (a, 1), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('bengalPu', (a, 2), f'bengal{i}')
    sprites.make_group('bengalPuextra', (a, 2), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('bengalPu', (a, 3), f'bengal{i}')
    sprites.make_group('bengalPuextra', (a, 3), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('bengalY', (a, 0), f'bengal{i}')
    sprites.make_group('bengalYextra', (a, 0), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('bengalY', (a, 1), f'bengal{i}')
    sprites.make_group('bengalYextra', (a, 1), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('bengalY', (a, 2), f'bengal{i}')
    sprites.make_group('bengalYextra', (a, 2), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('bengalY', (a, 3), f'bengal{i}')
    sprites.make_group('bengalYextra', (a, 3), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('bengalG', (a, 0), f'bengal{i}')
    sprites.make_group('bengalGextra', (a, 0), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('bengalG', (a, 1), f'bengal{i}')
    sprites.make_group('bengalGextra', (a, 1), f'bengalextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('bengalG', (a, 2), f'bengal{i}')
    sprites.make_group('bengalGextra', (a, 2), f'bengalextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('bengalG', (a, 3), f'bengal{i}')
    sprites.make_group('bengalGextra', (a, 3), f'bengalextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('mackerelBl', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelBlextra', (a, 0), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('mackerelBl', (a, 1), f'mackerel{i}')
    sprites.make_group('mackerelBlextra', (a, 1), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('mackerelBl', (a, 2), f'mackerel{i}')
    sprites.make_group('mackerelBlextra', (a, 2), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('mackerelPu', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelPuextra', (a, 0), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('mackerelPu', (a, 1), f'mackerel{i}')
    sprites.make_group('mackerelPuextra', (a, 1), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('mackerelPu', (a, 2), f'mackerel{i}')
    sprites.make_group('mackerelPuextra', (a, 2), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('mackerelPu', (a, 3), f'mackerel{i}')
    sprites.make_group('mackerelPuextra', (a, 3), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('mackerelY', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelYextra', (a, 0), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('mackerelY', (a, 1), f'mackerel{i}')
    sprites.make_group('mackerelYextra', (a, 1), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('mackerelY', (a, 2), f'mackerel{i}')
    sprites.make_group('mackerelYextra', (a, 2), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('mackerelY', (a, 3), f'mackerel{i}')
    sprites.make_group('mackerelYextra', (a, 3), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('mackerelG', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelGextra', (a, 0), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('mackerelG', (a, 1), f'mackerel{i}')
    sprites.make_group('mackerelGextra', (a, 1), f'mackerelextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('mackerelG', (a, 2), f'mackerel{i}')
    sprites.make_group('mackerelGextra', (a, 2), f'mackerelextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('mackerelG', (a, 3), f'mackerel{i}')
    sprites.make_group('mackerelGextra', (a, 3), f'mackerelextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('classicBl', (a, 0), f'classic{i}')
    sprites.make_group('classicBlextra', (a, 0), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('classicBl', (a, 1), f'classic{i}')
    sprites.make_group('classicBlextra', (a, 1), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('classicBl', (a, 2), f'classic{i}')
    sprites.make_group('classicBlextra', (a, 2), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('classicPu', (a, 0), f'classic{i}')
    sprites.make_group('classicPuextra', (a, 0), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('classicPu', (a, 1), f'classic{i}')
    sprites.make_group('classicPuextra', (a, 1), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('classicPu', (a, 2), f'classic{i}')
    sprites.make_group('classicPuextra', (a, 2), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('classicPu', (a, 3), f'classic{i}')
    sprites.make_group('classicPuextra', (a, 3), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('classicY', (a, 0), f'classic{i}')
    sprites.make_group('classicYextra', (a, 0), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('classicY', (a, 1), f'classic{i}')
    sprites.make_group('classicYextra', (a, 1), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('classicY', (a, 2), f'classic{i}')
    sprites.make_group('classicYextra', (a, 2), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('classicY', (a, 3), f'classic{i}')
    sprites.make_group('classicYextra', (a, 3), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('classicG', (a, 0), f'classic{i}')
    sprites.make_group('classicGextra', (a, 0), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('classicG', (a, 1), f'classic{i}')
    sprites.make_group('classicGextra', (a, 1), f'classicextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('classicG', (a, 2), f'classic{i}')
    sprites.make_group('classicGextra', (a, 2), f'classicextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('classicG', (a, 3), f'classic{i}')
    sprites.make_group('classicGextra', (a, 3), f'classicextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('sokokeBl', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokeBlextra', (a, 0), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('sokokeBl', (a, 1), f'sokoke{i}')
    sprites.make_group('sokokeBlextra', (a, 1), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('sokokeBl', (a, 2), f'sokoke{i}')
    sprites.make_group('sokokeBlextra', (a, 2), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('sokokePu', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokePuextra', (a, 0), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('sokokePu', (a, 1), f'sokoke{i}')
    sprites.make_group('sokokePuextra', (a, 1), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('sokokePu', (a, 2), f'sokoke{i}')
    sprites.make_group('sokokePuextra', (a, 2), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('sokokePu', (a, 3), f'sokoke{i}')
    sprites.make_group('sokokePuextra', (a, 3), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('sokokeY', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokeYextra', (a, 0), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('sokokeY', (a, 1), f'sokoke{i}')
    sprites.make_group('sokokeYextra', (a, 1), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('sokokeY', (a, 2), f'sokoke{i}')
    sprites.make_group('sokokeYextra', (a, 2), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('sokokeY', (a, 3), f'sokoke{i}')
    sprites.make_group('sokokeYextra', (a, 3), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('sokokeG', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokeGextra', (a, 0), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('sokokeG', (a, 1), f'sokoke{i}')
    sprites.make_group('sokokeGextra', (a, 1), f'sokokeextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('sokokeG', (a, 2), f'sokoke{i}')
    sprites.make_group('sokokeGextra', (a, 2), f'sokokeextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('sokokeG', (a, 3), f'sokoke{i}')
    sprites.make_group('sokokeGextra', (a, 3), f'sokokeextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('agoutiBl', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiBlextra', (a, 0), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('agoutiBl', (a, 1), f'agouti{i}')
    sprites.make_group('agoutiBlextra', (a, 1), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('agoutiBl', (a, 2), f'agouti{i}')
    sprites.make_group('agoutiBlextra', (a, 2), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('agoutiPu', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiPuextra', (a, 0), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('agoutiPu', (a, 1), f'agouti{i}')
    sprites.make_group('agoutiPuextra', (a, 1), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('agoutiPu', (a, 2), f'agouti{i}')
    sprites.make_group('agoutiPuextra', (a, 2), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('agoutiPu', (a, 3), f'agouti{i}')
    sprites.make_group('agoutiPuextra', (a, 3), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('agoutiY', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiYextra', (a, 0), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('agoutiY', (a, 1), f'agouti{i}')
    sprites.make_group('agoutiYextra', (a, 1), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('agoutiY', (a, 2), f'agouti{i}')
    sprites.make_group('agoutiYextra', (a, 2), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('agoutiY', (a, 3), f'agouti{i}')
    sprites.make_group('agoutiYextra', (a, 3), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('agoutiG', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiGextra', (a, 0), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('agoutiG', (a, 1), f'agouti{i}')
    sprites.make_group('agoutiGextra', (a, 1), f'agoutiextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('agoutiG', (a, 2), f'agouti{i}')
    sprites.make_group('agoutiGextra', (a, 2), f'agoutiextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('agoutiG', (a, 3), f'agouti{i}')
    sprites.make_group('agoutiGextra', (a, 3), f'agoutiextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('backedBl', (a, 0), f'backed{i}')
    sprites.make_group('backedBlextra', (a, 0), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('backedBl', (a, 1), f'backed{i}')
    sprites.make_group('backedBlextra', (a, 1), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('backedBl', (a, 2), f'backed{i}')
    sprites.make_group('backedBlextra', (a, 2), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('backedPu', (a, 0), f'backed{i}')
    sprites.make_group('backedPuextra', (a, 0), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('backedPu', (a, 1), f'backed{i}')
    sprites.make_group('backedPuextra', (a, 1), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('backedPu', (a, 2), f'backed{i}')
    sprites.make_group('backedPuextra', (a, 2), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('backedPu', (a, 3), f'backed{i}')
    sprites.make_group('backedPuextra', (a, 3), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('backedY', (a, 0), f'backed{i}')
    sprites.make_group('backedYextra', (a, 0), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('backedY', (a, 1), f'backed{i}')
    sprites.make_group('backedYextra', (a, 1), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('backedY', (a, 2), f'backed{i}')
    sprites.make_group('backedYextra', (a, 2), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('backedY', (a, 3), f'backed{i}')
    sprites.make_group('backedYextra', (a, 3), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('backedG', (a, 0), f'backed{i}')
    sprites.make_group('backedGextra', (a, 0), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('backedG', (a, 1), f'backed{i}')
    sprites.make_group('backedGextra', (a, 1), f'backedextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('backedG', (a, 2), f'backed{i}')
    sprites.make_group('backedGextra', (a, 2), f'backedextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('backedG', (a, 3), f'backed{i}')
    sprites.make_group('backedGextra', (a, 3), f'backedextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('dobermanBl', (a, 0), f'doberman{i}')
    sprites.make_group('dobermanBlextra', (a, 0), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('dobermanBl', (a, 1), f'doberman{i}')
    sprites.make_group('dobermanBlextra', (a, 1), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('dobermanBl', (a, 2), f'doberman{i}')
    sprites.make_group('dobermanBlextra', (a, 2), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('dobermanPu', (a, 0), f'doberman{i}')
    sprites.make_group('dobermanPuextra', (a, 0), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('dobermanPu', (a, 1), f'doberman{i}')
    sprites.make_group('dobermanPuextra', (a, 1), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('dobermanPu', (a, 2), f'doberman{i}')
    sprites.make_group('dobermanPuextra', (a, 2), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('dobermanPu', (a, 3), f'doberman{i}')
    sprites.make_group('dobermanPuextra', (a, 3), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('dobermanY', (a, 0), f'doberman{i}')
    sprites.make_group('dobermanYextra', (a, 0), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('dobermanY', (a, 1), f'doberman{i}')
    sprites.make_group('dobermanYextra', (a, 1), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('dobermanY', (a, 2), f'doberman{i}')
    sprites.make_group('dobermanYextra', (a, 2), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('dobermanY', (a, 3), f'doberman{i}')
    sprites.make_group('dobermanYextra', (a, 3), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('dobermanG', (a, 0), f'doberman{i}')
    sprites.make_group('dobermanGextra', (a, 0), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('dobermanG', (a, 1), f'doberman{i}')
    sprites.make_group('dobermanGextra', (a, 1), f'dobermanextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('dobermanG', (a, 2), f'doberman{i}')
    sprites.make_group('dobermanGextra', (a, 2), f'dobermanextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('dobermanG', (a, 3), f'doberman{i}')
    sprites.make_group('dobermanGextra', (a, 3), f'dobermanextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('skeleBl', (a, 0), f'skele{i}')
    sprites.make_group('skeleBlextra', (a, 0), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('skeleBl', (a, 1), f'skele{i}')
    sprites.make_group('skeleBlextra', (a, 1), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('skeleBl', (a, 2), f'skele{i}')
    sprites.make_group('skeleBlextra', (a, 2), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('skelePu', (a, 0), f'skele{i}')
    sprites.make_group('skelePuextra', (a, 0), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('skelePu', (a, 1), f'skele{i}')
    sprites.make_group('skelePuextra', (a, 1), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('skelePu', (a, 2), f'skele{i}')
    sprites.make_group('skelePuextra', (a, 2), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('skelePu', (a, 3), f'skele{i}')
    sprites.make_group('skelePuextra', (a, 3), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('skeleY', (a, 0), f'skele{i}')
    sprites.make_group('skeleYextra', (a, 0), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('skeleY', (a, 1), f'skele{i}')
    sprites.make_group('skeleYextra', (a, 1), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('skeleY', (a, 2), f'skele{i}')
    sprites.make_group('skeleYextra', (a, 2), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('skeleY', (a, 3), f'skele{i}')
    sprites.make_group('skeleYextra', (a, 3), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('skeleG', (a, 0), f'skele{i}')
    sprites.make_group('skeleGextra', (a, 0), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('skeleG', (a, 1), f'skele{i}')
    sprites.make_group('skeleGextra', (a, 1), f'skeleextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('skeleG', (a, 2), f'skele{i}')
    sprites.make_group('skeleGextra', (a, 2), f'skeleextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('skeleG', (a, 3), f'skele{i}')
    sprites.make_group('skeleGextra', (a, 3), f'skeleextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('stainBl', (a, 0), f'stain{i}')
    sprites.make_group('stainBlextra', (a, 0), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('stainBl', (a, 1), f'stain{i}')
    sprites.make_group('stainBlextra', (a, 1), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('stainBl', (a, 2), f'stain{i}')
    sprites.make_group('stainBlextra', (a, 2), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('stainPu', (a, 0), f'stain{i}')
    sprites.make_group('stainPuextra', (a, 0), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('stainPu', (a, 1), f'stain{i}')
    sprites.make_group('stainPuextra', (a, 1), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('stainPu', (a, 2), f'stain{i}')
    sprites.make_group('stainPuextra', (a, 2), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('stainPu', (a, 3), f'stain{i}')
    sprites.make_group('stainPuextra', (a, 3), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('stainY', (a, 0), f'stain{i}')
    sprites.make_group('stainYextra', (a, 0), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('stainY', (a, 1), f'stain{i}')
    sprites.make_group('stainYextra', (a, 1), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('stainY', (a, 2), f'stain{i}')
    sprites.make_group('stainYextra', (a, 2), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('stainY', (a, 3), f'stain{i}')
    sprites.make_group('stainYextra', (a, 3), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('stainG', (a, 0), f'stain{i}')
    sprites.make_group('stainGextra', (a, 0), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('stainG', (a, 1), f'stain{i}')
    sprites.make_group('stainGextra', (a, 1), f'stainextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('stainG', (a, 2), f'stain{i}')
    sprites.make_group('stainGextra', (a, 2), f'stainextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('stainG', (a, 3), f'stain{i}')
    sprites.make_group('stainGextra', (a, 3), f'stainextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('mottledBl', (a, 0), f'mottled{i}')
    sprites.make_group('mottledBlextra', (a, 0), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('mottledBl', (a, 1), f'mottled{i}')
    sprites.make_group('mottledBlextra', (a, 1), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('mottledBl', (a, 2), f'mottled{i}')
    sprites.make_group('mottledBlextra', (a, 2), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('mottledPu', (a, 0), f'mottled{i}')
    sprites.make_group('mottledPuextra', (a, 0), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('mottledPu', (a, 1), f'mottled{i}')
    sprites.make_group('mottledPuextra', (a, 1), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('mottledPu', (a, 2), f'mottled{i}')
    sprites.make_group('mottledPuextra', (a, 2), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('mottledPu', (a, 3), f'mottled{i}')
    sprites.make_group('mottledPuextra', (a, 3), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('mottledY', (a, 0), f'mottled{i}')
    sprites.make_group('mottledYextra', (a, 0), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('mottledY', (a, 1), f'mottled{i}')
    sprites.make_group('mottledYextra', (a, 1), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('mottledY', (a, 2), f'mottled{i}')
    sprites.make_group('mottledYextra', (a, 2), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('mottledY', (a, 3), f'mottled{i}')
    sprites.make_group('mottledYextra', (a, 3), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('mottledG', (a, 0), f'mottled{i}')
    sprites.make_group('mottledGextra', (a, 0), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('mottledG', (a, 1), f'mottled{i}')
    sprites.make_group('mottledGextra', (a, 1), f'mottledextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('mottledG', (a, 2), f'mottled{i}')
    sprites.make_group('mottledGextra', (a, 2), f'mottledextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('mottledG', (a, 3), f'mottled{i}')
    sprites.make_group('mottledGextra', (a, 3), f'mottledextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('snowflakeBl', (a, 0), f'snowflake{i}')
    sprites.make_group('snowflakeBlextra', (a, 0), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('snowflakeBl', (a, 1), f'snowflake{i}')
    sprites.make_group('snowflakeBlextra', (a, 1), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('snowflakeBl', (a, 2), f'snowflake{i}')
    sprites.make_group('snowflakeBlextra', (a, 2), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('snowflakePu', (a, 0), f'snowflake{i}')
    sprites.make_group('snowflakePuextra', (a, 0), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('snowflakePu', (a, 1), f'snowflake{i}')
    sprites.make_group('snowflakePuextra', (a, 1), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('snowflakePu', (a, 2), f'snowflake{i}')
    sprites.make_group('snowflakePuextra', (a, 2), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('snowflakePu', (a, 3), f'snowflake{i}')
    sprites.make_group('snowflakePuextra', (a, 3), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('snowflakeY', (a, 0), f'snowflake{i}')
    sprites.make_group('snowflakeYextra', (a, 0), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('snowflakeY', (a, 1), f'snowflake{i}')
    sprites.make_group('snowflakeYextra', (a, 1), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('snowflakeY', (a, 2), f'snowflake{i}')
    sprites.make_group('snowflakeYextra', (a, 2), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('snowflakeY', (a, 3), f'snowflake{i}')
    sprites.make_group('snowflakeYextra', (a, 3), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('snowflakeG', (a, 0), f'snowflake{i}')
    sprites.make_group('snowflakeGextra', (a, 0), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('snowflakeG', (a, 1), f'snowflake{i}')
    sprites.make_group('snowflakeGextra', (a, 1), f'snowflakeextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('snowflakeG', (a, 2), f'snowflake{i}')
    sprites.make_group('snowflakeGextra', (a, 2), f'snowflakeextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('snowflakeG', (a, 3), f'snowflake{i}')
    sprites.make_group('snowflakeGextra', (a, 3), f'snowflakeextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('charcoalBl', (a, 0), f'charcoal{i}')
    sprites.make_group('charcoalBlextra', (a, 0), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('charcoalBl', (a, 1), f'charcoal{i}')
    sprites.make_group('charcoalBlextra', (a, 1), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('charcoalBl', (a, 2), f'charcoal{i}')
    sprites.make_group('charcoalBlextra', (a, 2), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('charcoalPu', (a, 0), f'charcoal{i}')
    sprites.make_group('charcoalPuextra', (a, 0), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('charcoalPu', (a, 1), f'charcoal{i}')
    sprites.make_group('charcoalPuextra', (a, 1), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('charcoalPu', (a, 2), f'charcoal{i}')
    sprites.make_group('charcoalPuextra', (a, 2), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('charcoalPu', (a, 3), f'charcoal{i}')
    sprites.make_group('charcoalPuextra', (a, 3), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('charcoalY', (a, 0), f'charcoal{i}')
    sprites.make_group('charcoalYextra', (a, 0), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('charcoalY', (a, 1), f'charcoal{i}')
    sprites.make_group('charcoalYextra', (a, 1), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('charcoalY', (a, 2), f'charcoal{i}')
    sprites.make_group('charcoalYextra', (a, 2), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('charcoalY', (a, 3), f'charcoal{i}')
    sprites.make_group('charcoalYextra', (a, 3), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('charcoalG', (a, 0), f'charcoal{i}')
    sprites.make_group('charcoalGextra', (a, 0), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('charcoalG', (a, 1), f'charcoal{i}')
    sprites.make_group('charcoalGextra', (a, 1), f'charcoalextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('charcoalG', (a, 2), f'charcoal{i}')
    sprites.make_group('charcoalGextra', (a, 2), f'charcoalextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('charcoalG', (a, 3), f'charcoal{i}')
    sprites.make_group('charcoalGextra', (a, 3), f'charcoalextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('ghostBl', (a, 0), f'ghost{i}')
    sprites.make_group('ghostBlextra', (a, 0), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('ghostBl', (a, 1), f'ghost{i}')
    sprites.make_group('ghostBlextra', (a, 1), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('ghostBl', (a, 2), f'ghost{i}')
    sprites.make_group('ghostBlextra', (a, 2), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('ghostPu', (a, 0), f'ghost{i}')
    sprites.make_group('ghostPuextra', (a, 0), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('ghostPu', (a, 1), f'ghost{i}')
    sprites.make_group('ghostPuextra', (a, 1), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('ghostPu', (a, 2), f'ghost{i}')
    sprites.make_group('ghostPuextra', (a, 2), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('ghostPu', (a, 3), f'ghost{i}')
    sprites.make_group('ghostPuextra', (a, 3), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('ghostY', (a, 0), f'ghost{i}')
    sprites.make_group('ghostYextra', (a, 0), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('ghostY', (a, 1), f'ghost{i}')
    sprites.make_group('ghostYextra', (a, 1), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('ghostY', (a, 2), f'ghost{i}')
    sprites.make_group('ghostYextra', (a, 2), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('ghostY', (a, 3), f'ghost{i}')
    sprites.make_group('ghostYextra', (a, 3), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('ghostG', (a, 0), f'ghost{i}')
    sprites.make_group('ghostGextra', (a, 0), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('ghostG', (a, 1), f'ghost{i}')
    sprites.make_group('ghostGextra', (a, 1), f'ghostextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('ghostG', (a, 2), f'ghost{i}')
    sprites.make_group('ghostGextra', (a, 2), f'ghostextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('ghostG', (a, 3), f'ghost{i}')
    sprites.make_group('ghostGextra', (a, 3), f'ghostextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('merleBl', (a, 0), f'merle{i}')
    sprites.make_group('merleBlextra', (a, 0), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('merleBl', (a, 1), f'merle{i}')
    sprites.make_group('merleBlextra', (a, 1), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('merleBl', (a, 2), f'merle{i}')
    sprites.make_group('merleBlextra', (a, 2), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('merlePu', (a, 0), f'merle{i}')
    sprites.make_group('merlePuextra', (a, 0), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('merlePu', (a, 1), f'merle{i}')
    sprites.make_group('merlePuextra', (a, 1), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('merlePu', (a, 2), f'merle{i}')
    sprites.make_group('merlePuextra', (a, 2), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('merlePu', (a, 3), f'merle{i}')
    sprites.make_group('merlePuextra', (a, 3), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('merleY', (a, 0), f'merle{i}')
    sprites.make_group('merleYextra', (a, 0), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('merleY', (a, 1), f'merle{i}')
    sprites.make_group('merleYextra', (a, 1), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('merleY', (a, 2), f'merle{i}')
    sprites.make_group('merleYextra', (a, 2), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('merleY', (a, 3), f'merle{i}')
    sprites.make_group('merleYextra', (a, 3), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('merleG', (a, 0), f'merle{i}')
    sprites.make_group('merleGextra', (a, 0), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('merleG', (a, 1), f'merle{i}')
    sprites.make_group('merleGextra', (a, 1), f'merleextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('merleG', (a, 2), f'merle{i}')
    sprites.make_group('merleGextra', (a, 2), f'merleextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('merleG', (a, 3), f'merle{i}')
    sprites.make_group('merleGextra', (a, 3), f'merleextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('ratBl', (a, 0), f'rat{i}')
    sprites.make_group('ratBlextra', (a, 0), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('ratBl', (a, 1), f'rat{i}')
    sprites.make_group('ratBlextra', (a, 1), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('ratBl', (a, 2), f'rat{i}')
    sprites.make_group('ratBlextra', (a, 2), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('ratPu', (a, 0), f'rat{i}')
    sprites.make_group('ratPuextra', (a, 0), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('ratPu', (a, 1), f'rat{i}')
    sprites.make_group('ratPuextra', (a, 1), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('ratPu', (a, 2), f'rat{i}')
    sprites.make_group('ratPuextra', (a, 2), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('ratPu', (a, 3), f'rat{i}')
    sprites.make_group('ratPuextra', (a, 3), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('ratY', (a, 0), f'rat{i}')
    sprites.make_group('ratYextra', (a, 0), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('ratY', (a, 1), f'rat{i}')
    sprites.make_group('ratYextra', (a, 1), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('ratY', (a, 2), f'rat{i}')
    sprites.make_group('ratYextra', (a, 2), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('ratY', (a, 3), f'rat{i}')
    sprites.make_group('ratYextra', (a, 3), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('ratG', (a, 0), f'rat{i}')
    sprites.make_group('ratGextra', (a, 0), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('ratG', (a, 1), f'rat{i}')
    sprites.make_group('ratGextra', (a, 1), f'ratextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('ratG', (a, 2), f'rat{i}')
    sprites.make_group('ratGextra', (a, 2), f'ratextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('ratG', (a, 3), f'rat{i}')
    sprites.make_group('ratGextra', (a, 3), f'ratextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('hoodedBl', (a, 0), f'hooded{i}')
    sprites.make_group('hoodedBlextra', (a, 0), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('hoodedBl', (a, 1), f'hooded{i}')
    sprites.make_group('hoodedBlextra', (a, 1), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('hoodedBl', (a, 2), f'hooded{i}')
    sprites.make_group('hoodedBlextra', (a, 2), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('hoodedPu', (a, 0), f'hooded{i}')
    sprites.make_group('hoodedPuextra', (a, 0), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('hoodedPu', (a, 1), f'hooded{i}')
    sprites.make_group('hoodedPuextra', (a, 1), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('hoodedPu', (a, 2), f'hooded{i}')
    sprites.make_group('hoodedPuextra', (a, 2), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('hoodedPu', (a, 3), f'hooded{i}')
    sprites.make_group('hoodedPuextra', (a, 3), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('hoodedY', (a, 0), f'hooded{i}')
    sprites.make_group('hoodedYextra', (a, 0), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('hoodedY', (a, 1), f'hooded{i}')
    sprites.make_group('hoodedYextra', (a, 1), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('hoodedY', (a, 2), f'hooded{i}')
    sprites.make_group('hoodedYextra', (a, 2), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('hoodedY', (a, 3), f'hooded{i}')
    sprites.make_group('hoodedYextra', (a, 3), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('hoodedG', (a, 0), f'hooded{i}')
    sprites.make_group('hoodedGextra', (a, 0), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('hoodedG', (a, 1), f'hooded{i}')
    sprites.make_group('hoodedGextra', (a, 1), f'hoodedextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('hoodedG', (a, 2), f'hooded{i}')
    sprites.make_group('hoodedGextra', (a, 2), f'hoodedextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('hoodedG', (a, 3), f'hooded{i}')
    sprites.make_group('hoodedGextra', (a, 3), f'hoodedextra{i}', sprites_y=2)	
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
for a, i in enumerate(['PALEBOW', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM']):
    sprites.make_group('skittyBl', (a, 0), f'skitty{i}')
    sprites.make_group('skittyBlextra', (a, 0), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC']):
    sprites.make_group('skittyBl', (a, 1), f'skitty{i}')
    sprites.make_group('skittyBlextra', (a, 1), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW']):
    sprites.make_group('skittyBl', (a, 2), f'skitty{i}')
    sprites.make_group('skittyBlextra', (a, 2), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA']):
    sprites.make_group('skittyPu', (a, 0), f'skitty{i}')
    sprites.make_group('skittyPuextra', (a, 0), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT']):
    sprites.make_group('skittyPu', (a, 1), f'skitty{i}')
    sprites.make_group('skittyPuextra', (a, 1), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['PURPLE', 'WINE', 'RASIN']):
    sprites.make_group('skittyPu', (a, 2), f'skitty{i}')
    sprites.make_group('skittyPuextra', (a, 2), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['GENDER', 'REDNEG']):
    sprites.make_group('skittyPu', (a, 3), f'skitty{i}')
    sprites.make_group('skittyPuextra', (a, 3), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT']):
    sprites.make_group('skittyY', (a, 0), f'skitty{i}')
    sprites.make_group('skittyYextra', (a, 0), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY']):
    sprites.make_group('skittyY', (a, 1), f'skitty{i}')
    sprites.make_group('skittyYextra', (a, 1), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA']):
    sprites.make_group('skittyY', (a, 2), f'skitty{i}')
    sprites.make_group('skittyYextra', (a, 2), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['SADDLE', 'CEDAR', 'ONYX']):
    sprites.make_group('skittyY', (a, 3), f'skitty{i}')
    sprites.make_group('skittyYextra', (a, 3), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD']):
    sprites.make_group('skittyG', (a, 0), f'skitty{i}')
    sprites.make_group('skittyGextra', (a, 0), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['OLIVE', 'DARKOLIVE', 'GREEN', 'FOREST', 'JADE']):
    sprites.make_group('skittyG', (a, 1), f'skitty{i}')
    sprites.make_group('skittyGextra', (a, 1), f'skittyextra{i}', sprites_y=2)
for a, i in enumerate(['SPINNACH', 'SEAWEED', 'SACRAMENTO']):
    sprites.make_group('skittyG', (a, 2), f'skitty{i}')
    sprites.make_group('skittyGextra', (a, 2), f'skittyextra{i}', sprites_y=2)	
for a, i in enumerate(['XANADU', 'DEEPFOREST']):
    sprites.make_group('skittyG', (a, 3), f'skitty{i}')
    sprites.make_group('skittyGextra', (a, 3), f'skittyextra{i}', sprites_y=2)	

#PridePELTS(For Torties)
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('pridebase', (a, 0), f'single{i}')
    sprites.make_group('pridebaseextra', (a, 0), f'singleextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('agoutiP', (a, 0), f'agouti{i}')
    sprites.make_group('agoutiPextra', (a, 0), f'agoutiextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('backedP', (a, 0), f'backed{i}')
    sprites.make_group('backedPextra', (a, 0), f'backedextra{i}', sprites_y=2)	    
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('bengalP', (a, 0), f'bengal{i}')
    sprites.make_group('bengalPextra', (a, 0), f'bengalextra{i}', sprites_y=2)	 
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('charcoalP', (a, 0), f'charcoal{i}')
    sprites.make_group('charcoalPextra', (a, 0), f'charcoalextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('classicP', (a, 0), f'classic{i}')
    sprites.make_group('classicPextra', (a, 0), f'classicextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('dobermanP', (a, 0), f'doberman{i}')
    sprites.make_group('dobermanPextra', (a, 0), f'dobermanextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('ghostP', (a, 0), f'ghost{i}')
    sprites.make_group('ghostPextra', (a, 0), f'ghostextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('hoodedP', (a, 0), f'hooded{i}')
    sprites.make_group('hoodedPextra', (a, 0), f'hoodedextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('mackerelP', (a, 0), f'mackerel{i}')
    sprites.make_group('mackerelPextra', (a, 0), f'mackerelextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('marbleP', (a, 0), f'marbled{i}')
    sprites.make_group('marblePextra', (a, 0), f'marbledextra{i}', sprites_y=2)	 
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('merleP', (a, 0), f'merle{i}')
    sprites.make_group('merlePextra', (a, 0), f'merleextra{i}', sprites_y=2)	 
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('mottledP', (a, 0), f'mottled{i}')
    sprites.make_group('mottledPextra', (a, 0), f'mottledextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('ratP', (a, 0), f'rat{i}')
    sprites.make_group('ratPextra', (a, 0), f'ratextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('rosetteP', (a, 0), f'rosette{i}')
    sprites.make_group('rosettePextra', (a, 0), f'rosetteextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('skeleP', (a, 0), f'skele{i}')
    sprites.make_group('skelePextra', (a, 0), f'skeleextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('skittyP', (a, 0), f'skitty{i}')
    sprites.make_group('skittyPextra', (a, 0), f'skittyextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('smokeP', (a, 0), f'smoke{i}')
    sprites.make_group('smokePextra', (a, 0), f'smokeextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('snowflakeP', (a, 0), f'snowflake{i}')
    sprites.make_group('snowflakePextra', (a, 0), f'snowflakeextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('sokokeP', (a, 0), f'sokoke{i}')
    sprites.make_group('sokokePextra', (a, 0), f'sokokeextra{i}', sprites_y=2)	
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('speckledP', (a, 0), f'speckled{i}')
    sprites.make_group('speckledPextra', (a, 0), f'speckledextra{i}', sprites_y=2)	 
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('stainP', (a, 0), f'stain{i}')
    sprites.make_group('stainPextra', (a, 0), f'stainextra{i}', sprites_y=2)	 
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('tabbyP', (a, 0), f'tabby{i}')
    sprites.make_group('tabbyPextra', (a, 0), f'tabbyextra{i}', sprites_y=2)	 
for a, i in enumerate(['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']):
    sprites.make_group('tickedP', (a, 0), f'ticked{i}')
    sprites.make_group('tickedPextra', (a, 0), f'tickedextra{i}', sprites_y=2)	
 
# sphynxes
sprites.make_group('skin_sphynx', (0, 0), 'skinS_BLACK')
sprites.make_group('skinextra_sphynx', (0, 0), 'skinextraS_BLACK', sprites_y=2)
sprites.make_group('skin_sphynx', (1, 0), 'skinS_RED')
sprites.make_group('skinextra_sphynx', (1, 0), 'skinextraS_RED', sprites_y=2)
sprites.make_group('skin_sphynx', (2, 0), 'skinS_PINK')
sprites.make_group('skinextra_sphynx', (2, 0), 'skinextraS_PINK', sprites_y=2)
sprites.make_group('skin_sphynx', (3, 0), 'skinS_DARKBROWN')
sprites.make_group('skinextra_sphynx', (3, 0), 'skinextraS_DARKBROWN', sprites_y=2)
sprites.make_group('skin_sphynx', (4, 0), 'skinS_BROWN')
sprites.make_group('skinextra_sphynx', (4, 0), 'skinextraS_BROWN', sprites_y=2)
sprites.make_group('skin_sphynx', (5, 0), 'skinS_LIGHTBROWN')
sprites.make_group('skinextra_sphynx', (5, 0), 'skinextraS_LIGHTBROWN', sprites_y=2)
sprites.make_group('skin_sphynx', (0, 1), 'skinS_DARK')
sprites.make_group('skinextra_sphynx', (0, 1), 'skinextraS_DARK', sprites_y=2)
sprites.make_group('skin_sphynx', (1, 1), 'skinS_DARKGREY')
sprites.make_group('skinextra_sphynx', (1, 1), 'skinextraS_DARKGREY', sprites_y=2)
sprites.make_group('skin_sphynx', (2, 1), 'skinS_GREY')
sprites.make_group('skinextra_sphynx', (2, 1), 'skinextraS_GREY', sprites_y=2)
sprites.make_group('skin_sphynx', (3, 1), 'skinS_DARKSALMON')
sprites.make_group('skinextra_sphynx', (3, 1), 'skinextraS_DARKSALMON', sprites_y=2)
sprites.make_group('skin_sphynx', (4, 1), 'skinS_SALMON')
sprites.make_group('skinextra_sphynx', (4, 1), 'skinextraS_SALMON', sprites_y=2)
sprites.make_group('skin_sphynx', (5, 1), 'skinS_PEACH')
sprites.make_group('skinextra_sphynx', (5, 1), 'skinextraS_PEACH', sprites_y=2)
sprites.make_group('skin_sphynx', (0, 2), 'skinS_DARKMARBLED')
sprites.make_group('skinextra_sphynx', (0, 2), 'skinextraS_DARKMARBLED', sprites_y=2)
sprites.make_group('skin_sphynx', (1, 2), 'skinS_MARBLED')
sprites.make_group('skinextra_sphynx', (1, 2), 'skinextraS_MARBLED', sprites_y=2)
sprites.make_group('skin_sphynx', (2, 2), 'skinS_LIGHTMARBLED')
sprites.make_group('skinextra_sphynx', (2, 2), 'skinextraS_LIGHTMARBLED', sprites_y=2)
sprites.make_group('skin_sphynx', (3, 2), 'skinS_DARKBLUE')
sprites.make_group('skinextra_sphynx', (3, 2), 'skinextraS_DARKBLUE', sprites_y=2)
sprites.make_group('skin_sphynx', (4, 2), 'skinS_BLUE')
sprites.make_group('skinextra_sphynx', (4, 2), 'skinextraS_BLUE', sprites_y=2)
sprites.make_group('skin_sphynx', (5, 2), 'skinS_LIGHTBLUE')
sprites.make_group('skinextra_sphynx', (5, 2), 'skinextraS_LIGHTBLUE', sprites_y=2)
sprites.make_group('skin2', (0, 2), 'skinS_ALBINOPINK')
sprites.make_group('skin2extra', (0, 2), 'skinextraS_ALBINOPINK', sprites_y=2)
sprites.make_group('skin2', (1, 2), 'skinS_ALBINOBLUE')
sprites.make_group('skin2extra', (1, 2), 'skinextraS_ALBINOBLUE', sprites_y=2)
sprites.make_group('skin2', (2, 2), 'skinS_ALBINORED')
sprites.make_group('skin2extra', (2, 2), 'skinextraS_ALBINORED', sprites_y=2)
sprites.make_group('skin2', (3, 2), 'skinS_ALBINOVIOLET')
sprites.make_group('skin2extra', (3, 2), 'skinextraS_ALBINOVIOLET', sprites_y=2)
sprites.make_group('skin2', (4, 2), 'skinS_ALBINOYELLOW')
sprites.make_group('skin2extra', (4, 2), 'skinextraS_ALBINOYELLOW', sprites_y=2)
sprites.make_group('skin2', (5, 2), 'skinS_ALBINOGREEN')
sprites.make_group('skin2extra', (5, 2), 'skinextraS_ALBINOGREEN', sprites_y=2)
sprites.make_group('skin2', (3, 1), 'skinS_MELANISTICLIGHT')
sprites.make_group('skin2extra', (3, 1), 'skinextraS_MELANISTICLIGHT', sprites_y=2)
sprites.make_group('skin2', (4, 1), 'skinS_MELANISTIC')
sprites.make_group('skin2extra', (4, 1), 'skinextraS_MELANISTIC', sprites_y=2)
sprites.make_group('skin2', (5, 1), 'skinS_MELANISTICDARK')
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
sprites.make_group('skin3', (3, 2), 'skinXANADU')

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
sprites.make_group('skin3extra', (3, 2), 'skinextraXANADU', sprites_y=2)

#SKINS MAGIC
sprites.make_group('skin3', (0, 0), 'skinFIRE')
sprites.make_group('skin3extra', (0, 0), 'skinextraFIRE', sprites_y=2)
sprites.make_group('skin3', (1, 0), 'skinWATER')
sprites.make_group('skin3extra', (1, 0), 'skinextraWATER', sprites_y=2)
sprites.make_group('skin3', (2, 0), 'skinEARTH')
sprites.make_group('skin3extra', (2, 0), 'skinextraEARTH', sprites_y=2)
sprites.make_group('skin3', (3, 0), 'skinWIND')
sprites.make_group('skin3extra', (3, 0), 'skinextraWIND', sprites_y=2)
sprites.make_group('skin3', (4, 0), 'skinSTAR')
sprites.make_group('skin3extra', (4, 0), 'skinextraSTAR', sprites_y=2)
sprites.make_group('skin3', (5, 0), 'skinBLOOD')
sprites.make_group('skin3extra', (5, 0), 'skinextraBLOOD', sprites_y=2)
sprites.make_group('skin3', (0, 1), 'skinSTEAM')
sprites.make_group('skin3extra', (0, 1), 'skinextraSTEAM', sprites_y=2)
sprites.make_group('skin3', (1, 1), 'skinMAGMA')
sprites.make_group('skin3extra', (1, 1), 'skinextraMAGMA', sprites_y=2)
sprites.make_group('skin3', (2, 1), 'skinSMOKE')
sprites.make_group('skin3extra', (2, 1), 'skinextraSMOKE', sprites_y=2)
sprites.make_group('skin3', (3, 1), 'skinHELL')
sprites.make_group('skin3extra', (3, 1), 'skinextraHELL', sprites_y=2)
sprites.make_group('skin3', (4, 1), 'skinMUD')
sprites.make_group('skin3extra', (4, 1), 'skinextraMUD', sprites_y=2)
sprites.make_group('skin3', (5, 1), 'skinSTORM')
sprites.make_group('skin3extra', (5, 1), 'skinextraSTORM', sprites_y=2)
sprites.make_group('skin3', (0, 2), 'skinSAND')
sprites.make_group('skin3extra', (0, 2), 'skinextraSAND', sprites_y=2)
sprites.make_group('skin3', (1, 2), 'skinBERRY')
sprites.make_group('skin3extra', (1, 2), 'skinextraBERRY', sprites_y=2)
sprites.make_group('skin3', (2, 2), 'skinGHOST')
sprites.make_group('skin3extra', (2, 2), 'skinextraGHOST', sprites_y=2)
sprites.make_group('skin3_sphynx', (0, 0), 'skinS_FIRE')
sprites.make_group('skin3extra_sphynx', (0, 0), 'skinextra_FIRE', sprites_y=2)
sprites.make_group('skin3_sphynx', (1, 0), 'skinS_WATER')
sprites.make_group('skin3extra_sphynx', (1, 0), 'skinextraS_WATER', sprites_y=2)
sprites.make_group('skin3_sphynx', (2, 0), 'skinS_EARTH')
sprites.make_group('skin3extra_sphynx', (2, 0), 'skinextraS_EARTH', sprites_y=2)
sprites.make_group('skin3_sphynx', (3, 0), 'skinS_WIND')
sprites.make_group('skin3extra_sphynx', (3, 0), 'skinextraS_WIND', sprites_y=2)
sprites.make_group('skin3_sphynx', (4, 0), 'skinS_STAR')
sprites.make_group('skin3extra_sphynx', (4, 0), 'skinextraS_STAR', sprites_y=2)
sprites.make_group('skin3_sphynx', (5, 0), 'skinS_BLOOD')
sprites.make_group('skin3extra_sphynx', (5, 0), 'skinextraS_BLOOD', sprites_y=2)
sprites.make_group('skin3_sphynx', (0, 1), 'skinS_STEAM')
sprites.make_group('skin3extra_sphynx', (0, 1), 'skinextraS_STEAM', sprites_y=2)
sprites.make_group('skin3_sphynx', (1, 1), 'skinS_MAGMA')
sprites.make_group('skin3extra_sphynx', (1, 1), 'skinextraS_MAGMA', sprites_y=2)
sprites.make_group('skin3_sphynx', (2, 1), 'skinS_SMOKE')
sprites.make_group('skin3extra_sphynx', (2, 1), 'skinextraS_SMOKE', sprites_y=2)
sprites.make_group('skin3_sphynx', (3, 1), 'skinS_HELL')
sprites.make_group('skin3extra_sphynx', (3, 1), 'skinextraS_HELL', sprites_y=2)
sprites.make_group('skin3_sphynx', (4, 1), 'skinS_MUD')
sprites.make_group('skin3extra_sphynx', (4, 1), 'skinextraS_MUD', sprites_y=2)
sprites.make_group('skin3_sphynx', (5, 1), 'skinS_STORM')
sprites.make_group('skin3extra_sphynx', (5, 1), 'skinextraS_STORM', sprites_y=2)
sprites.make_group('skin3_sphynx', (0, 2), 'skinS_SAND')
sprites.make_group('skin3extra_sphynx', (0, 2), 'skinextraS_SAND', sprites_y=2)
sprites.make_group('skin3_sphynx', (1, 2), 'skinS_BERRY')
sprites.make_group('skin3extra_sphynx', (1, 2), 'skinextraS_BERRY', sprites_y=2)
sprites.make_group('skin3_sphynx', (2, 2), 'skinS_GHOST')
sprites.make_group('skin3extra_sphynx', (2, 2), 'skinextraS_GHOST', sprites_y=2)


#SKINS ALBINO/MELANISTIC 
sprites.make_group('skin2', (0, 0), 'skinALBINOPINK')
sprites.make_group('skin2extra', (0, 0), 'skinextraALBINOPINK', sprites_y=2)
sprites.make_group('skin2', (1, 0), 'skinALBINOBLUE')
sprites.make_group('skin2extra', (1, 0), 'skinextraALBINOBLUE', sprites_y=2)
sprites.make_group('skin2', (2, 0), 'skinALBINORED')
sprites.make_group('skin2extra', (2, 0), 'skinextraALBINORED', sprites_y=2)
sprites.make_group('skin2', (3, 0), 'skinALBINOVIOLET')
sprites.make_group('skin2extra', (3, 0), 'skinextraALBINOVIOLET', sprites_y=2)
sprites.make_group('skin2', (4, 0), 'skinALBINOYELLOW')
sprites.make_group('skin2extra', (4, 0), 'skinextraALBINOYELLOW', sprites_y=2)
sprites.make_group('skin2', (5, 0), 'skinALBINOGREEN')
sprites.make_group('skin2extra', (5, 0), 'skinextraALBINOGREEN', sprites_y=2)
sprites.make_group('skin2', (0, 1), 'skinMELANISTICLIGHT')
sprites.make_group('skin2extra', (0, 1), 'skinextraMELANISTICLIGHT', sprites_y=2)
sprites.make_group('skin2', (1, 1), 'skinMELANISTIC')
sprites.make_group('skin2extra', (1, 1), 'skinextraMELANISTIC', sprites_y=2)
sprites.make_group('skin2', (2, 1), 'skinMELANISTICDARK')
sprites.make_group('skin2extra', (2, 1), 'skinextraMELANISTICDARK', sprites_y=2)

#SKINS WINGS
sprites.make_group('wings2', (0, 1), 'skinMELANISTICLIGHTWING')
sprites.make_group('wings2extra', (0, 1), 'skinextraMELANISTICLIGHTWING', sprites_y=2)
sprites.make_group('wings2', (1, 1), 'skinMELANISTICWING')
sprites.make_group('wings2extra', (1, 1), 'skinextraMELANISTICWING', sprites_y=2)
sprites.make_group('wings2', (2, 1), 'skinMELANISTICDARKWING')
sprites.make_group('wings2extra', (2, 1), 'skinextraMELANISTICDARKWING', sprites_y=2)
sprites.make_group('wings2', (0, 2), 'skinALBINOPINKWING')
sprites.make_group('wings2extra', (0, 2), 'skinextraALBINOPINKWING', sprites_y=2)
sprites.make_group('wings2', (1, 0), 'skinALBINOBLUEWING')
sprites.make_group('wings2extra', (1, 0), 'skinextraALBINOBLUEWING', sprites_y=2)
sprites.make_group('wings2', (2, 0), 'skinALBINOREDWING')
sprites.make_group('wings2extra', (2, 0), 'skinextraALBINOREDWING', sprites_y=2)
sprites.make_group('wings2', (3, 0), 'skinALBINOVIOLETWING')
sprites.make_group('wings2extra', (3, 0), 'skinextraALBINOVIOLETWING', sprites_y=2)
sprites.make_group('wings2', (4, 0), 'skinALBINOYELLOWWING')
sprites.make_group('wings2extra', (4, 0), 'skinextraALBINOYELLOWWING', sprites_y=2)
sprites.make_group('wings2', (5, 0), 'skinALBINOGREENWING')
sprites.make_group('wings2extra', (5, 0), 'skinextraALBINOGREENWING', sprites_y=2)

sprites.make_group('wings', (0, 0), 'skinWHITEWING')
sprites.make_group('wingsextra', (0, 0), 'skinextraWHITEWING', sprites_y=2)
sprites.make_group('wings', (1, 0), 'skinBLUEGREENWING')
sprites.make_group('wingsextra', (1, 0), 'skinextraBLUEGREENWING', sprites_y=2)
sprites.make_group('wings', (2, 0), 'skinREDWING')
sprites.make_group('wingsextra', (2, 0), 'skinextraREDWING', sprites_y=2)
sprites.make_group('wings', (3, 0), 'skinPURPLEFADEWING')
sprites.make_group('wingsextra', (3, 0), 'skinextraPURPLEFADEWING', sprites_y=2)
sprites.make_group('wings', (4, 0), 'skinRAINBOWWING')
sprites.make_group('wingsextra', (4, 0), 'skinextraRAINBOWWING', sprites_y=2)
sprites.make_group('wings', (5, 0), 'skinSILVERWING')
sprites.make_group('wingsextra', (5, 0), 'skinextraSILVERWING', sprites_y=2)
sprites.make_group('wings', (0, 1), 'skinSTRAKITWING')
sprites.make_group('wingsextra', (0, 1), 'skinextraSTRAKITWING', sprites_y=2)
sprites.make_group('wings', (1, 1), 'skinSONICWING')
sprites.make_group('wingsextra', (1, 1), 'skinextraSONICWING', sprites_y=2)
sprites.make_group('wings', (2, 1), 'skinMEWWING')
sprites.make_group('wingsextra', (2, 1), 'skinextraMEWWING', sprites_y=2)
sprites.make_group('wings', (3, 1), 'skinOLIVEWING')
sprites.make_group('wingsextra', (3, 1), 'skinextraOLIVEWING', sprites_y=2)
sprites.make_group('wings', (4, 1), 'skinGREENWING')
sprites.make_group('wingsextra', (4, 1), 'skinextraGREENWING', sprites_y=2)
sprites.make_group('wings', (5, 1), 'skinGREYWING')
sprites.make_group('wingsextra', (5, 1), 'skinextraGREYWING', sprites_y=2)
sprites.make_group('wings', (0, 2), 'skinGREYFADEWING')
sprites.make_group('wingsextra', (0, 2), 'skinextraGREYFADEWING', sprites_y=2)
sprites.make_group('wings', (1, 2), 'skinBROWNFADEWING')
sprites.make_group('wingsextra', (1, 2), 'skinextraBROWNFADEWING', sprites_y=2)
sprites.make_group('wings', (2, 2), 'skinPARROTWING')
sprites.make_group('wingsextra', (2, 2), 'skinextraPARROTWING', sprites_y=2)
sprites.make_group('wings', (3, 2), 'skinGOLDWING')
sprites.make_group('wingsextra', (3, 2), 'skinextraGOLDWING', sprites_y=2)
sprites.make_group('wings', (4, 2), 'skinLIGHTBROWNWING')
sprites.make_group('wingsextra', (4, 2), 'skinextraLIGHTBROWNWING', sprites_y=2)
sprites.make_group('wings', (5, 2), 'skinBLACKWING')
sprites.make_group('wingsextra', (5, 2), 'skinextraBLACKWING', sprites_y=2)

# tiles.make_group('dithered', (0, 0), 'terrain')
# tiles.make_group('dithered', (1, 0), 'terraintwo')

sprites.load_scars()
