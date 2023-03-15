# pylint: disable=line-too-long
"""

TODO: Docs


"""  # pylint: enable=line-too-long

from random import choice, choices, randint, random, sample
import pygame
from scripts.cat.names import names

try:
    import ujson
except ImportError:
    import json as ujson
import logging


logger = logging.getLogger(__name__)
from scripts.game_structure import image_cache

from sys import exit as sys_exit

from scripts.cat.sprites import sprites, Sprites
from scripts.cat.pelts import (
    choose_pelt,
    scars1,
    scars2,
    scars3,
    plant_accessories,
    wild_accessories,
    collars,
    wing_sprites,)
from scripts.game_structure.game_essentials import game, screen_x, screen_y

# ---------------------------------------------------------------------------- #
#                              Counting Cats                                   #
# ---------------------------------------------------------------------------- #

def get_alive_clan_queens(all_cats):
    """
    Returns a list with all cats with the 'status' queen.
    """
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
            if (parent_2 is None or parent_2.gender == 'male') and \
                    not parent_1.dead and not parent_1.exiled and not parent_1.outside:
                queens.append(parent_1)
            elif parent_2 and not parent_2.dead and not parent_2.exiled and not parent_2.outside:
                queens.append(parent_2)
        elif not parent_1.dead and not parent_1.dead and not parent_1.exiled and not parent_1.outside:
            queens.append(parent_1)
    return queens


def get_alive_kits(Cat):
    """
    returns a list of all living kittens in the clan
    """
    alive_kits = list(filter(
        lambda kitty: (kitty.age == "kitten"
                       and not kitty.dead
                       and not kitty.outside),
        Cat.all_cats.values()
    ))
    return alive_kits


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
    """
    TODO: DOCS
    """
    count = 0
    for the_cat in Cat.all_cats.values():
        if the_cat.dead or the_cat.exiled:
            continue
        count += 1
    return count


def get_living_clan_cat_count(Cat):
    """
    TODO: DOCS
    """
    count = 0
    for the_cat in Cat.all_cats.values():
        if the_cat.dead or the_cat.exiled or the_cat.outside:
            continue
        count += 1
    return count

def get_cats_same_age(cat, range=10):  # pylint: disable=redefined-builtin
    """Look for all cats in the clan and returns a list of cats, which are in the same age range as the given cat."""
    cats = []
    for inter_cat in cat.all_cats.values():
        if inter_cat.dead or inter_cat.outside or inter_cat.exiled:
            continue
        if inter_cat.moons <= cat.moons + range and inter_cat.moons <= cat.moons - range:
            cats.append(inter_cat)

    return cats


# ---------------------------------------------------------------------------- #
#                          Handling Outside Factors                            #
# ---------------------------------------------------------------------------- #
def get_current_season():
    """
    function to handle the math for finding the clan's current season
    :return: the clan's current season
    """
    # print(game.clan.current_season)
    modifiers = {
        "Newleaf": 0,
        "Greenleaf": 3,
        "Leaf-fall": 6,
        "Leaf-bare": 9
    }
    index = game.clan.age % 12 + modifiers[game.clan.starting_season]
    # print(index)
    if index > 11:
        index = index - 12
    # print(index)
    game.clan.current_season = game.clan.seasons[index]
    # print(game.clan.current_season)

    return game.clan.current_season


def change_clan_reputation(difference=0):
    """
    will change the clan's reputation with outsider cats according to the difference parameter.
    """
    # grab rep
    reputation = int(game.clan.reputation)
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


