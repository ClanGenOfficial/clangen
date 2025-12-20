import random
from typing import Optional

import i18n
import ujson

from scripts.cat.cats import Cat
from scripts.cat.skills import SkillPath
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
    cat_for_event,
)
from scripts.events_module.short.short_event import ShortEvent
from scripts.game_structure import constants, game
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.utility import get_living_clan_cat_count, get_warring_clan

loaded_events = {}
used_events = set()


def get_resource_directory(fallback=False):
    return f"resources/lang/{i18n.config.get('locale') if not fallback else i18n.config.get('fallback')}/events/"


def create_short_event(
    event_type: str,
    main_cat: Cat,
    random_cat: Cat = None,
    victim_cat: Cat = None,
    sub_type: list = None,
    future_event=None,
):
    """
    Handles everything involved in finding and executing an appropriate short event for the given args.
    :param event_type: The type of event to find.
    :param main_cat: The cat object that will take the role of m_c.
    :param random_cat: The cat object that will take the role of r_c.
    :param victim_cat: The cat object that will take the role of mur_c.
    :param sub_type: The required subtypes for this event.
    :param future_event: If this is being triggered by a future event, pass the future event object here.
    """
    if future_event and (
        not main_cat.status.alive_in_player_clan
        or (random_cat and not random_cat.status.alive_in_player_clan)
    ):
        # we set this to true because we want it to be considered triggered and thus removed
        # however we aren't removing because it was triggered, we're removing because none of the involved cats are eligible
        future_event.triggered = True
        return

    types = [event_type]
    sub_types = sub_type if sub_type else []

    # check for war and assign other_clan accordingly
    war_chance = 5
    # if the war didn't go badly, then we decrease the chance of this event being war-focused
    if switch_get_value(Switch.war_rel_change_type) != "rel_down":
        war_chance = 2
    if game.clan.war.get("at_war", False) and random.randint(1, war_chance) != 1:
        enemy_clan = get_warring_clan()
        other_clan = enemy_clan
        sub_types.append("war")
    else:
        other_clan = random.choice(
            game.clan.all_other_clans if game.clan.all_other_clans else None
        )

    # collecting CAMP skill cats for reduction events
    camp_cats = [
        c
        for c in Cat.all_cats_list
        if c.status.alive_in_player_clan
        and (
            (c.skills.primary and c.skills.primary.path == SkillPath.CAMP)
            or (c.skills.secondary and c.skills.secondary.path == SkillPath.CAMP)
        )
    ]

    avoidance_chance = 1
    # each camp cat will increase the chance that significant reduction events do not occur
    for c in camp_cats:
        # tiers are added in order to make the chance num, this means the higher tiers have greater influence
        if c.skills.primary.path == SkillPath.CAMP:
            # +1 bc primary paths should have a little bit larger influence
            avoidance_chance += c.skills.primary.tier + 1
        elif c.skills.secondary and c.skills.secondary.path == SkillPath.CAMP:
            avoidance_chance += c.skills.secondary.tier

    # NOW find the possible events and filter
    if event_type == "birth_death":
        event_type = "death"
    elif event_type == "health":
        event_type = "injury"

    # choosing frequency
    # think of it as "in a span of 10 moons, in how many moons should this sort of event appear?"
    frequency_roll = random.randint(1, 10)
    if frequency_roll <= 4:
        frequency = 4
    elif frequency_roll <= 7:
        frequency = 3
    elif frequency_roll <= 9:
        frequency = 2
    else:
        frequency = 1

    chosen_event = None
    while not chosen_event and frequency < 5:
        events = find_needed_events(
            frequency,
            event_type,
        )

        chosen_event, random_cat = filter_events(
            possible_events=events,
            main_cat=main_cat,
            random_cat=random_cat,
            other_clan=other_clan,
            sub_types=sub_types,
            allowed_events=future_event.allowed_events if future_event else None,
            excluded_events=future_event.excluded_events if future_event else None,
            ignore_subtyping=future_event.negate_subtyping if future_event else None,
            reduction_avoidance_chance=avoidance_chance,
        )
        if not chosen_event:
            # we'll see if any more common events are available
            frequency += 1
            # if we've hit 5 frequency, then we've probably used all the events.
            # so we'll reset the used_events list and look for 4 frequency events again
            if used_events and frequency == 5:
                used_events.clear()
                frequency = 4

    if chosen_event:
        used_events.add(chosen_event.event_id)
        # set future event trigger status
        if future_event:
            future_event.triggered = True

        # setting event info
        chosen_event.main_cat = main_cat
        chosen_event.random_cat = random_cat
        chosen_event.victim_cat = victim_cat
        chosen_event.types = types

        # execute the event
        chosen_event.execute_event(other_clan)

    else:
        # this doesn't necessarily mean there's a problem, but can be helpful for narrowing down possibilities
        print(f"WARNING: no {event_type}: {sub_types} events found for {main_cat.name}")
        return


