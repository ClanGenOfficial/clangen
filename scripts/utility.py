import pygame
try:
    import ujson
except ImportError:
    import json as ujson
import traceback
from scripts.game_structure import image_cache

from scripts.cat.sprites import *
from scripts.cat.pelts import *
from scripts.game_structure.game_essentials import *

def scale(rect):
    rect[0] = round(rect[0]/1600 * screen_x) if rect[0] > 0 else rect[0]
    rect[1] = round(rect[1]/1400 * screen_y) if rect[1] > 0 else rect[1]
    rect[2] = round(rect[2] / 1600 * screen_x) if rect[2] > 0 else rect[2]
    rect[3] = round(rect[3] / 1400 * screen_y) if rect[3] > 0 else rect[3]

    return rect


def get_alive_clan_queens(all_cats):
	"""Returns a list with all cats with the 'status' queen."""
	queens = []
	for inter_cat in all_cats.values():
		if inter_cat.dead:
			continue
		if str(inter_cat.status) != 'kitten' or inter_cat.parent1 is None:
			continue

		parent_1 = all_cats[inter_cat.parent1]
		parent_2 = None
		if inter_cat.parent2:
			parent_2 = all_cats[inter_cat.parent2]

		if parent_1.gender == 'male':
			if (parent_2 is None or parent_2.gender == 'male') and\
				not parent_1.dead and not parent_1.exiled and not parent_1.outside:
				queens.append(parent_1)
			elif parent_2 and not parent_2.dead and not parent_2.exiled and not parent_2.outside:
				queens.append(parent_2)
		elif not parent_1.dead and not parent_1.dead and not parent_1.exiled and not parent_1.outside:
			queens.append(parent_1)
	return queens

def get_med_cats(Cat, working=True):
    """
    returns a list of all meds and med apps currently alive, in the clan, and able to work

    set working to False if you want all meds and med apps regardless of their work status
    """
    all_cats = Cat.all_cats.values()

    if working is False:
        medicine_apprentices = list(filter(
            lambda c: c.status == 'medicine cat apprentice' and not c.dead and not c.outside
            , all_cats
        ))
        medicine_cats = list(filter(
            lambda c: c.status == 'medicine cat' and not c.dead and not c.outside
            , all_cats
        ))
    else:
        medicine_apprentices = list(filter(
            lambda c: c.status == 'medicine cat apprentice' and not c.dead and not c.outside and not c.not_working()
            , all_cats
        ))
        medicine_cats = list(filter(
            lambda c: c.status == 'medicine cat' and not c.dead and not c.outside and not c.not_working()
            , all_cats
        ))

    possible_med_cats = []
    possible_med_cats.extend(medicine_cats)
    possible_med_cats.extend(medicine_apprentices)

    return possible_med_cats


def get_living_cat_count(Cat):
    count = 0
    for the_cat in Cat.all_cats.values():
        if the_cat.dead or the_cat.exiled:
            continue
        count += 1
    return count


def change_clan_reputation(difference=0):
    """
    will change the clan's reputation with outsider cats according to the difference parameter.
    """
    # grab rep
    reputation = game.clan.reputation
    # ensure this is an int value
    difference = int(difference)
    # change rep
    reputation += difference
    game.clan.reputation = reputation


def change_clan_relations(other_clan, difference=0):
    """
    will change the clan's relation with other clans according to the difference parameter.
    """
    # grab the clan that has been indicated
    other_clan = other_clan
    # grab the relation value for that clan
    y = game.clan.all_clans.index(other_clan)
    clan_relations = int(game.clan.all_clans[y].relations)
    # change the value
    clan_relations += difference
    game.clan.all_clans[y].relations = clan_relations

# ---------------------------------------------------------------------------- #
#                       Relationship / Traits / Relative                       #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/"
PERSONALITY_COMPATIBILITY = None
with open(f"{resource_directory}personality_compatibility.json", 'r') as read_file:
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
        if cat.ID in inter_cat.relationships:
            relation = inter_cat.relationships[cat.ID]
        else:
            continue

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


def add_siblings_to_cat(cat, cat_class, orphan=False):
    """Iterate over all current cats and add the ID to the current cat."""
    orphan = orphan
    if orphan:
        for inter_cat in cat_class.all_cats.values():
            cat.siblings.append(inter_cat.ID)
            inter_cat.siblings.append(cat.ID)
    else:
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


