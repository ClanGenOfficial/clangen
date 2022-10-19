import ujson
from .game_essentials import *
# simple utility function which are not direct related to a class

resource_directory = "scripts/resources/"
PERSONALITY_COMPATIBILITY = None
try:
    with open(f"{resource_directory}personality_compatibility.json", 'r') as read_file:
        PERSONALITY_COMPATIBILITY = ujson.loads(read_file.read())
except:
    game.switches['error_message'] = 'There was an error loading the personality compatibility json!'


def get_highest_romantic_relation(relationships):
    """Returns the relationship with the highest romantic value."""
    romantic_relation = list(filter(lambda rel: rel.romantic_love > 0, relationships))
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

def add_siblings_to_cat(cat, cat_class):
    """Iterate over all current cats and add the ID to the current cat."""
    for inter_cat in cat_class.all_cats.values():
        if inter_cat.is_sibling(cat) and inter_cat.ID not in cat.siblings:
            cat.siblings.append(inter_cat.ID)
        if cat.is_sibling(inter_cat) and cat.ID not in inter_cat.siblings:
            inter_cat.siblings.append(cat.ID)