from typing import List

from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import Relationship, RelType
from scripts.debug_commands.command import Command
from scripts.debug_commands.utils import add_output_line_to_log


def set_cat_relationship_to_cat(cat_a: Cat, rel_type: str, cat_b: Cat, rel_value: int):
    """
    Sets the specified relationship type (rel_type)
    of cat_a towards cat_b to a specified value (rel_value)
    """
    cat_from_relationship: Relationship = cat_a.relationships.get(cat_b.ID)
    if not cat_from_relationship:
        return

    setattr(cat_from_relationship, rel_type, rel_value)

    add_output_line_to_log(
        f"Successfully set {str(cat_a.name)}'s {rel_type} towards {str(cat_b.name)} to {rel_value}"
    )


class SetRelationshipCommand(Command):
    name = "set"
    description = "Set the relationship values of a cat towards another cat."
    usage = "<cat_from name|id> <romance|like|respect|trust|comfort> <cat_to name|id> [number] <mutual>"
    aliases = ["s"]

    def callback(self, args):
        if len(args) == 0:
            add_output_line_to_log("Please specify a cat name or ID")
            return

        if len(args) < 4:
            add_output_line_to_log("Missing more than one required argument")
            return

        cat_from = None
        cat_to = None
        rel_type = args[1].lower()

        if not args[3].isdigit():
            add_output_line_to_log("rel_value is not an integer")
            return

        rel_value = int(args[3])

        if (
            not rel_type
            in RelType._value2member_map_  # pylint: disable=protected-access
        ):
            add_output_line_to_log(f"Invalid relationship type '{rel_type}'")
            return

        for cat in Cat.all_cats_list:
            if cat_from and cat_to:
                break
            cat_name = str(cat.name).lower()
            if cat_name == args[0].lower() or cat.ID == args[0]:
                cat_from = cat
                continue
            if cat_name == args[2].lower() or cat.ID == args[2]:
                cat_to = cat
                continue

        if not cat_from:
            add_output_line_to_log(
                "Failed to retrieve cat_from, did you specify a valid cat name or ID?"
            )
            return
        if not cat_to:
            add_output_line_to_log(
                "Failed to retrieve cat_to, did you specify a valid cat name or ID?"
            )
            return

        set_cat_relationship_to_cat(cat_from, rel_type, cat_to, rel_value)
        if len(args) == 5:
            set_cat_relationship_to_cat(cat_to, rel_type, cat_from, rel_value)


class RelationshipsCommand(Command):
    name = "relationships"
    description = "Manage cats' relationships"
    aliases = ["relationship", "relation", "rel", "r"]

    sub_commands = [
        SetRelationshipCommand(),
    ]

    def callback(self, args: List[str]):
        add_output_line_to_log("Please specify a subcommand")
