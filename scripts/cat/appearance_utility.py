import random
from .pelts import *
from scripts.cat.sprites import Sprites

# ---------------------------------------------------------------------------- #
#                               utility functions                              #
# ---------------------------------------------------------------------------- #

def plural_acc_names(accessory, plural, singular):
    acc_display = accessory.lower()
    if acc_display == 'maple leaf':
        if plural:
            acc_display = 'maple leaves'
        if singular:
            acc_display = 'maple leaf'
    elif acc_display == 'holly':
        if plural:
            acc_display = 'holly berries'
        if singular:
            acc_display = 'holly berry'
    elif acc_display == 'blue berries':
        if plural:
            acc_display = 'blueberries'
        if singular:
            acc_display = 'blueberry'
    elif acc_display == 'forget me nots':
        if plural:
            acc_display = 'forget me nots'
        if singular:
            acc_display = 'forget me not flower'
    elif acc_display == 'rye stalk':
        if plural:
            acc_display = 'rye stalks'
        if singular:
            acc_display = 'rye stalk'
    elif acc_display == 'laurel':
        if plural:
            acc_display = 'laurel'
        if singular:
            acc_display = 'laurel plant'
    elif acc_display == 'bluebells':
        if plural:
            acc_display = 'bluebells'
        if singular:
            acc_display = 'bluebell flower'
    elif acc_display == 'nettle':
        if plural:
            acc_display = 'nettles'
        if singular:
            acc_display = 'nettle'
    elif acc_display == 'poppy':
        if plural:
            acc_display = 'poppies'
        if singular:
            acc_display = 'poppy flower'
    elif acc_display == 'lavender':
        if plural:
            acc_display = 'lavender'
        if singular:
            acc_display = 'lavender flower'
    elif acc_display == 'herbs':
        if plural:
            acc_display = 'herbs'
        if singular:
            acc_display = 'herb'
    elif acc_display == 'petals':
        if plural:
            acc_display = 'petals'
        if singular:
            acc_display = 'petal'
    elif acc_display == 'dry herbs':
        if plural:
            acc_display = 'dry herbs'
        if singular:
            acc_display = 'dry herb'
    elif acc_display == 'oak leaves':
        if plural:
            acc_display = 'oak leaves'
        if singular:
            acc_display = 'oak leaf'
    elif acc_display == 'catmint':
        if plural:
            acc_display = 'catnip'
        if singular:
            acc_display = 'catnip sprig'
    elif acc_display == 'maple seed':
        if plural:
            acc_display = 'maple seeds'
        if singular:
            acc_display = 'maple seed'
    elif acc_display == 'juniper':
        if plural:
            acc_display = 'juniper berries'
        if singular:
            acc_display = 'juniper berry'
    elif acc_display == 'red feathers':
        if plural:
            acc_display = 'cardinal feathers'
        if singular:
            acc_display = 'cardinal feather'
    elif acc_display == 'blue feathers':
        if plural:
            acc_display = 'crow feathers'
        if singular:
            acc_display = 'crow feather'
    elif acc_display == 'jay feathers':
        if plural:
            acc_display = 'jay feathers'
        if singular:
            acc_display = 'jay feather'
    elif acc_display == 'moth wings':
        if plural:
            acc_display = 'moth wings'
        if singular:
            acc_display = 'moth wing'
    elif acc_display == 'cicada wings':
        if plural:
            acc_display = 'cicada wings'
        if singular:
            acc_display = 'cicada wing'

    if plural is True and singular is False:
        return acc_display
    elif singular is True and plural is False:
        return acc_display

# ---------------------------------------------------------------------------- #
#                                init functions                                #
# ---------------------------------------------------------------------------- #


