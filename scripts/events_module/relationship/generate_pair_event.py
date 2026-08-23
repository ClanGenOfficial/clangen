from random import choice, choices
from typing import Optional, Literal

import i18n

from scripts.cat.cats import Cat
from scripts.cat.enums import CatCompatibility, CatRank
from scripts.cat_relations.enums import RelType
from scripts.cat_relations.relationship import Relationship
from scripts.config import get_config
from scripts.events_module.event_information import EventInformation
from scripts.events_module.consequences import change_relationship_values
from scripts.events_module.event_filters import (
    get_personality_compatibility,
)
from scripts.events_module.text_adjust import process_text
from scripts.events_module.text_pool_event.event_retrieval import (
    get_valid_event,
    load_text_pool_events,
)
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import game


# TRIGGER
def trigger_interaction(
    main_cat: Cat,
    other_cat: Cat,
    specific_type: Optional[RelType] = None,
    is_joining: bool = False,
) -> bool:
    """
    Start an interaction between two cats
    :param main_cat: The main cat that the event revolves around
    :param other_cat: The other cat that the event revolves around
    :param specific_type: Use to specify if the event must change a certain aspect of the relationship
    :param is_joining: Set True if generated interaction should be "joining" instead of "normal"
    :return: True if interaction occurred, False otherwise
    """
    # only interact between two player clan cats
    if (
        not main_cat.status.alive_in_player_clan
        or not other_cat.status.alive_in_player_clan
    ):
        return False
    # no interacting with self
    if main_cat == other_cat:
        return False

    # make sure a relationship exists
    if other_cat.ID not in main_cat.relationships:
        _create_relationship(main_cat, other_cat)

    existing_relationship = main_cat.relationships[other_cat.ID]

    # get pos or negative
    type_of_change = _get_type_of_change(main_cat, other_cat, existing_relationship)
    type_of_interaction = (
        _get_type_of_interaction(
            main_cat, other_cat, existing_relationship, type_of_change
        )
        if not specific_type
        else specific_type
    )
    # pick how intense the change is
    intensity_chances = get_config("relationship.pair_events.intensity_chances")
    chosen_intensity = choices(
        list(intensity_chances.keys()), list(intensity_chances.values())
    )[0]

    path = f"events/relationship_events/{'joining_interactions' if is_joining else 'normal_interactions'}/{type_of_interaction}/{chosen_intensity}/{type_of_change}.json"
    events = load_text_pool_events(path)

    # find valid event
    chosen_event = _get_event(events, main_cat, other_cat)

    involved_cats = {
        "m_c": main_cat,
        "r_c": other_cat,
    }

    # resolve event
    if not chosen_event:
        return False
    else:
        _resolve_event(
            chosen_event,
            chosen_intensity,
            involved_cats,
            type_of_change,
            type_of_interaction,
            existing_relationship,
        )
        return True


def _create_relationship(main_cat: Cat, other_cat: Cat):
    """
    Creates a relationship between the two cats if one did not already exist.
    """

    main_cat.relationships[other_cat.ID] = Relationship(main_cat, other_cat)
    main_cat.relationships[other_cat.ID].link_relationship()


# GET
def _get_type_of_change(
    main_cat: Cat, other_cat: Cat, relationship: Relationship
) -> Literal["positive", "negative"]:
    """
    Returns if the change will be positive or negative
    :param main_cat: The main cat that the event revolves around
    :param other_cat: The other cat involved in the event
    :param relationship: Main cat's relationship object for other_cat
    :return: "positive" or "negative"
    """
    # base for non-existing like
    bool_ballot = [True, False]

    # take personality in count
    comp = get_personality_compatibility(main_cat, other_cat)
    if comp == CatCompatibility.POSITIVE:
        bool_ballot.append(True)
    elif comp == CatCompatibility.NEGATIVE:
        bool_ballot.append(False)

    if (
        get_config("relationship.deputy_to_leader_neg_buff")
        and main_cat.status.rank == CatRank.DEPUTY
        and other_cat.status.is_leader
    ):
        bool_ballot.append(False)

    # further influence the partition based on the relationship
    for value in (
        relationship.like,
        relationship.respect,
        relationship.comfort,
        relationship.trust,
    ):
        # each 20th above 0 adds another True
        if value > 0:
            bool_ballot += [True] * int(value / 20)
        # each 20th below 0
        else:
            bool_ballot += [False] * int(abs(value) / 20)

    return "positive" if choice(bool_ballot) else "negative"


