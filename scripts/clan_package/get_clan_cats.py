from typing import Union, Type, TYPE_CHECKING, Tuple, List

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


def get_alive_clan_queens(living_cats):
    living_kits = [
        cat
        for cat in living_cats
        if cat.status.alive_in_player_clan and cat.status.rank.is_baby()
    ]

    queen_dict = {}
    for cat in living_kits.copy():
        parents = cat.get_parents()
        # Fetch parent object, only alive and not outside.
        parents = [
            cat.fetch_cat(i)
            for i in parents
            if cat.fetch_cat(i) and cat.fetch_cat(i).status.alive_in_player_clan
        ]
        if not parents:
            continue

        if (
            len(parents) == 1
            or len(parents) > 2
            or all(i.gender == "male" for i in parents)
            or parents[0].gender == "female"
        ):
            if parents[0].ID in queen_dict:
                queen_dict[parents[0].ID].append(cat)
                living_kits.remove(cat)
            else:
                queen_dict[parents[0].ID] = [cat]
                living_kits.remove(cat)
        elif len(parents) == 2:
            if parents[1].ID in queen_dict:
                queen_dict[parents[1].ID].append(cat)
                living_kits.remove(cat)
            else:
                queen_dict[parents[1].ID] = [cat]
                living_kits.remove(cat)
    return queen_dict, living_kits


def find_alive_cats_with_rank(
    Cat: Union["Cat", Type["Cat"]],
    ranks: list,
    working: bool = False,
    sort: bool = False,
) -> list:
    """
    returns a list of cat objects for all living cats with a listed rank in Clan
    :param Cat Cat: Cat class
    :param list ranks: list of ranks to search for
    :param bool working: default False, set to True if you would like the list to only include working cats
    :param bool sort: default False, set to True if you would like list sorted by descending moon age
    """

    alive_cats = [
        i
        for i in Cat.all_cats.values()
        if i.status.rank in ranks and i.status.alive_in_player_clan
    ]

    if working:
        alive_cats = [i for i in alive_cats if not i.not_working()]

    if sort:
        alive_cats = sorted(alive_cats, key=lambda cat: cat.moons, reverse=True)

    return alive_cats


def get_living_clan_cat_count(Cat):
    """
    Returns the int of all living cats within the Clan
    :param Cat: Cat class
    """
    count = 0
    for the_cat in Cat.all_cats.values():
        if not the_cat.status.alive_in_player_clan:
            continue
        count += 1
    return count


def get_cats_same_age(Cat, cat, age_range=10):
    """
    Look for all cats in the Clan and returns a list of cats which are in the same age range as the given cat.
    :param Cat: Cat class
    :param cat: the given cat
    :param int age_range: The allowed age difference between the two cats, default 10
    """
    cats = []
    for inter_cat in Cat.all_cats.values():
        if not inter_cat.status.alive_in_player_clan:
            continue
        if inter_cat.ID == cat.ID:
            continue

        if inter_cat.ID not in cat.relationships:
            cat.create_one_relationship(inter_cat)
            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)
            continue

        if (
            inter_cat.moons <= cat.moons + age_range
            and inter_cat.moons <= cat.moons - age_range
        ):
            cats.append(inter_cat)

    return cats


def get_possible_mates(cat) -> Tuple[List["Cat"], List["Cat"]]:
    """
    Returns a list of available cats which are possible mates for the given cat,
    and a second list of cats that are possible mates with pre-existing romantic interest.
    :param cat: The cat
    :return: possible mates and possible mates with existing romantic interest
    """
    possible_mates = []
    existing_romance_mates = []
    for inter_cat in cat.all_cats.values():
        if not inter_cat.status.alive_in_player_clan:
            continue
        if inter_cat.ID == cat.ID:
            continue

        if inter_cat.ID not in cat.relationships:
            cat.create_one_relationship(inter_cat)
            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)
            continue

        if inter_cat.is_potential_mate(cat, for_love_interest=True):
            if cat.relationships[inter_cat.ID].romance > 0:
                existing_romance_mates.append(inter_cat)
            possible_mates.append(inter_cat)
    return possible_mates, existing_romance_mates
