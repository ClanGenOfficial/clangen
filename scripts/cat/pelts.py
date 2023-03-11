from random import choice


class SingleColour():
    name = "SingleColour"
    sprites = {1: 'single'}
    white_patches = None

    def __init__(self, colour, length):
        self.colour = colour
        self.length = length
        self.white = self.colour == "white"

    def __repr__(self):
        return self.colour + self.length


class TwoColour():
    name = "TwoColour"
    sprites = {1: 'single', 2: 'white'}

    def __init__(self, colour, length):
        self.colour = colour
        self.length = length
        self.white = True

    def __repr__(self):
        return f"white and {self.colour}{self.length}"


class Tabby():
    name = "Tabby"
    sprites = {1: 'tabby', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} tabby"
        else:
            return self.colour + self.length + " tabby"


class Marbled():
    name = "Marbled"
    sprites = {1: 'marbled', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} marbled"
        else:
            return self.colour + self.length + " marbled"


class Rosette():
    name = "Rosette"
    sprites = {1: 'rosette', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} rosette"
        else:
            return self.colour + self.length + " rosette"


class Smoke():
    name = "Smoke"
    sprites = {1: 'smoke', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} smoke"
        else:
            return self.colour + self.length + " smoke"


class Ticked():
    name = "Ticked"
    sprites = {1: 'ticked', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} ticked"
        else:
            return self.colour + self.length + " ticked"


class Speckled():
    name = "Speckled"
    sprites = {1: 'speckled', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour} speckled{self.length}"
        else:
            return f"{self.colour} speckled{self.length}"


class Bengal():
    name = "Bengal"
    sprites = {1: 'bengal', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour} bengal{self.length}"
        else:
            return f"{self.colour} bengal{self.length}"


class Mackerel():
    name = "Mackerel"
    sprites = {1: 'mackerel', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour} mackerel tabby{self.length}"
        else:
            return f"{self.colour} mackerel tabby{self.length}"


class Classic():
    name = "Classic"
    sprites = {1: 'classic', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour} classic tabby{self.length}"
        else:
            return f"{self.colour} classic tabby{self.length}"


class Sokoke():
    name = "Sokoke"
    sprites = {1: 'sokoke', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour} sokoke tabby{self.length}"
        else:
            return f"{self.colour} sokoke tabby{self.length}"


class Agouti():
    name = "Agouti"
    sprites = {1: 'agouti', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour} agouti{self.length}"
        else:
            return f"{self.colour} agouti{self.length}"


class Backed():
    name = "Backed"
    sprites = {1: 'backed', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length
    def __repr__(self):
        if self.white:
            return f"white and {self.colour} backed{self.length}"
        else:
            return f"{self.colour} backed{self.length}"

class Charcoal():
    name = "Charcoal"
    sprites = {1: 'charcoal', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} charcoal"
        else:
            return self.colour + self.length + " charcoal"

class Ghost():
    name = "Ghost"
    sprites = {1: 'tabby', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} ghost"
        else:
            return self.colour + self.length + " ghost"

class Merle():
    name = "Merle"
    sprites = {1: 'merle', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} merle"
        else:
            return self.colour + self.length + " merle"

class Doberman():
    name = "Doberman"
    sprites = {1: 'doberman', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} doberman"
        else:
            return self.colour + self.length + " doberman"

class Snowflake():
    name = "Snowflake"
    sprites = {1: 'snowflake', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} snowflake"
        else:
            return self.colour + self.length + " snowflake"            

class Skele():
    name = "Skele"
    sprites = {1: 'skele', 2: 'white'}
    
    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} skele"
        else:
            return self.colour + self.length + " skele"

class Stain():
    name = "Stain"
    sprites = {1: 'stain', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} stain"
        else:
            return self.colour + self.length + " stain"     

class Mottled():
    name = "Mottled"
    sprites = {1: 'mottled', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} mottled"
        else:
            return self.colour + self.length + " mottled"     

class Rat():
    name = "Rat"
    sprites = {1: 'rat', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} rat"
        else:
            return self.colour + self.length + " rat"  

class Skitty():
    name = "Skitty"
    sprites = {1: 'skitty', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} skitty"
        else:
            return self.colour + self.length + " skitty"  

class Hooded():
    name = "Hooded"
    sprites = {1: 'hooded', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} hooded"
        else:
            return self.colour + self.length + " hooded"  


class Tortie():
    name = "Tortie"
    sprites = {1: 'tortie', 2: 'white'}

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and tortoiseshell{self.length}"
        else:
            return f"tortoiseshell{self.length}"


class Calico():
    name = "Calico"
    sprites = {1: 'calico', 2: 'white'}

    def __init__(self, colour, length):
        self.colour = colour
        self.length = length
        self.white = True

    def __repr__(self):
        return f"calico{self.length}"


