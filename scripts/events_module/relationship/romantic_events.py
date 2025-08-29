import random
from copy import deepcopy
from random import choice
from typing import Dict, List

import i18n

import scripts.cat_relations.interaction as interactions
from scripts.cat.cats import Cat
from scripts.cat_relations.relationship import RelType
from scripts.event_class import Single_Event
from scripts.game_structure import constants
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource
from scripts.utility import (
    get_highest_romantic_relation,
    event_text_adjust,
    get_personality_compatibility,
    process_text,
)


class RomanticEvents:
    """
    All events which are related to mates such as becoming mates and breakups,
    but also for possible mates and romantic interactions.
    """

    # ---------------------------------------------------------------------------- #
    #                                LOAD RESOURCES                                #
    # ---------------------------------------------------------------------------- #

    MATE_DICTS = {}
    BREAKUP_STRINGS = {}
    POLY_MATE_DICTS = {}
    current_loaded_lang = None
    ROMANTIC_EVENTS: Dict = {}
    ROMANTIC_INTERACTIONS: Dict = {}
    MATE_INTERACTIONS: Dict[str, List] = {}
    MATE_RELEVANT_INTERACTIONS: Dict[str, Dict[str, List]] = {}
    ROMANTIC_RELEVANT_INTERACTIONS: Dict[str, Dict[str, List]] = {}

    @classmethod
    def rebuild_dicts(cls):
        """
        Rebuild the event dicts after a language change.
        """
        if RomanticEvents.current_loaded_lang == i18n.config.get("locale"):
            return

        resources = [
            ("MATE_DICTS", "become_mates.json"),
            ("BREAKUP_STRINGS", "breakup_mates.json"),
            (
                "POLY_MATE_DICTS",
                "become_mates_poly.json",
            ),
        ]
        for resource, location in resources:
            setattr(
                cls,
                resource,
                load_lang_resource(f"events/relationship_events/{location}"),
            )

        RomanticEvents.current_loaded_lang = i18n.config.get("locale")
        interactions.rebuild_relationship_dicts()

        # ---------------------------------------------------------------------------- #
        #            build up dictionaries which can be used for moon events           #
        #         because there may be less romantic/mate relevant interactions,       #
        #        the dictionary will be ordered in only 'positive' and 'negative'      #
        # ---------------------------------------------------------------------------- #

        # ---------------------------------------------------------------------------- #
        #                                     MATE                                     #
        # ---------------------------------------------------------------------------- #

        # Use the overall master interaction dictionary and filter for mate tag
        cls.MATE_RELEVANT_INTERACTIONS: Dict[str, Dict[str, List]] = {}
        for val_type, dictionary in interactions.INTERACTION_MASTER_DICT.items():
            cls.MATE_RELEVANT_INTERACTIONS[val_type] = {}
            cls.MATE_RELEVANT_INTERACTIONS[val_type]["increase"] = list(
                filter(
                    lambda inter: "mates" in inter.relationship_constraint
                    and "not_mates" not in inter.relationship_constraint,
                    dictionary["increase"],
                )
            )
            cls.MATE_RELEVANT_INTERACTIONS[val_type]["decrease"] = list(
                filter(
                    lambda inter: "mates" in inter.relationship_constraint
                    and "not_mates" not in inter.relationship_constraint,
                    dictionary["decrease"],
                )
            )

        # resort the first generated overview dictionary to only "positive" and "negative" interactions
        cls.MATE_INTERACTIONS = {"positive": [], "negative": []}
        for val_type, dictionary in cls.MATE_RELEVANT_INTERACTIONS.items():
            cls.MATE_INTERACTIONS["positive"].extend(dictionary["increase"])
            cls.MATE_INTERACTIONS["negative"].extend(dictionary["decrease"])

        # ---------------------------------------------------------------------------- #
        #                                   ROMANTIC                                   #
        # ---------------------------------------------------------------------------- #

        # Use the overall master interaction dictionary and filter for any interactions, which requires a certain
        # amount of romance
        cls.ROMANTIC_RELEVANT_INTERACTIONS = {}
        for val_type, dictionary in interactions.INTERACTION_MASTER_DICT.items():
            cls.ROMANTIC_RELEVANT_INTERACTIONS[val_type] = {}

            # if it's the romance interaction type add all interactions
            if val_type == RelType.ROMANCE:
                cls.ROMANTIC_RELEVANT_INTERACTIONS[val_type]["increase"] = dictionary[
                    "increase"
                ]
                cls.ROMANTIC_RELEVANT_INTERACTIONS[val_type]["decrease"] = dictionary[
                    "decrease"
                ]
            else:
                cls.ROMANTIC_RELEVANT_INTERACTIONS[val_type]["increase"] = [
                    interaction
                    for interaction in dictionary["decrease"]
                    for tag in interaction.relationship_constraint
                    if RelType.ROMANCE in tag
                ]

                cls.ROMANTIC_RELEVANT_INTERACTIONS[val_type]["decrease"] = [
                    interaction
                    for interaction in dictionary["decrease"]
                    for tag in interaction.relationship_constraint
                    if RelType.ROMANCE in tag
                ]

        # resort the first generated overview dictionary to only "positive" and "negative" interactions
        cls.ROMANTIC_INTERACTIONS = {"positive": [], "negative": []}
        for val_type, dictionary in cls.ROMANTIC_RELEVANT_INTERACTIONS.items():
            cls.ROMANTIC_INTERACTIONS["positive"].extend(dictionary["increase"])
            cls.ROMANTIC_INTERACTIONS["negative"].extend(dictionary["decrease"])

    @staticmethod
    def start_interaction(cat_from, cat_to):
        """
        Filters and triggers events which are connected to romance between these two cats.

        Returns
        -------
        bool : if an event is triggered or not
        """
        if cat_from.ID == cat_to.ID:
            return False

        if RomanticEvents.current_loaded_lang != i18n.config.get("locale"):
            RomanticEvents.rebuild_dicts()
            RomanticEvents.current_loaded_lang = i18n.config.get("locale")

        relevant_dict = deepcopy(RomanticEvents.ROMANTIC_INTERACTIONS)
        if cat_to.ID in cat_from.mate and not cat_to.dead:
            relevant_dict = deepcopy(RomanticEvents.MATE_INTERACTIONS)

        # check if it should be a positive or negative interaction
        relationship = cat_from.relationships[cat_to.ID]
        positive = relationship.positive_interaction()

        # get the possible interaction list and filter them
        possible_interactions = (
            relevant_dict["positive"] if positive else relevant_dict["negative"]
        )
        filtered_interactions = relationship.get_relevant_interactions(
            possible_interactions
        )

        if not filtered_interactions:
            print(
                f"There were no romance interactions for: {cat_from.name} to {cat_to.name}"
            )
            return False

        # chose interaction
        chosen_interaction = choice(filtered_interactions)
        # check if the current interaction id is already used and us another if so
        id_check_list = filtered_interactions.copy()
        while (
            chosen_interaction.id in relationship.used_interaction_ids
            and len(id_check_list) > 2
        ):
            id_check_list.remove(chosen_interaction)
            # pick a new one if any are still available
            if id_check_list:
                chosen_interaction = choice(id_check_list)
            else:
                chosen_interaction = None

        # if we couldn't find a non-duplicate, we just pick any of them
        if not chosen_interaction:
            chosen_interaction = choice(filtered_interactions)

        # if the chosen_interaction is still in the TRIGGERED_SINGLE_INTERACTIONS, clean the list
        if chosen_interaction in relationship.used_interaction_ids:
            relationship.used_interaction_ids = []
        relationship.used_interaction_ids.append(chosen_interaction.id)

        # affect relationship - it should always be in a romantic way
        value_change = "increase" if positive else "decrease"
        rel_type = RelType.ROMANCE
        relationship.chosen_interaction = chosen_interaction
        relationship.interaction_affect_relationships(
            value_change, chosen_interaction.intensity, rel_type
        )

        # give cats injuries
        if len(chosen_interaction.get_injuries) > 0:
            for abbreviations, injury_dict in chosen_interaction.get_injuries.items():
                if "injury_names" not in injury_dict:
                    print(
                        f"ERROR: there are no injury names in the chosen interaction {chosen_interaction.id}."
                    )
                    continue

                injured_cat = cat_from
                if abbreviations != "m_c":
                    injured_cat = cat_to

                injuries = []
                for inj in injury_dict["injury_names"]:
                    injured_cat.get_injured(inj, True)
                    injuries.append(inj)

                possible_scar = (
                    injury_dict["scar_text"] if "scar_text" in injury_dict else None
                )
                possible_death = (
                    injury_dict["death_text"] if "death_text" in injury_dict else None
                )
                if injured_cat.status.is_leader:
                    possible_death = (
                        injury_dict["death_leader_text"]
                        if "death_leader_text" in injury_dict
                        else None
                    )

                if possible_scar or possible_death:
                    for condition in injuries:
                        injured_cat.history.add_possible_history(
                            condition,
                            death_text=possible_death,
                            scar_text=possible_scar,
                        )

        # get any possible interaction string out of this interaction
        interaction_str = choice(chosen_interaction.interactions)

        # prepare string for display
        cat_dict = {
            "m_c": (str(cat_from.name), choice(cat_from.pronouns)),
            "r_c": (str(cat_to.name), choice(cat_to.pronouns)),
        }
        interaction_str = process_text(interaction_str, cat_dict)

        # extract intensity from the interaction, defaults to "positive"
        intensity = getattr(chosen_interaction, "intensity", "positive")

        effect = ""
        if value_change == "increase":
            effect = f" ({intensity} positive effect)"
        if value_change == "decrease":
            effect = f" ({intensity} negative effect)"

        interaction_str = interaction_str + effect

        # send string to current moon relationship events before adding age of cats
        relevant_event_tabs = ["relation", "interaction"]
        if len(chosen_interaction.get_injuries) > 0:
            relevant_event_tabs.append("health")
        game.cur_events_list.append(
            Single_Event(
                interaction_str,
                relevant_event_tabs,
                [cat_to.ID, cat_from.ID],
                cat_dict={"m_c": cat_to, "r_c": cat_from},
            )
        )

        # now add the age of the cats before the string is sent to the cats' relationship logs
        relationship.log.append(
            interaction_str
            + i18n.t(
                "relationships.age_postscript", name=cat_from.name, count=cat_from.moons
            )
        )

        if not relationship.opposite_relationship and cat_from.ID != cat_to.ID:
            relationship.link_relationship()
            relationship.opposite_relationship.log.append(
                interaction_str
                + i18n.t(
                    "relationships.age_postscript",
                    name=str(cat_to.name),
                    count=cat_to.moons,
                )
            )

        return True

    @staticmethod
    def handle_mating_and_breakup(cat):
        """Handle events related to making new mates, and breaking up."""

        if cat.no_mates:
            return

        RomanticEvents.handle_moving_on(cat)
        RomanticEvents.handle_breakup_events(cat)
        RomanticEvents.handle_new_mate_events(cat)

    @staticmethod
    def handle_new_mate_events(cat):
        """Triggers and handles any events that result in a new mate"""

        # First, check high love confession
        flag = RomanticEvents.handle_confession(cat)
        if flag:
            return

        # Then, handle more random mating
        # Choose some subset of cats that they have relationships with
        if not cat.relationships:
            return
        subset = [
            Cat.fetch_cat(x)
            for x in cat.relationships
            if isinstance(Cat.fetch_cat(x), Cat)
            and Cat.fetch_cat(x).status.alive_in_player_clan
        ]
        if not subset:
            return

        subset = random.sample(subset, max(int(len(subset) / 3), 1))

        for other_cat in subset:
            relationship = cat.relationships.get(other_cat.ID)
            flag = RomanticEvents.handle_new_mates(cat, other_cat)
            if flag:
                return

    @staticmethod
    def handle_breakup_events(cat: Cat):
        """Triggers and handles any events that results in a breakup"""

        for x in cat.mate:
            mate_ob = Cat.fetch_cat(x)
            if not isinstance(mate_ob, Cat):
                continue

            flag = RomanticEvents.handle_breakup(cat, mate_ob)
            if flag:
                return

    @staticmethod
    def handle_moving_on(cat):
        """Handles moving on from dead or outside mates"""
        for mate_id in cat.mate:
            if mate_id not in Cat.all_cats:
                print(f"WARNING: Cat #{cat} has a invalid mate. It will be removed.")
                cat.mate.remove(mate_id)
                continue

            cat_mate = Cat.fetch_cat(mate_id)
            if cat_mate.no_mates:
                return

            # Move on from dead mates
            if (
                cat_mate
                and "grief stricken" not in cat.illnesses
                and (
                    (cat_mate.dead and cat_mate.dead_for >= 4)
                    or cat_mate.status.is_outsider
                )
            ):
                # randint is a slow function, don't call it unless we have to.
                if not cat_mate.no_mates and random.random() > 0.5:
                    text = i18n.t(
                        "hardcoded.move_on_dead_mate", mate=str(cat_mate.name)
                    )
                    game.cur_events_list.append(
                        Single_Event(
                            text, "relation", cat_dict={"m_c": cat, "r_c": cat_mate}
                        )
                    )
                    cat.unset_mate(cat_mate)

    @staticmethod
    def handle_new_mates(cat_from, cat_to) -> bool:
        """More in depth check if the cats will become mates."""

        become_mates, mate_string = RomanticEvents.check_if_new_mate(cat_from, cat_to)

        if become_mates and mate_string:
            cat_from.set_mate(cat_to)
            game.cur_events_list.append(
                Single_Event(
                    mate_string,
                    ["relation", "misc"],
                    cat_dict={"m_c": cat_from, "r_c": cat_to},
                )
            )
            return True

        return False

    @staticmethod
    def handle_breakup(cat_from: Cat, cat_to: Cat) -> bool:
        """Handles cats breaking up their relationship"""

        RomanticEvents.rebuild_dicts()

        if cat_from.ID not in cat_to.mate:
            return False

        if cat_from.no_mates or cat_to.no_mates:
            return False

        if cat_to.no_mates or cat_from.no_mates:
            return False

        if not RomanticEvents.check_if_breakup(cat_from, cat_to):
            return False

        # Determine if this is a nice breakup or a fight breakup
        # TODO - make this better
        breakup_type = random.choices(
            [
                "had_fight",
                "decided_to_be_friends",
                "lost_feelings",
                "bad_breakup",
                "chill_breakup",
            ],
            [3, 3, 2, 5, 5],
        )[0]

        cat_from.unset_mate(cat_to, breakup=False)

        if cat_to.ID in cat_from.relationships:
            relationship_from = cat_from.relationships[cat_to.ID]
        else:
            relationship_from = cat_from.create_one_relationship(cat_to)

        if cat_from.ID in cat_to.relationships:
            relationship_to = cat_to.relationships[cat_from.ID]
        else:
            relationship_to = cat_to.create_one_relationship(cat_from)

        # These are large decreases - they are to prevent becoming mates again on the same moon.
        if breakup_type == "had_fight":
            relationship_to.romance -= 15
            relationship_from.romance -= 15
            relationship_from.like -= 10
            relationship_to.like -= 10
            relationship_from.trust -= 10
            relationship_to.trust -= 10
        elif breakup_type == "decided_to_be_friends":
            relationship_to.romance -= 30
            relationship_from.romance -= 30
            relationship_from.like += 30
            relationship_to.like += 30
            relationship_from.trust += 20
            relationship_to.trust += 20
            relationship_to.comfort += 5
            relationship_from.comfort += 5
        elif breakup_type == "lost_feelings":
            relationship_to.romance -= 30
            relationship_from.romance -= 30
            relationship_from.like -= 10
            relationship_to.like -= 10
            relationship_to.comfort -= 10
            relationship_from.comfort -= 10
        elif breakup_type == "bad_breakup":
            relationship_to.romance -= 20
            relationship_from.romance -= 15
            relationship_from.like -= 10
            relationship_to.like -= 15
            relationship_from.trust -= 20
            relationship_to.trust -= 25
            relationship_to.comfort -= 20
            relationship_from.comfort -= 20
            relationship_to.respect -= 10
            relationship_from.respect -= 10
        elif breakup_type == "chill_breakup":
            relationship_to.romance -= 15
            relationship_from.romance -= 15
            relationship_to.comfort -= 10
            relationship_from.comfort -= 10

        text = choice(RomanticEvents.BREAKUP_STRINGS[breakup_type])
        text = event_text_adjust(Cat, text, main_cat=cat_from, random_cat=cat_to)
        game.cur_events_list.append(
            Single_Event(
                text,
                ["relation", "misc"],
                [cat_from.ID, cat_to.ID],
                cat_dict={"m_c": cat_from, "r_c": cat_to},
            )
        )
        return True

    @staticmethod
    def handle_confession(cat_from) -> bool:
        """
        Check if the cat has a high love for another and mate them if there are in the boundaries
        :param cat_from: cat in question

        return: bool if event is triggered or not
        """

        # get the highest romantic love relationships and
        rel_list = cat_from.relationships.values()
        highest_romantic_relation = get_highest_romantic_relation(
            rel_list, exclude_mate=True
        )
        if not highest_romantic_relation:
            return False

        condition = constants.CONFIG["mates"]["confession"]["make_confession"]
        if not RomanticEvents.relationship_fulfill_condition(
            highest_romantic_relation, condition
        ):
            return False

        cat_to = highest_romantic_relation.cat_to

        if cat_to.status.is_outsider != cat_from.status.is_outsider:
            return False

        if not cat_to.is_potential_mate(cat_from) or not cat_from.is_potential_mate(
            cat_to
        ):
            return False

        alive_inclan_from_mates = [
            mate for mate in cat_from.mate if cat_from.status.alive_in_player_clan
        ]
        alive_inclan_to_mates = [
            mate
            for mate in cat_to.mate
            if cat_to.fetch_cat(mate).status.alive_in_player_clan
        ]
        poly = len(alive_inclan_from_mates) > 0 or len(alive_inclan_to_mates) > 0

        if poly and not RomanticEvents.current_mates_allow_new_mate(cat_from, cat_to):
            return False

        become_mate = False
        condition = constants.CONFIG["mates"]["confession"]["accept_confession"]
        rel_to_check = highest_romantic_relation.opposite_relationship
        if not rel_to_check:
            highest_romantic_relation.link_relationship()
            rel_to_check = highest_romantic_relation.opposite_relationship

        if RomanticEvents.relationship_fulfill_condition(rel_to_check, condition):
            become_mate = True
            mate_string = RomanticEvents.get_mate_string(
                "high_romantic", poly, cat_from, cat_to
            )
        # second acceptance chance if the romantic is high enough
        elif (
            RelType.ROMANCE in condition
            and condition[RelType.ROMANCE] != 0
            and condition[RelType.ROMANCE] > 0
            and rel_to_check.romance >= condition[RelType.ROMANCE] * 1.5
        ):
            become_mate = True
            mate_string = RomanticEvents.get_mate_string(
                "high_romantic", poly, cat_from, cat_to
            )
        else:
            mate_string = RomanticEvents.get_mate_string(
                "rejected", poly, cat_from, cat_to
            )
            cat_from.relationships[cat_to.ID].romance -= 10
            cat_to.relationships[cat_from.ID].comfort -= 10

        mate_string = RomanticEvents.prepare_relationship_string(
            mate_string, cat_from, cat_to
        )
        game.cur_events_list.append(
            Single_Event(
                mate_string,
                ["relation", "misc"],
                cat_dict={"m_c": cat_from, "r_c": cat_to},
            )
        )

        if become_mate:
            cat_from.set_mate(cat_to)

        return True

    # ---------------------------------------------------------------------------- #
    #                          check if event is triggered                         #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def check_if_breakup(cat_from, cat_to):
        """More in depth check if the cats will break up.
        Returns:
            bool (True or False)
        """
        if cat_from.ID not in cat_to.mate:
            return False

        # Moving on, not breakups, occur when one mate is dead or outside.
        if (
            not cat_from.status.alive_in_player_clan
            or not cat_to.status.alive_in_player_clan
        ):
            return False

        chance_number = RomanticEvents.get_breakup_chance(cat_from, cat_to)
        if chance_number == 0:
            return False

        return not int(random.random() * chance_number)

    @staticmethod
    def check_if_new_mate(cat_from, cat_to):
        """Checks if the two cats can become mates, or not. Returns: boolean and event_string"""
        become_mates = False
        young_age = ("newborn", "kitten", "adolescent")
        if cat_to.status.is_outsider != cat_from.status.is_outsider:
            return False, None

        if not cat_from.is_potential_mate(cat_to):
            return False, None

        if cat_from.ID in cat_to.mate:
            return False, None

        # Gather relationships
        if cat_to.ID in cat_from.relationships:
            relationship_from = cat_from.relationships[cat_to.ID]
        else:
            relationship_from = cat_from.create_one_relationship(cat_to)

        if cat_from.ID in cat_to.relationships:
            relationship_to = cat_to.relationships[cat_from.ID]
        else:
            relationship_to = cat_to.create_one_relationship(cat_from)

        mate_string = None
        mate_chance = constants.CONFIG["mates"]["chance_fulfilled_condition"]
        hit = int(random.random() * mate_chance)

        # has to be high because every moon this will be checked for each relationship in the game
        friends_to_lovers = constants.CONFIG["mates"]["chance_friends_to_lovers"]
        random_hit = int(random.random() * friends_to_lovers)

        # already return if there is 'no' hit (everything above 0), other checks are not necessary
        if hit > 0 and random_hit > 0:
            return False, None

        alive_inclan_from_mates = [
            mate
            for mate in cat_from.mate
            if cat_from.fetch_cat(mate).status.alive_in_player_clan
        ]
        alive_inclan_to_mates = [
            mate
            for mate in cat_to.mate
            if cat_to.fetch_cat(mate).status.alive_in_player_clan
        ]
        poly = len(alive_inclan_from_mates) > 0 or len(alive_inclan_to_mates) > 0

        if poly and not RomanticEvents.current_mates_allow_new_mate(cat_from, cat_to):
            return False, None

        if (
            not hit
            and RomanticEvents.relationship_fulfill_condition(
                relationship_from, constants.CONFIG["mates"]["mate_condition"]
            )
            and RomanticEvents.relationship_fulfill_condition(
                relationship_to, constants.CONFIG["mates"]["mate_condition"]
            )
        ):
            become_mates = True
            mate_string = RomanticEvents.get_mate_string(
                "low_romantic", poly, cat_from, cat_to
            )
        if (
            not random_hit
            and RomanticEvents.relationship_fulfill_condition(
                relationship_from, constants.CONFIG["mates"]["like_to_romance"]
            )
            and RomanticEvents.relationship_fulfill_condition(
                relationship_to, constants.CONFIG["mates"]["like_to_romance"]
            )
        ):
            become_mates = True
            mate_string = RomanticEvents.get_mate_string(
                "like_to_romance", poly, cat_from, cat_to
            )

        if not become_mates:
            return False, None

        if poly:
            print("----- POLY-POLY-POLY", cat_from.name, cat_to.name)
            print(cat_from.mate)
            print(cat_to.mate)

        mate_string = RomanticEvents.prepare_relationship_string(
            mate_string, cat_from, cat_to
        )

        return become_mates, mate_string

    @staticmethod
    def relationship_fulfill_condition(relationship, condition):
        """
        Check if the relationship can fulfill the condition.
        Example condition:
            {
            "romance": 20,
            "like": 30,
            "respect": 0,
            "comfort": 20,
            "trust": -10
            }

        VALUES:
            - 0: no condition
            - positive number: value has to be higher than number
            - negative number: value has to be lower than number

        """
        if not relationship:
            return False

        return relationship.relationship_qualifies(condition)

    @staticmethod
    def current_mates_allow_new_mate(cat_from, cat_to) -> bool:
        """Check if all current mates are fulfill the given conditions."""
        current_mate_condition = constants.CONFIG["mates"]["poly"][
            "current_mate_condition"
        ]
        current_to_new_condition = constants.CONFIG["mates"]["poly"][
            "mates_to_each_other"
        ]

        # check relationship from current mates from cat_from
        all_mates_fulfill_current_mate_condition = True
        all_mates_fulfill_current_to_new = True
        alive_inclan_from_mates = [
            mate
            for mate in cat_from.mate
            if cat_from.fetch_cat(mate).status.alive_in_player_clan
        ]
        if len(alive_inclan_from_mates) > 0:
            for mate_id in alive_inclan_from_mates:
                mate_cat = cat_from.fetch_cat(mate_id)
                if mate_cat.dead:
                    continue
                if (
                    mate_id in cat_from.relationships
                    and cat_from.ID in mate_cat.relationships
                ):
                    if not RomanticEvents.relationship_fulfill_condition(
                        cat_from.relationships[mate_id], current_mate_condition
                    ) or not RomanticEvents.relationship_fulfill_condition(
                        mate_cat.relationships[cat_from.ID], current_mate_condition
                    ):
                        all_mates_fulfill_current_mate_condition = False

                if (
                    mate_id in cat_to.relationships
                    and cat_to.ID in mate_cat.relationships
                ):
                    if not RomanticEvents.relationship_fulfill_condition(
                        cat_to.relationships[mate_id], current_to_new_condition
                    ) or not RomanticEvents.relationship_fulfill_condition(
                        mate_cat.relationships[cat_to.ID], current_to_new_condition
                    ):
                        all_mates_fulfill_current_to_new = False
        if (
            not all_mates_fulfill_current_mate_condition
            or not all_mates_fulfill_current_to_new
        ):
            return False

        # check relationship from current mates from cat_to
        all_mates_fulfill_current_mate_condition = True
        all_mates_fulfill_current_to_new = True
        alive_inclan_to_mates = [
            mate
            for mate in cat_to.mate
            if cat_to.fetch_cat(mate).status.alive_in_player_clan
        ]
        if len(alive_inclan_to_mates) > 0:
            for mate_id in alive_inclan_to_mates:
                mate_cat = cat_to.fetch_cat(mate_id)
                if mate_cat.dead:
                    continue
                if (
                    mate_id in cat_to.relationships
                    and cat_to.ID in mate_cat.relationships
                ):
                    if not RomanticEvents.relationship_fulfill_condition(
                        cat_to.relationships[mate_id], current_mate_condition
                    ) or not RomanticEvents.relationship_fulfill_condition(
                        mate_cat.relationships[cat_to.ID], current_mate_condition
                    ):
                        all_mates_fulfill_current_mate_condition = False

                if (
                    mate_id in cat_from.relationships
                    and cat_from.ID in mate_cat.relationships
                ):
                    if not RomanticEvents.relationship_fulfill_condition(
                        cat_from.relationships[mate_id], current_to_new_condition
                    ) or not RomanticEvents.relationship_fulfill_condition(
                        mate_cat.relationships[cat_from.ID], current_to_new_condition
                    ):
                        all_mates_fulfill_current_to_new = False
        if (
            not all_mates_fulfill_current_mate_condition
            or not all_mates_fulfill_current_to_new
        ):
            return False

        return True

    @staticmethod
    def prepare_relationship_string(mate_string, cat_from, cat_to):
        """Prepares the relationship event string for display"""
        # replace mates with their names
        if "[m_c_mates]" in mate_string:
            mate_names = [
                str(cat_from.fetch_cat(mate_id).name)
                for mate_id in cat_from.mate
                if cat_from.fetch_cat(mate_id) is not None
                and cat_from.fetch_cat(mate_id).status.alive_in_player_clan
            ]
            mate_name_string = mate_names[0]
            if len(mate_names) == 2:
                mate_name_string = mate_names[0] + " and " + mate_names[1]
            if len(mate_names) > 2:
                mate_name_string = (
                    ", ".join(mate_names[:-1]) + ", and " + mate_names[-1]
                )
            mate_string = mate_string.replace("[m_c_mates]", mate_name_string)

        if "[r_c_mates]" in mate_string:
            mate_names = [
                str(cat_to.fetch_cat(mate_id).name)
                for mate_id in cat_to.mate
                if cat_to.fetch_cat(mate_id) is not None
                and cat_to.fetch_cat(mate_id).status.alive_in_player_clan
            ]
            mate_name_string = mate_names[0]
            if len(mate_names) == 2:
                mate_name_string = mate_names[0] + " and " + mate_names[1]
            if len(mate_names) > 2:
                mate_name_string = (
                    ", ".join(mate_names[:-1]) + ", and " + mate_names[-1]
                )
            mate_string = mate_string.replace("[r_c_mates]", mate_name_string)

        if "(m_c_mate/mates)" in mate_string:
            insert = "mate"
            if len(cat_from.mate) > 1:
                insert = "mates"
            mate_string = mate_string.replace("(m_c_mate/mates)", insert)

        if "(r_c_mate/mates)" in mate_string:
            insert = "mate"
            if len(cat_to.mate) > 1:
                insert = "mates"
            mate_string = mate_string.replace("(r_c_mate/mates)", insert)

        mate_string = event_text_adjust(
            Cat, mate_string, main_cat=cat_from, random_cat=cat_to
        )
        return mate_string

    @staticmethod
    def get_mate_string(key, poly, cat_from, cat_to):
        """Returns the mate string with the certain key, cats and poly."""
        RomanticEvents.rebuild_dicts()
        if not poly:
            return choice(RomanticEvents.MATE_DICTS[key])
        else:
            poly_key = ""
            alive_inclan_from_mates = [
                mate
                for mate in cat_from.mate
                if cat_from.fetch_cat(mate).status.alive_in_player_clan
            ]
            alive_inclan_to_mates = [
                mate
                for mate in cat_to.mate
                if cat_to.fetch_cat(mate).status.alive_in_player_clan
            ]
            if len(alive_inclan_from_mates) > 0 and len(alive_inclan_to_mates) > 0:
                poly_key = "both_mates"
            elif len(alive_inclan_from_mates) > 0 and len(alive_inclan_to_mates) <= 0:
                poly_key = "m_c_mates"
            elif len(alive_inclan_from_mates) <= 0 and len(alive_inclan_to_mates) > 0:
                poly_key = "r_c_mates"
            if not poly_key:
                # none of the other involved mates are alive
                return choice(RomanticEvents.MATE_DICTS[key])
            return choice(RomanticEvents.POLY_MATE_DICTS[key][poly_key])

    # ---------------------------------------------------------------------------- #
    #                             get/calculate chances                            #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def get_breakup_chance(cat_from: Cat, cat_to: Cat) -> int:
        """Looks into the current values and calculate the chance of breaking up. The lower, the more likely they will break up.
        Returns:
            integer (number)
        """
        # Gather relationships
        if cat_to.ID in cat_from.relationships:
            relationship_from = cat_from.relationships[cat_to.ID]
        else:
            relationship_from = cat_from.create_one_relationship(cat_to)

        if cat_from.ID in cat_to.relationships:
            relationship_to = cat_to.relationships[cat_from.ID]
        else:
            relationship_to = cat_to.create_one_relationship(cat_from)

        # No breakup chance if the cat is a good deal above the make-confession requirments.
        condition = constants.CONFIG["mates"]["confession"]["make_confession"].copy()
        for x in condition:
            if condition[x] > 0:
                condition[x] += 16
        if RomanticEvents.relationship_fulfill_condition(relationship_from, condition):
            return 0
        if RomanticEvents.relationship_fulfill_condition(relationship_to, condition):
            return 0

        chance_number = 30
        chance_number += int(relationship_from.romance / 20)
        chance_number += int(relationship_to.romance / 20)
        chance_number += int(relationship_from.like / 20)
        chance_number += int(relationship_to.like / 20)
        chance_number += int(relationship_from.respect / 20)
        chance_number += int(relationship_to.respect / 20)
        chance_number += int(relationship_from.trust / 20)
        chance_number += int(relationship_to.trust / 20)
        chance_number += int(relationship_from.comfort / 20)
        chance_number += int(relationship_to.comfort / 20)

        # change the change based on the personality
        get_along = get_personality_compatibility(cat_from, cat_to)
        if get_along is not None and get_along:
            chance_number += 5
        if get_along is not None and not get_along:
            chance_number -= 10

        # Then, at least a 1/5 chance
        chance_number = max(chance_number, 5)

        return chance_number
