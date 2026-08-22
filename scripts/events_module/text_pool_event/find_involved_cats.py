import random
from typing import Union

from scripts.cat.cats import Cat
from scripts.clan import OtherClan
from scripts.config import get_config
from scripts.events_module.event_filters import (
    check_rel_constraint_groups,
    cat_for_event,
)
from scripts.events_module.parameter_dicts import InvolvedCatDict
from scripts.events_module.patrol.create_new_cat import updated_create_new_cat
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent


def find_cats(
    interactable_cats: list,
    involved_cats: dict,
    outside_cats: list,
    event: Union[PatrolEvent, TextPoolEvent],
    other_clan: OtherClan,
) -> dict:
    """
    Finds and returns cats for a PatrolEvent or TextPoolEvent.
    :param interactable_cats: A list of cats within the Clan eligible to appear in the event.
    :param involved_cats: Dict of cats already involved. Key is abbreviation, value is cat object
    :param outside_cats: A list of cats outside the Clan eligible to appear in the event.
    :param event: The PatrolEvent or TextPoolEvent that needs involved cats
    :param other_clan: The OtherClan object involved in the event
    :return: Updated involved_cats dict with valid cats. If dict is empty, then valid cats were not found.
    """
    temp_involved_cats = involved_cats.copy()
    interactable_cats = interactable_cats.copy()

    cats_to_create = []

    can_give_condition = hasattr(event, "condition")

    # just an initial relationship check to catch things like patrol_cats
    if involved_cats and event.relationship_constraint:
        if not all(
            check_rel_constraint_groups(block, temp_involved_cats)
            for block in event.relationship_constraint
        ):
            return {}

    for abbr, constraints in event.involved_cats.items():
        possible_injuries = get_potential_conditions(abbr, can_give_condition, event)

        # CHECK ALREADY ASSIGNED CAT
        if abbr in involved_cats:
            if involved_cats[abbr] is None and abbr in event.involved_cats:
                # sometimes a specific abbr may be "preset" as None
                # which indicates that events requiring that abbr should be avoided
                return {}
            possible_cats = (
                involved_cats[abbr] if isinstance(abbr, list) else [involved_cats[abbr]]
            )

        # CHECK PRIOR ABBREVIATIONS
        elif constraints.get("prior_abbreviation"):
            possible_cats = _check_prior_abbreviation(
                abbr, constraints, event, interactable_cats, involved_cats
            )

        # CHECK NEW CATS
        elif "n_c" in abbr:
            # CATS THAT CAN BE MADE
            if "can_create_new_cat" in constraints:
                # these cats can be created if need be, so we'll do them after we've found all the cats that must exist
                cats_to_create.append(abbr)
                continue

            # CATS THAT MUST EXIST
            possible_cats = [
                c for c in outside_cats if c not in temp_involved_cats.values()
            ]

        # CHECK MULTI_CAT
        elif abbr == "multi_cat":
            temp_involved_cats["multi_cat"] = _get_multi_cats(
                involved_cats,
                interactable_cats.copy(),
                event,
                constraints,
                possible_injuries,
            )
            # if we found no one, then this event isn't possible, and we should try a different one
            if not temp_involved_cats["multi_cat"]:
                return {}
            else:
                # remove cats from the pool so they don't get repeated in the event
                for c in temp_involved_cats["multi_cat"]:
                    interactable_cats.remove(c)
                continue

        # CHECK ALL UN-USED CATS
        else:
            possible_cats = interactable_cats

        if not possible_cats:
            # uh oh, we're out of options!
            return {}

        # random shuffle to ensure we aren't picking the same cats all the time
        random.shuffle(possible_cats)

        # initial filter of the entire list of cats for the more general constraints
        possible_cats = cat_for_event(
            constraint_dict=constraints,
            possible_cats=possible_cats,
            tags=event.tags,
            injuries=possible_injuries,
            other_involved_clan_id=other_clan.group_ID if other_clan else None,
            return_list=True,
            return_id=False,
        )
        if not possible_cats:
            return {}

        # now choose a cat to fill the role, checking for relationship constraints
        temp_involved_cats = _find_involved_cat(
            abbr,
            possible_cats,
            relationship_constraint=event.relationship_constraint,
            cat_constraints=constraints,
            temp_involved_cats=temp_involved_cats,
            other_clan=other_clan,
        )
        if not temp_involved_cats:
            return {}

        if temp_involved_cats[abbr] in interactable_cats:
            interactable_cats.remove(temp_involved_cats[abbr])

    # create new cats if we need to!
    for abbr in cats_to_create:
        # this will first try to find an existing cat, but if it can't then it'll make a new one
        constraints = event.involved_cats[abbr]
        cat_list = [c for c in outside_cats if c not in temp_involved_cats.values()]
        possible_injuries = get_potential_conditions(abbr, can_give_condition, event)

        # initial filter of the entire list of cats for the more general constraints
        possible_cats = cat_for_event(
            constraint_dict=constraints,
            possible_cats=cat_list,
            tags=event.tags,
            injuries=possible_injuries,
            other_involved_clan_id=other_clan.group_ID if other_clan else None,
            return_list=True,
            return_id=False,
        )

        new_cats = _find_involved_cat(
            abbr,
            possible_cats,
            relationship_constraint=event.relationship_constraint,
            cat_constraints=constraints,
            temp_involved_cats=temp_involved_cats,
            other_clan=other_clan,
        )
        temp_involved_cats.update(new_cats)

    return temp_involved_cats