# ATTRIBUTES, including non-pelt related
pelt_colours = ['PALECREAM', 'CREAM', 'BEIGE', 'MEERKAT', 'KHAKI', 'SAND', 'WOOD', 'ROSE', 
    'GINGER', 'SUNSET', 'RUFOUS', 'FIRE', 'BRICK', 'RED', 'SCARLET', 'APRICOT', 'GARFIELD', 
    'APPLE', 'CRIMSON', 'BURNT', 'CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD', 'SOOT', 'DARKGREY', 
    'ANCHOR', 'CHARCOAL', 'COAL', 'BLACK', 'GREY', 'MARENGO', 'BATTLESHIP', 'CADET', 
    'BLUEGREY', 'STEEL', 'SLATE', 'CAPPUCCINO', 'ECRU', 'ASHBROWN', 'DUSTBROWN', 'SANDALWOOD', 
    'PINECONE', 'WRENGE', 'BROWN', 'MINK', 'CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 
    'CHOCOLATE', 'MOCHA', 'COFFEE', 'TAUPE', 'UMBER', 'WHITE', 'SILVER', 'BRONZE', 'PALEBOW', 
    'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM', 'SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC',
    'POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW', 'PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 
    'DARKSALMON', 'MAGENTA', 'PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT', 'PURPLE', 'WINE', 'RASIN',
    'GENDER', 'REDNEG', 'IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT', 'LEMON', 'LAGUNA', 
    'YELLOW', 'CORN', 'GOLD', 'HONEY', 'BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA', 
    'SADDLE', 'CEDAR', 'ONYX', 'LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD', 'OLIVE',
    'DARKOLIVE', 'GREEN', 'FOREST', 'JADE', 'SPINNACH', 'SEAWEED', 'SACRAMENTO', 'XANADU', 'DEEPFOREST',
    'AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']
pelt_c_no_white = ['PALECREAM', 'CREAM', 'BEIGE', 'MEERKAT', 'KHAKI', 'SAND', 'WOOD', 'ROSE', 
    'GINGER', 'SUNSET', 'RUFOUS', 'FIRE', 'BRICK', 'RED', 'SCARLET', 'APRICOT', 'GARFIELD', 
    'APPLE', 'CRIMSON', 'BURNT', 'CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD', 'SOOT', 'DARKGREY', 
    'ANCHOR', 'CHARCOAL', 'COAL', 'BLACK', 'GREY', 'MARENGO', 'BATTLESHIP', 'CADET', 
    'BLUEGREY', 'STEEL', 'SLATE', 'CAPPUCCINO', 'ECRU', 'ASHBROWN', 'DUSTBROWN', 'SANDALWOOD', 
    'PINECONE', 'WRENGE', 'BROWN', 'MINK', 'CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 
    'CHOCOLATE', 'MOCHA', 'COFFEE', 'TAUPE', 'UMBER','TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM', 
    'SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC', 'POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW', 
    'PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA', 'MEW', 
    'HEATHER', 'ORCHID', 'STRAKIT', 'PURPLE', 'WINE', 'RASIN','GENDER', 'REDNEG', 'BANNANA', 'FARROW', 
    'HAY', 'FAWN', 'HAZELNUT', 'LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY', 'BEE', 
    'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA', 'SADDLE', 'CEDAR', 'ONYX', 'LIME', 'CHARTRUSE', 
    'LETTUCE', 'GRASS', 'MINT', 'EMERALD', 'OLIVE','DARKOLIVE', 'GREEN', 'FOREST', 'JADE', 'SPINNACH', 
    'SEAWEED', 'SACRAMENTO', 'XANADU', 'DEEPFOREST', 'GAYBOW']
pelt_c_no_bw = ['PALECREAM', 'CREAM', 'BEIGE', 'MEERKAT', 'KHAKI', 'SAND', 'WOOD', 'ROSE', 
    'GINGER', 'SUNSET', 'RUFOUS', 'FIRE', 'BRICK', 'RED', 'SCARLET', 'APRICOT', 'GARFIELD', 
    'APPLE', 'CRIMSON', 'BURNT', 'CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD', 'GREY', 'MARENGO', 
    'BATTLESHIP', 'CADET', 'BLUEGREY', 'STEEL', 'SLATE', 'CAPPUCCINO', 'ECRU', 
    'ASHBROWN', 'DUSTBROWN', 'SANDALWOOD', 'PINECONE', 'WRENGE', 'BROWN', 'MINK', 
    'CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA', 'COFFEE', 'TAUPE', 'UMBER',
    'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM', 'SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC',
    'POWDERBLUE', 'JEANS', 'NAVY', 'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM', 'SHINYMEW', 
    'SKY', 'TEAL', 'COBALT', 'SONIC', 'POWDERBLUE', 'JEANS', 'NAVY', 'PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 
    'DARKSALMON', 'MAGENTA', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT', 'PURPLE', 'WINE',
    'GENDER', 'REDNEG', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT', 'LEMON', 'LAGUNA', 
    'YELLOW', 'CORN', 'GOLD', 'HONEY', 'BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA', 
    'SADDLE', 'CEDAR', 'LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD', 'OLIVE',
    'DARKOLIVE', 'GREEN', 'FOREST', 'JADE', 'SPINNACH', 'SEAWEED', 'SACRAMENTO', 'XANADU', 'DEEPFOREST',
    'GAYBOW']  

