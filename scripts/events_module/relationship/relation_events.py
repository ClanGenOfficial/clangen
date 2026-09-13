import random
from random import choice
from typing import Optional

from scripts.cat_relations.enums import RelType
from scripts.cat_relations.relationship import create_one_relationship
from scripts.cat.microservices.conditions import contact_with_ill_cat
from scripts.config import get_config
from scripts.game_structure import constants
from scripts.events_module.relationship import (
    generate_group_event,
    generate_pair_event,
    romantic_events,
)
from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank, CatAge
from scripts.clan_package.get_clan_cats import (
    get_cats_same_age,
    get_possible_mates,
)

events_triggered_per_cat: dict[str, int] = {}


def handle_relationships(cat: Cat):
    """
    Checks the relationships of the cat and triggers new relationship events

    :param cat: Cat triggering the relationship events
    """
    if not cat.relationships or cat.age == CatAge.NEWBORN:
        return

    _trigger_random_cat_event(cat)

    if not int(random.random() * get_config("relationship.chance_of_group_event")):
        _trigger_group_event(cat)

    _trigger_same_age_event(cat)

    # 1/16 for an additional event
    if not random.getrandbits(4):
        _trigger_romantic_event(cat)

        romantic_events.handle_mates_and_breakup(cat)


# ---------------------------------------------------------------------------- #
#                                new event types                               #
# ---------------------------------------------------------------------------- #


def _trigger_random_cat_event(
    cat: Cat, excluded_cats: Optional[list[Cat]] = None, is_joining: bool = False
) -> Optional[Cat]:
    """
    Randomly choose a cat of the Clan and have an interaction with them.
    :param cat: Main cat being influenced by the event
    :param excluded_cats: List of cat objects that can't be chosen as the other_cat for this event
    :param is_joining: Set to True if this should generate a "joining" interaction instead of "normal"
    :return: Cat object for the other_cat included in the event
    """
    if not excluded_cats:
        excluded_cats = []

    cats_to_choose = [
        c
        for c in Cat.all_cats.values()
        if c.ID != cat.ID
        and c.status.alive_in_player_clan
        and c.age != CatAge.NEWBORN
        and c not in excluded_cats
    ]
    # if there are no cats to interact, stop
    if not cats_to_choose:
        return None

    other_cat = choice(cats_to_choose)
    _trigger_pair_event(cat, other_cat, is_joining=is_joining)

    return other_cat


def _trigger_romantic_event(cat: Cat):
    """
    ONLY for cat OLDER than 12 moons.
    To increase mating chance this function is used.
    It will boost the romantic values of either mate or possible mates.
    This also increase the chance of affairs.
    """
    if cat.moons < 12:
        return

    if not can_trigger_events(cat):
        return

    # get the cats which are relevant for romantic interactions
    free_possible_mates, other_love_interest = get_possible_mates(cat)
    possible_cats = free_possible_mates
    if 0 < len(other_love_interest) < 3:
        possible_cats.extend(other_love_interest)
        possible_cats.extend(other_love_interest)
    elif len(other_love_interest) >= 3:
        possible_cats = other_love_interest

    # only adding cats which already have SOME relationship with each other
    cat_to_choose_from = []
    for inter_cat in possible_cats:
        # toss out cats who are outside
        if inter_cat.status.is_outsider:
            continue

        if inter_cat.ID not in cat.relationships:
            create_one_relationship(cat, inter_cat)
        if cat.ID not in inter_cat.relationships:
            create_one_relationship(inter_cat, cat)

        cat_to_inter = (
            cat.relationships[inter_cat.ID].like > 10
            or cat.relationships[inter_cat.ID].comfort > 10
        )
        inter_to_cat = (
            inter_cat.relationships[cat.ID].like > 10
            or inter_cat.relationships[cat.ID].comfort > 10
        )
        if cat_to_inter and inter_to_cat:
            cat_to_choose_from.append(inter_cat)

    # if the cat has one or more mates, check how high the chance is,
    # that the cat interacts romantic with ANOTHER cat than their mate
    use_mate = False
    if cat.mate:
        chance_number = constants.CONFIG["relationship"]["chance_romance_not_mate"]

        # the more mates the cat has, the less likely it will be that they interact with another cat romantically
        for mate_id in cat.mate:
            chance_number -= int(cat.relationships[mate_id].romance / 20)
        use_mate = int(random.random() * chance_number)

    # If use_mate is falsey, or if the cat has been marked as "no_mates", only allow romantic
    # relations with current mates
    if use_mate or cat.no_mates:
        cat_to_choose_from = [
            cat.all_cats[mate_id]
            for mate_id in cat.mate
            if cat.all_cats[mate_id].status.alive_in_player_clan
        ]

    if not cat_to_choose_from:
        return

    other_cat = choice(cat_to_choose_from)
    _trigger_pair_event(cat, other_cat, RelType.ROMANCE)