def get_potential_conditions(abbr, can_give_condition, event):
    possible_injuries = []
    # grab any injuries they might get
    if can_give_condition and event.condition:
        for block in event.condition:
            if abbr in block["cats"]:
                possible_injuries.extend(block["condition"])
    return possible_injuries


def _check_prior_abbreviation(
    abbr, constraints, event, interactable_cats, involved_cats
):
    """
    Checks which cats are allowed per prior_abbreviation constraints
    """
    # check for exclusionary status
    is_exclusionary = any(
        value.find("-") == 0 for value in constraints["prior_abbreviation"]
    )
    # now grab the "clean" abbreviations
    prior_abbreviations = [
        a.replace("-", "") for a in constraints["prior_abbreviation"]
    ]
    # find all the cats that were listed in the abbreviations
    abbr_cats = [involved_cats.get(_a) for _a in prior_abbreviations]
    # if it's "any" then that's easy-peasy, just allow any of the cats
    if "any" in prior_abbreviations:
        possible_cats = interactable_cats
    # if it's meant to be exclusionary, then possible_cats will be all cats not in abbr_cats
    elif is_exclusionary:
        possible_cats = [c for c in interactable_cats if c not in abbr_cats]
    # otherwise it's just abbr_cats
    else:
        if abbr_cats == [None]:
            print(f"WARNING: issue with {abbr} prior_abbreviation setting on {event}")
            return []

        possible_cats = abbr_cats

    return possible_cats


def _find_involved_cat(
    abbr: str,
    possible_cats: list[Cat],
    relationship_constraint,
    cat_constraints,
    temp_involved_cats: dict,
    other_clan: OtherClan,
) -> dict:
    """
    Finds a cat from the available cats that can fill the abbreviation slot. This will check against relationship
    constraints and will create a new cat if necessary and allowed.
    """
    if possible_cats:
        possible_cats = possible_cats.copy()

    # if relationships aren't required, just grab some cats and go!
    if possible_cats and not relationship_constraint:
        # take first cat
        temp_involved_cats[abbr] = possible_cats[0]
        return temp_involved_cats

    # otherwise, let's make sure we fulfill the rel constraints with this cat
    elif possible_cats:
        while not temp_involved_cats.get(abbr):
            # need a temp cat dict that includes our possible kitty
            _temp_cats = temp_involved_cats.copy()
            _temp_cats[abbr] = possible_cats[0]
            # now we check each rel constraint to make sure our new cat is valid
            if not all(
                check_rel_constraint_groups(block, _temp_cats)
                for block in relationship_constraint
            ):
                # they aren't! so we remove them from the possibilities
                possible_cats.remove(_temp_cats[abbr])
                if not possible_cats:
                    # oops! no more cats available! this event isn't possible
                    return {}
                else:
                    # still some possibilities, let's try the next!
                    continue
            # if we got here, then this cat works!
            temp_involved_cats[abbr] = _temp_cats[abbr]

    # there weren't any possible cats, so we'll create a new one if we're allowed
    else:
        # we don't need to check relationship constraints if we're making a new cat
        if "n_c" in abbr and "can_create_new_cat" in cat_constraints:
            temp_involved_cats[abbr] = updated_create_new_cat(
                option_dict=cat_constraints,
                involved_cats=temp_involved_cats,
                other_clan=other_clan,
            )
            if len(temp_involved_cats[abbr]) == 1:
                # if this is a list of a single cat, then we take them out of the list
                temp_involved_cats[abbr] = temp_involved_cats[abbr][0]
        else:
            # if we aren't allowed to make a new one, then we can't do this event
            return {}

    return temp_involved_cats


def _get_multi_cats(
    involved_cats: dict,
    interactable_cats: list[Cat],
    event: TextPoolEvent,
    cat_constraints: InvolvedCatDict,
    possible_injuries: list,
) -> list[Cat]:
    """
    Finds and returns multiple available cats for use as a group in the event.
    """
    # find out how many cats we'll allow
    max_cats = random.choice(get_config("relationship.group_events.multi_cat_amounts"))
    chosen_cats = []

    # get the cats who qualify
    possible_cats = cat_for_event(
        cat_constraints,
        interactable_cats,
        event.tags,
        involved_cat_dict=involved_cats,
        injuries=possible_injuries,
        return_list=True,
        return_id=False,
    )
    # if not enough possible cats, return empty list
    if not possible_cats or len(possible_cats) <= 1:
        return []

    involved_cats["multi_cat"] = []  # set this up ahead of time

    # if relationships aren't required, then we just pick some cats and go!
    if not event.relationship_constraint:
        chosen_cats = random.sample(possible_cats, min(len(possible_cats), max_cats))
        return chosen_cats

    # now we need to find who qualifies for the relationship constraints
    while len(chosen_cats) < max_cats and possible_cats:
        cat = random.choice(possible_cats)

        # copy up so that it's easier to pass this and test it, but we can still go back to the OG dict if it fails
        _temp_involved_cats = involved_cats.copy()
        _temp_involved_cats["multi_cat"].append(cat)

        # no matter what, cat is no longer allowed in the possible_cats list
        possible_cats.remove(cat)

        # find out if this cat will match the rel constraints
        if not all(
            check_rel_constraint_groups(block, _temp_involved_cats)
            for block in event.relationship_constraint
            if "multi_cat" in block["cats_from"] + block["cats_to"]
        ):
            _temp_involved_cats["multi_cat"].remove(cat)
            continue

        # if we're here, then this is a valid cat! we move on
        chosen_cats.append(cat)

    # if we didn't find enough cats, then return empty list
    if not chosen_cats or len(chosen_cats) <= 1:
        return []
    # otherwise, return all the cats we found!
    return chosen_cats