tortiepatterns = ['ONE', 'TWO', 'THREE', 'FOUR', 'REDTAIL', 'DELILAH', 'MINIMAL1', 'MINIMAL2', 'MINIMAL3', 'MINIMAL4',
                  'OREO', 'SWOOP', 'MOTTLED', 'SIDEMASK', 'EYEDOT', 'BANDANA', 'PACMAN', 'STREAMSTRIKE', 'ORIOLE',
                  'ROBIN', 'BRINDLE', 'PAIGE', 'COMBO', 'BLENDED', 'SCATTER', 'LIGHT']
tortiebases = ['single', 'tabby', 'bengal', 'marbled', 'ticked', 'smoke', 'rosette', 'speckled', 'mackerel',
               'classic', 'sokoke', 'agouti', 'backed', 'charcoal', 'ghost', 'merle', 'doberman', 'skele', 'stain', 
               'mottled', 'snowflake', 'rat', 'hooded', 'skitty']

pelt_length = ["short", "medium", "long"]
eye_colours = ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE', 'GREY', 'CYAN', 'EMERALD',
               'PALEBLUE',
               'PALEYELLOW', 'GOLD', 'HEATHERBLUE', 'COPPER', 'SAGE', 'BLUE2', 'SUNLITICE', 'GREENYELLOW']
yellow_eyes = ['YELLOW', 'AMBER', 'PALEYELLOW', 'GOLD', 'COPPER', 'GREENYELLOW']
blue_eyes = ['BLUE', 'DARKBLUE', 'CYAN', 'PALEBLUE', 'HEATHERBLUE', 'BLUE2', 'SUNLITICE', 'GREY']
green_eyes = ['PALEGREEN', 'GREEN', 'EMERALD', 'SAGE', 'HAZEL']
# scars1 is scars from other cats, other animals - scars2 is missing parts - scars3 is "special" scars that could only happen in a special event
# bite scars by @wood pank on discord
scars1 = ["ONE", "TWO", "THREE", "TAILSCAR", "SNOUT", "CHEEK", "SIDE", "THROAT", "TAILBASE", "BELLY",
          "LEGBITE", "NECKBITE", "FACE", "MANLEG", "BRIGHTHEART", "MANTAIL", "BRIDGE", "RIGHTBLIND", "LEFTBLIND",
          "BOTHBLIND", "BEAKCHEEK", "BEAKLOWER", "CATBITE", "RATBITE", "QUILLCHUNK", "QUILLSCRATCH"]
scars2 = ["LEFTEAR", "RIGHTEAR", "NOTAIL", "HALFTAIL", "NOPAW", "NOLEFTEAR", "NORIGHTEAR", "NOEAR"]
scars3 = ["SNAKE", "TOETRAP", "BURNPAWS", "BURNTAIL", "BURNBELLY", "BURNRUMP", "FROSTFACE", "FROSTTAIL", "FROSTMITT",
          "FROSTSOCK", ]

plant_accessories = ["MAPLE LEAF", "HOLLY", "BLUE BERRIES", "FORGET ME NOTS", "RYE STALK", "LAUREL",
                     "BLUEBELLS", "NETTLE", "POPPY", "LAVENDER", "HERBS", "PETALS", "DRY HERBS",
                     "OAK LEAVES", "CATMINT", "MAPLE SEED", "JUNIPER"
                     ]
wild_accessories = ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS", "MOTH WINGS", "CICADA WINGS"
                    ]
tail_accessories = ["RED FEATHERS", "BLUE FEATHERS", "JAY FEATHERS"]
collars = [
    "CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME", "GREEN", "RAINBOW",
    "BLACK", "SPIKES", "WHITE", "PINK", "PURPLE", "MULTI", "INDIGO", "CRIMSONBELL", "BLUEBELL",
    "YELLOWBELL", "CYANBELL", "REDBELL", "LIMEBELL", "GREENBELL",
    "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "WHITEBELL", "PINKBELL", "PURPLEBELL",
    "MULTIBELL", "INDIGOBELL", "CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW",
    "LIMEBOW", "GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "WHITEBOW", "PINKBOW",
    "PURPLEBOW", "MULTIBOW", "INDIGOBOW", "CRIMSONNYLON", "BLUENYLON", "YELLOWNYLON", "CYANNYLON",
    "REDNYLON", "LIMENYLON", "GREENNYLON", "RAINBOWNYLON",
    "BLACKNYLON", "SPIKESNYLON", "WHITENYLON", "PINKNYLON", "PURPLENYLON", "MULTINYLON", "INDIGONYLON",
]

