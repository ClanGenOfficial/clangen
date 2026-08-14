import random
from random import choice, randint
from typing import Dict, List, Union, Optional

import i18n
import math

from scripts.cat.cats import Cat
from scripts.cat.enums import (
    CatAge,
    CatGroup,
    CatRank,
    CatSocial,
    CatCompatibility,
    CatThought,
)
from scripts.cat.factories.enums import CatType
from scripts.cat.factories.new_cat_factory import NewCatFactory
from scripts.cat.names import names, Name
from scripts.cat.factories.typed_dicts import StatusDict
from scripts.cat_relations.relationship import Relationship, RelType
from scripts.cat_relations.inheritance2 import inheritance_db
from scripts.clan_package.settings import get_clan_setting
from scripts.event_class import Single_Event
from scripts.events_module.short.condition_events import Condition_Events
from scripts.game_structure import constants
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource
from scripts.events_module.text_adjust import (
    event_text_adjust,
    adjust_list_text,
    process_text,
)
from scripts.events_module.consequences import (
    create_new_cat,
    change_relationship_values,
    check_stolen_vitality,
)
from scripts.events_module.event_filters import (
    get_highest_romantic_relation,
    get_personality_compatibility,
)
from scripts.clan_package.get_clan_cats import find_alive_cats_with_rank
from scripts.config import get_config


