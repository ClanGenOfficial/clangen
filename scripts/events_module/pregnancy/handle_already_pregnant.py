from random import choices, choice, randint, random
from typing import Optional, Dict, List

import i18n

from scripts.cat.cats import Cat
from scripts.cat.enums import CatGroup, CatRank
from scripts.cat.names import Name
from scripts.cat_relations.relationship import Relationship
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.clan_package.settings import get_clan_setting
from scripts.cat.microservices.conditions import get_injured
from scripts.config import get_config
from scripts.events_module.event_information import EventInformation
from scripts.events_module.consequences import (
    check_stolen_vitality,
    change_relationship_values,
)
from scripts.events_module.pregnancy.build_strings import (
    get_pregnancy_strings,
    get_breakup_strings,
)
from scripts.events_module.pregnancy.check_family_size import set_biggest_family
from scripts.events_module.pregnancy.create_kits import get_kits, get_amount_of_kits
from scripts.events_module.text_adjust import event_text_adjust, process_text
from scripts.game_structure import game


def handle_one_moon_pregnant(cat: Cat):
    """Handles if the cat is one moon pregnant."""
    if cat.ID not in game.clan.pregnancy_data.keys():
        return

    # if the pregnant cat killed meanwhile, delete it from the dictionary
    if cat.dead:
        del game.clan.pregnancy_data[cat.ID]
        return

    amount = get_amount_of_kits(cat)

    # add the amount to the pregnancy dict
    game.clan.pregnancy_data[cat.ID]["amount"] = amount

    # if the cat is outside the clan, they won't guess how many kits they will have
    if cat.status.is_outsider:
        return

    thinking_amount = choices(["correct", "incorrect", "unsure"], [4, 1, 1], k=1)
    if amount <= 3:
        correct_guess = "small"
    else:
        correct_guess = "large"

    pregnancy_strings = get_pregnancy_strings()

    if thinking_amount[0] == "correct":
        if correct_guess == "small":
            text = choice(pregnancy_strings["litter_guess"]["small"])
        else:
            text = choice(pregnancy_strings["litter_guess"]["large"])
    elif thinking_amount[0] == "incorrect":
        if correct_guess == "small":
            text = choice(pregnancy_strings["litter_guess"]["large"])
        else:
            text = choice(pregnancy_strings["litter_guess"]["small"])
    else:
        text = choice(pregnancy_strings["litter_guess"]["unsure"])

    try:
        if cat.injuries["pregnant"]["severity"] == "minor":
            cat.injuries["pregnant"]["severity"] = "major"
            text += choice(pregnancy_strings["major_severity"])
    except KeyError:
        print("Is this an old save? Cat does not have the pregnant condition")

    text = event_text_adjust(Cat, text, main_cat=cat, clan=game.clan)
    game.cur_events_list.append(
        EventInformation(text, ["birth_death"], cat_dict={"m_c": cat})
    )


