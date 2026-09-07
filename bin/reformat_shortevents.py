import os

import ujson
import re

from scripts.cat.enums import CatRank, CatAge
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
    RequiredReputationDict,
)

root_dir = "../resources/lang/en/events"
folders = ["death", "injury", "misc", "new_cat"]
file_set = set()


def load_paths():
    for folder in folders:
        for dir_, _, files in os.walk(f"{root_dir}/{folder}"):
            for file_name in files:
                rel_dir = os.path.relpath(dir_, root_dir)
                rel_file = os.path.join(rel_dir, file_name)
                if "death_reactions" in rel_file:
                    continue
                if "outsider_deaths" in rel_file:
                    continue
                if "murder" in rel_file:
                    continue
                if os.path.splitext(rel_file)[-1].lower() == ".json":
                    file_set.add(f"{rel_file}")


def reformat():
    for path in file_set:
        new_events = []
        try:
            with open(f"{root_dir}/{path}", "r") as read_file:
                events = read_file.read()
                event_dict = ujson.loads(events)

        except:
            print(f"Something went wrong with {path}")
            continue

        for e in event_dict:
            if isinstance(e, str):
                continue

            reformatted_event = {
                "event_id": e.get("event_id"),
                "frequency": e.get("frequency"),
            }
            if e.get("location") and e.get("location") != "any":
                reformatted_event["location"] = e.get("location")
            if e.get("season") and e.get("season") != "any":
                reformatted_event["season"] = e.get("season")
            reformatted_event["tags"] = e.get("tags", [])
            if e.get("sub_type"):
                reformatted_event["tags"].extend(e["sub_type"])
            if e.get("poi"):
                reformatted_event["poi"] = e["poi"]

            required_reputation = RequiredReputationDict()
            if e.get("outsider", {}).get("current_rep"):
                required_reputation["outsider"] = e["outsider"]["current_rep"]
            if e.get("other_clan", {}).get("current_rep"):
                required_reputation["other_clan"] = e["other_clan"]["current_rep"]

            reformatted_event["strings"] = [e.get("event_text")]

            involved_cats = {}
            relationship_constraints = None
            if e.get("m_c"):
                new_dict, relationship_status = get_involved_cat_info(e["m_c"])
                involved_cats.update({"m_c": new_dict})
                if relationship_status:
                    relationship_constraints = RelationshipConstraintDict(
                        cats_from=["m_c"],
                        cats_to=["r_c"],
                        mutual=False,
                        constraints=relationship_status,
                    )
            if e.get("r_c"):
                new_dict, relationship_status = get_involved_cat_info(e["r_c"])
                involved_cats.update({"r_c": new_dict})
                if relationship_status:
                    if relationship_constraints:
                        relationship_constraints["mutual"] = True
                        relationship_constraints["constraints"].extend(
                            relationship_status
                        )
                    else:
                        relationship_constraints = RelationshipConstraintDict(
                            cats_from=["r_c"],
                            cats_to=["m_c"],
                            mutual=False,
                            constraints=relationship_status,
                        )
            if relationship_constraints:
                reformatted_event["relationship_constraints"] = relationship_constraints

            new_cats_joining = []
            new_cat_death_dict = None
            if e.get("new_cat"):
                for i, attr_list in enumerate(e["new_cat"]):
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
                            parent_match
                            or adoptive_match
                            or mate_match
                            or tag == "litter"
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
                            cat_dict["can_create_new_cat"][
                                "assign_mate"
                            ] = final_mate_list

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
                            if clean_tag in (
                                CatRank.APPRENTICE,
                                CatRank.MEDICINE_APPRENTICE,
                            ):
                                cat_dict["age"] = [CatAge.ADOLESCENT]
                            join_dict["new_status"] = [clean_tag]

                        elif age_match:
                            age_tag = tag.replace("age:", "")
                            if age_tag != "mate":
                                if age_tag == "has_kits":
                                    cat_dict["age"] = [
                                        CatAge.ADULT,
                                        CatAge.SENIOR_ADULT,
                                    ]
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

            if involved_cats:
                reformatted_event["involved_cats"] = involved_cats

            if e.get("exclude_involved"):
                reformatted_event["hide_involved"] = e["exclude_involved"]

            if e.get("relationships"):
                reformatted_event["relationship_changes"] = e.get("relationships")

            reputation_changes = ReputationChangesDict()
            if e.get("outsider"):
                if e["outsider"].get("changed"):
                    reputation_changes["outsider"] = e["outsider"]["changed"]
            if e.get("other_clan"):
                if e["other_clan"].get("changed"):
                    reputation_changes["other_clan"] = e["other_clan"]["changed"]

            if new_cats_joining:
                reformatted_event["join"] = new_cats_joining

            if e.get("new_gender"):
                reformatted_event["new_gender"] = e["new_gender"]
            if e.get("new_accessory"):
                reformatted_event["gain_accessory"] = {
                    "cats": ["m_c"],
                    "accessory": e["new_accessory"],
                }

            scar_history = {}
            if e.get("history"):
                death_list = []
                for block in e["history"]:
                    if block.get("death"):
                        new_block = DeathDict(
                            cats=block["cats"], history=block["death"]
                        )
                        if "no_body" in reformatted_event["tags"]:
                            new_block["body"] = False
                            reformatted_event["tags"].remove("no_body")

                        death_list.append(new_block)

                    if block.get("scar"):
                        scar_history.update({c: block["scar"] for c in block["cats"]})

                if death_list:
                    reformatted_event["death"] = death_list

            if e.get("injury"):
                reformatted_event["condition"] = []
                for block in e["injury"]:
                    new_block = ConditionDict(
                        cats=block["cats"],
                        condition=block["injuries"],
                    )
                    if block.get("scars"):
                        new_block["scar_pool_override"] = block["scars"]

                    if scar_history:
                        new_block["scar_history"] = scar_history.get(
                            block["cats"][0], ""
                        )

                    reformatted_event["condition"].append(new_block)

            if e.get("supplies"):
                reformatted_event["supply"] = e["supplies"]

            if e.get("future_event"):
                reformatted_event["future_event"] = e["future_event"]

            new_events.append(reformatted_event)

        dict_text = ujson.dumps(new_events, indent=4)
        dict_text = dict_text.replace(
            "\/", "/"
        )  # ujson tries to escape "/", but doesn't end up doing a good job.

        with open(f"{root_dir}/{path}", "w") as write_file:
            write_file.write(dict_text)


def get_involved_cat_info(e) -> tuple[InvolvedCatDict, list]:
    old_dict = e
    new_dict = InvolvedCatDict()
    relationship_change = []
    if old_dict.get("age") and "any" not in old_dict["age"]:
        new_dict["age"] = old_dict["age"]
    if old_dict.get("status") and "any" not in old_dict["status"]:
        new_dict["status"] = old_dict["status"]
    if old_dict.get("group"):
        new_dict["group"] = old_dict["group"]
    stat_dict = StatDict()
    if old_dict.get("skill"):
        stat_dict["skill"] = old_dict["skill"]
    if old_dict.get("trait"):
        stat_dict["trait"] = old_dict["trait"]
    if stat_dict.get("trait") and stat_dict.get("skill"):
        stat_dict["must_have_both"] = True
    if stat_dict:
        new_dict["stat"] = stat_dict
    if old_dict.get("backstory"):
        new_dict["backstory"] = old_dict["backstory"]
    if old_dict.get("gender"):
        new_dict["gender"] = old_dict["gender"]
    if old_dict.get("relationship_status"):
        relationship_change = old_dict["relationship_status"]

    return new_dict, relationship_change


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


load_paths()
reformat()
