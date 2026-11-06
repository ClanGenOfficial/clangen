import os

import ujson
import re

from scripts.cat.enums import CatAge, CatRank
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    StatDict,
    CanCreateNewCatDict,
    JoinDict,
    DeathDict,
    SupplyDict,
    ConditionDict,
    LostDict,
    ReputationChangesDict,
    RelationshipConstraintDict,
)

"""
I'm preserving this file for future reference and modder usage, if modders so desire.

Modders please note that this script does not convert patrols perfectly. 
It does its best and it gets the majority of the work done, however our prior patrol format was extremely lenient 
compared to the newer format. This makes it difficult to track things like inconsistent abbreviation usage. I had to 
fix a lot of patrols by hand. I recommend you preserve the already-fixed vanilla patrols and convert your modded patrols
 specifically, then add those modded patrols back into the correct files after you have corrected any problems. This 
 way you do not have to manually fix all the vanilla patrols as well (i already went through hell for you).
"""


root_dir = "../resources/lang/en/patrols"
file_set = set()


def load_paths():
    for dir_, _, files in os.walk(root_dir):
        for file_name in files:
            rel_dir = os.path.relpath(dir_, root_dir)
            rel_file = os.path.join(rel_dir, file_name)
            if os.path.splitext(rel_file)[-1].lower() == ".json":
                file_set.add(rel_file)


