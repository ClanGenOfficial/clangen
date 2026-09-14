from random import randint, random, choice
from typing import TYPE_CHECKING

from scripts.cat.enums import CatThought
from scripts.cat_relations.enums import RelTier, rel_type_tiers
from scripts.cat_relations.relationship import Relationship
from scripts.cat.microservices.conditions import get_ill
from scripts.events_module.text_adjust import event_text_adjust
from scripts.game_structure import game

if TYPE_CHECKING:
    from scripts.cat.cats import Cat


def grief(dead_cat: "Cat", body: bool):
    """
    compiles grief moon event text
    """
    if body:
        body_status = "body"
    else:
        body_status = "no_body"

    # Keep track of whether the body was treated with rosemary.
    body_treated = False
    text = None

    # apply grief to cats with high positive relationships to dead cat
    for cat in dead_cat.all_cats.values():
        if cat.dead or cat.status.is_outsider or cat.moons < 1:
            continue

        rel_with_dead = cat.relationships.get(dead_cat.ID)
        if not isinstance(rel_with_dead, Relationship):
            continue

        family_relation = familial_grief(dead_cat=dead_cat, living_cat=cat)
        very_high_types = []
        high_types = []
        very_low_types = []

        # find what tier of rel they had for each type
        tiers: list[RelTier] = rel_with_dead.get_reltype_tiers()
        for tier in tiers:
            rel_type = [k for k in rel_type_tiers if tier in rel_type_tiers[k]]
            if tier.is_extreme_pos:
                very_high_types.extend(rel_type)
            elif tier.is_mid_pos:
                high_types.extend(rel_type)
            elif tier.is_extreme_neg:
                very_low_types.extend(rel_type)
            elif tier.is_mid_neg and randint(1, 6) == 1:
                very_low_types.extend(rel_type)
            continue

        major_chance = 0
        if very_high_types:
            # major grief eligible cats.

            major_chance = 3
            # the less stable the cat, the more likely to grieve
            if cat.personality.stability < 5:
                major_chance -= 1

            # if considered family, grief more likely
            if family_relation != "general":
                major_chance -= 1

            # decrease major grief chance if grave herbs are used
            if (
                body
                and not body_treated
                and game.clan.herb_supply.entire_supply["rosemary"]
            ):
                body_treated = True
                game.clan.herb_supply.remove_herb("rosemary", -1)
                game.herb_events_list.append(
                    f"Rosemary was used for {dead_cat.name}'s body."
                )

            if body_treated:
                major_chance += 1

        # If major_chance is not 0, there is a chance for major grief
        grief_type = None
        if major_chance and not int(random() * major_chance):
            grief_type = "major"

            possible_strings = []
            for x in very_high_types:
                possible_strings.extend(
                    dead_cat.generate_events.possible_death_reactions(
                        family_relation, x, cat.personality.trait, body_status
                    )
                )

            if not possible_strings:
                print("No grief strings")
                continue

            text = choice(possible_strings)
            text = event_text_adjust(cat, text=text, main_cat=dead_cat, random_cat=cat)

            get_ill(cat, "grief stricken", event_triggered=True, severity="major")

        # If major grief fails, but there are still very_high or high values,
        # it can fail to minor grief. If they have a family relation, bypass the roll and guarantee it
        elif (very_high_types or high_types) and (
            family_relation != "general" or not int(random() * 5)
        ):
            grief_type = "minor"

            text = CatThought.ON_GRIEF_NO_BODY

            if body:
                text = CatThought.ON_GRIEF_TOWARD_BODY

        if grief_type:
            # Generate the event:
            if cat.ID not in game.clan.grief_strings:
                game.clan.grief_strings[cat.ID] = []

            game.clan.grief_strings[cat.ID].append(
                (text, (dead_cat.ID, cat.ID), grief_type)
            )
            continue

        # Negative "grief" messages are just for flavor.
        if very_low_types:
            # Generate the event:
            possible_strings = []
            for x in very_low_types:
                value = f"neg_{x}"
                possible_strings.extend(
                    dead_cat.generate_events.possible_death_reactions(
                        family_relation, value, cat.personality.trait, body_status
                    )
                )

            text = event_text_adjust(
                cat, choice(possible_strings), main_cat=dead_cat, random_cat=cat
            )
            if cat.ID not in game.clan.grief_strings:
                game.clan.grief_strings[cat.ID] = []

            game.clan.grief_strings[cat.ID].append(
                (text, (dead_cat.ID, cat.ID), "negative")
            )


def familial_grief(dead_cat, living_cat: "Cat"):
    """
    returns relevant grief strings for family members, if no relevant strings then returns None
    """
    if dead_cat.is_parent(living_cat):
        return "child"
    elif living_cat.is_parent(dead_cat):
        return "parent"
    elif dead_cat.is_sibling(living_cat):
        return "sibling"
    elif dead_cat.ID in living_cat.mate:
        return "mate"
    else:
        return "general"
