import math
from random import choice, randint, random, randrange
from typing import Optional

import i18n

from scripts.cat.cats import Cat
from scripts.cat.enums import CatAge, CatSocial, CatGroup, CatThought, CatCompatibility
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.factories.typed_dicts import StatusDict
from scripts.cat.names import Name
from scripts.cat_relations.enums import RelType
from scripts.cat_relations.inheritance2 import inheritance_db
from scripts.cat_relations.relationship import Relationship, create_one_relationship
from scripts.clan_package.settings import get_clan_setting
from scripts.cat.microservices.conditions import add_congenital_condition
from scripts.config import get_config
from scripts.events_module.event_information import EventInformation
from scripts.events_module.consequences import (
    create_new_cat,
    change_relationship_values,
)
from scripts.events_module.event_filters import get_personality_compatibility
from scripts.events_module.pregnancy.build_strings import get_newborn_strings
from scripts.events_module.pregnancy.check_family_size import (
    biggest_family_is_big,
    get_biggest_family,
)
from scripts.events_module.short.condition_events import Condition_Events
from scripts.events_module.text_adjust import event_text_adjust, adjust_list_text
from scripts.game_structure import game


def get_kits(
    kits_amount: int,
    cat: Optional[Cat] = None,
    other_cat: Optional[Cat] = None,
    adoptive_parents: Optional[list] = None,
):
    """
    Create some amount of kits
    If no parents are specified, it will create a blood parents for all the
    kits to be related to. They may be dead or alive, but will always be outside
    the clan.
    """
    all_kitten = []
    if not adoptive_parents:
        adoptive_parents = []

    # First, just a check: If we have no cat, but an other_cat was provided, swap other_cat to cat:
    # This way, we can ensure that if only one parent is provided, it's cat, not other_cat.
    # And if cat is None, we know that no parents were provided.
    if other_cat and not cat:
        cat = other_cat
        other_cat = None

    blood_parent = None

    ##### SELECT BACKSTORY #####
    if cat and "pregnant" in cat.injuries:
        backstory = choice(["halfclan1", "outsider_roots1"])
    elif cat:
        backstory = choice(["halfclan2", "outsider_roots2"])
    else:  # cat is adopted
        backstory = choice(["abandoned1", "abandoned2", "abandoned3", "abandoned4"])
    ###########################

    ##### ADOPTIVE PARENTS #####
    # First, gather all the mates of the provided bio parents to be added
    # as adoptive parents (if there is  a poly relationship).
    all_adoptive_parents = []
    birth_parents = [i.ID for i in (cat, other_cat) if i]

    # ----- CAT MATES -----
    if cat and cat.mate:
        poly_parenting = bool(other_cat and other_cat.ID in cat.mate)

        for mate_id in cat.mate:
            if mate_id is None:
                continue

            mate = Cat.fetch_cat(mate_id)
            if not mate or not mate.status.alive_in_player_clan:
                continue

            add_poly_mate = poly_parenting and mate.ID != other_cat.ID

            if (
                add_poly_mate
                and mate.ID not in birth_parents
                and mate.ID not in all_adoptive_parents
            ):
                all_adoptive_parents.append(mate_id)

    # ----- OTHER CAT MATES -----
    if other_cat and other_cat.mate:
        poly_parenting = bool(cat and cat.ID in other_cat.mate)

        for mate_id in other_cat.mate:
            if mate_id is None:
                continue

            mate = Cat.fetch_cat(mate_id)
            if not mate or not mate.status.alive_in_player_clan:
                continue

            add_poly_mate = poly_parenting and mate.ID != cat.ID

            if (
                add_poly_mate
                and mate.ID not in birth_parents
                and mate.ID not in all_adoptive_parents
            ):
                all_adoptive_parents.append(mate_id)
    # Then, add any additional adoptive parents that were provided passed directly into the
    # function.
    for _mate in adoptive_parents:
        if _mate not in all_adoptive_parents:
            all_adoptive_parents.append(_mate)

    #############################

    #### GENERATE THE KITS ######
    for kit in range(kits_amount):
        # shouldn't have to use this initial assignment, but just in case, we'll set it as newborn
        kitten_status = {"age": CatAge.NEWBORN}

        # setup basic clan kitten status
        if cat:
            kitten_status: StatusDict = {
                "social": cat.status.social,
                "age": CatAge.NEWBORN,
                "group_ID": cat.status.group_ID,
            }

        if not cat:
            # No parents provided, create a blood parent - this is an adoption.
            if not blood_parent:
                # Generate a blood parent if we haven't already.
                thought = i18n.t(
                    "conditions.pregnancy.half_blood_kitting_thought",
                    count=kits_amount,
                )

                blood_parent = create_new_cat(
                    Cat,
                    original_social=choice((CatSocial.LONER, CatSocial.KITTYPET)),
                    alive=False,
                    moons=randint(15, 120),
                    outside=True,
                )[0]
                thought = event_text_adjust(Cat, text=thought, main_cat=blood_parent)
                blood_parent.thought = thought

            kitten_status: StatusDict = {
                "social": blood_parent.status.social,
                "age": CatAge.NEWBORN,
                "group_ID": blood_parent.status.get_last_living_group(),
            }

            kit = NewCatFactory.create_cat(
                parent1=blood_parent.ID,
                moons=0,
                backstory=backstory,
                status=kitten_status,
            )

        elif cat and other_cat:
            # Two parents provided
            # The cat that gave birth is always parent1 so there is no need to check gender
            kit = NewCatFactory.create_cat(
                parent1=cat.ID,
                parent2=other_cat.ID,
                moons=0,
                status_dict=kitten_status,
            )
        else:
            # A one blood parent litter is the only option left.
            kit = NewCatFactory.create_cat(
                parent1=cat.ID,
                moons=0,
                backstory=backstory,
                status_dict=kitten_status,
            )

        kit.assign_thought()

        # make lost status match parent
        if cat and cat.status.is_lost():
            kit.status.make_standing_unknown(CatGroup.PLAYER_CLAN_ID)
            kit.status.become_lost(
                cat.status.social, specific_group=CatGroup.PLAYER_CLAN_ID
            )

        # Prevent duplicate prefixes in the same litter
        while kit.name.prefix in [kitty.name.prefix for kitty in all_kitten]:
            kit.name = Name("newborn")

        all_kitten.append(kit)
        # adoptive parents are set at the end, when everything else is decided

        # remove scars
        kit.pelt.scars = tuple()

        # try to give them a permanent condition. 1/90 chance
        # don't delete the game.clan condition, this is needed for a test
        if game.clan and not int(
            random() * get_config("cat_generation.base_permanent_condition")
        ):
            add_congenital_condition(kit)
            for condition in kit.permanent_condition:
                if kit.permanent_condition[condition] == "born without a leg":
                    cat.pelt.scars = (*cat.pelt.scars, "NOPAW")
                elif kit.permanent_condition[condition] == "born without a tail":
                    cat.pelt.scars = (*cat.pelt.scars, "NOTAIL")
            Condition_Events.handle_already_disabled(kit)

        # create and update relationships
        relationships_to_update = []
        # if kits are in a clan, the whole clan gets to know
        if cat and cat.status.alive_in_player_clan:
            relationships_to_update = game.clan.clan_cats
        # if they aren't, then they only know parents, sibling rels will be added later
        elif cat:
            relationships_to_update = [cat.ID]
            # other parent only knows if they're in the same group
            if other_cat and other_cat.status.group == cat.status.group:
                relationships_to_update.append(other_cat.ID)

        if relationships_to_update:
            for cat_id in relationships_to_update:
                if cat_id == kit.ID:
                    continue
                the_cat = Cat.all_cats.get(cat_id)
                if the_cat.dead:
                    continue
                if the_cat.ID in kit.get_parents():
                    parent_to_kit = get_config("new_cat.parent_buff.parent_to_kit")
                    y = randrange(0, 15)
                    start_relation = Relationship(the_cat, kit, family=True)
                    start_relation.like = parent_to_kit[RelType.LIKE] + y
                    start_relation.comfort = parent_to_kit[RelType.COMFORT] + y
                    start_relation.respect = parent_to_kit[RelType.RESPECT] + y
                    start_relation.trust = parent_to_kit[RelType.TRUST] + y
                    the_cat.relationships[kit.ID] = start_relation

                    kit_to_parent = get_config("new_cat.parent_buff.kit_to_parent")
                    y = randrange(0, 15)
                    start_relation = Relationship(kit, the_cat, family=True)
                    start_relation.like += kit_to_parent[RelType.LIKE] + y
                    start_relation.comfort = kit_to_parent[RelType.COMFORT] + y
                    start_relation.respect = kit_to_parent[RelType.RESPECT] + y
                    start_relation.trust = kit_to_parent[RelType.TRUST] + y
                    kit.relationships[the_cat.ID] = start_relation
                else:
                    the_cat.relationships[kit.ID] = Relationship(the_cat, kit)
                    kit.relationships[the_cat.ID] = Relationship(kit, the_cat)

        #### REMOVE ACCESSORY ######
        kit.pelt.accessory = tuple()
        game.clan.add_cat(kit)

        #### GIVE HISTORY ######
        kit.history.add_beginning(clan_born=bool(cat))

    # check other cats of Clan for siblings
    for kitten in all_kitten:
        # update/buff the relationship towards the siblings
        for second_kitten in all_kitten:
            y = randrange(0, 15)
            if second_kitten.ID == kitten.ID:
                continue
            relationship_value = get_config("new_cat.sib_buff.littermates_to_eachother")
            start_relation = Relationship(kitten, second_kitten, False, True)
            start_relation.like += relationship_value["like"] + y
            start_relation.comfort += relationship_value["comfort"] + y
            start_relation.trust += relationship_value["trust"] + y
            kitten.relationships[second_kitten.ID] = start_relation

    # check if the possible adoptive cat is not already in the family tree and
    # add them as adoptive parents if not
    final_adoptive_parents = []
    for adoptive_p in all_adoptive_parents:
        Cat.fetch_cat(adoptive_p).assign_thought(CatThought.ON_BIRTH)
        if adoptive_p not in inheritance_db.get_relatives(all_kitten[0].ID, True):
            final_adoptive_parents.append(adoptive_p)
    if not adoptive_parents:
        cat.assign_thought(CatThought.ON_BIRTH)
        if other_cat:
            cat.assign_thought(CatThought.ON_BIRTH)

    # Add the adoptive parents.
    if final_adoptive_parents:
        for kit in all_kitten:
            kit.adoptive_parents = final_adoptive_parents

            # update relationship for adoptive parents
            for parent_id in final_adoptive_parents:
                parent = Cat.fetch_cat(parent_id)
                if parent:
                    kit_to_parent = get_config("new_cat.parent_buff.kit_to_parent")
                    parent_to_kit = get_config("new_cat.parent_buff.parent_to_kit")
                    change_relationship_values(
                        cats_from=[kit],
                        cats_to=[parent],
                        **kit_to_parent,
                    )
                    change_relationship_values(
                        cats_from=[parent],
                        cats_to=[kit],
                        **parent_to_kit,
                    )

    inheritance_db.load_inheritances(Cat)

    # check for more extended family members to create relationships with
    all_relatives: list = all_kitten[
        0
    ].get_relatives()  # we only need this for one kit, since they all share relatives
    parents = all_kitten[0].get_parents()
    # getting the cat objects
    all_relatives = [
        Cat.fetch_cat(c)
        for c in all_relatives
        if c not in list(parents) and c not in [k.ID for k in all_kitten]
    ]
    all_relatives = [c for c in all_relatives if c.status.alive_in_player_clan]

    for kit in all_kitten:
        for c in all_relatives:
            ext_relative_modifier = get_config("new_cat.ext_relative_modifier")
            rel_reflection = ext_relative_modifier * len(parents)
            variation_range = math.ceil(20 / len(parents))
            y = randrange(-variation_range, variation_range)

            # this finds what the relative's relationship is toward each parent and applies a reflection of that
            # relationship to the kit. reflection values will be divided by 4 by default and then modified
            # by the random y value
            new_relationship = {
                "cats_to": [kit],
                "cats_from": [c],
                "like": 0,
                "comfort": 0,
                "respect": 0,
                "trust": 0,
            }
            for parent_id in parents:
                try:
                    relation_toward_parent: Relationship = c.relationships[parent_id]
                except KeyError:
                    # cat had no relationship toward parent
                    continue

                new_relationship["like"] += (
                    int(relation_toward_parent.like / rel_reflection) + y
                    if relation_toward_parent.like
                    else 5
                )
                new_relationship["comfort"] += (
                    int(relation_toward_parent.comfort / rel_reflection) + y
                    if relation_toward_parent.comfort
                    else 0
                )
                new_relationship["respect"] += (
                    int(relation_toward_parent.respect / rel_reflection) + y
                    if relation_toward_parent.respect
                    else 0
                )
                new_relationship["trust"] += (
                    int(relation_toward_parent.trust / rel_reflection) + y
                    if relation_toward_parent.trust
                    else 0
                )

            # determine what sort of relationship we've ended up with
            rel_amounts = [
                new_relationship["like"],
                new_relationship["comfort"],
                new_relationship["respect"],
                new_relationship["trust"],
            ]
            neg = False
            pos = False
            for digit in rel_amounts:
                if digit < 0:
                    neg = True
                else:
                    pos = True
                if neg and pos:
                    break

            if pos and neg:
                rel_type = "neutral"
            elif pos:
                rel_type = "positive"
            else:
                rel_type = "negative"

            # adds reaction text to type postscript and age postscript
            new_relationship["log"] = i18n.t(
                f"relationships.{rel_type}_postscript",
                text=event_text_adjust(
                    Cat,
                    choice(get_newborn_strings()[f"{rel_type}_log"]),
                    main_cat=c,
                    random_cat=kit,
                    clan=game.clan,
                ),
            )

            change_relationship_values(**new_relationship)

    return all_kitten


