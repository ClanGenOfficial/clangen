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
        num = 200
        if cat.white_patches in [high_white, mostly_white, 'FULLWHITE'] or cat.pelt.colour == 'WHITE':
            num -= 100
        if par1:
            if par1.eye_colour2:
                num = num - 20
        if par2:
            if par2.eye_colour2:
                num = num - 20

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

def init_pelt(cat):
    '''if cat.parent2 is None and cat.parent1 in cat.all_cats.keys():
        # 1 in 3 chance to inherit a single parent's pelt
        par1 = cat.all_cats[cat.parent1]
        cat.pelt = choose_pelt(cat.gender, choice([par1.pelt.colour, None]), choice([par1.pelt.white, None]), choice([par1.pelt.name, None]),
                                choice([par1.pelt.length, None]))
    if cat.parent1 in cat.all_cats.keys() and cat.parent2 in cat.all_cats.keys():
        # 2 in 3 chance to inherit either parent's pelt
        par1 = cat.all_cats[cat.parent1]
        par2 = cat.all_cats[cat.parent2]
        cat.pelt = choose_pelt(cat.gender, choice([par1.pelt.colour, par2.pelt.colour, None]), choice([par1.pelt.white, par2.pelt.white, None]),
                                choice([par1.pelt.name, par2.pelt.name, None]), choice([par1.pelt.length, par2.pelt.length, None]))                  
    else:
        cat.pelt = choose_pelt(cat.gender)'''
    if cat.pelt is not None:
        return cat.pelt
    else:
        # new pelt inheritance
        par1 = None
        par2 = None
        if cat.parent1 in cat.all_cats.keys():
            par1 = cat.all_cats[cat.parent1]
        if cat.parent2 in cat.all_cats.keys():
            par2 = cat.all_cats[cat.parent2]
        # setting parent pelt categories
        if par1 != None:
            if par1.pelt in tabbies:
                par1_peltcategory = tabbies
            elif par1.pelt in spotted:
                par1_peltcategory = spotted
            elif par1.pelt in plain:
                par1_peltcategory = plain
            elif par1.pelt in exotic:
                par1_peltcategory = exotic
            elif par1.pelt in torties:
                par1_peltcategory = torties
        if par2 != None:
            if par2.pelt in tabbies:
                par2_peltcategory = tabbies
            elif par2.pelt in spotted:
                par2_peltcategory = spotted
            elif par2.pelt in plain:
                par2_peltcategory = plain
            elif par2.pelt in exotic:
                par2_peltcategory = exotic
            elif par2.pelt in torties:
                par2_peltcategory = torties
        if par1 != None:
            par1_colour = par1.pelt.colour
        if par1 != None:
            par2_colour = par2.pelt.colour
        white = False
        pelt_choice = None
        colour_choice = None
        tortie_chanceM = 0
        tortie_chanceF = False
        tortie = False
        length_choice = None
        direct_inherit = randint(0, 10)
        if par1 != None:
            if par1_colour in [ginger_colours, black_colours] and not par2:
                tortie_chanceF = choice(True, False)
                tortie_chanceM = random.getrandbits(8)
            elif par1 != None and par2 != None and par1_colour in ginger_colours and par2_colour in black_colours\
                or par1_colour in black_colours and par2_colour in ginger_colours:
                tortie_chanceF = choice(True, False)
                tortie_chanceM = random.getrandbits(7)
        else:
            tortie_chanceF = choice([True, False, False])
            tortie_chanceM = random.getrandbits(8)

        # just gonna go ahead and decide if the cat is a tortie here
        if cat.gender == 'female' and tortie_chanceF:
            pelt_choice = torties
        elif cat.gender == 'male' and tortie_chanceM == 1:
            pelt_choice = torties

        if pelt_choice == torties:
            tortie = True

        # no parents, pretty random
        if not par1 and not par2:
            pelt_choice = random.choices(pelt_categories, weights=(35, 20, 30, 15, 0))
            if tortie:
                choice_ = choice(pelt_choice)
                cat.tortiebase = choice(choice_)
                colour_choice = tortiecolours
                length_choice = pelt_length
            else:
                colour_choice = pelt_colours
                length_choice = pelt_length
            print("First Check: " + str(pelt_choice))

        # pelt name inheritance or tortiebase for torties
        elif par1 and not par2: # for only one parent
            if direct_inherit == 1: # inherit directly from parent 1
                if par1.pelt not in torties:
                    cat.pelt = choose_pelt(par1_colour, par1.pelt.white, par1.pelt.name, par1.pelt.length, par1_peltcategory)
                elif par1.pelt in torties and pelt_choice == torties:
                    cat.pelt = choose_pelt(par1_colour, par1.pelt.white, par1.pelt.name, par1.pelt.length, par1_peltcategory)
            if par1.pelt.white:
                white = True
            if par1.pelt in tabbies:
                pelt_choice = random.choices(pelt_categories, weights=(35, 20, 20, 5, 0))
            elif par1.pelt in spotted:
                pelt_choice = random.choices(pelt_categories, weights=(30, 45, 20, 5, 0))
            elif par1.pelt in plain:
                pelt_choice = random.choices(pelt_categories, weights=(25, 25, 45, 5, 0))
            elif par1.pelt in exotic:
                pelt_choice = random.choices(pelt_categories, weights=(20, 20, 20, 40, 0))
            elif par1.pelt in torties:
                if par1.tortiebase.capitalize() in tabbies:
                    pelt_choice = random.choices(pelt_categories, weights=(35, 20, 20, 5, 0))
                elif par1.tortiebase.capitalize() in spotted:
                    pelt_choice = random.choices(pelt_categories, weights=(30, 45, 20, 5, 0))
                elif par1.tortiebase.capitalize() in plain:
                    pelt_choice = random.choices(pelt_categories, weights=(25, 25, 45, 5, 0))
                elif par1.tortiebase.capitalize() in exotic:
                    pelt_choice = random.choices(pelt_categories, weights=(20, 20, 20, 40, 0))

            # just doing one parent colour here too
            if tortie:
                colour_choice = tortiecolours
            else:
                colour_choice = random.choices(colour_categories, weights=(33, 33, 33))

            # one parent fur length
            if par1.pelt.length == 'short':
                length_choice = random.choices(pelt_length, weights=(45, 35, 20))
            elif par1.pelt.length == 'medium':
                length_choice = random.choices(pelt_length, weights=(25, 50, 25))
            elif par1.pelt.length == 'long':
                length_choice = random.choices(pelt_length, weights=(20, 35, 45))

        # choosing pelt again
        elif par1 and par2: # for both parents
            if direct_inherit == 1: # inherit directly from parent 1
                if par1.pelt not in torties:
                    cat.pelt = choose_pelt(par1_colour, par1.pelt.white, par1.pelt.name, par1.pelt.length, par1_peltcategory)
                elif par1.pelt in torties and pelt_choice == torties:
                    cat.pelt = choose_pelt(par1_colour, par1.pelt.white, par1.pelt.name, par1.pelt.length, par1_peltcategory)
            elif direct_inherit == 2: # inherit directly from parent 2
                if par2.pelt not in torties:
                    cat.pelt = choose_pelt(par2_colour, par2.pelt.white, par2.pelt.name, par2.pelt.length, par2_peltcategory)
                elif par2.pelt in torties and pelt_choice == torties:
                    cat.pelt = choose_pelt(par2_colour, par2.pelt.white, par2.pelt.name, par2.pelt.length, par2_peltcategory)
            if par1.pelt.white or par2.pelt.white:
                white = True
            if par1.pelt in tabbies:
                if par2.pelt in tabbies:
                    pelt_choice = random.choices(pelt_categories, weights=(50, 28, 28, 4, 0))
                elif par2.pelt in spotted:
                    pelt_choice = random.choices(pelt_categories, weights=(40, 40, 16, 4, 0))
                elif par2.pelt in plain:
                    pelt_choice = random.choices(pelt_categories, weights=(40, 16, 40, 4, 0))
                elif par2.pelt in exotic:
                    pelt_choice = random.choices(pelt_categories, weights=(40, 15, 15, 30, 0))
                elif par2.pelt in torties:
                    if par2.tortiebase.capitalize() in tabbies:
                        pelt_choice = random.choices(pelt_categories, weights=(50, 28, 28, 4, 0))
                    elif par2.tortiebase.capitalize() in spotted:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 40, 16, 4, 0))
                    elif par2.tortiebase.capitalize() in plain:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 16, 40, 4, 0))
                    elif par2.tortiebase.capitalize() in exotic:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 15, 15, 30, 0))
            elif par1.pelt in spotted:
                if par2.pelt in tabbies:
                    pelt_choice = random.choices(pelt_categories, weights=(40, 40, 16, 4, 0))
                elif par2.pelt in spotted:
                    pelt_choice = random.choices(pelt_categories, weights=(28, 50, 28, 4, 0))
                elif par2.pelt in plain:
                    pelt_choice = random.choices(pelt_categories, weights=(16, 40, 40, 4, 0))
                elif par2.pelt in exotic:
                    pelt_choice = random.choices(pelt_categories, weights=(15, 40, 15, 30, 0))
                elif par2.pelt in torties:
                    if par2.tortiebase.capitalize() in tabbies:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 40, 16, 4, 0))
                    elif par2.tortiebase.capitalize() in spotted:
                        pelt_choice = random.choices(pelt_categories, weights=(28, 50, 28, 4, 0))
                    elif par2.tortiebase.capitalize() in plain:
                        pelt_choice = random.choices(pelt_categories, weights=(16, 40, 40, 4, 0))
                    elif par2.tortiebase.capitalize() in exotic:
                        pelt_choice = random.choices(pelt_categories, weights=(15, 40, 15, 30, 0))
            elif par1.pelt in plain:
                if par2.pelt in tabbies:
                    pelt_choice = random.choices(pelt_categories, weights=(40, 16, 40, 4, 0))
                elif par2.pelt in spotted:
                    pelt_choice = random.choices(pelt_categories, weights=(16, 40, 40, 4, 0))
                elif par2.pelt in plain:
                    pelt_choice = random.choices(pelt_categories, weights=(28, 28, 50, 4, 0))
                elif par2.pelt in exotic:
                    pelt_choice = random.choices(pelt_categories, weights=(15, 15, 40, 30, 0))
                elif par2.pelt in torties:
                    if par2.tortiebase.capitalize() in tabbies:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 16, 40, 4, 0))
                    elif par2.tortiebase.capitalize() in spotted:
                        pelt_choice = random.choices(pelt_categories, weights=(16, 40, 40, 4, 0))
                    elif par2.tortiebase.capitalize() in plain:
                        pelt_choice = random.choices(pelt_categories, weights=(28, 28, 50, 4, 0))
                    elif par2.tortiebase.capitalize() in exotic:
                        pelt_choice = random.choices(pelt_categories, weights=(15, 15, 40, 30, 0))
            elif par1.pelt in exotic:
                if par2.pelt in tabbies:
                    pelt_choice = random.choices(pelt_categories, weights=(40, 15, 15, 30, 0))
                elif par2.pelt in spotted:
                    pelt_choice = random.choices(pelt_categories, weights=(15, 40, 15, 30, 0))
                elif par2.pelt in plain:
                    pelt_choice = random.choices(pelt_categories, weights=(28, 28, 50, 4, 0))
                elif par2.pelt in exotic:
                    pelt_choice = random.choices(pelt_categories, weights=(20, 20, 20, 40, 0))
                elif par2.pelt in torties:
                    if par2.tortiebase.capitalize() in tabbies:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 15, 15, 30, 0))
                    elif par2.tortiebase.capitalize() in spotted:
                        pelt_choice = random.choices(pelt_categories, weights=(15, 40, 15, 30, 0))
                    elif par2.tortiebase.capitalize() in plain:
                        pelt_choice = random.choices(pelt_categories, weights=(28, 28, 50, 4, 0))
                    elif par2.tortiebase.capitalize() in exotic:
                        pelt_choice = random.choices(pelt_categories, weights=(20, 20, 20, 40, 0))
            elif par1.pelt in torties:
                if par1.tortiebase.capitalize() in tabbies:
                    if par2.pelt in tabbies:
                        pelt_choice = random.choices(pelt_categories, weights=(50, 28, 28, 4, 0))
                    elif par2.pelt in spotted:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 40, 16, 4, 0))
                    elif par2.pelt in plain:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 16, 40, 4, 0))
                    elif par2.pelt in exotic:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 15, 15, 30, 0))
                    elif par2.pelt in torties:
                        if par2.tortiebase.capitalize() in tabbies:
                            pelt_choice = random.choices(pelt_categories, weights=(50, 28, 28, 4, 0))
                        elif par2.tortiebase.capitalize() in spotted:
                            pelt_choice = random.choices(pelt_categories, weights=(40, 40, 16, 4, 0))
                        elif par2.tortiebase.capitalize() in plain:
                            pelt_choice = random.choices(pelt_categories, weights=(40, 16, 40, 4, 0))
                        elif par2.tortiebase.capitalize() in exotic:
                            pelt_choice = random.choices(pelt_categories, weights=(40, 15, 15, 30, 0))
                elif par1.tortiebase.capitalize() in spotted:
                    if par2.pelt in tabbies:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 40, 16, 4, 0))
                    elif par2.pelt in spotted:
                        pelt_choice = random.choices(pelt_categories, weights=(28, 50, 28, 4, 0))
                    elif par2.pelt in plain:
                        pelt_choice = random.choices(pelt_categories, weights=(16, 40, 40, 4, 0))
                    elif par2.pelt in exotic:
                        pelt_choice = random.choices(pelt_categories, weights=(15, 40, 15, 30, 0))
                    elif par2.pelt in torties:
                        if par2.tortiebase.capitalize() in tabbies:
                            pelt_choice = random.choices(pelt_categories, weights=(40, 40, 16, 4, 0))
                        elif par2.tortiebase.capitalize() in spotted:
                            pelt_choice = random.choices(pelt_categories, weights=(28, 50, 28, 4, 0))
                        elif par2.tortiebase.capitalize() in plain:
                            pelt_choice = random.choices(pelt_categories, weights=(16, 40, 40, 4, 0))
                        elif par2.tortiebase.capitalize() in exotic:
                            pelt_choice = random.choices(pelt_categories, weights=(15, 40, 15, 30, 0))
                elif par1.tortiebase.capitalize() in plain:
                    if par2.pelt in tabbies:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 16, 40, 4, 0))
                    elif par2.pelt in spotted:
                        pelt_choice = random.choices(pelt_categories, weights=(16, 40, 40, 4, 0))
                    elif par2.pelt in plain:
                        pelt_choice = random.choices(pelt_categories, weights=(28, 28, 50, 4, 0))
                    elif par2.pelt in exotic:
                        pelt_choice = random.choices(pelt_categories, weights=(15, 15, 40, 30, 0))
                    elif par2.pelt in torties:
                        if par2.tortiebase.capitalize() in tabbies:
                            pelt_choice = random.choices(pelt_categories, weights=(40, 16, 40, 4, 0))
                        elif par2.tortiebase.capitalize() in spotted:
                            pelt_choice = random.choices(pelt_categories, weights=(16, 40, 40, 4, 0))
                        elif par2.tortiebase.capitalize() in plain:
                            pelt_choice = random.choices(pelt_categories, weights=(28, 28, 50, 4, 0))
                        elif par2.tortiebase.capitalize() in exotic:
                            pelt_choice = random.choices(pelt_categories, weights=(15, 15, 40, 30, 0))
                elif par1.tortiebase.capitalize() in exotic:
                    if par2.pelt in tabbies:
                        pelt_choice = random.choices(pelt_categories, weights=(40, 15, 15, 30, 0))
                    elif par2.pelt in spotted:
                        pelt_choice = random.choices(pelt_categories, weights=(15, 40, 15, 30, 0))
                    elif par2.pelt in plain:
                        pelt_choice = random.choices(pelt_categories, weights=(28, 28, 50, 4, 0))
                    elif par2.pelt in exotic:
                        pelt_choice = random.choices(pelt_categories, weights=(20, 20, 20, 40, 0))
                    elif par2.pelt in torties:
                        if par2.tortiebase.capitalize() in tabbies:
                            pelt_choice = random.choices(pelt_categories, weights=(40, 15, 15, 30, 0))
                        elif par2.tortiebase.capitalize() in spotted:
                            pelt_choice = random.choices(pelt_categories, weights=(15, 40, 15, 30, 0))
                        elif par2.tortiebase.capitalize() in plain:
                            pelt_choice = random.choices(pelt_categories, weights=(28, 28, 50, 4, 0))
                        elif par2.tortiebase.capitalize() in exotic:
                            pelt_choice = random.choices(pelt_categories, weights=(20, 20, 20, 40, 0))
            # pelt chosen, continue to color
            if pelt_choice == torties:
                if par1_colour in black_colours:
                    if par2_colour in black_colours:
                        colour_choice = random.choices(colour_categories, weights=(70, 0, 30))
                    elif par2_colour in brown_colours or par2_colour in ginger_colours:
                        colour_choice = random.choices(colour_categories, weights=(50, 0, 50))
                elif par1_colour in brown_colours:
                    if par2_colour in black_colours:
                        colour_choice = random.choices(colour_categories, weights=(30, 0, 70))
                    elif par2_colour in brown_colours or par2_colour in ginger_colours:
                        colour_choice = random.choices(colour_categories, weights=(50, 0, 50))
                elif par1_colour in ginger_colours:
                    if par2_colour in black_colours:
                        colour_choice = random.choices(colour_categories, weights=(70, 0, 30))
                    elif par2_colour in brown_colours or par2_colour in ginger_colours:
                        colour_choice = random.choices(colour_categories, weights=(50, 0, 50))
            else:
                if par1_colour in black_colours:
                    if par2_colour in black_colours:
                        colour_choice = random.choices(colour_categories, weights=(60, 10, 30))
                    elif par2_colour in brown_colours:
                        colour_choice = random.choices(colour_categories, weights=(50, 10, 40))
                    elif par2_colour in ginger_colours:
                        colour_choice = random.choices(colour_categories, weights=(35, 30, 35))
                elif par1_colour in brown_colours:
                    if par2_colour in black_colours:
                        colour_choice = random.choices(colour_categories, weights=(30, 10, 60))
                    elif par2_colour in brown_colours:
                        colour_choice = random.choices(colour_categories, weights=(40, 10, 50))
                    elif par2_colour in ginger_colours:
                        colour_choice = random.choices(colour_categories, weights=(35, 30, 35))
                elif par1_colour in ginger_colours:
                    if par2_colour in black_colours:
                        colour_choice = random.choices(colour_categories, weights=(30, 40, 30))
                    elif par2_colour in brown_colours:
                        colour_choice = random.choices(colour_categories, weights=(20, 40, 40))
                    elif par2_colour in ginger_colours:
                        colour_choice = random.choices(colour_categories, weights=(15, 70, 15))
            # one parent fur length
            if par1.pelt.length == 'short':
                if par2.pelt.length == 'short':
                    length_choice = random.choices(pelt_length, weights=(65, 25, 10))
                elif par2.pelt.length == 'medium':
                    length_choice = random.choices(pelt_length, weights=(40, 40, 20))
                elif par2.pelt.length == 'long':
                    length_choice = random.choices(pelt_length, weights=(25, 50, 25))
            elif par1.pelt.length == 'medium':
                if par2.pelt.length == 'short':
                    length_choice = random.choices(pelt_length, weights=(40, 40, 20))
                elif par2.pelt.length == 'medium':
                    length_choice = random.choices(pelt_length, weights=(35, 35, 30))
                elif par2.pelt.length == 'long':
                    length_choice = random.choices(pelt_length, weights=(20, 40, 40))
            elif par1.pelt.length == 'long':
                if par2.pelt.length == 'short':
                    length_choice = random.choices(pelt_length, weights=(25, 50, 25))
                elif par2.pelt.length == 'medium':
                    length_choice = random.choices(pelt_length, weights=(20, 40, 40))
                elif par2.pelt.length == 'long':
                    length_choice = random.choices(pelt_length, weights=(10, 25, 65))
        # now.. choose
        print("Second Check: " + str(pelt_choice))
        if not cat.pelt:
            cat_pelt_c = choice(colour_choice)
            cat_pelt_l = choice(length_choice)
            choicep = choice(pelt_choice)
            cat_pelt = choice(choicep)
            if tortie and cat.tortiebase == None:
                choiceb = choice(pelt_choice)
                cat.tortiebase = choice(choiceb)
                cat_pelt = choice(torties)
            cat.pelt = choose_pelt(colour=cat_pelt_c, white=white, pelt=cat_pelt, length=cat_pelt_l)
            print("Third Check: " + str(pelt_choice) + str(cat.pelt))

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

