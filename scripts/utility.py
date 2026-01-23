# pylint: disable=line-too-long
"""

TODO: Docs


"""  # pylint: enable=line-too-long

import logging
from typing import TYPE_CHECKING

from scripts.cat_relations.enums import RelType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    pass


# ---------------------------------------------------------------------------- #
#                               Getting Cats                                   #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                          Handling Outside Factors                            #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                             Cat Relationships                                #
# ---------------------------------------------------------------------------- #


# todo: kill this function. with fire.
def get_num_of_cats_with_relation_amount_towards(cat, amount, all_cats):
    """
    Looks how many cats have the certain value
    :param cat: cat in question
    :param amount: amount of relationship value which has to be reached
    :param all_cats: list of cats which has to be checked
    """

    # collect all true or false if the value is reached for the cat or not
    # later count or sum can be used to get the amount of cats
    # this will be handled like this, because it is easier / shorter to check

    relation_dict = {v: [] for v in [*RelType]}

    for inter_cat in all_cats:
        if cat.ID in inter_cat.relationships:
            relation = inter_cat.relationships[cat.ID]
        else:
            continue

        for value in [*RelType]:
            if amount > 0:
                relation_dict[value].append(
                    relation.get_amount_of_type(value) >= amount
                )
            elif amount < 0:
                relation_dict[value].append(
                    relation.get_amount_of_type(value) <= amount
                )

    return_dict = {v: sum(relation_dict[v]) for v in [*RelType]}

    return return_dict


# ---------------------------------------------------------------------------- #
#                               Text Adjust                                    #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                                    Sprites                                   #
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
#                                     OTHER                                    #
# ---------------------------------------------------------------------------- #