def handle_two_moon_pregnant(cat: Cat):
    """Handles if the cat is two moons pregnant."""
    if cat.ID not in game.clan.pregnancy_data.keys():
        return

    # if the pregnant cat is killed meanwhile, delete it from the dictionary
    if cat.dead:
        del game.clan.pregnancy_data[cat.ID]
        return

    kits_amount = game.clan.pregnancy_data[cat.ID]["amount"]
    if (
        kits_amount == 0
    ):  # safety check, sometimes pregnancies were ending up with 0 due to save rollbacks
        kits_amount = 1
    other_cat_id = game.clan.pregnancy_data[cat.ID]["second_parent"]
    other_cat = Cat.all_cats.get(other_cat_id)

    set_biggest_family()
    extra_naming_text = None

    adoptive_parents = []
    cheated_mate = None
    mate_claimed_kits = False
    secret_affair_birth = False
    affair_known = _get_affair_visibility_from_pregnancy(cat)

    if other_cat and cat.mate and other_cat.ID not in cat.mate:
        cheated_mate = _get_cheated_mate(cat)
        if cheated_mate:
            # if the mate at first didn't know they were cheated on,
            # there's a chance they will find out
            if not affair_known and randint(0, 1):
                secret_affair_birth = True
                adoptive_parents.append(cheated_mate.ID)
            else:
                # if they knew, they can still choose to help raise the kits or not
                mate_claimed_kits = _check_should_claim_affair_kits(cheated_mate, cat)
                if mate_claimed_kits:
                    adoptive_parents.append(cheated_mate.ID)
    kits = get_kits(kits_amount, cat, other_cat, adoptive_parents=adoptive_parents)
    kits_amount = len(kits)
    set_biggest_family()

    # delete the cat out of the pregnancy dictionary
    del game.clan.pregnancy_data[cat.ID]

    insert = i18n.t("conditions.pregnancy.kit_amount", count=kits_amount)

    # Since cat has given birth, apply the birth cooldown.
    cat.birth_cooldown = get_config("pregnancy.birth_cooldown")

    # choose event string
    # TODO: currently they don't choose which 'mate' is the 'blood' parent or not
    # change or leave as it is?
    events = get_pregnancy_strings()

    # GET MAIN EVENT
    (
        coparenting_outcome,
        other_cat_affair_known,
        involved_cats,
        cat_dict,
        event_list,
    ) = _handle_main_birth_event(cat, other_cat, events, secret_affair_birth)

    # the birthing cat's mate can choose to either help their cheating mate raise the new litter or
    # not be involved with their mate's kits at all
    if (
        cheated_mate
        and other_cat
        and other_cat.ID not in cat.mate
        and not secret_affair_birth
    ):
        if mate_claimed_kits:
            extra_text = i18n.t(
                "conditions.pregnancy.mate_claims_kits",
                insert=insert,
            )
        else:
            extra_text = i18n.t(
                "conditions.pregnancy.mate_disowns_kits",
                insert=insert,
            )
        extra_text = event_text_adjust(
            Cat,
            extra_text,
            main_cat=cat,
            random_cat=cheated_mate,
            clan=game.clan,
        )
        event_list.append(extra_text)

    # add naming choice for OUTSIDERS text here
    if cat.status.is_outsider:
        keep_clan_tradition = choice([True, False])
        for kit in kits:
            # should already match their parents, but just in case
            if not kit.status.is_outsider:
                kit.status.generate_new_status(
                    age=kit.age,
                    social=cat.status.social,
                    group_ID=cat.status.group_ID,
                )
            kit.backstory = "outsider1"

            if cat.status.is_exiled(CatGroup.PLAYER_CLAN_ID):
                name = choice(Name.names_dict["normal_prefixes"])
                kit.name = Name(prefix=name, suffix="", cat=kit)
                extra_naming_text = "conditions.pregnancy.reject_clan_tradition"

            if other_cat and not other_cat.status.is_outsider:
                kit.backstory = "outsider2"

            if cat.status.is_lost(CatGroup.PLAYER_CLAN_ID):
                kit.backstory = "outsider3"
                if not keep_clan_tradition:
                    name = choice(Name.names_dict["normal_prefixes"])
                    kit.name = Name(prefix=name, suffix="", cat=kit)
                    extra_naming_text = "conditions.pregnancy.reject_clan_tradition"
                else:
                    extra_naming_text = "conditions.pregnancy.keep_clan_tradition"
        if extra_naming_text:
            event_list.append(
                i18n.t(
                    extra_naming_text,
                    name=cat.name,
                )
            )

    involved_cats += [k.ID for k in kits]

    if game.clan.game_mode != "classic":
        try:
            death_chance = cat.injuries["pregnant"]["mortality"]
        except KeyError:
            death_chance = 40
    else:
        death_chance = 40

    if not int(random() * death_chance):  # chance for a cat to die during childbirth
        possible_events = events["birth"]["death"]
        # just makin sure meds aren't mentioned if they aren't around or if they are a parent
        meds = find_alive_cats_with_rank(
            Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE], sort=True
        )
        mate_is_med = [mate_id for mate_id in cat.mate if mate_id in meds]
        if not meds or cat in meds or len(mate_is_med) > 0:
            for event in possible_events:
                if CatRank.MEDICINE_CAT in event:
                    possible_events.remove(event)

        if cat.status.is_outsider:
            possible_events = events["birth"]["outside_death"]
        if game.clan.leader_lives > 1 and cat.status.is_leader:
            possible_events = events["birth"]["lead_death"]
        event_list.append(choice(possible_events))

        if cat.status.is_leader:
            game.clan.leader_lives -= 1
            cat.die()
            death_event = i18n.t("conditions.pregnancy.leader_kitting_death")
            if extra_result := check_stolen_vitality(cat, 1):
                death_event += " " + extra_result
        else:
            cat.die()
            death_event = i18n.t("conditions.pregnancy.kitting_death", name=cat.name)
        cat.history.add_death(death_text=death_event)
    elif not cat.status.is_outsider:  # if cat doesn't die, give recovering from birth
        get_injured(cat, "recovering from birth", event_triggered=True)
        if "blood loss" in cat.injuries:
            if cat.status.is_leader:
                death_event = i18n.t("conditions.pregnancy.leader_kitting_death_severe")
            else:
                death_event = i18n.t(
                    "conditions.pregnancy.kitting_death_harsh", name=cat.name
                )
            cat.history.add_possible_history("blood loss", death_text=death_event)
            possible_events = events["birth"]["difficult_birth"]
            # just makin sure meds aren't mentioned if they aren't around or if they are a parent
            meds = find_alive_cats_with_rank(
                Cat, [CatRank.MEDICINE_CAT, CatRank.MEDICINE_APPRENTICE]
            )
            mate_is_med = [mate_id for mate_id in cat.mate if mate_id in meds]
            if not meds or cat in meds or len(mate_is_med) > 0:
                for event in possible_events:
                    if CatRank.MEDICINE_CAT in event:
                        possible_events.remove(event)

            event_list.append(choice(possible_events))
    if not cat.dead:
        # If they are dead in childbirth above, all condition are cleared anyway.
        try:
            cat.injuries.pop("pregnant")
        except KeyError:
            print("Is this an old save? Your cat didn't have the pregnant condition!")
    print_event = " ".join(event_list)
    print_event = print_event.replace("{insert}", insert)

    # if the event doesn't mention mc/rc_mate, remove the cheated mate's ID from the event
    involved_cats = _remove_unmentioned_mate_ids(involved_cats, print_event, cat_dict)

    print_event = event_text_adjust(
        Cat, print_event, main_cat=cat, random_cat=other_cat, clan=game.clan
    )
    extra_cat_dict = {}
    if "mc_mate" in cat_dict:
        extra_cat_dict["mc_mate"] = (
            str(cat_dict["mc_mate"].name),
            choice(cat_dict["mc_mate"].pronouns),
        )
    if "rc_mate" in cat_dict:
        extra_cat_dict["rc_mate"] = (
            str(cat_dict["rc_mate"].name),
            choice(cat_dict["rc_mate"].pronouns),
        )
    if extra_cat_dict:
        print_event = process_text(print_event, extra_cat_dict)

    _handle_on_birth_relationship_changes(
        cat,
        other_cat,
        kits,
        coparenting_outcome,
        other_cat_affair_known,
        secret_affair_birth,
    )

    # display event
    game.cur_events_list.append(
        EventInformation(
            print_event, ["health", "birth_death"], involved_cats, cat_dict=cat_dict
        )
    )

    # chance to break up the cat and their mate
    # if the mate doesn't want to anything to do with the affair litter
    if cheated_mate and not mate_claimed_kits and not secret_affair_birth:
        _handle_affair_discovery_breakup(cat, cheated_mate)

        if other_cat and other_cat.mate:
            other_cat_mate = None
            for mate_id in other_cat.mate:
                if mate_id != cat.ID:
                    other_cat_mate = Cat.fetch_cat(mate_id)
                    if other_cat_mate and not other_cat_mate.dead:
                        break
                    other_cat_mate = None
            # break up the other cat and their mate
            if other_cat_mate and other_cat_affair_known:
                _handle_affair_discovery_breakup(other_cat, other_cat_mate)


