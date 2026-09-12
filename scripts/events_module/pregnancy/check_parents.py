from random import choice, random
from typing import Optional

from scripts.cat.cats import Cat
from scripts.cat.enums import (
    CatAge,
)
from scripts.cat_relations.relationship import Relationship, create_one_relationship
from scripts.clan_package.settings import get_clan_setting
from scripts.events_module.pregnancy.check_family_size import (
    biggest_family_is_big,
    get_biggest_family,
)
from scripts.events_module.event_filters import (
    get_highest_romantic_relation,
)
from scripts.config import get_config


def check_if_can_have_kits(cat):
    """Check if the given cat can have kits, see for age, birth-cooldown and so on."""
    if not cat:
        return False

    if cat.birth_cooldown:
        return False

    if "recovering from birth" in cat.injuries:
        return False

    # decide chances of having kits, and if it's possible at all.
    # Including - age, dead status, having kits turned off.
    not_correct_age = (
        cat.age in [CatAge.NEWBORN, CatAge.KITTEN, CatAge.ADOLESCENT] or cat.moons < 15
    )
    if not_correct_age or cat.no_kits or cat.dead:
        return False

    # check for mate
    if cat.mate:
        for mate_id in cat.mate:
            if mate_id not in cat.all_cats:
                print(
                    f"WARNING: {cat.name}  has an invalid mate # {mate_id}. This has been unset."
                )
                cat.mate.remove(mate_id)
    else:
        # if the cat has no mate, and we don't allow single parents, unmated parents, or affairs
        # then they can't have kits
        if (
            not get_clan_setting("single parentage")
            and not get_clan_setting("unmated parentage")
            and not get_clan_setting("affair")
        ):
            return False

    # if function reaches this point, having kits is possible
    return True


def check_second_parent(cat: Cat, second_parent: Cat) -> tuple[bool, bool]:
    """
    This checks to see if the chosen second parent can have kits. It assumes CAT can have kits.
    returns:
    parent can have kits, kits are adopted
    """
    # Checks for second parent alone:
    if not check_if_can_have_kits(second_parent):
        return False, False

    # Check to see if the pair can have kits.
    if cat.gender == second_parent.gender:
        if get_clan_setting("same sex birth"):
            return True, False
        elif get_clan_setting("same sex adoption"):
            return True, True
        else:
            return False, False

    return True, False


def get_second_parent(cat: Cat) -> tuple[Optional[Cat], bool]:
    """
    Return the second parent of a cat, which will have kits.
    Also returns a bool that is true if an affair was triggered.
    """
    # randomly select a mate of given cat
    chosen_mate = None
    # if the sex does matter, choose the best solution to allow kits
    same_sex_birth_allowed = get_clan_setting("same sex birth")
    coparenting_allowed = get_clan_setting("unmated parentage")
    if cat.mate:
        if same_sex_birth_allowed:
            # choose any mate
            chosen_mate = cat.fetch_cat(choice(cat.mate))
        else:
            # choose mate that is opposite sex
            possible_mates = [
                cat.fetch_cat(mate_id)
                for mate_id in cat.mate
                if cat.fetch_cat(mate_id).gender != cat.gender
            ]
            if possible_mates:
                chosen_mate = choice(possible_mates)
    elif not coparenting_allowed:
        # if coparenting is OFF, then an unmated cat can't have a kitten
        return None, False

    affair_allowed = get_clan_setting("affair")
    if chosen_mate and not affair_allowed:
        # if affairs setting is OFF, mate will always be the second parent
        return chosen_mate, False

    # get relationships to influence the affair chance
    relationship_toward_mate = None
    if chosen_mate and chosen_mate.ID in cat.relationships:
        relationship_toward_mate = cat.relationships[chosen_mate.ID]
    elif chosen_mate:
        relationship_toward_mate = create_one_relationship(cat, chosen_mate)

    # NONRANDOM AFFAIR & COPARENTING
    # Handle love affair chance.
    new_partner = _determine_highest_romantic_relation(
        cat, chosen_mate, relationship_toward_mate, same_sex_birth_allowed
    )
    if new_partner:
        return new_partner, True

    # RANDOM AFFAIR & COPARENTING
    if not cat.mate:
        # is there's no mate to cheat on then this isn't an affair, rather it's coparenting
        coparenting = True
    else:
        coparenting = False

    if coparenting:
        chance = get_config("pregnancy.unmated_random_affair_chance")
    else:
        chance = get_config("pregnancy.random_affair_chance")

    # 'buff' affairs & coparenting if the current biggest family is big + this cat doesn't belong there
    biggest_family = get_biggest_family()

    if biggest_family_is_big() and cat.ID not in biggest_family:
        chance = int(chance * 0.8)

    # "regular" random fling
    if not int(random() * chance):
        possible_partners = [
            i
            for i in Cat.all_cats_list
            if i.is_potential_mate(cat, for_love_interest=True)
            and (same_sex_birth_allowed or i.gender != cat.gender)
            and i.ID not in cat.mate
        ]

        # even it is a random affair, the cats should not hate each other or something like that
        p_affairs = []
        if len(possible_partners) > 0:
            for p_affair in possible_partners:
                if p_affair.ID in cat.relationships:
                    p_rel = cat.relationships[p_affair.ID]
                    if not p_rel.opposite_relationship:
                        p_rel.link_relationship()
                    p_rel_opp = p_rel.opposite_relationship
                    if p_rel_opp.like > -20 and p_rel.like > -20:
                        p_affairs.append(p_affair)
        possible_partners = p_affairs

        if len(possible_partners) > 0:
            chosen_affair = choice(possible_partners)
            return chosen_affair, True

    # no affair/coparent was found
    return chosen_mate, False


