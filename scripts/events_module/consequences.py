import re
from random import getrandbits, randint, choice, randrange, choices, random, sample
from typing import Optional, List, Union, Type

import i18n

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank, CatAge, CatSocial, CatGroup, CatStanding
from scripts.cat.names import names
from scripts.cat_relations.enums import RelType
from scripts.clan_package.settings import get_clan_setting
from scripts.game_structure import game, constants
from scripts.cat.constants import BACKSTORIES, PERMANENT
from scripts.events_module.text_adjust import process_text


def create_new_cat_block(
    Cat: Optional["Cat"],
    Relationship,
    event,
    in_event_cats: dict,
    i: int,
    attribute_list: List[str],
    other_clan=None,
) -> list:
    """
    Creates a single new_cat block and then generates and returns the cats within the block
    :param Cat Cat: always pass Cat class
    :param Relationship Relationship: always pass Relationship class
    :param event: always pass the event class
    :param dict in_event_cats: dict containing involved cats' abbreviations as keys and cat objects as values
    :param int i: index of the cat block
    :param list[str] attribute_list: attribute list contained within the block
    """

    thought = i18n.t("hardcoded.thought_new_cat")
    new_cats = None

    # gather parents
    parent1 = None
    parent2 = None
    adoptive_parents = []
    for tag in attribute_list:
        parent_match = re.match(r"parent:([,0-9]+)", tag)
        adoptive_match = re.match(r"adoptive:(.+)", tag)
        if not parent_match and not adoptive_match:
            continue

        parent_indexes = parent_match.group(1).split(",") if parent_match else []
        adoptive_indexes = adoptive_match.group(1).split(",") if adoptive_match else []
        if not parent_indexes and not adoptive_indexes:
            continue

        parent_indexes = [int(index) for index in parent_indexes]
        for index in parent_indexes:
            if index >= i:
                continue

            if parent1 is None:
                parent1 = event.new_cats[index][0]
            else:
                parent2 = event.new_cats[index][0]

        adoptive_indexes = [
            int(index) if index.isdigit() else index for index in adoptive_indexes
        ]
        for index in adoptive_indexes:
            if in_event_cats[index].ID not in adoptive_parents:
                adoptive_parents.append(in_event_cats[index].ID)
                adoptive_parents.extend(in_event_cats[index].mate)

    # gather mates
    give_mates = []
    for tag in attribute_list:
        match = re.match(r"mate:([_,0-9a-zA-Z]+)", tag)
        if not match:
            continue

        mate_indexes = match.group(1).split(",")

        # TODO: make this less ugly
        for index in mate_indexes:
            if index in in_event_cats:
                if in_event_cats[index].status.rank.is_any_apprentice_rank():
                    print("Can't give apprentices mates")
                    continue

                give_mates.append(in_event_cats[index])

    # determine gender
    if "male" in attribute_list:
        gender = "male"
    elif "female" in attribute_list:
        gender = "female"
    elif "can_birth" in attribute_list and not get_clan_setting("same sex birth"):
        gender = "female"
    else:
        gender = None

    # will the cat get a new name?
    if "new_name" in attribute_list:
        new_name = True
    elif "old_name" in attribute_list:
        new_name = False
    else:
        new_name = bool(getrandbits(1))

    # RANK - must be handled before backstories
    rank = None
    for _tag in attribute_list:
        match = re.match(r"status:(.+)", _tag)
        if not match:
            continue

        if match.group(1) in [
            CatRank.NEWBORN,
            CatRank.KITTEN,
            CatRank.ELDER,
            CatRank.APPRENTICE,
            CatRank.WARRIOR,
            CatRank.MEDIATOR_APPRENTICE,
            CatRank.MEDIATOR,
            CatRank.MEDICINE_APPRENTICE,
            CatRank.MEDICINE_CAT,
        ]:
            rank = match.group(1)
            break

    # SET AGE
    age = None
    for _tag in attribute_list:
        match = re.match(r"age:(.+)", _tag)
        if not match:
            continue

        if match.group(1) in Cat.age_moons:
            min_age, max_age = Cat.age_moons[CatAge(match.group(1))]
            age = randint(min_age, max_age)
            break

        # Set same as first mate
        if match.group(1) == "mate" and give_mates:
            min_age, max_age = Cat.age_moons[give_mates[0].age]
            age = randint(min_age, max_age)
            break

        if match.group(1) == "has_kits":
            age = randint(19, 120)
            break

    if rank and not age:
        if rank in [
            CatRank.APPRENTICE,
            CatRank.MEDIATOR_APPRENTICE,
            CatRank.MEDICINE_APPRENTICE,
        ]:
            age = randint(
                Cat.age_moons[CatAge.ADOLESCENT][0],
                Cat.age_moons[CatAge.ADOLESCENT][1],
            )
        elif rank in [CatRank.WARRIOR, CatRank.MEDIATOR, CatRank.MEDICINE_CAT]:
            age = randint(
                Cat.age_moons["young adult"][0], Cat.age_moons["senior adult"][1]
            )
        elif rank == CatRank.ELDER:
            age = randint(Cat.age_moons["senior"][0], Cat.age_moons["senior"][1])

    cat_group = None

    if "kittypet" in attribute_list:
        cat_social = CatSocial.KITTYPET
    elif "rogue" in attribute_list:
        cat_social = CatSocial.ROGUE
    elif "loner" in attribute_list:
        cat_social = CatSocial.LONER
    elif "clancat" in attribute_list or "former clancat" in attribute_list:
        cat_social = CatSocial.CLANCAT
        if "former clancat" in attribute_list:
            cat_social = "former clancat"
        if other_clan:
            cat_group = other_clan.group_ID
        else:
            cat_group = choice([x.group_ID for x in game.clan.all_other_clans])
    else:
        cat_social = choice([CatSocial.KITTYPET, CatSocial.LONER, "former clancat"])

    # LITTER
    litter = False
    if "litter" in attribute_list:
        litter = True
        if rank not in (CatRank.KITTEN, CatRank.NEWBORN):
            rank = CatRank.KITTEN

    # CHOOSE DEFAULT BACKSTORY BASED ON CAT TYPE, STATUS
    if rank in (CatRank.KITTEN, CatRank.NEWBORN):
        chosen_backstory = choice(
            BACKSTORIES["backstory_categories"]["abandoned_backstories"]
        )
    elif rank == CatRank.MEDICINE_CAT and cat_social == CatSocial.CLANCAT:
        chosen_backstory = choice(["medicine_cat", "disgraced1"])
    elif rank == CatRank.MEDICINE_CAT:
        chosen_backstory = choice(["wandering_healer1", "wandering_healer2"])
    else:
        if cat_social == CatSocial.CLANCAT:
            x = "former_clancat"
        else:
            x = cat_social
        chosen_backstory = choice(
            BACKSTORIES["backstory_categories"].get(f"{x}_backstories", ["outsider1"])
        )

    # OPTION TO OVERRIDE DEFAULT BACKSTORY
    bs_override = False
    stor = []
    for _tag in attribute_list:
        match = re.match(r"backstory:(.+)", _tag)
        if match:
            bs_list = [x for x in re.split(r", ?", match.group(1))]
            stor = []
            for story in bs_list:
                if story in set(
                    [
                        backstory
                        for backstory_block in BACKSTORIES[
                            "backstory_categories"
                        ].values()
                        for backstory in backstory_block
                    ]
                ):
                    stor.append(story)
                elif story in BACKSTORIES["backstory_categories"]:
                    stor.extend(BACKSTORIES["backstory_categories"][story])
            bs_override = True
            break
    if bs_override:
        chosen_backstory = choice(stor)
        if chosen_backstory in (
            BACKSTORIES["backstory_categories"]["baby_clancat_backstories"]
            + BACKSTORIES["backstory_categories"]["former_clancat_backstories"]
        ):
            cat_social = CatSocial.CLANCAT
        elif chosen_backstory in (
            BACKSTORIES["backstory_categories"]["baby_loner_backstories"]
            + BACKSTORIES["backstory_categories"]["loner_backstories"]
        ):
            cat_social = CatSocial.LONER
        elif chosen_backstory in (
            BACKSTORIES["backstory_categories"]["baby_kittypet_backstories"]
            + BACKSTORIES["backstory_categories"]["kittypet_backstories"]
        ):
            cat_social = CatSocial.KITTYPET
        elif (
            chosen_backstory in BACKSTORIES["backstory_categories"]["rogue_backstories"]
        ):
            cat_social = CatSocial.ROGUE

    # KITTEN THOUGHT
    if rank in (CatRank.KITTEN, CatRank.NEWBORN):
        thought = i18n.t("hardcoded.thought_new_kitten")

    # MEETING - DETERMINE IF THIS IS AN OUTSIDE CAT
    outside = False
    if "meeting" in attribute_list:
        outside = True
        rank = None
        new_name = False
        thought = i18n.t("hardcoded.thought_meeting")
        if age is not None and age <= 6 and not bs_override:
            chosen_backstory = "outsider1"

    # IS THE CAT DEAD?
    alive = True
    if "dead" in attribute_list:
        alive = False
        thought = i18n.t("hardcoded.thought_new_dead")

    # check if we can use an existing cat here
    chosen_cat: Optional["Cat"] = None
    if "exists" in attribute_list:
        existing_outsiders = [
            i for i in Cat.all_cats.values() if i.status.is_outsider and not i.dead
        ]
        possible_outsiders = []
        for cat in existing_outsiders:
            if stor and cat.backstory not in stor:
                continue
            if cat_social != cat.status.social or (
                cat_social == "former clancat" and not cat.status.is_former_clancat
            ):
                continue
            if gender and gender != cat.gender:
                continue
            if age and age not in Cat.age_moons[cat.age]:
                continue
            possible_outsiders.append(cat)

        if possible_outsiders:
            chosen_cat = choice(possible_outsiders)
            if not alive:
                chosen_cat.die()
            elif not outside:
                if not rank:
                    rank = chosen_cat.status.get_rank_from_age(chosen_cat.age)
                chosen_cat.add_to_clan()
                if chosen_cat.status.rank != rank:
                    chosen_cat.rank_change(new_rank=CatRank(rank), resort=True)
            elif outside:
                # updates so that the clan is marked as knowing of this cat
                current_standing = chosen_cat.status.get_standing_with_group(
                    CatGroup.PLAYER_CLAN_ID
                )
                if (
                    CatStanding.KNOWN not in current_standing
                    and CatStanding.EXILED not in current_standing
                ):
                    chosen_cat.status.change_standing(CatStanding.KNOWN)

            if new_name:
                name = f"{chosen_cat.name.prefix}"
                spaces = name.count(" ")
                if bool(getrandbits(1)):
                    if spaces > 0:  # adding suffix to OG name
                        # make a list of the words within the name, then add the OG name back in the list
                        words = name.split(" ")
                        words.append(name)
                        new_prefix = choice(words)  # pick new prefix from that list
                        name = new_prefix
                    chosen_cat.name.prefix = name
                    chosen_cat.name.give_suffix(
                        pelt=chosen_cat.pelt,
                        biome=game.clan.biome,
                        tortie_pattern=chosen_cat.pelt.tortie_pattern,
                    )
                else:  # completely new name
                    chosen_cat.name.give_prefix(
                        eyes=chosen_cat.pelt.eye_colour,
                        colour=chosen_cat.pelt.colour,
                        biome=game.clan.biome,
                    )
                    chosen_cat.name.give_suffix(
                        pelt=chosen_cat.pelt.colour,
                        biome=game.clan.biome,
                        tortie_pattern=chosen_cat.pelt.tortie_pattern,
                    )

            new_cats = [chosen_cat]

    # Now we generate the new cat
    if not chosen_cat:
        new_cats = create_new_cat(
            Cat,
            new_name=new_name,
            kit=False if litter else rank in (CatRank.KITTEN, CatRank.NEWBORN),
            # this is for singular kits, litters need this to be false
            litter=litter,
            backstory=chosen_backstory,
            rank=rank,
            original_social=cat_social,
            original_group=cat_group,
            moons=age,
            gender=gender,
            thought=thought,
            alive=alive,
            outside=outside,
            parent1=parent1.ID if parent1 else None,
            parent2=parent2.ID if parent2 else None,
            adoptive_parents=adoptive_parents if adoptive_parents else None,
        )

        # NEXT
        # add relations to bio parents, if needed
        # add relations to cats generated within the same block, as they are littermates
        # add mates
        # THIS DOES NOT ADD RELATIONS TO CATS IN THE EVENT, those are added within the relationships block of the event

        for n_c in new_cats:
            # SET MATES
            for inter_cat in give_mates:
                if n_c == inter_cat or n_c.ID in inter_cat.mate:
                    continue

                # this is some duplicate work, since this triggers inheritance re-calcs
                # TODO: optimize
                n_c.set_mate(inter_cat)

            # LITTERMATES
            for inter_cat in new_cats:
                if n_c == inter_cat:
                    continue

                y = randrange(0, 20)
                start_relation = Relationship(n_c, inter_cat, False, True)
                start_relation.like += 40 + y
                start_relation.comfort = 40 + y
                start_relation.respect = 10 + y
                start_relation.trust = 30 + y
                n_c.relationships[inter_cat.ID] = start_relation

            # BIO PARENTS
            for par in (parent1, parent2):
                if not par:
                    continue

                y = randrange(0, 20)
                start_relation = Relationship(par, n_c, False, True)
                start_relation.like += 60 + y
                start_relation.comfort = 40 + y
                start_relation.respect = 30 + y
                start_relation.trust = 30 + y
                par.relationships[n_c.ID] = start_relation

                y = randrange(0, 20)
                start_relation = Relationship(n_c, par, False, True)
                start_relation.like += 40 + y
                start_relation.comfort = 70 + y
                start_relation.respect = 30 + y
                start_relation.trust = 60 + y
                n_c.relationships[par.ID] = start_relation

            # ADOPTIVE PARENTS
            for par in adoptive_parents:
                if not par:
                    continue

                par = Cat.fetch_cat(par)

                y = randrange(0, 20)
                start_relation = Relationship(par, n_c, False, True)
                start_relation.like += 60 + y
                start_relation.comfort = 40 + y
                start_relation.respect = 30 + y
                start_relation.trust = 30 + y
                par.relationships[n_c.ID] = start_relation

                y = randrange(0, 20)
                start_relation = Relationship(n_c, par, False, True)
                start_relation.like += 40 + y
                start_relation.comfort = 70 + y
                start_relation.respect = 30 + y
                start_relation.trust = 60 + y
                n_c.relationships[par.ID] = start_relation

            # UPDATE INHERITANCE
            n_c.create_inheritance_new_cat()

    return new_cats


