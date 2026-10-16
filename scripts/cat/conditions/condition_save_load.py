import dataclasses
import os

import ujson

from scripts.cat.cats import Cat
from scripts.cat.conditions.permanent_condition import PermanentCondition
from scripts.cat.conditions.temporary_condition import TemporaryCondition
from scripts.cat.constants import PERMANENT_CONDITIONS, TEMPORARY_CONDITIONS
from scripts.game_structure import game
from scripts.game_structure.game import switch_get_value, Switch, safe_save
from scripts.housekeeping.datadir import get_save_dir


def save_condition(cat):
    # save conditions for each cat
    save_id = None
    if switch_get_value(Switch.clan_save_id) != "":
        save_id = switch_get_value(Switch.clan_save_id)
    elif len(switch_get_value(Switch.clan_list)) > 0:
        save_id = switch_get_value(Switch.clan_list)[0]
    elif game.clan is not None:
        save_id = game.clan.save_id

    condition_directory = get_save_dir() + "/" + save_id + "/conditions"
    condition_file_path = condition_directory + "/" + cat.ID + "_conditions.json"

    if (not cat.temporary_conditions and not cat.permanent_conditions) or (
        (cat.dead or cat.status.is_outsider) and not cat.permanent_conditions
    ):
        if os.path.exists(condition_file_path):
            os.remove(condition_file_path)
        return

    conditions = {}

    if cat.temporary_conditions:
        conditions["temporary_conditions"] = [
            dataclasses.asdict(con) for con in cat.temporary_conditions
        ]

    if cat.permanent_conditions:
        conditions["permanent_conditions"] = [
            dataclasses.asdict(con) for con in cat.permanent_conditions
        ]

    safe_save(condition_file_path, conditions)


def load_conditions(cat: Cat, version_info: dict):
    if switch_get_value(Switch.clan_save_id) != "":
        clanname = switch_get_value(Switch.clan_save_id)
    else:
        clanname = switch_get_value(Switch.clan_list)[0]

    condition_directory = get_save_dir() + "/" + clanname + "/conditions/"
    condition_cat_directory = condition_directory + cat.ID + "_conditions.json"
    if not os.path.exists(condition_cat_directory):
        return

    try:
        with open(condition_cat_directory, "r", encoding="utf-8") as read_file:
            condition_data = ujson.loads(read_file.read())

            if version_info["version_name"] <= 5:
                condition_data = condition_convert(condition_data)

            cat.temporary_conditions = [
                TemporaryCondition(**info)
                for info in condition_data.get("temporary_conditions", {})
            ]
            cat.permanent_conditions = [
                PermanentCondition(**info)
                for info in condition_data.get("permanent_conditions", {})
            ]

        if "paralyzed" in cat.permanent_conditions and not cat.pelt.paralyzed:
            cat.pelt.paralyzed = True

    except Exception as e:
        print(
            f"WARNING: There was an error reading the condition file of cat #{cat}.\n",
            e,
        )


def condition_convert(condition_info: dict) -> dict:
    """
    Needs to happen during cat object creation. `version_convert()` happens afterward, so this func is necessary to preempt it.
    """
    new_save_info = {
        "permanent_conditions": [],
        "temporary_conditions": [],
    }

    for condition_type, conditions in condition_info.items():
        if condition_type == "permanent conditions":
            for name, con in conditions.items():
                name = _convert_name(name)
                new_info = {
                    "name": name,
                    "severity": con["severity"],
                    "is_congenital": con["born_with"],
                    "moons_until_discovery": con["moons_until"],
                    "removed_on_death": PERMANENT_CONDITIONS[name].get(
                        "removed_on_death", False
                    ),
                    "moon_gained": con["moon_start"]
                    if "moon_start" in con
                    else con.get("moons_with"),
                    "mortality": max(0.05, round(1 / con["mortality"], 2))
                    if con["mortality"]
                    else 0.0,
                    "immune_system_effect": round(
                        1 / con["illness_infectiousness"][0]["chance"], 2
                    )
                    if con["illness_infectiousness"]
                    else 0.0,
                    "progression": PERMANENT_CONDITIONS[name]["progression"],
                    "risks": {},
                    "current_complication": con["complication"],
                    "omit_moonskip": con["event_triggered"],
                }
                for risk in con["risks"]:
                    risk_name = _convert_name(risk["name"])
                    if (
                        risk_name in new_info["progression"]
                        or risk_name not in PERMANENT_CONDITIONS[name]["risks"]
                    ):
                        continue
                    new_info["risks"].update(
                        {risk_name: max(0.05, round(1 / risk["chance"], 2))}
                    )
                if (
                    new_info.get("mortality")
                    and not PERMANENT_CONDITIONS[name]["mortality"]
                ):
                    new_info["mortality"] = 0.0

                new_save_info["permanent_conditions"].append(new_info)

        if condition_type in ("illnesses", "injuries"):
            for name, con in conditions.items():
                name = _convert_name(name)
                new_info = {
                    "name": name,
                    "severity": con["severity"],
                    "duration": con["duration"],
                    "moon_gained": con["moon_start"]
                    if "moon_start" in con
                    else con.get("moons_with"),
                    "mortality": max(0.05, round(1 / con["mortality"], 2))
                    if con.get("mortality")
                    else 0.0,
                    "immune_system_effect": round(
                        1 / con["illness_infectiousness"][0].get("lower_by", 5), 2
                    )
                    if con.get("illness_infectiousness")
                    else 0.0,
                    "infectiousness": max(0.05, round(1 / con["infectiousness"], 2))
                    if con.get("infectiousness")
                    else 0.0,
                    "progression": TEMPORARY_CONDITIONS[name]["progression"],
                    "risks": {},
                    "current_complication": con.get("complication"),
                    "omit_moonskip": con["event_triggered"],
                    "scar_pool_override": con.get("potential_scars"),
                    "is_complication": name in ("infection", "festering_wound"),
                }
                for risk in con["risks"]:
                    risk_name = _convert_name(risk["name"])
                    if (
                        risk_name in new_info["progression"]
                        or risk_name not in TEMPORARY_CONDITIONS[name]["risks"]
                    ):
                        continue
                    new_info["risks"].update(
                        {risk_name: max(0.05, round(1 / risk["chance"], 2))}
                    )
                if (
                    new_info.get("mortality")
                    and not TEMPORARY_CONDITIONS[name]["mortality"]
                ):
                    new_info["mortality"] = 0.0

                new_save_info["temporary_conditions"].append(new_info)

    return new_save_info


def _convert_name(name: str) -> str:
    name = name.replace(" ", "_").replace("-", "_")

    if name in CONVERSION_DICT["condition_map"]:
        return CONVERSION_DICT["condition_map"][name]

    return name


with open(f"resources/dicts/conversion_dict.json", "r", encoding="utf-8") as read_file:
    CONVERSION_DICT = ujson.loads(read_file.read())
