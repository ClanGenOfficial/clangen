from random import choice, randint


class SingleColour(object):
    name = "SingleColour"
    sprites = {1: 'single'}
    white_patches = None

    def __init__(self, colour, length):
        self.colour = colour
        self.length = length
        if self.colour == "white":
            self.white = True
        else:
            self.white = False

    def __repr__(self):
        return self.colour + self.length


class TwoColour(object):
    name = "TwoColour"
    sprites = {1: 'single', 2: 'white'}
    white_patches = ['ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY2', 'ANY2',
                     'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'VANCREAMY', 'ANY2CREAMY',
                     'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO']

    def __init__(self, colour, length):
        self.colour = colour
        self.length = length
        self.white = True

    def __repr__(self):
        return "white and " + self.colour + self.length


class Tabby(object):
    name = "Tabby"
    sprites = {1: 'tabby', 2: 'white'}
    white_patches = ['ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY2', 'ANY2',
                     'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
                     'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'VANCREAMY', 'ANY2CREAMY']

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return "white and " + self.colour + self.length + " tabby"
        else:
            return self.colour + self.length + " tabby"


class Speckled(object):
    name = "Speckled"
    sprites = {1: 'speckled', 2: 'white'}
    white_patches = ['ANY', 'TUXEDO', 'LITTLE', 'ANY', 'TUXEDO', 'LITTLE', 'ANY2', 'ANY2',
                     'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
                     'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'ANY2CREAMY']

    def __init__(self, colour, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = colour
        self.length = length

    def __repr__(self):
        if self.white:
            return "white and " + self.colour + " speckled" + self.length
        else:
            return self.colour + " speckled" + self.length


class Tortie(object):
    name = "Tortie"
    sprites = {1: 'tortie', 2: 'white'}
    white_patches = ['TUXEDO', 'LITTLE', 'TUXEDO', 'LITTLE', None, 'EXTRA',
                     'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
                     'TUXEDOCREAMY', 'LITTLECREAMY']

    def __init__(self, white, length):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = choice(["BLACK", "GINGER"])
        self.length = length

    def __repr__(self):
        if self.white:
            return "white and tortoiseshell" + self.length
        else:
            return "tortoiseshell" + self.length


class Calico(object):
    name = "Calico"
    sprites = {1: 'calico', 2: 'white'}
    white_patches = ['ANY', 'TUXEDO', 'VAN', 'ANY', 'TUXEDO', 'VAN', 'ANY2', 'ANY2',
                     'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
                     'ANYCREAMY', 'TUXEDOCREAMY', 'VANCREAMY', 'ANY2CREAMY']

    def __init__(self, length):
        self.colour = choice(["BLACK", "GINGER", "WHITE"])
        self.length = length
        self.white = True

    def __repr__(self):
        return "calico" + self.length


# ATTRIBUTES, including non-pelt related
pelt_colours = ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER', 'GOLDEN', 'GINGER',
                'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN']
pelt_c_no_white = ['PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER', 'GOLDEN', 'GINGER',
                   'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN']
pelt_c_no_bw = ['PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'PALEGINGER', 'GOLDEN', 'GINGER',
                'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN']
tortie_pattern = ['ONE', 'TWO', 'FADEDONE', 'FADEDTWO','BLUEONE','BLUETWO']
calico_pattern = ['ONE', 'TWO', 'THREE', 'FOUR', 'FADEDONE', 'FADEDTWO', 'FADEDTHREE', 'FADEDFOUR','BLUEONE','BLUETWO','BLUETHREE','BLUEFOUR']

pelt_length = ["short", "medium", "medium", "long"]
eye_colours = ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE']
scars1 = ["ONE", "TWO", "THREE"]
scars2 = ["LEFTEAR", "RIGHTEAR", "LEFTEAR", "RIGHTEAR", "NOTAIL"]

pelt_names_F = ["SingleColour", "SingleColour", "TwoColour", "Tabby", "Tortie", "Calico", "Tabby", "TwoColour",
                "Speckled"]
pelt_names_M = ["SingleColour", "SingleColour", "TwoColour", "Tabby", "Tabby", "Speckled", "TwoColour"]

# SPRITE NAMES
single_colours = ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER', 'GOLDEN', 'GINGER',
                  'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN']
eye_sprites = ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE', 'BLUEYELLOW', 'BLUEGREEN']
white_sprites = ['ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN',
                 'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY', 'VANCREAMY',
                 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO']
skin_sprites = ['BLACK', 'RED', 'PINK']


# CHOOSING PELT
def choose_pelt(gender, colour=None, white=None, pelt=None, length=None, determined=False):
    if pelt is None:
        a = randint(0, 100)
        if a != 1:
            if gender == "female":
                pelt = choice(pelt_names_F)
            else:
                pelt = choice(pelt_names_M)
        else:
            pelt = choice(pelt_names_F)
            if gender == 'male' and pelt in ['Tortie', 'Calico']:
                print ("Male tortie/calico!")

    elif pelt in ['Tortie', 'Calico'] and gender == 'male' and not determined:
        a = randint(0, 200)
        if a != 1:
            pelt = choice(pelt_names_M)

    if length is None:
        length = choice(pelt_length)

    if pelt == "SingleColour":
        if colour is None and not white:
            return SingleColour(choice(pelt_colours), length)
        elif colour is None and white:
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

    elif pelt == "Tortie":
        if white is None:
            return Tortie(choice([False, True]), length)
        else:
            return Tortie(white, length)

    elif pelt == "Speckled":
        if colour is None and white is None:
            return Speckled(choice(pelt_colours), choice([False, True]), length)
        elif colour is None:
            return Speckled(choice(pelt_colours), white, length)
        else:
            return Speckled(colour, white, length)

    elif pelt == "Calico":
        return Calico(length)
