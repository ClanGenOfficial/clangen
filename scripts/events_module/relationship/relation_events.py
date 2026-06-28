import random
from random import choice
from typing import Optional

from scripts.cat_relations.enums import RelType
from scripts.config import get_config
from scripts.game_structure import constants
from scripts.events_module.relationship import (
    generate_group_event,
    generate_pair_event,
)
from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank, CatAge
from scripts.events_module.relationship.romantic_events import RomanticEvents
from scripts.events_module.relationship.welcoming_events import Welcoming_Events
from scripts.events_module.event_filters import filter_relationship_type
from scripts.clan_package.get_clan_cats import (
    get_cats_same_age,
    get_possible_mates,
)


class Relation_Events:
    """All relationship events."""

    cats_triggered_events = {}

    @staticmethod
    def handle_relationships(cat: Cat):
        """Checks the relationships of the cat and trigger additional events if possible.

        Parameters
        ----------
        cat : Cat
            the cat where the relationships should be checked

        Returns
        -------
        """
        if not cat.relationships or cat.age == CatAge.NEWBORN:
            return

        Relation_Events.random_cat_events(cat)

        if not int(random.random() * get_config("relationship.chance_of_group_event")):
            Relation_Events.group_events(cat)

        Relation_Events.same_age_events(cat)

        # 1/16 for an additional event
        if not random.getrandbits(4):
            Relation_Events.romantic_events(cat)

        RomanticEvents.handle_mating_and_breakup(cat)

    # ---------------------------------------------------------------------------- #
    #                                new event types                               #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def random_cat_events(cat):
        """Randomly choose a cat of the Clan and have an interaction with them."""

        cats_to_choose = [
            c
            for c in Cat.all_cats.values()
            if c.ID != cat.ID
            and c.status.alive_in_player_clan
            and c.age != CatAge.NEWBORN
        ]
        # if there are no cats to interact, stop
        if not cats_to_choose:
            return

        other_cat = choice(cats_to_choose)
        Relation_Events.trigger_pair_event(cat, other_cat)

    @staticmethod
    def romantic_events(cat):
        """
        ONLY for cat OLDER than 12 moons.
        To increase mating chance this function is used.
        It will boost the romantic values of either mate or possible mates.
        This also increase the chance of affairs.
        """
        if cat.moons < 12:
            return

        if not Relation_Events.can_trigger_events(cat):
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
                cat.create_one_relationship(inter_cat)
            if cat.ID not in inter_cat.relationships:
                inter_cat.create_one_relationship(cat)

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
        Relation_Events.trigger_pair_event(cat, other_cat, RelType.ROMANCE)

    @staticmethod
    def same_age_events(cat):
        """
        To increase the relationship amounts with cats of the same age.
        This should lead to 'friends', 'enemies' and possible mates around the same age group.
        """
        if not Relation_Events.can_trigger_events(cat):
            return

        # gets cats who are within an age range. range is either 40% their current moon age OR 40 moons, whichever is smaller
        same_age_cats = get_cats_same_age(
            Cat, cat, min(constants.CONFIG["mates"]["age_range"], int(cat.moons * 0.4))
        )
        if [c for c in same_age_cats if c.age == CatAge.NEWBORN]:
            pass
        if len(same_age_cats) > 0:
            other_cat = choice(same_age_cats)
            if (
                Relation_Events.can_trigger_events(other_cat)
                and other_cat.ID in cat.relationships
            ):
                Relation_Events.trigger_pair_event(cat, other_cat)

    @staticmethod
    def trigger_pair_event(cat, other_cat, specific_type: Optional[RelType] = None):
        """
        Triggers a relationship event between two cats
        :param cat: The main cat involved
        :param other_cat: The other cat involved
        :param specific_type: The main RelType to influence
        """
        successful = generate_pair_event.trigger_interaction(
            main_cat=cat, other_cat=other_cat, specific_type=specific_type
        )

        if not successful:
            return

        # handle contact with ill cat if
        if cat.is_ill():
            other_cat.contact_with_ill_cat(cat)
        if other_cat.is_ill():
            cat.contact_with_ill_cat(other_cat)
        Relation_Events.update_events_triggered_count(cat)
        Relation_Events.update_events_triggered_count(other_cat)

    @staticmethod
    def group_events(cat):
        """
        This function triggers group events, based on the given cat.
        First it will be decided if a special type of group (found in relationship_events/group_interactions/group_types.json).
        As default all cats will be a possible 'group' of interaction.
        """
        if not Relation_Events.can_trigger_events(cat):
            return

        possible_interaction_cats = [
            c
            for c in Cat.all_cats_list
            if c.status.alive_in_player_clan
            and not c.status.rank == CatRank.NEWBORN
            and c != cat
            and Relation_Events.can_trigger_events(cat)
        ]

        interacted_cat_ids = generate_group_event.trigger_interaction(
            main_cat=cat,
            interactable_cats=possible_interaction_cats,
        )

        for i in interacted_cat_ids:
            inter_cat = Cat.all_cats[i]
            Relation_Events.update_events_triggered_count(inter_cat)

    @staticmethod
    def welcome_new_cats(new_cats=None):
        """This function will handle the welcome of new cats, if there are new cats in the clan."""
        if new_cats is None or len(new_cats) <= 0:
            return

        for new_cat in new_cats:
            same_age_cats = get_cats_same_age(
                Cat,
                new_cat,
                min(constants.CONFIG["mates"]["age_range"], int(new_cat.moons * 0.4)),
            )
            alive_cats = [
                i for i in new_cat.all_cats.values() if i.status.alive_in_player_clan
            ]
            number = constants.CONFIG["new_cat"]["cat_amount_welcoming"]

            if len(alive_cats) == 0:
                return
            elif number > len(same_age_cats) > 0:
                for age_cat in same_age_cats:
                    Welcoming_Events.welcome_cat(age_cat, new_cat)

                rest_number = number - len(same_age_cats)
                same_age_ids = [c.ID for c in same_age_cats]
                alive_cats = [
                    alive_cat
                    for alive_cat in alive_cats
                    if alive_cat.ID not in same_age_ids
                ]

                chosen_rest = random.choices(population=alive_cats, k=len(alive_cats))
                if rest_number >= len(alive_cats):
                    chosen_rest = random.choices(population=alive_cats, k=rest_number)
                for inter_cat in chosen_rest:
                    Welcoming_Events.welcome_cat(inter_cat, new_cat)
            elif len(same_age_cats) >= number:
                chosen = random.choices(population=same_age_cats, k=number)
                for chosen_cat in chosen:
                    Welcoming_Events.welcome_cat(chosen_cat, new_cat)
            elif len(alive_cats) <= number:
                for alive_cat in alive_cats:
                    Welcoming_Events.welcome_cat(alive_cat, new_cat)
            else:
                chosen = random.choices(population=alive_cats, k=number)
                for chosen_cat in chosen:
                    Welcoming_Events.welcome_cat(chosen_cat, new_cat)

    # ---------------------------------------------------------------------------- #
    #                                helper function                               #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def cats_with_relationship_constraints(main_cat, constraint):
        """Returns a list of cats, where the relationship from main_cat towards the cat fulfill the given constraints."""
        cat_list = list(
            filter(
                lambda cat: cat.status.alive_in_player_clan,
                Cat.all_cats.values(),
            )
        )
        cat_list.remove(main_cat)
        filtered_cat_list = []

        for inter_cat in cat_list:
            if inter_cat.ID == main_cat.ID:
                continue

            cat_from = main_cat
            cat_to = inter_cat

            if cat_to.ID not in cat_from.relationships:
                cat_from.create_one_relationship(cat_to)
                if cat_from.ID not in cat_to.relationships:
                    cat_to.create_one_relationship(cat_from)
                continue

            passed = filter_relationship_type(
                group=[cat_from, cat_to], filter_types=constraint
            )

            if not passed:
                continue

            filtered_cat_list.append(inter_cat)

        return filtered_cat_list

    @staticmethod
    def update_events_triggered_count(cat):
        if cat.ID in Relation_Events.cats_triggered_events:
            Relation_Events.cats_triggered_events[cat.ID] += 1
        else:
            Relation_Events.cats_triggered_events[cat.ID] = 1

    @staticmethod
    def can_trigger_events(cat):
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

        if cat.ID not in Relation_Events.cats_triggered_events:
            return True

        return Relation_Events.cats_triggered_events[cat.ID] < threshold

    @staticmethod
    def clear_trigger_dict():
        """Cleans the trigger dictionary, this function should be called every new moon."""
        Relation_Events.cats_triggered_events = {}


# ---------------------------------------------------------------------------- #
#                                load resources                                #
# ---------------------------------------------------------------------------- #