tabbies = ["Tabby", "Ticked", "Mackerel", "Classic", "Sokoke", "Agouti", "Merle"]
spotted = ["Speckled", "Rosette", "Snowflake", "Mottled"]
plain = ["SingleColour", "TwoColour", "Smoke", "Backed", "Doberman", "Skitty", "Rat"]
exotic = ["Bengal", "Marbled", "Skele", "Stain", "Charcoal", "Hooded"]
torties = ["Tortie", "Calico"]
pelt_categories = [tabbies, spotted, plain, exotic, torties]

# SPRITE NAMES
pride_colours = ['AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']
single_colours = ['PALECREAM', 'CREAM', 'BEIGE', 'MEERKAT', 'KHAKI', 'SAND', 'WOOD', 'ROSE', 
    'GINGER', 'SUNSET', 'RUFOUS', 'FIRE', 'BRICK', 'RED', 'SCARLET', 'APRICOT', 'GARFIELD', 
    'APPLE', 'CRIMSON', 'BURNT', 'CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD', 'SOOT', 'DARKGREY', 
    'ANCHOR', 'CHARCOAL', 'COAL', 'BLACK', 'GREY', 'MARENGO', 'BATTLESHIP', 'CADET', 
    'BLUEGREY', 'STEEL', 'SLATE', 'CAPPUCCINO', 'ECRU', 'ASHBROWN', 'DUSTBROWN', 'SANDALWOOD', 
    'PINECONE', 'WRENGE', 'BROWN', 'MINK', 'CHESTNUT', 'TAN', 'DARKBROWN', 'BEAVER', 
    'CHOCOLATE', 'MOCHA', 'COFFEE', 'TAUPE', 'UMBER', 'WHITE', 'SILVER', 'BRONZE', 'PALEBOW', 
    'TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'OCEAN', 'DENIUM', 'SHINYMEW', 'SKY', 'TEAL', 'COBALT', 'SONIC',
    'POWDERBLUE', 'JEANS', 'NAVY', 'DUSKBOW', 'PANTONE', 'SALMON', 'THISTLE', 'AMYTHYST', 
    'DARKSALMON', 'MAGENTA', 'PETAL', 'MEW', 'HEATHER', 'ORCHID', 'STRAKIT', 'PURPLE', 'WINE', 'RASIN',
    'GENDER', 'REDNEG', 'IVORY', 'BANNANA', 'FARROW', 'HAY', 'FAWN', 'HAZELNUT', 'LEMON', 'LAGUNA', 
    'YELLOW', 'CORN', 'GOLD', 'HONEY', 'BEE', 'PINEAPPLE', 'TROMBONE', 'MEDALLION', 'GRANOLA', 
    'SADDLE', 'CEDAR', 'ONYX', 'LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD', 'OLIVE',
    'DARKOLIVE', 'GREEN', 'FOREST', 'JADE', 'SPINNACH', 'SEAWEED', 'SACRAMENTO', 'XANADU', 'DEEPFOREST',
    'AGENDER', 'ENBY', 'ASEXUAL', 'TRANS', 'GAYBOW']
cream_colours = ['PALECREAM', 'CREAM', 'BEIGE', 'MEERKAT', 'KHAKI', 'SAND', 'WOOD', 'PANTONE', 'SALMON',
    'THISTLE', 'BANNANA', 'FARROW', 'HAY']
ginger_colours = ['ROSE', 'GINGER', 'SUNSET', 'RUFOUS', 'FIRE', 'BRICK', 'RED', 
    'SCARLET', 'APRICOT', 'GARFIELD', 'APPLE', 'CRIMSON', 'BURNT', 'CARMINE', 'COSMOS', 
    'ROSEWOOD', 'BLOOD']
black_colours = ['SOOT', 'DARKGREY', 'ANCHOR', 'CHARCOAL', 'COAL', 'BLACK', 'ONYX', 'RASIN', 'DUSKBOW']
grey_colours = ['GREY', 'MARENGO', 'BATTLESHIP', 'CADET', 'BLUEGREY', 'STEEL', 'SLATE']
white_colours = ['WHITE', 'SILVER', 'BRONZE', 'PALEBOW', 'PETAL', 'IVORY']
brown_colours = ['CAPPUCCINO', 'ECRU', 'ASHBROWN', 'DUSTBROWN', 'SANDALWOOD', 
    'PINECONE', 'WRENGE', 'BROWN', 'MINK', 'CHESTNUT', 'TAN', 'TROMBONE', 'MEDALLION', 'GRANOLA', 
    'SADDLE', 'CEDAR', 'DARKBROWN', 'BEAVER', 'CHOCOLATE', 'MOCHA', 'COFFEE', 'TAUPE', 'UMBER']
