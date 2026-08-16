from scripts.cat.cats import Cat

biggest_family = {}


def set_biggest_family():
    """Gets the biggest family of the clan."""
    global biggest_family
    for cat in Cat.all_cats.values():
        ancestors = list(cat.get_relatives())
        if not biggest_family:
            biggest_family = ancestors
            biggest_family.append(cat.ID)
        elif len(biggest_family) < len(ancestors) + 1:
            biggest_family = ancestors
            biggest_family.append(cat.ID)


def get_biggest_family() -> dict:
    if not biggest_family:
        set_biggest_family()

    return biggest_family


def biggest_family_is_big():
    """Returns if the current biggest family is big enough to 'activates' additional inbreeding counters."""

    living_cats = len(
        [i for i in Cat.all_cats.values() if i.status.alive_in_player_clan]
    )
    return len(biggest_family) > (living_cats / 10)
