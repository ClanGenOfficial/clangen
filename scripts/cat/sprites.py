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
                   sprites_y=7):  # pos = ex. (2, 3), no single pixels
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
        for a, i in enumerate(
                ["ONE", "TWO", "THREE", "MANLEG", "BRIGHTHEART", "MANTAIL", 
                 "BRIDGE", "RIGHTBLIND", "LEFTBLIND", "BOTHBLIND", "BURNPAWS", "BURNTAIL"]):
            sprites.make_group('scars', (a, 0), f'scars{i}')
        for a, i in enumerate(
                ["BURNBELLY", "BEAKCHEEK", "BEAKLOWER", "BURNRUMP", "CATBITE", "RATBITE",
                 "FROSTFACE", "FROSTTAIL", "FROSTMITT", "FROSTSOCK", "QUILLCHUNK", "QUILLSCRATCH"]):
            sprites.make_group('scars', (a, 1), f'scars{i}')
        for a, i in enumerate(
                ["TAILSCAR", "SNOUT", "CHEEK", "SIDE", "THROAT", "TAILBASE", "BELLY", "TOETRAP", "SNAKE",
                 "LEGBITE", "NECKBITE", "FACE"]):
            sprites.make_group('scars', (a, 2), f'scars{i}')
        # missing parts
        for a, i in enumerate(
                ["LEFTEAR", "RIGHTEAR", "NOTAIL", "NOLEFTEAR", "NORIGHTEAR", "NOEAR", "HALFTAIL", "NOPAW"]):
            sprites.make_group('missingscars', (a, 0), f'scars{i}')

            # Accessories
        for a, i in enumerate([
            "MAPLE LEAF", "HOLLY", "BLUE BERRIES", "FORGET ME NOTS", "RYE STALK", "LAUREL"]):
            sprites.make_group('medcatherbs', (a, 0), f'acc_herbs{i}')
        for a, i in enumerate([
            "BLUEBELLS", "NETTLE", "POPPY", "LAVENDER", "HERBS", "PETALS"]):
            sprites.make_group('medcatherbs', (a, 1), f'acc_herbs{i}')
        for a, i in enumerate([
            "OAK LEAVES", "CATMINT", "MAPLE SEED", "JUNIPER"]):
            sprites.make_group('medcatherbs', (a, 3), f'acc_herbs{i}')
        sprites.make_group('medcatherbs', (5, 2), 'acc_herbsDRY HERBS')

        for a, i in enumerate([
            "RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS", "MOTH WINGS", "CICADA WINGS"]):
            sprites.make_group('medcatherbs', (a, 2), f'acc_wild{i}')
        for a, i in enumerate(["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME"]):
            sprites.make_group('collars', (a, 0), f'collars{i}')
        for a, i in enumerate(["GREEN", "RAINBOW", "BLACK", "SPIKES", "WHITE"]):
            sprites.make_group('collars', (a, 1), f'collars{i}')
        for a, i in enumerate(["PINK", "PURPLE", "MULTI", "INDIGO"]):
            sprites.make_group('collars', (a, 2), f'collars{i}')
        for a, i in enumerate([
            "CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL",
            "LIMEBELL"
        ]):
            sprites.make_group('bellcollars', (a, 0), f'collars{i}')
        for a, i in enumerate(
                ["GREENBELL", "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL"]):
            sprites.make_group('bellcollars', (a, 1), f'collars{i}')
        for a, i in enumerate(["PINKBELL", "PURPLEBELL", "MULTIBELL", "INDIGOBELL"]):
            sprites.make_group('bellcollars', (a, 2), f'collars{i}')
        for a, i in enumerate([
            "CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW",
            "LIMEBOW"
        ]):
            sprites.make_group('bowcollars', (a, 0), f'collars{i}')
        for a, i in enumerate(
                ["GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW"]):
            sprites.make_group('bowcollars', (a, 1), f'collars{i}')
        for a, i in enumerate(["PINKBOW", "PURPLEBOW", "MULTIBOW", "INDIGOBOW"]):
            sprites.make_group('bowcollars', (a, 2), f'collars{i}')
        for a, i in enumerate([
            "CRIMSONNYLON", "BLUENYLON", "YELLOWNYLON", "CYANNYLON", "REDNYLON",
            "LIMENYLON"
        ]):
            sprites.make_group('nyloncollars', (a, 0), f'collars{i}')
        for a, i in enumerate(
                ["GREENNYLON", "RAINBOWNYLON", "BLACKNYLON", "SPIKESNYLON", "WHITENYLON"]):
            sprites.make_group('nyloncollars', (a, 1), f'collars{i}')
        for a, i in enumerate(["PINKNYLON", "PURPLENYLON", "MULTINYLON", "INDIGONYLON"]):
            sprites.make_group('nyloncollars', (a, 2), f'collars{i}')


