from random import choice, randint


class SingleColour(object):
    name = "SingleColour"
    sprites = {1: 'single'}
    white_patches = None

    def __init__(self, colour, length, markings):
        self.markings = markings
        self.colour = colour
        self.length = length
        self.white = self.colour == "white"

    def __repr__(self):
        return self.colour + self.length + self.markings


class TwoColour(object):
    name = "TwoColour"
    sprites = {1: 'single', 2: 'white'}
    white_patches = ['ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN',
                    'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY', 'VANCREAMY',
                    'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
                    'PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'PIEBALD',
                    'CURVED', 'HEART', 'LILTWO', 'GLASS', 'MOORISH', 'POINTMARK']

    def __init__(self, colour, length, markings):
        self.markings = markings
        self.colour = colour
        self.length = length
        self.white = True

    def __repr__(self):
        return f"white and {self.colour}{self.length}{self.markings}"


#class Tabby(object):
 #   name = "Tabby"
 #   sprites = {1: 'tabby', 2: 'white'}
 #   white_patches = ['ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY', 'TUXEDO', 'LITTLE', 'VAN', 'ANY2', 'ANY2',
 #                    'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
 #                    'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'VANCREAMY', 'ANY2CREAMY']

 #   def __init__(self, colour, white, length, markings):
 #       self.white = white  # boolean; does cat have white on it or no
 #       self.colour = colour
 #       self.length = length
 #       self.markings = markings

 #   def __repr__(self):
 #       if self.white:
 #           return "white and " + self.colour + self.length + " tabby"
 #      else:
 #          return self.colour + self.length + " tabby"


#class Speckled(object):
#    name = "Speckled"
#    sprites = {1: 'speckled', 2: 'white'}
#    white_patches = ['ANY', 'TUXEDO', 'LITTLE', 'ANY', 'TUXEDO', 'LITTLE', 'ANY2', 'ANY2',
#                     'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
#                     'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'ANY2CREAMY']

#    def __init__(self, colour, white, length, markings):
#        self.white = white  # boolean; does cat have white on it or no
#        self.colour = colour
#        self.length = length
#        self.markings = markings

#    def __repr__(self):
#        if self.white:
#            return "white and " + self.colour + " speckled" + self.length
#        else:
#            return self.colour + " speckled" + self.length


class Tortie(object):
    name = "Tortie"
    sprites = {1: 'tortie', 2: 'white'}
    white_patches = ['ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN',
                    'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY', 'VANCREAMY',
                    'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
                    'PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'PIEBALD',
                    'CURVED', 'HEART', 'LILTWO', 'GLASS', 'MOORISH', 'POINTMARK']

    def __init__(self, white, length, markings):
        self.white = white  # boolean; does cat have white on it or no
        self.colour = choice(["BLACK", "GINGER"])
        self.length = length
        self.markings = markings

    def __repr__(self):
        if self.white:
            return f"white and tortoiseshell{self.length}{self.markings}"
        else:
            return f"tortoiseshell{self.length}{self.markings}"


class Calico(object):
    name = "Calico"
    sprites = {1: 'calico', 2: 'white'}
    white_patches = ['ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN',
                    'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY', 'VANCREAMY',
                    'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
                    'PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'PIEBALD',
                    'CURVED', 'HEART', 'LILTWO', 'GLASS', 'MOORISH', 'POINTMARK']

    def __init__(self, length, markings):
        self.colour = choice(["BLACK", "GINGER", "WHITE"])
        self.length = length
        self.markings = markings
        self.white = True

    def __repr__(self):
        return f"calico{self.length}{self.markings}"


# ATTRIBUTES, including non-pelt related
pelt_colours = ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER', 'GOLDEN', 'GINGER',
                'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN']
pelt_c_no_white = ['PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER', 'GOLDEN', 'GINGER',
                   'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN']
pelt_c_no_bw = ['PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'PALEGINGER', 'GOLDEN', 'GINGER',
                'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN']
tortie_pattern = ['ONE', 'TWO', 'FADEDONE', 'FADEDTWO', 'BLUEONE', 'BLUETWO']
calico_pattern = ['ONE', 'TWO', 'THREE', 'FOUR', 'FADEDONE', 'FADEDTWO', 'FADEDTHREE', 'FADEDFOUR', 'BLUEONE',
                  'BLUETWO', 'BLUETHREE', 'BLUEFOUR']