def init_eyes(cat):
    if cat.eye_colour is not None:
        return   
    else:
        par1 = None
        par2 = None
        if cat.parent1 is None:
            cat.eye_colour = choice(eye_colours)
        elif cat.parent2 is None:
            par1 = cat.all_cats[cat.parent1]
            cat.eye_colour = choice(
                [par1.eye_colour, choice(eye_colours)])
        else:
            par1 = cat.all_cats[cat.parent1]
            par2 = cat.all_cats[cat.parent2]
            cat.eye_colour = choice([
                par1.eye_colour, par2.eye_colour,
                choice(eye_colours)
            ])
        num = 120
        if cat.white_patches in [high_white, mostly_white, 'FULLWHITE'] or cat.pelt.colour == 'WHITE':
            num = num - 90
        if cat.white_patches == 'FULLWHITE' or cat.pelt.colour == 'WHITE':
            num -= 10
        if par1:
            if par1.eye_colour2:
                num -= 10
        if par2:
            if par2.eye_colour2:
                num -= 10
        if num < 0:
            num = 1
        hit = randint(0, num)
        if hit == 0:
            if cat.eye_colour in yellow_eyes:
                eye_choice = choice([blue_eyes, green_eyes])
                cat.eye_colour2 = choice(eye_choice)
            elif cat.eye_colour in blue_eyes:
                eye_choice = choice([yellow_eyes, green_eyes])
                cat.eye_colour2 = choice(eye_choice)
            elif cat.eye_colour in green_eyes:
                eye_choice = choice([yellow_eyes, blue_eyes])
                cat.eye_colour2 = choice(eye_choice)