sprites = Sprites(50)
#tiles = Sprites(64)

for x in [
    'lineart', 'singlecolours', 'speckledcolours', 'tabbycolours',
    'whitepatches', 'eyes', 'eyes2', 'skin', 'scars', 'missingscars',
    'collars', 'bellcollars', 'bowcollars', 'nyloncollars',
    'bengalcolours', 'marbledcolours', 'rosettecolours', 'smokecolours', 'tickedcolours', 
    'mackerelcolours', 'classiccolours', 'sokokecolours', 'agouticolours', 'singlestripecolours', 
    'shadersnewwhite', 'lineartdead', 'tortiepatchesmasks', 
    'medcatherbs', 'lineartdf', 'lightingnew', 'fademask',
    'fadestarclan', 'fadedarkforest'

]:
    sprites.spritesheet(f"sprites/{x}.png", x)

# Line art
sprites.make_group('lineart', (0, 0), 'lines')
sprites.make_group('shadersnewwhite', (0, 0), 'shaders')
sprites.make_group('lightingnew', (0, 0), 'lighting')

sprites.make_group('lineartdead', (0, 0), 'lineartdead')
sprites.make_group('lineartdf', (0, 0), 'lineartdf')

# Fading Fog
for i in range(0, 3):
    sprites.make_group('fademask', (i, 0), f'fademask{i}')
    sprites.make_group('fadestarclan', (i, 0), f'fadestarclan{i}')
    sprites.make_group('fadedarkforest', (i, 0), f'fadedf{i}')

for a, i in enumerate(
        ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 
        'DARKBLUE', 'GREY', 'CYAN', 'EMERALD', 'HEATHERBLUE', 'SUNLITICE']):
    sprites.make_group('eyes', (a, 0), f'eyes{i}')
    sprites.make_group('eyes2', (a, 0), f'eyes2{i}')
for a, i in enumerate(
        ['COPPER', 'SAGE', 'COBALT', 'PALEBLUE', 'BRONZE', 'SILVER',
        'PALEYELLOW', 'GOLD', 'GREENYELLOW']):
    sprites.make_group('eyes', (a, 1), f'eyes{i}')
    sprites.make_group('eyes2', (a, 1), f'eyes2{i}')

# white patches
for a, i in enumerate(['FULLWHITE', 'ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN', 'ANYTWO',
    'MOON', 'PHANTOM', 'POWDER']):
    sprites.make_group('whitepatches', (a, 0), f'white{i}')
for a, i in enumerate(['EXTRA', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 
    'LIGHTSONG', 'VITILIGO', 'BLACKSTAR', 'PIEBALD', 'CURVED', 'PETAL']):
    sprites.make_group('whitepatches', (a, 1), f'white{i}')
# ryos white patches
for a, i in enumerate(['TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE', 'PANTSTWO', 'GOATEE', 'VITILIGOTWO',
    'PAWS', 'MITAINE', 'BROKENBLAZE', 'SCOURGE']):
    sprites.make_group('whitepatches', (a, 2), f'white{i}')
for a, i in enumerate(['TAIL', 'BLAZE', 'PRINCE', 'BIB', 'VEE', 'UNDERS', 'HONEY',
    'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TAILTIP', 'TOES']):
    sprites.make_group('whitepatches', (a, 3), f'white{i}')
for a, i in enumerate(
        ['APRON', 'CAPSADDLE', 'MASKMANTLE', 'SQUEAKS', 'STAR', 'TOESTAIL', 'RAVENPAW',
        'PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA']):
    sprites.make_group('whitepatches', (a, 4), f'white{i}')
# beejeans white patches + perrio's point marks, painted, and heart2 + anju's new marks + key's blackstar
for a, i in enumerate(['HEART', 'LILTWO', 'GLASS', 'MOORISH', 'SEPIAPOINT', 'MINKPOINT', 'SEALPOINT',
    'MAO', 'LUNA', 'CHESTSPECK', 'WINGS', 'PAINTED', 'HEARTTWO']):
    sprites.make_group('whitepatches', (a, 5), 'white' + i)

