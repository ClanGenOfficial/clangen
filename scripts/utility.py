import ujson

from scripts.cat.sprites import *
from scripts.cat.pelts import *
from scripts.game_structure.game_essentials import *

# ---------------------------------------------------------------------------- #
#                       Relationship / Traits / Relative                       #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/"
PERSONALITY_COMPATIBILITY = None
with open(f"{resource_directory}personality_compatibility.json",'r') as read_file:
    PERSONALITY_COMPATIBILITY = ujson.loads(read_file.read())

def get_highest_romantic_relation(relationships):
    """Returns the relationship with the highest romantic value."""
    romantic_relation = list(
        filter(lambda rel: rel.romantic_love > 0, relationships))
    if romantic_relation is None or len(romantic_relation) == 0:
        return None

    relation = romantic_relation[0]
    max_love_value = relation.romantic_love
    # if there more love relations, pick the biggest one
    for inter_rel in romantic_relation:
        if max_love_value < inter_rel.romantic_love:
            max_love_value = inter_rel.romantic_love
            relation = inter_rel

    return relation

def get_personality_compatibility(cat1, cat2):
    """Returns:
        True - if personalities have a positive compatibility
        False - if personalities have a negative compatibility
        None - if personalities have a neutral compatibility
    """
    personality1 = cat1.trait
    personality2 = cat2.trait

    if personality1 == personality2 and personality1 in game.cat_class.traits:
        return True

    if personality1 in PERSONALITY_COMPATIBILITY:
        if personality2 in PERSONALITY_COMPATIBILITY[personality1]:
            return PERSONALITY_COMPATIBILITY[personality1][personality2]

    if personality2 in PERSONALITY_COMPATIBILITY:
        if personality1 in PERSONALITY_COMPATIBILITY[personality2]:
            return PERSONALITY_COMPATIBILITY[personality2][personality1]

    return None

def get_amount_of_cats_with_relation_value_towards(cat, value, all_cats):
    """
    Looks how many cats have the certain value 
    :param cat: cat in question
    :param value: value which has to be reached
    :param all_cats: list of cats which has to be checked
    """

    # collect all true or false if the value is reached for the cat or not
    # later count or sum can be used to get the amount of cats
    # this will be handled like this, because it is easier / shorter to check
    relation_dict = {
        "romantic_love": [],
        "platonic_like": [],
        "dislike": [],
        "admiration": [],
        "comfortable": [],
        "jealousy": [],
        "trust": []
    }

    for inter_cat in all_cats:
        relation = list(filter(lambda r: r.cat_to.ID == cat.ID, inter_cat.relationships))
        if len(relation) < 1:
            continue
        
        relation = relation[0]
        relation_dict['romantic_love'].append(relation.romantic_love >= value)
        relation_dict['platonic_like'].append(relation.platonic_like >= value)
        relation_dict['dislike'].append(relation.dislike >= value)
        relation_dict['admiration'].append(relation.admiration >= value)
        relation_dict['comfortable'].append(relation.comfortable >= value)
        relation_dict['jealousy'].append(relation.jealousy >= value)
        relation_dict['trust'].append(relation.trust >= value)

    return_dict = {
        "romantic_love": sum(relation_dict['romantic_love']),
        "platonic_like": sum(relation_dict['platonic_like']),
        "dislike": sum(relation_dict['dislike']),
        "admiration": sum(relation_dict['admiration']),
        "comfortable": sum(relation_dict['comfortable']),
        "jealousy": sum(relation_dict['jealousy']),
        "trust": sum(relation_dict['trust'])
    }

    return return_dict

def add_siblings_to_cat(cat, cat_class):
    """Iterate over all current cats and add the ID to the current cat."""
    for inter_cat in cat_class.all_cats.values():
        if inter_cat.is_sibling(cat) and inter_cat.ID not in cat.siblings:
            cat.siblings.append(inter_cat.ID)
        if cat.is_sibling(inter_cat) and cat.ID not in inter_cat.siblings:
            inter_cat.siblings.append(cat.ID)

