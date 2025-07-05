import i18n

from scripts.cat_relations.enums import RelValue
from scripts.events_module.event_filters import event_for_cat
from scripts.game_structure.localization import load_lang_resource


class SingleInteraction:
    def __init__(
        self,
        interact_id,
        biome=None,
        season=None,
        intensity="medium",
        interactions=None,
        get_injuries=None,
        has_injuries=None,
        relationship_constraint=None,
        backstory_constraint=None,
        main_status_constraint=None,
        random_status_constraint=None,
        main_trait_constraint=None,
        random_trait_constraint=None,
        main_skill_constraint=None,
        random_skill_constraint=None,
        reaction_random_cat=None,
        also_influences=None,
    ):
        self.id = interact_id
        self.intensity = intensity
        self.biome = biome if biome else ["any"]
        self.season = season if season else ["any"]
        self.interactions = (
            interactions
            if interactions
            else [i18n.t("defaults.interaction", id=interact_id)]
        )
        self.get_injuries = get_injuries if get_injuries else {}
        self.has_injuries = has_injuries if has_injuries else {}
        self.relationship_constraint = (
            relationship_constraint if relationship_constraint else []
        )
        self.backstory_constraint = backstory_constraint if backstory_constraint else {}
        self.main_status_constraint = (
            main_status_constraint if main_status_constraint else []
        )
        self.random_status_constraint = (
            random_status_constraint if random_status_constraint else []
        )
        self.main_trait_constraint = (
            main_trait_constraint if main_trait_constraint else []
        )
        self.random_trait_constraint = (
            random_trait_constraint if random_trait_constraint else []
        )
        self.main_skill_constraint = (
            main_skill_constraint if main_skill_constraint else []
        )
        self.random_skill_constraint = (
            random_skill_constraint if random_skill_constraint else []
        )
        self.reaction_random_cat = reaction_random_cat if reaction_random_cat else {}
        self.also_influences = also_influences if also_influences else {}


class GroupInteraction:
    def __init__(
        self,
        interact_id,
        biome=None,
        season=None,
        intensity="medium",
        cat_amount=None,
        interactions=None,
        get_injuries=None,
        has_injuries=None,
        status_constraint=None,
        trait_constraint=None,
        skill_constraint=None,
        relationship_constraint=None,
        backstory_constraint=None,
        specific_reaction=None,
        general_reaction=None,
    ):
        self.id = interact_id
        self.intensity = intensity
        self.biome = biome if biome else ["any"]
        self.season = season if season else ["any"]
        self.cat_amount = cat_amount
        self.interactions = (
            interactions
            if interactions
            else [i18n.t("defaults.interaction", id=interact_id)]
        )
        self.get_injuries = get_injuries if get_injuries else {}
        self.has_injuries = has_injuries if has_injuries else {}
        self.relationship_constraint = (
            relationship_constraint if relationship_constraint else {}
        )
        self.backstory_constraint = backstory_constraint if backstory_constraint else {}
        self.status_constraint = status_constraint if status_constraint else {}
        self.trait_constraint = trait_constraint if trait_constraint else {}
        self.skill_constraint = skill_constraint if skill_constraint else {}
        self.specific_reaction = specific_reaction if specific_reaction else {}
        self.general_reaction = general_reaction if general_reaction else {}


# ---------------------------------------------------------------------------- #
#                some useful functions related to interactions                 #
# ---------------------------------------------------------------------------- #


def cats_fulfill_single_interaction_constraints(
    main_cat, random_cat, interaction
) -> bool:
    """Check if the two cats fulfills the interaction constraints."""

    main_constraint_dict = {
        "status": interaction.main_status_constraint,
        "trait": interaction.main_trait_constraint,
        "backstory": interaction.backstory_constraint.get("m_c"),
        "skills": interaction.main_skill_constraint,
        "relationship_status": interaction.relationship_constraint,
    }
    random_constraint_dict = {
        "status": interaction.random_status_constraint,
        "trait": interaction.random_trait_constraint,
        "backstory": interaction.backstory_constraint.get("r_c"),
        "skills": interaction.random_skill_constraint,
    }

    main_cat_satisfied = event_for_cat(
        main_constraint_dict, main_cat, [main_cat, random_cat], event_id=interaction.id
    )
    random_cat_satisfied = event_for_cat(
        random_constraint_dict,
        random_cat,
        [random_cat, main_cat],
        event_id=interaction.id,
    )

    if len(interaction.has_injuries) >= 1:
        if "m_c" in interaction.has_injuries:
            injuries_in_needed = list(
                filter(
                    lambda inj: inj in interaction.has_injuries["m_c"],
                    main_cat.injuries.keys(),
                )
            )
            if len(injuries_in_needed) <= 0:
                return False
        if "r_c" in interaction.has_injuries:
            injuries_in_needed = list(
                filter(
                    lambda inj: inj in interaction.has_injuries["r_c"],
                    random_cat.injuries.keys(),
                )
            )
            if len(injuries_in_needed) <= 0:
                return False

    if main_cat_satisfied and random_cat_satisfied:
        return True

    return False


