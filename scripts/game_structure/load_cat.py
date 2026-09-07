import logging
import os
from math import floor
from random import choice
from typing import Union

import i18n
import ujson

from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.save_load import load_faded_cat_ids
from scripts.cat_relations.inheritance2 import inheritance_db
from scripts.cat.save_load import get_faded_ids
from ..cat.enums import CatGroup, CatRank
from scripts.cat.pelts import Pelt
from scripts.cat_relations.inheritance import Inheritance
from scripts.game_structure.game.switches import (
    switch_get_value,
    switch_set_value,
    Switch,
)
from ..cat.factories.enums import CatType
from ..cat.factories.load_cat_factory import LoadCatFactory
from ..cat.factories.typed_dicts import MentorshipDict, StatusDict
from ..cat.names import Name
from ..cat.pronouns import get_new_pronouns
from scripts.housekeeping.version import SAVE_VERSION_NUMBER
from scripts.game_structure import constants
from scripts.game_structure import game
from ..cat.personality import Personality
from ..cat.skills import CatSkills
from ..cat_relations.cat_handle_funcs import (
    init_all_relationships,
    load_relationship_of_cat,
)
from ..clan_resources.point_of_interest import (
    clear_pois,
    generate_and_add_new_poi,
    PoiType,
)
from ..cat.microservices.conditions import get_permanent_condition
from ..housekeeping.datadir import get_save_dir

logger = logging.getLogger(__name__)


def load_cats():
    load_faded_cat_ids(switch_get_value(Switch.clan_save_id))
    try:
        json_load()
    except FileNotFoundError:
        csv_load(Cat.all_cats)
    except Exception:
        Cat.all_cats.clear()
        Cat.all_cats_list.clear()
        raise


def json_load():
    Cat.all_cats.clear()
    Cat.all_cats_list.clear()

    all_cats = []
    clanname = switch_get_value(Switch.clan_list)[0]
    clan_cats_json_path = f"{get_save_dir()}/{clanname}/clan_cats.json"
    with open(
        f"resources/dicts/conversion_dict.json", "r", encoding="utf-8"
    ) as read_file:
        convert = ujson.loads(read_file.read())
    try:
        with open(clan_cats_json_path, "r", encoding="utf-8") as read_file:
            cat_data = ujson.loads(read_file.read())
    except PermissionError as e:
        switch_set_value(Switch.error_message, f"Can\t open {clan_cats_json_path}!")
        switch_set_value(Switch.traceback, e)
        raise
    except ujson.JSONDecodeError as e:
        switch_set_value(Switch.error_message, f"{clan_cats_json_path} is malformed!")
        switch_set_value(Switch.traceback, e)
        raise

    old_tortie_patches = convert["old_tortie_patches"]

    # create new cat objects
    for i, cat_dict in enumerate(cat_data):
        try:
            cat = LoadCatFactory.create_cat(**cat_dict)
            Cat.all_cats[cat.ID] = cat
            all_cats.append(cat)

        except KeyError as e:
            if "ID" in cat_dict:
                key = f" ID #{cat_dict['ID']} "
            else:
                key = f" at index {i} "
            switch_set_value(
                Switch.error_message, f"Cat{key}in clan_cats.json is missing {e}!"
            )
            switch_set_value(Switch.traceback, e)
            raise

    # replace cat ids with cat objects and add other needed variables
    for cat in all_cats:
        if cat.status.rank in (CatRank.LEADER, CatRank.DEPUTY, CatRank.MEDICINE_CAT):
            if cat.status.group == CatGroup.STARCLAN:
                game.starclan.adjust_facets_by_cat(cat)
            elif cat.status.group == CatGroup.DARK_FOREST:
                game.dark_forest.adjust_facets_by_cat(cat)

        cat.load_conditions()

        # this is here to handle paralyzed cats in old saves
        if cat.pelt.paralyzed and "paralyzed" not in cat.permanent_condition:
            get_permanent_condition(cat, "paralyzed")
        elif "paralyzed" in cat.permanent_condition and not cat.pelt.paralyzed:
            cat.pelt.paralyzed = True

        # load the relationships
        try:
            if not cat.dead:
                load_relationship_of_cat(cat)
                if cat.relationships is not None and len(cat.relationships) < 1:
                    init_all_relationships(cat)
            else:
                cat.relationships = {}
        except Exception as e:
            logger.exception(
                f"There was an error loading relationships for cat #{cat}."
            )
            switch_set_value(
                Switch.error_message,
                f"There was an error loading relationships for cat #{cat}.",
            )
            switch_set_value(Switch.traceback, e)
            raise
        if constants.CONFIG["save_load"]["load_integrity_checks"]:
            save_check()

    inheritance_db.clear_stored_data()
    inheritance_db.load_inheritances(Cat, get_faded_ids)