def change_relationship_values(cats_to,
                               cats_from,
                               romantic_love=0,
                               platonic_like=0,
                               dislike=0,
                               admiration=0,
                               comfortable=0,
                               jealousy=0,
                               trust=0,
                               auto_romance=False
                               ):
    """
    changes relationship values according to the parameters.

    cats_from - a list of cats for the cats whose rel values are being affected
    cats_to - a list of cat IDs for the cats who are the target of that rel value
            i.e. cats in cats_from lose respect towards the cats in cats_to
    auto_romance - if this is set to False (which is the default) then if the cat_from already has romantic value
            with cat_to then the platonic_like param value will also be used for the romantic_love param
            if you don't want this to happen, then set auto_romance to False

    use the relationship value params to indicate how much the values should change.
    """
    # this is just for prints, if it's still here later, just remove it
    changed = False
    if romantic_love == 0 and platonic_like == 0 and dislike == 0 and admiration == 0 and \
            comfortable == 0 and jealousy == 0 and trust == 0:
        changed = False
    else:
        changed = True

    # pick out the correct cats
    for cat in cats_from:
        relationships = list(filter(lambda rel: rel.cat_to.ID in cats_to,
                                    list(cat.relationships.values())))

        # make sure that cats don't gain rel with themselves
        for rel in relationships:
            if cat.ID == rel.cat_to.ID:
                continue

            # if cat already has romantic feelings then automatically increase romantic feelings
            # when platonic feelings would increase
            if rel.romantic_love > 0 and auto_romance:
                romantic_love = platonic_like

            # now gain the values
            rel.romantic_love += romantic_love
            rel.platonic_like += platonic_like
            rel.dislike += dislike
            rel.admiration += admiration
            rel.comfortable += comfortable
            rel.jealousy += jealousy
            rel.trust += trust

            # for testing purposes
            """print(str(cat.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                  "Romantic: " + str(romantic_love) +
                  " /Platonic: " + str(platonic_like) +
                  " /Dislike: " + str(dislike) +
                  " /Respect: " + str(admiration) +
                  " /Comfort: " + str(comfortable) +
                  " /Jealousy: " + str(jealousy) +
                  " /Trust: " + str(trust)) if changed else print("No relationship change")"""


# ---------------------------------------------------------------------------- #
#                               Text Adjust                                    #
# ---------------------------------------------------------------------------- #