def _get_type_of_interaction(
    main_cat: Cat,
    other_cat: Cat,
    relationship: Relationship,
    type_of_change: Literal["positive", "negative"],
) -> RelType:
    """
    Returns the relationship type that will be influenced by this event
    :param main_cat: The main cat that the event revolves around
    :param other_cat: The other cat involved in the event
    :param relationship: Main cat's relationship object for other_cat
    :param type_of_change: "positive" or "negative" depending on how the relationship is changing
    :return: The chosen RelType
    """
    is_positive: bool = True if type_of_change == "positive" else False

    value_weights: dict[RelType, int] = {v: 1 for v in [*RelType]}

    # add a neg deputy change, this is a 0 unless a cruel card is in play
    if (
        not is_positive
        and main_cat.status.rank == CatRank.DEPUTY
        and other_cat.status.is_leader
    ):
        value_weights[RelType.RESPECT] += get_config(
            "relationship.deputy_envy_leader_influence"
        )

    # change the weights according if the interaction should be positive or negative
    # existing rel values determine the weight added
    for attr, rel_type in zip(
        [getattr(relationship, r) for r in [*RelType]], [*RelType]
    ):
        if is_positive:
            if attr > 0:
                value_weights[rel_type] += int(attr / 10)
        else:
            if rel_type == RelType.ROMANCE:
                continue
            if attr > 0:
                value_weights[rel_type] += int(abs(attr / 10))

    # increase the chance of a romance interaction if they are already mates
    if other_cat.ID in main_cat.mate:
        value_weights[RelType.ROMANCE] += 1
    else:
        # if a romance relationship is not possible, remove this type, but only if there are no mates
        # if there already mates (set up by the user for example), don't remove this type
        mate_from_to = main_cat.is_potential_mate(other_cat, for_love_interest=True)
        mate_to_from = main_cat.is_potential_mate(other_cat, for_love_interest=True)
        if not mate_from_to or not mate_to_from:
            while RelType.ROMANCE in value_weights:
                value_weights.pop(RelType.ROMANCE)

    # if cats have no romance relationship already, don't allow romance decrease
    if (
        not is_positive
        and RelType.ROMANCE in value_weights
        and not relationship.romance
    ):
        value_weights.pop(RelType.ROMANCE)

    chosen_type = choices(
        [value for value in value_weights.keys()],
        [weight for weight in value_weights.values()],
    )[0]

    return chosen_type


def _get_event(
    events: list[TextPoolEvent], main_cat: Cat, other_cat: Cat
) -> TextPoolEvent:
    """
    Returns a valid event for all involved cats
    :param events: The list of events to filter
    :param main_cat: The main cat that the event revolves around
    :param other_cat: The other cat involved in the event
    :return: A TextPoolEvent valid for both cats and current game state
    """

    # this is its own function so that we can test
    # attempt to find a valid event where we can fill the other roles
    other_clan = (
        (choice(game.clan.all_other_clans) if game.clan.all_other_clans else None)
        if game.clan
        else None
    )
    chosen_event, involved_cats = get_valid_event(
        primary_cat=main_cat,
        involved_cats={"m_c": main_cat, "r_c": other_cat},
        interactable_cats=[other_cat],
        possible_events=events,
        other_clan=other_clan,
        frequency_active=False,
    )

    return chosen_event


def _get_change_amount(
    is_positive: bool,
    intensity: Literal["low", "medium", "high"],
    relationship: Relationship,
) -> int:
    """
    Finds and returns the int amount that the relationship type will change by according to given intensity and additional modifiers

    :param is_positive: Set to True if the change should be a positive number, False if it should be negative
    :param intensity: "low", "medium", or "high" depending on how large the change should be
    :param relationship: Main cat's relationship object for other_cat
    :return: The int amount that the relationship type should change by
    """
    # get the normal amount
    amount = get_config(f"relationship.value_change_amount.{intensity}")
    if not is_positive:
        amount = amount * -1

    compatible_effect = get_config(f"relationship.compatibility_effect")

    # take compatibility into account
    compatibility = get_personality_compatibility(
        relationship.cat_from, relationship.cat_to
    )
    if compatibility == CatCompatibility.NEUTRAL:
        amount = amount
    elif compatibility == CatCompatibility.POSITIVE:
        amount += compatible_effect
    else:
        # negative compatibility
        amount -= compatible_effect
    return amount