blue_colours = ['TURQUOISE', 'TIFFANY', 'SAPPHIRE', 'SHINYMEW', 'SKY', 'OCEAN', 'DENIUM', 'COBALT', 'SONIC', 'POWDERBLUE', 'JEANS', 'NAVY']
yellow_colours = ['FAWN', 'HAZELNUT', 'LEMON', 'LAGUNA', 'YELLOW', 'CORN', 'GOLD', 'HONEY', 'BEE', 'PINEAPPLE']
purple_colours = ['AMYTHYST', 'DARKSALMON', 'MAGENTA', 'MEW', 'HEATHER', 
    'ORCHID', 'STRAKIT', 'PURPLE', 'WINE', 'GENDER', 'REDNEG']
green_colours = ['LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD', 'OLIVE', 'DARKOLIVE', 'GREEN', 
    'FOREST', 'JADE', 'SPINNACH', 'SEAWEED', 'SACRAMENTO', 'XANADU', 'DEEPFOREST']

colour_categories = [cream_colours, ginger_colours, black_colours, grey_colours, white_colours, brown_colours, blue_colours, 
    yellow_colours, purple_colours, green_colours, pride_colours]
    
eye_sprites = [
    'YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE', 'BLUEYELLOW', 'BLUEGREEN',
    'GREY', 'CYAN', 'EMERALD', 'PALEBLUE', 'PALEYELLOW', 'GOLD', 'HEATHERBLUE', 'COPPER', 'SAGE', 'BLUE2',
    'SUNLITICE', 'GREENYELLOW'
]
little_white = ['LITTLE', 'LIGHTTUXEDO', 'BUZZARDFANG', 'TIP', 'BLAZE', 'BIB', 'VEE', 'PAWS', 
    'BELLY', 'TAILTIP', 'TOES', 'BROKENBLAZE', 'LILTWO', 'SCOURGE', 'TOESTAIL', 'RAVENPAW', 'HONEY', 'VENUS', 
    'SHADOWSIGHT', 'TWIST', 'OKAPI', 'LUNA', 'EXTRA']
mid_white = ['TUXEDO', 'FANCY', 'UNDERS', 'DAMIEN', 'SKUNK', 'MITAINE', 'SQUEAKS', 'STAR', 'MOSSCLAW',
             'NIGHTMIST', 'SKELEWHITE', 'WINGS']           
high_white = ['ANY', 'ANY2', 'BROKEN', 'FRECKLES', 'RINGTAIL', 'HALFFACE', 'PANTS2', 
    'GOATEE', 'PRINCE', 'FAROFA', 'MISTER', 'PANTS', 'REVERSEPANTS', 'HALFWHITE', 'APPALOOSA', 'PIEBALD',
    'CURVED', 'GLASS', 'MASKMANTLE', 'CHANCE', 'RETSUKO', 'MAO', 'PAINTED'] 
mostly_white = ['VAN', 'ONEEAR', 'LIGHTSONG', 'TAIL', 'HEART', 'MOORISH', 'APRON', 'CAPSADDLE', 'DAPPLED', 
    'HAWK', 'FRECKLEMASK', 'MOTH', 'CHESTSPECK', 'HEART2', 'BLACKSTAR']
point_markings = ['COLOURPOINT', 'COLOURPOINTCREAMY', 'RAGDOLL', 'KARPATI', 'SNOWSHOE', 'SNOWBOOT',  
    'LIGHTPOINT', 'SEPIAPOINT', 'MINKPOINT', 'SEALPOINT']
vit = ['VITILIGO', 'VITILIGO2']
white_sprites = [
    little_white, mid_white, high_white, mostly_white, point_markings, vit, 'FULLWHITE']

skin_sprites = ['BLACK', 'RED', 'PINK', 'DARKBROWN', 'BROWN', 'LIGHTBROWN', 'DARK', 'DARKGREY', 'GREY', 'DARKSALMON',
                'SALMON', 'PEACH', 'DARKMARBLED', 'MARBLED', 'LIGHTMARBLED', 'DARKBLUE', 'BLUE', 'LIGHTBLUE']