def pelt_inheritance(cat, parents: tuple):
    # setting parent pelt categories
    #We are using a set, since we don't need this to be ordered, and sets deal with removing duplicates.
    par_peltlength = set()
    par_peltcolours = set()
    par_peltnames = set()
    par_pelts = []
    par_white = []
    for p in parents:
        if p:
            #Gather pelt color.
            par_peltcolours.add(p.pelt.colour)

            #Gather pelt length
            par_peltlength.add(p.pelt.length)

            # Gather pelt name
            if p.pelt.name in torties:
                par_peltnames.add(p.tortiebase.capitalize())
                print(p.tortiebase.capitalize())
            else:
                par_peltnames.add(p.pelt.name)

            #Gather exact pelts, for direct inheritance.
            par_pelts.append(p.pelt)

            #Gather if they have white in their pelt.
            par_white.append(bool(p.white_patches))

        #If this list is empty, something went wrong.
        if not par_peltcolours:
            print("Error - no parents: pelt randomized")
            randomize_pelt(cat)
            return

        # There is a 1/15 chance for kits to have the exact same pelt as one of their parents
        if not randint(0, 15):  # 1/15 chance
            selected = choice(par_pelts)
            cat.pelt = choose_pelt(selected.colour, selected.white, selected.name,
                                   selected.length)
            return

        # ------------------------------------------------------------------------------------------------------------#
        #   PELT
        # ------------------------------------------------------------------------------------------------------------#

        # Determine pelt.
        weights = [0, 0, 0, 0]  #Weights for each pelt group. It goes: (tabbies, spotted, plain, exotic)
        for p_ in par_peltnames:
            if p_ in tabbies:
                add_weight = (35, 20, 20, 5)
            elif p_ in spotted:
                add_weight = (30, 45, 20, 5)
            elif p_ in plain:
                add_weight = (25, 25, 45, 5)
            elif p_ in exotic:
                add_weight = (20, 20, 20, 40)
            else:
                add_weight = (0, 0, 0, 0)

            for x in range(0, len(weights)):
                weights[x] += add_weight[x]

        #A quick check to make sure all the weights aren't 0
        if all([x == 0 for x in weights]):
            weights = [1, 1, 1, 1]

        # Now, choose the pelt category and pelt. The extra 0 is for the tortie pelts,
        chosen_pelt = choice(
            random.choices(pelt_categories, weights = weights + [0], k = 1)[0]
        )

        # Tortie chance
        tortie_chance_f = 3  # There is a default chance for female tortie
        tortie_chance_m = 9
        for p_ in par_pelts:
            if p_.colour in ginger_colours + black_colours:
                tortie_chance_f = 2
                tortie_chance_m -= 1

        # Determine tortie:
        if cat.gender == "female":
            torbie = random.getrandbits(tortie_chance_f) == 1
        else:
            torbie = random.getrandbits(tortie_chance_m) == 1

        chosen_tortie_base = None
        if torbie:
            # If it is tortie, the chosen pelt above becomes the base pelt.
            chosen_tortie_base = chosen_pelt.lower()
            if chosen_tortie_base == ["TwoColour", "SingleColour"]:
                chosen_tortie_base = "Single"
            chosen_pelt = random.choice(torties)


        # ------------------------------------------------------------------------------------------------------------#
        #   PELT COLOUR
        # ------------------------------------------------------------------------------------------------------------#
        weights = [0, 0, 0]  # Weights for each pelt group. It goes: (ginger_colours, black_colours, brown_colours)
        for p_ in par_peltcolours:
            if p_ in ginger_colours:
                add_weight = (35, 0, 15)
            elif p_ in black_colours:
                add_weight = (0, 35, 15)
            elif p_ in brown_colours:
                add_weight = (15, 15, 35)
            else:
                add_weight = (0, 0, 0)

            for x in range(0, len(weights)):
                weights[x] += add_weight[x]

            # A quick check to make sure all the weights aren't 0
            if all([x == 0 for x in weights]):
                weights = [1, 1, 1]

        chosen_pelt_color = choice(
            random.choices(colour_categories, weights=weights, k = 1)[0]
        )

        # ------------------------------------------------------------------------------------------------------------#
        #   PELT LENGTH
        # ------------------------------------------------------------------------------------------------------------#

        weights = [0, 0, 0]  # Weights for each length. It goes (short, medium, long)
        for p_ in par_peltlength:
            if p_ == "short":
                add_weight = (45, 35, 20)
            elif p_ == "medium":
                add_weight = (25, 50, 25)
            elif p_ == "long":
                add_weight = (20, 35, 45)
            else:
                add_weight = (0, 0, 0)

            for x in range(0, len(weights)):
                weights[x] += add_weight[x]

        # A quick check to make sure all the weights aren't 0
        if all([x == 0 for x in weights]):
            weights = [1, 1, 1]

        chosen_pelt_length = random.choices(pelt_length, weights = weights, k = 1)[0]

        # ------------------------------------------------------------------------------------------------------------#
        #   PELT WHITE
        # ------------------------------------------------------------------------------------------------------------#

        chance = 5
        for p_ in par_white:
            if p:
                chance += 45

        chosen_white = random.randint(1, 100) <= chance

        if chosen_white and chosen_pelt == "Torbie":
            chosen_pelt = "Calico"

        # SET THE PELT
        cat.pelt = choose_pelt(chosen_pelt_color, chosen_white, chosen_pelt, chosen_pelt_length)
        cat.tortie_base = chosen_tortie_base # This will be none if the cat isn't a tortie.

def randomize_pelt(cat):
    # ------------------------------------------------------------------------------------------------------------#
    #   PELT
    # ------------------------------------------------------------------------------------------------------------#

    # Determine pelt.
    chosen_pelt = choice(
        random.choices(pelt_categories, weights=(35, 20, 30, 15, 0), k=1)[0]
    )

    # Tortie chance
    tortie_chance_f = 2  # There is a default chance for female tortie
    tortie_chance_m = 9
    if cat.gender == "female":
        torbie = random.getrandbits(tortie_chance_f) == 1
    else:
        torbie = random.getrandbits(tortie_chance_m) == 1

    chosen_tortie_base = None
    if torbie:
        # If it is tortie, the chosen pelt above becomes the base pelt.
        chosen_tortie_base = chosen_pelt.lower()
        if chosen_tortie_base == ["TwoColour", "SingleColour"]:
            chosen_tortie_base = "Single"
        chosen_pelt = random.choice(torties)

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT COLOUR
    # ------------------------------------------------------------------------------------------------------------#

    chosen_pelt_color = choice(
        random.choices(colour_categories, k=1)[0]
    )

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT LENGTH
    # ------------------------------------------------------------------------------------------------------------#


    chosen_pelt_length = random.choice(pelt_length)

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT WHITE
    # ------------------------------------------------------------------------------------------------------------#


    chosen_white = random.randint(1, 100) <= 35
    

    cat.pelt = choose_pelt(chosen_pelt_color, chosen_white, chosen_pelt, chosen_pelt_length)
    cat.tortie_base = chosen_tortie_base  # This will be none if the cat isn't a tortie.

