import logging
import os
from math import floor
from random import choice

import i18n
import ujson

from scripts.cat.cats import Cat, BACKSTORIES
from ..cat.enums import CatGroup, CatRank
from scripts.cat.pelts import Pelt
from scripts.cat_relations.inheritance import Inheritance
from scripts.game_structure.game.switches import (
    switch_get_value,
    switch_set_value,
    Switch,
)
from scripts.game_structure.localization import get_new_pronouns
from scripts.housekeeping.version import SAVE_VERSION_NUMBER
from scripts.game_structure import constants
from scripts.game_structure import game
from ..cat.personality import Personality
from ..cat.skills import CatSkills
from ..cat.status import StatusDict
from ..housekeeping.datadir import get_save_dir

logger = logging.getLogger(__name__)


def load_cats():
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
    Cat.dead_cats.clear()
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
    for i, cat in enumerate(cat_data):
        try:
            # accounting for old saves
            # checks first if status is in the old format
            # if it is then we use the old info to provide an initial status dict
            if isinstance(cat["status"], str):
                # this sucks, but we need to get the actual str age to make sure nothing goes wonky
                age = None
                for key_age in Cat.age_moons.keys():
                    if cat["moons"] in range(
                        Cat.age_moons[key_age][0], Cat.age_moons[key_age][1] + 1
                    ):
                        age = key_age
                status_dict = {"rank": cat["status"], "age": age}
            else:
                status_dict = cat["status"]

            new_cat = Cat(
                ID=cat["ID"],
                prefix=cat["name_prefix"],
                suffix=cat["name_suffix"],
                specsuffix_hidden=(
                    cat["specsuffix_hidden"] if "specsuffix_hidden" in cat else False
                ),
                gender=cat["gender"],
                status_dict=status_dict,
                parent1=cat["parent1"],
                parent2=cat["parent2"],
                moons=cat["moons"],
                eye_colour=cat["eye_colour"],
                loading_cat=True,
            )

            if cat["eye_colour"] == "BLUE2":
                cat["eye_colour"] = "COBALT"
            if cat["eye_colour"] in ["BLUEYELLOW", "BLUEGREEN"]:
                if cat["eye_colour"] == "BLUEYELLOW":
                    cat["eye_colour2"] = "YELLOW"
                elif cat["eye_colour"] == "BLUEGREEN":
                    cat["eye_colour2"] = "GREEN"
                cat["eye_colour"] = "BLUE"
            if "eye_colour2" in cat:
                if cat["eye_colour2"] == "BLUE2":
                    cat["eye_colour2"] = "COBALT"

            if "tint" in cat:
                if cat["tint"] == "none":
                    cat["tint"] = None
            if "white_patches_tint" in cat:
                if cat["white_patches_tint"] == "none":
                    cat["white_patches_tint"] = None

            if "pattern" in cat:
                cat["tortie_marking"] = cat["pattern"]
                del cat["pattern"]

            new_cat.pelt = Pelt(
                name=cat["pelt_name"],
                length=cat["pelt_length"],
                colour=cat["pelt_color"],
                eye_color=cat["eye_colour"],
                eye_colour2=cat["eye_colour2"] if "eye_colour2" in cat else None,
                paralyzed=cat["paralyzed"],
                kitten_sprite=(
                    cat["sprite_kitten"]
                    if "sprite_kitten" in cat
                    else cat["spirit_kitten"]
                ),
                adol_sprite=(
                    cat["sprite_adolescent"]
                    if "sprite_adolescent" in cat
                    else cat["spirit_adolescent"]
                ),
                adult_sprite=(
                    cat["sprite_adult"]
                    if "sprite_adult" in cat
                    else cat["spirit_adult"]
                ),
                senior_sprite=(
                    cat["sprite_senior"]
                    if "sprite_senior" in cat
                    else cat["spirit_elder"]
                ),
                para_adult_sprite=(
                    cat["sprite_para_adult"] if "sprite_para_adult" in cat else None
                ),
                reverse=cat["reverse"],
                vitiligo=cat["vitiligo"] if "vitiligo" in cat else None,
                points=cat["points"] if "points" in cat else None,
                white_patches_tint=(
                    cat["white_patches_tint"]
                    if "white_patches_tint" in cat
                    else "offwhite"
                ),
                white_patches=cat["white_patches"],
                tortie_base=cat["tortie_base"],
                tortie_colour=cat["tortie_color"],
                tortie_pattern=cat["tortie_pattern"],
                tortie_marking=cat["tortie_marking"],
                skin=cat["skin"],
                tint=cat["tint"] if "tint" in cat else None,
                scars=cat["scars"] if "scars" in cat else [],
                accessory=cat["accessory"],
                opacity=cat["opacity"] if "opacity" in cat else 100,
            )

            # Runs a bunch of appearance-related conversion of old stuff.
            new_cat.pelt.check_and_convert(convert)

            # converting old specialty saves into new scar parameter
            if "specialty" in cat or "specialty2" in cat:
                if cat["specialty"] is not None:
                    new_cat.pelt.scars.append(cat["specialty"])
                if cat["specialty2"] is not None:
                    new_cat.pelt.scars.append(cat["specialty2"])

            new_cat.adoptive_parents = (
                cat["adoptive_parents"] if "adoptive_parents" in cat else []
            )

            new_cat.genderalign = cat["gender_align"]
            new_cat.pronouns = (
                cat["pronouns"]
                if "pronouns" in cat
                else {i18n.config.get("locale"): get_new_pronouns(new_cat.genderalign)}
            )
            new_cat.backstory = cat["backstory"] if "backstory" in cat else None
            if new_cat.backstory in BACKSTORIES["conversion"]:
                new_cat.backstory = BACKSTORIES["conversion"][new_cat.backstory]
            new_cat.birth_cooldown = (
                cat["birth_cooldown"] if "birth_cooldown" in cat else 0
            )
            new_cat.moons = cat["moons"]

            if "facets" in cat and cat["facets"] is not None:
                facets = [int(i) for i in cat["facets"].split(",")]
                new_cat.personality = Personality(
                    trait=cat["trait"],
                    kit_trait=new_cat.age in ["newborn", "kitten"],
                    lawful=facets[0],
                    social=facets[1],
                    aggress=facets[2],
                    stable=facets[3],
                )
            else:
                new_cat.personality = Personality(
                    trait=cat["trait"], kit_trait=new_cat.age in ["newborn", "kitten"]
                )

            new_cat.mentor = cat["mentor"]
            new_cat.former_mentor = (
                cat["former_mentor"] if "former_mentor" in cat else []
            )
            new_cat.patrol_with_mentor = (
                cat["patrol_with_mentor"] if "patrol_with_mentor" in cat else 0
            )
            new_cat.no_kits = cat["no_kits"]
            new_cat.no_mates = cat["no_mates"] if "no_mates" in cat else False
            new_cat.no_retire = cat["no_retire"] if "no_retire" in cat else False

            if "skill_dict" in cat:
                new_cat.skills = CatSkills(cat["skill_dict"])
            elif "skill" in cat:
                if new_cat.backstory is None:
                    if "skill" == "formerly a loner":
                        backstory = choice(["loner1", "loner2", "rogue1", "rogue2"])
                        new_cat.backstory = backstory
                    elif "skill" == "formerly a kittypet":
                        backstory = choice(["kittypet1", "kittypet2"])
                        new_cat.backstory = backstory
                    else:
                        new_cat.backstory = "clanborn"
                new_cat.skills = CatSkills.get_skills_from_old(
                    cat["skill"], new_cat.status.rank, new_cat.age
                )

            new_cat.mate = cat["mate"] if type(cat["mate"]) is list else [cat["mate"]]
            if None in new_cat.mate:
                new_cat.mate = [i for i in new_cat.mate if i is not None]
            new_cat.previous_mates = (
                cat["previous_mates"] if "previous_mates" in cat else []
            )

            # checking for old dead
            if (
                cat.get("dead")
                or cat.get("df")
                or cat.get("driven_out")
                or cat.get("exiled")
                or cat.get("outside")
            ):
                if cat.get("dead") and (
                    not new_cat.status.group or not new_cat.status.group.is_afterlife()
                ):
                    if cat.get("df"):
                        new_cat.status.send_to_afterlife(target=CatGroup.DARK_FOREST)
                    elif cat.get("outside"):
                        new_cat.status.send_to_afterlife(
                            target=CatGroup.UNKNOWN_RESIDENCE
                        )
                    else:
                        new_cat.status.send_to_afterlife(target=CatGroup.STARCLAN)

                else:
                    # these should properly change the cat's status to align with old bool info
                    if cat.get("exiled"):
                        new_cat.status.exile_from_group()
                    elif cat.get("outside") and not new_cat.status.is_outsider:
                        new_cat.status.become_lost()

                    if cat.get("driven_out"):
                        new_cat.status.change_group_nearness(CatGroup.PLAYER_CLAN)

            new_cat.dead_for = cat["dead_moons"]
            new_cat.experience = cat["experience"]
            new_cat.apprentice = cat["current_apprentice"]
            new_cat.former_apprentices = cat["former_apprentices"]

            new_cat.faded_offspring = (
                cat["faded_offspring"] if "faded_offspring" in cat else []
            )
            new_cat.prevent_fading = (
                cat["prevent_fading"] if "prevent_fading" in cat else False
            )
            new_cat.favourite = cat["favourite"] if "favourite" in cat else False

            if "died_by" in cat or "scar_event" in cat or "mentor_influence" in cat:
                new_cat.convert_history(
                    cat["died_by"] if "died_by" in cat else [],
                    cat["scar_event"] if "scar_event" in cat else [],
                )

            all_cats.append(new_cat)

        except KeyError as e:
            if "ID" in cat:
                key = f" ID #{cat['ID']} "
            else:
                key = f" at index {i} "
            switch_set_value(
                Switch.error_message, f"Cat{key}in clan_cats.json is missing {e}!"
            )
            switch_set_value(Switch.traceback, e)
            raise

    # replace cat ids with cat objects and add other needed variables
    other_clan_cats = [c for c in Cat.all_cats_list if c.status.is_other_clancat]
    for cat in all_cats:
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

        cat.inheritance = Inheritance(cat)

        try:
            # initialization of thoughts
            cat.thoughts(other_clan_cats=other_clan_cats)
        except Exception as e:
            logger.exception(
                f"There was an error when thoughts for cat #{cat} are created."
            )
            switch_set_value(
                Switch.error_message,
                f"There was an error when thoughts for cat #{cat} are created.",
            )
            switch_set_value(Switch.traceback, e)
            raise

        # Save integrety checks
        if constants.CONFIG["save_load"]["load_integrity_checks"]:
            save_check()


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
                the_cat = Cat(
                    ID=attr[0],
                    prefix=attr[1].split(":")[0],
                    suffix=attr[1].split(":")[1],
                    gender=attr[2],
                    status={"rank": attr[3]},
                    pelt=the_pelt,
                    parent1=attr[6],
                    parent2=attr[7],
                )

                switch_set_value(
                    Switch.error_message,
                    f"There was an error loading cat # {str(attr[0])} (code: 3)",
                )
                the_cat.age, the_cat.mentor = attr[4], attr[8]
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
                    the_cat.pelt.accessory = [attr[28]]
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
                        the_cat.status.send_to_afterlife(target=CatGroup.STARCLAN)
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

    if version < 3 and game.clan.freshkill_pile:
        # freshkill start for older clans
        add_prey = game.clan.freshkill_pile.amount_food_needed() * 2
        game.clan.freshkill_pile.add_freshkill(add_prey)