skin_sphynx = ['S_BLACK', 'S_RED', 'S_PINK', 'S_DARKBROWN', 'S_BROWN', 'S_LIGHTBROWN', 'S_DARK', 'S_DARKGREY', 'S_GREY', 'S_DARKSALMON',
                'S_SALMON', 'S_PEACH', 'S_DARKMARBLED', 'S_MARBLED', 'S_LIGHTMARBLED', 'S_DARKBLUE', 'S_BLUE', 'S_LIGHTBLUE']
albino_sprites = ['ALBINOPINK', 'ALBINOBLUE', 'ALBINORED', 'ALBINOVIOLET', 'ALBINOYELLOW', 'ALBINOGREEN', 'S_ALBINOPINK',  
                'S_ALBINOBLUE', 'S_ALBINORED', 'S_ALBINOVIOLET', 'S_ALBINOYELLOW', 'S_ALBINOGREEN', 'ALBINOPINKWING', 'ALBINOBLUEWING', 
                'ALBINOREDWING', 'ALBINOVIOLETWING', 'ALBINOYELLOWWING', 'ALBINOGREENWING']
melanistic_sprites = ['MELANISTICLIGHT', 'MELANISTIC', 'MELANISTICDARK', 'S_MELANISTICLIGHT', 'S_MELANISTIC', 'S_MELANISTICDARK', 
                'MELANISTICLIGHTWING', 'MELANISTICWING', 'MELANISTICDARKWING', ] 
wing_sprites = ['WHITEWING', 'BLUEGREENWING', 'REDWING', 'PURPLEFADEWING', 'RAINBOWWING', 'SILVERWING',
                'STRAKITWING', 'SONICWING', 'MEWWING', 'OLIVEWING', 'GREENWING', 'GREYWING', 'GREYFADEWING',
                'BROWNFADEWING', 'PARROTWING', 'GOLDWING', 'LIGHTBROWNWING', 'BLACKWING']
magic_kitty = ['FIRE', 'WATER', 'EARTH', 'WIND', 'STAR', 'STEAM', 'MAGMA', 'SMOKE', 
                'HELL', 'MUD', 'STORM', 'BLOOD', 'SAND', 'BERRY', 'GHOST', 'S_FIRE', 'S_WATER', 'S_EARTH', 
                'S_WIND', 'S_STAR', 'S_STEAM', 'S_MAGMA', 'S_SMOKE', 'S_HELL', 'S_MUD', 'S_STORM', 'S_BLOOD', 
                'S_SAND', 'S_BERRY', 'S_GHOST']
skin_categories = [skin_sprites, skin_sphynx, albino_sprites, melanistic_sprites, wing_sprites, magic_kitty] 

sphynx = ['S_BLACK', 'S_RED', 'S_PINK', 'S_DARKBROWN', 'S_BROWN', 'S_LIGHTBROWN', 'S_DARK', 'S_DARKGREY', 'S_GREY', 'S_DARKSALMON',
            'S_SALMON', 'S_PEACH', 'S_DARKMARBLED', 'S_MARBLED', 'S_LIGHTMARBLED', 'S_DARKBLUE', 'S_BLUE', 'S_LIGHTBLUE',  
            'S_ALBINOPINK', 'S_ALBINOBLUE', 'S_ALBINORED', 'S_ALBINOVIOLET', 'S_ALBINOYELLOW', 'S_ALBINOGREEN' 'S_MELANISTICLIGHT', 
            'S_MELANISTIC', 'S_MELANISTICDARK', 'S_FIRE', 'S_WATER', 'S_EARTH', 'S_WIND', 'S_STAR', 'S_STEAM', 'S_MAGMA', 
            'S_SMOKE', 'S_HELL', 'S_MUD', 'S_STORM', 'S_BLOOD', 'S_SAND', 'S_BERRY', 'S_GHOST']
wings = ['WHITEWING', 'BLUEGREENWING', 'REDWING', 'PURPLEFADEWING', 'RAINBOWWING', 'SILVERWING',
            'STRAKITWING', 'SONICWING', 'MEWWING', 'OLIVEWING', 'GREENWING', 'GREYWING', 'GREYFADEWING',
            'BROWNFADEWING', 'PARROTWING', 'GOLDWING', 'LIGHTBROWNWING', 'BLACKWING'"ALBINOPINKWING", "ALBINOBLUEWING", 
            "ALBINOREDWING", "ALBINOVIOLETWING", "ALBINOYELLOWWING", "ALBINOGREENWING", "MELANISTICLIGHTWING", 
            "MELANISTICWING", "MELANISTICDARKWING"]

