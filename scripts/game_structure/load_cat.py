import logging
import os
from math import floor
from random import choice

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
from ..cat.factories.cat_factory import CatFactory
from ..cat.factories.enums import CatType
from ..cat.factories.typed_dicts import MentorshipDict, StatusDict
from ..cat.names import Name
from ..cat.pronouns import get_new_pronouns
from scripts.housekeeping.version import SAVE_VERSION_NUMBER
from scripts.game_structure import constants
from scripts.game_structure import game
from ..cat.personality import Personality
from ..cat.skills import CatSkills
from ..clan_resources.point_of_interest import (
    clear_pois,
    generate_and_add_new_poi,
    PoiType,
)
from ..housekeeping.datadir import get_save_dir

logger = logging.getLogger(__name__)


def load_cats():
    load_faded_cat_ids(switch_get_value(Switch.clan_save_id))
    try:
        json_load()
    except FileNotFoundError:
        try:
            csv_load(Cat.all_cats)
        except FileNotFoundError as e:
            switch_set_value(Switch.error_message, "Can't find clan_cats.json!")
            switch_set_value(Switch.traceback, e)
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
            cat = CatFactory.create_cat(cat_type=CatType.LOAD_JSON, **cat_dict)
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
            cat.get_permanent_condition("paralyzed")
        elif "paralyzed" in cat.permanent_condition and not cat.pelt.paralyzed:
            cat.pelt.paralyzed = True

        # load the relationships
        try:
            if not cat.dead:
                cat.load_relationship_of_cat()
                if cat.relationships is not None and len(cat.relationships) < 1:
                    cat.init_all_relationships()
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
        cat_data = ""
    else:
        if os.path.exists(
            get_save_dir() + "/" + switch_get_value(Switch.clan_list)[0] + "cats.csv"
        ):
            with open(
                get_save_dir()
                + "/"
                + switch_get_value(Switch.clan_list)[0]
                + "cats.csv",
                "r",
                encoding="utf-8",
            ) as read_file:
                cat_data = read_file.read()
        else:
            with open(
                get_save_dir()
                + "/"
                + switch_get_value(Switch.clan_list)[0]
                + "cats.txt",
                "r",
                encoding="utf-8",
            ) as read_file:
                cat_data = read_file.read()
    if len(cat_data) > 0:
        cat_data = cat_data.replace("\t", ",")
        for i in cat_data.split("\n"):
            # CAT: ID(0) - prefix:suffix(1) - gender(2) - status(3) - age(4) - trait(5) - parent1(6) - parent2(7) - mentor(8)
            # PELT: pelt(9) - colour(10) - white(11) - length(12)
            # SPRITE: kitten(13) - apprentice(14) - warrior(15) - elder(16) - eye colour(17) - reverse(18)
            # - white patches(19) - pattern(20) - tortiebase(21) - tortiepattern(22) - tortiecolour(23) - skin(24) - skill(25) - NONE(26) - spec(27) - accessory(28) -
            # spec2(29) - moons(30) - mate(31)
            # dead(32) - SPRITE:dead(33) - exp(34) - dead for _ moons(35) - current apprentice(36)
            # (BOOLS, either TRUE OR FALSE) paralyzed(37) - no kits(38) - exiled(39)
            # genderalign(40) - former apprentices list (41)[FORMER APPS SHOULD ALWAYS BE MOVED TO THE END]
            if i.strip() != "":
                attr = i.split(",")
                for x in range(len(attr)):
                    attr[x] = attr[x].strip()
                    if attr[x] in ["None", "None "]:
                        attr[x] = None
                    elif attr[x].upper() == "TRUE":
                        attr[x] = True
                    elif attr[x].upper() == "FALSE":
                        attr[x] = False
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 1)",
                )
                the_pelt = Pelt(
                    colour=attr[2], name=attr[11], length=attr[9], eye_color=attr[17]
                )
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 2)",
                )

                inheritance = {
                    "parent1": attr[6],
                    "parent2": attr[7],
                }

                mentorship = MentorshipDict(
                    mentor=attr[8],
                    former_mentor=[],
                    patrol_with_mentor=0,
                    apprentice=[],
                    former_apprentices=[],
                )

                the_cat = CatFactory.create_cat(
                    CatType.LOAD_CSV,
                    ID=attr[0],
                    gender=attr[2],
                    status={"rank": attr[3]},
                    inheritance=inheritance,
                    mentorship=mentorship,
                    pelt=the_pelt,
                )

                the_cat.name = Name(
                    prefix=attr[1].split(":")[0],
                    suffix=attr[1].split(":")[1],
                )

                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 3)",
                )
                the_cat.mentor = attr[8]
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 4)",
                )
                (
                    the_cat.pelt.cat_sprites["kitten"],
                    the_cat.pelt.cat_sprites["adolescent"],
                ) = int(attr[13]), int(attr[14])
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 5)",
                )
                the_cat.pelt.cat_sprites["adult"], the_cat.pelt.cat_sprites["elder"] = (
                    int(attr[15]),
                    int(attr[16]),
                )
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 6)",
                )
                (
                    the_cat.pelt.cat_sprites["young adult"],
                    the_cat.pelt.cat_sprites["senior adult"],
                ) = int(attr[15]), int(attr[15])
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 7)",
                )
                (
                    the_cat.pelt.reverse,
                    the_cat.pelt.white_patches,
                    the_cat.pelt.tortie_marking,
                ) = (attr[18], attr[19], attr[20])
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 8)",
                )
                (
                    the_cat.pelt.tortie_base,
                    the_cat.pelt.tortie_pattern,
                    the_cat.pelt.tortie_colour,
                ) = (attr[21], attr[22], attr[23])
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 9)",
                )
                the_cat.trait, the_cat.pelt.skin, the_cat.specialty = (
                    attr[5],
                    attr[24],
                    attr[27],
                )
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 10)",
                )
                the_cat.skill = attr[25]
                if len(attr) > 28:
                    the_cat.pelt.accessory = (attr[28],)
                if len(attr) > 29:
                    the_cat.specialty2 = attr[29]
                else:
                    the_cat.specialty2 = None
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 11)",
                )
                if len(attr) > 34:
                    the_cat.experience = int(attr[34])
                    experiencelevels = [
                        "very low",
                        "low",
                        "slightly low",
                        "average",
                        "somewhat high",
                        "high",
                        "very high",
                        "master",
                        "max",
                    ]
                    the_cat.experience_level = experiencelevels[
                        floor(int(the_cat.experience) / 10)
                    ]
                else:
                    the_cat.experience = 0
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 12)",
                )
                if len(attr) > 30:
                    # Attributes that are to be added after the update
                    the_cat.moons = int(attr[30])
                    if len(attr) >= 31:
                        # assigning mate to cat, if any
                        the_cat.mate = [attr[31]]
                    if len(attr) >= 32:
                        # Is the cat dead
                        the_cat.status.send_to_afterlife(target_ID=CatGroup.STARCLAN_ID)
                        the_cat.pelt.cat_sprites["dead"] = attr[33]
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 13)",
                )
                if len(attr) > 35:
                    the_cat.dead_for = int(attr[35])
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 14)",
                )
                if len(attr) > 36 and attr[36] is not None:
                    the_cat.apprentice = attr[36].split(";")
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 15)",
                )
                if len(attr) > 37:
                    the_cat.pelt.paralyzed = bool(attr[37])
                if len(attr) > 38:
                    the_cat.no_kits = bool(attr[38])
                if len(attr) > 39:
                    if bool(attr[39]):
                        the_cat.status.exile_from_group()
                if len(attr) > 40:
                    the_cat.genderalign = attr[40]
                if len(attr) > 41 and attr[41] is not None:  # KEEP THIS AT THE END
                    the_cat.former_apprentices = attr[41].split(";")
        switch_set_value(
            Switch.error_message,
            "There was an error loading this clan's mentors, apprentices, relationships, or sprite info.",
        )
        for inter_cat in all_cats.values():
            # Load the mentors and apprentices after all cats have been loaded
            switch_set_value(
                Switch.error_message,
                f"There was an error loading this clan's mentors/apprentices. Last cat read was {inter_cat}",
            )
            inter_cat.mentor = Cat.all_cats.get(inter_cat.mentor)
            apps = []
            former_apps = []
            for app_id in inter_cat.apprentice:
                app = Cat.all_cats.get(app_id)
                # Make sure if cat isn't an apprentice, they're a former apprentice
                if app.status.rank == CatRank.APPRENTICE:
                    apps.append(app)
                else:
                    former_apps.append(app)
            for f_app_id in inter_cat.former_apprentices:
                f_app = Cat.all_cats.get(f_app_id)
                former_apps.append(f_app)
            inter_cat.apprentice = [
                a.ID for a in apps
            ]  # Switch back to IDs. I don't want to risk breaking everything.
            inter_cat.former_apprentices = [a.ID for a in former_apps]
            if not inter_cat.dead:
                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading this clan's relationships. Last cat read was {inter_cat}",
                )
                inter_cat.load_relationship_of_cat()
            switch_set_value(
                Switch.error_message,
                f"There was an error loading a cat's sprite info. Last cat read was {inter_cat}",
            )
            # update_sprite(inter_cat)
        # generate the relationship if some is missing
        if not the_cat.dead:
            switch_set_value(
                Switch.error_message,
                f"There was an error when relationships were created.",
            )
            for id in all_cats.keys():
                the_cat = all_cats.get(id)
                switch_set_value(
                    Switch.error_message,
                    f"There was an error when relationships for cat #{the_cat} are created.",
                )
                if the_cat.relationships is not None and len(the_cat.relationships) < 1:
                    the_cat.create_all_relationships()
        switch_set_value(Switch.error_message, "")


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
