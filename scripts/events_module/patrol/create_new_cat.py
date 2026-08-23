from itertools import combinations
from random import choice, randint, getrandbits, choices, random

from scripts.cat.cats import Cat
from scripts.cat.constants import INJURIES, ILLNESSES, PERMANENT, BACKSTORIES
from scripts.cat.enums import CatRank, CatAge, CatGroup, CatStanding, CatSocial
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.names import Name
from scripts.cat.personality import Personality
from scripts.cat.skills import SkillPath, Skill
from scripts.cat.factories.typed_dicts import StatusDict
from scripts.cat_relations.cat_handle_funcs import create_relationships_new_cat
from scripts.cat_relations.inheritance2 import inheritance_db
from scripts.cat_relations.relationship import Relationship
from scripts.clan import OtherClan
from scripts.clan_package.settings import get_clan_setting
from scripts.cat.microservices.conditions import (
    get_ill,
    get_injured,
    get_permanent_condition,
)
from scripts.config import get_config
from scripts.events_module.consequences import change_relationship_values
from scripts.events_module.parameter_dicts import InvolvedCatDict
from scripts.game_structure import game, constants


# called the "updated" create_new_cat so that it's not conflicting with the existing create_new_cat
# eventually it should fully replace the old func and get renamed
def updated_create_new_cat(
    option_dict: InvolvedCatDict, involved_cats: dict[str, Cat], other_clan: OtherClan
) -> list[Cat]:
    """
    USED WITH "involved_cat" PARAMETER ONLY
    :param option_dict: the InvolvedCatDict for this cat(s)
    :param involved_cats: the dict of cats already involved in this event, key is event abbr and value is Cat object
    :param other_clan: the other clan involved in this event
    :return: list of created cats
    """
    option_dict = option_dict.copy()
    # STATUS
    status = StatusDict()
    if option_dict.get("status"):
        # check for "clancat" first since it's not really a rank
        if "clancat" in option_dict["status"]:
            status["social"] = CatSocial.CLANCAT
            possible_ranks = [r for r in option_dict["status"] if r != "clancat"]
            possible_ranks.extend(
                [
                    r
                    for r in [*CatRank]
                    if r.is_any_clancat_rank()
                    and r not in (CatRank.LEADER, CatRank.DEPUTY)
                ]
            )
        else:
            possible_ranks = option_dict["status"]

        status["rank"] = CatRank(choice(possible_ranks))
        # if no group given and the rank/social is a clancat, then assign to other clan
        if not option_dict.get("group") and (
            status["rank"].is_any_clancat_rank()
            or status.get("social") == CatSocial.CLANCAT
        ):
            status["group_ID"] = _get_id_for_group(
                [CatGroup.OTHER_CLAN], involved_cats, other_clan
            )
    if option_dict.get("age"):
        status["age"] = CatAge(choice(option_dict["age"]))

    # check if we need to match age to an assigned mate
    if option_dict.get("can_create_new_cat", {}).get("assign_mate"):
        possible_ages = []
        for m in option_dict["can_create_new_cat"].get("assign_mate", []):
            if m in involved_cats:
                possible_ages.append(involved_cats[m].age)
        status["age"] = choice(possible_ages)

    if option_dict.get("group"):
        status["group_ID"] = _get_id_for_group(
            option_dict["group"], involved_cats, other_clan
        )

    if not status.get("rank") and not status.get("age"):
        # if no group was given either, then we just pick either no group or other clan
        if not option_dict.get("group"):
            status["group_ID"] = _get_id_for_group(
                ["no_group", CatGroup.OTHER_CLAN], involved_cats, other_clan
            )

        # then we find an appropriate rank for that group
        if status["group_ID"] == "no_group":
            status["rank"] = choice(
                [r for r in [*CatRank] if not r.is_any_clancat_rank()]
            )
        else:
            status["rank"] = choice([r for r in [*CatRank] if r.is_any_clancat_rank()])

    # handle applying an age for litters if one wasn't specified
    is_litter = option_dict["can_create_new_cat"].get("become_litter")
    if is_litter:
        if not status.get("age") or not status["age"].is_baby():
            status["age"] = choice((CatAge.NEWBORN, CatAge.KITTEN))

    # MOONS OLD
    moons = None
    if status.get("age"):
        moons = randint(
            Cat.age_moons[status["age"]][0], Cat.age_moons[status["age"]][1]
        )

    # PARENTS
    blood_parents: list[Cat] = []
    adoptive_parents: list[Cat] = []

    for p in option_dict["can_create_new_cat"].get("assign_blood_parent", []):
        if p in involved_cats:
            if isinstance(involved_cats[p], list):
                blood_parents.extend(involved_cats[p])
            else:
                blood_parents.append(involved_cats[p])
    for p in option_dict["can_create_new_cat"].get("assign_adoptive_parent", []):
        if p in involved_cats:
            if isinstance(involved_cats[p], list):
                adoptive_parents.extend(involved_cats[p])
            else:
                adoptive_parents.append(involved_cats[p])

    # GENDER
    gender = option_dict.get("gender", None)
    if gender == "can_birth":
        if not get_clan_setting("same sex birth"):
            gender = "female"
        else:
            gender = None

    # CREATE CATS
    new_cats = []
    num_of_cats = randint(2, 6) if is_litter else 1

    for i in range(num_of_cats):
        created_cat = NewCatFactory.create_cat(
            status_dict=status,
            moons=moons,
            gender=gender,
            parent1=blood_parents[0].ID if blood_parents else None,
            parent2=blood_parents[1].ID if len(blood_parents) > 1 else None,
            adoptive_parents=[p.ID for p in adoptive_parents]
            if adoptive_parents
            else None,
        )
        # check if kittypets get collar
        if created_cat.status.social == CatSocial.KITTYPET and bool(getrandbits(1)):
            created_cat.pelt.accessory = (
                *created_cat.pelt.accessory,
                choice(created_cat.pelt.collar_accessories),
            )

        # MATES
        _assign_mates(created_cat, involved_cats, option_dict)

        # PAST STATUS
        _assign_past_status_and_standing(
            created_cat, option_dict, involved_cats, other_clan
        )

        # CURRENT STANDING
        _assign_current_standing(created_cat, option_dict, involved_cats, other_clan)

        # TRAIT AND SKILL
        _assign_stats(created_cat, option_dict)

        # HEALTH
        _assign_health(created_cat, option_dict)

        # BACKSTORY
        _assign_backstory(created_cat, option_dict)

        # NAME
        _assign_name(created_cat)

        create_relationships_new_cat(created_cat)
        game.clan.add_cat(created_cat)
        new_cats.append(created_cat)

    # ESTABLISH FAMILY RELATIONSHIPS
    # parent to kid
    if blood_parents or adoptive_parents:
        for p in blood_parents + adoptive_parents:
            for c in new_cats:
                if c.ID not in p.relationships:
                    p.relationships[c.ID] = Relationship(
                        cat_from=p, cat_to=c, family=True
                    )
                if p.ID not in c.relationships:
                    c.relationships[p.ID] = Relationship(
                        cat_from=c, cat_to=p, family=True
                    )

        change_relationship_values(
            cats_to=new_cats,
            cats_from=blood_parents + adoptive_parents,
            **get_config("new_cat.parent_buff.parent_to_kit"),
        )
        change_relationship_values(
            cats_to=blood_parents + adoptive_parents,
            cats_from=new_cats,
            **get_config("new_cat.parent_buff.kit_to_parent"),
        )

    # littermate to littermate
    if is_litter:
        for pair in combinations(new_cats, 2):
            if pair[0].ID not in pair[1].relationships:
                pair[1].relationships[pair[0].ID] = Relationship(
                    cat_from=pair[1], cat_to=pair[0], family=True
                )
            if pair[1].ID not in pair[0].relationships:
                pair[0].relationships[pair[1].ID] = Relationship(
                    cat_from=pair[0], cat_to=pair[1], family=True
                )

        change_relationship_values(
            cats_to=new_cats,
            cats_from=new_cats,
            **get_config("new_cat.sib_buff.cat1_to_cat2"),
        )

        pass

    # UPDATE INHERITANCE if we had any assignments that would change them
    if (
        blood_parents
        or adoptive_parents
        or is_litter
        or option_dict["can_create_new_cat"].get("assign_mate")
    ):
        inheritance_db.load_inheritances(Cat)

    return new_cats


