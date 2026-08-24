from typing import Union, Optional, TYPE_CHECKING

from scripts.clan_package.get_clan_cats import get_living_clan_cat_count
from scripts.events_module.event_filters import (
    event_for_tags,
    event_for_location,
    event_for_season,
    event_for_required_cat_types,
    event_for_reputation,
    event_for_clan_relations,
    event_for_freshkill_supply,
    event_for_herb_supply,
    event_for_temperament,
)
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import game

if TYPE_CHECKING:
    from scripts.cat.cats import Cat
    from scripts.clan import OtherClan


def passes_general_constraints(
    event: Union[PatrolEvent, TextPoolEvent],
    primary_cat: "Cat",
    involved_cats: dict,
    other_clan: Optional["OtherClan"] = None,
    is_debug_event: bool = False,
) -> bool:
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

    # CHECK TEMPERAMENT
    if hasattr(event, "required_temperament"):
        if not event_for_temperament(event.required_temperament, primary_cat):
            if is_debug_event:
                print(
                    "DEBUG: requested event does not meet constraints (patrol_temperament)"
                )
            return False

    if hasattr(event, "required_reputation") and event.required_reputation:
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

    if hasattr(event, "supply") and event.supply:
        clan_size = get_living_clan_cat_count(primary_cat)
        for block in event.supply:
            if not block.get("trigger"):
                continue
            if "freshkill" in block["type"]:
                if not event_for_freshkill_supply(
                    game.clan.freshkill_pile,
                    trigger=block["trigger"],
                    clan_size=clan_size,
                ):
                    if is_debug_event:
                        print(
                            "DEBUG: requested event does not meet constraints (freshkill trigger)"
                        )
                    return False
            else:
                if not event_for_herb_supply(
                    trigger=block["trigger"], supply_type=block["type"]
                ):
                    if is_debug_event:
                        print(
                            "DEBUG: requested event does not meet constraints (herb trigger)"
                        )
                    return False

    return True
