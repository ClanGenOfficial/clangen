from typing import Union

from scripts.cat.cats import Cat
from scripts.clan import OtherClan
from scripts.clan_package.get_clan_cats import get_living_clan_cat_count
from scripts.clan_resources.freshkill import FRESHKILL_EVENT_TRIGGER_FACTOR
from scripts.events_module.event_filters import (
    event_for_tags,
    event_for_location,
    event_for_season,
    event_for_required_cat_types,
    event_for_reputation,
    event_for_clan_relations,
    event_for_freshkill_supply,
    event_for_herb_supply,
)
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import game


def pass_general_constraints(
    event: Union[PatrolEvent, TextPoolEvent],
    primary_cat: Cat,
    involved_cats: dict,
    other_clan: OtherClan = None,
    is_debug_event: bool = False,
):
    # CHECK LOCATION
    if not event_for_location(event.location):
        if is_debug_event:
            print("DEBUG: requested event does not meet constraints (biome)")
        return False

    # CHECK SEASON
    if not event_for_season(event.season):
        if is_debug_event:
            print("DEBUG: requested event does not meet constraints (season)")
        return False

    # CHECK CAT TYPES
    if not event_for_required_cat_types(event.required_cat_types, involved_cats):
        if is_debug_event:
            print("DEBUG: requested event does not meet cat type requirements.")
        return False

    # CHECK TAGS
    if not event_for_tags(event.tags, primary_cat):
        if is_debug_event:
            print("DEBUG: requested event does not meet constraints (tags)")
        return False

    if hasattr(event, "required_reputation"):
        if not event_for_reputation(event.required_reputation.get("outsider")):
            if is_debug_event:
                print(
                    "DEBUG: requested event does not meet constraints (outsider reputation)"
                )
                return False

        if not event_for_clan_relations(
            event.required_reputation.get("other_clan"), other_clan
        ):
            if is_debug_event:
                print(
                    "DEBUG: requested event does not meet constraints (other_clan reputation)"
                )
                return False

    if hasattr(event, "supply"):
        clan_size = get_living_clan_cat_count(Cat)
        for block in event.supply:
            if not block.get("trigger"):
                continue
            if "freshkill" in block["type"]:
                if not event_for_freshkill_supply(
                    game.clan.freshkill_pile,
                    trigger=block["trigger"],
                    factor=FRESHKILL_EVENT_TRIGGER_FACTOR,
                    clan_size=clan_size,
                ):
                    if is_debug_event:
                        print(
                            "DEBUG: requested event does not meet constraints (freshkill trigger)"
                        )
                    return False
            else:
                if not event_for_herb_supply(
                    trigger=block["trigger"],
                    supply_type=block["type"],
                    clan_size=clan_size,
                ):
                    if is_debug_event:
                        print(
                            "DEBUG: requested event does not meet constraints (herb trigger)"
                        )
                    return False

    return True