def _assign_mates(
    created_cat: Cat, involved_cats: dict[str, Cat], option_dict: InvolvedCatDict
):
    if option_dict["can_create_new_cat"].get("assign_mate"):
        for m in option_dict["can_create_new_cat"].get("assign_mate", []):
            if m in involved_cats:
                # we delay inheritance recalc because we'll handle it later on, and we don't want to do it twice
                created_cat.set_mate(involved_cats[m], recalculate_inheritance=False)


def _assign_name(created_cat: Cat):
    if not created_cat.status.social == CatSocial.CLANCAT:
        # if it ain't a clancat, give it a non-clancat name
        name_categories = [
            "silly_names",
            "human_names",
            "loner_names",
            "normal_prefixes",
        ]
        # defaults in case of error
        weights = [1, 1, 1, 1]
        # give kittypets a kittypet name
        if created_cat.status.social == CatSocial.KITTYPET:
            weights = constants.CONFIG["cat_name_controls"]["kittypet"]
            # check if the kittypets come with a pretty acc
            if bool(getrandbits(1)):
                created_cat.pelt.accessory = (
                    *created_cat.pelt.accessory,
                    choice(created_cat.pelt.collar_accessories),
                )
        if created_cat.status.social == CatSocial.LONER:
            weights = constants.CONFIG["cat_name_controls"]["loner"]

        if created_cat.status.social == CatSocial.ROGUE:
            weights = constants.CONFIG["cat_name_controls"]["rogue"]

        selected_category = choices(name_categories, weights, k=1)[0]
        name = choice(Name.names_dict[selected_category])
        created_cat.change_name(new_prefix=name, new_suffix="")