def get_other_clan(clan_name):
    """
    returns the clan object of given clan name
    """
    for clan in game.clan.all_other_clans:
        if clan.name == clan_name:
            return clan


def create_new_cat(
    Cat: Union["Cat", Type["Cat"]],
    new_name: bool = False,
    kit: bool = False,
    litter: bool = False,
    backstory: bool = None,
    rank: Optional[CatRank] = None,
    original_social: CatSocial = CatSocial.CLANCAT,
    original_group: CatGroup = None,
    moons: int = None,
    gender: str = None,
    thought: str = None,
    alive: bool = True,
    outside: bool = False,
    parent1: str = None,
    parent2: str = None,
    adoptive_parents: list = None,
) -> list:
    """
    This function creates new cats and then returns a list of those cats
    :param Cat Cat: pass the Cat class
    :params Relationship Relationship: pass the Relationship class
    :param bool new_name: set True if cat(s) is a loner/rogue receiving a new Clan name - default: False
    :param bool kit: set True if the cat is a lone kitten - default: False
    :param bool litter: set True if a litter of kittens needs to be generated - default: False
    :param bool backstory: a list of possible backstories.json for the new cat(s) - default: None
    :param rank: set as the rank you want the new cat to have - default: None (will cause a random status to be picked)
    :param original_social: set as the cat's old social - default: None (cat will not be given any past social, it will
    appear that they have always been a clancat)
    :param original_group: set as the cat's old group - default: None (cat will not be given any past group)
    :param bool outside: set this as True to generate the cat as an outsider instead of as part of the Clan - default: False (Clan cat)
    :param int moons: set the age of the new cat(s) - default: None (will be random or if kit/litter is true, will be kitten.
    :param str gender: set the gender (BIRTH SEX) of the cat - default: None (will be random)
    :param str thought: if you need to give a custom "welcome" thought, set it here
    :param bool alive: set this as False to generate the cat as already dead - default: True (alive)
    :param str parent1: Cat ID to set as the biological parent1
    :param str parent2: Cat ID to set as the biological parent2
    :param list adoptive_parents: Cat IDs to set as adoptive parents
    """

    if thought is None:
        thought = i18n.t("hardcoded.thought_new_cat")

    if isinstance(backstory, list):
        backstory = choice(backstory)

    if (
        backstory
        in (
            BACKSTORIES["backstory_categories"]["former_clancat_backstories"]
            + BACKSTORIES["backstory_categories"]["baby_clancat_backstories"]
        )
        or original_social == "former clancat"
    ) and not original_group:
        original_group = choice([x.group_ID for x in game.clan.all_other_clans])

    created_cats = []

    if not litter:
        number_of_cats = 1
    else:
        number_of_cats = choices([2, 3, 4, 5], [5, 4, 1, 1], k=1)[0]

    if not isinstance(moons, int):
        if rank == CatRank.NEWBORN:
            moons = 0
        elif litter or kit:
            moons = randint(1, 5)
        elif rank in (
            CatRank.APPRENTICE,
            CatRank.MEDICINE_APPRENTICE,
            CatRank.MEDIATOR_APPRENTICE,
        ):
            moons = randint(6, 11)
        elif rank == CatRank.WARRIOR:
            moons = randint(23, 120)
        elif rank == CatRank.MEDICINE_CAT:
            moons = randint(23, 140)
        elif rank == CatRank.ELDER:
            moons = randint(120, 130)
        else:
            moons = randint(6, 120)

    # setting rank
    if not rank and not outside:
        if moons == 0:
            rank = CatRank.NEWBORN
        elif moons < 6:
            rank = CatRank.KITTEN
        elif 6 <= moons <= 11:
            rank = CatRank.APPRENTICE
        elif moons >= 120:
            rank = CatRank.ELDER
        else:
            rank = CatRank.WARRIOR

    # need to get actual age enum
    age = CatAge.SENIOR
    for key_age in Cat.age_moons.keys():
        if moons in range(Cat.age_moons[key_age][0], Cat.age_moons[key_age][1] + 1):
            age: CatAge = key_age
            break

    # cat creation and naming time
    for index in range(number_of_cats):
        # setting gender
        if not gender:
            _gender = choice(["female", "male"])
        else:
            _gender = gender

        # first we generate the cat as though they are not part of the clan yet
        new_cat = Cat(
            moons=moons,
            status_dict={
                "social": original_social,
                "age": age,
                "group_ID": original_group,
            },
            gender=_gender,
            backstory=backstory,
            parent1=parent1,
            parent2=parent2,
            adoptive_parents=adoptive_parents if adoptive_parents else [],
        )
        # this simulates a "history" as whomever they used to be
        new_cat.status.change_current_moons_as(moons)

        if original_social == "former clancat":
            new_cat.status.become_lost(CatSocial.LONER)
        # now we actually add them to the clan, if they should be joining
        if not outside and alive:
            new_cat.add_to_clan()
            # check if cat is the correct rank
            if new_cat.status.rank != rank:
                new_cat.status._change_rank(CatRank(rank))
            # give apprentice aged cat a mentor
            if new_cat.status.rank.is_any_apprentice_rank():
                new_cat.update_mentor()
                # ensuring that any cats joining as an apprentice will display the correct skills
                new_cat.skills.primary.interest_only = True
                if new_cat.skills.secondary:
                    new_cat.skills.secondary.interest_only = True

        # NAMES and accs
        # clancat adults should have already generated with a clan-ish name, thus they skip all of this re-naming
        # little babies will take a clancat name, we love indoctrination
        if (
            kit or litter or moons < 12
        ) and original_group not in game.clan.other_clan_IDs:
            # babies change name, in case their initial name isn't clan-ish
            new_cat.change_name()
        elif original_group not in game.clan.other_clan_IDs:
            # give kittypets a kittypet name
            if original_social == CatSocial.KITTYPET:
                name = choice(names.names_dict["loner_names"])
                # check if the kittypets come with a pretty acc
                if bool(getrandbits(1)):
                    # TODO: refactor this entire function to remove this call amongst other things
                    from scripts.cat.pelts import Pelt

                    new_cat.pelt.accessory.append(choice(Pelt.collar_accessories))

            # try to give name from full loner name list
            elif original_social in (CatSocial.LONER, CatSocial.ROGUE) and bool(
                getrandbits(1)
            ):
                name = choice(names.names_dict["loner_names"])
            # otherwise give name from prefix list (more nature-y names)
            else:
                name = choice(names.names_dict["normal_prefixes"])

                # now, if this cat should take a new clan name, we give them such
            if new_name:
                # check if adding suffix to OG name
                if bool(getrandbits(1)):
                    spaces = name.count(" ")
                    if spaces > 0:
                        # make a list of the words within the name, then add the OG name back in the list
                        words = name.split(" ")
                        words.append(name)
                        new_prefix = choice(words)  # pick new prefix from that list
                        new_cat.change_name(new_prefix=new_prefix)
                # else, take a whole new name
                else:
                    new_cat.change_name()
            # else, let them keep their old name
            else:
                new_cat.change_name(new_prefix=name, new_suffix="")

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
        for scar in new_cat.pelt.scars:
            if scar in not_allowed:
                new_cat.pelt.scars.remove(scar)

        # chance to give the new cat a permanent condition, higher chance for found kits and litters
        if kit or litter:
            chance = int(
                constants.CONFIG["cat_generation"]["base_permanent_condition"] / 11.25
            )
        else:
            chance = constants.CONFIG["cat_generation"]["base_permanent_condition"] + 10
        if not int(random() * chance):
            possible_conditions = []
            for condition in PERMANENT:
                if (kit or litter) and PERMANENT[condition]["congenital"] not in [
                    "always",
                    "sometimes",
                ]:
                    continue
                # next part ensures that a kit won't get a condition that takes too long to reveal
                moons = new_cat.moons
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
                    new_cat.get_permanent_condition(chosen_condition, True)
                    if (
                        new_cat.permanent_condition[chosen_condition]["moons_until"]
                        == 0
                    ):
                        new_cat.permanent_condition[chosen_condition][
                            "moons_until"
                        ] = -2

                # assign scars
                if chosen_condition in ("lost a leg", "born without a leg"):
                    new_cat.pelt.scars.append("NOPAW")
                elif chosen_condition in ("lost their tail", "born without a tail"):
                    new_cat.pelt.scars.append("NOTAIL")

        # KILL >:D only if we're sposed to tho
        if not alive:
            new_cat.die()

        # newbie thought
        new_cat.thought = thought

        # and they exist now
        created_cats.append(new_cat)
        game.clan.add_cat(new_cat)
        new_cat.history.add_beginning()

        # create relationships
        new_cat.create_relationships_new_cat()
        # Note - we always update inheritance after the cats are generated, to
        # allow us to add parents.
        # new_cat.create_inheritance_new_cat()

    return created_cats