def reformat():
    for path in file_set:
        new_patrols = []
        try:
            if path == ".\\prey_text_replacements.json":
                continue
            with open(f"{root_dir}/{path}", "r") as read_file:
                patrols = read_file.read()
                patrol_dict = ujson.loads(patrols)

        except:
            print(f"Something went wrong with {path}")
            continue

        for p in patrol_dict:
            all_mentored = False
            specific_mentored = []

            if isinstance(p, str):
                continue

            reformatted_patrol = {"id": p.get("patrol_id")}
            medicine_cat_allowed = False
            if p.get("types"):
                reformatted_patrol["types"] = p.get("types")
                if "herb_gathering" in reformatted_patrol["types"]:
                    medicine_cat_allowed = True

            if p.get("frequency"):
                reformatted_patrol["frequency"] = p.get("frequency")
            if p.get("biome"):
                if "any" not in p["biome"]:
                    reformatted_patrol["location"] = p.get("biome")
            if p.get("season"):
                if "any" not in p["season"]:
                    reformatted_patrol["season"] = p.get("season")

            # TAGGING
            if p.get("tags"):
                preserved_tags = []
                for tag in p["tags"]:
                    if tag == "rom_two_apps":
                        if "romance" not in p["tags"]:
                            preserved_tags.append(tag)
                        continue
                    if tag == "all_mentored":
                        all_mentored = True
                        continue
                    if "mentored" in tag:
                        specific_mentored.append(
                            tag.replace("_mentored", "").replace("app", "")
                        )
                        continue
                    if tag == "new_cat":
                        continue
                    preserved_tags.append(tag)
                reformatted_patrol["tags"] = preserved_tags

            if p.get("poi"):
                reformatted_patrol["poi"] = p.get("poi")

            required_cat_types = {
                "patrol_cats": [p.get("min_cats", 1), p.get("max_cats", 6)]
            }
            if p.get("min_max_status"):
                required_cat_types.update(p.get("min_max_status"))

            reformatted_patrol["required_cat_types"] = required_cat_types

            involved_cats = {}
            if p.get("pl_skill_constraint") or p.get("pl_trait_constraints"):
                involved_cats["p_l"] = InvolvedCatDict(
                    stat=StatDict(
                        skill=p.get("pl_skill_constraint", []),
                        trait=p.get("pl_trait_constraints", []),
                    )
                )

            if p.get("relationship_constraint"):
                reformatted_patrol["relationship_constraint"] = [
                    {
                        "cats_from": ["p_l"],
                        "cats_to": ["patrol_cats"],
                        "mutual": False,
                        "constraints": p.get("relationship_constraint"),
                    }
                ]

            text_to_search = p.get("intro_text") + p.get("decline_text")
            if "r_c" in text_to_search and p.get("max_cats") != 1:
                involved_cats["r_c"] = {}
            for i in range(0, 7):
                if f"app{i}" in text_to_search:
                    rank_list = [CatRank.APPRENTICE]
                    if medicine_cat_allowed:
                        rank_list.append(CatRank.MEDICINE_APPRENTICE)
                    involved_cats[f"r_c{i}"] = InvolvedCatDict(status=rank_list)
                    if all_mentored or str(i) in specific_mentored:
                        involved_cats[f"r_c{i}"]["has_mentor"] = True

            reformatted_patrol["involved_cats"] = involved_cats

            reformatted_patrol["chance_of_success"] = p.get("chance_of_success")
            if p.get("patrol_art"):
                reformatted_patrol["patrol_art"] = p.get("patrol_art")
            if p.get("patrol_art_clean"):
                reformatted_patrol["patrol_art_clean"] = p.get("patrol_art_clean")

            replace_rc_to_pl = False
            if p.get("max_cats") == 1 and "r_c" in p.get("intro_text"):
                replace_rc_to_pl = True
                p["intro_text"] = p["intro_text"].replace("r_c", "p_l")
            for i in range(0, 7):
                if f"app{i}" in p["intro_text"]:
                    if p.get("max_cats") == 1:
                        replace_rc_to_pl = True
                        p["intro_text"] = p["intro_text"].replace(f"app{i}", f"p_l")
                        if f"r_c{i}" in reformatted_patrol["involved_cats"]:
                            reformatted_patrol["involved_cats"][
                                "p_l"
                            ] = reformatted_patrol["involved_cats"][f"r_c{i}"]
                            reformatted_patrol["involved_cats"].pop(f"r_c{i}")
                    else:
                        p["intro_text"] = p["intro_text"].replace(f"app{i}", f"r_c{i}")
            reformatted_patrol["intro_text"] = p.get("intro_text")
            if p.get("max_cats") == 1 and "r_c" in p.get("decline_text"):
                replace_rc_to_pl = True
                p["decline_text"] = p["decline_text"].replace("r_c", "p_l")
            for i in range(0, 7):
                if f"app{i}" in p["decline_text"]:
                    if p.get("max_cats") == 1:
                        replace_rc_to_pl = True
                        p["decline_text"] = p["decline_text"].replace(f"app{i}", f"p_l")
                        if f"r_c{i}" in reformatted_patrol["involved_cats"]:
                            reformatted_patrol["involved_cats"][
                                "p_l"
                            ] = reformatted_patrol["involved_cats"][f"r_c{i}"]
                            reformatted_patrol["involved_cats"].pop(f"r_c{i}")
                    else:
                        p["decline_text"] = p["decline_text"].replace(
                            f"app{i}", f"r_c{i}"
                        )
            reformatted_patrol["decline_text"] = p.get("decline_text")

            reformatted_patrol["success_outcomes"] = []
            for outcome in p["success_outcomes"]:
                reformatted_patrol["success_outcomes"].append(
                    reformat_outcome(
                        outcome,
                        reformatted_patrol["involved_cats"],
                        replace_rc_to_pl,
                        medicine_cat_allowed,
                    )
                )

            reformatted_patrol["fail_outcomes"] = []
            for outcome in p["fail_outcomes"]:
                reformatted_patrol["fail_outcomes"].append(
                    reformat_outcome(
                        outcome,
                        reformatted_patrol["involved_cats"],
                        replace_rc_to_pl,
                        medicine_cat_allowed,
                    )
                )

            if p.get("antag_success_outcomes"):
                reformatted_patrol["antag_success_outcomes"] = []
                for outcome in p["antag_success_outcomes"]:
                    reformatted_patrol["antag_success_outcomes"].append(
                        reformat_outcome(
                            outcome,
                            reformatted_patrol["involved_cats"],
                            replace_rc_to_pl,
                            medicine_cat_allowed,
                        )
                    )
            if p.get("antag_fail_outcomes"):
                reformatted_patrol["antag_fail_outcomes"] = []
                for outcome in p["antag_fail_outcomes"]:
                    reformatted_patrol["antag_fail_outcomes"].append(
                        reformat_outcome(
                            outcome,
                            reformatted_patrol["involved_cats"],
                            replace_rc_to_pl,
                            medicine_cat_allowed,
                        )
                    )

            if not reformatted_patrol["involved_cats"]:
                reformatted_patrol.pop("involved_cats")
            new_patrols.append(reformatted_patrol)

        dict_text = ujson.dumps(new_patrols, indent=4)
        dict_text = dict_text.replace(
            "\/", "/"
        )  # ujson tries to escape "/", but doesn't end up doing a good job.

        with open(f"{root_dir}/{path}", "w") as write_file:
            write_file.write(dict_text)


