import i18n

from scripts.cat.cats import Cat
from scripts.config import get_config
from scripts.game_structure import game
from scripts.game_structure.game.settings.settings import cat


def handle_moonskip():
    _check_expiration()
    game.clan.current_nest_build_count.clear()


def _check_expiration():
    expiration = get_config("clan_resources.herbs.quarantine_nest_expiration")
    expired_entries = [
        moon_created
        for moon_created in game.clan.quarantine_nests
        if int(moon_created.replace("moon_", "")) + expiration <= game.clan.age
    ]
    if not expired_entries:
        return

    # now make sure we don't expire a nest in use
    current_count = get_current_nest_count()
    num_of_quarantined_cats = len(game.clan.quarantined_cats)
    while current_count - len(expired_entries) < num_of_quarantined_cats:
        expired_entries.pop(0)
        if not expired_entries:
            break

    amount_expiring = 0

    for entry in expired_entries:
        amount_expiring += game.clan.quarantine_nests[entry]
        game.clan.quarantine_nests.pop(entry)

    game.herb_events_list.append(
        i18n.t("screens.med_den.nest_expiration", count=amount_expiring)
    )


def get_current_nest_count():
    count = 0
    for entry in game.clan.quarantine_nests.values():
        count += entry

    return count


def add_nest(building_cat_ID: str):
    game.clan.quarantine_nests[f"moon_{game.clan.age}"] += 1

    game.clan.current_nest_build_count[building_cat_ID] = (
        game.clan.current_nest_build_count.get(building_cat_ID, 0) + 1
    )

    for herb, amount in get_config(
        "clan_resources.herbs.quarantine_nest_recipe"
    ).items():
        game.clan.herb_supply.remove_herb(herb, amount)


def remove_nest(occupying_cat: Cat = None):
    remove_entry = None
    for moon in game.clan.quarantine_nests:
        game.clan.quarantine_nests[moon] -= 1
        if game.clan.quarantine_nests[moon] <= 0:
            remove_entry = moon
        break

    if remove_entry:
        game.clan.quarantine_nests.pop(remove_entry)

    game.herb_events_list.append(
        i18n.t("screens.med_den.nest_removed", name=str(occupying_cat.name))
    )