def gather_cat_objects(
    Cat, abbr_list: List[str], event, stat_cat=None, extra_cat=None
) -> list:
    """
    gathers cat objects from list of abbreviations used within an event format block
    :param Cat Cat: Cat class
    :param list[str] abbr_list: The list of abbreviations
    :param event: the controlling class of the event (e.g. Patrol, HandleShortEvents), default None
    :param Cat stat_cat: if passing the Patrol class, must include stat_cat separately
    :param Cat extra_cat: if not passing an event class, include the single affected cat object here. If you are not
    passing a full event class, then be aware that you can only include "m_c" as a cat abbreviation in your rel block.
    The other cat abbreviations will not work.
    :return: list of cat objects
    """

    clan_cats = [x for x in Cat.all_cats_list if x.status.alive_in_player_clan]
    out_set = set()

    for abbr in abbr_list:
        if abbr == "m_c":
            if extra_cat:
                out_set.add(extra_cat)
            else:
                out_set.add(event.main_cat)
        elif abbr == "r_c":
            out_set.add(event.random_cat)
        elif re.match(r"n_c:[0-9]+", abbr):
            index = re.match(r"n_c:([0-9]+)", abbr).group(1)
            index = int(index)
            if index < len(event.new_cats):
                out_set.update(event.new_cats[index])
        # PATROL SPECIFIC
        elif abbr == "p_l":
            out_set.add(event.patrol_leader)
        elif abbr == "s_c":
            out_set.add(stat_cat)
        elif abbr == "app1" and len(event.patrol_apprentices) >= 1:
            out_set.add(event.patrol_apprentices[0])
        elif abbr == "app2" and len(event.patrol_apprentices) >= 2:
            out_set.add(event.patrol_apprentices[1])
        elif abbr == "app3" and len(event.patrol_apprentices) >= 3:
            out_set.add(event.patrol_apprentices[2])
        elif abbr == "app4" and len(event.patrol_apprentices) >= 4:
            out_set.add(event.patrol_apprentices[3])
        elif abbr == "app5" and len(event.patrol_apprentices) >= 5:
            out_set.add(event.patrol_apprentices[4])
        elif abbr == "app6" and len(event.patrol_apprentices) >= 6:
            out_set.add(event.patrol_apprentices[5])
        elif abbr == "patrol":
            out_set.update(event.patrol_cats)
        elif abbr == "multi":
            cat_num = randint(1, max(1, len(event.patrol_cats) - 1))
            out_set.update(sample(event.patrol_cats, cat_num))
        # OVERALL CLAN CATS
        elif abbr == "clan":
            out_set.update(clan_cats)
        elif abbr == "some_clan":  # 1 / 8 of clan cats are affected
            out_set.update(
                sample(clan_cats, randint(1, max(1, round(len(clan_cats) / 8))))
            )
        # FACET CATS IN CLAN
        elif abbr == "high_social":
            out_set = {c for c in out_set if c.personality.sociability > 8}
        elif abbr == "low_social":
            out_set = {c for c in out_set if c.personality.sociability <= 8}
        elif abbr == "high_lawful":
            out_set = {c for c in out_set if c.personality.lawfulness > 8}
        elif abbr == "low_lawful":
            out_set = {c for c in out_set if c.personality.lawfulness <= 8}
        elif abbr == "high_stable":
            out_set = {c for c in out_set if c.personality.stability > 8}
        elif abbr == "low_stable":
            out_set = {c for c in out_set if c.personality.stability <= 8}
        elif abbr == "high_aggress":
            out_set = {c for c in out_set if c.personality.aggression > 8}
        elif abbr == "low_aggress":
            out_set = {c for c in out_set if c.personality.aggression <= 8}

        else:
            print(f"WARNING: Unsupported abbreviation {abbr}")

    return list(out_set)