def init_pelt(cat):
    if cat.pelt is not None:
        return cat.pelt
    else:
        # Grab Parents
        par1 = None
        par2 = None
        if cat.parent1 in cat.all_cats:
            par1 = cat.all_cats[cat.parent1]
        if cat.parent2 in cat.all_cats:
            par2 = cat.all_cats[cat.parent2]

        if par1 or par2:
            #If the cat has parents, use inheritance to decide pelt.
            pelt_inheritance(cat, (par1, par2))
        else:
            randomize_pelt(cat)

def init_sprite(cat):
    if cat.pelt is None:
        init_pelt(cat)
    cat.age_sprites = {
        'kitten': randint(0, 2),
        'adolescent': randint(3, 5),
        'elder': randint(3, 5)
    }
    cat.reverse = choice([True, False])
    # skin chances
    cat.skin = choice(skin_sprites)
            
    if cat.pelt is not None:
        if cat.pelt.length != 'long':
            cat.age_sprites['adult'] = randint(6, 8)
        else:
            cat.age_sprites['adult'] = randint(0, 2)
        cat.age_sprites['young adult'] = cat.age_sprites['adult']
        cat.age_sprites['senior adult'] = cat.age_sprites['adult']
        cat.age_sprites['dead'] = None


def init_scars(cat):
    if not cat.scars:
        scar_choice = randint(0, 15)
        if cat.age in ['kitten', 'adolescent']:
            scar_choice = randint(0, 50)
        elif cat.age in ['young adult', 'adult']:
            scar_choice = randint(0, 20)
        if scar_choice == 1:
            cat.scars.append(choice([
                choice(scars1),
                choice(scars3)
            ]))

    if 'NOTAIL' in cat.scars and 'HALFTAIL' in cat.scars:
        cat.scars.remove('HALFTAIL')


def init_accessories(cat):
    acc_display_choice = randint(0, 35)
    if cat.age in ['kitten', 'adolescent']:
        acc_display_choice = randint(0, 15)
    elif cat.age in ['young adult', 'adult']:    
        acc_display_choice = randint(0, 50)
    if acc_display_choice == 1:
        cat.acc_display = choice([
            choice(plant_accessories),
            choice(wild_accessories)
        ])
    else:
        cat.acc_display = None


def init_pattern(cat):
    if cat.pelt is None:
        init_pelt(cat)
    if cat.pelt.name in torties:
        cat.tortiecolour = cat.pelt.colour
        if cat.tortiebase is None:
            cat.tortiebase = choice(['single', 'tabby', 'bengal', 'marbled', 'ticked', 'smoke', 'rosette', 'speckled'])
        if cat.tortiebase == 'tabby':
            cat.tortiepattern = 'tortietabby'
        elif cat.tortiebase == 'bengal':
            cat.tortiepattern = 'tortiebengal'
        elif cat.tortiebase == 'marbled':
            cat.tortiepattern = 'tortiemarbled'
        elif cat.tortiebase == 'ticked':
            cat.tortiepattern = 'tortieticked'
        elif cat.tortiebase == 'rosette':
            cat.tortiepattern = 'tortierosette'
        elif cat.tortiebase == 'smoke':
            cat.tortiepattern = 'tortiesmoke'
        elif cat.tortiebase == 'speckled':
            cat.tortiepattern = 'tortiespeckled'
        elif cat.tortiebase == 'mackerel':
            cat.tortiepattern = 'tortiemackerel'
        elif cat.tortiebase == 'classic':
            cat.tortiepattern = 'tortieclassic'
        elif cat.tortiebase == 'sokoke':
            cat.tortiepattern = 'tortiesokoke'
        elif cat.tortiebase == 'agouti':
            cat.tortiepattern = 'tortieagouti'
        else:
            cat.tortiepattern = 'tortietabby'
    else:
        cat.tortiebase = None
        cat.tortiepattern = None
        cat.tortiecolour = None
    if cat.pelt.name in torties and cat.pelt.colour is not None:
        if cat.pelt.colour in ["BLACK", "DARKBROWN", "GHOST"]:
            cat.pattern = choice(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR', 'GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR',
                                    'DARKONE', 'DARKTWO', 'DARKTHREE', 'DARKFOUR'])
        elif cat.pelt.colour in ["DARKGREY", "BROWN"]:
            cat.pattern = choice(['GOLDONE', 'GOLDTWO', 'GOLDTHREE', 'GOLDFOUR', 'GINGERONE', 'GINGERTWO', 'GINGERTHREE', 'GINGERFOUR'])
        elif cat.pelt.colour in ["SILVER", "GREY", "LIGHTBROWN"]:
            cat.pattern = choice(['PALEONE', 'PALETWO', 'PALETHREE', 'PALEFOUR', 'CREAMONE', 'CREAMTWO', 'CREAMTHREE', 'CREAMFOUR'])
    else:
        cat.pattern = None


