#!/usr/bin/env python3
# -*- coding: ascii -*-
import random

import i18n
import ujson

from scripts.cat_relations.enums import RelType
from scripts.events_module.event_filters import (
    event_for_location,
    event_for_season,
    event_for_tags,
    event_for_reputation,
    event_for_cat,
    event_for_freshkill_supply,
    event_for_herb_supply,
    event_for_clan_relations,
    cat_for_event,
)
from scripts.events_module.ongoing.ongoing_event import OngoingEvent
from scripts.events_module.short.short_event import ShortEvent
from scripts.game_structure import constants
from scripts.game_structure.game.switches import switch_get_value, Switch
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource
from scripts.utility import (
    get_living_clan_cat_count,
)


def get_resource_directory(fallback=False):
    return f"resources/lang/{i18n.config.get('locale') if not fallback else i18n.config.get('fallback')}/events/"


# ---------------------------------------------------------------------------- #
#                Tagging Guidelines can be found at the bottom                 #
# ---------------------------------------------------------------------------- #


class GenerateEvents:
    loaded_events = {}

    with open(
        f"resources/dicts/conditions/injuries.json", "r", encoding="utf-8"
    ) as read_file:
        INJURIES = ujson.loads(read_file.read())

    @staticmethod
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

    @staticmethod
    def get_ongoing_event_dicts(file_path):
        events = None
        try:
            with open(file_path, "r", encoding="utf-8") as read_file:
                events = ujson.loads(read_file.read())
        except:
            print(f"ERROR: Unable to load events from biome {file_path}.")

        return events

    @staticmethod
    def get_death_reaction_dicts(family_relation, rel_value):
        return load_lang_resource(
            f"events/death/death_reactions/{family_relation}/{family_relation}_{rel_value}.json"
        )

    @staticmethod
    def get_lead_den_event_dicts(event_type: str, success: bool):
        try:
            file_path = f"{get_resource_directory()}leader_den/{'success' if success else 'fail'}/{event_type}.json"
            with open(file_path, "r", encoding="utf-8") as read_file:
                events = ujson.loads(read_file.read())
        except:
            events = None
            print(
                f"ERROR: Unable to load lead den events for {event_type} {'success' if success else 'fail'}."
            )

        return events

    @staticmethod
    def clear_loaded_events():
        GenerateEvents.loaded_events = {}

    @staticmethod
    def generate_short_events(event_triggered, biome, frequency):
        file_path = f"{event_triggered}/{biome}.json"
        load_name = f"{file_path}_{frequency}"

        try:
            if load_name in GenerateEvents.loaded_events:
                return GenerateEvents.loaded_events[load_name]
            else:
                events_dict = GenerateEvents.get_short_event_dicts(file_path)

                event_list = []
                if not events_dict:
                    return event_list
                for event in events_dict:
                    event_text = event["event_text"] if "event_text" in event else None
                    event_frequency = event["frequency"] if "frequency" in event else 4
                    if not event_text:
                        event_text = (
                            event["death_text"] if "death_text" in event else None
                        )

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
                            event["exclude_involved"]
                            if "exclude_involved" in event
                            else []
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
                GenerateEvents.loaded_events[load_name] = event_list
                return event_list
        except:
            print(f"WARNING: {file_path} was not found, check short event generation")

    @staticmethod
    def generate_ongoing_events(event_type, biome, specific_event=None):
        file_path = f"{get_resource_directory()}/{event_type}/{biome}.json"

        if file_path in GenerateEvents.loaded_events:
            return GenerateEvents.loaded_events[file_path]
        else:
            events_dict = GenerateEvents.get_short_event_dicts(file_path)

            if not specific_event:
                event_list = []
                for event in events_dict:
                    event = OngoingEvent(
                        event=event["event"],
                        camp=event["camp"],
                        season=event["season"],
                        tags=event["tags"],
                        priority=event["priority"],
                        duration=event["duration"],
                        current_duration=0,
                        rarity=event["rarity"],
                        trigger_events=event["trigger_events"],
                        progress_events=event["progress_events"],
                        conclusion_events=event["conclusion_events"],
                        secondary_disasters=event["secondary_disasters"],
                        collateral_damage=event["collateral_damage"],
                    )
                    event_list.append(event)
                return event_list
            else:
                event = None
                for event in events_dict:
                    if event["event"] != specific_event:
                        continue
                    event = OngoingEvent(
                        event=event["event"],
                        camp=event["camp"],
                        season=event["season"],
                        tags=event["tags"],
                        priority=event["priority"],
                        duration=event["duration"],
                        current_duration=0,
                        progress_events=event["progress_events"],
                        conclusion_events=event["conclusion_events"],
                        collateral_damage=event["collateral_damage"],
                    )
                    break
                return event

    @staticmethod
    def possible_short_events(
        frequency,
        event_type=None,
    ):
        event_list = []

        # skip the rest of the loading if there is an unrecognised biome
        temp_biome = (
            game.clan.biome
            if not game.clan.override_biome
            else game.clan.override_biome
        )
        if temp_biome not in constants.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES "
                f"in clan.py?"
            )

        biome = temp_biome.lower()

        # biome specific events
        event_list.extend(
            GenerateEvents.generate_short_events(event_type, biome, frequency)
        )

        # any biome events
        event_list.extend(
            GenerateEvents.generate_short_events(event_type, "general", frequency)
        )

        return event_list

    @staticmethod
    def filter_possible_short_events(
        Cat_class,
        possible_events,
        cat,
        other_clan,
        freshkill_active,
        freshkill_trigger_factor,
        random_cat=None,
        sub_types=None,
        allowed_events=None,
        excluded_events=None,
        ignore_subtyping=False,
    ):
        final_events = []
        incorrect_format = []

        for event in possible_events:
            if event.history:
                if (
                    not isinstance(event.history, list)
                    or "cats" not in event.history[0]
                ):
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

            # if requirements are overridden, allow event through
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
                and cat.moons < constants.CONFIG["death_related"]["old_age_death_start"]
            ):
                continue
            # remove some non-old age events to encourage elders to die of old age more often
            if (
                "old_age" not in event.sub_type
                and cat.moons > constants.CONFIG["death_related"]["old_age_death_start"]
                and int(random.random() * 3)
            ):
                continue

            # check if already trans
            if "transition" in event.sub_type and cat.gender != cat.genderalign:
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
                    cat=cat,
                    cat_group=[cat, random_cat] if random_cat else None,
                    event_id=event.event_id,
                    injuries=m_c_injuries,
                ):
                    continue
            # if a random cat was pre-chosen, then we check if the event will be suitable for them
            if random_cat:
                if not event_for_cat(
                    cat_info=event.r_c,
                    cat=random_cat,
                    cat_group=[random_cat, cat],
                    event_id=event.event_id,
                    injuries=r_c_injuries,
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
                    if (
                        event.other_clan["changed"] < 0
                        and rel_change_type != "rel_down"
                    ):
                        continue

            # clans below a certain age can't have their supplies messed with
            if game.clan.age < 5 and event.supplies:
                continue

            elif event.supplies:
                clan_size = get_living_clan_cat_count(Cat_class)
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

            final_events.extend([event] * event.weight)
        if not final_events:
            return None, None

        cat_list = [
            c for c in Cat_class.all_cats.values() if c.status.alive_in_player_clan
        ]
        chosen_cat = None
        chosen_event = None

        if random_cat:
            chosen_cat = random_cat
            # if we've got our random cat already, then check if we have to find an ensured event
            if constants.CONFIG["event_generation"]["debug_ensure_event_id"]:
                for event in final_events:
                    if (
                        event.event_id
                        == constants.CONFIG["event_generation"]["debug_ensure_event_id"]
                    ):
                        chosen_event = event
                        break
            # else, pick a random one from the available events
            elif not chosen_event:
                chosen_event = random.choice(final_events)

        failed_ids = []
        while final_events and not chosen_cat and not chosen_event:
            chosen_event = random.choice(final_events)
            if chosen_event.event_id in failed_ids:
                final_events.remove(chosen_event)
                chosen_event = None
                continue

            # if we have an ensured id, only allow that event past
            if (
                constants.CONFIG["event_generation"]["debug_ensure_event_id"]
                and constants.CONFIG["event_generation"]["debug_ensure_event_id"]
                != chosen_event.event_id
            ):
                final_events.remove(chosen_event)
                chosen_event = None
                continue

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
                constraint_dict=chosen_event.r_c,
                possible_cats=cat_list,
                comparison_cat=cat,
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

        return chosen_event, chosen_cat

    @staticmethod
    def possible_ongoing_events(event_type=None, specific_event=None):
        event_list = []

        if game.clan.biome not in constants.BIOME_TYPES:
            print(
                f"WARNING: unrecognised biome {game.clan.biome} in generate_events. Have you added it to BIOME_TYPES in clan.py?"
            )

        else:
            biome = game.clan.biome.lower()
            if not specific_event:
                event_list.extend(
                    GenerateEvents.generate_ongoing_events(event_type, biome)
                )
                """event_list.extend(
                    GenerateEvents.generate_ongoing_events(event_type, "general", specific_event)
                )"""
                return event_list
            else:
                event = GenerateEvents.generate_ongoing_events(
                    event_type, biome, specific_event
                )
                return event

    @staticmethod
    def possible_death_reactions(family_relation, rel_value, trait, body_status):
        possible_events = []
        # grab general events first, since they'll always exist
        events = GenerateEvents.get_death_reaction_dicts("general", rel_value)
        possible_events.extend(events["general"][body_status])
        if trait in events and body_status in events[trait]:
            possible_events.extend(events[trait][body_status])

        # grab family events if they're needed. Family events should not be romantic.
        if family_relation != "general" and rel_value != RelType.ROMANCE:
            events = GenerateEvents.get_death_reaction_dicts(family_relation, rel_value)
            possible_events.extend(events["general"][body_status])
            if trait in events and body_status in events[trait]:
                possible_events.extend(events[trait][body_status])

        return possible_events

    def possible_lead_den_events(
        self,
        cat,
        event_type: str,
        interaction_type: str,
        success: bool,
        other_clan_temper=None,
        player_clan_temper=None,
    ) -> list:
        """
        finds and generates a list of possible leader den events
        :param cat: the cat object of the cat attending the Gathering
        :param other_clan_temper: the temperament of the other clan
        :param player_clan_temper: the temperament of the player clan
        :param event_type: other_clan or outsider
        :param interaction_type: str retrieved from object_ID of selected interaction button
        :param success: True if the interaction was a success, False if it was a failure
        """
        possible_events = []

        events = GenerateEvents.get_lead_den_event_dicts(event_type, success)
        for event in events:
            if event["interaction_type"] != interaction_type:
                continue

            if "other_clan_temper" in event or "player_clan_temper" in event:
                if (
                    other_clan_temper not in event["other_clan_temper"]
                    and "any" not in event["other_clan_temper"]
                ):
                    continue
                if (
                    player_clan_temper not in event["player_clan_temper"]
                    and "any" not in event["player_clan_temper"]
                ):
                    continue

            elif "reputation" in event:
                if not event_for_reputation(event["reputation"]):
                    continue

            cat_info = event["m_c"]
            if not event_for_cat(cat_info=cat_info, cat=cat):
                continue

            possible_events.append(event)

        return possible_events


generate_events = GenerateEvents()