def unpack_rel_block(
    Cat, relationship_effects: List[dict], event=None, stat_cat=None, extra_cat=None
):
    """
    Unpacks the info from the relationship effect block used in patrol and moon events, then adjusts rel values
    accordingly.

    :param Cat Cat: Cat class
    :param list[dict] relationship_effects: the relationship effect block
    :param event: the controlling class of the event (e.g. Patrol, HandleShortEvents), default None
    :param Cat stat_cat: if passing the Patrol class, must include stat_cat separately
    :param Cat extra_cat: if not passing an event class, include the single affected cat object here. If you are not passing a full event class, then be aware that you can only include "m_c" as a cat abbreviation in your rel block.  The other cat abbreviations will not work.
    """
    possible_values = [*RelType]

    for block in relationship_effects:
        cats_from = block.get("cats_from", [])
        cats_to = block.get("cats_to", [])
        amount = block.get("amount")
        values = [x for x in block.get("values", ()) if x in possible_values]

        # Gather actual cat objects:
        cats_from_ob = gather_cat_objects(Cat, cats_from, event, stat_cat, extra_cat)
        cats_to_ob = gather_cat_objects(Cat, cats_to, event, stat_cat, extra_cat)

        # Remove any "None" that might have snuck in
        if None in cats_from_ob:
            cats_from_ob.remove(None)
        if None in cats_to_ob:
            cats_to_ob.remove(None)

        positive = False

        # grabbing values
        value_changes = {}

        for val in [*RelType]:
            if val in values:
                value_changes[val] = amount
                if amount > 0:
                    positive = True

        if positive:
            effect = i18n.t("relationships.positive_postscript")
        else:
            effect = i18n.t("relationships.negative_postscript")

        # Get log
        to_log = None
        from_log = None
        if "log" in block:
            to_log = (
                block["log"].get("cats_to", "") + effect
                if "cats_to" in block["log"]
                else None
            )
            from_log = (
                block["log"].get("cats_from", "") + effect
                if "cats_from" in block["log"]
                else None
            )
            if not to_log and not from_log:
                print(f"something is wrong with relationship log: {block['log']}")

        change_relationship_values(
            cats_to_ob,
            cats_from_ob,
            **value_changes,
            log=from_log,
        )

        if block.get("mutual"):
            # we'll default to the other log if no unique log was written
            change_relationship_values(
                cats_from_ob,
                cats_to_ob,
                **value_changes,
                log=to_log if to_log else from_log,
            )


