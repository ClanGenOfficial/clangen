import random
from random import choice, randint

# Alphabetical !! yea !!
from .pelts import (
    black_colours,
    blue_eyes,
    brown_colours,
    choose_pelt,
    colour_categories,
    exotic,
    eye_colours,
    ginger_colours,
    green_eyes,
    high_white,
    little_white,
    mid_white,
    mostly_white,
    pelt_categories,
    pelt_length,
    plain,
    plant_accessories,
    point_markings,
    scars1,
    scars3,
    skin_sprites,
    spotted,
    tabbies,
    tortiebases,
    torties,
    vit,
    white_colours,
    wild_accessories,
    yellow_eyes,
    pelt_colours,
    tortiepatterns,
    sphynx,
    cream_colours,
    grey_colours,
    blue_colours,
    green_colours,
    purple_colours,
    yellow_colours,
    pride_colours,
    skin_categories,
    )

from scripts.cat.sprites import Sprites
from scripts.game_structure.game_essentials import game

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
    elif acc_display == ('dry herbs' or 'dry_herbs'):
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
    elif acc_display == 'rat black':
        if plural:
            acc_display = 'black rats'
        if singular:
            acc_display = 'black rat'  
    elif acc_display == 'rat brown':
        if plural:
            acc_display = 'brown rats'
        if singular:
            acc_display = 'brown rat'  
    elif acc_display == 'rat cream':
        if plural:
            acc_display = 'cream rats'
        if singular:
            acc_display = 'cream rat'  
    elif acc_display == 'rat white':
        if plural:
            acc_display = 'white rats'
        if singular:
            acc_display = 'white rat'  
    elif acc_display == 'rat grey':
        if plural:
            acc_display = 'grey rats'
        if singular:
            acc_display = 'grey rat'  
    elif acc_display == 'rat hooded':
        if plural:
            acc_display = 'hooded rats'
        if singular:
            acc_display = 'hooded rat' 

    if plural is True and singular is False:
        return acc_display
    elif singular is True and plural is False:
        return acc_display

# ---------------------------------------------------------------------------- #
#                                init functions                                #
# ---------------------------------------------------------------------------- #


