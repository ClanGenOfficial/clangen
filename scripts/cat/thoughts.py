import traceback
from random import choice

import i18n

from scripts.game_structure.localization import load_lang_resource


class Thoughts:
    @staticmethod
    def thought_fulfill_rel_constraints(main_cat, random_cat, constraint) -> bool:
        """Check if the relationship fulfills the interaction relationship constraints."""
        # if the constraints are not existing, they are considered to be fulfilled
        if not random_cat:
            return False

        # No current relationship-value bases tags, so this is commented out.
        relationship = None
        if random_cat.ID in main_cat.relationships:
            relationship = main_cat.relationships[random_cat.ID]

        if "siblings" in constraint and not main_cat.is_sibling(random_cat):
            return False

        if "littermates" in constraint and not main_cat.is_littermate(random_cat):
            return False

        if "mates" in constraint and random_cat.ID not in main_cat.mate:
            return False

        if "not_mates" in constraint and random_cat.ID in main_cat.mate:
            return False

        if "parent/child" in constraint and not main_cat.is_parent(random_cat):
            return False

        if "child/parent" in constraint and not random_cat.is_parent(main_cat):
            return False

        if "mentor/app" in constraint and random_cat not in main_cat.apprentice:
            return False

        if "app/mentor" in constraint and random_cat.ID != main_cat.mentor:
            return False

        if (
            "strangers" in constraint
            and relationship
            and (relationship.platonic_like < 1 or relationship.romantic_love < 1)
        ):
            return False

        return True

    @staticmethod
    def cats_fulfill_thought_constraints(
        main_cat, random_cat, thought, game_mode, biome, season, camp
    ) -> bool:
        """Check if the two cats fulfills the thought constraints."""

        # This is for checking biome
        if "biome" in thought:
            if biome not in thought["biome"]:
                return False

        # This is checking for season
        if "season" in thought:
            if season not in thought["season"]:
                return False

        # This is for checking camp
        if "camp" in thought:
            if camp not in thought["camp"]:
                return False

        # This is for checking the 'not_working' status
        if "not_working" in thought:
            if thought["not_working"] != main_cat.not_working():
                return False

        # This is for checking if another cat is needed and there is another cat
        r_c_in = [
            thought_str for thought_str in thought["thoughts"] if "r_c" in thought_str
        ]
        if len(r_c_in) > 0 and not random_cat:
            return False

        # This is for filtering certain relationship types between the main cat and random cat.
        if "relationship_constraint" in thought and random_cat:
            if not Thoughts.thought_fulfill_rel_constraints(
                main_cat, random_cat, thought["relationship_constraint"]
            ):
                return False

        # Constraints for the status of the main cat
        if "main_status_constraint" in thought:
            if (
                main_cat.status not in thought["main_status_constraint"]
                and "any" not in thought["main_status_constraint"]
            ):
                return False

        # Constraints for the status of the random cat
        if "random_status_constraint" in thought and random_cat:
            if (
                random_cat.status not in thought["random_status_constraint"]
                and "any" not in thought["random_status_constraint"]
            ):
                return False
        elif "random_status_constraint" in thought and not random_cat:
            pass

        # main cat age constraint
        if "main_age_constraint" in thought:
            if main_cat.age not in thought["main_age_constraint"]:
                return False

        if "random_age_constraint" in thought and random_cat:
            if random_cat.age not in thought["random_age_constraint"]:
                return False

        if "main_trait_constraint" in thought:
            if main_cat.personality.trait not in thought["main_trait_constraint"]:
                return False

        if "random_trait_constraint" in thought and random_cat:
            if random_cat.personality.trait not in thought["random_trait_constraint"]:
                return False

        if "main_skill_constraint" in thought:
            _flag = False
            for _skill in thought["main_skill_constraint"]:
                spli = _skill.split(",")

                if len(spli) != 2:
                    print("Throught constraint not properly formated", _skill)
                    continue

                if main_cat.skills.meets_skill_requirement(spli[0], int(spli[1])):
                    _flag = True
                    break

            if not _flag:
                return False

        if "random_skill_constraint" in thought and random_cat:
            _flag = False
            for _skill in thought["random_skill_constraint"]:
                spli = _skill.split(",")

                if len(spli) != 2:
                    print("Throught constraint not properly formated", _skill)
                    continue

                if random_cat.skills.meets_skill_requirement(spli[0], spli[1]):
                    _flag = True
                    break

            if not _flag:
                return False

        if "main_backstory_constraint" in thought:
            if main_cat.backstory not in thought["main_backstory_constraint"]:
                return False

        if "random_backstory_constraint" in thought:
            if (
                random_cat
                and random_cat.backstory not in thought["random_backstory_constraint"]
            ):
                return False

        # Filter for the living status of the random cat. The living status of the main cat
        # is taken into account in the thought loading process.
        if random_cat and "random_living_status" in thought:
            if random_cat:
                if random_cat.dead:
                    if random_cat.df:
                        living_status = "darkforest"
                    else:
                        living_status = "starclan"
                else:
                    living_status = "living"
            else:
                living_status = "unknownresidence"
            if living_status and living_status not in thought["random_living_status"]:
                return False

        # this covers if living status isn't stated
        else:
            living_status = None
            if random_cat and not random_cat.dead and not random_cat.outside:
                living_status = "living"
            if living_status and living_status != "living":
                return False

        if (
            random_cat
            and random_cat.outside
            and random_cat.status
            not in ["kittypet", "loner", "rogue", "former Clancat", "exiled"]
        ):
            outside_status = "lost"
        elif random_cat and random_cat.outside:
            outside_status = "outside"
        else:
            outside_status = "clancat"
        if random_cat and "random_outside_status" in thought:
            if outside_status not in thought["random_outside_status"]:
                return False
        else:
            if (
                main_cat.outside
            ):  # makes sure that outsiders can get thoughts all the time
                pass
            else:
                if outside_status and outside_status != "clancat" and len(r_c_in) > 0:
                    return False

            if "has_injuries" in thought:
                if "m_c" in thought["has_injuries"]:
                    if main_cat.injuries or main_cat.illnesses:
                        injuries_and_illnesses = (
                            list(main_cat.injuries.keys()) + list(main_cat.injuries.keys())
                        )
                        if (
                            not [
                                i
                                for i in injuries_and_illnesses
                                if i in thought["has_injuries"]["m_c"]
                            ]
                            and "any" not in thought["has_injuries"]["m_c"]
                        ):
                            return False
                    else:
                        return False

                if "r_c" in thought["has_injuries"] and random_cat:
                    if random_cat.injuries or random_cat.illnesses:
                        injuries_and_illnesses = (
                            list(random_cat.injuries.keys()) + list(random_cat.injuries.keys())
                        )
                        if (
                            not [
                                i
                                for i in injuries_and_illnesses
                                if i in thought["has_injuries"]["r_c"]
                            ]
                            and "any" not in thought["has_injuries"]["r_c"]
                        ):
                            return False
                    else:
                        return False

            if "perm_conditions" in thought:
                if "m_c" in thought["perm_conditions"]:
                    if main_cat.permanent_condition:
                        if (
                            not [
                                i
                                for i in main_cat.permanent_condition
                                if i in thought["perm_conditions"]["m_c"]
                            ]
                            and "any" not in thought["perm_conditions"]["m_c"]
                        ):
                            return False
                    else:
                        return False

                if "r_c" in thought["perm_conditions"] and random_cat:
                    if random_cat.permanent_condition:
                        if (
                            not [
                                i
                                for i in random_cat.permanent_condition
                                if i in thought["perm_conditions"]["r_c"]
                            ]
                            and "any" not in thought["perm_conditions"]["r_c"]
                        ):
                            return False
                    else:
                        return False

        if "perm_conditions" in thought:
            if "m_c" in thought["perm_conditions"]:
                if main_cat.permanent_condition:
                    if (
                        not [
                            i
                            for i in main_cat.permanent_condition
                            if i in thought["perm_conditions"]["m_c"]
                        ]
                        and "any" not in thought["perm_conditions"]["m_c"]
                    ):
                        return False

            if "r_c" in thought["perm_conditions"] and random_cat:
                if random_cat.permanent_condition:
                    if (
                        not [
                            i
                            for i in random_cat.permanent_condition
                            if i in thought["perm_conditions"]["r_c"]
                        ]
                        and "any" not in thought["perm_conditions"]["r_c"]
                    ):
                        return False

        return True

    # ---------------------------------------------------------------------------- #
    #                            BUILD MASTER DICTIONARY                           #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def create_thoughts(
        inter_list, main_cat, other_cat, game_mode, biome, season, camp
    ) -> list:
        created_list = []
        for inter in inter_list:
            if Thoughts.cats_fulfill_thought_constraints(
                main_cat, other_cat, inter, game_mode, biome, season, camp
            ):
                created_list.append(inter)
        return created_list

    @staticmethod
    def load_thoughts(main_cat, other_cat, game_mode, biome, season, camp):
        status = main_cat.status
        status = status.replace(" ", "_")
        # match status:
        #     case "medicine cat apprentice":
        #         status = "medicine_cat_apprentice"
        #     case "mediator apprentice":
        #         status = "mediator_apprentice"
        #     case "medicine cat":
        #         status = "medicine_cat"
        #     case 'former Clancat':
        #         status = 'former_Clancat'

        if not main_cat.dead:
            life_dir = "alive"
        else:
            life_dir = "dead"

        if main_cat.dead:
            if main_cat.outside:
                spec_dir = "/unknownresidence"
            elif main_cat.df:
                spec_dir = "/darkforest"
            else:
                spec_dir = "/starclan"
        elif main_cat.outside:
            spec_dir = "/alive_outside"
        else:
            spec_dir = ""

        # newborns only pull from their status thoughts. this is done for convenience
        try:
            if main_cat.age == "newborn":
                loaded_thoughts = load_lang_resource(
                    f"thoughts/{life_dir}{spec_dir}/newborn.json"
                )
            else:
                thoughts = load_lang_resource(
                    f"thoughts/{life_dir}{spec_dir}/{status}.json"
                )
                genthoughts = load_lang_resource(
                    f"thoughts/{life_dir}{spec_dir}/general.json"
                )
                loaded_thoughts = thoughts + genthoughts

            final_thoughts = Thoughts.create_thoughts(
                loaded_thoughts, main_cat, other_cat, game_mode, biome, season, camp
            )
            return final_thoughts
        except IOError:
            print("ERROR: loading thoughts")

    @staticmethod
    def get_chosen_thought(main_cat, other_cat, game_mode, biome, season, camp):
        # get possible thoughts
        try:
            # checks if the cat is Rick Astley to give the rickroll thought, otherwise proceed as usual
            if (main_cat.name.prefix + main_cat.name.suffix).replace(
                " ", ""
            ).lower() == "rickastley":
                return i18n.t("defaults.rickroll")
            else:
                chosen_thought_group = choice(
                    Thoughts.load_thoughts(
                        main_cat, other_cat, game_mode, biome, season, camp
                    )
                )
                chosen_thought = choice(chosen_thought_group["thoughts"])
        except Exception:
            traceback.print_exc()
            chosen_thought = i18n.t("defaults.thought")

        return chosen_thought

    def create_death_thoughts(self, inter_list) -> list:
        # helper function for death thoughts
        created_list = []
        for inter in inter_list:
            created_list.append(inter)
        return created_list

    def leader_death_thought(self, lives_left, darkforest):
        """
        Load the special leader death thoughts, since they function differently than regular ones
        :param lives_left: How many lives the leader has left - used to determine if they actually die or not
        :param darkforest: Whether or not dead cats go to StarClan (false) or the DF (true)
        """
        base_path = f"resources/lang/{i18n.config.get('locale')}/thoughts/ondeath"
        fallback_path = f"resources/lang/{i18n.config.get('fallback')}/thoughts/ondeath"
        if darkforest:
            spec_dir = "/darkforest"
        else:
            spec_dir = "/starclan"
        THOUGHTS: []
        try:
            if lives_left > 0:
                loaded_thoughts = load_lang_resource(
                    f"thoughts/ondeath{spec_dir}/leader_life.json"
                )
            else:
                loaded_thoughts = load_lang_resource(
                    f"thoughts/ondeath{spec_dir}/leader_death.json"
                )
            thought_group = choice(
                Thoughts.create_death_thoughts(self, loaded_thoughts)
            )
            chosen_thought = choice(thought_group["thoughts"])
            return chosen_thought
        except Exception:
            traceback.print_exc()
            chosen_thought = i18n.t("defaults.thought")
            return chosen_thought

    def new_death_thought(self, darkforest, isoutside):
        base_path = f"resources/lang/{i18n.config.get('locale')}/thoughts/ondeath"
        fallback_path = f"resources/lang/{i18n.config.get('fallback')}/thoughts/ondeath"

        if isoutside:
            spec_dir = "/unknownresidence"
        elif darkforest is False:
            spec_dir = "/starclan"
        else:
            spec_dir = "/darkforest"
        THOUGHTS: []
        try:
            loaded_thoughts = load_lang_resource(
                f"thoughts/ondeath{spec_dir}/general.json"
            )
            thought_group = choice(
                Thoughts.create_death_thoughts(self, loaded_thoughts)
            )
            chosen_thought = choice(thought_group["thoughts"])
            return chosen_thought
        except Exception:
            traceback.print_exc()
            return i18n.t("defaults.thought")