def _get_affair_visibility_from_pregnancy(
    cat: Optional[Cat] = None, pregnant_cat: Optional[Cat] = None
) -> Optional[bool]:
    """Read whether an affair was explicitly announced from pregnancy data."""
    target_cat = cat or pregnant_cat
    if not target_cat or not game.clan:
        return None
    pregnancy = game.clan.pregnancy_data.get(target_cat.ID)
    if pregnancy is None:
        return None
    return pregnancy.get("affair_known")


def _get_cheated_mate(subject_cat: Cat, include_dead: bool = False):
    """Gets cheating cat's mate for the events"""
    for mate_id in subject_cat.mate:
        mate = Cat.fetch_cat(mate_id)
        if not mate:
            continue
        if include_dead and mate.dead:
            return mate
        if not include_dead and not mate.dead:
            return mate
    return None


def _check_should_claim_affair_kits(mate: Cat, pregnant_cat: Cat) -> bool:
    """Determines if the mate chooses to claim kits after an affair birth."""
    if not mate or mate.dead:
        return False
    rel = mate.relationships.get(pregnant_cat.ID)
    romance = rel.romance if rel else 0
    claim_chance = get_config("pregnancy.base_claim_kit_chance")
    if romance >= 85:
        claim_chance += 40
    elif romance >= 65:
        claim_chance += 20
    elif romance >= 45:
        # this value just stays the base chance
        claim_chance = claim_chance
    elif romance >= 25:
        claim_chance -= 20
    else:
        claim_chance -= 30

    # capping values higher than 100 and lower than 0
    claim_chance = max(0, min(claim_chance, 100))

    return randint(1, 100) <= claim_chance