def create_new_cat(Cat,
                   Relationship,
                   new_name=False,
                   loner=False,
                   kittypet=False,
                   kit=False,
                   litter=False,
                   other_clan=None,
                   backstory=None,
                   status=None,
                   age=None,
                   gender=None,
                   thought='Is looking around the camp with wonder',
                   alive=True,
                   outside=False):
    """
    This function creates new cats and then returns a list of those cats
    :param Cat: pass the Cat class
    :params Relationship: pass the Relationship class
    :param new_name: set True if cat(s) is a loner/rogue receiving a new Clan name - default: False
    :param loner: set True if cat(s) is a loner or rogue - default: False
    :param kittypet: set True if cat(s) is a kittypet - default: False
    :param kit: set True if the cat is a lone kitten - default: False
    :param litter: set True if a litter of kittens needs to be generated - default: False
    :param other_clan: if new cat(s) are from a neighboring clan, pass the name of their home Clan - default: None
    :param backstory: a list of possible backstories for the new cat(s) - default: None
    :param status: set as the rank you want the new cat to have - default: None (will cause a random status to be picked)
    :param age: set the age of the new cat(s) - default: None (will be random or if kit/litter is true, will be kitten.
    :param gender: set the gender (BIRTH SEX) of the cat - default: None (will be random)
    :param thought: if you need to give a custom "welcome" thought, set it here
    :param alive: set this as False to generate the cat as already dead - default: True (alive)
    :param outside: set this as True to generate the cat as an outsider instead of as part of the clan - default: False (clan cat)
    """
    accessory = None
    backstory = choice(backstory)

    created_cats = []

    if not litter:
        number_of_cats = 1
    else:
        number_of_cats = choices([1, 2, 3, 4, 5], [2, 5, 4, 1, 1], k=1)
        number_of_cats = number_of_cats[0]
    # setting age
    if not age:
        if litter or kit:
            age = randint(0, 5)
        elif status == 'apprentice':
            age = randint(6, 11)
        elif status == 'warrior':
            age = randint(23, 120)
        elif status == 'medicine cat':
            age = randint(23, 140)
        else:
            age = randint(6, 120)
    else:
        age = age
    # setting status
    if not status:
        if age < 6:
            status = "kitten"
        elif 6 <= age <= 11:
            status = "apprentice"
        elif age >= 12:
            status = "warrior"

    # cat creation and naming time
    for index in range(number_of_cats):

        # setting gender
        if not gender:
            gender = choice(['female', 'male'])

        # other clan cats and kittens (kittens get indoctrinated lmao no old names for them)
        if other_clan or kit or litter:
            new_cat = Cat(moons=age,
                          status=status,
                          gender=gender,
                          backstory=backstory)
        else:
            # grab starting names and accs for loners/kittypets
            if kittypet:
                name = choice(names.names_dict["loner_names"])
                if choice([1, 2]) == 1:
                    accessory = choice(collars)
            elif loner and choice([1, 2]) == 1:  # try to give name from full loner name list
                name = choice(names.names_dict["loner_names"])
            else:
                name = choice(
                    names.names_dict["normal_prefixes"])  # otherwise give name from prefix list (more nature-y names)

            # now we make the cats
            if new_name:  # these cats get new names
                if choice([1, 2]) == 1:  # adding suffix to OG name
                    spaces = name.count(" ")
                    if spaces > 0:
                        # make a list of the words within the name, then add the OG name back in the list
                        words = name.split(" ")
                        words.append(name)
                        new_prefix = choice(words)  # pick new prefix from that list
                        name = new_prefix
                    new_cat = Cat(moons=age,
                                  prefix=name,
                                  status=status,
                                  gender=gender,
                                  backstory=backstory)
                else:  # completely new name
                    new_cat = Cat(moons=age,
                                  status=status,
                                  gender=gender,
                                  backstory=backstory)
            # these cats keep their old names
            else:
                new_cat = Cat(moons=age,
                              prefix=name,
                              suffix="",
                              status=status,
                              gender=gender,
                              backstory=backstory)

        # give em a collar if they got one
        if accessory:
            new_cat.accessory = accessory

        # newbie thought
        new_cat.thought = thought

        # give apprentice aged cat a mentor
        if new_cat.age == 'adolescent':
            new_cat.update_mentor()

        # Remove disabling scars, if they generated.
        not_allowed = ['NOPAW', 'NOTAIL', 'HALFTAIL', 'NOEAR', 'BOTHBLIND', 'RIGHTBLIND', 'LEFTBLIND',
                       'BRIGHTHEART', 'NOLEFTEAR', 'NORIGHTEAR', 'MANLEG']
        for scar in new_cat.scars:
            if scar in not_allowed:
                new_cat.scars.remove(scar)

        # chance to give the new cat a permanent condition, higher chance for found kits and litters
        if game.clan.game_mode != 'classic':
            if kit or litter:
                chance = int(game.config["cat_generation"]["base_permanent_condition"] / 11.25)
            else:
                chance = game.config["cat_generation"]["base_permanent_condition"] + 10
            if not int(random() * chance):
                possible_conditions = []
                for condition in PERMANENT:
                    possible_conditions.append(condition)
                chosen_condition = choice(possible_conditions)
                born_with = False
                if PERMANENT[chosen_condition]['congenital'] in ['always', 'sometimes']:
                    born_with = True

                new_cat.get_permanent_condition(chosen_condition, born_with)

                # assign scars
                if chosen_condition in ['lost a leg', 'born without a leg']:
                    new_cat.scars.append('NOPAW')
                elif chosen_condition in ['lost their tail', 'born without a tail']:
                    new_cat.scars.append("NOTAIL")

        if outside:
            new_cat.outside = True
        if not alive:
            new_cat.dead = True

        # and they exist now
        created_cats.append(new_cat)
        game.clan.add_cat(new_cat)

        # create relationship class
        for inter_cat in Cat.all_cats.values():
            if inter_cat.ID == new_cat.ID:
                continue
            inter_cat.relationships[new_cat.ID] = Relationship(inter_cat, new_cat)
            new_cat.relationships[inter_cat.ID] = Relationship(new_cat, inter_cat)

    return created_cats