def change_relationship_values(
    cats_to: list,
    cats_from: list,
    romance: int = 0,
    like: int = 0,
    respect: int = 0,
    comfort: int = 0,
    trust: int = 0,
    log: str = None,
):
    """
    changes relationship values according to the parameters.

    :param list[Cat] cats_from: list of cat objects whose rel values will be affected
    (e.g. cat_from loses trust in cat_to)
    :param list[Cat] cats_to: list of cats objects who are the target of that rel value
    (e.g. cat_from loses trust in cat_to)
    :param int romance: amount to change romantic, default 0
    :param int like: amount to change platonic, default 0
    :param int respect: amount to change admiration (respect), default 0
    :param int comfort: amount to change comfort, default 0
    :param int trust: amount to change trust, default 0
    :param str log: the string to append to the relationship log of cats involved
    """

    # This is just for test prints - DON'T DELETE - you can use this to test if relationships are changing
    """changed = False
    if romance == 0 and like == 0 and respect == 0 and \
            comfort == 0 and trust == 0:
        changed = False
    else:
        changed = True"""

    # pick out the correct cats
    for single_cat_from in cats_from:
        for single_cat_to in cats_to:
            # make sure we aren't trying to change a cat's relationship with themself
            if single_cat_from == single_cat_to:
                continue

            # if the cats don't know each other, start a new relationship
            if single_cat_to.ID not in single_cat_from.relationships:
                single_cat_from.create_one_relationship(single_cat_to)

            rel = single_cat_from.relationships[single_cat_to.ID]

            # here we just double-check that the cats are allowed to be romantic with each other
            if (
                single_cat_from.is_potential_mate(single_cat_to, for_love_interest=True)
                or single_cat_to.ID in single_cat_from.mate
            ):
                # now gain the romance
                rel.romance += romance

            # gain other rel values
            rel.like += like
            rel.respect += respect
            rel.comfort += comfort
            rel.trust += trust

            # for testing purposes - DON'T DELETE - you can use this to test if relationships are changing
            """
            print(str(single_cat_from.name) + " gained relationship with " + str(rel.cat_to.name) + ": " +
                  "Romance: " + str(romance) +
                  " /Like: " + str(like) +
                  " /Respect: " + str(respect) +
                  " /Comfort: " + str(comfort) +
                  " /Trust: " + str(trust)) if changed else print("No relationship change")"""
            if not log:
                log = i18n.t("relationships.relationship_log")
            if log and isinstance(log, str):
                replace_dict = {}
                if "from_cat" in log:
                    replace_dict["from_cat"] = (
                        str(single_cat_from.name),
                        choice(single_cat_from.pronouns),
                    )
                if "to_cat" in log:
                    replace_dict["to_cat"] = (
                        str(single_cat_to.name),
                        choice(single_cat_to.pronouns),
                    )
                if replace_dict:
                    processed_log = process_text(log, replace_dict)
                else:
                    processed_log = log

                log_text = processed_log + i18n.t(
                    "relationships.age_postscript",
                    name=str(single_cat_to.name),
                    count=single_cat_to.moons,
                )
                if log_text not in rel.log:
                    rel.log.append(log_text)