def csv_load(all_cats):
    if switch_get_value(Switch.clan_list)[0].strip() == "":
        return
    else:
        switch_set_value(Switch.error_message, "Can't find clan_cats.json")
        if os.path.exists(
            get_save_dir() + "/" + switch_get_value(Switch.clan_list)[0] + "cats.csv"
        ):
            switch_set_value(
                Switch.error_message,
                "CSV Clans are no longer supported. Please use an external tool to update your Clan to the modern format.",
            )
        elif os.path.exists(
            get_save_dir() + "/" + switch_get_value(Switch.clan_list)[0] + "cats.txt"
        ):
            switch_set_value(
                Switch.error_message,
                "TXT Clans are no longer supported. Please use an external tool to update your Clan to the modern format.",
            )
        raise FileNotFoundError


def save_check():
    """Checks through loaded cats, checks and attempts to fix issues
    NOT currently working."""
    return

    for cat in Cat.all_cats:
        cat_ob = Cat.all_cats[cat]

        # Not-mutural mate relations
        # if cat_ob.mate:
        #    _temp_ob = Cat.all_cats.get(cat_ob.mate)
        #    if _temp_ob:
        #        # Check if the mate's mate feild is set to none
        #        if not _temp_ob.mate:
        #            _temp_ob.mate = cat_ob.ID
        #    else:
        #        # Invalid mate
        #        cat_ob.mate = None


def version_convert(version_info):
    """Does all save-conversion that require referencing the saved version number.
    This is a separate function, since the version info is stored in clan.json, but most conversion needs to be
    done on the cats. Clan data is loaded in after cats, however."""

    if version_info is None:
        return

    if version_info["version_name"] == SAVE_VERSION_NUMBER:
        # Save was made on current version
        return

    if version_info["version_name"] is None:
        version = 0
    else:
        version = version_info["version_name"]

    if version < 1:
        # Save was made before version number storage was implemented.
        # (ie, save file version 0)
        # This means the EXP must be adjusted.
        for c in Cat.all_cats.values():
            c.experience = c.experience * 3.2

    if version < 2:
        for c in Cat.all_cats.values():
            for con in c.injuries:
                moons_with = 0
                if "moons_with" in c.injuries[con]:
                    moons_with = c.injuries[con]["moons_with"]
                    c.injuries[con].pop("moons_with")
                c.injuries[con]["moon_start"] = game.clan.age - moons_with

            for con in c.illnesses:
                moons_with = 0
                if "moons_with" in c.illnesses[con]:
                    moons_with = c.illnesses[con]["moons_with"]
                    c.illnesses[con].pop("moons_with")
                c.illnesses[con]["moon_start"] = game.clan.age - moons_with

            for con in c.permanent_condition:
                moons_with = 0
                if "moons_with" in c.permanent_condition[con]:
                    moons_with = c.permanent_condition[con]["moons_with"]
                    c.permanent_condition[con].pop("moons_with")
                c.permanent_condition[con]["moon_start"] = game.clan.age - moons_with

    # freshkill start for older clans
    if version < 3 and game.clan.freshkill_pile:
        add_prey = game.clan.freshkill_pile.amount_food_needed() * 2
        game.clan.freshkill_pile.add_freshkill(add_prey)

    # death history text revision
    if version < 4:
        for c in Cat.all_cats.values():
            if not c.status.is_leader:
                continue
            for death in c.history.died_by:
                if death["text"] == "multi_lives":
                    # skip these as changing them will break stuff
                    continue
                if death["text"].startswith("m_c lost a life"):
                    # skip these as it duplicates the existing death text
                    continue
                death["text"] = (
                    "m_c lost a life when {PRONOUN/m_c/subject} " + death["text"]
                )
                # check if a period is present and append one if not
                if death["text"][-1] != ".":
                    death["text"] += "."

    # generate points of interest
    if version < 5:
        # remove any already loaded points of interest
        clear_pois()

        generate_and_add_new_poi(biome=game.clan.biome, category=PoiType.GATHERING)
        generate_and_add_new_poi(biome=game.clan.biome, category=PoiType.MOONPLACE)

        for i in range(3):
            generate_and_add_new_poi(biome=game.clan.biome, category=PoiType.TERRAIN)