# ---------------------------------------------------------------------------- #
#                             Cat Relationships                                #
# ---------------------------------------------------------------------------- #

resource_directory = "resources/dicts/"
PERSONALITY_COMPATIBILITY = None
with open(f"{resource_directory}personality_compatibility.json", 'r') as read_file:
    PERSONALITY_COMPATIBILITY = ujson.loads(read_file.read())


def get_highest_romantic_relation(relationships, exclude_mate=False, potential_mate=False):
    """Returns the relationship with the highest romantic value."""
    # Different filters for different
    romantic_relation = list(
        filter(lambda rel: rel.romantic_love > 0 and (exclude_mate and rel.cat_to.ID != rel.cat_to.mate)
                           and (potential_mate and rel.cat_to.is_potential_mate(rel.cat_from, for_love_interest=True)),
               relationships))

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


def check_relationship_value(cat_from, cat_to, rel_value=None):
    """
    returns the value of the rel_value param given
    :param cat_from: the cat who is having the feelings
    :param cat_to: the cat that the feelings are directed towards
    :param rel_value: the relationship value that you're looking for,
    options are: romantic, platonic, dislike, admiration, comfortable, jealousy, trust
    """
    if cat_to.ID in cat_from.relationships:
        relationship = cat_from.relationships[cat_to.ID]
    else:
        relationship = cat_from.create_one_relationship(cat_to)

    if rel_value == "romantic":
        return relationship.romantic_love
    elif rel_value == "platonic":
        return relationship.platonic_like
    elif rel_value == "dislike":
        return relationship.dislike
    elif rel_value == "admiration":
        return relationship.admiration
    elif rel_value == "comfortable":
        return relationship.comfortable
    elif rel_value == "jealousy":
        return relationship.jealousy
    elif rel_value == "trust":
        return relationship.trust


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
        if cat.is_parent(inter_cat) and inter_cat.ID not in cat.children:
            cat.children.append(inter_cat.ID)
        if inter_cat.is_parent(cat) and cat.ID not in inter_cat.children:
            inter_cat.children.append(cat.ID)
    print('cats children', cat.children)


