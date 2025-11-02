#!/usr/bin/env python3
# -*- coding: ascii -*-

import i18n
import ujson

from scripts.cat_relations.enums import RelType
from scripts.events_module.event_filters import (
    event_for_reputation,
    event_for_cat,
)
from scripts.events_module.ongoing.ongoing_event import OngoingEvent
from scripts.game_structure import constants
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource


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
    def generate_ongoing_events(event_type, biome, specific_event=None):
        file_path = f"{get_resource_directory()}/{event_type}/{biome}.json"

        if file_path in GenerateEvents.loaded_events:
            return GenerateEvents.loaded_events[file_path]
        else:
            events_dict = GenerateEvents.get_ongoing_event_dicts(file_path)

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
        possible_events.extend(events["general"].get(body_status, []))
        if trait in events and body_status in events[trait]:
            possible_events.extend(events[trait].get(body_status, []))

        # grab family events if they're needed. Family events should not be romantic.
        if family_relation != "general" and rel_value != RelType.ROMANCE:
            events = GenerateEvents.get_death_reaction_dicts(family_relation, rel_value)
            if "general" in events:
                possible_events.extend(events["general"].get(body_status, []))
            if trait in events and body_status in events[trait]:
                possible_events.extend(events[trait].get(body_status, []))

        return possible_events

    @staticmethod
    def possible_lead_den_events(
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
