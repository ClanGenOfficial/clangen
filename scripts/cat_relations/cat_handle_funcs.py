import os


from random import randint
from typing import TYPE_CHECKING

import ujson

from scripts.cat_relations.relationship import Relationship
from scripts.game_structure import game
from scripts.game_structure.game import game_setting_get, switch_get_value, Switch
from scripts.housekeeping.datadir import get_save_dir

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


def create_relationships_new_cat(new_cat: "Cat"):
    """Create relationships for a new generated cat."""
    for inter_cat in new_cat.all_cats.values():
        # the inter_cat is the same as the current cat
        if inter_cat.ID == new_cat.ID:
            continue
        # if the cat already has (somehow) a relationship with the inter cat
        if inter_cat.ID in new_cat.relationships:
            continue
        # if they dead (dead cats have no relationships)
        if new_cat.dead or inter_cat.dead:
            continue
        # if they are not within the same group
        if new_cat.status.group_ID != inter_cat.status.group_ID:
            continue
        inter_cat.relationships[new_cat.ID] = Relationship(inter_cat, new_cat)
        new_cat.relationships[inter_cat.ID] = Relationship(new_cat, inter_cat)


def init_all_relationships(cat: "Cat"):
    """Create Relationships to all current Clancats."""
    for ID in cat.all_cats:
        the_cat = cat.all_cats.get(ID)
        if the_cat.ID is not cat.ID:
            are_parents = False
            parents = False
            siblings = False

            if (
                cat.parent1 is not None
                and cat.parent2 is not None
                and the_cat.parent1 is not None
                and the_cat.parent2 is not None
            ):
                are_parents = the_cat.ID in (cat.parent1, cat.parent2)
                parents = are_parents or cat.ID in (
                    the_cat.parent1,
                    the_cat.parent2,
                )
                siblings = cat.parent1 in (
                    the_cat.parent1,
                    the_cat.parent2,
                ) or cat.parent2 in (the_cat.parent1, the_cat.parent2)

            related = parents or siblings

            # set the different stats
            romance = 0
            like = 0
            respect = 0
            comfort = 0
            trust = 0
            if game_setting_get("random relation"):
                if (
                    game.clan
                    and the_cat == game.clan.instructor
                    and game.clan.instructor.dead_for >= cat.moons
                ):
                    pass
                elif randint(1, 20) == 1 and romance < 1:
                    like += randint(-25, 5)
                    respect += randint(-10, 15)
                    trust += randint(-15, 5)
                    comfort += randint(-15, 10)
                else:
                    like += randint(-10, 35)
                    respect += randint(-10, 25)
                    trust += randint(-5, 15)
                    comfort += randint(-5, 15)
                    if (
                        randint(1, 100 - like) == 1
                        and cat.moons > 11
                        and the_cat.moons > 11
                        and cat.age == the_cat.age
                    ):
                        romance += randint(15, 30)
                        comfort = int(comfort * 1.3)
                        trust = int(trust * 1.2)

            if are_parents and like < 60:
                like = 60
            if siblings and like < 30:
                like = 30

            rel = Relationship(
                cat_from=cat,
                cat_to=the_cat,
                family=related,
                romance=romance,
                like=like,
                respect=respect,
                comfort=comfort,
                trust=trust,
            )
            cat.relationships[the_cat.ID] = rel


def load_relationship_of_cat(cat):
    if switch_get_value(Switch.clan_save_id) != "":
        clanname = switch_get_value(Switch.clan_save_id)
    else:
        clanname = switch_get_value(Switch.clan_list)[0]

    relation_directory = get_save_dir() + "/" + clanname + "/relationships/"
    relation_cat_directory = relation_directory + cat.ID + "_relations.json"

    cat.relationships = {}
    if os.path.exists(relation_directory):
        if not os.path.exists(relation_cat_directory):
            init_all_relationships(cat)
            for cat in cat.all_cats.values():
                if cat == cat:
                    continue
                cat.create_one_relationship(cat)
            return
        try:
            with open(relation_cat_directory, "r", encoding="utf-8") as read_file:
                rel_data = ujson.loads(read_file.read())

                for rel in rel_data:
                    # checking validity
                    cat_to = cat.all_cats.get(rel["cat_to_id"])
                    if cat_to is None or rel["cat_to_id"] == cat.ID:
                        continue

                    # converting old saves
                    if "platonic_like" in rel:
                        old_rel = rel.copy()
                        rel = {}
                        rel["log"] = old_rel["log"]
                        rel["family"] = old_rel["family"]
                        rel["cat_to_id"] = old_rel["cat_to_id"]

                        # romance
                        rel["romance"] = old_rel["romantic_love"]

                        # attempts to convert "complex" relationships by
                        #   using the "negative" value for the lower of
                        #   platonic_like/comfort and trust/admiration.
                        # if the relationship isn't complex
                        #   (<= 5 for negative values; this is an arbitrary value),
                        #   then it just takes the value without considering the negative.
                        if old_rel["platonic_like"] > old_rel["comfortable"]:
                            rel["like"] = old_rel["platonic_like"]
                            if old_rel["dislike"] <= 5:
                                rel["comfort"] = old_rel["comfortable"]
                            else:
                                rel["comfort"] = -old_rel["dislike"]
                        else:  # old_rel["platonic_like"] < old_rel["comfort"]
                            rel["comfort"] = old_rel["comfortable"]
                            if old_rel["dislike"] <= 5:
                                rel["like"] = old_rel["platonic_like"]
                            else:
                                rel["like"] = -old_rel["dislike"]

                        if old_rel["trust"] > old_rel["admiration"]:
                            rel["trust"] = old_rel["trust"]
                            if old_rel["jealousy"] <= 5:
                                rel["respect"] = old_rel["admiration"]
                            else:
                                rel["respect"] = -old_rel["jealousy"]
                        else:  # old_rel["trust"] < old_rel["admiration"]
                            rel["respect"] = old_rel["admiration"]
                            if old_rel["jealousy"] <= 5:
                                rel["trust"] = old_rel["trust"]
                            else:
                                rel["trust"] = -old_rel["jealousy"]

                    # create relationship
                    new_rel = Relationship(
                        cat_from=cat,
                        cat_to=cat_to,
                        family=rel["family"] or False,
                        romance=(rel["romance"] or 0),
                        like=(rel["like"] or 0),
                        respect=rel["respect"] or 0,
                        comfort=rel["comfort"] or 0,
                        trust=rel["trust"] or 0,
                        log=rel["log"],
                    )
                    cat.relationships[rel["cat_to_id"]] = new_rel

        except KeyError:
            print(
                f"WARNING: There was an error reading the relationship file of cat #{cat}."
            )
