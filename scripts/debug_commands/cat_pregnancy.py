from typing import List

from scripts.cat.cats import Cat
from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import (
    add_output_line_to_log,
    add_multiple_lines_to_log,
)
from scripts.game_structure.game_essentials import game
from scripts.events_module.relationship.pregnancy_events import Pregnancy_Events


def get_cat_from_name_or_id(nameid: str) -> Cat:
    try:
        cat = [
            x
            for x in Cat.all_cats_list
            if nameid.lower() == str(x.name).lower() or nameid == x.ID
        ]
        if len(cat) > 0:
            cat = cat[0]
        else:
            cat = None
    except:
        cat = None
    return cat


class AddPregnancyCommand(Command):
    name = "add"
    description = "Add a pregnancy"
    aliases = ["a"]

    usage = "<cat name|id> <other parent name|id>"

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log(
                "Please specify the name/id of the cat to add a pregnancy to."
            )
            return
        cat = get_cat_from_name_or_id(args[0])
        second_parent = get_cat_from_name_or_id(args[1]) if len(args) > 1 else None
        if second_parent:
            Pregnancy_Events.handle_zero_moon_pregnant(
                cat, other_cat=second_parent, clan=game.clan
            )
        elif len(args) > 1:
            add_output_line_to_log("Invalid name or id for second parent.")
            return
        elif cat:
            Pregnancy_Events.handle_zero_moon_pregnant(cat, clan=game.clan)
        else:
            add_output_line_to_log("Invalid name or id.")
            return
        add_output_line_to_log(f"Added pregnancy to {cat.name} ({cat.ID})")


class RemovePregnancyCommand(Command):
    name = "remove"
    description = "Remove a pregnancy"
    aliases = ["r"]

    usage = "<cat name|id>"

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log(
                "Please specify the name/id of the cat to remove the pregnancy from."
            )
            return
        cat = get_cat_from_name_or_id(args[0])
        if cat and "pregnant" in cat.injuries:
            del game.clan.pregnancy_data[cat.ID]
            cat.injuries.pop("pregnant")
            add_output_line_to_log(f"Removed pregnancy from {cat.name} ({cat.ID})")
        else:
            add_output_line_to_log("Invalid name/id or cat is not pregnant.")


class EditPregnancyCommand(Command):
    name = "edit"
    description = "Edit a pregnancy"
    aliases = ["e"]

    usage = "<cat id> [moons] [amount] <severity (major|minor)> <other parent name|id>"

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log(
                "Please specify the name/id of the cat to edit the pregnancy of."
            )
            return
        current_cat = get_cat_from_name_or_id(args[0])
        if not current_cat:
            add_output_line_to_log("Invalid name/id.")
            return
        moons_amt = args[1] if len(args) > 1 else None
        if not moons_amt or moons_amt in ("same" or "" or "s"):
            moons_amt = game.clan.pregnancy_data[current_cat.ID]["moons"]

        kits_amt = args[2] if len(args) > 2 else None
        if not kits_amt or kits_amt in ("same" or "" or "s"):
            kits_amt = game.clan.pregnancy_data[current_cat.ID]["amount"]

        severtity = args[3] if len(args) > 3 else None
        if not severtity or severtity in ("same" or "" or "s"):
            severtity = current_cat.injuries["pregnant"]["severity"]

        second_parent = args[4] if len(args) > 4 else None
        if not second_parent or second_parent in ("same" or "" or "s"):
            second_parent = game.clan.pregnancy_data[current_cat.ID]["second_parent"]

        second_parent_cat = (
            get_cat_from_name_or_id(second_parent) if second_parent else None
        )
        second_parent_repr = (
            f"{second_parent_cat.name} ({second_parent_cat.ID})"
            if second_parent_cat
            else "None"
        )
        if "pregnant" in current_cat.injuries:
            game.clan.pregnancy_data[current_cat.ID]["moons"] = int(moons_amt)
            game.clan.pregnancy_data[current_cat.ID]["amount"] = int(kits_amt)
            current_cat.injuries["pregnant"]["severity"] = severtity
            game.clan.pregnancy_data[current_cat.ID]["second_parent"] = second_parent
            add_output_line_to_log(
                f"Successfully edited pregnancy of {current_cat.name} ({current_cat.ID}), new pregnancy data: "
            )
            add_multiple_lines_to_log(
                f"""Moons: {moons_amt}
                                        Amount of Kits: {kits_amt}
                                        Severity: {severtity}
                                        Second Parent: {second_parent_repr}"""
            )
        else:
            add_output_line_to_log("Specified cat is not pregnant")


class ViewPregnancyCommand(Command):
    name = "view"
    description = "View the stats a pregnancy"
    aliases = ["v"]

    usage = "<cat id>"

    def callback(self, args: List[str]):
        if len(args) == 0:
            add_output_line_to_log(
                "Please specify the name/id of the cat to edit the pregnancy of."
            )
            return
        cat = get_cat_from_name_or_id(args[0])

        second_parent_cat = (
            get_cat_from_name_or_id(game.clan.pregnancy_data[cat.ID]["second_parent"])
            if game.clan.pregnancy_data[cat.ID]["second_parent"]
            else None
        )
        second_parent_repr = (
            f"{second_parent_cat.name} ({second_parent_cat.ID})"
            if second_parent_cat
            else "None"
        )
        if "pregnant" in cat.injuries:
            add_multiple_lines_to_log(
                f"""Cat: {cat.name} ({cat.ID})
                                        Moons: {game.clan.pregnancy_data[cat.ID]["moons"]}
                                        Amount of Kits: {game.clan.pregnancy_data[cat.ID]["amount"]}
                                        Severity: {cat.injuries["pregnant"]["severity"]}
                                        Second Parent: {second_parent_repr}"""
            )
        else:
            add_output_line_to_log("Specified cat is not pregnant")


class PregnanciesCommand(Command):
    name = "pregnancies"
    description = "Manage Cat Pregnancies"
    aliases = ["preg", "p", "pregnancy"]

    sub_commands = [
        AddPregnancyCommand(),
        RemovePregnancyCommand(),
        EditPregnancyCommand(),
        ViewPregnancyCommand(),
    ]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