def reformat_outcome(
    outcome: dict,
    already_involved_cats: dict,
    replace_name: bool,
    medicine_cat_allowed: bool,
) -> dict:
    reformatted_outcome = {"tags": [], "frequency": outcome.get("frequency")}

    if outcome.get("art"):
        reformatted_outcome["outcome_art"] = outcome.get("art")
    if outcome.get("art_clean"):
        reformatted_outcome["outcome_art_clean"] = outcome.get("art_clean")

    if replace_name:
        outcome["text"] = outcome["text"].replace("r_c", "p_l")

    reformatted_outcome["strings"] = [outcome.get("text")]

    if outcome.get("min_max_status"):
        reformatted_outcome["required_cat_types"] = outcome.get("min_max_status")

    text_to_search = outcome.get("text")
    involved_cats = {}
    if "r_c" in text_to_search and "r_c" not in already_involved_cats:
        involved_cats["r_c"] = {}
    for i in range(0, 7):
        if f"app{i}" in text_to_search and f"app{i}" not in already_involved_cats:
            if replace_name:
                reformatted_outcome["strings"][0] = outcome["text"].replace(
                    f"app{i}", f"p_l"
                )
            else:
                reformatted_outcome["strings"][0] = outcome["text"].replace(
                    f"app{i}", f"r_c{i}"
                )
            rank_list = [CatRank.APPRENTICE]
            if medicine_cat_allowed:
                rank_list.append(CatRank.MEDICINE_APPRENTICE)
            involved_cats[f"r_c{i}"] = InvolvedCatDict(status=rank_list)

    if "s_c" in text_to_search:
        can_have_stat = outcome.get("can_have_stat")
        stat = StatDict()
        if outcome.get("stat_skill"):
            stat["skill"] = outcome.get("stat_skill")
        if outcome.get("stat_trait"):
            stat["trait"] = outcome.get("stat_trait")
        if stat.get("trait") and stat.get("skill"):
            stat["must_have_both"] = True

        if not can_have_stat or "any" in can_have_stat:
            involved_cats["s_c"] = InvolvedCatDict(
                prior_abbreviation=["any"], stat=stat
            )
        else:
            prior_abbreviations = []
            if "p_l" in can_have_stat:
                prior_abbreviations.append("p_l")
            if "r_c" in can_have_stat:
                prior_abbreviations.append("r_c")

            for i in range(0, 7):
                if f"app{i}" in can_have_stat:
                    prior_abbreviations.append(f"r_c{i}")

            if "not_pl_rc" in can_have_stat:
                prior_abbreviations.extend(["-p_l", "-r_c"])
            if "not_pl" in can_have_stat:
                prior_abbreviations.append("-p_l")
            if "not_rc" in can_have_stat:
                prior_abbreviations.append("-r_c")

            involved_cats["s_c"] = InvolvedCatDict(stat=stat)
            if prior_abbreviations:
                involved_cats["s_c"]["prior_abbreviations"] = prior_abbreviations

    new_cats_joining = []
    new_cat_death_dict = None
    if outcome.get("new_cat"):
        for i, attr_list in enumerate(outcome["new_cat"]):
            join_dict = JoinDict(cats=[])
            cat_abbr = f"n_c:{i}"
            cat_dict = InvolvedCatDict()
            if "meeting" not in attr_list:
                join_dict["cats"].append(cat_abbr)
            if "dead" in attr_list:
                if not new_cat_death_dict:
                    new_cat_death_dict = DeathDict(
                        cats=[],
                        history="This cat died while wandering.",
                        no_results="unknown" in attr_list,
                    )
                new_cat_death_dict["cats"].append(cat_abbr)
            if "exists" not in attr_list:
                cat_dict["can_create_new_cat"] = CanCreateNewCatDict()

            for tag in attr_list:
                parent_match = re.match(r"parent:([,0-9]+)", tag)
                adoptive_match = re.match(r"adoptive:(.+)", tag)
                mate_match = re.match(r"mate:([_,0-9a-zA-Z]+)", tag)
                rank_match = re.match(r"status:(.+)", tag)
                age_match = re.match(r"age:(.+)", tag)
                backstory_match = re.match(r"backstory:(.+)", tag)

                if (
                    parent_match or adoptive_match or mate_match or tag == "litter"
                ) and "can_create_new_cat" not in cat_dict:
                    cat_dict["can_create_new_cat"] = CanCreateNewCatDict()

                if parent_match:
                    clean_tag = tag.replace("parent:", "")
                    parent_tag_list = clean_tag.split(",")
                    final_parent_list = []
                    for p in parent_tag_list:
                        if p.isdigit():
                            final_parent_list.append(f"n_c:{p}")
                        else:
                            final_parent_list.append(p)

                    cat_dict["can_create_new_cat"][
                        "assign_blood_parent"
                    ] = final_parent_list
                elif adoptive_match:
                    clean_tag = tag.replace("adoptive:", "")
                    parent_tag_list = clean_tag.split(",")
                    final_parent_list = []
                    for p in parent_tag_list:
                        if p.isdigit():
                            final_parent_list.append(f"n_c:{p}")
                        else:
                            final_parent_list.append(p)

                    cat_dict["can_create_new_cat"][
                        "assign_adoptive_parent"
                    ] = final_parent_list
                elif mate_match:
                    clean_tag = tag.replace("mate:", "")
                    mate_tag_list = clean_tag.split(",")
                    final_mate_list = []
                    for p in mate_tag_list:
                        if p.isdigit():
                            final_mate_list.append(f"n_c:{p}")
                        else:
                            final_mate_list.append(p)
                    cat_dict["can_create_new_cat"]["assign_mate"] = final_mate_list

                elif tag == "litter":
                    cat_dict["can_create_new_cat"]["become_litter"] = True

                elif tag == "male" or tag == "female" or tag == "can_birth":
                    cat_dict["gender"] = tag

                elif tag == "new_name":
                    join_dict["change_name"] = True
                elif tag == "old_name":
                    join_dict["change_name"] = False

                elif rank_match:
                    clean_tag = tag.replace("status:", "")
                    if (
                        clean_tag in (CatRank.NEWBORN, CatRank.KITTEN)
                        and not "age" in cat_dict
                    ):
                        cat_dict["age"] = [clean_tag]
                    if (
                        clean_tag in (CatRank.WARRIOR, CatRank.MEDICINE_CAT)
                        and not "age" in cat_dict
                    ):
                        cat_dict["age"] = [
                            CatAge.ADULT,
                            CatAge.YOUNG_ADULT,
                            CatAge.SENIOR_ADULT,
                        ]
                    if clean_tag in (CatRank.APPRENTICE, CatRank.MEDICINE_APPRENTICE):
                        cat_dict["age"] = [CatAge.ADOLESCENT]
                    join_dict["new_status"] = [clean_tag]

                elif age_match:
                    age_tag = tag.replace("age:", "")
                    if age_tag != "mate":
                        if age_tag == "has_kits":
                            cat_dict["age"] = [CatAge.ADULT, CatAge.SENIOR_ADULT]
                        else:
                            cat_dict["age"] = [age_tag]

                elif tag in ("kittypet", "rogue", "loner", "clancat"):
                    if not cat_dict.get("status"):
                        cat_dict["status"] = [tag]
                    else:
                        cat_dict["status"].append(tag)
                elif tag == "former clancat":
                    cat_dict["past_status"] = ["clancat"]

                elif backstory_match:
                    bs_tags = tag.replace("backstory:", "")
                    tag_list = bs_tags.split(",")
                    cat_dict["backstory"] = tag_list

            involved_cats[cat_abbr] = cat_dict

            new_cats_joining.append(join_dict)

    reformatted_outcome["involved_cats"] = involved_cats

    if outcome.get("relationship_constraint"):
        reformatted_outcome["relationship_constraint"] = [
            {
                "cats_from": ["p_l"],
                "cats_to": ["patrol_cats"],
                "mutual": False,
                "constraints": outcome.get("relationship_constraint"),
            }
        ]

    reformatted_outcome["exp_gained"] = outcome.get("exp")

    reputation_changes = ReputationChangesDict()
    if outcome.get("outsider_rep"):
        reputation_changes["outsider"] = outcome.get("outsider_rep")
    if outcome.get("other_clan_rep"):
        reputation_changes["other_clan"] = outcome.get("other_clan_rep")
    if reputation_changes:
        reformatted_outcome["reputation_changes"] = reputation_changes

    if outcome.get("relationships"):
        reformatted_outcome["relationship_changes"] = outcome.get("relationships")

    if outcome.get("prey"):
        reformatted_outcome["supply"] = []
        for prey in outcome["prey"]:
            if prey == "very_small":
                prey = "tiny"
            reformatted_outcome["supply"].append(
                SupplyDict(type="freshkill", adjust=f"increase_{prey}")
            )
    if outcome.get("herbs"):
        reformatted_outcome["supply"] = []
        many_herb = "many_herbs" in outcome["herbs"]
        for herb in outcome["herbs"]:
            if herb == "many_herbs":
                many_herb = True
                continue
            reformatted_outcome["supply"].append(
                SupplyDict(
                    type=herb,
                    adjust=f"increase_medium" if not many_herb else "increase_huge",
                )
            )

    if outcome.get("dead_cats"):
        death_dict = DeathDict(
            cats=[],
            history=outcome.get("history_text", {}).get("death", ""),
        )
        for c in outcome["dead_cats"]:
            if c in ("some_lives", "all_lives"):
                if not reformatted_outcome.get("tags"):
                    reformatted_outcome["tags"] = [c]
                else:
                    reformatted_outcome["tags"].append(c)
                continue
            for i in range(0, 7):
                if f"app{i}" == c:
                    death_dict["cats"].append(f"r_c{i}")
                    continue
            death_dict["cats"].append(c)

        reformatted_outcome["death"] = [death_dict]

    if new_cat_death_dict:
        if not reformatted_outcome.get("death"):
            reformatted_outcome["death"] = [new_cat_death_dict]
        else:
            reformatted_outcome["death"].append(new_cat_death_dict)

    if outcome.get("injury"):
        reformatted_outcome["injury"] = []
        for injury in outcome["injury"]:
            non_lethal = False
            if "non_lethal" in injury["injuries"]:
                non_lethal = True
                injury["injuries"].remove("non_lethal")

            cat_list = []
            for c in injury["cats"]:
                name_change = False
                for i in range(0, 7):
                    if f"app{i}" == c:
                        cat_list.append(f"r_c{i}")
                        name_change = True
                if not name_change:
                    cat_list.append(c)

            injury_dict = ConditionDict(
                cats=cat_list,
                condition=injury["injuries"],
            )
            if non_lethal:
                injury_dict["non_lethal"] = True
            if injury.get("scars"):
                injury_dict["scar_pool_override"] = injury["scars"]
            if injury.get("no_results"):
                injury_dict["no_results"] = injury["no_results"]
            if outcome.get("history_text"):
                scar_history = outcome["history_text"].get("scar")
                death_history = outcome["history_text"].get("death")
                if scar_history:
                    injury_dict["scar_history"] = scar_history
                if death_history:
                    injury_dict["death_history"] = death_history

            reformatted_outcome["injury"].append(injury_dict)

    if outcome.get("lost_cats"):
        cat_list = []
        for c in outcome["lost_cats"]:
            name_change = False
            for i in range(0, 7):
                if f"app{i}" == c:
                    cat_list.append(f"r_c{i}")
                    name_change = True
                    continue
            if not name_change:
                cat_list.append(c)
        reformatted_outcome["lost"] = [LostDict(cats=cat_list)]

    if new_cats_joining:
        reformatted_outcome["join"] = new_cats_joining

    if not reformatted_outcome["tags"]:
        reformatted_outcome.pop("tags")
    if not reformatted_outcome["involved_cats"]:
        reformatted_outcome.pop("involved_cats")

    return reformatted_outcome