class Pregnancy_Events:
    """All events which are related to pregnancy such as kitting and defining who are the parents."""

    biggest_family = {}
    PREGNANT_STRINGS: Optional[Dict[str, Union[List, Dict[str, List]]]] = {}
    NEWBORN_REL_REACTIONS: Dict = {}
    BREAKUP_STRINGS: Dict = {}
    currently_loaded_lang: str = None

    @staticmethod
    def rebuild_strings():
        if Pregnancy_Events.currently_loaded_lang == i18n.config.get("locale"):
            return
        Pregnancy_Events.PREGNANT_STRINGS = load_lang_resource(
            "conditions/pregnancy.json"
        )

        Pregnancy_Events.NEWBORN_REL_REACTIONS = load_lang_resource(
            "events/relationship_events/newborn_relative_logs.json"
        )

        Pregnancy_Events.BREAKUP_STRINGS = load_lang_resource(
            "events/relationship_events/breakup_mates.json"
        )

        Pregnancy_Events.currently_loaded_lang = i18n.config.get("locale")

    @staticmethod
    def _append_second_parent_if_mentioned(
        involved_cats: List[str], event_text: str, mentioned_cat: Optional[Cat]
    ) -> List[str]:
        """
        Appends the second parent/mate ID only if the event text mentions r_c.
        :param involved_cats: the cats involved in the invent, usually the first and second parent

        :return: involved_cats dict with mentioned_cat included if needed
        """
        if (
            mentioned_cat
            and "r_c" in event_text
            and mentioned_cat.ID not in involved_cats
        ):
            involved_cats.append(mentioned_cat.ID)
        return involved_cats

    @staticmethod
    def remove_unmentioned_mate_ids(
        involved_cats: List[str], event_text: str, cat_dict: Dict
    ) -> List[str]:
        """Removes the cheated mate's ID if mc/rc_mate isn't present in the affair birth event text."""
        for placeholder in ("mc_mate", "rc_mate"):
            cat = cat_dict.get(placeholder)
            if cat and placeholder not in event_text and cat.ID in involved_cats:
                involved_cats.remove(cat.ID)
        return involved_cats

    @staticmethod
    def get_cheated_mate(subject_cat: Cat, include_dead: bool = False):
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

    @staticmethod
    def should_claim_affair_kits(mate: Cat, pregnant_cat: Cat) -> bool:
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

        return random.randint(1, 100) <= claim_chance

    @staticmethod
    def handle_affair_discovery_breakup(cheating_cat: Cat, mate_cat: Cat):
        """Handles a chance for a breakup event after an affair is discovered."""
        if not cheating_cat or not mate_cat:
            return
        if cheating_cat.ID not in mate_cat.mate:
            return

        breakup_chance = get_config("mates.mates_breakup.affair_breakup_chance")
        if random.random() <= breakup_chance:
            mate_cat.unset_mate(cheating_cat, breakup=True, fight=True)
            breakup_text = choice(
                Pregnancy_Events.BREAKUP_STRINGS["affair_discovery_breakup"]
            )
            breakup_text = event_text_adjust(
                Cat,
                breakup_text,
                main_cat=mate_cat,
                random_cat=cheating_cat,
                clan=game.clan,
            )
            game.cur_events_list.append(
                Single_Event(
                    breakup_text,
                    ["relation", "misc"],
                    [mate_cat.ID, cheating_cat.ID],
                    cat_dict={"m_c": mate_cat, "r_c": cheating_cat},
                )
            )

    @staticmethod
    def set_affair_visibility_on_pregnancy(
        cat: Optional[Cat] = False,
        is_affair_known: Optional[bool] = False,
        pregnant_cat: Optional[Cat] = False,
    ):
        """Store whether an affair was explicitly announced in pregnancy data."""
        target_cat = cat or pregnant_cat
        if not target_cat or not game.clan:
            return
        pregnancy = game.clan.pregnancy_data.get(target_cat.ID)
        if pregnancy is None:
            return
        pregnancy["affair_known"] = is_affair_known

    @staticmethod
    def get_affair_visibility_from_pregnancy(
        cat: Optional[Cat] = None, pregnant_cat: Optional[Cat] = None, clan=game.clan
    ) -> Optional[bool]:
        """Read whether an affair was explicitly announced from pregnancy data."""
        target_cat = cat or pregnant_cat
        if not target_cat or not clan:
            return None
        pregnancy = clan.pregnancy_data.get(target_cat.ID)
        if pregnancy is None:
            return None
        return pregnancy.get("affair_known")

    @staticmethod
    def create_pregnancy_data(
        pregnant_cat: Cat, second_parent: Optional[Cat], clan=game.clan
    ):
        """Creates the pregnancy data entry for a new pregnancy."""
        clan.pregnancy_data[pregnant_cat.ID] = {
            "second_parent": str(second_parent.ID) if second_parent else None,
            "moons": 0,
            "amount": 0,
        }

    @staticmethod
    def create_pregnancy_announcement(
        pregnant_cat: Cat,
        announcement_key: str,
        random_cat: Optional[Cat] = None,
        mentioned_cat: Optional[Cat] = None,
    ):
        """Creates announcement text, applies pregnancy injury, and returns involved cats."""
        text = choice(Pregnancy_Events.PREGNANT_STRINGS[announcement_key])
        event_text = text
        severity = random.choices(["minor", "major"], [3, 1], k=1)[0]
        pregnant_cat.get_injured("pregnant", severity=severity)
        text += choice(Pregnancy_Events.PREGNANT_STRINGS[f"{severity}_severity"])
        text = event_text_adjust(
            Cat,
            text,
            main_cat=pregnant_cat,
            random_cat=random_cat,
            clan=game.clan,
        )
        involved_cats = [pregnant_cat.ID]
        involved_cats = Pregnancy_Events._append_second_parent_if_mentioned(
            involved_cats, event_text, mentioned_cat or random_cat
        )
        return text, involved_cats

    @staticmethod
    def set_biggest_family():
        """Gets the biggest family of the clan."""
        biggest_family = None
        for cat in Cat.all_cats.values():
            ancestors = list(cat.get_relatives())
            if not biggest_family:
                biggest_family = ancestors
                biggest_family.append(cat.ID)
            elif len(biggest_family) < len(ancestors) + 1:
                biggest_family = ancestors
                biggest_family.append(cat.ID)
        Pregnancy_Events.biggest_family = biggest_family

    @staticmethod
    def biggest_family_is_big():
        """Returns if the current biggest family is big enough to 'activates' additional inbreeding counters."""

        living_cats = len(
            [i for i in Cat.all_cats.values() if i.status.alive_in_player_clan]
        )
        return len(Pregnancy_Events.biggest_family) > (living_cats / 10)

    @staticmethod
    def handle_pregnancy_age(clan):
        """Increase the moon for each pregnancy in the pregnancy dictionary"""
        for pregnancy_key in clan.pregnancy_data.keys():
            clan.pregnancy_data[pregnancy_key]["moons"] += 1

    @staticmethod
    def handle_having_kits(cat, clan):
        """Handles pregnancy of a cat."""
        if not clan:
            return

        if not Pregnancy_Events.biggest_family:
            Pregnancy_Events.set_biggest_family()

        # Handles if a cat is already pregnant
        if cat.ID in clan.pregnancy_data:
            moons = clan.pregnancy_data[cat.ID]["moons"]
            if moons == 1:
                Pregnancy_Events.handle_one_moon_pregnant(cat, clan)
                return
            if moons >= 2:
                Pregnancy_Events.handle_two_moon_pregnant(cat, clan)
                # events.ceremony_accessory = True
                return

        if not cat.status.alive_in_player_clan or cat.not_working():
            return

        # Handle birth cooldown outside the check_if_can_have_kits function, so it only happens once
        # for each cat.
        if cat.birth_cooldown > 0:
            cat.birth_cooldown -= 1

        # Check if they can have kits.
        can_have_kits = Pregnancy_Events.check_if_can_have_kits(
            cat,
            get_clan_setting("single parentage"),
            get_clan_setting("unmated parentage"),
            get_clan_setting("affair"),
        )
        if not can_have_kits:
            return

        # DETERMINE THE SECOND PARENT
        # check if there is a cat in the clan for the second parent
        second_parent, is_affair = Pregnancy_Events.get_second_parent(cat)

        # check if the second_parent is not none and if they also can have kits
        can_have_kits, kits_are_adopted = Pregnancy_Events.check_second_parent(
            cat,
            second_parent,
            get_clan_setting("single parentage"),
            get_clan_setting("unmated parentage"),
            get_clan_setting("affair"),
            get_clan_setting("same sex birth"),
            get_clan_setting("same sex adoption"),
        )
        if second_parent:
            if not can_have_kits:
                return
        else:
            if not get_clan_setting("single parentage"):
                return

        chance = Pregnancy_Events.get_balanced_kit_chance(
            cat, second_parent, is_affair, clan
        )

        if not int(random.random() * chance):
            # If you've reached here - congrats, kits!
            if kits_are_adopted:
                Pregnancy_Events.handle_adoption(cat, second_parent, clan)
            else:
                Pregnancy_Events.handle_zero_moon_pregnant(cat, second_parent, clan)

    # ---------------------------------------------------------------------------- #
    #                                 handle events                                #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def handle_adoption(cat: Cat, other_cat=None, clan=game.clan):
        """Handle if the there is no pregnancy but the pair triggered kits chance."""
        if other_cat and (
            not other_cat.status.alive_in_player_clan or other_cat.birth_cooldown > 0
        ):
            return

        if cat.ID in clan.pregnancy_data:
            return

        if other_cat and other_cat.ID in clan.pregnancy_data:
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

        amount = Pregnancy_Events.get_amount_of_kits(cat)
        kits = Pregnancy_Events.get_kits(
            amount, None, None, game.clan, adoptive_parents=adoptive_parents
        )

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
        cat.get_new_thought(CatThought.ON_BIRTH)
        if other_cat:
            cats_involved["r_c"] = other_cat
            other_cat.get_new_thought(CatThought.ON_BIRTH)

        for kit in kits:
            kit.get_new_thought()

        # Normally, birth cooldown is only applied to cat who gave birth
        # However, if we don't apply birth cooldown to adoption, we get
        # too much adoption, since adoptive couples are using the increased two-parent
        # kits chance. We will only apply it to "cat" in this case
        # which is enough to stop the couple from adopting about within
        # the window.
        cat.birth_cooldown = get_config("pregnancy.birth_cooldown")

        game.cur_events_list.append(
            Single_Event(print_event, "birth_death", cat_dict=cats_involved)
        )

    @staticmethod
    def handle_zero_moon_pregnant(cat: Cat, other_cat=None, clan=game.clan):
        """Handles if the cat is zero moons pregnant."""
        if other_cat and (
            not other_cat.status.alive_in_player_clan or other_cat.birth_cooldown > 0
        ):
            return

        if cat.ID in clan.pregnancy_data:
            return

        if other_cat and other_cat.ID in clan.pregnancy_data:
            return

        # additional save for no kit setting
        if (cat and cat.no_kits) or (other_cat and other_cat.no_kits):
            return

        Pregnancy_Events.rebuild_strings()
        allow_affair = get_clan_setting("affair")
        allow_coparenting = get_clan_setting("unmated parentage")

        if get_clan_setting("same sex birth"):
            # 50/50 for single cats to get pregnant or just bring a litter back
            if not other_cat and random.randint(0, 1):
                amount = Pregnancy_Events.get_amount_of_kits(cat)
                kits = Pregnancy_Events.get_kits(amount, cat, None, clan)
                print_event = i18n.t(
                    "conditions.pregnancy.pregnant_secret",
                    name=cat.name,
                    insert=i18n.t("conditions.pregnancy.kit_amount", count=amount),
                )
                cats_involved = [cat.ID]
                cat_dict = {"m_c": cat}
                for kit in kits:
                    cats_involved.append(kit.ID)
                game.cur_events_list.append(
                    Single_Event(
                        print_event, "birth_death", cats_involved, cat_dict=cat_dict
                    )
                )
                return

            # same sex birth enables all cats to get pregnant,
            # therefore the main cat will be used, regarding of gender
            Pregnancy_Events.create_pregnancy_data(cat, other_cat, clan)
            mate = [
                Cat.fetch_cat(mate_id) for mate_id in cat.mate if Cat.fetch_cat(mate_id)
            ]
            if not mate:
                mate = None
            # if both cats are faithful to each other and aren't cheaters,
            # the pregnancy will be announced as normal
            if other_cat and other_cat.ID in cat.mate:
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    cat, "announcement", random_cat=other_cat
                )
            # if the pregnant cat is single and had a fling with a random cat, let them
            # announce their surprise pregnancy and leave the Clan and player pointing
            # fingers on who the second parent may be
            elif allow_coparenting and not mate:
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    cat, "announcement_surprise"
                )

            # and lastly, if the pregnant cat got knocked up by another cat who ISN'T their mate,
            # let the player guess whether it's an affair or not, sometimes the events will tell you,
            # sometimes they won't...
            elif (
                allow_affair is True
                and other_cat
                and other_cat.ID not in cat.mate
                and mate
            ):
                announcement_key = choice(["announcement_affair", "announcement"])
                Pregnancy_Events.set_affair_visibility_on_pregnancy(
                    cat, announcement_key == "announcement_affair"
                )
                random_cat = mate[0]
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    cat, announcement_key, random_cat=random_cat
                )
            # if all else fails, just a regular announcement happens
            else:
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    cat, "announcement", random_cat=other_cat
                )
            game.cur_events_list.append(
                Single_Event(text, "birth_death", involved_cats)
            )
        else:
            if not other_cat and cat.gender == "male":
                amount = Pregnancy_Events.get_amount_of_kits(cat)
                kits = Pregnancy_Events.get_kits(amount, cat, None, clan)
                print_event = i18n.t(
                    "conditions.pregnancy.pregnant_secret",
                    name=cat.name,
                    insert=i18n.t("conditions.pregnancy.kit_amount", count=amount),
                )
                cats_involved = [cat.ID]
                for kit in kits:
                    cats_involved.append(kit.ID)
                game.cur_events_list.append(
                    Single_Event(
                        print_event, "birth_death", cats_involved, cat_dict={"m_c": cat}
                    )
                )
                return

            # if the other cat is afab and the current cat is amab, make the afab cat pregnant
            pregnant_cat = cat
            second_parent = other_cat
            if (
                cat.gender == "male"
                and other_cat is not None
                and other_cat.gender == "female"
            ):
                pregnant_cat = other_cat
                second_parent = cat

            Pregnancy_Events.create_pregnancy_data(pregnant_cat, second_parent, clan)
            mate = []
            afab_mate = []
            amab_mate = []
            for mate_id in pregnant_cat.mate:
                mate_cat = Cat.fetch_cat(mate_id)
                mate.append(mate_cat)

                if mate_cat.gender == "female":
                    afab_mate.append(mate_cat)
                else:
                    amab_mate.append(mate_cat)

            # if both cats are faithful to each other and aren't cheaters,
            # the pregnancy will be announced as normal
            if second_parent and second_parent.ID in pregnant_cat.mate:
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    pregnant_cat, "announcement", random_cat=second_parent
                )
            # if the pregnant cat is single and had a fling with a random cat, let them
            # announce their surprise pregnancy and leave the Clan and player pointing
            # fingers on who the second parent may be
            elif allow_coparenting and not mate:
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    pregnant_cat, "announcement_surprise"
                )
            # if the pregnant cat is in a same-sex relationship and they get knocked-up
            # by another cat, let there be some drama for that!
            elif (
                allow_affair is True
                and second_parent
                and second_parent.ID not in pregnant_cat.mate
                and afab_mate
            ):
                random_cat = afab_mate[0] if afab_mate else None
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    pregnant_cat,
                    "announcement_affair_samesex",
                    random_cat=random_cat,
                )
            # and lastly, if the pregnant cat got knocked up by another cat who ISN'T their mate,
            # let the player guess whether it's an affair or not, sometimes the events will tell you,
            # sometimes they won't...
            elif (
                allow_affair is True
                and second_parent
                and second_parent.ID not in pregnant_cat.mate
                and amab_mate
            ):
                announcement_key = choice(["announcement_affair", "announcement"])
                Pregnancy_Events.set_affair_visibility_on_pregnancy(
                    pregnant_cat, announcement_key == "announcement_affair"
                )
                random_cat = amab_mate[0] if amab_mate else None
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    pregnant_cat, announcement_key, random_cat=random_cat
                )
            # if all else fails, just a regular announcement happens
            else:
                text, involved_cats = Pregnancy_Events.create_pregnancy_announcement(
                    pregnant_cat, "announcement", random_cat=second_parent
                )
            game.cur_events_list.append(
                Single_Event(text, "birth_death", involved_cats)
            )

    @staticmethod
    def handle_one_moon_pregnant(cat: Cat, clan=game.clan):
        """Handles if the cat is one moon pregnant."""
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat killed meanwhile, delete it from the dictionary
        if cat.dead:
            del clan.pregnancy_data[cat.ID]
            return

        amount = Pregnancy_Events.get_amount_of_kits(cat)
        text = "This should not appear (pregnancy_events.py)"

        # add the amount to the pregnancy dict
        clan.pregnancy_data[cat.ID]["amount"] = amount

        # if the cat is outside of the clan, they won't guess how many kits they will have
        if cat.status.is_outsider:
            return

        thinking_amount = random.choices(
            ["correct", "incorrect", "unsure"], [4, 1, 1], k=1
        )
        if amount <= 3:
            correct_guess = "small"
        else:
            correct_guess = "large"

        Pregnancy_Events.rebuild_strings()

        if thinking_amount[0] == "correct":
            if correct_guess == "small":
                text = choice(
                    Pregnancy_Events.PREGNANT_STRINGS["litter_guess"]["small"]
                )
            else:
                text = choice(
                    Pregnancy_Events.PREGNANT_STRINGS["litter_guess"]["large"]
                )
        elif thinking_amount[0] == "incorrect":
            if correct_guess == "small":
                text = choice(
                    Pregnancy_Events.PREGNANT_STRINGS["litter_guess"]["large"]
                )
            else:
                text = choice(
                    Pregnancy_Events.PREGNANT_STRINGS["litter_guess"]["small"]
                )
        else:
            text = choice(Pregnancy_Events.PREGNANT_STRINGS["litter_guess"]["unsure"])

        try:
            if cat.injuries["pregnant"]["severity"] == "minor":
                cat.injuries["pregnant"]["severity"] = "major"
                text += choice(Pregnancy_Events.PREGNANT_STRINGS["major_severity"])
        except:
            print("Is this an old save? Cat does not have the pregnant condition")

        text = event_text_adjust(Cat, text, main_cat=cat, clan=game.clan)
        game.cur_events_list.append(
            Single_Event(text, "birth_death", cat_dict={"m_c": cat})
        )

    @staticmethod
    def handle_two_moon_pregnant(cat: Cat, clan=game.clan):
        """Handles if the cat is two moons pregnant."""
        if cat.ID not in clan.pregnancy_data.keys():
            return

        # if the pregnant cat is killed meanwhile, delete it from the dictionary
        if cat.dead:
            del clan.pregnancy_data[cat.ID]
            return

        involved_cats = [cat.ID]
        cat_dict = {"m_c": cat}

        kits_amount = clan.pregnancy_data[cat.ID]["amount"]
        if (
            kits_amount == 0
        ):  # safety check, sometimes pregnancies were ending up with 0 due to save rollbacks
            kits_amount = 1
        other_cat_id = clan.pregnancy_data[cat.ID]["second_parent"]
        other_cat = Cat.all_cats.get(other_cat_id)

        Pregnancy_Events.set_biggest_family()
        extra_naming_text = None
        has_afab_mate = any(
            Cat.fetch_cat(mate_id) and Cat.fetch_cat(mate_id).gender == "female"
            for mate_id in cat.mate
        )
        adoptive_parents = []
        cheated_mate = None
        mate_claimed_kits = False
        secret_affair_birth = False
        other_cat_affair_known = True
        affair_known = Pregnancy_Events.get_affair_visibility_from_pregnancy(
            cat, clan=clan
        )
        if other_cat and cat.mate and other_cat.ID not in cat.mate:
            cheated_mate = Pregnancy_Events.get_cheated_mate(cat)
            if cheated_mate:
                # if the mate at first didn't know they were cheated on,
                # there's a chance they will find out
                if affair_known is False and random.randint(0, 1):
                    secret_affair_birth = True
                    adoptive_parents.append(cheated_mate.ID)
                else:
                    # if they knew, they can still choose to help raise the kits or not
                    mate_claimed_kits = Pregnancy_Events.should_claim_affair_kits(
                        cheated_mate, cat
                    )
                    if mate_claimed_kits:
                        adoptive_parents.append(cheated_mate.ID)
        coparenting_outcome = None
        kits = Pregnancy_Events.get_kits(
            kits_amount, cat, other_cat, game.clan, adoptive_parents=adoptive_parents
        )
        kits_amount = len(kits)
        Pregnancy_Events.set_biggest_family()

        # delete the cat out of the pregnancy dictionary
        del clan.pregnancy_data[cat.ID]

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
                    name = choice(names.names_dict["normal_prefixes"])
                    kit.name = Name(prefix=name, suffix="", cat=kit)
                    extra_naming_text = i18n.t(
                        "conditions.pregnancy.reject_clan_tradition",
                        name=cat.name,
                    )

                if other_cat and not other_cat.status.is_outsider:
                    kit.backstory = "outsider2"

                if cat.status.is_lost(CatGroup.PLAYER_CLAN_ID):
                    kit.backstory = "outsider3"
                    if not keep_clan_tradition:
                        name = choice(names.names_dict["normal_prefixes"])
                        kit.name = Name(prefix=name, suffix="", cat=kit)
                        extra_naming_text = i18n.t(
                            "conditions.pregnancy.reject_clan_tradition",
                            name=cat.name,
                        )
                    else:
                        extra_naming_text = i18n.t(
                            "conditions.pregnancy.keep_clan_tradition",
                            name=cat.name,
                        )

        insert = i18n.t("conditions.pregnancy.kit_amount", count=kits_amount)

        # Since cat has given birth, apply the birth cooldown.
        cat.birth_cooldown = get_config("pregnancy.birth_cooldown")

        # choose event string
        # TODO: currently they don't choose which 'mate' is the 'blood' parent or not
        # change or leaf as it is?
        Pregnancy_Events.rebuild_strings()
        events = Pregnancy_Events.PREGNANT_STRINGS
        event_list = []
        # single parent strings
        if not cat.status.is_outsider and other_cat is None:
            event_list.append(choice(events["birth"]["unmated_parent"]))

        # outsider birth strings
        elif cat.status.is_outsider:
            adding_text = choice(events["birth"]["outside_alone"])
            if cat.status.is_lost(CatGroup.PLAYER_CLAN):
                adding_text = choice(events["birth"]["outside_lost"])
            if other_cat and not other_cat.status.is_outsider:
                adding_text = choice(events["birth"]["outside_in_clan"])
            event_list.append(adding_text)

        # two parents strings
        elif other_cat.ID in cat.mate and other_cat.status.alive_in_player_clan:
            involved_cats.append(other_cat.ID)
            cat_dict["r_c"] = other_cat
            event_list.append(choice(events["birth"]["two_parents"]))

        # dead mate strings
        elif other_cat.ID in cat.mate and other_cat.dead:
            involved_cats.append(other_cat.ID)
            cat_dict["r_c"] = other_cat
            event_list.append(choice(events["birth"]["dead_mate"]))

        # the long awaited outsider mate event strings
        elif other_cat.ID in cat.mate and other_cat.status.is_outsider:
            involved_cats.append(other_cat.ID)
            cat_dict["r_c"] = other_cat
            event_list.append(choice(events["birth"]["outside_mate"]))

        # unmated strings
        elif len(cat.mate) < 1 and len(other_cat.mate) < 1 and not other_cat.dead:
            involved_cats.append(other_cat.ID)
            cat_dict["r_c"] = other_cat
            # 50% chance for the parents to be positive or negative towards co-parenting
            if random.randint(0, 1):
                coparenting_outcome = "positive"
                event_list.append(choice(events["birth"]["both_unmated_pos"]))
            else:
                coparenting_outcome = "negative"
                event_list.append(choice(events["birth"]["both_unmated_neg"]))

        # affair birth strings (same sex)
        elif (
            not get_clan_setting("same sex birth")
            and has_afab_mate
            and other_cat.ID not in cat.mate
        ):
            involved_cats.append(other_cat.ID)
            cat_dict["r_c"] = other_cat
            chosen_mate = Pregnancy_Events.get_cheated_mate(cat)
            if chosen_mate:
                cat_dict["mc_mate"] = chosen_mate
                involved_cats.append(chosen_mate.ID)
            event_list.append(choice(events["birth"]["affair_mated_samesex"]))

        # affair birth strings (the main cat cheated on their mate)
        elif len(cat.mate) > 0 and other_cat.ID not in cat.mate and not other_cat.dead:
            living_mate = Pregnancy_Events.get_cheated_mate(cat)
            dead_mate = Pregnancy_Events.get_cheated_mate(cat, include_dead=True)
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

        # affair birth strings (the other_cat cheated on their mate)
        elif (
            len(other_cat.mate) > 0
            and cat.ID not in other_cat.mate
            and not other_cat.dead
        ):
            other_mate = Pregnancy_Events.get_cheated_mate(other_cat)
            if other_mate:
                # determine if the other_cat's mate is aware of their mate
                # cheating on them
                other_cat_affair_known = bool(random.randint(0, 1))
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

        # add naming choice text here
        if extra_naming_text:
            event_list.append(extra_naming_text)

        involved_cats += [k.ID for k in kits]

        if clan.game_mode != "classic":
            try:
                death_chance = cat.injuries["pregnant"]["mortality"]
            except:
                death_chance = 40
        else:
            death_chance = 40
        if not int(
            random.random() * death_chance
        ):  # chance for a cat to die during childbirth
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
                clan.leader_lives -= 1
                cat.die()
                death_event = i18n.t("conditions.pregnancy.leader_kitting_death")
                if extra_result := check_stolen_vitality(cat, 1):
                    death_event += " " + extra_result
            else:
                cat.die()
                death_event = i18n.t(
                    "conditions.pregnancy.kitting_death", name=cat.name
                )
            cat.history.add_death(death_text=death_event)
        elif (
            not cat.status.is_outsider
        ):  # if cat doesn't die, give recovering from birth
            cat.get_injured("recovering from birth", event_triggered=True)
            if "blood loss" in cat.injuries:
                if cat.status.is_leader:
                    death_event = i18n.t(
                        "conditions.pregnancy.leader_kitting_death_severe"
                    )
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
            except:
                print(
                    "Is this an old save? Your cat didn't have the pregnant condition!"
                )
        print_event = " ".join(event_list)
        print_event = print_event.replace("{insert}", insert)

        # if the event doesn't mention mc/rc_mate, remove the cheated mate's ID from the event
        involved_cats = Pregnancy_Events.remove_unmentioned_mate_ids(
            involved_cats, print_event, cat_dict
        )

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

        # relationship changes for affair births
        # this outcome here happens if the birthing cat cheated on their mate
        # here, the cheated mate loses relationship to the birthing cat
        if (
            other_cat
            and len(cat.mate) > 0
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
                rel = mate.relationships.get(cat.ID)
                if rel:
                    rel.romance += breakup_reaction["romance"]
                    rel.trust += breakup_reaction["trust"]
                    rel.like += breakup_reaction["like"]
                    log_text = process_text(
                        i18n.t("conditions.pregnancy.affair_rel_log"),
                        {
                            "m_c": (str(mate.name), choice(mate.pronouns)),
                            "r_c": (str(cat.name), choice(cat.pronouns)),
                        },
                    )
                    log_text = i18n.t(
                        "relationships.negative_postscript", text=log_text
                    )
                    rel.log.append(
                        i18n.t(
                            "relationships.age_postscript",
                            text=log_text,
                            name=str(cat.name),
                            count=cat.moons,
                        )
                    )

        # if the other cat had a mate, their mate also lose relationship with them
        if (
            other_cat
            and len(other_cat.mate) > 0
            and cat.ID not in other_cat.mate
            and other_cat_affair_known
        ):
            for mate_id in other_cat.mate:
                mate = Cat.fetch_cat(mate_id)
                if not mate:
                    continue

                breakup_reaction = get_config(
                    "mates.mates.breakup.reactions.affair_discovery_other_mate_reaction"
                )
                rel = mate.relationships.get(other_cat.ID)
                if rel:
                    rel.romance += breakup_reaction["romance"]
                    rel.trust += breakup_reaction["trust"]
                    rel.like += breakup_reaction["like"]
                    rel.log.append(
                        process_text(
                            i18n.t("conditions.pregnancy.affair_rel_log"),
                            {
                                "m_c": (str(mate.name), choice(mate.pronouns)),
                                "r_c": (
                                    str(other_cat.name),
                                    choice(other_cat.pronouns),
                                ),
                            },
                        )
                        + i18n.t("relationships.negative_postscript")
                        + i18n.t(
                            "relationships.age_postscript",
                            name=str(other_cat.name),
                            count=other_cat.moons,
                        )
                    )

        # relationship changes for unmated co-parenting births
        if (
            other_cat
            and len(cat.mate) < 1
            and len(other_cat.mate) < 1
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
                    absent_parent_to_kit.respect += absent_parent_to_kit_reaction[
                        "respect"
                    ]
                    absent_parent_to_kit.comfort += absent_parent_to_kit_reaction[
                        "comfort"
                    ]
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
                    rel.comfort += coparenting_values_neg["comfort"]
                    rel.trust += coparenting_values_neg["trust"]
                    if rel.romance > 0:
                        rel.romance += coparenting_values_neg["romance"]
                    log_text = process_text(
                        i18n.t("conditions.pregnancy.coparenting_rel_log_neg"),
                        {
                            "m_c": (
                                str(first_cat.name),
                                choice(first_cat.pronouns),
                            ),
                            "r_c": (
                                str(second_cat.name),
                                choice(second_cat.pronouns),
                            ),
                        },
                    )
                    log_text = i18n.t(
                        "relationships.negative_postscript", text=log_text
                    )
                    rel.log.append(
                        i18n.t(
                            "relationships.age_postscript",
                            text=log_text,
                            name=str(second_cat.name),
                            count=second_cat.moons,
                        )
                    )
                elif coparenting_outcome == "positive":
                    rel.comfort += coparenting_values_pos["comfort"]
                    rel.trust += coparenting_values_pos["trust"]
                    if rel.romance > 0:
                        rel.romance += coparenting_values_pos["romance"]
                    log_text = process_text(
                        i18n.t("conditions.pregnancy.coparenting_rel_log_pos"),
                        {
                            "m_c": (
                                str(first_cat.name),
                                choice(first_cat.pronouns),
                            ),
                            "r_c": (
                                str(second_cat.name),
                                choice(second_cat.pronouns),
                            ),
                        },
                    )
                    log_text = i18n.t(
                        "relationships.positive_postscript", text=log_text
                    )
                    rel.log.append(
                        i18n.t(
                            "relationships.age_postscript",
                            text=log_text,
                            name=str(second_cat.name),
                            count=second_cat.moons,
                        )
                    )

        # display event
        game.cur_events_list.append(
            Single_Event(
                print_event, ["health", "birth_death"], involved_cats, cat_dict=cat_dict
            )
        )

        # chance to break up the cat and their mate
        # if the mate doesn't want to anything to do with the affair litter
        if cheated_mate and not mate_claimed_kits and not secret_affair_birth:
            Pregnancy_Events.handle_affair_discovery_breakup(cat, cheated_mate)

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
                    Pregnancy_Events.handle_affair_discovery_breakup(
                        other_cat, other_cat_mate
                    )

    # ---------------------------------------------------------------------------- #
    #                          check if event is triggered                         #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def check_if_can_have_kits(cat, allow_single_parent, allow_unmated, allow_affair):
        """Check if the given cat can have kits, see for age, birth-cooldown and so on."""
        if not cat:
            return False

        if cat.birth_cooldown > 0:
            return False

        if "recovering from birth" in cat.injuries:
            return False

        # decide chances of having kits, and if it's possible at all.
        # Including - age, dead status, having kits turned off.
        not_correct_age = (
            cat.age in [CatAge.NEWBORN, CatAge.KITTEN, CatAge.ADOLESCENT]
            or cat.moons < 15
        )
        if not_correct_age or cat.no_kits or cat.dead:
            return False

        # check for mate
        if len(cat.mate) > 0:
            for mate_id in cat.mate:
                if mate_id not in cat.all_cats:
                    print(
                        f"WARNING: {cat.name}  has an invalid mate # {mate_id}. This has been unset."
                    )
                    cat.mate.remove(mate_id)
        else:
            # if the cat has no mate, and we don't allow single parents, unmated parents, or affairs
            # then they can't have kits
            if not allow_single_parent or not allow_unmated or not allow_affair:
                return False

        # if function reaches this point, having kits is possible
        return True

    @staticmethod
    def check_second_parent(
        cat: Cat,
        second_parent: Cat,
        single_parentage: bool,
        allow_unmated: bool,
        allow_affair: bool,
        same_sex_birth: bool,
        same_sex_adoption: bool,
    ):
        """
        This checks to see if the chosen second parent and CAT can have kits. It assumes CAT can have kits.
        returns:
        parent can have kits, kits are adopted
        """

        # Checks for second parent alone:
        if not Pregnancy_Events.check_if_can_have_kits(
            second_parent, single_parentage, allow_unmated, allow_affair
        ):
            return False, False

        # Check to see if the pair can have kits.
        if cat.gender == second_parent.gender:
            if same_sex_birth:
                return True, False
            elif not same_sex_adoption:
                return False, False
            else:
                return True, True

        return True, False

    # ---------------------------------------------------------------------------- #
    #                               getter functions                               #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def get_second_parent(cat):
        """
        Return the second parent of a cat, which will have kits.
        Also returns a bool that is true if an affair was triggered.
        """
        samesex = get_clan_setting("same sex birth")
        allow_affair = get_clan_setting("affair")
        mate = None
        coparenting = False

        # randomly select a mate of given cat
        if len(cat.mate) > 0:
            mate = choice(cat.mate)
            mate = cat.fetch_cat(mate)

        # if the sex does matter, choose the best solution to allow kits
        if not samesex and mate and mate.gender == cat.gender:
            opposite_mate = [
                cat.fetch_cat(mate_id)
                for mate_id in cat.mate
                if cat.fetch_cat(mate_id).gender != cat.gender
            ]
            if len(opposite_mate) > 0:
                mate = choice(opposite_mate)

        if not allow_affair and mate:
            # if affairs setting is OFF, second parent (mate) will be returned
            return mate, False

        # get relationships to influence the affair chance
        mate_relation = None
        if mate and mate.ID in cat.relationships:
            mate_relation = cat.relationships[mate.ID]
        elif mate:
            mate_relation = cat.create_one_relationship(mate)

        if len(cat.mate) <= 0:
            coparenting = True

        # LOVE AFFAIR & COPARENTING
        # Handle love affair chance.
        affair_partner = Pregnancy_Events.determine_highest_romantic_relation(
            cat, mate, mate_relation, samesex
        )
        if affair_partner:
            return affair_partner, True

        # RANDOM AFFAIR & COPARENTING
        if coparenting:
            chance = get_config("pregnancy.unmated_random_affair_chance")
        else:
            chance = get_config("pregnancy.random_affair_chance")

        # 'buff' affairs & coparenting if the current biggest family is big + this cat doesn't belong there
        if not Pregnancy_Events.biggest_family:
            Pregnancy_Events.set_biggest_family()

        if (
            Pregnancy_Events.biggest_family_is_big()
            and cat.ID not in Pregnancy_Events.biggest_family
        ):
            chance = int(chance * 0.8)

        # "regular" random affair
        if not int(random.random() * chance):
            possible_affair_partners = [
                i
                for i in Cat.all_cats_list
                if i.is_potential_mate(cat, for_love_interest=True)
                and (samesex or i.gender != cat.gender)
                and i.ID not in cat.mate
            ]
            if coparenting:
                possible_affair_partners = [
                    c for c in possible_affair_partners if len(c.mate) < 1
                ]

            # even it is a random affair, the cats should not hate each other or something like that
            p_affairs = []
            if len(possible_affair_partners) > 0:
                for p_affair in possible_affair_partners:
                    if p_affair.ID in cat.relationships:
                        p_rel = cat.relationships[p_affair.ID]
                        if not p_rel.opposite_relationship:
                            p_rel.link_relationship()
                        p_rel_opp = p_rel.opposite_relationship
                        if p_rel_opp.like > -20 and p_rel.like > -20:
                            p_affairs.append(p_affair)
            possible_affair_partners = p_affairs

            if len(possible_affair_partners) > 0:
                chosen_affair = choice(possible_affair_partners)
                return chosen_affair, True

        return mate, False

    @staticmethod
    def determine_highest_romantic_relation(cat, mate, mate_relation, samesex):
        """
        Function to handle everything around love affairs.
        Will return a second parent if a love affair is triggerd, and none otherwise.
        """

        highest_romantic_relation = get_highest_romantic_relation(
            cat.relationships.values(), exclude_mate=True, potential_mate=True
        )

        if mate and highest_romantic_relation:
            # Love affair calculation when the cat has a mate
            chance_love_affair = Pregnancy_Events.get_love_affair_chance(
                mate_relation, highest_romantic_relation
            )
            if not chance_love_affair or not int(random.random() * chance_love_affair):
                if samesex or cat.gender != highest_romantic_relation.cat_to.gender:
                    return highest_romantic_relation.cat_to
        elif highest_romantic_relation:
            # Love affair chance if the cat doesn't have a mate:
            chance_love_affair = Pregnancy_Events.get_unmated_coparenting_chance(
                highest_romantic_relation
            )
            if not chance_love_affair or not int(random.random() * chance_love_affair):
                if samesex or cat.gender != highest_romantic_relation.cat_to.gender:
                    return highest_romantic_relation.cat_to

        return None

    @staticmethod
    def get_kits(
        kits_amount,
        cat=None,
        other_cat=None,
        clan=game.clan,
        adoptive_parents=None,
    ):
        """Create some amount of kits
        No parents are specified, it will create a blood parents for all the
        kits to be related to. They may be dead or alive, but will always be outside
        the clan."""
        Pregnancy_Events.rebuild_strings()
        all_kitten = []
        if not adoptive_parents:
            adoptive_parents = []

        # First, just a check: If we have no cat, but an other_cat was provided,
        # swap other_cat to cat:
        # This way, we can ensure that if only one parent is provided,
        # it's cat, not other_cat.
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
                if not mate:
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
                if not mate:
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
        for _m in adoptive_parents:
            if _m not in all_adoptive_parents:
                all_adoptive_parents.append(_m)

        #############################

        #### GENERATE THE KITS ######
        for kit in range(kits_amount):
            # should have to use this initial assignment, but just in case, we'll set it as newborn
            kitten_status = {"age": CatAge.NEWBORN}

            if cat:
                kitten_status: StatusDict = {
                    "social": cat.status.social,
                    "age": CatAge.NEWBORN,
                    "group_ID": cat.status.group_ID,
                }

            if not cat:
                # No parents provided, give a blood parent - this is an adoption.
                if not blood_parent:
                    # Generate a blood parent if we haven't already.
                    thought = i18n.t(
                        "conditions.pregnancy.half_blood_kitting_thought",
                        count=kits_amount,
                    )

                    blood_parent = create_new_cat(
                        Cat,
                        original_social=random.choice(
                            (CatSocial.LONER, CatSocial.KITTYPET)
                        ),
                        alive=False,
                        moons=randint(15, 120),
                        outside=True,
                    )[0]
                    thought = event_text_adjust(
                        Cat, text=thought, main_cat=blood_parent
                    )
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

            kit.get_new_thought()

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
                random.random() * get_config("cat_generation.base_permanent_condition")
            ):
                kit.congenital_condition(kit)
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
                relationships_to_update = clan.clan_cats
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
                        y = random.randrange(0, 15)
                        start_relation = Relationship(the_cat, kit, False, True)
                        start_relation.like = parent_to_kit[RelType.LIKE] + y
                        start_relation.comfort = parent_to_kit[RelType.COMFORT] + y
                        start_relation.respect = parent_to_kit[RelType.RESPECT] + y
                        start_relation.trust = parent_to_kit[RelType.TRUST] + y
                        the_cat.relationships[kit.ID] = start_relation

                        kit_to_parent = get_config("new_cat.parent_buff.kit_to_parent")
                        y = random.randrange(0, 15)
                        start_relation = Relationship(kit, the_cat, False, True)
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
            clan.add_cat(kit)

            #### GIVE HISTORY ######
            kit.history.add_beginning(clan_born=bool(cat))

        # check other cats of Clan for siblings
        for kitten in all_kitten:
            # update/buff the relationship towards the siblings
            for second_kitten in all_kitten:
                y = random.randrange(0, 10)
                if second_kitten.ID == kitten.ID:
                    continue
                relationship_value = get_config(
                    "new_cat.sib_buff.littermates_to_eachother"
                )
                start_relation = Relationship(kitten, second_kitten, False, True)
                start_relation.like += relationship_value["like"] + y
                start_relation.comfort += relationship_value["comfort"] + y
                start_relation.trust += relationship_value["trust"] + y
                kitten.relationships[second_kitten.ID] = start_relation

        # check if the possible adoptive cat is not already in the family tree and
        # add them as adoptive parents if not
        final_adoptive_parents = []
        for adoptive_p in all_adoptive_parents:
            Cat.fetch_cat(adoptive_p).get_new_thought(CatThought.ON_BIRTH)
            if adoptive_p not in inheritance_db.get_relatives(all_kitten[0].ID, True):
                final_adoptive_parents.append(adoptive_p)
        if not adoptive_parents:
            cat.get_new_thought(CatThought.ON_BIRTH)
            if other_cat:
                cat.get_new_thought(CatThought.ON_BIRTH)

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
                y = random.randrange(-variation_range, variation_range)

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
                        relation_toward_parent: Relationship = c.relationships[
                            parent_id
                        ]
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
                        cat,
                        choice(
                            Pregnancy_Events.NEWBORN_REL_REACTIONS[f"{rel_type}_log"]
                        ),
                        main_cat=c,
                        random_cat=kit,
                        clan=game.clan,
                    ),
                )

                change_relationship_values(**new_relationship)

        return all_kitten

    @staticmethod
    def get_amount_of_kits(cat):
        """Get the amount of kits which will be born."""
        min_kits = constants.CONFIG["pregnancy"]["min_kits"]
        min_kit = [min_kits] * constants.CONFIG["pregnancy"]["one_kit_possibility"][
            cat.age.value
        ]
        two_kits = [min_kits + 1] * constants.CONFIG["pregnancy"][
            "two_kit_possibility"
        ][cat.age.value]
        three_kits = [min_kits + 2] * constants.CONFIG["pregnancy"][
            "three_kit_possibility"
        ][cat.age.value]
        four_kits = [min_kits + 3] * constants.CONFIG["pregnancy"][
            "four_kit_possibility"
        ][cat.age.value]
        five_kits = [min_kits + 4] * constants.CONFIG["pregnancy"][
            "five_kit_possibility"
        ][cat.age.value]
        max_kits = [constants.CONFIG["pregnancy"]["max_kits"]] * constants.CONFIG[
            "pregnancy"
        ]["max_kit_possibility"][cat.age.value]
        amount = choice(
            min_kit + two_kits + three_kits + four_kits + five_kits + max_kits
        )

        return amount

    # ---------------------------------------------------------------------------- #
    #                                  get chances                                 #
    # ---------------------------------------------------------------------------- #

    @staticmethod
    def get_love_affair_chance(
        mate_relation: Relationship, affair_relation: Relationship
    ):
        """Looks into the current values and calculate the chance of having kits with the affair cat.
        The lower, the more likely they will have affairs. This function should only be called when mate
        and affair_cat are not the same.

        Returns:
            integer (number)
        """
        if not mate_relation.opposite_relationship:
            mate_relation.link_relationship()

        if not affair_relation.opposite_relationship:
            affair_relation.link_relationship()

        average_mate_love = (
            mate_relation.romance + mate_relation.opposite_relationship.romance
        ) / 2
        average_affair_love = (
            affair_relation.romance + affair_relation.opposite_relationship.romance
        ) / 2

        difference = average_mate_love - average_affair_love

        if difference < 0:
            # If the average love between affair partner is greater than the average love between the mate
            affair_chance = 10
            difference = -difference

            if difference > 30:
                affair_chance -= 7
            elif difference > 20:
                affair_chance -= 6
            elif difference > 15:
                affair_chance -= 5
            elif difference > 10:
                affair_chance -= 4

        elif difference > 0:
            # If the average love between the mate is greater than the average relationship between the affair
            affair_chance = 30

            if difference > 30:
                affair_chance += 8
            elif difference > 20:
                affair_chance += 5
            elif difference > 15:
                affair_chance += 3
            elif difference > 10:
                affair_chance += 5

        else:
            # For difference = 0 or some other weird stuff
            affair_chance = 15

        return affair_chance

    @staticmethod
    def get_unmated_coparenting_chance(relation: Relationship) -> int:
        """
        Calculates the chance of coparenting when neither the cat
        nor highest romantic relation have mates.
        """

        if not relation.opposite_relationship:
            relation.link_relationship()

        coparenting_chance = 15
        average_romantic_love = (
            relation.romance + relation.opposite_relationship.romance
        ) / 2

        if average_romantic_love > 50:
            coparenting_chance -= 12
        elif average_romantic_love > 40:
            coparenting_chance -= 10
        elif average_romantic_love > 30:
            coparenting_chance -= 7
        elif average_romantic_love > 10:
            coparenting_chance -= 5

        return coparenting_chance

    @staticmethod
    def get_balanced_kit_chance(
        first_parent: Cat, second_parent: Cat, affair, clan
    ) -> int:
        """Returns a chance based on different values."""
        # Now that the second parent is determined, we can calculate the balanced chance for kits
        # get the chance for pregnancy
        inverse_chance = get_config("pregnancy.primary_chance_unmated")
        if len(first_parent.mate) > 0 and not affair:
            inverse_chance = get_config("pregnancy.primary_chance_mated")

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
        living_cats = len(
            [i for i in Cat.all_cats.values() if i.status.alive_in_player_clan]
        )
        if living_cats < 10:
            inverse_chance = int(inverse_chance * 0.5)
        elif living_cats > 30:
            inverse_chance = int(inverse_chance * (living_cats / 30))

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
        # - decrease the inverse chance if the cats are going along well
        if second_parent:
            # get the needed relationships
            if second_parent.ID in first_parent.relationships:
                second_parent_relation = first_parent.relationships[second_parent.ID]
                if not second_parent_relation.opposite_relationship:
                    second_parent_relation.link_relationship()
            else:
                second_parent_relation = first_parent.create_one_relationship(
                    second_parent
                )
                if not second_parent_relation.opposite_relationship:
                    second_parent_relation.link_relationship()
            average_romantic_love = (
                second_parent_relation.romance
                + second_parent_relation.opposite_relationship.romance
            ) / 2
            average_comfort = (
                second_parent_relation.comfort
                + second_parent_relation.opposite_relationship.comfort
            ) / 2
            average_trust = (
                second_parent_relation.trust
                + second_parent_relation.opposite_relationship.trust
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
        avg_age = int(sum((cat.moons for cat in Cat.all_cats.values())) / living_cats)
        if avg_age > 80:
            inverse_chance = int(inverse_chance * 0.8)

        # CURRENT KIT COUNT
        # increases inverse chance according to number of existing children (ex. 5 kids will multiply by 1.5)
        inverse_chance += int(inverse_chance * len(first_parent.get_children()) * 0.1)

        # 'INBREED' counter
        # - increase inverse chance if one of the current cats belongs in the biggest family
        if not Pregnancy_Events.biggest_family:  # set the family if not already
            Pregnancy_Events.set_biggest_family()

        if (
            first_parent.ID in Pregnancy_Events.biggest_family
            or second_parent
            and second_parent.ID in Pregnancy_Events.biggest_family
        ):
            inverse_chance = int(inverse_chance * 1.7)

        # - decrease inverse chance if the current family is small
        if len(first_parent.get_relatives(get_clan_setting("first cousin mates"))) < (
            living_cats / 15
        ):
            inverse_chance = int(inverse_chance * 0.7)

        # - decrease inverse chance single parents if settings allow an biggest family is huge
        settings_allow = not second_parent and not get_clan_setting("single parentage")
        if settings_allow and Pregnancy_Events.biggest_family_is_big():
            inverse_chance = int(inverse_chance * 0.9)

        return inverse_chance