def _assign_backstory(created_cat, option_dict):
    if option_dict.get("backstory"):
        possible_stories = []
        for story in option_dict["backstory"]:
            if story in set(
                [
                    backstory
                    for backstory_block in BACKSTORIES["backstory_categories"].values()
                    for backstory in backstory_block
                ]
            ):
                possible_stories.append(story)
            elif story in BACKSTORIES["backstory_categories"]:
                possible_stories.extend(BACKSTORIES["backstory_categories"][story])

        created_cat.backstory = choice(possible_stories)
    else:
        # figure out an appropriate backstory for who they are
        baby = created_cat.age.is_baby()
        social = created_cat.status.social
        categories = BACKSTORIES["backstory_categories"]

        if social == CatSocial.LONER:
            created_cat.backstory = (
                choice(categories["baby_loner_backstories"])
                if baby
                else choice(categories["loner_backstories"])
            )
        elif social == CatSocial.ROGUE:
            created_cat.backstory = (
                choice(categories["baby_rogue_backstories"])
                if baby
                else choice(categories["rogue_backstories"])
            )
        elif social == CatSocial.KITTYPET:
            created_cat.backstory = (
                choice(categories["baby_kittypet_backstories"])
                if baby
                else choice(categories["kittypet_backstories"])
            )
        elif social == CatSocial.CLANCAT:
            created_cat.backstory = (
                choice(categories["baby_clancat_backstories"])
                if baby
                else choice(categories["former_clancat_backstories"])
            )


def _assign_health(created_cat, option_dict):
    # Remove disabling scars, if they generated.
    # these are removed bc the cat won't have the associated perm condition
    not_allowed = [
        "NOPAW",
        "NOTAIL",
        "HALFTAIL",
        "NOEAR",
        "BOTHBLIND",
        "RIGHTBLIND",
        "LEFTBLIND",
        "BRIGHTHEART",
        "NOLEFTEAR",
        "NORIGHTEAR",
        "MANLEG",
    ]

    created_cat.pelt.scars = tuple(
        scar for scar in created_cat.pelt.scars if scar not in not_allowed
    )

    # now see if any new conditions should be applied
    if option_dict.get("health", {}).get("condition"):
        condition = choice(option_dict["health"]["condition"])
        if condition in INJURIES:
            get_injured(created_cat, name=condition)
        elif condition in ILLNESSES:
            get_ill(created_cat, illness_name=condition)
        elif condition in PERMANENT:
            get_permanent_condition(
                created_cat,
                name=condition,
                born_with=option_dict["health"].get("must_be_congenital", False),
            )
            if condition in ("lost a leg", "born without a leg"):
                created_cat.pelt.scars = (*created_cat.pelt.scars, "NOPAW")
            elif condition in ("lost their tail", "born without a tail"):
                created_cat.pelt.scars = (*created_cat.pelt.scars, "NOTAIL")

    # RANDOM PERM CONDITION ASSIGNMENT
    # chance to give the new cat a permanent condition, higher chance for found kits and litters
    if created_cat.age.is_baby():
        chance = int(
            constants.CONFIG["cat_generation"]["base_permanent_condition"] / 11.25
        )
    else:
        chance = constants.CONFIG["cat_generation"]["base_permanent_condition"] + 10
    if not int(random() * chance):
        possible_conditions = []
        for condition in PERMANENT:
            if created_cat.age.is_baby() and PERMANENT[condition]["congenital"] not in [
                "always",
                "sometimes",
            ]:
                continue
            # next part ensures that a kit won't get a condition that takes too long to reveal
            moons = created_cat.moons
            leeway = 5 - (PERMANENT[condition]["moons_until"] + 1)
            if moons > leeway:
                continue
            possible_conditions.append(condition)

        if possible_conditions:
            chosen_condition = choice(possible_conditions)
            if PERMANENT[chosen_condition]["congenital"] in [
                "always",
                "sometimes",
            ]:
                get_permanent_condition(created_cat, chosen_condition, True)
                if (
                    created_cat.permanent_condition[chosen_condition]["moons_until"]
                    == 0
                ):
                    created_cat.permanent_condition[chosen_condition][
                        "moons_until"
                    ] = -2

            # assign scars
            if chosen_condition in ("lost a leg", "born without a leg"):
                created_cat.pelt.scars = (*created_cat.pelt.scars, "NOPAW")
            elif chosen_condition in ("lost their tail", "born without a tail"):
                created_cat.pelt.scars = (*created_cat.pelt.scars, "NOTAIL")