def add_children_to_cat(cat, cat_class):
    """Iterate over all current cats and add the ID to the current cat."""
    for inter_cat in cat_class.all_cats.values():
        if cat.is_parent(cat) and inter_cat.ID not in cat.children:
            cat.children.append(inter_cat.ID)
        if inter_cat.is_parent(inter_cat) and cat.ID not in inter_cat.children:
            inter_cat.children.append(cat.ID)

# ---------------------------------------------------------------------------- #
#                                    Sprites                                   #
# ---------------------------------------------------------------------------- #

def draw(cat, pos):
    new_pos = list(pos)
    if pos[0] == 'center':
        new_pos[0] = screen_x / 2 - sprites.size / 2
    elif pos[0] < 0:
        new_pos[0] = screen_x + pos[0] - sprites.size
    cat.used_screen.blit(cat.sprite, new_pos)

def draw_big(cat, pos):
    new_pos = list(pos)
    if pos[0] == 'center':
        new_pos[0] = screen_x / 2 - sprites.new_size / 2
    elif pos[0] < 0:
        new_pos[0] = screen_x + pos[0] - sprites.new_size
    cat.used_screen.blit(cat.big_sprite, new_pos)

def draw_large(cat, pos):
    new_pos = list(pos)
    if pos[0] == 'center':
        new_pos[0] = screen_x / 2 - sprites.size * 3 / 2
    elif pos[0] < 0:
        new_pos[0] = screen_x + pos[0] - sprites.size * 3
    cat.used_screen.blit(cat.large_sprite, new_pos)

