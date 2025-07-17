import json as ujson
import os
import re

death_beach = []
death_forest = []
death_general = []
death_mountainous = []
death_plains = []
death_wetlands = []
death_desert = []

injury_beach = []
injury_forest = []
injury_general = []
injury_mountainous = []
injury_plains = []
injury_wetlands = []
injury_desert = []

new_beach = []
new_forest = []
new_general = []
new_mountainous = []
new_plains = []
new_wetlands = []
new_desert = []

misc_beach = []
misc_forest = []
misc_general = []
misc_mountainous = []
misc_plains = []
misc_wetlands = []
misc_desert = []


def reformat(path):
    if "Copy" not in path:
        return
    not_allowed = [
        "fresh",
        "nutrition",
        "disasters",
        "ceremony",
        "dislike",
        "jealousy",
        "witness",
        "template",
        "reactions",
        "beach.json",
        "forest.json",
        "new_general.json",
        "mountainous.json",
        "plains.json",
        "wetlands.json",
        "desert.json",
    ]
    for item in not_allowed:
        if item in path:
            return
    try:
        with open(path, "r", encoding="utf-8") as read_file:
            events = read_file.read()
            event_ujson = ujson.loads(events)

    except:
        print(f"Something went wrong with {path}")

    if not event_ujson:
        return

    try:
        if type(event_ujson[0]) != dict:
            print(
                path,
                "is not in the correct event format. It may not be an event .json.",
            )
            return
    except KeyError:
        return

    print(path)

    for event in event_ujson:
        new_format = {
            "event_id": "",
        }

        if "general" not in path:
            new_format["biome"] = []
            if "beach" in path:
                new_format["biome"].append("beach")
            if "forest" in path:
                new_format["biome"].append("forest")
            if "mountainous" in path:
                new_format["biome"].append("mountainous")
            if "plains" in path:
                new_format["biome"].append("plains")
            if "wetlands" in path:
                new_format["biome"].append("wetlands")
            if "desert" in path:
                new_format["biome"].append("desert")

        if "camp" in event:
            new_format["camp"] = []
            new_format["camp"].append(event["camp"])

        if "tags" in event:
            new_format["season"] = []
            if "Greenleaf" in event["tags"]:
                new_format["season"].append("greenleaf")
                event["tags"].remove("Greenleaf")
            if "Green-leaf" in event["tags"]:
                new_format["season"].append("greenleaf")
                event["tags"].remove("Green-leaf")
            if "Newleaf" in event["tags"]:
                new_format["season"].append("newleaf")
                event["tags"].remove("Newleaf")
            if "Leaf-fall" in event["tags"]:
                new_format["season"].append("leaf-fall")
                event["tags"].remove("Leaf-fall")
            if "Leaf-bare" in event["tags"]:
                new_format["season"].append("leaf-bare")
                event["tags"].remove("Leaf-bare")
            if "Leafbare" in event["tags"]:
                new_format["season"].append("leaf-bare")
                event["tags"].remove("Leafbare")

        if new_format["season"] == ["greenleaf", "newleaf", "leaf-fall", "leaf-bare"]:
            new_format["season"] = ["any"]

        new_format["tags"] = []

        new_format["weight"] = 20

        if "event_text" in event:
            new_format["event_text"] = event["event_text"]
        if "death_text" in event:
            new_format["event_text"] = event["death_text"]

        if "accessories" in event:
            new_format["new_accessory"] = event["accessories"]

        new_format["m_c"] = {}
        new_format["m_c"]["age"] = []

        if "kitten" in path:
            new_format["m_c"]["age"].append("kitten")
        if (
            "apprentice" in path
            or "medicine_cat_app" in event["tags"]
            or "mediator" in path
        ):
            new_format["m_c"]["age"].append("adolescent")
        if (
            "warrior" in path
            or "deputy" in path
            or "leader" in path
            or "mediator" in path
        ):
            new_format["m_c"]["age"].append("young adult")
            new_format["m_c"]["age"].append("adult")
            new_format["m_c"]["age"].append("senior adult")
        if "medicine" in path and "medicine_cat_app" not in event["tags"]:
            new_format["m_c"]["age"].append("young adult")
            new_format["m_c"]["age"].append("adult")
            new_format["m_c"]["age"].append("senior adult")
        if (
            "elder" in path
            or "leader" in path
            or "medicine" in path
            or "mediator" in path
        ):
            new_format["m_c"]["age"].append("senior")
        if "elder" in path and "old_age" not in event["tags"]:
            new_format["m_c"]["age"].append("adolescent")
            new_format["m_c"]["age"].append("young adult")
            new_format["m_c"]["age"].append("adult")
            new_format["m_c"]["age"].append("senior adult")

        new_format["m_c"]["status"] = []

        if "kitten" in path:
            new_format["m_c"]["status"].append("kitten")
        if "apprentice" in path:
            new_format["m_c"]["status"].append("apprentice")
        if "medicine_cat_app" in event["tags"]:
            new_format["m_c"]["status"].append("medicine cat apprentice")
            event["tags"].remove("medicine_cat_app")
        if "warrior" in path:
            new_format["m_c"]["status"].append("warrior")
            new_format["m_c"]["status"].append("deputy")
            new_format["m_c"]["status"].append("leader")
        if "deputy" in path and "deputy" not in new_format["m_c"]["status"]:
            new_format["m_c"]["status"].append("deputy")
        if "leader" in path and "leader" not in new_format["m_c"]["status"]:
            new_format["m_c"]["status"].append("leader")
        if "medicine" in path and "medicine_cat_app" not in event["tags"]:
            new_format["m_c"]["status"].append("medicine cat")
            if "medicine_cat" in event["tags"]:
                event["tags"].remove("medicine_cat")
        if "mediator" in path:
            new_format["m_c"]["status"].append("mediator")
            new_format["m_c"]["status"].append("mediator apprentice")
        if "elder" in path:
            new_format["m_c"]["age"].append("elder")

        if "other_cat" in event["tags"]:
            new_format["m_c"]["relationship_status"] = []
            if "other_cat_mate" in event["tags"]:
                event["tags"].remove("other_cat_mate")
                new_format["m_c"]["relationship_status"].append("mates")
            if "other_cat_child" in event["tags"]:
                event["tags"].remove("other_cat_child")
                new_format["m_c"]["relationship_status"].append("parent/child")
            if "other_cat_parent" in event["tags"]:
                event["tags"].remove("other_cat_parent")
                new_format["m_c"]["relationship_status"].append("child/parent")
            if "other_cat_own_app" in event["tags"]:
                event["tags"].remove("other_cat_own_app")
                new_format["m_c"]["relationship_status"].append("mentor/app")
            if "other_cat_mentor" in event["tags"]:
                event["tags"].remove("other_cat_mentor")
                new_format["m_c"]["relationship_status"].append("app/mentor")

        if "cat_skill" in event:
            if event["cat_skill"]:
                new_format["m_c"]["skill"] = event["cat_skill"]
        if "cat_negate_skill" in event:
            if event["cat_negate_skill"]:
                new_format["m_c"]["not_skill"] = event["cat_negate_skill"]
        if "cat_trait" in event:
            if event["cat_trait"]:
                new_format["m_c"]["trait"] = event["cat_trait"]
        if "cat_negate_trait" in event:
            if event["cat_negate_trait"]:
                new_format["m_c"]["not_trait"] = event["cat_negate_trait"]

        if "backstory_constraint" in event:
            if event["backstory_constraint"]:
                new_format["m_c"]["backstory"] = event["backstory_constraint"]

        if "death" in path:
            new_format["m_c"]["dies"] = True

        if "tags" in event:
            for tag in event["tags"]:
                if tag in [
                    "other_cat",
                    "other_cat_kit",
                    "other_cat_med",
                    "other_cat_warrior",
                    "other_cat_dep",
                    "other_cat_leader",
                    "other_cat_app",
                    "other_cat_med_app",
                    "other_cat_elder",
                    "rc_to_mc",
                    "mc_to_rc",
                ]:
                    new_format["r_c"] = {}
                    new_format["r_c"]["age"] = []

                    if "other_cat_kit" in event["tags"]:
                        event["tags"].remove("other_cat_kit")
                        new_format["r_c"]["age"].append("kitten")
                    if "other_cat_app" in event["tags"]:
                        event["tags"].remove("other_cat_app")
                        new_format["r_c"]["age"].append("adolescent")
                    if "other_cat_med_app" in event["tags"]:
                        event["tags"].remove("other_cat_med_app")
                        new_format["r_c"]["age"].append("adolescent")
                    if (
                        "other_cat_warrior" in event["tags"]
                        or "other_cat_leader" in event["tags"]
                        or "other_cat_dep" in event["tags"]
                        or "other_cat_med" in event["tags"]
                        or "other_cat_adult" in event["tags"]
                    ):
                        new_format["r_c"]["age"].append("young adult")
                        new_format["r_c"]["age"].append("adult")
                        new_format["r_c"]["age"].append("senior adult")
                    if "other_cat_med" in event["tags"]:
                        event["tags"].remove("other_cat_med")
                        new_format["r_c"]["age"].append("young adult")
                        new_format["r_c"]["age"].append("adult")
                        new_format["r_c"]["age"].append("senior adult")
                        new_format["r_c"]["age"].append("senior")
                    if (
                        "other_cat_elder" in event["tags"]
                        or "other_cat_leader" in event["tags"]
                    ):
                        new_format["r_c"]["age"].append("senior")
                    if (
                        "other_cat_elder" in event["tags"]
                        and "old_age" not in event["tags"]
                    ):
                        new_format["r_c"]["age"].append("adolescent")
                        new_format["r_c"]["age"].append("young adult")
                        new_format["r_c"]["age"].append("adult")
                        new_format["r_c"]["age"].append("senior adult")

                    if "other_cat_warrior" in event["tags"]:
                        event["tags"].remove("other_cat_warrior")
                    if "other_cat_leader" in event["tags"]:
                        event["tags"].remove("other_cat_leader")
                    if "other_cat_dep" in event["tags"]:
                        event["tags"].remove("other_cat_dep")
                    if "other_cat_med" in event["tags"]:
                        event["tags"].remove("other_cat_med")
                    if "other_cat_adult" in event["tags"]:
                        event["tags"].remove("other_cat_adult")
                    if "other_cat_elder" in event["tags"]:
                        event["tags"].remove("other_cat_elder")

                    new_format["r_c"]["status"] = []

                    if "other_cat_kit" in event["tags"]:
                        event["tags"].remove("other_cat_kit")
                        new_format["r_c"]["status"].append("kitten")
                    if "other_cat_app" in event["tags"]:
                        event["tags"].remove("other_cat_app")
                        new_format["r_c"]["status"].append("apprentice")
                    if "other_cat_med_app" in event["tags"]:
                        event["tags"].remove("other_cat_med_app")
                        new_format["r_c"]["status"].append("medicine cat apprentice")
                    if "other_cat_warrior" in event["tags"]:
                        event["tags"].remove("other_cat_warrior")
                        new_format["r_c"]["status"].append("warrior")
                    if "other_cat_dep" in event["tags"]:
                        event["tags"].remove("other_cat_dep")
                        new_format["r_c"]["status"].append("deputy")
                    if "other_cat_leader" in event["tags"]:
                        event["tags"].remove("other_cat_leader")
                        new_format["r_c"]["status"].append("leader")
                    if "other_cat_med" in event["tags"]:
                        event["tags"].remove("other_cat_med")
                        new_format["r_c"]["status"].append("medicine cat")
                    if "other_cat_elder" in event["tags"]:
                        event["tags"].remove("other_cat_elder")
                        new_format["r_c"]["age"].append("elder")

                    if "other_cat_skill" in event:
                        if event["other_cat_skill"]:
                            new_format["r_c"]["skill"] = event["other_cat_skill"]
                    if "other_cat_negate_skill" in event:
                        if event["other_cat_negate_skill"]:
                            new_format["r_c"]["not_skill"] = event[
                                "other_cat_negate_skill"
                            ]
                    if "other_cat_trait" in event:
                        if event["other_cat_trait"]:
                            new_format["r_c"]["trait"] = event["other_cat_trait"]
                    if "other_cat_negate_trait" in event:
                        if event["other_cat_negate_trait"]:
                            new_format["r_c"]["not_trait"] = event[
                                "other_cat_negate_trait"
                            ]

                    if "multi_death" in event["tags"]:
                        event["tags"].remove("multi_death")
                        new_format["r_c"]["dies"] = True

        if "new_cat" in path:
            new_format["new_cat"] = []
            info = []
            if "new_name" in event:
                if event["new_name"]:
                    info.append("new_name")
                else:
                    info.append("old_name")

            if "kittypet" in event:
                if event["kittypet"]:
                    info.append("kittypet")

            if "loner" in event:
                if event["loner"]:
                    info.append("loner")

            if "clancat" in event:
                if event["clancat"]:
                    info.append("clancat")

            if "litter" in event:
                if event["litter"]:
                    info.append("litter")

            if "new_warrior" in event["tags"]:
                event["tags"].remove("new_warrior")
                info.append("status:{warrior}")
            if "new_app" in event["tags"]:
                event["tags"].remove("new_app")
                info.append("status:{apprentice}")
            if "new_med_app" in event["tags"]:
                event["tags"].remove("new_med_app")
                info.append("status:{medicine cat apprentice}")
            if "new_med" in event["tags"]:
                event["tags"].remove("new_med")
                info.append("status:{medicine cat}")

            new_format["new_cat"].append(info)

        if "injury" in event or "other_cat_injure" in event["tags"]:
            new_format["injury"] = []

            if "injury" in event:
                info = {"cats": ["m_c"], "injuries": []}
                info["injuries"].append(event["injury"])
                if "scar" in event["tags"]:
                    event["tags"].remove("scar")
                    info["scars"] = []
                    scar_list = [
                        "ONE",
                        "TWO",
                        "THREE",
                        "TAILSCAR",
                        "SNOUT",
                        "CHEEK",
                        "SIDE",
                        "THROAT",
                        "TAILBASE",
                        "BELLY",
                        "LEGBITE",
                        "NECKBITE",
                        "FACE",
                        "MANLEG",
                        "BRIGHTHEART",
                        "MANTAIL",
                        "BRIDGE",
                        "RIGHTBLIND",
                        "LEFTBLIND",
                        "BOTHBLIND",
                        "BEAKCHEEK",
                        "BEAKLOWER",
                        "CATBITE",
                        "RATBITE",
                        "QUILLCHUNK",
                        "QUILLSCRATCH",
                        "HINDLEG",
                        "BACK",
                        "QUILLSIDE",
                        "SCRATCHSIDE",
                        "BEAKSIDE",
                        "CATBITETWO",
                        "FOUR",
                        "LEFTEAR",
                        "RIGHTEAR",
                        "NOTAIL",
                        "HALFTAIL",
                        "NOPAW",
                        "NOLEFTEAR",
                        "NORIGHTEAR",
                        "NOEAR",
                        "SNAKE",
                        "TOETRAP",
                        "BURNPAWS",
                        "BURNTAIL",
                        "BURNBELLY",
                        "BURNRUMP",
                        "FROSTFACE",
                        "FROSTTAIL",
                        "FROSTMITT",
                        "FROSTSOCK",
                        "TOE",
                        "SNAKETWO",
                    ]
                    for tag in event["tags"]:
                        if tag in scar_list:
                            info["scars"].append(tag)
                            event["tags"].remove(tag)

                new_format["injury"].append(info)

            if "other_cat_injure" in event["tags"]:
                event["tags"].remove("other_cat_injure")
                info = {"cats": ["r_c"], "injuries": []}
                injuries = [
                    "claw-wound",
                    "bite-wound",
                    "cat bite",
                    "beak bite",
                    "snake bite",
                    "rat bite",
                    "tick bites",
                    "blood loss",
                    "broken jaw",
                    "broken bone",
                    "mangled leg",
                    "dislocated joint",
                    "joint pain",
                    "sprain",
                    "mangled tail",
                    "bruises",
                    "cracked pads",
                    "sore",
                    "phantom pain",
                    "scrapes",
                    "small cut",
                    "torn pelt",
                    "torn ear",
                    "frostbite",
                    "recovering from birth",
                    "water in their lungs",
                    "burn",
                    "severe burn",
                    "shock",
                    "lingering shock",
                    "shivering",
                    "dehydrated",
                    "head damage",
                    "damaged eyes",
                    "quilled by a porcupine",
                    "broken back",
                    "poisoned",
                    "bee sting",
                    "headache",
                    "severe headache",
                    "pregnant",
                ]

                pools = [
                    "battle_injury",
                    "minor_injury",
                    "blunt_force_injury",
                    "hot_injury",
                    "cold_injury",
                    "big_bite_injury",
                    "small_bite_injury",
                    "beak_bite",
                    "rat_bite",
                ]

                for tag in event["tags"]:
                    if tag in injuries:
                        info["injuries"].append(tag)
                        event["tags"].remove(tag)
                    if tag in pools:
                        info["injuries"].append(tag)
                        event["tags"].remove(tag)

                if "scar" in event["tags"]:
                    event["tags"].remove("scar")
                    info["scars"] = []
                    scar_list = [
                        "ONE",
                        "TWO",
                        "THREE",
                        "TAILSCAR",
                        "SNOUT",
                        "CHEEK",
                        "SIDE",
                        "THROAT",
                        "TAILBASE",
                        "BELLY",
                        "LEGBITE",
                        "NECKBITE",
                        "FACE",
                        "MANLEG",
                        "BRIGHTHEART",
                        "MANTAIL",
                        "BRIDGE",
                        "RIGHTBLIND",
                        "LEFTBLIND",
                        "BOTHBLIND",
                        "BEAKCHEEK",
                        "BEAKLOWER",
                        "CATBITE",
                        "RATBITE",
                        "QUILLCHUNK",
                        "QUILLSCRATCH",
                        "HINDLEG",
                        "BACK",
                        "QUILLSIDE",
                        "SCRATCHSIDE",
                        "BEAKSIDE",
                        "CATBITETWO",
                        "FOUR",
                        "LEFTEAR",
                        "RIGHTEAR",
                        "NOTAIL",
                        "HALFTAIL",
                        "NOPAW",
                        "NOLEFTEAR",
                        "NORIGHTEAR",
                        "NOEAR",
                        "SNAKE",
                        "TOETRAP",
                        "BURNPAWS",
                        "BURNTAIL",
                        "BURNBELLY",
                        "BURNRUMP",
                        "FROSTFACE",
                        "FROSTTAIL",
                        "FROSTMITT",
                        "FROSTSOCK",
                        "TOE",
                        "SNAKETWO",
                    ]
                    for tag in event["tags"]:
                        if tag in scar_list:
                            info["scars"].append(tag)
                            event["tags"].remove(tag)

                new_format["injury"].append(info)

        if "history_text" in event:
            if event["history_text"]:
                new_format["history"] = {}
                if "scar" in event["history_text"]:
                    new_format["history"]["scar"] = event["history_text"]["scar"]
                if "reg_death" in event["history_text"]:
                    new_format["history"]["reg_death"] = event["history_text"][
                        "reg_death"
                    ]
                if "lead_death" in event["history_text"]:
                    new_format["history"]["lead_death"] = event["history_text"][
                        "lead_death"
                    ]

        for tag in event["tags"]:
            if tag in [
                "other_cat",
                "other_cat_kit",
                "other_cat_med",
                "other_cat_warrior",
                "other_cat_dep",
                "other_cat_leader",
                "other_cat_app",
                "other_cat_med_app",
                "other_cat_elder",
                "rc_to_mc",
                "mc_to_rc",
            ]:
                new_format["relationships"] = []
                info = {}
                if "mc_to_rc" in event["tags"]:
                    event["tags"].remove("mc_to_rc")
                    info["cats_from"] = ["m_c"]
                    info["cats_to"] = ["r_c"]
                if "rc_to_mc" in event["tags"]:
                    event["tags"].remove("rc_to_mc")
                    info["cats_from"] = ["r_c"]
                    info["cats_to"] = ["m_c"]
                if "to_both" in event["tags"]:
                    event["tags"].remove("to_both")
                    info["mututal"] = True

                info["values"] = []
                if "romantic" in event["tags"]:
                    event["tags"].remove("romantic")
                    info["values"].append("romantic")
                if "platonic" in event["tags"]:
                    event["tags"].remove("platonic")
                    info["values"].append("platonic")
                if "dislike" in event["tags"]:
                    event["tags"].remove("dislike")
                    info["values"].append("dislike")
                if "comfort" in event["tags"]:
                    event["tags"].remove("comfort")
                    info["values"].append("comfort")
                if "jealous" in event["tags"]:
                    event["tags"].remove("jealous")
                    info["values"].append("jealous")
                if "trust" in event["tags"]:
                    event["tags"].remove("trust")
                    info["values"].append("trust")
                if "respect" in event["tags"]:
                    event["tags"].remove("respect")
                    info["values"].append("respect")

                info["amount"] = 5

                if "neg_romantic" in event["tags"]:
                    event["tags"].remove("neg_romantic")
                    info["values"].append("romantic")
                    info["amount"] = -5

                if "neg_platonic" in event["tags"]:
                    event["tags"].remove("neg_platonic")
                    info["values"].append("platonic")
                    info["amount"] = -5
                if "neg_dislike" in event["tags"]:
                    event["tags"].remove("neg_dislike")
                    info["amount"] = -5
                    info["values"].append("dislike")
                if "neg_comfort" in event["tags"]:
                    event["tags"].remove("neg_comfort")
                    info["amount"] = -5
                    info["values"].append("comfort")
                if "neg_jealous" in event["tags"]:
                    info["amount"] = -5
                    event["tags"].remove("neg_jealous")
                    info["values"].append("jealous")
                if "neg_trust" in event["tags"]:
                    event["tags"].remove("neg_trust")
                    info["amount"] = -5
                    info["values"].append("trust")
                if "neg_respect" in event["tags"]:
                    info["amount"] = -5
                    event["tags"].remove("neg_respect")
                    info["values"].append("respect")

                new_format["relationships"].append(info)

        if "new_cat" in path:
            new_format["outsider"] = {"current_rep": [], "changed": 1}
            if "hostile" in event["tags"]:
                event["tags"].remove("hostile")
                new_format["outsider"]["current_rep"].append("hostile")
            if "neutral" in event["tags"]:
                event["tags"].remove("neutral")
                new_format["outsider"]["current_rep"].append("neutral")
            if "welcoming" in event["tags"]:
                event["tags"].remove("welcoming")
                new_format["outsider"]["current_rep"].append("welcoming")

        if "other_clan" in event["tags"]:
            new_format["other_clan"] = {"current_rep": [], "changed": 0}
            if "war" in event["tags"]:
                event["tags"].remove("war")
                new_format["other_clan"]["current_rep"].append("hostile")
            if "hostile" in event["tags"]:
                event["tags"].remove("hostile")
                if "hostile" not in new_format["other_clan"]["current_rep"]:
                    new_format["other_clan"]["current_rep"].append("hostile")
            if "neutral" in event["tags"]:
                event["tags"].remove("neutral")
                new_format["other_clan"]["current_rep"].append("neutral")
            if "ally" in event["tags"]:
                event["tags"].remove("ally")
                new_format["other_clan"]["current_rep"].append("ally")

            if "rel_down" in event["tags"]:
                event["tags"].remove("rel_down")
                new_format["other_clan"]["changed"] = -5
            elif "rel_up" in event["tags"]:
                event["tags"].remove("rel_up")
                new_format["other_clan"]["changed"] = 5

            event["tags"].remove("other_clan")

        if "other_cat" in event["tags"]:
            event["tags"].remove("other_cat")

        if event["tags"]:
            for tag in event["tags"]:
                new_format["tags"].append(tag)

        # print(new_format["tags"])

        dict_text = ujson.dumps(new_format, indent=4)
        dict_text = dict_text.replace(
            "\/", "/"
        )  # ujson tries to escape "/", but doesn't end up doing a good job.

        if "injury" in path:
            if "beach" in path:
                injury_beach.append(dict_text)
            if "forest" in path:
                injury_forest.append(dict_text)
            if "general" in path:
                injury_general.append(dict_text)
            if "mountainous" in path:
                injury_mountainous.append(dict_text)
            if "plains" in path:
                injury_plains.append(dict_text)
            if "wetlands" in path:
                injury_wetlands.append(dict_text)
            if "desert" in path:
                injury_desert.append(dict_text)

    if injury_beach:
        string = ""
        for event in injury_beach:
            string = string + event
        with open("injury/beach.json", "w", encoding="utf-8") as write_file:
            write_file.write(string)
    if injury_forest:
        string = ""
        for event in injury_forest:
            string = string + event
        with open("injury/forest.json", "w") as write_file:
            write_file.write(string)
    if injury_general:
        string = ""
        for event in injury_general:
            string = string + event
        with open("injury/general.json", "w") as write_file:
            write_file.write(string)
    if injury_mountainous:
        string = ""
        for event in injury_mountainous:
            string = string + event
        with open("injury/mountainous.json", "w") as write_file:
            write_file.write(string)
    if injury_plains:
        string = ""
        for event in injury_plains:
            string = string + event
        with open("injury/plains.json", "w") as write_file:
            write_file.write(string)
    if injury_wetlands:
        string = ""
        for event in injury_wetlands:
            string = string + event
        with open("injury/wetlands.json", "w") as write_file:
            write_file.write(string)
    if injury_desert:
        string = ""
        for event in injury_desert:
            string = string + event
        with open("injury/desert.json", "w") as write_file:
            write_file.write(string)


root_dir = "../events"
file_set = set()

for dir_, _, files in os.walk(root_dir):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, root_dir)
        rel_file = os.path.join(rel_dir, file_name)
        if os.path.splitext(rel_file)[-1].lower() == ".json":
            file_set.add(rel_file)

for pa in file_set:
    reformat(pa)