# single (solid)
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('singlecolours', (a, 0), f'single{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('singlecolours', (a, 1), f'single{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('singlecolours', (a, 2), f'single{i}')
# tabby
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('tabbycolours', (a, 0), f'tabby{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('tabbycolours', (a, 1), f'tabby{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('tabbycolours', (a, 2), f'tabby{i}')
# marbled
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('marbledcolours', (a, 0), f'marbled{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('marbledcolours', (a, 1), f'marbled{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('marbledcolours', (a, 2), f'marbled{i}')
# rosette
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('rosettecolours', (a, 0), f'rosette{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('rosettecolours', (a, 1), f'rosette{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('rosettecolours', (a, 2), f'rosette{i}')
# smoke
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('smokecolours', (a, 0), f'smoke{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('smokecolours', (a, 1), f'smoke{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('smokecolours', (a, 2), f'smoke{i}')
# ticked
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('tickedcolours', (a, 0), f'ticked{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('tickedcolours', (a, 1), f'ticked{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('tickedcolours', (a, 2), f'ticked{i}')
# speckled
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('speckledcolours', (a, 0), f'speckled{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('speckledcolours', (a, 1), f'speckled{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('speckledcolours', (a, 2), f'speckled{i}')
# bengal
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('bengalcolours', (a, 0), f'bengal{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('bengalcolours', (a, 1), f'bengal{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('bengalcolours', (a, 2), f'bengal{i}')
# mackerel
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('mackerelcolours', (a, 0), f'mackerel{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('mackerelcolours', (a, 1), f'mackerel{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('mackerelcolours', (a, 2), f'mackerel{i}')
# classic
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('classiccolours', (a, 0), f'classic{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('classiccolours', (a, 1), f'classic{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('classiccolours', (a, 2), f'classic{i}')
# sokoke
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('sokokecolours', (a, 0), f'sokoke{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('sokokecolours', (a, 1), f'sokoke{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('sokokecolours', (a, 2), f'sokoke{i}')
# agouti
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('agouticolours', (a, 0), f'agouti{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('agouticolours', (a, 1), f'agouti{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('agouticolours', (a, 2), f'agouti{i}')
# singlestripe
for a, i in enumerate(['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'GHOST']):
    sprites.make_group('singlestripecolours', (a, 0), f'singlestripe{i}')
for a, i in enumerate(['PALEGINGER', 'GOLDEN', 'GINGER', 'DARKGINGER', 'CREAM']):
    sprites.make_group('singlestripecolours', (a, 1), f'singlestripe{i}')
for a, i in enumerate(['LIGHTBROWN', 'BROWN', 'DARKBROWN', 'BLACK']):
    sprites.make_group('singlestripecolours', (a, 2), f'singlestripe{i}')
    
# new new torties
for a, i in enumerate(['ONE', 'TWO', 'THREE', 'FOUR', 'REDTAIL', 'DELILAH']):
    sprites.make_group('tortiepatchesmasks', (a, 0), f"tortiemask{i}")
for a, i in enumerate(['MINIMALONE', 'MINIMALTWO', 'MINIMALTHREE', 'MINIMALFOUR', 'OREO', 'SWOOP']):
    sprites.make_group('tortiepatchesmasks', (a, 1), f"tortiemask{i}")
for a, i in enumerate(['MOTTLED', 'SIDEMASK', 'EYEDOT', 'BANDANA', 'PACMAN', 'STREAMSTRIKE']):
    sprites.make_group('tortiepatchesmasks', (a, 2), f"tortiemask{i}")
for a, i in enumerate(['ORIOLE', 'ROBIN', 'BRINDLE', 'PAIGE']):
    sprites.make_group('tortiepatchesmasks', (a, 3), f"tortiemask{i}")

# SKINS
for a, i in enumerate(['BLACK', 'RED', 'PINK', 'DARKBROWN', 'BROWN', 'LIGHTBROWN']):
    sprites.make_group('skin', (a, 0), f"skin{i}")
for a, i in enumerate(['DARK', 'DARKGREY', 'GREY', 'DARKSALMON', 'SALMON', 'PEACH']):
    sprites.make_group('skin', (a, 1), f"skin{i}")
for a, i in enumerate(['DARKMARBLED', 'MARBLED', 'LIGHTMARBLED', 'DARKBLUE', 'BLUE', 'LIGHTBLUE']):
    sprites.make_group('skin', (a, 2), f"skin{i}")

sprites.load_scars()
