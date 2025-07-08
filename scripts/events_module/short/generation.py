import random

import i18n
import ujson

from scripts.cat.cats import Cat
from scripts.clan_resources.freshkill import (
    FRESHKILL_EVENT_ACTIVE,
    FRESHKILL_EVENT_TRIGGER_FACTOR,
)
from scripts.events_module.event_filters import (
    event_for_location,
    event_for_tags,
    event_for_cat,
    event_for_reputation,
    event_for_clan_relations,
    event_for_freshkill_supply,
    event_for_herb_supply,
    event_for_season,
)
from scripts.events_module.short.short_event import ShortEvent
from scripts.game_structure.game_essentials import game
from scripts.utility import get_living_clan_cat_count, get_warring_clan

loaded_events = {}


def get_resource_directory(fallback=False):
    return f"resources/lang/{i18n.config.get('locale') if not fallback else i18n.config.get('fallback')}/events/"


def get_short_event_dicts(file_path):
    try:
        with open(
            get_resource_directory() + file_path, "r", encoding="utf-8"
        ) as read_file:
            events = ujson.loads(read_file.read())
    except:
        try:
            with open(
                get_resource_directory(fallback=True) + file_path,
                "r",
                encoding="utf-8",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"ERROR: Unable to load {file_path}.")
            return None

    return events


def find_possible_short_events(event_type=None):
    event_list = []

    # skip the rest of the loading if there is an unrecognised biome
    temp_biome = (
        game.clan.biome if not game.clan.override_biome else game.clan.override_biome
    )
    if temp_biome not in game.clan.BIOME_TYPES:
        print(
            f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES "
            f"in clan.py?"
        )

    biome = temp_biome.lower()

    # biome specific events
    event_list.extend(generate_short_events(event_type, biome))

    # any biome events
    event_list.extend(generate_short_events(event_type, "general"))

    return event_list


def generate_short_events(event_triggered, biome):
    file_path = f"{event_triggered}/{biome}.json"

    try:
        if file_path in loaded_events:
            return loaded_events[file_path]
        else:
            events_dict = get_short_event_dicts(file_path)

            event_list = []
            if not events_dict:
                return event_list
            for event in events_dict:
                event_text = event["event_text"] if "event_text" in event else None
                if not event_text:
                    event_text = event["death_text"] if "death_text" in event else None

                if not event_text:
                    print(
                        f"WARNING: some events resources which are used in generate_events have no 'event_text'."
                    )
                event = ShortEvent(
                    event_id=event["event_id"] if "event_id" in event else "",
                    location=event["location"] if "location" in event else ["any"],
                    season=event["season"] if "season" in event else ["any"],
                    sub_type=event["sub_type"] if "sub_type" in event else [],
                    tags=event["tags"] if "tags" in event else [],
                    weight=event["weight"] if "weight" in event else 20,
                    text=event_text,
                    new_accessory=(
                        event["new_accessory"] if "new_accessory" in event else []
                    ),
                    m_c=event["m_c"] if "m_c" in event else {},
                    r_c=event["r_c"] if "r_c" in event else {},
                    new_cat=event["new_cat"] if "new_cat" in event else [],
                    injury=event["injury"] if "injury" in event else [],
                    exclude_involved=(
                        event["exclude_involved"] if "exclude_involved" in event else []
                    ),
                    history=event["history"] if "history" in event else [],
                    relationships=(
                        event["relationships"] if "relationships" in event else []
                    ),
                    outsider=event["outsider"] if "outsider" in event else {},
                    other_clan=event["other_clan"] if "other_clan" in event else {},
                    supplies=event["supplies"] if "supplies" in event else [],
                    new_gender=event["new_gender"] if "new_gender" in event else [],
                    future_event=event["future_event"]
                    if "future_event" in event
                    else {},
                )
                event_list.append(event)

            # Add to loaded events.
            loaded_events[file_path] = event_list
            return event_list
    except:
        print(f"WARNING: {file_path} was not found, check short event generation")


