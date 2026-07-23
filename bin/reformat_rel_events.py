import os
import ujson

root_dir = "../resources/lang/en/events/relationship_events/normal_interactions"
file_set = set()

intensity_dict = {"low": 5, "medium": 10, "high": 15}


def load_paths():
    for dir_, _, files in os.walk(root_dir):
        for file_name in files:
            rel_dir = os.path.relpath(dir_, root_dir)
            rel_file = os.path.join(rel_dir, file_name)
            if os.path.splitext(rel_file)[-1].lower() == ".json":
                file_set.add(rel_file)


def reformat():
    for path in file_set:
        new_events = {
            "low": [],
            "medium": [],
            "high": [],
        }

        try:
            with open(f"{root_dir}/{path}", "r") as read_file:
                events = read_file.read()
                event_dict = ujson.loads(events)

        except:
            print(f"Something went wrong with {path}")
            continue

        for e in event_dict:
            reformatted_event: dict = {
                "id": e.get("id"),
                "strings": e.get("interactions"),
            }

            # MAIN CAT
            m_c = {}
            if e.get("main_status_constraint"):
                if "living" in e.get("main_status_constraint"):
                    m_c["group"] = ["-afterlife"]

                m_c["status"] = e.get("main_status_constraint")

            if e.get("main_trait_constraint"):
                m_c["stat"] = {
                    "trait": e.get("main_trait_constraint"),
                }
            if e.get("main_skill_constraint"):
                m_c["stat"] = {
                    "skill": e.get("main_skill_constraint"),
                }

            if m_c:
                reformatted_event["involved_cats"] = {}
                reformatted_event["involved_cats"]["m_c"] = m_c

            # RANDOM CAT
            r_c = {}
            if e.get("random_status_constraint"):
                r_c["status"] = e.get("random_status_constraint")

            if e.get("random_age_constraint"):
                r_c["age"] = e.get("random_age_constraint")

            if e.get("random_trait_constraint"):
                r_c["stat"] = {
                    "trait": e.get("random_trait_constraint"),
                }
            if e.get("random_skill_constraint"):
                r_c["stat"] = {
                    "skill": e.get("random_skill_constraint"),
                }

            if r_c:
                if not reformatted_event.get("involved_cats"):
                    reformatted_event["involved_cats"] = {}
                reformatted_event["involved_cats"]["r_c"] = r_c

            if e.get("relationship_constraint"):
                reformatted_event["relationship_constraint"] = [
                    {
                        "cats_from": ["m_c"],
                        "cats_to": ["r_c"],
                        "mutual": False,
                        "constraints": e.get("relationship_constraint"),
                    }
                ]

            if e.get("reaction_random_cat"):
                if not "relationship_changes" in reformatted_event:
                    reformatted_event["relationship_changes"] = []

                increase = []
                decrease = []
                for rel_type, v in e["reaction_random_cat"].items():
                    if v == "increase":
                        increase.append(rel_type)
                    else:
                        decrease.append(rel_type)

                if increase:
                    reformatted_event["relationship_changes"].append(
                        {
                            "cats_from": ["r_c"],
                            "cats_to": ["m_c"],
                            "mutual": False,
                            "values": increase,
                            "amount": intensity_dict[e.get("intensity", "medium")],
                        }
                    )
                if decrease:
                    reformatted_event["relationship_changes"].append(
                        {
                            "cats_from": ["r_c"],
                            "cats_to": ["m_c"],
                            "mutual": False,
                            "values": decrease,
                            "amount": intensity_dict[e.get("intensity", "medium")] * -1,
                        }
                    )
            if e.get("reaction_main_cat"):
                if not "relationship_changes" in reformatted_event:
                    reformatted_event["relationship_changes"] = []

                increase = []
                decrease = []
                for rel_type, v in e["reaction_main_cat"].items():
                    if v == "increase":
                        increase.append(rel_type)
                    else:
                        decrease.append(rel_type)

                if increase:
                    reformatted_event["relationship_changes"].append(
                        {
                            "cats_from": ["m_c"],
                            "cats_to": ["r_c"],
                            "mutual": False,
                            "values": increase,
                            "amount": intensity_dict[e.get("intensity", "medium")],
                        }
                    )
                if decrease:
                    reformatted_event["relationship_changes"].append(
                        {
                            "cats_from": ["m_c"],
                            "cats_to": ["r_c"],
                            "mutual": False,
                            "values": decrease,
                            "amount": intensity_dict[e.get("intensity", "medium")] * -1,
                        }
                    )

            new_events[e.get("intensity", "medium")].append(reformatted_event)

        for intensity, event_list in new_events.items():
            dict_text = ujson.dumps(event_list, indent=4)
            dict_text = dict_text.replace(
                "\/", "/"
            )  # ujson tries to escape "/", but doesn't end up doing a good job.

            path_strings = path.split("\\")
            with open(
                f"{root_dir}/{path_strings[0]}/{intensity}/{path_strings[1]}", "x"
            ) as write_file:
                write_file.write(dict_text)


load_paths()
reformat()