def init_eyes(cat):
    if cat.eye_colour:
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
        num = game.config["cat_generation"]["base_heterochromia"]
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
            # Gather pelt color.
            par_peltcolours.add(p.pelt.colour)

             # Gather pelt length
            par_peltlength.add(p.pelt.length)

            # Gather pelt name
            if p.pelt.name in torties:
                par_peltnames.add(p.tortiebase.capitalize())
            else:
                par_peltnames.add(p.pelt.name)

            # Gather exact pelts, for direct inheritance.
            par_pelts.append(p.pelt)

            # Gather if they have white in their pelt.
            par_white.append(p.pelt.white)
        else:
            # If order for white patches to work correctly, we also want to randomly generate a "pelt_white"
            # for each "None" parent (missing or unknown parent)
            par_white.append(bool(random.getrandbits(1)))

            # Append None
            # Gather pelt color.
            par_peltcolours.add(None)
            par_peltlength.add(None)
            par_peltnames.add(None)

    # If this list is empty, something went wrong.
    if not par_peltcolours:
        print("Error - no parents: pelt randomized")
        randomize_pelt(cat)
        return

    # There is a 1/10 chance for kits to have the exact same pelt as one of their parents
    if not randint(0, game.config["cat_generation"]["direct_inheritance"]):  # 1/10 chance
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
            add_weight = (50, 10, 5, 7)
        elif p_ in spotted:
            add_weight = (10, 50, 5, 5)
        elif p_ in plain:
            add_weight = (5, 5, 50, 0)
        elif p_ in exotic:
            add_weight = (15, 15, 1, 45)
        elif p_ is None:  # If there is at least one unknown parent, a None will be added to the set.
            add_weight = (35, 20, 30, 15)
        else:
            add_weight = (0, 0, 0, 0)

        for x in range(0, len(weights)):
            weights[x] += add_weight[x]

    #A quick check to make sure all the weights aren't 0
    if all([x == 0 for x in weights]):
        weights = [1, 1, 1, 1]

    # Now, choose the pelt category and pelt. The extra 0 is for the tortie pelts,
    chosen_pelt = choice(
        random.choices(pelt_categories, weights=weights + [0], k = 1)[0]
    )

    # Tortie chance
    tortie_chance_f = game.config["cat_generation"]["base_female_tortie"]  # There is a default chance for female tortie
    tortie_chance_m = game.config["cat_generation"]["base_male_tortie"]
    for p_ in par_pelts:
        if p_.name in torties:
            tortie_chance_f = int(tortie_chance_f / 2)
            tortie_chance_m = tortie_chance_m - 1
            break

    # Determine tortie:
    if cat.gender == "female":
        torbie = random.getrandbits(tortie_chance_f) == 1
    else:
        torbie = random.getrandbits(tortie_chance_m) == 1

    chosen_tortie_base = None
    if torbie:
        # If it is tortie, the chosen pelt above becomes the base pelt.
        chosen_tortie_base = chosen_pelt
        if chosen_tortie_base in ["TwoColour", "SingleColour"]:
            chosen_tortie_base = "Single"
        chosen_tortie_base = chosen_tortie_base.lower()
        chosen_pelt = random.choice(torties)

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT COLOUR
    # ------------------------------------------------------------------------------------------------------------#
    # Weights for each colour group. It goes: (cream, ginger, black, grey, white, brown, 
        #blue, yellow, purple, green)
    weights = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for p_ in par_peltcolours:
        if p_ in cream_colours:
            add_weight = (40, 20, 0, 0, 0, 10, 0, 5, 5, 2)
        if p_ in ginger_colours:
            add_weight = (20, 40, 0, 0, 0, 10, 0, 0, 5, 0)
        elif p_ in black_colours:
            add_weight = (0, 0, 40, 20, 2, 5, 5, 0, 0, 0)
        elif p_ in grey_colours:
            add_weight = (0, 0, 10, 40, 10, 2, 5, 0, 0, 1)
        elif p_ in white_colours:
            add_weight = (2, 0, 5, 20, 40, 0, 5, 2, 0, 1)
        elif p_ in brown_colours:
            add_weight = (5, 10, 5, 2, 0, 35, 0, 5, 0, 1)
        elif p_ in blue_colours:
            add_weight = (0, 0, 20, 20, 20, 0, 25, 0, 2, 0)
        elif p_ in yellow_colours:
            add_weight = (10, 0, 0, 0, 10, 20, 0, 25, 0, 5)
        elif p_ in purple_colours:
            add_weight = (20, 20, 0, 0, 0, 0, 0, 5, 25, 0)
        elif p_ in green_colours:
            add_weight = (2, 0, 0, 1, 1, 1, 0, 5, 0, 35)
        elif p_ is None:
            add_weight = (40, 40, 40, 40, 40, 40, 2, 2, 2, 15)
        else:
            add_weight = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

        for x in range(0, len(weights)):
            weights[x] += add_weight[x]

        # A quick check to make sure all the weights aren't 0
        if all([x == 0 for x in weights]):
            weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

    chosen_pelt_color = choice(
        random.choices(colour_categories, weights=weights, k=1)[0])

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT LENGTH
    # ------------------------------------------------------------------------------------------------------------#

    weights = [0, 0, 0]  # Weights for each length. It goes (short, medium, long)
    for p_ in par_peltlength:
        if p_ == "short":
            add_weight = (50, 10, 2)
        elif p_ == "medium":
            add_weight = (25, 50, 25)
        elif p_ == "long":
            add_weight = (2, 10, 50)
        elif p_ is None:
            add_weight = (10, 10, 10)
        else:
            add_weight = (0, 0, 0)

        for x in range(0, len(weights)):
            weights[x] += add_weight[x]

    # A quick check to make sure all the weights aren't 0
    if all([x == 0 for x in weights]):
        weights = [1, 1, 1]

    chosen_pelt_length = random.choices(pelt_length, weights=weights, k=1)[0]

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT WHITE
    # ------------------------------------------------------------------------------------------------------------#

    # There is 94 percentage points that can be added by
    # parents having white. If we have more than two, this
    # will keep that the same.
    percentage_add_per_parent = int(94 / len(par_white))
    chance = 3
    for p_ in par_white:
        if p_:
            chance += percentage_add_per_parent

    chosen_white = random.randint(1, 100) <= chance

    # Adjustments to pelt chosen based on if the pelt has white in it or not.
    if chosen_pelt in ["TwoColour", "SingleColour"]:
        if chosen_white:
            chosen_pelt = "TwoColour"
        else:
            chosen_pelt = "SingleColour"
    elif chosen_pelt == "Calico":
        if not chosen_white:
            chosen_pelt = "Tortie"

    # SET THE PELT
    cat.pelt = choose_pelt(chosen_pelt_color, chosen_white, chosen_pelt, chosen_pelt_length)
    cat.tortiebase = chosen_tortie_base   # This will be none if the cat isn't a tortie.