def _handle_main_birth_event(
    cat, other_cat, events, secret_affair_birth
) -> tuple[str, bool, list, dict, list]:
    other_cat_affair_known = False
    coparenting_outcome = None
    involved_cats = [cat.ID]
    cat_dict = {"m_c": cat}
    event_list = []

    # SINGLE PARENT
    if not cat.status.is_outsider and other_cat is None:
        event_list.append(choice(events["birth"]["unmated_parent"]))

    # OUTSIDER
    elif cat.status.is_outsider:
        adding_text = choice(events["birth"]["outside_alone"])
        if cat.status.is_lost(CatGroup.PLAYER_CLAN):
            adding_text = choice(events["birth"]["outside_lost"])
        if other_cat and not other_cat.status.is_outsider:
            adding_text = choice(events["birth"]["outside_in_clan"])
        event_list.append(adding_text)

    # TWO PARENTS
    elif other_cat.ID in cat.mate and other_cat.status.alive_in_player_clan:
        involved_cats.append(other_cat.ID)
        cat_dict["r_c"] = other_cat
        event_list.append(choice(events["birth"]["two_parents"]))

    # DEAD MATE
    elif other_cat.ID in cat.mate and other_cat.dead:
        involved_cats.append(other_cat.ID)
        cat_dict["r_c"] = other_cat
        event_list.append(choice(events["birth"]["dead_mate"]))

    # OUTSIDER MATE
    elif other_cat.ID in cat.mate and other_cat.status.is_outsider:
        involved_cats.append(other_cat.ID)
        cat_dict["r_c"] = other_cat
        event_list.append(choice(events["birth"]["outside_mate"]))

    # UNMATED
    elif len(cat.mate) < 1 and len(other_cat.mate) < 1 and not other_cat.dead:
        involved_cats.append(other_cat.ID)
        cat_dict["r_c"] = other_cat
        # 50% chance for the parents to be positive or negative towards co-parenting
        if randint(0, 1):
            coparenting_outcome = "positive"
            event_list.append(choice(events["birth"]["both_unmated_pos"]))
        else:
            coparenting_outcome = "negative"
            event_list.append(choice(events["birth"]["both_unmated_neg"]))

    # SAME-SEX RELATIONSHIP AFFAIR
    elif (
        not get_clan_setting("same sex birth")
        and any(
            Cat.fetch_cat(mate_id) and Cat.fetch_cat(mate_id).gender == "female"
            for mate_id in cat.mate
        )
        and other_cat.ID not in cat.mate
    ):
        involved_cats.append(other_cat.ID)
        cat_dict["r_c"] = other_cat
        chosen_mate = _get_cheated_mate(cat)
        if chosen_mate:
            cat_dict["mc_mate"] = chosen_mate
            involved_cats.append(chosen_mate.ID)
        event_list.append(choice(events["birth"]["affair_mated_samesex"]))

    # MAIN CAT CHEATED ON MATE
    elif len(cat.mate) > 0 and other_cat.ID not in cat.mate and not other_cat.dead:
        living_mate = _get_cheated_mate(cat)
        dead_mate = _get_cheated_mate(cat, include_dead=True)
        involved_cats.append(other_cat.ID)
        cat_dict["r_c"] = other_cat
        if living_mate:
            cat_dict["mc_mate"] = living_mate
            involved_cats.append(living_mate.ID)
            if secret_affair_birth:
                event_list.append(choice(events["birth"]["affair_mated_secret"]))
            else:
                event_list.append(choice(events["birth"]["affair_mated"]))
        # including the dead mate version
        # because of a bug where the game can't find any birthing events
        # if the cheated mate is dead
        else:
            cat_dict["mc_mate"] = dead_mate
            involved_cats.append(dead_mate.ID)
            event_list.append(choice(events["birth"]["affair_mated_dead_mate"]))

    # OTHER CAT CHEATED ON MATE
    elif (
        len(other_cat.mate) > 0 and cat.ID not in other_cat.mate and not other_cat.dead
    ):
        other_mate = _get_cheated_mate(other_cat)
        if other_mate:
            # determine if the other_cat's mate is aware of their mate
            # cheating on them
            other_cat_affair_known = bool(randint(0, 1))
            involved_cats.append(other_cat.ID)
            cat_dict["r_c"] = other_cat
            cat_dict["rc_mate"] = other_mate
            involved_cats.append(other_mate.ID)
            if other_cat_affair_known:
                event_list.append(choice(events["birth"]["affair"]))
            else:
                event_list.append(choice(events["birth"]["affair_secret"]))
        # just in case if the other cat's mate is dead
        else:
            involved_cats.append(other_cat.ID)
            cat_dict["r_c"] = other_cat
            event_list.append(choice(events["birth"]["both_unmated_pos"]))
    else:
        event_list.append(choice(events["birth"]["unmated_parent"]))
    return (
        coparenting_outcome,
        other_cat_affair_known,
        involved_cats,
        cat_dict,
        event_list,
    )