def handle_adoption(cat: Cat, other_cat: Optional[Cat] = None):
    """Handle if the there is no pregnancy but the pair triggered kits chance."""
    if other_cat and (
        not other_cat.status.alive_in_player_clan or other_cat.birth_cooldown
    ):
        return

    # if the parents are already expecting, then they don't need to adopt
    if (cat.ID in game.clan.pregnancy_data) or (
        other_cat and other_cat.ID in game.clan.pregnancy_data
    ):
        return

    # Gather adoptive parents, to feed into the
    # get kits function.
    adoptive_parents = [cat.ID]
    if other_cat:
        adoptive_parents.append(other_cat.ID)

    for _m in cat.mate:
        if _m not in adoptive_parents:
            adoptive_parents.append(_m)

    if other_cat:
        for _m in other_cat.mate:
            if _m not in adoptive_parents:
                adoptive_parents.append(_m)

    amount = get_amount_of_kits(cat)
    kits = get_kits(amount, None, None, adoptive_parents=adoptive_parents)

    event = "hardcoded.adoption_kittens_single"
    cats_names = str(cat.name)
    if other_cat:
        event = "hardcoded.adoption_kittens_pair"
        cats_names = adjust_list_text([str(cat.name), str(other_cat.name)])

    print_event = i18n.t(
        event,
        names=cats_names,
        insert=i18n.t("conditions.pregnancy.kit_amount", count=amount),
        count=amount,
    )

    cats_involved = {"m_c": cat}
    cat.assign_thought(CatThought.ON_BIRTH)
    if other_cat:
        cats_involved["r_c"] = other_cat
        other_cat.assign_thought(CatThought.ON_BIRTH)

    for kit in kits:
        kit.assign_thought()

    # Normally, birth cooldown is only applied to cat who gave birth. However, if we don't apply birth cooldown to
    # adoption, we get too much adoption, since adoptive couples are using the increased two-parent kits chance.
    # We will only apply it to "cat" in this case, which is enough to stop the couple from adopting about within
    # the window.
    cat.birth_cooldown = get_config("pregnancy.birth_cooldown")

    game.cur_events_list.append(
        EventInformation(print_event, ["birth_death"], cat_dict=cats_involved)
    )