pelt_length = ["short", "medium", "medium", "long"]
eye_colours = ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE']
scars1 = ["ONE", "TWO", "THREE"]
scars2 = ["LEFTEAR", "RIGHTEAR", "LEFTEAR", "RIGHTEAR", "NOTAIL"]
scars3 = ["CRIMSON", "BLUE", "YELLOW", "CYAN", "RED", "LIME", "GREEN", "RAINBOW", "BLACK", "SPIKES", "PINK", "PURPLE", "MULTI",
            "CRIMSONBELL", "BLUEBELL", "YELLOWBELL", "CYANBELL", "REDBELL", "LIMEBELL", "GREENBELL", "RAINBOWBELL", 
            "BLACKBELL", "SPIKESBELL", "PINKBELL", "PURPLEBELL", "MULTIBELL",
            "CRIMSONBOW", "BLUEBOW", "YELLOWBOW", "CYANBOW", "REDBOW", "LIMEBOW", "GREENBOW", "RAINBOWBOW", "BLACKBOW", 
            "SPIKESBOW", "PINKBOW", "PURPLEBOW", "MULTIBOW", "CRIMSONBAND", "BLUEBAND", "YELLOWBAND", "CYANBAND", "REDBAND", "LIMEBAND",
            "GREENBAND", "RAINBOWBAND", "SKULLBAND", "POLKABAND", "PINKBAND", "PURPLEBAND", "HEARTBAND"]

pelt_names_F = ["SingleColour", "SingleColour", "TwoColour", "Tortie", "Calico", "TwoColour"]
pelt_names_M = ["SingleColour", "SingleColour", "TwoColour", "TwoColour"]

pelt_markings = ["Solid", "Solid", "Ticked", "Ticked", "Ticked", "Tabby", "Tabby", "Tabby", "Speckled", "Speckled", "Marbled", "Rosette", "TickedAbyss"]

# SPRITE NAMES
single_colours = ['WHITE', 'PALEGREY', 'SILVER', 'GREY', 'DARKGREY', 'BLACK', 'PALEGINGER', 'GOLDEN', 'GINGER',
                  'DARKGINGER', 'LIGHTBROWN', 'BROWN', 'DARKBROWN']
eye_sprites = ['YELLOW', 'AMBER', 'HAZEL', 'PALEGREEN', 'GREEN', 'BLUE', 'DARKBLUE', 'BLUEYELLOW', 'BLUEGREEN']
white_sprites = ['ANY', 'TUXEDO', 'LITTLE', 'COLOURPOINT', 'VAN',
                 'ANYCREAMY', 'TUXEDOCREAMY', 'LITTLECREAMY', 'COLOURPOINTCREAMY', 'VANCREAMY',
                 'ONEEAR', 'BROKEN', 'LIGHTTUXEDO', 'BUZZARDFANG', 'RAGDOLL', 'LIGHTSONG', 'VITILIGO',
                 'PANTS', 'REVERSEPANTS', 'SKUNK', 'KARPATI', 'HALFWHITE', 'APPALOOSA', 'PIEBALD',
                 'CURVED', 'HEART', 'LILTWO', 'GLASS', 'MOORISH', 'POINTMARK']
skin_sprites = ['BLACK', 'RED', 'PINK']


# CHOOSING PELT
def choose_pelt(gender, colour=None, white=None, pelt=None, length=None, markings=None, determined=False):

    if pelt is None:
        a = randint(0, 100)
        if a != 1:
            markings = choice(pelt_markings)
            pelt = choice(pelt_names_F) if gender == "female" else choice(pelt_names_M)
        else:
            markings = choice(pelt_markings)
            pelt = choice(pelt_names_F)
            if gender == 'male' and pelt in ['Tortie', 'Calico']:
                print("Male tortie/calico!")
    elif pelt in ['Tortie', 'Calico'] and gender == 'male' and not determined:
        a = randint(0, 200)
        if a != 1:
            markings = choice(pelt_markings)
            pelt = choice(pelt_names_M)

    if length is None:
        length = choice(pelt_length)
        
    if markings is None:
        markings = choice(pelt_markings)

    if pelt == "SingleColour":
        if colour is None and not white:
            return SingleColour(choice(pelt_colours), length, markings)
        elif colour is None:
            return SingleColour("WHITE", length, markings)
        else:
            return SingleColour(colour, length, markings)

    elif pelt == "TwoColour":
        if colour is None:
            return TwoColour(choice(pelt_c_no_white), length, markings)
        else:
            return TwoColour(colour, length, markings)

     # elif pelt == "Tabby":
   #     if colour is None and white is None:
   #         return Tabby(choice(pelt_colours), choice([False, True]), length, markings)
   #     elif colour is None:
   #         return Tabby(choice(pelt_colours), white, length, markings)
   #     else:
   #         return Tabby(colour, white, length, markings)

    elif pelt == "Tortie":
        if white is None:
            return Tortie(choice([False, True]), length, markings)
        else:
            return Tortie(white, length, markings)
   # elif pelt == "Speckled":
   #     if colour is None and white is None:
   #         return Speckled(choice(pelt_colours), choice([False, True]), length, markings)
   #     elif colour is None:
   #         return Speckled(choice(pelt_colours), white, length, markings)
   #     else:
   #         return Speckled(colour, white, length, markings)

    elif pelt == "Calico":
        return Calico(length, markings)