def _remove_unmentioned_mate_ids(
    involved_cats: List[str], event_text: str, cat_dict: Dict
) -> List[str]:
    """Removes the cheated mate's ID if mc/rc_mate isn't present in the affair birth event text."""
    for placeholder in ("mc_mate", "rc_mate"):
        cat = cat_dict.get(placeholder)
        if cat and placeholder not in event_text and cat.ID in involved_cats:
            involved_cats.remove(cat.ID)
    return involved_cats


def _handle_on_birth_relationship_changes(
    cat,
    other_cat,
    kits,
    coparenting_outcome,
    other_cat_affair_known,
    secret_affair_birth,
):
    # relationship changes for affair births
    # this outcome here happens if the birthing cat cheated on their mate
    # here, the cheated mate loses relationship to the birthing cat
    if (
        other_cat
        and cat.mate
        and other_cat.ID not in cat.mate
        and not secret_affair_birth
    ):
        for mate_id in cat.mate:
            mate = Cat.fetch_cat(mate_id)
            if not mate:
                continue

            breakup_reaction = get_config(
                "mates.breakup.reactions.affair_discovery_mate_reaction"
            )
            log_text = process_text(
                i18n.t("conditions.pregnancy.affair_rel_log"),
                {
                    "m_c": (str(mate.name), choice(mate.pronouns)),
                    "r_c": (str(cat.name), choice(cat.pronouns)),
                },
            )
            log_text = i18n.t("relationships.negative_postscript", text=log_text)
            change_relationship_values(
                cats_to=[cat], cats_from=[mate], log=log_text, **breakup_reaction
            )

    # if the other cat had a mate, their mate also lose relationship with them
    if (
        other_cat
        and other_cat.mate
        and cat.ID not in other_cat.mate
        and other_cat_affair_known
    ):
        for mate_id in other_cat.mate:
            mate = Cat.fetch_cat(mate_id)
            if not mate:
                continue

            breakup_reaction = get_config(
                "mates.breakup.reactions.affair_discovery_other_mate_reaction"
            )
            log_text = process_text(
                i18n.t("conditions.pregnancy.affair_rel_log"),
                {
                    "m_c": (str(mate.name), choice(mate.pronouns)),
                    "r_c": (str(other_cat.name), choice(other_cat.pronouns)),
                },
            )
            log_text = i18n.t("relationships.negative_postscript", text=log_text)
            change_relationship_values(
                cats_to=[other_cat],
                cats_from=[mate],
                log=log_text,
                **breakup_reaction,
            )
    # relationship changes for unmated co-parenting births
    if (
        other_cat
        and not cat.mate
        and not other_cat.mate
        and not other_cat.dead
        and coparenting_outcome
    ):
        if coparenting_outcome == "negative":
            absent_parent_to_kit_reaction = get_config(
                "new_cat.parent_buff.absent_parent_to_kit"
            )
            for kit in kits:
                absent_parent_to_kit = Relationship(other_cat, kit, family=True)
                other_cat.relationships[kit.ID] = absent_parent_to_kit
                absent_parent_to_kit.like += absent_parent_to_kit_reaction["like"]
                absent_parent_to_kit.respect += absent_parent_to_kit_reaction["respect"]
                absent_parent_to_kit.comfort += absent_parent_to_kit_reaction["comfort"]
                absent_parent_to_kit.trust += absent_parent_to_kit_reaction["trust"]
                kit_to_absent_parent = Relationship(kit, other_cat, family=True)
                kit.relationships[other_cat.ID] = kit_to_absent_parent
                absent_parent_to_kit.opposite_relationship = kit_to_absent_parent
                kit_to_absent_parent.opposite_relationship = absent_parent_to_kit

        for first_cat, second_cat in ((cat, other_cat), (other_cat, cat)):
            rel = first_cat.relationships.get(second_cat.ID)
            if not rel:
                rel = Relationship(first_cat, second_cat)
                first_cat.relationships[second_cat.ID] = rel

            coparenting_values_neg = get_config("pregnancy.coparenting_values_neg")
            coparenting_values_pos = get_config("pregnancy.coparenting_values_pos")

            if coparenting_outcome == "negative":
                log_text = process_text(
                    i18n.t("conditions.pregnancy.coparenting_rel_log_neg"),
                    {
                        "m_c": (str(first_cat.name), choice(first_cat.pronouns)),
                        "r_c": (str(second_cat.name), choice(second_cat.pronouns)),
                    },
                )
                log_text = i18n.t("relationships.negative_postscript", text=log_text)
                change_relationship_values(
                    cats_to=[second_cat],
                    cats_from=[first_cat],
                    log=log_text,
                    **coparenting_values_neg,
                )
            elif coparenting_outcome == "positive":
                log_text = process_text(
                    i18n.t("conditions.pregnancy.coparenting_rel_log_pos"),
                    {
                        "m_c": (str(first_cat.name), choice(first_cat.pronouns)),
                        "r_c": (str(second_cat.name), choice(second_cat.pronouns)),
                    },
                )
                log_text = i18n.t("relationships.positive_postscript", text=log_text)
                change_relationship_values(
                    cats_to=[second_cat],
                    cats_from=[first_cat],
                    log=log_text,
                    **coparenting_values_pos,
                )


def _handle_affair_discovery_breakup(cheating_cat: Cat, mate_cat: Cat):
    """Handles a chance for a breakup event after an affair is discovered."""
    if not cheating_cat or not mate_cat:
        return
    if cheating_cat.ID not in mate_cat.mate:
        return

    breakup_chance = get_config("mates.breakup.affair_breakup_chance")
    if random() <= breakup_chance:
        mate_cat.unset_mate(cheating_cat, user_initiated_breakup=True, fight=True)
        breakup_text = choice(get_breakup_strings()["affair_discovery_breakup"])
        breakup_text = event_text_adjust(
            Cat,
            breakup_text,
            main_cat=mate_cat,
            random_cat=cheating_cat,
            clan=game.clan,
        )
        game.cur_events_list.append(
            EventInformation(
                breakup_text,
                ["relation", "misc"],
                [mate_cat.ID, cheating_cat.ID],
                cat_dict={"m_c": mate_cat, "r_c": cheating_cat},
            )
        )