def second_reformat():
    for path in file_set:
        new_patrols = []
        try:
            if path == ".\\prey_text_replacements.json":
                continue
            with open(f"{root_dir}/{path}", "r") as read_file:
                patrols = read_file.read()
                patrol_dict = ujson.loads(patrols)

        except:
            print(f"Something went wrong with {path}")
            continue

        for p in patrol_dict:
            # reformatted_patrol = check_romance(p)

            for outcome in (
                p.get("success_outcomes")
                + p.get("fail_outcomes")
                + p.get("antag_success_outcomes", [])
                + p.get("antag_fail_outcomes", [])
            ):
                for abbr, constraints in outcome.get("involved_cats", {}).items():
                    if "n_c" in abbr and not constraints.get("can_create_new_cat"):
                        outcome["involved_cats"][abbr]["can_create_new_cat"] = {}

            reformatted_patrol = p

            new_patrols.append(reformatted_patrol)

        dict_text = ujson.dumps(new_patrols, indent=4)
        dict_text = dict_text.replace(
            "\/", "/"
        )  # ujson tries to escape "/", but doesn't end up doing a good job.

        with open(f"{root_dir}/{path}", "w") as write_file:
            write_file.write(dict_text)


def _check_romance(d: dict):
    reformatted_dict = d.copy()
    if d.get("tags"):
        if "romance" in d["tags"]:
            new_block = RelationshipConstraintDict(
                cats_to=["patrol_cats"],
                cats_from=["patrol_cats"],
                mutual=True,
                constraints=["can_romance"],
            )
            if d.get("relationship_constraint"):
                reformatted_dict["relationship_constraint"].append(new_block)
            else:
                reformatted_dict["relationship_constraint"] = [new_block]
    return reformatted_dict


