import os

import ujson


root_dir = "../resources/lang/en/thoughts"
file_set = set()


def load_paths():
    for dir_, _, files in os.walk(root_dir):
        for file_name in files:
            if file_name == "reformat_thoughts.py":
                continue
            rel_dir = os.path.relpath(dir_, root_dir)
            rel_file = os.path.join(rel_dir, file_name)
            if os.path.splitext(rel_file)[-1].lower() == ".json":
                file_set.add(rel_file)


def reformat():
    for path in file_set:
        new_thoughts = []
        try:
            with open(path, "r") as read_file:
                thoughts = read_file.read()
                thoughts_dict = ujson.loads(thoughts)

        except:
            print(f"Something went wrong with {path}")
            continue

        for t in thoughts_dict:
            reformatted_thought = {"id": t.get("id")}
            if t.get("biome"):
                reformatted_thought["location"] = t.get("biome")
            if t.get("season"):
                reformatted_thought["season"] = t.get("season")

            reformatted_thought["strings"] = t.get("thoughts")

            # MAIN CAT
            m_c = {}
            if t.get("main_status_constraint"):
                if "living" in t.get("main_status_constraint"):
                    m_c["group"] = ["-afterlife"]

                m_c["status"] = t.get("main_status_constraint")

            if t.get("main_status_history"):
                m_c["past_status"] = t.get("main_status_history")

            if t.get("main_age_constraint"):
                m_c["age"] = t.get("main_age_constraint")

            if t.get("main_trait_constraint"):
                m_c["stat"] = {
                    "trait": t.get("main_trait_constraint"),
                }
            if t.get("main_skill_constraint"):
                m_c["stat"] = {
                    "skill": t.get("main_skill_constraint"),
                }
            if (
                t.get("has_injuries", {}).get("m_c")
                or t.get("perm_conditions", {}).get("m_c")
                or t.get("not_working")
            ):
                health = {}
                if t.get("not_working"):
                    health["working"] = not t.get("not_working")
                if t.get("has_injuries", {}).get("m_c"):
                    health["condition"] = t["has_injuries"]["m_c"]
                if t.get("perm_conditions", {}).get("m_c"):
                    health["condition"] = t["perm_conditions"]["m_c"]
                    if t["perm_conditions"].get("born_with", {}).get("m_c"):
                        health["must_be_congenital"] = True

                m_c["health"] = health

            if t.get("main_backstory_constraint"):
                m_c["backstory"] = t.get("main_backstory_constraint")
            if m_c:
                reformatted_thought["involved_cats"] = {}
                reformatted_thought["involved_cats"]["m_c"] = m_c

            # RANDOM CAT
            r_c = {}
            if t.get("random_status_constraint"):
                r_c["status"] = t.get("random_status_constraint")

            if t.get("random_status_history"):
                r_c["past_status"] = t.get("random_status_history")

            if t.get("random_age_constraint"):
                r_c["age"] = t.get("random_age_constraint")

            if t.get("random_living_status"):
                if (
                    "starclan" in t.get("random_living_status")
                    and "darkforest" in t.get("random_living_status")
                    and "unknownresidence" in t.get("random_living_status")
                    and "living" in t.get("random_living_status")
                ):
                    # there's at least one thought that does this for some reason, so we're just gonna try and catch it
                    pass
                elif "living" in t.get("random_living_status"):
                    r_c["group"] = ["-afterlife"]
                elif (
                    "starclan" in t.get("random_living_status")
                    and "darkforest" in t.get("random_living_status")
                    and "unknownresidence" in t.get("random_living_status")
                ):
                    r_c["group"] = ["afterlife"]
                else:
                    r_c["group"] = []
                    if "starclan" in t.get("random_living_status"):
                        r_c["group"].append("starclan")
                    if "darkforest" in t.get("random_living_status"):
                        r_c["group"].append("dark_forest")
                    if "unknownresidence" in t.get("random_living_status"):
                        r_c["group"].append("unknown_residence")

            if t.get("random_outside_status"):
                if "clancat" in t["random_outside_status"]:
                    r_c["group"].append("player_clan")
                if "outside" in t["random_outside_status"]:
                    r_c["group"].append("no_group")

            if t.get("random_trait_constraint"):
                r_c["stat"] = {
                    "trait": t.get("random_trait_constraint"),
                }
            if t.get("random_skill_constraint"):
                r_c["stat"] = {
                    "skill": t.get("random_skill_constraint"),
                }

            if t.get("has_injuries", {}).get("r_c") or t.get("perm_conditions", {}).get(
                "r_c"
            ):
                health: dict = {"condition": []}
                if t.get("has_injuries", {}).get("r_c"):
                    health["condition"] = t["has_injuries"]["r_c"]
                if t.get("perm_conditions", {}).get("r_c"):
                    health["condition"] = t["perm_conditions"]["r_c"]

                r_c["health"] = health

            if t.get("random_backstory_constraint"):
                r_c["backstory"] = t.get("random_backstory_constraint")
            if r_c:
                if not reformatted_thought.get("involved_cats"):
                    reformatted_thought["involved_cats"] = {}
                reformatted_thought["involved_cats"]["r_c"] = r_c

            if t.get("relationship_constraint"):
                reformatted_thought["relationship_constraint"] = [
                    {
                        "cats_from": ["m_c"],
                        "cats_to": ["r_c"],
                        "mutual": False,
                        "constraints": t.get("relationship_constraint"),
                    }
                ]
            new_thoughts.append(reformatted_thought)

        dict_text = ujson.dumps(new_thoughts, indent=4)
        dict_text = dict_text.replace(
            "\/", "/"
        )  # ujson tries to escape "/", but doesn't end up doing a good job.

        with open(path, "w") as write_file:
            write_file.write(dict_text)


load_paths()
reformat()