def find_needed_events(frequency, event_type=None) -> list:
    """
    Handles detecting the biome and collecting all events possible for biome and type
    :param frequency: The event frequency to look for
    :param event_type: The type of event to pull
    """
    event_list = []

    # skip the rest of the loading if there is an unrecognised biome
    temp_biome = (
        game.clan.biome if not game.clan.override_biome else game.clan.override_biome
    )
    if temp_biome not in constants.BIOME_TYPES:
        print(
            f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES "
            f"in clan.py?"
        )

    biome = temp_biome.lower()

    # biome specific events
    event_list.extend(generate_event_objects(event_type, biome, frequency))

    # any biome events
    event_list.extend(generate_event_objects(event_type, "general", frequency))

    return event_list


def get_event_dicts(file_path) -> list:
    """
    Opens and loads .json for the given file path.
    :param file_path: The file path to open
    """
    try:
        with open(
            get_resource_directory() + file_path, "r", encoding="utf-8"
        ) as read_file:
            events = ujson.loads(read_file.read())
    except ValueError:
        try:
            with open(
                get_resource_directory(fallback=True) + file_path,
                "r",
                encoding="utf-8",
            ) as read_file:
                events = ujson.loads(read_file.read())
        except ValueError:
            print(f"ERROR: Unable to load {file_path}.")
            return []

    return events