# CHOOSING PELT
def choose_pelt(colour=None, white=None, pelt=None, length=None, category=None, determined=False):
    colour = colour
    white = white
    pelt = pelt
    length = length
    category = category
    if pelt is None:
        if category != None:
            pelt = choice(category)
    else:
        pelt = pelt
    if length is None:
        length = choice(pelt_length)
    if pelt == 'SingleColour':
        if colour is None and not white:
            return SingleColour(choice(pelt_colours), length)
        elif colour is None:
            return SingleColour("WHITE", length)
        else:
            return SingleColour(colour, length)
    elif pelt == 'TwoColour':
        if colour is None:
            return TwoColour(choice(pelt_c_no_white), length)
        else:
            return TwoColour(colour, length)
    elif pelt == 'Tabby':
        if colour is None and white is None:
            return Tabby(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Tabby(choice(pelt_colours), white, length)
        else:
            return Tabby(colour, white, length)
    elif pelt == 'Marbled':
        if colour is None and white is None:
            return Marbled(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Marbled(choice(pelt_colours), white, length)
        else:
            return Marbled(colour, white, length)
    elif pelt == 'Rosette':
        if colour is None and white is None:
            return Rosette(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Rosette(choice(pelt_colours), white, length)
        else:
            return Rosette(colour, white, length)
    elif pelt == 'Smoke':
        if colour is None and white is None:
            return Smoke(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Smoke(choice(pelt_colours), white, length)
        else:
            return Smoke(colour, white, length)
    elif pelt == 'Ticked':
        if colour is None and white is None:
            return Ticked(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Ticked(choice(pelt_colours), white, length)
        else:
            return Ticked(colour, white, length)
    elif pelt == 'Speckled':
        if colour is None and white is None:
            return Speckled(choice(pelt_colours), choice([False, True]),
                            length)
        elif colour is None:
            return Speckled(choice(pelt_colours), white, length)
        else:
            return Speckled(colour, white, length)
    elif pelt == 'Bengal':
        if colour is None and white is None:
            return Bengal(choice(pelt_colours), choice([False, True]),
                          length)
        elif colour is None:
            return Bengal(choice(pelt_colours), white, length)
        else:
            return Bengal(colour, white, length)
    elif pelt == 'Mackerel':
        if colour is None and white is None:
            return Mackerel(choice(pelt_colours), choice([False, True]),
                            length)
        elif colour is None:
            return Mackerel(choice(pelt_colours), white, length)
        else:
            return Mackerel(colour, white, length)
    elif pelt == 'Classic':
        if colour is None and white is None:
            return Classic(choice(pelt_colours), choice([False, True]),
                           length)
        elif colour is None:
            return Classic(choice(pelt_colours), white, length)
        else:
            return Classic(colour, white, length)
    elif pelt == 'Sokoke':
        if colour is None and white is None:
            return Sokoke(choice(pelt_colours), choice([False, True]),
                          length)
        elif colour is None:
            return Sokoke(choice(pelt_colours), white, length)
        else:
            return Sokoke(colour, white, length)
    elif pelt == 'Agouti':
        if colour is None and white is None:
            return Agouti(choice(pelt_colours), choice([False, True]),
                          length)
        elif colour is None:
            return Agouti(choice(pelt_colours), white, length)
        else:
            return Agouti(colour, white, length)
    elif pelt == 'Backed':
        if colour is None and white is None:
            return Backed(choice(pelt_colours), choice([False, True]),
                             length)
        elif colour is None:
            return Backed(choice(pelt_colours), white, length)
        else:
            return Backed(colour, white, length)
    elif pelt == "Doberman":
        if colour is None and white is None:
            return Doberman(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Doberman(choice(pelt_colours), white, length)
        else:
            return Doberman(colour, white, length)   
    elif pelt == "Ghost":
        if colour is None and white is None:
            return Ghost(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Ghost(choice(pelt_colours), white, length)
        else:
            return Ghost(colour, white, length)            
    elif pelt == "Merle":
        if colour is None and white is None:
            return Merle(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Merle(choice(pelt_colours), white, length)
        else:
            return Merle(colour, white, length)     
    elif pelt == "Snowflake":
        if colour is None and white is None:
            return Snowflake(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Snowflake(choice(pelt_colours), white, length)
        else:
            return Snowflake(colour, white, length)            
    elif pelt == "Skele":
        if colour is None and white is None:
            return Skele(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Skele(choice(pelt_colours), white, length)
        else:
            return Skele(colour, white, length)      
    elif pelt == "Mottled":
        if colour is None and white is None:
            return Mottled(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Mottled(choice(pelt_colours), white, length)
        else:
            return Mottled(colour, white, length)  
    elif pelt == "Rat":
        if colour is None and white is None:
            return Rat(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Rat(choice(pelt_colours), white, length)
        else:
            return Rat(colour, white, length) 
    elif pelt == "Skitty":
        if colour is None and white is None:
            return Skitty(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Skitty(choice(pelt_colours), white, length)
        else:
            return Skitty(colour, white, length) 
    elif pelt == "Hooded":
        if colour is None and white is None:
            return Hooded(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Hooded(choice(pelt_colours), white, length)
        else:
            return Hooded(colour, white, length) 
    elif pelt == 'Tortie':
        if white is None:
            return Tortie(colour, choice([False, True]), length)
        else:
            return Tortie(colour, white, length)
    else:
        return Calico(colour, length)

def describe_color(pelt, tortiecolour, tortiepattern, white_patches, skin):
    color_name = ''
    color_name = str(pelt.colour).lower()
    if tortiecolour is not None:
        color_name = str(tortiecolour).lower()
    if color_name == 'ashbrown':
        color_name = 'ash brown'
    elif color_name == 'dustbrown':
        color_name = 'dust brown'
    elif color_name == 'darkbrown':
        color_name = 'dark brown'
    elif color_name == 'palecream':
        color_name = 'pale cream'
    elif color_name == 'darkgrey':
        color_name = 'dark grey'
    elif color_name == 'shinymew':
        color_name = 'shiny mew'
    elif color_name == 'sonic':
        color_name = 'sonic blue'
    elif color_name == 'darksalmon':
        color_name = 'dark salmon'            
    elif color_name == 'strakit':
        color_name = 'starkit purple'
    elif color_name == 'gender' or color_name == 'redneg':
        color_name = 'genderfluid blurple'   
    if skin in albino_sprites:
        color_name = "albino"      
    elif skin in melanistic_sprites:
        color_name = "melanistic"   
    if pelt.name == "Tabby":
        color_name = color_name + ' tabby'
    elif pelt.name == "Speckled":
        color_name = color_name + ' speckled'
    elif pelt.name == "Bengal":
        color_name = color_name + ' bengal'
    elif pelt.name == "Marbled":
        color_name = color_name + ' marbled tabby'
    elif pelt.name == "Rosette":
        color_name = color_name + ' rosetted'
    elif pelt.name == "Ticked":
        color_name = color_name + ' ticked tabby'
    elif pelt.name == "Smoke":
        color_name = color_name + ' smoke'
    elif pelt.name == "Mackerel":
        color_name = color_name + ' mackerel tabby'
    elif pelt.name == "Classic":
        color_name = color_name + ' classic tabby'
    elif pelt.name == "Sokoke":
        color_name = color_name + ' sokoke tabby'
    elif pelt.name == "Agouti":
        color_name = color_name + ' agouti'
    elif pelt.name == "Backed":
        color_name = color_name + ' stripe backed'
    elif pelt.name == "Charcoal":
        color_name = color_name + ' charcoal tabby'
    elif pelt.name == "Stain":
        color_name = color_name + ' stain'
    elif pelt.name == "Doberman":
        color_name = color_name + ' doberman point'            
    elif pelt.name == "Ghost":
        color_name = color_name + ' ghost tabby'
    elif pelt.name == "Merle":
        color_name = color_name + ' merle'            
    elif pelt.name == "Snowflake":
        color_name = color_name + ' snowflake'
    elif pelt.name == "Skele":
        color_name = color_name + ' skeleton'     
    elif pelt.name == "Rat":
        color_name = color_name + ' solid rat'  
    elif pelt.name == "Skitty":
        color_name = color_name + ' skitty'  
    elif pelt.name == "Hooded":
        color_name = color_name + ' charcoal hooded tabby'  
    if skin in sphynx:
        color_name = color_name + ' sphynx'
    elif skin in wings:
        color_name = 'winged ' + color_name 

    elif pelt.name == "Tortie":
        if tortiepattern not in ["tortiesolid", "tortiesmoke"]:
            color_name = color_name + ' torbie'
        else:
            color_name = color_name + ' tortie'
    elif pelt.name == "Calico":
        if tortiepattern not in ["tortiesolid", "tortiesmoke"]:
            color_name = color_name + ' tabico'
        else:
            color_name = color_name + ' calico'
    # enough to comment but not make calico
    if white_patches is not None:
        if white_patches in little_white + mid_white:
            color_name = color_name + ' and stain'
        # and white
        elif white_patches in high_white:
            if pelt.name != "Calico":
                color_name = color_name + ' and stain'   

        # white and
        elif white_patches in mostly_white:
            color_name = 'stained and ' + color_name 
        # colorpoint
        elif white_patches in point_markings:
            color_name = color_name + ' point'
            if color_name == 'dark ginger point' or color_name == 'ginger point':
                color_name = 'flame point'
        # vitiligo
        elif white_patches in vit:
            color_name = color_name + ' with vitiligo'
    else:
        color_name = color_name

    if color_name == 'tortie':
        color_name = 'tortoiseshell'

    if white_patches == 'FULLWHITE':
        color_name = 'stained'

    return color_name