def change_relationship_values(cats_to: list,
                               cats_from: list,
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
    '''# this is just for test prints - DON'T DELETE - you can use this to test if relationships are changing
    changed = False
    if romantic_love == 0 and platonic_like == 0 and dislike == 0 and admiration == 0 and \
            comfortable == 0 and jealousy == 0 and trust == 0:
        changed = False
    else:
        changed = True'''

    # pick out the correct cats
    for kitty in cats_from:
        relationships = list(filter(lambda rel: rel.cat_to.ID in cats_to,
                                    list(kitty.relationships.values())))

        # make sure that cats don't gain rel with themselves
        for rel in relationships:
            if kitty.ID == rel.cat_to.ID:
                continue

            # here we just double-check that the cats are allowed to be romantic with eath other
            if kitty.is_potential_mate(rel.cat_to, for_love_interest=True) or kitty.mate == rel.cat_to.ID:
                # if cat already has romantic feelings then automatically increase romantic feelings
                # when platonic feelings would increase
                if rel.romantic_love > 0 and auto_romance:
                    romantic_love = platonic_like

                # now gain the romance
                rel.romantic_love += romantic_love

            # gain other rel values
            rel.platonic_like += platonic_like
            rel.dislike += dislike
            rel.admiration += admiration
            rel.comfortable += comfortable
            rel.jealousy += jealousy
            rel.trust += trust

            '''# for testing purposes - DON'T DELETE - you can use this to test if relationships are changing
            print(str(kitty.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                  "Romantic: " + str(romantic_love) +
                  " /Platonic: " + str(platonic_like) +
                  " /Dislike: " + str(dislike) +
                  " /Respect: " + str(admiration) +
                  " /Comfort: " + str(comfortable) +
                  " /Jealousy: " + str(jealousy) +
                  " /Trust: " + str(trust)) if changed else print("No relationship change")'''


# ---------------------------------------------------------------------------- #
#                               Text Adjust                                    #
# ---------------------------------------------------------------------------- #

def get_snippet_list(chosen_list, amount, sense_groups=None, return_string=True):
    """
    function to grab items from various lists in snippet_collections.json
    list options are:
    -prophecy_list - sense_groups = sight, sound, smell, emotional, touch
    -omen_list - sense_groups = sight, sound, smell, emotional, touch
    -clair_list  - sense_groups = sound, smell, emotional, touch, taste
    -dream_list (this list doesn't have sense_groups)
    -story_list (this list doesn't have sense_groups)
    :param chosen_list: pick which list you want to grab from
    :param amount: the amount of items you want the returned list to contain
    :param sense_groups: list which senses you want the snippets to correspond with:
     "touch", "sight", "emotional", "sound", "smell" are the options. Default is None, if left as this then all senses
     will be included (if the list doesn't have sense categories, then leave as None)
    :param return_string: if True then the function will format the snippet list with appropriate commas and 'ands'.
    This will work with any number of items. If set to True, then the function will return a string instead of a list.
    (i.e. ["hate", "fear", "dread"] becomes "hate, fear, and dread") - Default is True
    :return: a list of the chosen items from chosen_list or a formatted string if format is True
    """
    biome = game.clan.biome.casefold()

    # these lists don't get sense specific snippets, so is handled first
    if chosen_list in ["dream_list", "story_list"]:

        if chosen_list == 'story_list':  # story list has some biome specific things to collect
            snippets = SNIPPETS[chosen_list]['general']
            snippets.extend(SNIPPETS[chosen_list][biome])
        elif chosen_list == 'clair_list':  # the clair list also pulls from the dream list
            snippets = SNIPPETS[chosen_list]
            snippets.extend(SNIPPETS["dream_list"])
        else:  # the dream list just gets the one
            snippets = SNIPPETS[chosen_list]

    else:
        # if no sense groups were specified, use all of them
        if not sense_groups:
            if chosen_list == 'clair_list':
                sense_groups = ["taste", "sound", "smell", "emotional", "touch"]
            else:
                sense_groups = ["sight", "sound", "smell", "emotional", "touch"]

        # find the correct lists and compile them
        snippets = []
        for sense in sense_groups:
            snippet_group = SNIPPETS[chosen_list][sense]
            snippets.extend(snippet_group["general"])
            snippets.extend(snippet_group[biome])

    # now choose a unique snippet from each snip list
    unique_snippets = []
    for snip_list in snippets:
        unique_snippets.append(choice(snip_list))

    # pick out our final snippets
    final_snippets = sample(unique_snippets, k=amount)

    if return_string:
        if amount == 1:
            text = str(final_snippets[0])
        elif amount == 2:
            text = " and ".join(final_snippets)
        else:
            start = ", ".join(final_snippets[:-1])
            text = ", and ".join([start, final_snippets[-1]])
        return text
    else:
        return final_snippets


def event_text_adjust(Cat,
                      text,
                      cat,
                      other_cat=None,
                      other_clan_name=None,
                      keep_m_c=False,
                      new_cat=None,
                      clan=None):
    """
    This function takes the given text and returns it with the abbreviations replaced appropriately
    :param Cat: Always give the Cat class
    :param text: The text that needs to be changed
    :param cat: The cat taking the place of m_c
    :param other_cat: The cat taking the place of r_c
    :param other_clan_name: The other clan involved in the event
    :param keep_m_c: set True if you don't want m_c to be replaced with the name - this is only currently important for history text
    :param new_cat: The cat taking the place of n_c
    :param clan: The player's Clan
    :return: the adjusted text
    """

    name = str(cat.name)
    other_name = None
    if other_cat:
        other_name = str(other_cat.name)

    adjust_text = text
    if keep_m_c is False:
        adjust_text = adjust_text.replace("m_c", str(name).strip())
    if other_name:
        adjust_text = adjust_text.replace("r_c", str(other_name))
    if other_clan_name:
        adjust_text = adjust_text.replace("o_c", str(other_clan_name))
    if new_cat:
        adjust_text = adjust_text.replace("n_c_pre", str(new_cat.name.prefix))
        adjust_text = adjust_text.replace("n_c", str(new_cat.name))
    if "acc_plural" in adjust_text:
        adjust_text = adjust_text.replace("acc_plural", str(ACC_DISPLAY[cat.accessory]["plural"]))
    if "acc_singular" in adjust_text:
        adjust_text = adjust_text.replace("acc_singular", str(ACC_DISPLAY[cat.accessory]["singular"]))

    if "omen_list" in adjust_text:
        chosen_omens = get_snippet_list("omen_list", randint(2, 4), sense_groups=["sight"])
        adjust_text = adjust_text.replace("omen_list", chosen_omens)
    if "prophecy_list" in adjust_text:
        chosen_prophecy = get_snippet_list("prophecy_list", randint(2, 4), sense_groups=["sight", "emotional", "touch"])
        adjust_text = adjust_text.replace("prophecy_list", chosen_prophecy)
    if "dream_list" in adjust_text:
        chosen_dream = get_snippet_list("dream_list", randint(2, 4))
        adjust_text = adjust_text.replace("dream_list", chosen_dream)
    if "clair_list" in adjust_text:
        chosen_clair = get_snippet_list("clair_list", randint(2, 4))
        adjust_text = adjust_text.replace("clair_list", chosen_clair)
    if "story_list" in adjust_text:
        chosen_story = get_snippet_list("story_list", randint(1, 2))
        adjust_text = adjust_text.replace("story_list", chosen_story)

    if clan:
        _tmp = clan
    else:
        _tmp = game.clan
    adjust_text = adjust_text.replace("c_n", str(_tmp.name) + "Clan")
    adjust_text = adjust_text.replace("p_l", name)

    return adjust_text


def ceremony_text_adjust(Cat, text, cat, dead_mentor=None, mentor=None, previous_alive_mentor=None, random_honor=None,
                         living_parents=(), dead_parents=()):
    name = str(cat.name)
    prefix = str(cat.name.prefix)
    clanname = str(game.clan.name + "Clan")

    if mentor:
        mentor_name = str(mentor.name)
    else:
        mentor_name = "mentor_placeholder"

    if dead_mentor:
        dead_mentor_name = str(dead_mentor.name)
    else:
        dead_mentor_name = "dead_mentor_placeholder"

    if previous_alive_mentor:
        previous_alive_mentor_name = str(previous_alive_mentor.name)
    else:
        previous_alive_mentor_name = "previous_mentor_name"

    if game.clan.leader:
        leader_name = str(game.clan.leader.name)
    else:
        leader_name = "leader_placeholder"

    if living_parents:
        random_living_parent = choice(living_parents)
    else:
        random_living_parent = None

    if dead_parents:
        random_dead_parent = choice(dead_parents)
    else:
        random_dead_parent = None

    random_honor = random_honor

    adjust_text = text
    adjust_text = adjust_text.replace("(prefix)", prefix)
    adjust_text = adjust_text.replace("m_c", name)
    adjust_text = adjust_text.replace("c_n", clanname)
    if mentor_name:
        adjust_text = adjust_text.replace("(mentor)", mentor_name)
    adjust_text = adjust_text.replace("l_n", leader_name)
    adjust_text = adjust_text.replace("(deadmentor)", dead_mentor_name)
    adjust_text = adjust_text.replace("(previous_mentor)", previous_alive_mentor_name)

    # Living Parents
    if "p1" in adjust_text and "p2" in adjust_text and len(living_parents) >= 2:
        adjust_text = adjust_text.replace("p1", str(living_parents[0].name))
        adjust_text = adjust_text.replace("p2", str(living_parents[1].name))
    elif "p1" in adjust_text and random_living_parent:
        adjust_text = adjust_text.replace("p1", str(random_living_parent.name))
    elif "p2" in adjust_text and random_living_parent:
        adjust_text = adjust_text.replace("p2", str(random_living_parent.name))

    # Dead Parents
    if "dead_par1" in adjust_text and "dead_par2" in adjust_text and len(dead_parents) >= 2:
        adjust_text = adjust_text.replace("dead_par1", str(dead_parents[0].name))
        adjust_text = adjust_text.replace("dead_par2", str(dead_parents[1].name))
    elif "dead_par1" in adjust_text and random_dead_parent:
        adjust_text = adjust_text.replace("dead_par1", str(random_dead_parent.name))
    elif "dead_par2" in adjust_text and random_living_parent:
        adjust_text = adjust_text.replace("dead_par2", str(random_dead_parent.name))

    if random_honor:
        adjust_text = adjust_text.replace("r_h", random_honor)

    return adjust_text, random_living_parent, random_dead_parent


# ---------------------------------------------------------------------------- #
#                                    Sprites                                   #
# ---------------------------------------------------------------------------- #

def scale(rect):
    rect[0] = round(rect[0] / 1600 * screen_x) if rect[0] > 0 else rect[0]
    rect[1] = round(rect[1] / 1400 * screen_y) if rect[1] > 0 else rect[1]
    rect[2] = round(rect[2] / 1600 * screen_x) if rect[2] > 0 else rect[2]
    rect[3] = round(rect[3] / 1400 * screen_y) if rect[3] > 0 else rect[3]

    return rect


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
            if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                new_sprite.blit(
                    sprites.sprites[cat.pelt.sprites[1] + 'extra' + cat.pelt.colour + str(cat.age_sprites[cat.age])],
                    (0, 0))
            else:
                new_sprite.blit(sprites.sprites[cat.pelt.sprites[1] + cat.pelt.colour + str(cat.age_sprites[cat.age])],
                                (0, 0))
        else:
            if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                # Base Coat
                new_sprite.blit(
                    sprites.sprites[cat.tortiebase + 'extra' + cat.pelt.colour + str(cat.age_sprites[cat.age])],
                    (0, 0))

                # Create the patch image
                patches = sprites.sprites[
                    cat.tortiepattern + 'extra' + cat.tortiecolour + str(cat.age_sprites[cat.age])].copy()
                patches.blit(sprites.sprites["tortiemask" + cat.pattern + str(cat.age_sprites[cat.age] + 9)],
                             (0, 0),
                             special_flags=pygame.BLEND_RGBA_MULT
                             )

                # Add patches onto cat.
                new_sprite.blit(patches, (0, 0))
            else:
                # Base Coat
                new_sprite.blit(
                    sprites.sprites[cat.tortiebase + cat.pelt.colour + str(cat.age_sprites[cat.age])],
                    (0, 0))

                # Create the patch image
                if cat.tortiepattern == "Single":
                    tortie_pattern = "SingleColour"
                else:
                    tortie_pattern = cat.tortiepattern

                patches = sprites.sprites[
                    tortie_pattern + cat.tortiecolour + str(cat.age_sprites[cat.age])].copy()
                patches.blit(sprites.sprites["tortiemask" + cat.pattern + str(cat.age_sprites[cat.age])], (0, 0),
                             special_flags=pygame.BLEND_RGBA_MULT)

                # Add patches onto cat.
                new_sprite.blit(patches, (0, 0))

        # TINTS
        if cat.tint != "none" and cat.tint in Sprites.cat_tints["tint_colours"]:
            # Multiply with alpha does not work as you would expect - it just lowers the alpha of the
            # entire surface. To get around this, we first blit the tint onto a white background to dull it,
            # then blit the surface onto the sprite with pygame.BLEND_RGB_MULT
            tint = pygame.Surface((50, 50)).convert_alpha()
            tint.fill(tuple(Sprites.cat_tints["tint_colours"][cat.tint]))
            new_sprite.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        # draw white patches
        if cat.white_patches is not None:
            if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                white_patches = sprites.sprites['whiteextra' + cat.white_patches + str(cat.age_sprites[cat.age])].copy()
            else:
                white_patches = sprites.sprites['white' + cat.white_patches + str(cat.age_sprites[cat.age])].copy()

            # Apply tint to white patches.
            if cat.white_patches_tint != "none" and cat.white_patches_tint in Sprites.white_patches_tints[
                "tint_colours"]:
                tint = pygame.Surface((50, 50)).convert_alpha()
                tint.fill(tuple(Sprites.white_patches_tints["tint_colours"][cat.white_patches_tint]))
                white_patches.blit(tint, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            new_sprite.blit(white_patches, (0, 0))

        # draw eyes & scars1
        if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
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
            if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
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
            if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                new_sprite.blit(
                    sprites.sprites['lines' +
                                    str(cat.age_sprites[cat.age] + 9)],
                    (0, 0))
            else:
                new_sprite.blit(
                    sprites.sprites['lines' + str(cat.age_sprites[cat.age])],
                    (0, 0))

        # draw skin and scars2
        blendmode = pygame.BLEND_RGBA_MIN
        if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
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

        #Draw Dead Lineart
        if cat.skin in wing_sprites:
            if cat.df:
                if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                    new_sprite.blit(
                        sprites.sprites['w_lineartdf' +
                                        str(cat.age_sprites[cat.age] + 9)],
                        (0, 0))
                else:
                    new_sprite.blit(
                        sprites.sprites['w_lineartdf' +
                                        str(cat.age_sprites[cat.age])], (0, 0))
            elif cat.dead:
                if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                    new_sprite.blit(
                        sprites.sprites['w_lineartdead' +
                                        str(cat.age_sprites[cat.age] + 9)],
                        (0, 0))
                else:
                    new_sprite.blit(
                        sprites.sprites['w_lineartdead' +
                                        str(cat.age_sprites[cat.age])], (0, 0))        

        else:
            if cat.df:
                if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                    new_sprite.blit(
                        sprites.sprites['lineartdf' +
                                        str(cat.age_sprites[cat.age] + 9)],
                        (0, 0))
                else:
                    new_sprite.blit(
                        sprites.sprites['lineartdf' +
                                        str(cat.age_sprites[cat.age])], (0, 0))
            elif cat.dead:
                if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                    new_sprite.blit(
                        sprites.sprites['lineartdead' +
                                        str(cat.age_sprites[cat.age] + 9)],
                        (0, 0))
                else:
                    new_sprite.blit(
                        sprites.sprites['lineartdead' +
                                        str(cat.age_sprites[cat.age])], (0, 0))        

        # Apply fading fog
        if cat.opacity <= 97 and not cat.prevent_fading and game.settings["fading"]:
            if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
                offset = 9
            else:
                offset = 0

            if 97 >= cat.opacity > 80:
                # Stage 1
                pass
            elif 80 >= cat.opacity > 45:
                # Stage 2
                offset += 15
            elif cat.opacity <= 45:
                # Stage 3
                offset += 30

            new_sprite.blit(sprites.sprites['fademask' + str(cat.age_sprites[cat.age] + offset)], (0, 0),
                            special_flags=pygame.BLEND_RGBA_MULT)

            if cat.df:
                temp = sprites.sprites['fadedf' + str(cat.age_sprites[cat.age] + offset)].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp
            else:
                temp = sprites.sprites['fadestarclan' + str(cat.age_sprites[cat.age] + offset)].copy()
                temp.blit(new_sprite, (0, 0))
                new_sprite = temp

        # draw accessories
        if cat.age == 'elder' or (cat.pelt.length == 'long' and cat.age not in ['kitten', 'adolescent']):
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
        logger.exception("Failed to load sprite")

        # Placeholder image
        new_sprite.blit(
            image_cache.load_image(f"sprites/faded/faded_adult.png").convert_alpha(),
            (0, 0)
        )

    # Opacity currently disabled for performance reasons. Fading Fog is used as placeholder.
    """# Apply opacity
    if cat.opacity < 100 and not cat.prevent_fading and game.settings["fading"]:
        new_sprite = apply_opacity(new_sprite, cat.opacity)"""

    # reverse, if assigned so
    if cat.reverse:
        new_sprite = pygame.transform.flip(new_sprite, True, False)

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
            pixel[3] = int(pixel[3] * opacity / 100)
            surface.set_at((x, y), tuple(pixel))
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


def quit(savesettings=False, clearevents=False):
    """
    Quits the game, avoids a bunch of repeated lines
    """
    if savesettings:
        game.save_settings()
    if clearevents:
        game.cur_events_list.clear()
    game.rpc.close_rpc.set()
    game.rpc.update_rpc.set()
    pygame.display.quit()
    pygame.quit()
    if game.rpc.is_alive():
        game.rpc.join(1)
    sys_exit()


PERMANENT = None
with open(f"resources/dicts/conditions/permanent_conditions.json", 'r') as read_file:
    PERMANENT = ujson.loads(read_file.read())

ACC_DISPLAY = None
with open(f"resources/dicts/acc_display.json", 'r') as read_file:
    ACC_DISPLAY = ujson.loads(read_file.read())

SNIPPETS = None
with open(f"resources/dicts/snippet_collections.json", 'r') as read_file:
    SNIPPETS = ujson.loads(read_file.read())