def check_solo_patrols():
    for path in file_set:
        try:
            if path == ".\\prey_text_replacements.json":
                continue
            with open(f"{root_dir}/{path}", "r") as read_file:
                patrols = read_file.read()
                patrol_dict = ujson.loads(patrols)

        except:
            print(f"Something went wrong with {path}")
            continue

        for p in patrol_dict:
            if p.get("required_cat_types")["patrol_cats"] == [1, 1]:
                for abbr in p.get("involved_cats", {}).keys():
                    if abbr != "p_l" and "s_c" not in abbr:
                        print(p["id"])
                        break
                for outcome in (
                    p.get("success_outcomes")
                    + p.get("fail_outcomes")
                    + p.get("antag_success_outcomes", [])
                    + p.get("antag_fail_outcomes", [])
                ):
                    done = False
                    for abbr in outcome.get("involved_cats", {}).keys():
                        if abbr != "p_l" and "s_c" not in abbr and "n_c" not in abbr:
                            print(p["id"])
                            done = True
                            break
                    if done:
                        break
            elif p.get("required_cat_types")["patrol_cats"][0] == 1:
                for abbr in p.get("involved_cats", {}).keys():
                    if abbr != "p_l" and "s_c" not in abbr:
                        print(p["id"])
                        break
                for outcome in (
                    p.get("success_outcomes")
                    + p.get("fail_outcomes")
                    + p.get("antag_success_outcomes", [])
                    + p.get("antag_fail_outcomes", [])
                ):
                    done = False
                    for abbr in outcome.get("involved_cats", {}).keys():
                        if "r_c" in abbr:
                            print(p["id"])
                            done = True
                            break
                    if done:
                        break


load_paths()
# reformat()
# second_reformat()
check_solo_patrols()