def filter_possible_short_events(
    possible_events,
    cat,
    random_cat,
    other_clan,
    freshkill_active,
    freshkill_trigger_factor,
    sub_types=None,
    allowed_events=None,
    excluded_events=None,
    ignore_subtyping=False,
):
    final_events = []
    incorrect_format = []

    for event in possible_events:
        if event.history:
            if not isinstance(event.history, list) or "cats" not in event.history[0]:
                if (
                    f"{event.event_id} history formatted incorrectly"
                    not in incorrect_format
                ):
                    incorrect_format.append(
                        f"{event.event_id} history formatted incorrectly"
                    )
        if event.injury:
            if not isinstance(event.injury, list) or "cats" not in event.injury[0]:
                if (
                    f"{event.event_id} injury formatted incorrectly"
                    not in incorrect_format
                ):
                    incorrect_format.append(
                        f"{event.event_id} injury formatted incorrectly"
                    )

        # check if event is in allowed or excluded
        if allowed_events and event.event_id not in allowed_events:
            continue
        if excluded_events and event.event_id in excluded_events:
            continue

        # ensure ID and requirements override
        if (
            event.event_id == game.config["event_generation"]["debug_ensure_event_id"]
            and game.config["event_generation"]["debug_override_requirements"]
        ):
            final_events.append(event)
            break

        # check for event sub_type
        if not ignore_subtyping:
            if set(event.sub_type) != set(sub_types):
                continue

        if not event_for_location(event.location):
            continue

        if not event_for_season(event.season):
            continue

        # check tags
        if not event_for_tags(event.tags, cat, random_cat):
            continue

        # make complete leader death less likely until the leader is over 150 moons (or unless it's a murder)
        if cat.status.is_leader:
            if "all_lives" in event.tags and "murder" not in event.sub_type:
                if int(cat.moons) < 150 and int(random.random() * 5):
                    continue

        # check for old age
        if (
            "old_age" in event.sub_type
            and cat.moons < game.config["death_related"]["old_age_death_start"]
        ):
            continue
        # remove some non-old age events to encourage elders to die of old age more often
        if (
            "old_age" not in event.sub_type
            and cat.moons > game.config["death_related"]["old_age_death_start"]
            and int(random.random() * 3)
        ):
            continue

        # check if already trans
        if "transition" in event.sub_type and cat.gender != cat.genderalign:
            continue

        if event.m_c:
            if not event_for_cat(
                cat_info=event.m_c,
                cat=cat,
                cat_group=[cat, random_cat] if random_cat else None,
                event_id=event.event_id,
            ):
                continue

        if event.r_c and random_cat:
            if not event_for_cat(
                cat_info=event.r_c,
                cat=random_cat,
                cat_group=[random_cat, cat],
                event_id=event.event_id,
            ):
                continue

        # check if outsider event is allowed
        if event.outsider:
            if not event_for_reputation(event.outsider["current_rep"]):
                continue

        # other Clan related checks
        if event.other_clan:
            if not other_clan:
                continue

            if not event_for_clan_relations(
                event.other_clan["current_rep"], other_clan
            ):
                continue

            # during a war we want to encourage the clans to have positive events
            # when the overall war notice was positive
            if "war" in event.sub_type:
                rel_change_type = game.switches["war_rel_change_type"]
                if event.other_clan["changed"] < 0 and rel_change_type != "rel_down":
                    continue

        # clans below a certain age can't have their supplies messed with
        if game.clan.age < 5 and event.supplies:
            continue

        elif event.supplies:
            clan_size = get_living_clan_cat_count(Cat)
            discard = False
            for supply in event.supplies:
                trigger = supply["trigger"]
                supply_type = supply["type"]
                if supply_type == "freshkill":
                    if not freshkill_active:
                        continue

                    if not event_for_freshkill_supply(
                        game.clan.freshkill_pile,
                        trigger,
                        freshkill_trigger_factor,
                        clan_size,
                    ):
                        discard = True
                        break
                    else:
                        discard = False

                else:  # if supply type wasn't freshkill, then it must be a herb type
                    if not event_for_herb_supply(trigger, supply_type, clan_size):
                        discard = True
                        break
                    else:
                        discard = False

            if discard:
                continue

        # ensure ID without requirements override
        if event.event_id == game.config["event_generation"]["debug_ensure_event_id"]:
            final_events.append(event)
            break

        final_events.extend([event] * event.weight)

    for notice in incorrect_format:
        print(notice)

    return final_events