def init_white_patches(cat):
    if cat.pelt is None:
        init_pelt(cat)
    non_white_pelt = False
    if cat.pelt.colour != 'WHITE' and cat.pelt.name in\
        ['Tortie', 'TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette', 'Mackerel', 
        'Classic', 'Sokoke', 'Agouti']:
        non_white_pelt = True
    if cat.pelt.white is True:
        pelt_choice = randint(0, 10)
        vit_chance = randint(0, 40)
        direct_inherit = randint(0, 10)
        white_patches_choice = None
        white_list = [None, little_white, mid_white, high_white, mostly_white, 'FULLWHITE']
        # inheritance
        # one parent
        if cat.parent1 is not None and cat.parent2 is None and cat.parent1 in cat.all_cats:
            par1 = cat.all_cats[cat.parent1]
            if direct_inherit == 1:
                if par1.pelt.white is False:
                    cat.pelt.white = False
                    cat.white_patches = None
                else:
                    cat.white_patches = par1.white_patches
            elif vit_chance == 1:
                cat.white_patches = choice(vit)
            else:
                if par1.white_patches in point_markings and non_white_pelt:
                    if pelt_choice < 5:
                        cat.white_patches = choice(point_markings)
                    else:
                        cat.white_patches = choice(mid_white)
                elif par1.white_patches in vit:
                    cat.white_patches = choice(vit)
                elif par1.white_patches in [None, little_white, mid_white, high_white]:
                    white_patches_choice = random.choices(white_list, weights=(20, 20, 20, 20, 19, 1))
                elif par1.white_patches in mostly_white:
                    white_patches_choice = random.choices(white_list, weights=(0, 0, 30, 30, 30, 10))
            # two parents
        elif cat.parent1 and cat.parent2 and\
            cat.parent1 in cat.all_cats and cat.parent2 in cat.all_cats:
            # if 1, cat directly inherits parent 1's white patches. if 2, it directly inherits parent 2's
            par1 = cat.all_cats[cat.parent1]
            par2 = cat.all_cats[cat.parent2]
            if direct_inherit == 1:
                if par1.pelt.white is False:
                    cat.pelt.white = False
                    cat.white_patches = None
                else:
                    cat.white_patches = par1.white_patches
            elif direct_inherit == 2:
                if par2.pelt.white is False:
                    cat.pelt.white = False
                    cat.white_patches = None
                else:
                    cat.white_patches = par2.white_patches
            elif vit_chance == 1:
                cat.white_patches = choice(vit)
            else:
                if par1.white_patches in point_markings and non_white_pelt\
                    or par2.white_patches in point_markings and non_white_pelt:
                    if pelt_choice < 5:
                        cat.white_patches = choice(point_markings)
                    else:
                        cat.white_patches = choice(mid_white)
                elif par1.white_patches in vit and non_white_pelt\
                    or par2.white_patches in vit and non_white_pelt:
                    cat.white_patches = choice(vit)
                elif par1.white_patches is None:
                    if par2.white_patches is None:
                        cat.pelt.white = False
                        cat.white_patches = None
                    elif par2.white_patches in little_white:
                        white_patches_choice = random.choices(white_list, weights=(10, 70, 20, 0, 0, 0))
                    elif par2.white_patches in mid_white or par2.white_patches in point_markings:
                        white_patches_choice = random.choices(white_list, weights=(0, 60, 40, 0, 0, 0))
                    elif par2.white_patches in high_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 20, 60, 20, 0, 0))
                    elif par2.white_patches in mostly_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 5, 45, 30, 20, 0))
                    elif par2.white_patches == 'FULLWHITE':
                        white_patches_choice = random.choices(white_list, weights=(0, 20, 20, 20, 20, 20))
                    else:
                        cat.white_patches = choice(little_white)
                elif par1.white_patches in little_white:
                    if par2.white_patches is None:
                        white_patches_choice = random.choices(white_list, weights=(20, 50, 30, 0, 0, 0))
                    elif par2.white_patches in little_white:
                        white_patches_choice = random.choices(white_list, weights=(5, 55, 40, 0, 0, 0))
                    elif par2.white_patches in mid_white or par2.white_patches in point_markings:
                        white_patches_choice = random.choices(white_list, weights=(0, 40, 30, 30, 0, 0))
                    elif par2.white_patches in high_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 10, 50, 30, 10, 0))
                    elif par2.white_patches in mostly_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 25, 40, 25, 10))
                    elif par2.white_patches == 'FULLWHITE':
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 45, 35, 20))
                    else:
                        cat.white_patches = choice(little_white)
                elif par1.white_patches in mid_white or par1.white_patches in point_markings:
                    if par2.white_patches is None:
                        white_patches_choice = random.choices(white_list, weights=(0, 60, 40, 0, 0, 0))
                    elif par2.white_patches in little_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 40, 30, 30, 0, 0))
                    elif par2.white_patches in mid_white or par2.white_patches in point_markings:
                        white_patches_choice = random.choices(white_list, weights=(0, 20, 60, 20, 0, 0))
                    elif par2.white_patches in high_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 30, 50, 20, 0))
                    elif par2.white_patches in mostly_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 20, 50, 20, 10))
                    elif par2.white_patches == 'FULLWHITE':
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 30, 40, 30))
                    else:
                        cat.white_patches = choice(mid_white)
                elif par1.white_patches in high_white:
                    if par2.white_patches is None:
                        white_patches_choice = random.choices(white_list, weights=(0, 20, 60, 20, 0, 0))
                    elif par2.white_patches in little_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 10, 50, 30, 10, 0))
                    elif par2.white_patches in mid_white or par2.white_patches in point_markings:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 30, 50, 20, 0))
                    elif par2.white_patches in high_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 30, 50, 20, 0))
                    elif par2.white_patches in mostly_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 20, 30, 30, 20))
                    elif par2.white_patches == 'FULLWHITE':
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 25, 50, 25))
                    else:
                        cat.white_patches = choice(high_white)
                elif par1.white_patches in mostly_white:
                    if par2.white_patches is None:
                        white_patches_choice = random.choices(white_list, weights=(0, 5, 45, 30, 20, 0))
                    elif par2.white_patches in little_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 25, 40, 25, 10))
                    elif par2.white_patches in mid_white or par2.white_patches in point_markings:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 20, 50, 20, 10))
                    elif par2.white_patches in high_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 20, 30, 30, 20))
                    elif par2.white_patches in mostly_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 20, 60, 20))
                    elif par2.white_patches == 'FULLWHITE':
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 0, 60, 40))
                    else:
                        cat.white_patches = choice(mostly_white)
                elif par1.white_patches == 'FULLWHITE':
                    if par2.white_patches is None:
                        white_patches_choice = random.choices(white_list, weights=(0, 20, 20, 20, 20, 20))
                    elif par2.white_patches in little_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 45, 35, 20))
                    elif par2.white_patches in mid_white or par2.white_patches in point_markings:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 30, 40, 30))
                    elif par2.white_patches in high_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 25, 50, 25))
                    elif par2.white_patches in mostly_white:
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 0, 60, 40))
                    elif par2.white_patches == 'FULLWHITE':
                        white_patches_choice = random.choices(white_list, weights=(0, 0, 0, 0, 40, 60))
                    else:
                        cat.white_patches = choice(mostly_white)
                
        # regular non-inheritance white patches generation
        else:
            if pelt_choice == 1 and non_white_pelt:
                cat.white_patches = choice(point_markings)
            elif pelt_choice == 2 and cat.pelt.name in ['Calico', 'TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette',
            'Mackerel', 'Classic', 'Sokoke', 'Agouti']:
                cat.white_patches = choice(mostly_white)
            elif pelt_choice == 3 and cat.pelt.name in ['TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette',
            'Mackerel', 'Classic', 'Sokoke', 'Agouti'] and cat.pelt.colour != 'WHITE':
                cat.white_patches = choice(['EXTRA', 'FULLWHITE'])
                if cat.white_patches == None:
                    cat.pelt.white = False
            else:
                if cat.pelt.name in ['TwoColour', 'Tabby', 'Speckled', 'Marbled', 'Bengal', 'Ticked', 'Smoke', 'Rosette', 
                                    'Mackerel', 'Classic', 'Sokoke', 'Agouti']:
                    white_patches_choice = random.choices(white_list, weights=(0, 30, 30, 30, 10, 0))
                elif cat.pelt.name == 'Tortie':
                    white_patches_choice = random.choices(white_list, weights=(0, 60, 40, 0, 0, 0))
                elif cat.pelt.name == 'Calico':
                    cat.white_patches = choice(high_white)
                elif pelt_choice == 1 and vit_chance == 1 and non_white_pelt:
                    cat.white_patches = choice(vit)
                else:
                    cat.pelt.white = False
        # just making sure no cats end up with no white patches and true white 
        if cat.white_patches == None:
            if cat.pelt.white is False:
                cat.white_patches = None
            elif white_patches_choice == None:
                cat.white_patches = None
                cat.pelt.white = False
            elif white_patches_choice == 'EXTRA' or white_patches_choice == 'FULLWHITE':
                cat.white_patches = white_patches_choice
            else:
                whitechoice = choice(list(white_patches_choice))
                if whitechoice == None:
                    cat.pelt.white = False
                    cat.white_patches = None
                elif type(whitechoice) == list:
                    cat.white_patches = choice(whitechoice)
                else:
                    cat.white_patches = whitechoice
        if cat.pelt.name == 'Calico' and not cat.white_patches in [high_white, mostly_white]:
            cat.pelt.name = 'Tortie'
        elif cat.pelt.name == 'Tortie' and cat.white_patches in [high_white, mostly_white]:
                cat.pelt.name = 'Calico'
        if cat.pelt.name == 'TwoColour' and cat.white_patches is None:
            cat.pelt.name = 'SingleColour'
    else:
        cat.white_patches = None
        cat.pelt.white = False
        if cat.pelt.name == 'Calico' and not cat.white_patches in [high_white, mostly_white]:
            cat.pelt.name = 'Tortie'
        elif cat.pelt.name == 'Tortie' and cat.white_patches in [high_white, mostly_white]:
                cat.pelt.name = 'Calico'
        if cat.pelt.name == 'TwoColour':
            cat.pelt.name = 'SingleColour'


def init_tint(cat):
    # Basic tints as possible for all colors.
    possible_tints = Sprites.cat_tints["possible_tints"]["basic"].copy()
    if cat.pelt.colour in Sprites.cat_tints["colour_groups"]:
        color_group = Sprites.cat_tints["colour_groups"][cat.pelt.colour]
        possible_tints += Sprites.cat_tints["possible_tints"][color_group]
        cat.tint = choice(possible_tints)