# RESOLVE
def _resolve_event(
    event: TextPoolEvent,
    intensity: Literal["low", "medium", "high"],
    involved_cats: dict[str, Cat],
    type_of_change: Literal["positive", "negative"],
    type_of_interaction: RelType,
    relationship: Relationship,
):
    """
    Handles resolving all the consequences of the event as well as formatting the string and adding it to the events list
    :param intensity: "low", "medium", or "high" depending on how large the change should be
    :param involved_cats: The dictionary of involved cats. Key is the string abbreviation for the cat and value is the cat object
    :param type_of_change: "positive" or "negative" depending on how the relationship is changing
    :param type_of_interaction: The main RelType that is being affected
    :param relationship: Main cat's relationship object for other_cat
    """
    event_string = choice(event.strings)

    # FORMATTING
    replace_dict = {
        abbr: (str(c.name), choice(c.pronouns)) for abbr, c in involved_cats.items()
    }
    # replace their abbreviations
    event_string = process_text(event_string, replace_dict)
    # add the postscript text
    event_string = i18n.t(
        f"relationships.{type_of_change}_postscript_{intensity}",
        text=event_string,
    )

    # EVENT LIST
    # collect cat IDs for the involved cat buttons
    cat_ids = [c.ID for c in involved_cats.values()]
    # append the event to the events list!
    game.cur_events_list.append(
        EventInformation(event_string, ["relation", "interaction"], cat_ids)
    )

    # APPLY INFLUENCE ON RELATIONSHIPS
    _apply_base_influence(
        intensity, relationship, type_of_change, type_of_interaction, event_string
    )
    _apply_extra_influence(event, involved_cats, relationship, event_string)


def _apply_extra_influence(
    event: TextPoolEvent,
    involved_cats: dict[str, Cat],
    relationship: Relationship,
    chosen_string: str,
):
    """
    Applies any additional relationship influence that was specified by the event
    :param event: the object for the event
    :param involved_cats: The dictionary of involved cats. Key is the string abbreviation for the cat and value is the cat object
    :param relationship: Main cat's relationship object for other_cat
    :param chosen_string: The string that was chosen for this event
    """
    if relationship.opposite_relationship is None:
        relationship.link_relationship()
    for change in event.relationship_changes:
        # get the cats_from
        cats_from = [involved_cats[c] for c in change["cats_from"]]

        # get the cats_to
        cats_to = [involved_cats[c] for c in change["cats_to"]]

        # find the values and their amounts for the kwargs
        value_changes = {}
        for value in change["values"]:
            value_changes[value] = change["amount"]

        # change the relationship!
        # only apply log if this is a change to r_c's feelings, cus m_c will already have the event in their log, and we don't want to double it
        change_relationship_values(
            cats_from=cats_from,
            cats_to=cats_to,
            **value_changes,
            log=chosen_string if involved_cats["r_c"] in cats_from else None,
        )


def _apply_base_influence(
    intensity: Literal["low", "medium", "high"],
    relationship: Relationship,
    type_of_change: Literal["positive", "negative"],
    type_of_interaction: RelType,
    chosen_string: str,
):
    """
    Applies the base influence for this event.
    :param intensity: "low", "medium", or "high" depending on how large the change should be
    :param relationship: Main cat's relationship object for other_cat
    :param type_of_change: "positive" or "negative" depending on how the relationship is changing
    :param type_of_interaction: The main RelType that is being affected
    :param chosen_string: The string that was chosen for this event
    """
    amount = _get_change_amount(
        is_positive=type_of_change == "positive",
        intensity=intensity,
        relationship=relationship,
    )
    setattr(
        relationship,
        type_of_interaction,
        getattr(relationship, type_of_interaction) + amount,
    )

    relationship.log.append(
        i18n.t(
            "relationships.age_postscript",
            text=chosen_string,
            name=str(relationship.cat_from.name),
            count=relationship.cat_from.moons,
        )
    )