def event_text_adjust(Cat, text, cat, other_cat=None, other_clan_name=None, keep_m_c=False):
    danger = ["a rogue", "a dog", "a fox", "an otter", "a rat", "a hawk", "an enemy warrior", "a badger"]
    tail_danger = ["a rogue", "a dog", "a fox", "an otter", "a rat", "a hawk",
                   "an enemy warrior", "a badger", "a Twoleg trap"]

    danger_choice = choice(danger)
    tail_choice = choice(tail_danger)

    name = str(cat.name)
    other_name = None
    if other_cat is not None:
        other_name = str(other_cat.name)
    mate = None
    if cat.mate is not None:
        mate = Cat.all_cats.get(cat.mate).name

    adjust_text = text
    if keep_m_c is False:
        adjust_text = adjust_text.replace("m_c", str(name).strip())
    if other_name is not None:
        adjust_text = adjust_text.replace("r_c", str(other_name))
    if other_clan_name is not None:
        adjust_text = adjust_text.replace("o_c", str(other_clan_name))
    if mate is not None:
        adjust_text = adjust_text.replace("c_m", str(mate))
    adjust_text = adjust_text.replace("d_l", danger_choice)
    adjust_text = adjust_text.replace("t_l", tail_choice)
    adjust_text = adjust_text.replace("c_n", str(game.clan.name) + "Clan")
    adjust_text = adjust_text.replace("p_l", name)

    return adjust_text


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
    # First, check if the cat is faded.
    if cat.faded:
        # Don't update the sprite if the cat is faded.
        return

    # First make pelt, if it wasn't possible before
    if cat.pelt is None:
        if cat.parent1 is None:
            # If pelt has not been picked manually, this function chooses one based on possible inheritances
            cat.pelt = choose_pelt()
        elif cat.parent2 is None and cat.parent1 in cat.all_cats.keys():
            # 1 in 3 chance to inherit a single parent's pelt
            par1 = cat.all_cats[cat.parent1]
            cat.pelt = choose_pelt(choice([par1.pelt.colour, None]), choice([par1.pelt.white, None]),
                                   choice([par1.pelt.name, None]),
                                   choice([par1.pelt.length, None]))
        if cat.parent1 in cat.all_cats.keys() and cat.parent2 in cat.all_cats.keys():
            # 2 in 3 chance to inherit either parent's pelt
            par1 = cat.all_cats[cat.parent1]
            par2 = cat.all_cats[cat.parent2]
            cat.pelt = choose_pelt(choice([par1.pelt.colour, par2.pelt.colour, None]),
                                   choice([par1.pelt.white, par2.pelt.white, None]),
                                   choice([par1.pelt.name, par2.pelt.name, None]),
                                   choice([par1.pelt.length, par2.pelt.length, None]))
        else:
            cat.pelt = choose_pelt()

            # THE SPRITE UPDATE
    # draw colour & style
    new_sprite = pygame.Surface((sprites.size, sprites.size), pygame.HWSURFACE | pygame.SRCALPHA)

    try:
        if cat.pelt.name not in ['Tortie', 'Calico']:
            if cat.pelt.length == 'long' and cat.status not in ['kitten', 'apprentice',
                                                                'medicine cat apprentice', "mediator apprentice"] \
                    or cat.age == 'elder':
                new_sprite.blit(
                    sprites.sprites[cat.pelt.sprites[1] + 'extra' + cat.pelt.colour + str(cat.age_sprites[cat.age])],
                    (0, 0))
            else:
                new_sprite.blit(sprites.sprites[cat.pelt.sprites[1] + cat.pelt.colour + str(cat.age_sprites[cat.age])],
                                (0, 0))
        else:
            if cat.pelt.length == 'long' and cat.status not in ['kitten', 'apprentice',
                                                                'medicine cat apprentice', "mediator apprentice"] \
                    or cat.age == 'elder':
                new_sprite.blit(
                    sprites.sprites[cat.tortiebase + 'extra' + cat.tortiecolour + str(cat.age_sprites[cat.age])], (0, 0))
                new_sprite.blit(sprites.sprites[cat.tortiepattern + 'extra' + cat.pattern + str(cat.age_sprites[cat.age])],
                                (0, 0))
            else:
                new_sprite.blit(sprites.sprites[cat.tortiebase + cat.tortiecolour + str(cat.age_sprites[cat.age])], (0, 0))
                new_sprite.blit(sprites.sprites[cat.tortiepattern + cat.pattern + str(cat.age_sprites[cat.age])], (0, 0))

        # TINTS
        if cat.tint != "none" and cat.tint in Sprites.cat_tints["tint_colours"]:
            # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
            # entire surface. To get around this, we first blit the tint onto a white background to dull it,
            # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
            base = pygame.Surface((50, 50)).convert_alpha()
            base.fill((255, 255, 255))
            tint = pygame.Surface((50, 50)).convert_alpha()
            tint.fill(tuple(Sprites.cat_tints["tint_colours"][cat.tint]))
            base.blit(tint, (0, 0))
            new_sprite.blit(base, (0, 0), special_flags=pygame.BLEND_RGB_MULT)



        # draw white patches
        if cat.white_patches is not None:
            if cat.pelt.length == 'long' and cat.status not in ['kitten', 'apprentice', 'medicine cat apprentice',
                                                                "mediator apprentice"] \
                    or cat.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['whiteextra' + cat.white_patches +
                                    str(cat.age_sprites[cat.age])], (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['white' + cat.white_patches +
                                    str(cat.age_sprites[cat.age])], (0, 0))
        # draw eyes & scars1
        if cat.pelt.length == 'long' and cat.status not in [
            'kitten', 'apprentice', 'medicine cat apprentice', "mediator apprentice"
        ] or cat.age == 'elder':
            new_sprite.blit(
                sprites.sprites['eyesextra' + cat.eye_colour +
                                str(cat.age_sprites[cat.age])], (0, 0))
            if cat.eye_colour2 != None:
                new_sprite.blit(
                sprites.sprites['eyes2extra' + cat.eye_colour2 +
                                str(cat.age_sprites[cat.age])], (0, 0))
            for scar in cat.scars:
                if scar in scars1:
                    new_sprite.blit(
                        sprites.sprites['scarsextra' + scar + str(cat.age_sprites[cat.age])],
                        (0, 0)
                    )
                if scar in scars3:
                    new_sprite.blit(
                        sprites.sprites['scarsextra' + scar + str(cat.age_sprites[cat.age])],
                        (0, 0)
                    )
            
        else:
            new_sprite.blit(
                sprites.sprites['eyes' + cat.eye_colour +
                                str(cat.age_sprites[cat.age])], (0, 0))
            if cat.eye_colour2 != None:
                new_sprite.blit(
                sprites.sprites['eyes2' + cat.eye_colour2 +
                                str(cat.age_sprites[cat.age])], (0, 0))
            for scar in cat.scars:
                if scar in scars1:
                    new_sprite.blit(
                        sprites.sprites['scars' + scar + str(cat.age_sprites[cat.age])],
                        (0, 0)
                    )
                if scar in scars3:
                    new_sprite.blit(
                        sprites.sprites['scars' + scar + str(cat.age_sprites[cat.age])],
                        (0, 0)
                    )
            

        # draw line art
        if game.settings['shaders'] and not cat.dead:
            if cat.pelt.length == 'long' and cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice', "mediator apprentice"
            ] or cat.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['shaders' +
                                    str(cat.age_sprites[cat.age] + 9)],
                    (0, 0),
                    special_flags=pygame.BLEND_RGB_MULT)
                new_sprite.blit(
                    sprites.sprites['lighting' +
                                    str(cat.age_sprites[cat.age] + 9)],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['shaders' +
                                    str(cat.age_sprites[cat.age])], (0, 0),
                    special_flags=pygame.BLEND_RGB_MULT)
                new_sprite.blit(
                    sprites.sprites['lighting' +
                                    str(cat.age_sprites[cat.age])],
                    (0, 0))


        if not cat.dead:
            if cat.pelt.length == 'long' and cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice', "mediator apprentice"
            ] or cat.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['lines' +
                                    str(cat.age_sprites[cat.age] + 9)],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['lines' + str(cat.age_sprites[cat.age])],
                    (0, 0))
        elif cat.df:
            if cat.pelt.length == 'long' and cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice', "mediator apprentice"
            ] or cat.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['lineartdf' +
                                    str(cat.age_sprites[cat.age] + 9)],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['lineartdf' +
                                    str(cat.age_sprites[cat.age])], (0, 0))
        elif cat.dead:
            if cat.pelt.length == 'long' and cat.status not in [
                'kitten', 'apprentice', 'medicine cat apprentice', "mediator apprentice"
            ] or cat.age == 'elder':
                new_sprite.blit(
                    sprites.sprites['lineartdead' +
                                    str(cat.age_sprites[cat.age] + 9)],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['lineartdead' +
                                    str(cat.age_sprites[cat.age])], (0, 0))
        # draw skin and scars2
        blendmode = pygame.BLEND_RGBA_MIN
        if cat.pelt.length == 'long' and cat.status not in [
            'kitten', 'apprentice', 'medicine cat apprentice', "mediator apprentice"
        ] or cat.age == 'elder':
            new_sprite.blit(
                sprites.sprites['skinextra' + cat.skin +
                                str(cat.age_sprites[cat.age])], (0, 0))
            for scar in cat.scars:
                if scar in scars2:
                    new_sprite.blit(sprites.sprites['scarsextra' + scar +
                                                    str(cat.age_sprites[cat.age])], (0, 0), special_flags=blendmode)

        else:
            new_sprite.blit(
                sprites.sprites['skin' + cat.skin +
                                str(cat.age_sprites[cat.age])], (0, 0))
            for scar in cat.scars:
                if scar in scars2:
                    new_sprite.blit(sprites.sprites['scars' + scar +
                                                    str(cat.age_sprites[cat.age])], (0, 0), special_flags=blendmode)

        # draw accessories        
        if cat.pelt.length == 'long' and cat.status not in [
            'kitten', 'apprentice', 'medicine cat apprentice', "mediator apprentice"
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
    except (TypeError, KeyError):
        print(f"ERROR: Failed to load cat ID #{cat}'s sprite:\n", traceback.format_exc())

        # Placeholder image
        new_sprite.blit(
            image_cache.load_image(f"sprites/faded/faded_adult.png").convert_alpha(),
            (0, 0)
        )

    # reverse, if assigned so
    if cat.reverse:
        new_sprite = pygame.transform.flip(new_sprite, True, False)

    # Apply opacity
    if cat.opacity < 100 and not cat.prevent_fading and game.settings["fading"]:
        new_sprite = apply_opacity(new_sprite, cat.opacity)

    # apply
    cat.sprite = new_sprite
    cat.big_sprite = pygame.transform.scale(
        new_sprite, (sprites.new_size, sprites.new_size))
    cat.large_sprite = pygame.transform.scale(
        cat.big_sprite, (sprites.size * 3, sprites.size * 3))
    # update class dictionary
    cat.all_cats[cat.ID] = cat


def apply_opacity(surface, opacity):
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            pixel = list(surface.get_at((x, y)))
            pixel[3] = int(pixel[3] * opacity/100)
            surface.set_at((x,y), tuple(pixel))
    return surface
# ---------------------------------------------------------------------------- #
#                                     OTHER                                    #
# ---------------------------------------------------------------------------- #

def is_iterable(y):
    try:
        0 in y
    except TypeError:
        return False


def get_text_box_theme(themename=""):
    """Updates the name of the theme based on dark or light mode"""
    if game.settings['dark mode']:
        if themename == "":
            return "#default_dark"
        else:
            return themename + "_dark"
    else:
        if themename == "":
            return "text_box"
        else:
            return themename