def randomize_pelt(cat):
    # ------------------------------------------------------------------------------------------------------------#
    #   PELT
    # ------------------------------------------------------------------------------------------------------------#

    # Determine pelt.
    chosen_pelt = choice(
        random.choices(pelt_categories, weights=(35, 20, 30, 15, 0), k=1)[0]
    )

    # Tortie chance
    # There is a default chance for female tortie, slightly increased for completely random generation.
    tortie_chance_f = game.config["cat_generation"]["base_female_tortie"] - 1
    tortie_chance_m = game.config["cat_generation"]["base_male_tortie"]
    if cat.gender == "female":
        torbie = random.getrandbits(tortie_chance_f) == 1
    else:
        torbie = random.getrandbits(tortie_chance_m) == 1

    chosen_tortie_base = None
    if torbie:
        # If it is tortie, the chosen pelt above becomes the base pelt.
        chosen_tortie_base = chosen_pelt
        if chosen_tortie_base in ["TwoColour", "SingleColour"]:
            chosen_tortie_base = "Single"
        chosen_tortie_base = chosen_tortie_base.lower()
        chosen_pelt = random.choice(torties)

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT COLOUR
    # ------------------------------------------------------------------------------------------------------------#

    chosen_pelt_color = choice(
        random.choices(colour_categories, weights=(30, 45, 40, 30, 25, 45, 15, 15, 10, 25), k=1)[0]
    )

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT LENGTH
    # ------------------------------------------------------------------------------------------------------------#


    chosen_pelt_length = random.choice(pelt_length)

    # ------------------------------------------------------------------------------------------------------------#
    #   PELT WHITE
    # ------------------------------------------------------------------------------------------------------------#


    chosen_white = random.randint(1, 100) <= 40

    # Adjustments to pelt chosen based on if the pelt has white in it or not.
    if chosen_pelt in ["TwoColour", "SingleColour"]:
        if chosen_white:
            chosen_pelt = "TwoColour"
        else:
            chosen_white = "SingleColour"
    elif chosen_pelt == "Calico":
        if not chosen_white:
            chosen_pelt = "Tortie"

    cat.pelt = choose_pelt(chosen_pelt_color, chosen_white, chosen_pelt, chosen_pelt_length)
    cat.tortiebase = chosen_tortie_base   # This will be none if the cat isn't a tortie.

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
    if cat.parent1 is None:
        cat.skin = choice(random.choices(skin_categories, weights=(297, 5, 3, 2, 1, 3), k=1) [0])
    elif cat.parent2 is None:
        par1 = cat.all_cats[cat.parent1]
        cat.skin = choice([par1.skin, choice(random.choices(skin_categories, weights=(191, 5, 3, 2, 1, 3), k=1)[0])])
    else:
        par1 = cat.all_cats[cat.parent1]
        par2 = cat.all_cats[cat.parent2]
        cat.skin = choice([par1.skin, par2.skin, choice(random.choices(skin_categories, weights=(187, 6, 4, 3, 2, 4), k=1)[0])]) 

    if cat.skin in sphynx:
        cat.pelt.length = 'short'
            
    if cat.pelt is not None:
        if cat.pelt.length != 'long':
            cat.age_sprites['adult'] = randint(6, 8)
        else:
            cat.age_sprites['adult'] = randint(0, 2)
        cat.age_sprites['young adult'] = cat.age_sprites['adult']
        cat.age_sprites['senior adult'] = cat.age_sprites['adult']
        cat.age_sprites['dead'] = None
            
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
        if not cat.tortiebase:
            cat.tortiebase = choice(tortiebases)
        if not cat.pattern:
            cat.pattern = choice(tortiepatterns)

        wildcard_chance = game.config["cat_generation"]["wildcard_tortie"]
        if cat.pelt.colour:
            # The "not wildcard_chance" allows users to set wildcard_tortie to 0
            # and always get wildcard torties.
            if not wildcard_chance or random.getrandbits(wildcard_chance) == 1:
                # This is the "wildcard" chance, where you can get funky combinations.
                print("WILDCARD TORTIE")

                # Allow any pattern:
                cat.tortiepattern = choice(tortiebases)

                # Allow any colors that aren't the base color.
                possible_colors = pelt_colours.copy()
                possible_colors.remove(cat.pelt.colour)
                possible_colors.extend(pride_colours * 4)
                cat.tortiecolour = choice(possible_colors)

            else:
                # Normal generation
                if cat.tortiebase in ["backed", "smoke", "single"]:
                    cat.tortiepattern = choice(['ghost', 'rat', 'snowflake', 'backed', 'smoke'])
                elif cat.tortiebase in ["speckled", "mottled"]:
                    cat.tortiepattern = choice(['speckled', 'mottled'])
                elif cat.tortiebase in ["charcoal", "hooded"]:
                    cat.tortiepattern = choice(['charcoal', 'hooded'])    
                else:
                    cat.tortiepattern = random.choices([cat.tortiebase, 'ghost', 'rat', 'skele'], weights=[93, 3, 3, 1], k=1)[0]

                # Ginger is often duplicated to increase its chances
                if cat.pelt.colour in ["WHITE", "SILVER", "BRONZE", "GREY", "PALEBOW", "TURQUOISE", "TIFFANY", "SHINYMEW", "SKY",
                                    "POWDERBLUE"]:
                    cat.tortiecolour = choice(['PALECREAM', 'CREAM', 'SAND', 'WOOD', 'PETAL', 'PANTONE', 'SALMON', 
                                    'THISTLE', 'MEW', 'LIME', 'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD', 'OLIVE'] + (pride_colours * 2))
                elif cat.pelt.colour in ["GREY", "MARENGO", "BATTLESHIP", "CADET", "BLUEGREY", "STEEL", "SLATE", "SAPPHIRE", "OCEAN", 
                                    "DENIUM", "TEAL", "COBALT"]:
                    cat.tortiecolour = choice(['ROSE', 'GINGER', 'SUNSET', 'RUFOUS', 'FIRE', 'BRICK', 'SCARLET', 'APRICOT', 
                                    'GARFIELD', 'APPLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA', 'HEATHER', 'ORCHID', 
                                    'PURPLE', 'DARKOLIVE', 'GREEN', 'SPINNACH', 'SEAWEED', 'SACRAMENTO'] + (pride_colours * 2))
                elif cat.pelt.colour in ["SOOT", "DARKGREY", "ANCHOR", "CHARCOAL", "COAL", "BLACK", "DUSKBOW", "SONIC", "JEANS", "NAVY"]:
                    cat.tortiecolour = choice(['RED', 'CRIMSON', 'BURNT', 'CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD', 'RASIN',
                                    'STRAKIT',  'WINE', 'GENDER', 'REDNEG', 'FOREST', 'JADE', 'XANADU', 'DEEPFOREST'] + (pride_colours * 2))
                
                elif cat.pelt.colour in ["PALECREAM", "CREAM", "SAND", "WOOD", "PETAL", "PANTONE", "SALMON", "THISTLE", "MEW"]:
                    cat.tortiecolour = choice(['WHITE', 'SILVER', 'BRONZE', 'GREY', 'PALEBOW', 
                                    'TURQUOISE', 'TIFFANY', 'SHINYMEW', 'SKY', 'POWDERBLUE', 'LIME', 
                                    'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD', 'OLIVE'] + (pride_colours * 2))
                elif cat.pelt.colour in ["ROSE", "GINGER", "SUNSET", "RUFOUS", "FIRE", "BRICK", "SCARLET", "APRICOT", 
                                    "GARFIELD", "APPLE", "AMYTHYST", "DARKSALMON", "MAGENTA", "HEATHER", "ORCHID", 
                                    "PURPLE"]:
                    cat.tortiecolour = choice(['GREY', 'MARENGO', 'BATTLESHIP', 'CADET', 'BLUEGREY', 'STEEL', 'SLATE',
                                    'SAPPHIRE', 'OCEAN', 'DENIUM', 'TEAL', 'COBALT', 'DARKOLIVE', 'GREEN', 'SPINNACH', 
                                    'SEAWEED', 'SACRAMENTO'] + (pride_colours * 2))
                elif cat.pelt.colour in ["RED", "CRIMSON", "BURNT", "CARMINE", "COSMOS", "ROSEWOOD", "BLOOD", "RASIN",
                                    "STRAKIT",  "WINE", "GENDER", "REDNEG"]:                   
                    cat.tortiecolour = choice(['SOOT', 'DARKGREY', 'ANCHOR', 'CHARCOAL', 'COAL', 'BLACK', 'DUSKBOW', 
                                    'SONIC', 'JEANS', 'NAVY', 'FOREST', 'JADE', 'XANADU', 'DEEPFOREST'] + (pride_colours * 2))

                elif cat.pelt.colour in ["BEIGE", "MEERKAT", "KHAKI", "IVORY", "BANNANA", "FARROW", "HAY"]:
                    cat.tortiecolour = choice(['PALECREAM', 'CREAM', 'SAND', 'WOOD', 'PETAL', 'PANTONE', 'SALMON', 
                                    'THISTLE', 'MEW', 'WHITE', 'SILVER', 'BRONZE', 'GREY', 'PALEBOW', 
                                    'TURQUOISE', 'TIFFANY', 'SHINYMEW', 'SKY', 'POWDERBLUE', 'LIME', 
                                    'CHARTRUSE', 'LETTUCE', 'GRASS', 'MINT', 'EMERALD', 'OLIVE'] + (pride_colours * 2))
                elif cat.pelt.colour in ["CAPPUCCINO", "ECRU", "ASHBROWN", "DUSTBROWN", "SANDALWOOD", "PINECONE", "WRENGE", "BROWN", 
                                    "MINK", "CHESTNUT", "TAN", "FAWN", "HAZELNUT", "LEMON", "LAGUNA", "YELLOW", "CORN",
                                    "BEE"]:
                    cat.tortiecolour = choice(['ROSE', 'GINGER', 'SUNSET', 'RUFOUS', 'FIRE', 'BRICK', 'SCARLET', 'APRICOT', 
                                    'GARFIELD', 'APPLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA', 'HEATHER', 'ORCHID', 
                                    'PURPLE', 'GREY', 'MARENGO', 'BATTLESHIP', 'CADET', 'BLUEGREY', 'STEEL', 'SLATE',
                                    'SAPPHIRE', 'OCEAN', 'DENIUM', 'TEAL', 'COBALT', 'DARKOLIVE', 'GREEN', 'SPINNACH', 
                                    'SEAWEED', 'SACRAMENTO'] + (pride_colours * 2))
                elif cat.pelt.colour in ["DARKBROWN", "BEAVER", "CHOCOLATE", "MOCHA", "COFFEE", "TAUPE", "UMBER", "ONYX", "GOLD", "HONEY", 
                                    "PINEAPPLE", "TROMBONE", "MEDALLION", "GRANOLA", "SADDLE", "CEDAR"]:
                    cat.tortiecolour = choice(['RED', 'CRIMSON', 'BURNT', 'CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD', 'RASIN',
                                    'STRAKIT',  'WINE', 'GENDER', 'REDNEG', 'SOOT', 'DARKGREY', 'ANCHOR', 'CHARCOAL', 
                                    'COAL', 'BLACK', 'DUSKBOW', 'SONIC', 'JEANS', 'NAVY', 'FOREST', 'JADE', 'XANADU', 
                                    'DEEPFOREST'] + (pride_colours * 2))

                elif cat.pelt.colour in ["LIME", "CHARTRUSE", "LETTUCE", "GRASS", "MINT", "EMERALD", "OLIVE"]:
                    cat.tortiecolour = choice (['PALECREAM', 'CREAM', 'SAND', 'WOOD', 'PETAL', 'PANTONE', 'SALMON', 
                                    'THISTLE', 'MEW', 'WHITE', 'SILVER', 'BRONZE', 'GREY', 'PALEBOW', 
                                    'TURQUOISE', 'TIFFANY', 'SHINYMEW', 'SKY', 'POWDERBLUE'] + (pride_colours * 2))
                elif cat.pelt.colour in ["DARKOLIVE", "GREEN", "SPINNACH", "SEAWEED", "SACRAMENTO"]:
                    cat.tortiecolour = choice (['ROSE', 'GINGER', 'SUNSET', 'RUFOUS', 'FIRE', 'BRICK', 'SCARLET', 'APRICOT', 
                                    'GARFIELD', 'APPLE', 'AMYTHYST', 'DARKSALMON', 'MAGENTA', 'HEATHER', 'ORCHID', 
                                    'PURPLE', 'GREY', 'MARENGO', 'BATTLESHIP', 'CADET', 'BLUEGREY', 'STEEL', 'SLATE',
                                    'SAPPHIRE', 'OCEAN', 'DENIUM', 'TEAL', 'COBALT'] + (pride_colours * 2))
                elif cat.pelt.colour in ["FOREST", "JADE", "XANADU", "DEEPFOREST"]:
                    cat.tortiecolour = choice (['RED', 'CRIMSON', 'BURNT', 'CARMINE', 'COSMOS', 'ROSEWOOD', 'BLOOD', 'RASIN',
                                    'STRAKIT', 'WINE', 'GENDER', 'REDNEG', 'SOOT', 'DARKGREY', 'ANCHOR', 'CHARCOAL', 
                                    'COAL', 'BLACK', 'DUSKBOW', 'SONIC', 'JEANS', 'NAVY'] + (pride_colours * 2))  

        else:
            cat.tortiecolour = choice(pride_colours)
    else:
        cat.tortiebase = None
        cat.tortiepattern = None
        cat.tortiecolour = None
        cat.pattern = None