def get_amount_of_kits(cat: Cat):
    """Get the amount of kits which will be born."""
    min_kits = get_config("pregnancy.min_kits")
    min_kit = [min_kits] * get_config(f"pregnancy.one_kit_possibility.{cat.age.value}")
    two_kits = [min_kits + 1] * get_config(
        f"pregnancy.two_kit_possibility.{cat.age.value}"
    )
    three_kits = [min_kits + 2] * get_config(
        f"pregnancy.three_kit_possibility.{cat.age.value}"
    )
    four_kits = [min_kits + 3] * get_config(
        f"pregnancy.four_kit_possibility.{cat.age.value}"
    )
    five_kits = [min_kits + 4] * get_config(
        f"pregnancy.five_kit_possibility.{cat.age.value}"
    )
    max_kits = [get_config("pregnancy.max_kits")] * get_config(
        f"pregnancy.max_kit_possibility.{cat.age.value}"
    )
    amount = choice(min_kit + two_kits + three_kits + four_kits + five_kits + max_kits)
    return amount


def get_balanced_kit_chance(first_parent: Cat, second_parent: Cat, is_affair) -> int:
    """Returns the chance for these cats to have kittens together"""
    # Now that the second parent is determined, we can calculate the balanced chance for kits
    # get the chance for pregnancy
    if first_parent.mate and not is_affair:
        inverse_chance = get_config("pregnancy.primary_chance_mated")
    else:
        inverse_chance = get_config("pregnancy.primary_chance_unmated")

    # SETTINGS
    # - decrease inverse chance if only mated pairs can have kits
    if not get_clan_setting("single parentage") or not get_clan_setting(
        "unmated parentage"
    ):
        inverse_chance = int(inverse_chance * 0.7)

    # - decrease inverse chance if affairs are not allowed
    if not get_clan_setting("affair"):
        inverse_chance = int(inverse_chance * 0.7)

    # CURRENT CAT AMOUNT
    # - increase the inverse chance if the clan is bigger
    clan_size = len([i for i in Cat.all_cats.values() if i.status.alive_in_player_clan])
    if clan_size < 10:
        inverse_chance = int(inverse_chance * 0.5)
    elif clan_size > 30:
        inverse_chance = int(inverse_chance * (clan_size / 30))

    # COMPATIBILITY
    # - decrease / increase depending on the compatibility
    if second_parent:
        comp = get_personality_compatibility(first_parent, second_parent)
        if comp != CatCompatibility.NEUTRAL:
            buff = 0.85
            if comp == CatCompatibility.NEGATIVE:
                buff += 0.3
            inverse_chance = int(inverse_chance * buff)

    # RELATIONSHIP
    # - decrease the inverse chance if the cats are getting along well
    if second_parent:
        # get the needed relationships
        if second_parent.ID in first_parent.relationships:
            first_to_second_relationship = first_parent.relationships[second_parent.ID]
        else:
            first_to_second_relationship = create_one_relationship(
                first_parent, second_parent
            )
        if first_parent.ID in second_parent.relationships:
            second_to_first_relationship = second_parent.relationships[first_parent.ID]
        else:
            second_to_first_relationship = create_one_relationship(
                second_parent, first_parent
            )

        average_romantic_love = (
            first_to_second_relationship.romance + second_to_first_relationship.romance
        ) / 2
        average_comfort = (
            first_to_second_relationship.comfort + second_to_first_relationship.comfort
        ) / 2
        average_trust = (
            first_to_second_relationship.trust + second_to_first_relationship.trust
        ) / 2

        if average_romantic_love >= 85:
            inverse_chance -= int(inverse_chance * 0.3)
        elif average_romantic_love >= 55:
            inverse_chance -= int(inverse_chance * 0.2)
        elif average_romantic_love >= 35:
            inverse_chance -= int(inverse_chance * 0.1)

        if average_comfort >= 85:
            inverse_chance -= int(inverse_chance * 0.3)
        elif average_comfort >= 55:
            inverse_chance -= int(inverse_chance * 0.2)
        elif average_comfort >= 35:
            inverse_chance -= int(inverse_chance * 0.1)

        if average_trust >= 85:
            inverse_chance -= int(inverse_chance * 0.3)
        elif average_trust >= 55:
            inverse_chance -= int(inverse_chance * 0.2)
        elif average_trust >= 35:
            inverse_chance -= int(inverse_chance * 0.1)

    # AGE
    # - decrease the inverse chance if the whole clan is really old
    avg_age = int(sum((cat.moons for cat in Cat.all_cats.values())) / clan_size)
    if avg_age > 80:
        inverse_chance = int(inverse_chance * 0.8)

    # CURRENT KIT COUNT
    # increases inverse chance according to number of existing children (ex. 5 kids will multiply by 1.5)
    inverse_chance += int(inverse_chance * len(first_parent.get_children()) * 0.1)

    # 'INBREED' counter
    # - increase inverse chance if one of the current cats belongs in the biggest family
    biggest_family = get_biggest_family()

    if (
        first_parent.ID in biggest_family
        or second_parent
        and second_parent.ID in biggest_family
    ):
        inverse_chance = int(inverse_chance * 1.7)

    # - decrease inverse chance if the current family is small
    if len(first_parent.get_relatives(get_clan_setting("first cousin mates"))) < (
        clan_size / 15
    ):
        inverse_chance = int(inverse_chance * 0.7)

    # - decrease inverse chance for single parents if settings allow and biggest family is huge
    settings_allow = not second_parent and not get_clan_setting("single parentage")
    if settings_allow and biggest_family_is_big():
        inverse_chance = int(inverse_chance * 0.9)

    return inverse_chance
