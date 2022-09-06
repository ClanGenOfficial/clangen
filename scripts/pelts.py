from random import choice, randint


class SingleColour(object):
    name = "SingleColour"
    sprites = {1: 'single'}
    white_patches = None

    def __init__(self, colour, length):
        self.colour = colour
        self.length = length
        self.white = self.colour == "white"

    def __repr__(self):
        return self.colour + self.length


class TwoColour(object):
    name = "TwoColour"
    sprites = {1: 'single', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN',
        'ANY2', 'ANY2', 'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY',
        'VANCREAMY', 'ANY2CREAMY', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO',
        'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO', 'TIP', 'FANCY',
        'FRECKLES', 'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'TAIL',
        'BLAZE', 'PRINCE', 'BIB', 'VEE', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN',
        'MISTER', 'BELLY', 'TAILTIP', 'TOES', 'BROKENBLAZE'
    ]

    def __init__(self, colour, length):
        self.colour = colour
        self.length = length
        self.white = True

    def __repr__(self):
        return f"white and {self.colour}{self.length}"


class Tabby(object):
    name = "Tabby"
    sprites = {1: 'tabby', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN',
        'ANY2', 'ANY2', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG',
        'RAGDOLL', 'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY',
        'LITTLECREAMY', 'VANCREAMY', 'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES',
        'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE',
        'BIB', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES',
        'BROKENBLAZE'
    ]

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} tabby"
        else:
            return self.colour + self.length + " tabby"


class Tabby2(object):
    name = "Tabby2"
    sprites = {1: 'tabby2', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN',
        'ANY2', 'ANY2', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG',
        'RAGDOLL', 'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY',
        'LITTLECREAMY', 'VANCREAMY', 'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES',
        'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE',
        'BIB', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES',
        'BROKENBLAZE'
    ]

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} bengal"
        else:
            return self.colour + self.length + " bengal"


class Rosette(object):
    name = "Rosette"
    sprites = {1: 'rosette', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN',
        'ANY2', 'ANY2', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG',
        'RAGDOLL', 'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY',
        'LITTLECREAMY', 'VANCREAMY', 'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES',
        'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE',
        'BIB', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES',
        'BROKENBLAZE'
    ]

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} rosette"
        else:
            return self.colour + self.length + " rosette"


class Smoke(object):
    name = "Smoke"
    sprites = {1: 'smoke', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN',
        'ANY2', 'ANY2', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG',
        'RAGDOLL', 'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY',
        'LITTLECREAMY', 'VANCREAMY', 'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES',
        'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE',
        'BIB', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES',
        'BROKENBLAZE'
    ]

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} smoke"
        else:
            return self.colour + self.length + " smoke"


class Ticked(object):
    name = "Ticked"
    sprites = {1: 'ticked', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN',
        'ANY2', 'ANY2', 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG',
        'RAGDOLL', 'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY',
        'LITTLECREAMY', 'VANCREAMY', 'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES',
        'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE',
        'BIB', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES',
        'BROKENBLAZE'
    ]

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour}{self.length} ticked"
        else:
            return self.colour + self.length + " ticked"


class Speckled(object):
    name = "Speckled"
    sprites = {1: 'speckled', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'LITTLE', 'ANY', 'TUXEDO', 'LITTLE', 'ANY2', 'ANY2',
        'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL',
        'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY',
        'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE',
        'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE', 'BIB', 'UNDERS', 'PAWS',
        'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES', 'BROKENBLAZE'
    ]

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour} speckled{self.length}"
        else:
            return f"{self.colour} speckled{self.length}"


class Speckled2(object):
    name = "Speckled2"
    sprites = {1: 'speckled2', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'LITTLE', 'ANY', 'TUXEDO', 'LITTLE', 'ANY2', 'ANY2',
        'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL',
        'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY',
        'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE',
        'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE', 'BIB', 'UNDERS', 'PAWS',
        'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES', 'BROKENBLAZE'
    ]

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and {self.colour} bengal{self.length}"
        else:
            return f"{self.colour} bengal{self.length}"


