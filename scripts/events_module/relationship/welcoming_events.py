import os
from copy import deepcopy
from random import choice

import i18n

from scripts.game_structure import constants
from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank
from scripts.event_class import Single_Event
from scripts.game_structure.game_essentials import game
from scripts.utility import (
    change_relationship_values,
    event_text_adjust,
)
from scripts.game_structure.localization import load_lang_resource


class Welcoming_Events:
    """All events which are related to welcome a new cat in the clan."""

    currently_loaded_lang = None

    @staticmethod
    def welcome_cat(clan_cat: Cat, new_cat: Cat) -> None:
        """Checks and triggers the welcome event from the Clan cat to the new cat.

        Parameters
        ----------
        clan_cat : Cat
            the Clan cat which welcome the new cat
        new_cat : Cat
            new cat which will be welcomed

        Returns
        -------
        """
        if new_cat.ID == clan_cat.ID:
            return

        if Welcoming_Events.currently_loaded_lang != i18n.config.get("locale"):
            Welcoming_Events.currently_loaded_lang = i18n.config.get("locale")
            Welcoming_Events.rebuild_dicts()

        # setup the status as "key" to use it
        rank = clan_cat.status.rank
        if rank.is_any_medicine_rank():
            rank = "medicine"

        if rank == CatRank.MEDIATOR_APPRENTICE:
            rank = CatRank.MEDIATOR

        # collect all events
        possible_events = deepcopy(GENERAL_WELCOMING)
        if rank not in WELCOMING_MASTER_DICT:
            print(f"ERROR: there is no welcoming json for the rank {rank}")
        else:
            possible_events.extend(WELCOMING_MASTER_DICT[rank])
        filtered_events = Welcoming_Events.filter_welcome_interactions(
            possible_events, new_cat
        )

        # choose which interaction will be displayed
        random_interaction = choice(filtered_events)
        interaction_str = choice(random_interaction.interactions)

        # prepare string for display
        interaction_str = event_text_adjust(
            Cat, interaction_str, main_cat=clan_cat, random_cat=new_cat
        )

        # influence the relationship
        new_to_clan_cat = constants.CONFIG["new_cat"]["rel_buff"]["new_to_clan_cat"]
        clan_cat_to_new = constants.CONFIG["new_cat"]["rel_buff"]["clan_cat_to_new"]
        change_relationship_values(
            cats_to=[clan_cat],
            cats_from=[new_cat],
            romantic_love=new_to_clan_cat["romantic"],
            platonic_like=new_to_clan_cat["platonic"],
            dislike=new_to_clan_cat["dislike"],
            admiration=new_to_clan_cat["admiration"],
            comfortable=new_to_clan_cat["comfortable"],
            jealousy=new_to_clan_cat["jealousy"],
            trust=new_to_clan_cat["trust"],
        )
        change_relationship_values(
            cats_to=[new_cat],
            cats_from=[clan_cat],
            romantic_love=clan_cat_to_new["romantic"],
            platonic_like=clan_cat_to_new["platonic"],
            dislike=clan_cat_to_new["dislike"],
            admiration=clan_cat_to_new["admiration"],
            comfortable=clan_cat_to_new["comfortable"],
            jealousy=clan_cat_to_new["jealousy"],
            trust=clan_cat_to_new["trust"],
        )

        # add it to the event list
        game.cur_events_list.append(
            Single_Event(
                interaction_str,
                ["relation", "interaction"],
                [new_cat.ID, clan_cat.ID],
                cat_dict={"m_c": new_cat, "r_c": clan_cat},
            )
        )

        # the effect is set through the settings, therefore a rough assumption has to be made
        effect = " (neutral effect)"
        if (
            clan_cat_to_new["romantic"] > 0
            or clan_cat_to_new["platonic"] > 0
            or clan_cat_to_new["admiration"] > 0
            or new_to_clan_cat["comfortable"] > 0
            or clan_cat_to_new["trust"] > 0
        ):
            effect = " (positive effect)"
        elif clan_cat_to_new["dislike"] > 0 or clan_cat_to_new["jealousy"] > 0:
            effect = " (negative effect)"

        interaction_str += effect

        # add to relationship logs
        if new_cat.ID in clan_cat.relationships:
            clan_cat.relationships[new_cat.ID].log.append(
                interaction_str
                + i18n.t(
                    "relationships.age_postscript",
                    name=str(clan_cat.name),
                    count=clan_cat.moons,
                )
            )

            new_cat.relationships[clan_cat.ID].link_relationship()

        if clan_cat.ID in new_cat.relationships:
            clan_cat.relationships[new_cat.ID].log.append(
                interaction_str
                + i18n.t(
                    "relationships.age_postscript",
                    name=str(new_cat.name),
                    count=new_cat.moons,
                )
            )

    @staticmethod
    def rebuild_dicts():
        global WELCOMING_MASTER_DICT, GENERAL_WELCOMING
        fallback_path = os.path.join(
            "resources",
            "lang",
            i18n.config.get("fallback"),
            "events",
            "relationship_events",
            "welcoming_events",
        )
        for file in os.listdir(
            fallback_path
        ):  # always use fallback bcs english must exist
            if "general.json" == file:
                continue
            rank = file.split(".")[0]
            WELCOMING_MASTER_DICT[rank] = create_welcome_interaction(
                load_lang_resource(
                    f"events/relationship_events/welcoming_events/{file}"
                )
            )

        GENERAL_WELCOMING = create_welcome_interaction(
            load_lang_resource(
                "events/relationship_events/welcoming_events/general.json"
            )
        )

    @staticmethod
    def filter_welcome_interactions(welcome_interactions: list, new_cat: Cat) -> list:
        """Filter welcome events based on states.

        Parameters
        ----------
        welcome_interactions : list
            a list of welcome interaction
        new_cat : Cat
            new cat which will be welcomed

        Returns
        -------
        filtered list of welcome interactions
        """
        filtered = []
        for interaction in welcome_interactions:
            if (
                interaction.background
                and new_cat.backstory not in interaction.background
            ):
                continue

            if interaction.new_cat_moons:
                threshold_moon = interaction.new_cat_moons.split("_")
                threshold_moon = int(threshold_moon[len(threshold_moon) - 1])

                if (
                    "over" in interaction.new_cat_moons
                    and new_cat.moons < threshold_moon
                ):
                    continue
                if (
                    "under" in interaction.new_cat_moons
                    and new_cat.moons > threshold_moon
                ):
                    continue
                if (
                    "over" not in interaction.new_cat_moons
                    and "under" not in interaction.new_cat_moons
                ):
                    print(
                        f"ERROR: The new cat welcoming event {interaction.id} has a not valid moon restriction for the new cat."
                    )
                    continue

            filtered.append(interaction)
        return filtered


class Welcome_Interaction:
    def __init__(self, id, interactions=None, background=None, new_cat_moons=None):
        self.id = id
        self.background = background
        self.new_cat_moons = new_cat_moons

        if interactions:
            self.interactions = interactions
        else:
            self.interactions = ["m_c is welcoming r_c."]


# ---------------------------------------------------------------------------- #
#                   build master dictionary for interactions                   #
# ---------------------------------------------------------------------------- #

WELCOMING_MASTER_DICT = {}
GENERAL_WELCOMING = []


def create_welcome_interaction(inter_list) -> list:
    created_list = []

    for inter in inter_list:
        created_list.append(
            Welcome_Interaction(
                id=inter["id"],
                interactions=inter["interactions"] if "interactions" in inter else None,
                background=inter["background"] if "background" in inter else None,
                new_cat_moons=(
                    inter["new_cat_moons"] if "new_cat_moons" in inter else None
                ),
            )
        )

    return created_list