def _assign_stats(created_cat, option_dict):
    if option_dict.get("stat"):
        skills = option_dict["stat"].get("skill", [])
        traits = option_dict["stat"].get("trait", [])

        # if kitty is not required to have both, then we randomly dump one of the lists
        if not option_dict["stat"].get("must_have_both") and (skills and traits):
            if randint(1, 2) == 1:
                skills.clear()
            else:
                traits.clear()

        if skills:
            skill_info = choice(skills).split(",")
            path = SkillPath[skill_info[0]]
            tier = max(int(skill_info[1]), 1)
            points = randint(
                Skill.tier_ranges[tier - 1][0],
                Skill.tier_ranges[tier - 1][1],
            )
            created_cat.skills.primary = Skill(
                path=path,
                points=points,
                interest_only=created_cat.age
                in (CatAge.KITTEN, CatAge.NEWBORN, CatAge.ADOLESCENT),
            )

        if traits:
            created_cat.personality = Personality(trait=choice(traits))


def _assign_current_standing(
    created_cat, option_dict, involved_cats, other_clan: OtherClan
):
    if option_dict.get("standing", {}).get("currently"):
        group = _get_id_for_group(
            option_dict["standing"]["group"], involved_cats, other_clan
        )

        created_cat.status.change_standing(
            new_standing=CatStanding(choice(option_dict["standing"]["currently"])),
            group_ID=group,
        )


def _assign_past_status_and_standing(
    created_cat, option_dict, involved_cats, other_clan: OtherClan
):
    status = StatusDict()
    if option_dict.get("past_status"):
        # check for "clancat" first since it's not really a rank
        if "clancat" in option_dict["past_status"]:
            status["social"] = CatSocial.CLANCAT
            possible_ranks = [r for r in option_dict["past_status"] if r != "clancat"]
            possible_ranks.extend([r for r in [*CatRank] if r.is_any_clancat_rank()])
        else:
            possible_ranks = option_dict["past_status"]

        status["rank"] = CatRank(choice(possible_ranks))
        # if no group given and the rank/social is a clancat, then assign to other clan
        if not option_dict.get("group") and (
            status["rank"].is_any_clancat_rank()
            or status.get("social") == CatSocial.CLANCAT
        ):
            status["group_ID"] = _get_id_for_group(
                [CatGroup.OTHER_CLAN], involved_cats, other_clan
            )

        created_cat.status.generate_new_status(**status)
    if option_dict.get("standing", {}).get("past"):
        group = _get_id_for_group(
            option_dict["standing"]["group"], involved_cats, other_clan
        )

        created_cat.status.change_standing(
            new_standing=CatStanding(choice(option_dict["standing"]["past"])),
            group_ID=group,
        )
        # then change to KNOWN so that the standing we had just assigned won't be the current one
        created_cat.status.change_standing(
            new_standing=CatStanding.KNOWN,
            group_ID=group,
        )
    # now set back to current status
    # we do this after the past standing is applied in order to avoid any overwriting of memberships
    if option_dict.get("past_status"):
        if option_dict.get("group"):
            group = _get_id_for_group(option_dict["group"], involved_cats, other_clan)

            created_cat.status.add_to_group(
                new_group_ID=group,
                become_rank=CatRank(choice(option_dict["status"]))
                if option_dict.get("status")
                else None,
            )
        if option_dict.get("status") and created_cat.status.rank == status["rank"]:
            created_cat.status._change_rank(CatRank(choice(option_dict["status"])))

    # this simulates a "history" as whomever they used to be
    created_cat.status.change_current_moons_as(created_cat.moons)


def _get_id_for_group(
    group_list: list[str], involved_cats: dict[str, Cat], other_clan: OtherClan
) -> str:
    possible_groups = []

    # handle match tags
    match_group = None
    for tag in group_list:
        if "match" in tag:
            cat_to_match = tag.replace("match:", "")
            match_group = involved_cats[cat_to_match].status.group
        if tag == "no_group":
            possible_groups.append("no_group")

    if match_group:
        group_list.append(match_group)

    # now find IDs for the groups
    for ID, group in game.used_group_IDs.items():
        if group in group_list:
            # only allow this event's chosen other clan
            if group == CatGroup.OTHER_CLAN and ID != other_clan.group_ID:
                continue
            possible_groups.append(ID)

    group = choice(possible_groups)
    return group