# ---------------------------------------------------------------------------- #
#                            BUILD MASTER DICTIONARY                           #
# ---------------------------------------------------------------------------- #


def create_interaction(inter_list) -> list:
    created_list = []
    for inter in inter_list:
        created_list.append(
            SingleInteraction(
                interact_id=inter["id"],
                biome=inter["biome"] if "biome" in inter else ["any"],
                season=inter["season"] if "season" in inter else ["any"],
                intensity=inter["intensity"] if "intensity" in inter else "medium",
                interactions=inter["interactions"] if "interactions" in inter else None,
                get_injuries=inter["get_injuries"] if "get_injuries" in inter else None,
                has_injuries=inter["has_injuries"] if "has_injuries" in inter else None,
                relationship_constraint=(
                    inter["relationship_constraint"]
                    if "relationship_constraint" in inter
                    else None
                ),
                backstory_constraint=(
                    inter["backstory_constraint"]
                    if "backstory_constraint" in inter
                    else None
                ),
                main_status_constraint=(
                    inter["main_status_constraint"]
                    if "main_status_constraint" in inter
                    else None
                ),
                random_status_constraint=(
                    inter["random_status_constraint"]
                    if "random_status_constraint" in inter
                    else None
                ),
                main_trait_constraint=(
                    inter["main_trait_constraint"]
                    if "main_trait_constraint" in inter
                    else None
                ),
                random_trait_constraint=(
                    inter["random_trait_constraint"]
                    if "random_trait_constraint" in inter
                    else None
                ),
                main_skill_constraint=(
                    inter["main_skill_constraint"]
                    if "main_skill_constraint" in inter
                    else None
                ),
                random_skill_constraint=(
                    inter["random_skill_constraint"]
                    if "random_skill_constraint" in inter
                    else None
                ),
                reaction_random_cat=(
                    inter["reaction_random_cat"]
                    if "reaction_random_cat" in inter
                    else None
                ),
                also_influences=(
                    inter["also_influences"] if "also_influences" in inter else None
                ),
            )
        )
    return created_list


def create_group_interaction(inter_list) -> list:
    created_list = []
    for inter in inter_list:
        created_list.append(
            GroupInteraction(
                interact_id=inter["id"],
                biome=inter["biome"] if "biome" in inter else ["any"],
                season=inter["season"] if "season" in inter else ["any"],
                cat_amount=inter["cat_amount"] if "cat_amount" in inter else None,
                intensity=inter["intensity"] if "intensity" in inter else "medium",
                interactions=inter["interactions"] if "interactions" in inter else None,
                get_injuries=inter["get_injuries"] if "get_injuries" in inter else None,
                has_injuries=inter["has_injuries"] if "has_injuries" in inter else None,
                status_constraint=(
                    inter["status_constraint"] if "status_constraint" in inter else None
                ),
                trait_constraint=(
                    inter["trait_constraint"] if "trait_constraint" in inter else None
                ),
                skill_constraint=(
                    inter["skill_constraint"] if "skill_constraint" in inter else None
                ),
                relationship_constraint=(
                    inter["relationship_constraint"]
                    if "relationship_constraint" in inter
                    else None
                ),
                backstory_constraint=(
                    inter["backstory_constraint"]
                    if "backstory_constraint" in inter
                    else None
                ),
                specific_reaction=(
                    inter["specific_reaction"] if "specific_reaction" in inter else None
                ),
                general_reaction=(
                    inter["general_reaction"] if "general_reaction" in inter else None
                ),
            )
        )
    return created_list


INTERACTION_MASTER_DICT = {x: {} for x in [*RelValue]}

relationship_lang = None


def rebuild_relationship_dicts():
    global INTERACTION_MASTER_DICT, relationship_lang
    if relationship_lang == i18n.config.get("locale"):
        return

    for rel in [*RelValue]:
        INTERACTION_MASTER_DICT[rel]["increase"] = create_interaction(
            load_lang_resource(
                f"events/relationship_events/normal_interactions/{rel}/increase.json"
            )
        )
        INTERACTION_MASTER_DICT[rel]["decrease"] = create_interaction(
            load_lang_resource(
                f"events/relationship_events/normal_interactions/{rel}/decrease.json"
            )
        )