class Tortie(object):
    name = "Tortie"
    sprites = {1: 'tortie', 2: 'white'}
    white_patches = [
        'TUXEDO', 'LITTLE', 'TUXEDO', 'LITTLE', None, None, None, None, 'EXTRA', 'ONEEAR',
        'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG',
        'VITILIGO', 'TUXEDOCREAMY', 'LITTLECREAMY', 'TIP', 'FANCY', 'FRECKLES',
        'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE',
        'BIB', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES',
        'BROKENBLAZE'
    ]

    def __init__(self, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = choice(["BLACK", "GINGER"])
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and tortoiseshell{self.length}"
        else:
            return f"tortoiseshell{self.length}"


class Tortie2(object):
    name = "Tortie2"
    sprites = {1: 'tortie2', 2: 'white'}
    white_patches = [
        'TUXEDO', 'LITTLE', 'TUXEDO', 'LITTLE', None, None, None, 'EXTRA', 'ONEEAR',
        'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG',
        'VITILIGO', 'TUXEDOCREAMY', 'LITTLECREAMY', 'TIP', 'FANCY', 'FRECKLES',
        'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE',
        'BIB', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES',
        'BROKENBLAZE'
    ]

    def __init__(self, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = choice(["BLACK", "GINGER"])
        self.length = length

    def __repr__(self):
        if self.white:
            return f"white and bengal{self.length}"
        else:
            return f"bengal{self.length}"


class Calico(object):
    name = "Calico"
    sprites = {1: 'calico', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'VAN', 'ANY', 'TUXEDO', 'VAN', 'ANY2', 'ANY2',
        'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL',
        'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY', 'VANCREAMY',
        'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE',
        'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE', 'BIB', 'UNDERS', 'PAWS',
        'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES', 'BROKENBLAZE'
    ]

    def __init__(self, length):
        self.colour = choice(["BLACK", "GINGER", "WHITE"])
        self.length = length
        self.white = True

    def __repr__(self):
        return f"calico{self.length}"
    
class Calico2(object):
    name = "Calico2"
    sprites = {1: 'calico2', 2: 'white'}
    white_patches = [
        'ANY', 'TUXEDO', 'VAN', 'ANY', 'TUXEDO', 'VAN', 'ANY2', 'ANY2',
        'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL',
        'LIGHTSONG', 'VITILIGO', 'ANYCREAMY', 'TUXEDOCREAMY', 'VANCREAMY',
        'ANY2CREAMY', 'TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE',
        'PANTS2', 'GOATEE', 'TAIL', 'BLAZE', 'PRINCE', 'BIB', 'UNDERS', 'PAWS',
        'FAROFA', 'DAMIEN', 'MISTER', 'BELLY', 'TOES', 'BROKENBLAZE'
    ]

    def __init__(self, length):
        self.colour = choice(["BLACK", "GINGER", "WHITE"])
        self.length = length
        self.white = True

    def __repr__(self):
        return f"calico{self.length}"


# ATTRIBUTES, including non-pelt related
pelt_colours = [
    'WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER',
    'GOLDEN', 'GINGER', 'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN'
]
pelt_c_no_white = [
    'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER', 'GOLDEN',
    'GINGER', 'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN'
]
pelt_c_no_bw = [
    'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'PALEGINGER', 'GOLDEN', 'GINGER',
    'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN'
]
tortie_pattern = ['ONE', 'TWO', 'FADEDONE', 'FADEDTWO', 'BLUEONE', 'BLUETWO']
calico_pattern = [
    'ONE', 'TWO', 'THREE', 'FOUR', 'FADEDONE', 'FADEDTWO', 'FADEDTHREE',
    'FADEDFOUR', 'BLUEONE', 'BLUETWO', 'BLUETHREE', 'BLUEFOUR'
]

pelt_length = ["short", "medium", "medium", "long"]
eye_colours = [
    'YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE'
]
scars1 = ["ONE", "TWO", "THREE"]
scars2 = ["LEFTEAR", "RIGHTEAR", "LEFTEAR", "RIGHTEAR", "NOTAIL"]
scars3 = [
    "CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME", "GREEN", "RAINBOW",
    "BLACK", "SPIKES", "PINK", "PURPLE", "MULTI", "CRIMSONBELL", "BLUEBELL",
    "YELLOWBELL", "CYANBELL", "REDBELL", "LIMEBELL", "GREENBELL",
    "RAINBOWBELL", "BLACKBELL", "SPIKESBELL", "PINKBELL", "PURPLEBELL",
    "MULTIBELL", "CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW",
    "LIMEBOW", "GREENBOW", "RAINBOWBOW", "BLACKBOW", "SPIKESBOW", "PINKBOW",
    "PURPLEBOW", "MULTIBOW"]
scars4 = ["TAILSCAR", "SNOUT", "CHEEK", "SIDE", "THROAT", "TAILBASE", "BELLY", "TOETRAP"]
scars5 = ["SNAKE"

]

pelt_names_F = [
    "SingleColour", "SingleColour", "TwoColour", "Tabby", "Tortie", "Calico",
    "Tabby", "TwoColour", "Speckled", "Tabby2", "Speckled2", 'Tortie2',
    "Rosette", "Smoke", "Ticked", "Calico2"
]
pelt_names_M = [
    "SingleColour", "SingleColour", "TwoColour", "Tabby", "Tabby", "Speckled",
    "TwoColour", "Tabby2", "Speckled2", "Rosette", "Smoke", "Ticked"
]

# SPRITE NAMES
single_colours = [
    'WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER',
    'GOLDEN', 'GINGER', 'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN'
]
eye_sprites = [
    'YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE',
    'BLUEYELLOW', 'BLUEGREEN'
]
white_sprites = [
    'ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN', 'ANYCREAMY',
    'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY', 'VANCREAMY', 'ONEEAR',
    'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
    'TIP', 'FANCY', 'FRECKLES', 'RINGTAIL', 'HALFFACE', 'PANTS2', 'GOATEE',
    'TAIL', 'BLAZE', 'PRINCE', 'BIB', 'VEE', 'UNDERS', 'PAWS', 'FAROFA', 'DAMIEN',
    'MISTER', 'BELLY', 'TAILTIP', 'TOES', 'BROKENBLAZE',
    'PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'PIEBALD',
    'CURVED', 'HEART', 'LILTWO', 'GLASS', 'MOORISH', 'POINTMARK'
]
skin_sprites = ['BLACK', 'RED', 'PINK']


# CHOOSING PELT
def choose_pelt(gender,
                colour=None,
                white=None,
                pelt=None,
                length=None,
                determined=False):
    if pelt is None:
        a = randint(0, 100)
        if a != 1:
            pelt = choice(pelt_names_F) if gender == "female" else choice(
                pelt_names_M)
        else:
            pelt = choice(pelt_names_F)
            if gender == 'male' and pelt in ['Tortie', 'Calico', 'Tortie2', 'Calico2']:
                print("Male tortie/calico!")
    elif pelt in ['Tortie', 'Calico', 'Tortie2', 'Calico2'] and gender == 'male' and not determined:
        a = randint(0, 200)
        if a != 1:
            pelt = choice(pelt_names_M)
    if length is None:
        length = choice(pelt_length)
    if pelt == "SingleColour":
        if colour is None and not white:
            return SingleColour(choice(pelt_colours), length)
        elif colour is None:
            return SingleColour("WHITE", length)
        else:
            return SingleColour(colour, length)
    elif pelt == "TwoColour":
        if colour is None:
            return TwoColour(choice(pelt_c_no_white), length)
        else:
            return TwoColour(colour, length)
    elif pelt == "Tabby":
        if colour is None and white is None:
            return Tabby(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Tabby(choice(pelt_colours), white, length)
        else:
            return Tabby(colour, white, length)
    elif pelt == "Tabby2":
        if colour is None and white is None:
            return Tabby2(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Tabby2(choice(pelt_colours), white, length)
        else:
            return Tabby2(colour, white, length)
    elif pelt == "Rosette":
        if colour is None and white is None:
            return Rosette(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Rosette(choice(pelt_colours), white, length)
        else:
            return Rosette(colour, white, length)
    elif pelt == "Smoke":
        if colour is None and white is None:
            return Smoke(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Smoke(choice(pelt_colours), white, length)
        else:
            return Smoke(colour, white, length)
    elif pelt == "Ticked":
        if colour is None and white is None:
            return Ticked(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Ticked(choice(pelt_colours), white, length)
        else:
            return Ticked(colour, white, length)
    elif pelt == "Tortie":
        if white is None:
            return Tortie(choice([False, True]), length)
        else:
            return Tortie(white, length)
    elif pelt == "Tortie2":
        if white is None:
            return Tortie2(choice([False, True]), length)
        else:
            return Tortie2(white, length)
    elif pelt == "Speckled":
        if colour is None and white is None:
            return Speckled(choice(pelt_colours), choice([False, True]),
                            length)
        elif colour is None:
            return Speckled(choice(pelt_colours), white, length)
        else:
            return Speckled(colour, white, length)
    elif pelt == "Speckled2":
        if colour is None and white is None:
            return Speckled2(choice(pelt_colours), choice([False, True]),
                             length)
        elif colour is None:
            return Speckled2(choice(pelt_colours), white, length)
        else:
            return Speckled2(colour, white, length)
    elif pelt == "Calico":
        return Calico(length)
    elif pelt == "Calico2":
        return Calico2(length)
