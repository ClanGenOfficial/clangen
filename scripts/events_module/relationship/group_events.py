import os
from copy import deepcopy
from random import choice, shuffle

import ujson

from scripts.cat.cats import Cat
from scripts.cat.history import History
from scripts.cat_relations.interaction import (
    create_group_interaction,
    GroupInteraction,
    rel_fulfill_rel_constraints,
)
from scripts.event_class import Single_Event
from scripts.game_structure.game_essentials import game
from scripts.utility import change_relationship_values, process_text


class GroupEvents:

    # ---------------------------------------------------------------------------- #
    #                   build master dictionary for interactions                   #
    # ---------------------------------------------------------------------------- #

    base_path = os.path.join(
        "resources", "dicts", "relationship_events", "group_interactions"
    )

    GROUP_INTERACTION_MASTER_DICT = {}
    for cat_amount in os.listdir(base_path):
        if cat_amount == "group_types.json":
            continue
        file_path = os.path.join(base_path, cat_amount, "neutral.json")
        GROUP_INTERACTION_MASTER_DICT[cat_amount] = {}
        with open(file_path, "r") as read_file:
            welcome_list = ujson.load(read_file)
            GROUP_INTERACTION_MASTER_DICT[cat_amount]["neutral"] = (
                create_group_interaction(welcome_list)
            )

        file_path = os.path.join(base_path, cat_amount, "positive.json")
        with open(file_path, "r") as read_file:
            welcome_list = ujson.load(read_file)
            GROUP_INTERACTION_MASTER_DICT[cat_amount]["positive"] = (
                create_group_interaction(welcome_list)
            )

        file_path = os.path.join(base_path, cat_amount, "negative.json")
        with open(file_path, "r") as read_file:
            welcome_list = ujson.load(read_file)
            GROUP_INTERACTION_MASTER_DICT[cat_amount]["negative"] = (
                create_group_interaction(welcome_list)
            )

    del base_path

    abbreviations_cat_id = {}
    cat_abbreviations_counter = {}
    chosen_interaction = None

    @staticmethod
    def start_interaction(cat: Cat, interact_cats: list) -> list:
        """Start to define the possible group interactions.

        Parameters
        ----------
        cat : Cat
            the main cat
        interact_cats : list
            a list of cats, which are open to interact with the main cat

        Returns
        -------
        list
            returns the list of the cat id's, which interacted with each other
        """
        abbreviations_cat_id = {}  # keeps track of which abbreviation is which cat
        abbreviations_cat_id["m_c"] = cat.ID  # set the main cat
        chosen_interaction = None

        cat_amount = choice(list(GroupEvents.GROUP_INTERACTION_MASTER_DICT.keys()))
        inter_type = choice(["negative", "positive", "neutral"])

        # if the chosen amount is bigger than the given interaction cats,
        # there will be no possible solution and it will be returned
        if len(interact_cats) < int(cat_amount):
            return []

        # setup the abbreviations_cat_id dictionary
        for integer in range(int(cat_amount) - 1):
            new_key = "r_c" + str(integer + 1)
            abbreviations_cat_id[new_key] = None

        # get all possibilities
        possibilities = GroupEvents.GROUP_INTERACTION_MASTER_DICT[cat_amount][
            inter_type
        ]

        # get some filters premisses
        biome = str(game.clan.biome).casefold()
        season = str(game.clan.current_season).casefold()

        # start filter for main cat / basic checks
        # - this might reduce the amount of checks which will be needed when checking for other cats
        possibilities = GroupEvents.get_main_cat_interactions(
            possibilities, biome, season, abbreviations_cat_id
        )

        # get possible interactions, considering the possible interacting cats
        possibilities = GroupEvents.get_filtered_interactions(
            possibilities, int(cat_amount), interact_cats, abbreviations_cat_id
        )

        # if there is no possibility return
        if len(possibilities) < 1:
            return []
        # choose one interaction and
        chosen_interaction = choice(possibilities)

        # TRIGGER ALL NEEDED FUNCTIONS TO REFLECT THE INTERACTION
        GroupEvents.injuring_cats(chosen_interaction, abbreviations_cat_id)
        amount = game.config["relationship"]["in_decrease_value"][
            chosen_interaction.intensity
        ]

        if len(chosen_interaction.general_reaction) > 0:
            # if there is a general reaction in the interaction, then use this
            GroupEvents.influence_general_relationship(
                amount, abbreviations_cat_id, chosen_interaction
            )
        else:
            GroupEvents.influence_specific_relationships(
                amount, abbreviations_cat_id, chosen_interaction
            )

        # choose the interaction text and display
        interaction_str = choice(chosen_interaction.interactions)
        interaction_str = GroupEvents.prepare_text(
            interaction_str, abbreviations_cat_id
        )
        # TODO: add the interaction to the relationship log?

        interaction_str = interaction_str + f" ({inter_type} effect)"
        ids = list(abbreviations_cat_id.values())
        relevant_event_tabs = ["relation", "interaction"]
        if chosen_interaction.get_injuries:
            relevant_event_tabs.append("health")

        game.cur_events_list.append(
            Single_Event(interaction_str, relevant_event_tabs, ids)
        )
        return ids

    # ---------------------------------------------------------------------------- #
    #                  functions to filter and decide interaction                  #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def get_main_cat_interactions(
        interactions: list, biome: str, season: str, abbreviations_cat_id: dict
    ) -> list:
        """Filter interactions for MAIN cat.

        Parameters
        ----------
        interactions : list
            the interactions which need to be filtered
        biome : str
            biome of the clan
        season : str
            current season of the clan
        abbreviations_cat_id : dict
            dictionary which contains all abbreviation with the belonging cat id

        Returns
        -------
        filtered : list
            a list of interactions, which fulfill the criteria
        """
        filtered_interactions = []
        allowed_season = [season, "Any", "any"]
        allowed_biome = [biome, "Any", "any"]
        main_cat = Cat.all_cats[abbreviations_cat_id["m_c"]]
        for interact in interactions:
            in_tags = [i for i in interact.biome if i in allowed_biome]
            if len(in_tags) < 1:
                continue

            in_tags = [i for i in interact.season if i in allowed_season]
            if len(in_tags) < 1:
                continue

            if (
                len(interact.status_constraint) >= 1
                and "m_c" in interact.status_constraint
            ):
                if main_cat.status not in interact.status_constraint["m_c"]:
                    continue

            if (
                len(interact.trait_constraint) >= 1
                and "m_c" in interact.trait_constraint
            ):
                if main_cat.personality.trait not in interact.trait_constraint["m_c"]:
                    continue

            if (
                len(interact.skill_constraint) >= 1
                and "m_c" in interact.skill_constraint
            ):
                if not main_cat.skills.check_skill_requirement_list(
                    interact.skill_constraint["m_c"]
                ):
                    continue

            if (
                len(interact.backstory_constraint) >= 1
                and "m_c" in interact.backstory_constraint
            ):
                if main_cat.backstory not in interact.backstory_constraint["m_c"]:
                    continue

            filtered_interactions.append(interact)
        return filtered_interactions

    @staticmethod
    def get_filtered_interactions(
        interactions: list, amount: int, interact_cats: list, abbreviations_cat_id: dict
    ):
        """First assign which cat is which abbreviation, then filtered interaction list based on all constraints, which include the other cats.

        Parameters
        ----------
        interactions : list
            the interactions which need to be filtered
        amount : int
            the amount of cats which are be needed for these interactions
        interact_cats : list
            a list of cats, which are open to interact with the main cat

        Returns
        -------
        filtered : list
            a list of interactions, which fulfill the criteria

        """
        # first handle the abbreviations possibilities for the cats
        abbr_per_interaction, cat_abbreviations_counter = (
            GroupEvents.get_abbreviations_possibilities(
                interactions, int(amount), interact_cats
            )
        )
        abbr_per_interaction = GroupEvents.remove_abbreviations_missing_cats(
            abbr_per_interaction
        )
        abbreviations_cat_id = GroupEvents.set_abbreviations_cats(
            interact_cats, abbreviations_cat_id, cat_abbreviations_counter
        )

        # check if any abbreviations_cat_ids is None, if so return
        not_none = [abbr != None for abbr in abbreviations_cat_id.values()]
        if not all(not_none):
            return []

        # last filter based on relationships between the cats
        filtered = []
        for interact in interactions:
            # if this interaction is not in the  abbreviations dictionary,
            # there is no solution for the cat-abbreviations problem and thus, this
            # interaction is not possible
            if interact.id not in abbr_per_interaction.keys():
                continue

            # check how the cats are and if they are fulfill the constraints like: status, trait, skill, ...
            cat_allow_interaction = GroupEvents.cat_allow_interaction(
                interact, abbreviations_cat_id
            )
            if not cat_allow_interaction:
                continue

            # now check for relationship constraints
            relationship_allow_interaction = (
                GroupEvents.relationship_allow_interaction(
                    interact, abbreviations_cat_id
                )
            )
            if not relationship_allow_interaction:
                continue

            filtered.append(interact)

        return filtered

    @staticmethod
    def get_abbreviations_possibilities(
        interactions: list, amount: int, interact_cats: list
    ) -> tuple:
        """Iterate over all pre-filtered interactions and
        check which cat fulfills skill/trait/status condition of which abbreviation.

        Parameters
        ----------
        interactions : list
            the interactions which need to be filtered
        amount : int
            the amount of cats for the current interaction
        interact_cats : list
            a list of cats, which are open to interact with the main cat
        """
        cat_abbreviations_counter = {}
        possibilities = {}
        # prepare how the base dictionary should look,
        # this depends on the chosen cat amount -> which abbreviation are needed
        base_dictionary = {}
        for integer in range(amount):
            new_key = "r_c" + str(integer + 1)
            base_dictionary[new_key] = []

        # iterate over all interactions and checks for each abbreviation, which cat is possible
        for interact in interactions:
            dictionary = deepcopy(base_dictionary)

            for abbreviation in dictionary:
                dictionary[abbreviation] = []
                status_ids = []
                skill_ids = []
                trait_ids = []

                # if the abbreviation has a status constraint, check in details
                if abbreviation in interact.status_constraint:
                    # if the cat status is in the status constraint, add the id to the list
                    status_ids = [
                        cat.ID
                        for cat in interact_cats
                        if cat.status in interact.status_constraint[abbreviation]
                    ]
                else:
                    # if there is no constraint, add all ids to the list
                    status_ids = [cat.ID for cat in interact_cats]

                # same as status
                if abbreviation in interact.skill_constraint:
                    skill_ids = [
                        cat.ID
                        for cat in interact_cats
                        if cat.skill in interact.skill_constraint[abbreviation]
                    ]
                else:
                    skill_ids = [cat.ID for cat in interact_cats]

                if abbreviation in interact.trait_constraint:
                    trait_ids = [
                        cat.ID
                        for cat in interact_cats
                        if cat.personality.trait
                        in interact.trait_constraint[abbreviation]
                    ]
                else:
                    trait_ids = [cat.ID for cat in interact_cats]

                # only add the id if it is in all other lists
                for cat_id in [cat.ID for cat in interact_cats]:
                    if (
                        cat_id in status_ids
                        and cat_id in skill_ids
                        and cat_id in trait_ids
                    ):
                        dictionary[abbreviation].append(cat_id)

                        if (
                            cat_id in cat_abbreviations_counter
                            and abbreviation in cat_abbreviations_counter[cat_id]
                        ):
                            cat_abbreviations_counter[cat_id][abbreviation] += 1
                        elif (
                            cat_id in cat_abbreviations_counter
                            and abbreviation not in cat_abbreviations_counter[cat_id]
                        ):
                            cat_abbreviations_counter[cat_id][abbreviation] = 1
                        else:
                            cat_abbreviations_counter[cat_id] = {}
                            cat_abbreviations_counter[cat_id][abbreviation] = 1

            possibilities[interact.id] = dictionary
        return possibilities, cat_abbreviations_counter

    @staticmethod
    def remove_abbreviations_missing_cats(abbreviations_per_interaction: dict):
        """
        Check which combinations of abbreviations are allowed and possible and which are not, only return a dictionary,
        with possible combinations together with the id for the interaction.
        """
        filtered_abbreviations = {}
        for interaction_id, dictionary in abbreviations_per_interaction.items():
            # check if there is any abbreviation, which is empty
            abbr_length = [len(val) for abr, val in dictionary.items()]
            # if one length is 0 the all function returns false
            if not all(abbr_length):
                continue

            filtered_abbreviations[interaction_id] = dictionary
        return filtered_abbreviations

    @staticmethod
    def set_abbreviations_cats(
        interact_cats: list, abbreviations_cat_id: dict, cat_abbreviations_counter: dict
    ):
        """Choose which cat is which abbreviations."""
        free_to_choose = [cat.ID for cat in interact_cats]
        # shuffle the list to prevent choosing the same cats every time
        shuffle(free_to_choose)

        for abbr_key in list(abbreviations_cat_id.keys()):
            if abbr_key == "m_c":
                continue
            highest_value = 0
            highest_id = None

            # gets the cat id which fits the abbreviations most of the time
            for cat_id in free_to_choose:
                # first set some values if there are none
                if cat_id not in cat_abbreviations_counter:
                    cat_abbreviations_counter[cat_id] = {}
                if abbr_key not in cat_abbreviations_counter[cat_id]:
                    cat_abbreviations_counter[cat_id][abbr_key] = 0

                # find the highest value
                curr_value = cat_abbreviations_counter[cat_id][abbr_key]
                if highest_value < curr_value:
                    highest_value = curr_value
                    highest_id = cat_id

            abbreviations_cat_id[abbr_key] = highest_id
            if highest_id in free_to_choose:
                free_to_choose.remove(highest_id)
        return abbreviations_cat_id

    # ---------------------------------------------------------------------------- #
    #                  helper functions for filtering interactions                 #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def relationship_allow_interaction(
        interaction: GroupInteraction, abbreviations_cat_id: dict
    ):
        """Check if the interaction is allowed with the current chosen cats."""
        fulfilled_list = []

        for name, rel_constraint in interaction.relationship_constraint.items():
            abbre_from = name.split("_to_")[0]
            abbre_to = name.split("_to_")[1]

            cat_from_id = abbreviations_cat_id[abbre_from]
            cat_to_id = abbreviations_cat_id[abbre_to]
            cat_from = Cat.all_cats[cat_from_id]
            cat_to = Cat.all_cats[cat_to_id]

            if cat_to_id not in cat_from.relationships:
                cat_from.create_one_relationship(cat_to)
                if cat_from.ID not in cat_to.relationships:
                    cat_to.create_one_relationship(cat_from)
                continue

            relationship = cat_from.relationships[cat_to_id]

            fulfilled = rel_fulfill_rel_constraints(
                relationship, rel_constraint, interaction.id
            )
            fulfilled_list.append(fulfilled)

        return all(fulfilled_list)

    @staticmethod
    def cat_allow_interaction(
        interaction: GroupInteraction, abbreviations_cat_id: dict
    ):
        """Check if the assigned cats fulfill the constraints of the interaction."""

        all_fulfilled = True
        for abbr, constraint in interaction.status_constraint.items():
            # main cat is already filtered
            if abbr == "m_c":
                continue
            # check if the current abbreviations cat fulfill the constraint
            relevant_cat = Cat.all_cats[abbreviations_cat_id[abbr]]
            if relevant_cat.status not in constraint:
                all_fulfilled = False
        if not all_fulfilled:
            return False

        # check if all cats fulfill the skill constraints
        all_fulfilled = True
        for abbr, constraint in interaction.skill_constraint.items():
            # main cat is already filtered
            if abbr == "m_c":
                continue
            # check if the current abbreviations cat fulfill the constraint
            relevant_cat = Cat.all_cats[abbreviations_cat_id[abbr]]
            if not relevant_cat.skills.check_skill_requirement_list(constraint):
                all_fulfilled = False
        if not all_fulfilled:
            return False

        # check if all cats fulfill the trait constraints
        all_fulfilled = True
        for abbr, constraint in interaction.trait_constraint.items():
            # main cat is already filtered
            if abbr == "m_c":
                continue
            # check if the current abbreviations cat fulfill the constraint
            relevant_cat = Cat.all_cats[abbreviations_cat_id[abbr]]
            if relevant_cat.personality.trait not in constraint:
                all_fulfilled = False
        if not all_fulfilled:
            return False

        # check if all cats fulfill the backstory constraints
        all_fulfilled = True
        for abbr, constraint in interaction.backstory_constraint.items():
            # main cat is already filtered
            if abbr == "m_c":
                continue
            # check if the current abbreviations cat fulfill the constraint
            relevant_cat = Cat.all_cats[abbreviations_cat_id[abbr]]
            if relevant_cat.backstory not in constraint:
                all_fulfilled = False
        if not all_fulfilled:
            return False

        # check if all cats fulfill the injuries constraints
        all_fulfilled = True
        for abbr, constraint in interaction.has_injuries.items():
            # main cat is already filtered
            if abbr == "m_c":
                continue
            # check if the current abbreviations cat fulfill the constraint
            relevant_cat = Cat.all_cats[abbreviations_cat_id[abbr]]
            injuries_in_needed = list(
                filter(lambda inj: inj in constraint, relevant_cat.injuries.keys())
            )
            if len(injuries_in_needed) <= 0:
                all_fulfilled = False
        if not all_fulfilled:
            return False
        return True

    # ---------------------------------------------------------------------------- #
    #                      functions after interaction decision                    #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def influence_general_relationship(
        amount, abbreviations_cat_id, chosen_interaction
    ):
        """
        Influence the relationship between all cats with the same amount, defined by the chosen group relationship.
        """
        dictionary = chosen_interaction.general_reaction

        # set the amount
        romantic = 0
        platonic = 0
        dislike = 0
        admiration = 0
        comfortable = 0
        jealousy = 0
        trust = 0
        if "romantic" in dictionary and dictionary["romantic"] != "neutral":
            romantic = amount if dictionary["romantic"] == "increase" else amount * -1
        if "platonic" in dictionary and dictionary["platonic"] != "neutral":
            platonic = amount if dictionary["platonic"] == "increase" else amount * -1
        if "dislike" in dictionary and dictionary["dislike"] != "neutral":
            platonic = amount if dictionary["dislike"] == "increase" else amount * -1
        if "admiration" in dictionary and dictionary["admiration"] != "neutral":
            platonic = amount if dictionary["admiration"] == "increase" else amount * -1
        if "comfortable" in dictionary and dictionary["comfortable"] != "neutral":
            platonic = (
                amount if dictionary["comfortable"] == "increase" else amount * -1
            )
        if "jealousy" in dictionary and dictionary["jealousy"] != "neutral":
            platonic = amount if dictionary["jealousy"] == "increase" else amount * -1
        if "trust" in dictionary and dictionary["trust"] != "neutral":
            platonic = amount if dictionary["trust"] == "increase" else amount * -1
        abbreviations_cat = []

        for cat in abbreviations_cat_id:
            abbreviations_cat.append(Cat.fetch_cat(cat))
        for inter_cat in abbreviations_cat:
            change_relationship_values(
                cats_from=[inter_cat],
                cats_to=list(abbreviations_cat),
                romantic_love=romantic,
                platonic_like=platonic,
                dislike=dislike,
                admiration=admiration,
                comfortable=comfortable,
                jealousy=jealousy,
                trust=trust,
            )

    @staticmethod
    def influence_specific_relationships(
        amount, abbreviations_cat_id, chosen_interaction
    ):
        """
        Influence the relationships based on the list of the reaction of the chosen group interaction.
        """
        if len(chosen_interaction.specific_reaction) <= 0:
            return

        for name, dictionary in chosen_interaction.specific_reaction.items():
            abbre_from = name.split("_to_")[0]
            abbre_to = name.split("_to_")[1]

            cat_from_id = abbreviations_cat_id[abbre_from]
            cat_to_id = abbreviations_cat_id[abbre_to]
            cat_from = Cat.all_cats[cat_from_id]
            cat_to = Cat.all_cats[cat_to_id]

            # set all values to influence the relationship
            romantic = 0
            platonic = 0
            dislike = 0
            admiration = 0
            comfortable = 0
            jealousy = 0
            trust = 0
            if "romantic" in dictionary and dictionary["romantic"] != "neutral":
                romantic = (
                    amount if dictionary["romantic"] == "increase" else amount * -1
                )
            if "platonic" in dictionary and dictionary["platonic"] != "neutral":
                platonic = (
                    amount if dictionary["platonic"] == "increase" else amount * -1
                )
            if "dislike" in dictionary and dictionary["dislike"] != "neutral":
                dislike = amount if dictionary["dislike"] == "increase" else amount * -1
            if "admiration" in dictionary and dictionary["admiration"] != "neutral":
                admiration = (
                    amount if dictionary["admiration"] == "increase" else amount * -1
                )
            if "comfortable" in dictionary and dictionary["comfortable"] != "neutral":
                comfortable = (
                    amount if dictionary["comfortable"] == "increase" else amount * -1
                )
            if "jealousy" in dictionary and dictionary["jealousy"] != "neutral":
                jealousy = (
                    amount if dictionary["jealousy"] == "increase" else amount * -1
                )
            if "trust" in dictionary and dictionary["trust"] != "neutral":
                trust = amount if dictionary["trust"] == "increase" else amount * -1

            change_relationship_values(
                cats_from=[cat_from],
                cats_to=[cat_to],
                romantic_love=romantic,
                platonic_like=platonic,
                dislike=dislike,
                admiration=admiration,
                comfortable=comfortable,
                jealousy=jealousy,
                trust=trust,
            )

    @staticmethod
    def injuring_cats(chosen_interaction, abbreviations_cat_id):
        """
        Injuring the cats based on the list of the injuries of the chosen group interaction.
        """
        if not chosen_interaction.get_injuries.items:
            return

        for abbreviations, injury_dict in chosen_interaction.get_injuries.items():
            if "injury_names" not in injury_dict:
                print(
                    f"ERROR: there are no injury names in the chosen interaction {chosen_interaction.id}."
                )
                continue
            injured_cat = Cat.all_cats[abbreviations_cat_id[abbreviations]]

            injuries = []
            for inj in injury_dict["injury_names"]:
                injured_cat.get_injured(inj, True)
                injuries.append(inj)

            possible_scar = (
                GroupEvents.prepare_text(
                    injury_dict["scar_text"], abbreviations_cat_id
                )
                if "scar_text" in injury_dict
                else None
            )
            possible_death = (
                GroupEvents.prepare_text(
                    injury_dict["death_text"], abbreviations_cat_id
                )
                if "death_text" in injury_dict
                else None
            )
            if injured_cat.status == "leader":
                possible_death = (
                    GroupEvents.prepare_text(
                        injury_dict["death_leader_text"], abbreviations_cat_id
                    )
                    if "death_leader_text" in injury_dict
                    else None
                )

            if possible_death or possible_scar:
                for condition in injuries:
                    History.add_possible_history(
                        injured_cat,
                        condition,
                        death_text=possible_death,
                        scar_text=possible_scar,
                    )

    @staticmethod
    def prepare_text(text: str, abbreviations_cat_id: dict) -> str:
        """Prep the text based of the amount of cats and the assigned abbreviations."""

        replace_dict = {}
        for abbr, cat_id in abbreviations_cat_id.items():
            replace_dict[abbr] = (
                str(Cat.all_cats[cat_id].name),
                choice(Cat.all_cats[cat_id].pronouns),
            )

        return process_text(text, replace_dict)