def update_sprite(cat):
    # First make pelt, if it wasn't possible before
    if cat.pelt is None:
        if cat.parent1 is None:
            # If pelt has not been picked manually, this function chooses one based on possible inheritances
            cat.pelt = choose_pelt(cat.gender)
        elif cat.parent2 is None and cat.parent1 in cat.all_cats.keys():
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
            cat.pelt = choose_pelt(cat.gender)            
                          
    # THE SPRITE UPDATE
    # draw colour & style
    new_sprite = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)
    game.switches['error_message'] = 'There was an error loading a cat\'s base coat sprite. Last cat read was ' + str(cat)
    if cat.pelt.name not in ['Tortie', 'Calico']:
        if cat.pelt.length == 'long' and cat.status not in ['kitten', 'apprentice', 'medicine cat apprentice'] or cat.age == 'elder':
            new_sprite.blit(sprites.sprites[cat.pelt.sprites[1] + 'extra' + cat.pelt.colour + str(cat.age_sprites[cat.age])], (0, 0))
        else:
            new_sprite.blit(sprites.sprites[cat.pelt.sprites[1] + cat.pelt.colour + str(cat.age_sprites[cat.age])], (0, 0))
    else:
        game.switches['error_message'] = 'There was an error loading a tortie\'s base coat sprite. Last cat read was ' + str(cat)
        if cat.pelt.length == 'long' and cat.status not in ['kitten', 'apprentice', 'medicine cat apprentice'] or cat.age == 'elder':
            new_sprite.blit(sprites.sprites[cat.tortiebase + 'extra' + cat.tortiecolour + str(cat.age_sprites[cat.age])], (0, 0))
            game.switches['error_message'] = 'There was an error loading a tortie\'s pattern sprite. Last cat read was ' + str(cat)
            new_sprite.blit(sprites.sprites[cat.tortiepattern + 'extra' + cat.pattern + str(cat.age_sprites[cat.age])], (0, 0))
        else:
            new_sprite.blit(sprites.sprites[cat.tortiebase + cat.tortiecolour + str(cat.age_sprites[cat.age])], (0, 0))
            game.switches['error_message'] = 'There was an error loading a tortie\'s pattern sprite. Last cat read was ' + str(cat)
            new_sprite.blit(sprites.sprites[cat.tortiepattern + cat.pattern + str(cat.age_sprites[cat.age])], (0, 0))
    game.switches['error_message'] = 'There was an error loading a cat\'s white patches sprite. Last cat read was ' + str(cat)
    # draw white patches
    if cat.white_patches is not None:
        if cat.pelt.length == 'long' and cat.status not in ['kitten', 'apprentice', 'medicine cat apprentice']\
            or cat.age == 'elder':
            new_sprite.blit(
                sprites.sprites['whiteextra' + cat.white_patches +
                                str(cat.age_sprites[cat.age])], (0, 0))
        else:
            new_sprite.blit(
                sprites.sprites['white' + cat.white_patches +
                                str(cat.age_sprites[cat.age])], (0, 0))
    game.switches[
        'error_message'] = 'There was an error loading a cat\'s scar and eye sprites. Last cat read was ' + str(
            cat)
    # draw eyes & scars1
    if cat.pelt.length == 'long' and cat.status not in [
            'kitten', 'apprentice', 'medicine cat apprentice'
    ] or cat.age == 'elder':
        if cat.specialty in scars1:
            new_sprite.blit(
                sprites.sprites['scarsextra' + cat.specialty +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty2 in scars1:
            new_sprite.blit(
                sprites.sprites['scarsextra' + cat.specialty2 +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty in scars4:
            new_sprite.blit(
                sprites.sprites['scarsextra' + cat.specialty +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty2 in scars4:
            new_sprite.blit(
                sprites.sprites['scarsextra' + cat.specialty2 +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty in scars5:
            new_sprite.blit(
                sprites.sprites['scarsextra' + cat.specialty +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty2 in scars5:
            new_sprite.blit(
                sprites.sprites['scarsextra' + cat.specialty2 +
                                str(cat.age_sprites[cat.age])], (0, 0))
        new_sprite.blit(
            sprites.sprites['eyesextra' + cat.eye_colour +
                            str(cat.age_sprites[cat.age])], (0, 0))
    else:
        if cat.specialty in scars1:
            new_sprite.blit(
                sprites.sprites['scars' + cat.specialty +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty2 in scars1:
            new_sprite.blit(
                sprites.sprites['scars' + cat.specialty2 +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty in scars4:
            new_sprite.blit(
                sprites.sprites['scars' + cat.specialty +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty2 in scars4:
            new_sprite.blit(
                sprites.sprites['scars' + cat.specialty2 +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty in scars5:
            new_sprite.blit(
                sprites.sprites['scars' + cat.specialty +
                                str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty2 in scars5:
            new_sprite.blit(
                sprites.sprites['scars' + cat.specialty2 +
                                str(cat.age_sprites[cat.age])], (0, 0))
        new_sprite.blit(
            sprites.sprites['eyes' + cat.eye_colour +
                            str(cat.age_sprites[cat.age])], (0, 0))
    game.switches[
        'error_message'] = 'There was an error loading a cat\'s shader sprites. Last cat read was ' + str(
            cat)
    # draw line art
    if game.settings['shaders'] and not cat.dead:
        if cat.pelt.length == 'long' and cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice'
        ] or cat.age == 'elder':
            new_sprite.blit(
                sprites.sprites['shaders' +
                                str(cat.age_sprites[cat.age] + 9)],
                (0, 0))
        else:
            new_sprite.blit(
                sprites.sprites['shaders' +
                                str(cat.age_sprites[cat.age])], (0, 0))
    elif not cat.dead:
        if cat.pelt.length == 'long' and cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice'
        ] or cat.age == 'elder':
            new_sprite.blit(
                sprites.sprites['lines' +
                                str(cat.age_sprites[cat.age] + 9)],
                (0, 0))
        else:
            new_sprite.blit(
                sprites.sprites['lines' + str(cat.age_sprites[cat.age])],
                (0, 0))
    elif cat.dead:
        if cat.pelt.length == 'long' and cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice'
        ] or cat.age == 'elder':
            new_sprite.blit(
                sprites.sprites['lineartdead' +
                                str(cat.age_sprites[cat.age] + 9)],
                (0, 0))
        else:
            new_sprite.blit(
                sprites.sprites['lineartdead' +
                                str(cat.age_sprites[cat.age])], (0, 0))
    game.switches[
        'error_message'] = 'There was an error loading a cat\'s skin and second set of scar sprites. Last cat read was ' + str(
            cat)
    # draw skin and scars2
    blendmode = pygame.BLEND_RGBA_MIN
    if cat.pelt.length == 'long' and cat.status not in [
            'kitten', 'apprentice', 'medicine cat apprentice'
    ] or cat.age == 'elder':
        new_sprite.blit(
            sprites.sprites['skinextra' + cat.skin +
                            str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty in scars2:
            new_sprite.blit(sprites.sprites['scarsextra' + cat.specialty +
            str(cat.age_sprites[cat.age])], (0, 0), special_flags=blendmode)
        if cat.specialty2 in scars2:
            new_sprite.blit(sprites.sprites['scarsextra' + cat.specialty2 +
            str(cat.age_sprites[cat.age])], (0, 0), special_flags=blendmode)
        
    else:
        new_sprite.blit(
            sprites.sprites['skin' + cat.skin +
            str(cat.age_sprites[cat.age])], (0, 0))
        if cat.specialty in scars2:
            new_sprite.blit(sprites.sprites['scars' + cat.specialty +
            str(cat.age_sprites[cat.age])], (0, 0), special_flags=blendmode)
        if cat.specialty2 in scars2:
            new_sprite.blit(sprites.sprites['scars' + cat.specialty2 +
            str(cat.age_sprites[cat.age])], (0, 0), special_flags=blendmode)
       
        
    game.switches[
    'error_message'] = 'There was an error loading a cat\'s accessory. Last cat read was ' + str(
        cat)                            
    # draw accessories        
    if cat.pelt.length == 'long' and cat.status not in [
            'kitten', 'apprentice', 'medicine cat apprentice'
    ] or cat.age == 'elder':
        if cat.accessory in plant_accessories:
            new_sprite.blit(
                sprites.sprites['acc_herbsextra' + cat.accessory +
                                str(cat.age_sprites[cat.age])], (0, 0))
        elif cat.accessory in wild_accessories:
            new_sprite.blit(
                sprites.sprites['acc_wildextra' + cat.accessory +
                                str(cat.age_sprites[cat.age])], (0, 0))
        elif cat.accessory in collars:
            new_sprite.blit(
                sprites.sprites['collarsextra' + cat.accessory +
                                str(cat.age_sprites[cat.age])], (0, 0))
        elif cat.accessory in collars:
            new_sprite.blit(
                sprites.sprites['collarsextra' + cat.accessory +
                                str(cat.age_sprites[cat.age])], (0, 0))
    else:
        if cat.accessory in plant_accessories:
            new_sprite.blit(
                sprites.sprites['acc_herbs' + cat.accessory +
                                str(cat.age_sprites[cat.age])], (0, 0))
        elif cat.accessory in wild_accessories:
            new_sprite.blit(
                sprites.sprites['acc_wild' + cat.accessory +
                                str(cat.age_sprites[cat.age])], (0, 0))
        elif cat.accessory in collars:
            new_sprite.blit(
                sprites.sprites['collars' + cat.accessory +
                                str(cat.age_sprites[cat.age])], (0, 0))
        elif cat.accessory in collars:
            new_sprite.blit(
                sprites.sprites['collars' + cat.accessory +
                                str(cat.age_sprites[cat.age])], (0, 0))
    game.switches[
        'error_message'] = 'There was an error loading a cat\'s skin and second set of scar sprites. Last cat read was ' + str(
            cat)
    game.switches[
        'error_message'] = 'There was an error reversing a cat\'s sprite. Last cat read was ' + str(
            cat)
            
    # reverse, if assigned so
    if cat.reverse:
        new_sprite = pygame.transform.flip(new_sprite, True, False)
    game.switches[
        'error_message'] = 'There was an error scaling a cat\'s sprites. Last cat read was ' + str(
            cat)
    # apply
    cat.sprite = new_sprite
    cat.big_sprite = pygame.transform.scale(
        new_sprite, (sprites.new_size, sprites.new_size))
    cat.large_sprite = pygame.transform.scale(
        cat.big_sprite, (sprites.size * 3, sprites.size * 3))
    game.switches[
        'error_message'] = 'There was an error updating a cat\'s sprites. Last cat read was ' + str(
            cat)
    # update class dictionary
    cat.all_cats[cat.ID] = cat
    game.switches['error_message'] = ''