def create_short_event(
    event_type: str,
    main_cat,
    random_cat,
    victim_cat=None,
    sub_type: list = None,
    future_event=None,
):
    """
    Handles everything involved in finding an appropriate short event for the given args
    """
    types = [event_type]
    sub_types = sub_type

    # check for war and assign other_clan accordingly
    war_chance = 5
    # if the war didn't go badly, then we decrease the chance of this event being war-focused
    if game.switches["war_rel_change_type"] != "rel_down":
        war_chance = 2
    if game.clan.war.get("at_war", False) and random.randint(1, war_chance) != 1:
        enemy_clan = get_warring_clan()
        other_clan = enemy_clan
        other_clan_name = f"{other_clan.name}Clan"
        sub_types.append("war")
    else:
        other_clan = random.choice(game.clan.all_clans if game.clan.all_clans else None)
        other_clan_name = f"{other_clan.name}Clan"

    # NOW find the possible events and filter
    if event_type == "birth_death":
        event_type = "death"
    elif event_type == "health":
        event_type = "injury"

    events = find_possible_short_events(event_type)

    final_events = filter_possible_short_events(
        possible_events=events,
        cat=main_cat,
        random_cat=random_cat,
        other_clan=other_clan,
        freshkill_active=FRESHKILL_EVENT_ACTIVE,
        freshkill_trigger_factor=FRESHKILL_EVENT_TRIGGER_FACTOR,
        sub_types=sub_types,
        allowed_events=future_event.allowed_events if future_event else None,
        excluded_events=future_event.excluded_events if future_event else None,
        ignore_subtyping=future_event.negate_subtyping if future_event else None,
    )
    if isinstance(game.config["event_generation"]["debug_ensure_event_id"], str):
        found = False
        for _event in final_events:
            if (
                _event.event_id
                == game.config["event_generation"]["debug_ensure_event_id"]
            ):
                final_events = [_event]
                print(
                    f"FOUND debug_ensure_event_id: {game.config['event_generation']['debug_ensure_event_id']} "
                    f"was set as the only event option"
                )
                found = True
                break
        if not found:
            # this print is very spammy, but can be helpful if unsure why a debug event isn't triggering
            # print(f"debug_ensure_event_id: {game.config['event_generation']['debug_ensure_event_id']} "
            #      f"was not possible for {self.main_cat.name}.  {self.main_cat.name} was looking for a {event_type}: {self.sub_types} event")
            pass

    try:
        # choose an event!
        chosen_event = random.choice(final_events)

        # set future event trigger status
        if future_event:
            future_event.triggered = True

        # setting event info
        chosen_event.main_cat = main_cat
        chosen_event.random_cat = random_cat
        chosen_event.victim_cat = victim_cat
        chosen_event.other_clan_name = other_clan_name
        chosen_event.types = types

        # execute the event
        chosen_event.execute_event(other_clan_name=other_clan_name, types=types)

        # this print is good for testing, but gets spammy in large clans
        # print(f"CHOSEN: {self.chosen_event.event_id}")
    except IndexError:
        # this doesn't necessarily mean there's a problem, but can be helpful for narrowing down possibilities
        print(
            f"WARNING: no {event_type}: {sub_types} events found for {main_cat.name} "
            f"and {random_cat.name if random_cat else 'no random cat'}"
        )
        return
