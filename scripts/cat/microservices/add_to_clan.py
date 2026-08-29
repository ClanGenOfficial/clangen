from typing import List

from scripts.cat.cats import Cat
from scripts.cat.enums import CatGroup
from scripts.game_structure import game


def add_to_clan(cat):
    """Makes an "outside cat" a Clan cat. Returns a list of IDs for any additional cats that
    are coming with them.
    """

    if not cat.status.is_exiled(CatGroup.PLAYER_CLAN_ID):
        cat.history.add_beginning()

    cat.status.add_to_group(new_group_ID=CatGroup.PLAYER_CLAN_ID, age=cat.age)

    if game.clan:
        game.clan.add_cat(cat)


def add_dependents_to_clan(cat: "Cat") -> List[str]:
    """
    :param cat: the cat whose dependents are being added to the clan
    :return ids: list of IDs of additional dependents that are coming with this one
    """
    # check if there are kits under 12 moons with this cat and also add them to the clan
    children = cat.get_children()
    ids = []
    for child_id in children:
        child = Cat.all_cats[child_id]
        if (
            not child.dead
            and not child.status.is_exiled(CatGroup.PLAYER_CLAN_ID)
            and child.moons < 12
            and not child.status.alive_in_player_clan
        ):
            child.history.add_beginning()
            child.status.add_to_group(
                new_group_ID=CatGroup.PLAYER_CLAN_ID, age=child.age
            )
            if game.clan:
                game.clan.add_cat(child)
            ids.append(child_id)

    return ids