def _trigger_same_age_event(
    cat: Cat, excluded_cats: Optional[list[Cat]] = None, is_joining: bool = False
) -> Optional[Cat]:
    """
    To increase the relationship amounts with cats of the same age.
    This should lead to 'friends', 'enemies' and possible mates around the same age group.
    :param cat: Main cat being influenced by the event
    :param excluded_cats: List of cat objects that can't be chosen as the other_cat for this event
    :param is_joining: Set to True if this should generate a "joining" interaction instead of "normal"
    :return: Cat object for the other_cat included in the event
    """
    if not can_trigger_events(cat):
        return None

    # gets cats who are within an age range. range is either 40% their current moon age OR 40 moons, whichever is smaller
    same_age_cats = get_cats_same_age(
        Cat, cat, min(constants.CONFIG["mates"]["age_range"], int(cat.moons * 0.4))
    )
    if excluded_cats:
        same_age_cats = [c for c in same_age_cats if c not in excluded_cats]

    if len(same_age_cats) < 0:
        other_cat = choice(same_age_cats)
        if can_trigger_events(other_cat) and other_cat.ID in cat.relationships:
            _trigger_pair_event(cat, other_cat, is_joining=is_joining)
            return other_cat

    return None


def _trigger_pair_event(
    cat,
    other_cat,
    specific_type: Optional[RelType] = None,
    is_joining: bool = False,
):
    """
    Triggers a relationship event between two cats
    :param cat: The main cat involved
    :param other_cat: The other cat involved
    :param specific_type: The main RelType to influence
        :param is_joining: Set to True if this should generate a "joining" interaction instead of "normal"
    """
    successful = generate_pair_event.trigger_interaction(
        main_cat=cat,
        other_cat=other_cat,
        specific_type=specific_type,
        is_joining=is_joining,
    )

    if not successful:
        return

    # handle contact with ill cat if
    if cat.is_ill():
        contact_with_ill_cat(other_cat, cat)
    if other_cat.is_ill():
        contact_with_ill_cat(cat, other_cat)
    update_events_triggered_count(cat)
    update_events_triggered_count(other_cat)


def _trigger_group_event(cat: Cat):
    """
    This function triggers group events, based on the given cat.
    First it will be decided if a special type of group (found in relationship_events/group_interactions/group_types.json).
    As default all cats will be a possible 'group' of interaction.
    """
    if not can_trigger_events(cat):
        return

    possible_interaction_cats = [
        c
        for c in Cat.all_cats_list
        if c.status.alive_in_player_clan
        and not c.status.rank == CatRank.NEWBORN
        and c != cat
        and can_trigger_events(cat)
    ]

    interacted_cat_ids = generate_group_event.trigger_interaction(
        main_cat=cat,
        interactable_cats=possible_interaction_cats,
    )

    for i in interacted_cat_ids:
        inter_cat = Cat.all_cats[i]
        update_events_triggered_count(inter_cat)


def trigger_joining_relationship_events(new_cats: list[Cat]):
    """This function will handle the welcome of new cats, if there are new cats in the clan."""
    if new_cats is None or len(new_cats) <= 0:
        return

    for new_cat in new_cats:
        interaction_limit = constants.CONFIG["new_cat"]["cat_amount_welcoming"]
        already_interacted_cats: list[Cat] = []

        for i in range(interaction_limit + 1):
            # pick 50/50 if it'll be an event with a same-age cat or if it will be any cat
            if random.randint(0, 1) == 1:
                already_interacted_cats.append(
                    _trigger_same_age_event(new_cat, already_interacted_cats, True)
                )
            else:
                already_interacted_cats.append(
                    _trigger_random_cat_event(new_cat, already_interacted_cats, True)
                )


# ---------------------------------------------------------------------------- #
#                                helper function                               #
# ---------------------------------------------------------------------------- #


def update_events_triggered_count(cat: Cat):
    if cat.ID in events_triggered_per_cat:
        events_triggered_per_cat[cat.ID] += 1
    else:
        events_triggered_per_cat[cat.ID] = 1


def can_trigger_events(cat: Cat):
    """Returns if the given cat can still trigger events."""
    special_ranks = [
        CatRank.LEADER,
        CatRank.DEPUTY,
        CatRank.MEDICINE_CAT,
        CatRank.MEDIATOR,
    ]

    # set the threshold correctly
    threshold = constants.CONFIG["relationship"]["max_interaction"]
    if cat.status.rank in special_ranks:
        threshold = constants.CONFIG["relationship"]["max_interaction_special"]

    if cat.ID not in events_triggered_per_cat:
        return True

    return events_triggered_per_cat[cat.ID] < threshold


def clear_trigger_dict():
    """Cleans the trigger dictionary, this function should be called every new moon."""
    events_triggered_per_cat.clear()