def white_patches_inheritance(cat, parents: tuple):

    par_whitepatches = set()
    for p in parents:
        if p and p.white_patches:
            par_whitepatches.add(p.white_patches)

    if not parents:
        print("Error - no parents. Randomizing white patches.")
        randomize_white_patches(cat)
        return

    # Direct inheritance. Will only work if at least one parent has white patches, otherwise continue on.
    if par_whitepatches and not randint(0, game.config["cat_generation"]["direct_inheritance"]):
        cat.white_patches = choice(list(par_whitepatches))
        return

    vit_chance = not randint(0, 40)
    if vit_chance:
        cat.white_patches = choice(vit)
        return

    white_list = [little_white, mid_white, high_white, mostly_white, point_markings, ['FULLWHITE']]

    weights = [0, 0, 0, 0, 0, 0]  # Same order as white_list
    for p_ in par_whitepatches:
        if p_ in little_white:
            add_weights = (40, 20, 15, 5, 0, 0)
        elif p_ in mid_white:
            add_weights = (10, 40, 15, 10, 0, 0)
        elif p_ in high_white:
            add_weights = (15, 20, 40, 10, 0, 1)
        elif p_ in mostly_white:
            add_weights = (5, 15, 20, 40, 0, 5)
        elif p_ in point_markings:
            add_weights = (10, 10, 10, 10, 65, 5)
        elif p_ == "FULLWHITE":
            add_weights = (0, 5, 15, 40, 0, 10)
        else:
            add_weights = (0, 0, 0, 0, 0, 0)

        for x in range(0, len(weights)):
            weights[x] += add_weights[x]


    # If all the weights are still 0, that means none of the parents have white patches.
    if not any(weights):
        if not all(parents):  # If any of the parents are None (unknown), use the following distribution:
            weights = [20, 10, 10, 5, 5, 0]
        else:
            # Otherwise, all parents are known and don't have any white patches. Focus distribution on little_white.
            weights = [50, 5, 0, 0, 0, 0]

    # Adjust weights for torties, since they can't have anything greater than mid_white:
    if cat.pelt.name == "Tortie":
        weights = weights[:2] + [0, 0, 0, 0]
        # Another check to make sure not all the values are zero. This should never happen, but better
        # safe then sorry.
        if not any(weights):
            weights = [2, 1, 0, 0, 0, 0]


    chosen_white_patches = choice(
        random.choices(white_list, weights=weights, k=1)[0]
    )

    cat.white_patches = chosen_white_patches