def _determine_highest_romantic_relation(
    cat: Cat,
    mate: Optional[Cat],
    relationship_with_mate: Optional[Relationship],
    same_sex_birth_allowed: bool,
) -> Optional[Cat]:
    """
    Function to handle everything around unmated affairs.
    Will return a second parent if triggerd, and none otherwise.
    """

    highest_romantic_relation = get_highest_romantic_relation(
        cat.relationships.values(), exclude_mate=True, potential_mate=True
    )

    # AFFAIR
    if mate and highest_romantic_relation:
        # Love affair calculation when the cat has a mate
        love_affair_chance = _get_love_affair_chance(
            relationship_with_mate, highest_romantic_relation
        )
        if not love_affair_chance or not int(random() * love_affair_chance):
            if (
                same_sex_birth_allowed
                or cat.gender != highest_romantic_relation.cat_to.gender
            ):
                return highest_romantic_relation.cat_to
    # COPARENTING
    elif highest_romantic_relation:
        # Love affair chance if the cat doesn't have a mate:
        coparenting_chance = _get_unmated_coparenting_chance(highest_romantic_relation)
        if not coparenting_chance or not int(random() * coparenting_chance):
            if (
                same_sex_birth_allowed
                or cat.gender != highest_romantic_relation.cat_to.gender
            ):
                return highest_romantic_relation.cat_to

    return None


def _get_love_affair_chance(mate_relation: Relationship, affair_relation: Relationship):
    """Looks into the current values and calculate the chance of having kits with the affair cat.
    The lower, the more likely they will have affairs. This function should only be called when mate
    and affair_cat are not the same.

    Returns:
        integer (number)
    """
    if not mate_relation.opposite_relationship:
        mate_relation.link_relationship()

    if not affair_relation.opposite_relationship:
        affair_relation.link_relationship()

    average_mate_love = (
        mate_relation.romance + mate_relation.opposite_relationship.romance
    ) / 2
    average_affair_love = (
        affair_relation.romance + affair_relation.opposite_relationship.romance
    ) / 2

    difference = average_mate_love - average_affair_love

    if difference < 0:
        # If the average love between affair partner is greater than the average love between the mate
        affair_chance = 10
        difference = -difference

        if difference > 30:
            affair_chance -= 7
        elif difference > 20:
            affair_chance -= 6
        elif difference > 15:
            affair_chance -= 5
        elif difference > 10:
            affair_chance -= 4

    elif difference > 0:
        # If the average love between the mate is greater than the average relationship between the affair
        affair_chance = 30

        if difference > 30:
            affair_chance += 8
        elif difference > 20:
            affair_chance += 5
        elif difference > 15:
            affair_chance += 3
        elif difference > 10:
            affair_chance += 5

    else:
        # For difference = 0 or some other weird stuff
        affair_chance = 15

    return affair_chance


def _get_unmated_coparenting_chance(relation: Relationship) -> int:
    """
    Calculates the chance of coparenting when neither the cat
    nor highest romantic relation have mates.
    """

    if not relation.opposite_relationship:
        relation.link_relationship()

    coparenting_chance = 15
    average_romantic_love = (
        relation.romance + relation.opposite_relationship.romance
    ) / 2

    if average_romantic_love > 50:
        coparenting_chance -= 12
    elif average_romantic_love > 40:
        coparenting_chance -= 10
    elif average_romantic_love > 30:
        coparenting_chance -= 7
    elif average_romantic_love > 10:
        coparenting_chance -= 5

    return coparenting_chance