def generate_event_objects(event_triggered, biome, frequency) -> list:
    """
    Gets the event dicts for the given args and creates the short event objects for each entry in the dict.
    :param event_triggered: The type of event triggered
    :param biome: The biome to pull events for
    :param frequency: The frequency to pull events for
    """
    file_path = f"{event_triggered}/{biome}.json"
    load_name = f"{file_path}_{frequency}"

    try:
        if file_path in loaded_events:
            return loaded_events[file_path]
        if load_name in loaded_events:
            return loaded_events[load_name]
        else:
            events_dict = get_event_dicts(file_path)

            event_list = []
            if not events_dict:
                return event_list
            for event in events_dict:
                event_text = event["event_text"] if "event_text" in event else None
                event_frequency = event["frequency"] if "frequency" in event else 4

                if not event_text:
                    event_text = event["death_text"] if "death_text" in event else None

                if not event_text:
                    print(
                        f"WARNING: some events resources which are used in generate_events have no 'event_text'."
                    )
                if frequency != event_frequency:
                    continue

                event = ShortEvent(
                    event_id=event["event_id"] if "event_id" in event else "",
                    location=event["location"] if "location" in event else ["any"],
                    season=event["season"] if "season" in event else ["any"],
                    sub_type=event["sub_type"] if "sub_type" in event else [],
                    tags=event["tags"] if "tags" in event else [],
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
            loaded_events[load_name] = event_list
            return event_list

    except ValueError:
        print(f"WARNING: {file_path} was not found, check short event generation")
        return []


def filter_events(
    possible_events,
    main_cat,
    random_cat,
    other_clan,
    sub_types: list = None,
    allowed_events: list = None,
    excluded_events: list = None,
    ignore_subtyping: bool = False,
    reduction_avoidance_chance: int = 1,
) -> (Optional[ShortEvent], Optional[Cat]):
    """
    Filters possible events to find an event that fits the given requirements
    :param possible_events: list of possible events
    :param main_cat: main cat for this event
    :param random_cat: random cat for this event
    :param other_clan: other clan for this event
    :param sub_types: subtypes for this event
    :param allowed_events: list of allowed event IDs
    :param excluded_events: list of excluded event IDs
    :param ignore_subtyping: ignores subtyping entirely
    :param reduction_avoidance_chance: chance to avoid events that reduce supplies
    """
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

        # check if event has already been used
        if event.event_id in used_events:
            continue

        # ensure ID and requirements override
        if constants.CONFIG["event_generation"]["debug_override_requirements"]:
            final_events.append(event)
            continue

        # check for event sub_type
        if not ignore_subtyping:
            if set(event.sub_type) != set(sub_types):
                continue

        if not event_for_location(event.location):
            continue

        if not event_for_season(event.season):
            continue

        # check tags
        if not event_for_tags(event.tags, main_cat, random_cat):
            continue

        # make complete leader death less likely until the leader is over 150 moons (or unless it's a murder)
        if main_cat.status.is_leader:
            if "all_lives" in event.tags and "murder" not in event.sub_type:
                if int(main_cat.moons) < 150 and int(random.random() * 5):
                    continue

        # check for old age
        if (
            "old_age" in event.sub_type
            and main_cat.moons
            < constants.CONFIG["death_related"]["old_age_death_start"]
        ):
            continue
        # remove some non-old age events to encourage elders to die of old age more often
        if (
            "old_age" not in event.sub_type
            and main_cat.moons
            > constants.CONFIG["death_related"]["old_age_death_start"]
            and int(random.random() * 3)
        ):
            continue

        # check if already trans
        if "transition" in event.sub_type and main_cat.gender != main_cat.genderalign:
            continue

        m_c_injuries = []
        r_c_injuries = []
        discard = False
        for block in event.injury:
            for injury in block["injuries"]:
                if "m_c" in block["cats"]:
                    m_c_injuries.append(injury)
                if "r_c" in block["cats"]:
                    r_c_injuries.append(injury)
            if discard:
                continue

        # check if m_c is allowed this event
        if event.m_c:
            if not event_for_cat(
                cat_info=event.m_c,
                cat=main_cat,
                cat_group=[main_cat, random_cat] if random_cat else None,
                event_id=event.event_id,
            ):
                continue

        # if a random cat was pre-chosen, then we check if the event will be suitable for them
        if random_cat:
            if not event_for_cat(
                cat_info=event.r_c,
                cat=random_cat,
                cat_group=[random_cat, main_cat],
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
                rel_change_type = switch_get_value(Switch.war_rel_change_type)
                if event.other_clan["changed"] < 0 and rel_change_type != "rel_down":
                    continue

        # clans below a certain age can't have their supplies messed with
        if game.clan.age < 5 and event.supplies:
            continue

        elif event.supplies:
            clan_size = get_living_clan_cat_count(Cat)
            # finding cats with the CAMP skill
            camp_cats = [
                c
                for c in Cat.all_cats_list
                if c.status.alive_in_player_clan
                and (
                    (c.skills.primary and c.skills.primary.path == SkillPath.CAMP)
                    or (
                        c.skills.secondary and c.skills.secondary.path == SkillPath.CAMP
                    )
                )
            ]

            discard = False
            for supply in event.supplies:
                trigger = supply["trigger"]
                supply_type = supply["type"]

                if (
                    supply["adjust"] in ["reduce_half", "reduce_full"]
                    and random.randint(1, reduction_avoidance_chance) != 1
                ):
                    discard = True
                    break

                if supply_type == "freshkill":
                    if not FRESHKILL_EVENT_ACTIVE:
                        continue

                    if not event_for_freshkill_supply(
                        game.clan.freshkill_pile,
                        trigger,
                        FRESHKILL_EVENT_TRIGGER_FACTOR,
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

        final_events.extend([event] * event.weight)

    if not final_events:
        return None, None

    cat_list = [
        c
        for c in Cat.all_cats.values()
        if c.status.alive_in_player_clan and c != main_cat
    ]
    chosen_cat = None
    chosen_event = None

    if random_cat:
        chosen_cat = random_cat
        # if we've got our random cat already, then check if we have to find an ensured event
        if constants.CONFIG["event_generation"]["debug_ensure_event_id"]:
            for possible_event in final_events:
                if (
                    possible_event.event_id
                    == constants.CONFIG["event_generation"]["debug_ensure_event_id"]
                ):
                    chosen_event = possible_event
                    break
        # else, pick a random one from the available events
        else:
            chosen_event = random.choice(final_events)

    failed_ids = []
    while final_events and not chosen_cat and not chosen_event:
        chosen_event = random.choice(final_events)
        if chosen_event.event_id in failed_ids:
            final_events.remove(chosen_event)
            chosen_event = None
            continue

        if (
            constants.CONFIG["event_generation"]["debug_ensure_event_id"]
            and constants.CONFIG["event_generation"]["debug_ensure_event_id"]
            != chosen_event.event_id
        ):
            final_events.remove(chosen_event)
            failed_ids.append(chosen_event.event_id)
            chosen_event = None
            continue

        # if this doesn't need a random cat, we stop here and run with it
        if not chosen_event.r_c:
            break

        # if we're overriding requirements, don't bother looking for an appropriate cat
        if constants.CONFIG["event_generation"]["debug_override_requirements"]:
            chosen_cat = random.choice(cat_list)
            continue

        # gotta gather injuries so we can check if the cat can get them
        r_c_injuries = []
        for block in chosen_event.injury:
            r_c_injuries.extend(block["injuries"] if "r_c" in block["cats"] else [])

        chosen_cat = cat_for_event(
            constraint_dict=chosen_event.r_c.copy(),
            possible_cats=cat_list,
            comparison_cat=main_cat,
            comparison_cat_rel_status=chosen_event.m_c.get(
                "relationship_status", []
            ).copy(),
            injuries=r_c_injuries,
            return_id=False,
        )

        if not chosen_cat:
            failed_ids.append(chosen_event.event_id)
            final_events.remove(chosen_event)
            chosen_event = None
        else:
            break

    for notice in incorrect_format:
        print(notice)

    if not final_events:
        return None, None

    return chosen_event, chosen_cat