def randomize_white_patches(cat):
    vit_chance = not randint(0, 40)
    if vit_chance:
        cat.white_patches = choice(vit)
        return

    # Adjust weights for torties, since they can't have anything greater than mid_white:
    if cat.pelt.name == "Tortie":
        weights = (2, 1, 0, 0, 0, 0)
    else:
        weights = (10, 10, 10, 10, 5, 1)


    white_list = [little_white, mid_white, high_white, mostly_white, point_markings, ['FULLWHITE']]
    chosen_white_patches = choice(
        random.choices(white_list, weights=weights, k=1)[0]
    )

    cat.white_patches = chosen_white_patches

def init_white_patches(cat):

    if cat.pelt is None:
        init_pelt(cat)

    if cat.white_patches:
        return

    if cat.pelt.white:

        par1 = None
        par2 = None
        if cat.parent1 in cat.all_cats:
            par1 = cat.all_cats[cat.parent1]
        if cat.parent2 in cat.all_cats:
            par2 = cat.all_cats[cat.parent2]

        if par1 or par2:
            white_patches_inheritance(cat, (par1, par2))
        else:
            randomize_white_patches(cat)

def init_tint(cat):
    """Sets tint for pelt and white patches"""

    # Basic tints as possible for all colors.
    cat.tint = "none"

    # These are the patches where the tint should always be none
    no_tint_patches = point_markings + vit

    if cat.white_patches and cat.white_patches not in no_tint_patches:
        #Now for white patches
        possible_tints = Sprites.white_patches_tints["possible_tints"]["basic"].copy()
        cat.white_patches_tint = choice(possible_tints)
    else:
        cat.white_patches_tint = "none"
