from random import choice, randint, choices

import i18n

from scripts.cat.enums import CatRank
from scripts.cat.skills import SkillPath
from scripts.clan_resources.herb.herb import Herb, HERBS
from scripts.clan_resources.herb.herb_effects import HerbEffect
from scripts.clan_resources.supply import Supply
from scripts.game_structure import constants
from scripts.game_structure.game_essentials import game
from scripts.game_structure.localization import load_lang_resource
from scripts.utility import (
    adjust_list_text,
    event_text_adjust,
    PERMANENT,
    ILLNESSES,
    INJURIES,
)
from collections import defaultdict


class HerbSupply:
    """Handles managing the Clan's herb supply."""

    def __init__(self, herb_supply: dict[str, list[int | float]] = None):
        """
        Initialize the class
        """
        # a dict of current stored herbs - herbs collected this moon
        self.storage = defaultdict(list)
        if herb_supply:
            for herb, amounts in herb_supply.items():
                self.storage[herb] = [int(i) for i in amounts]

        # a dict of herbs collected this moon
        self.collected = defaultdict(int)

        # herb count required for clan
        self.required_herb_count: int = 0

        # herbs the clan needs for treatment of current clan ailments
        self.in_need_of: list = []

        self.base_herb_list = HERBS
        self.herb = {}
        for herb in self.base_herb_list:
            self.herb[herb] = Herb(herb)
        self.base_herb_list = HERBS

        # med den log for current moon
        self.log = []

    @property
    def combined_supply_dict(self) -> dict:
        """
        returns a dict containing both the storage and the collected herb dicts
        """
        combined_supply = {"storage": self.storage, "collected": self.collected}
        return combined_supply

    @property
    def entire_supply(self) -> dict:
        """
        Dict of the storage and collected herbs combined and totaled. Key is herb name, value is total of that herb
        within the supply.
        """
        return {herb: self.total_of_herb(herb) for herb in self.base_herb_list}

    @property
    def total(self) -> int:
        """
        return total int of all herb inventory
        """
        total = 0
        for herb in self.storage:
            for stock in self.storage[herb]:
                total += stock
        for herb, count in self.collected.items():
            total += count

        return total

    @property
    def sorted_by_lowest(self) -> list:
        """
        returns list of herbs ordered from the least supply to most
        """
        sort_list = [x for x in self.entire_supply]
        sort_list.sort(key=lambda list_herb: self.entire_supply[list_herb])

        return sort_list

    @property
    def sorted_by_need(self) -> list:
        """
        returns list of herbs sorted by what is most needed and has the least supply
        """
        final_sort_list = []
        extra = []

        if not self.in_need_of:
            return self.sorted_by_lowest

        for herb in self.sorted_by_lowest:
            if herb in self.in_need_of and self.get_herb_rating(herb) in [
                Supply.EMPTY,
                Supply.LOW,
            ]:
                final_sort_list.append(herb)
            else:
                extra.append(herb)

        return final_sort_list + extra

    @property
    def low_qualifier(self) -> int:
        """
        returns the lowest qualifier for a low supply
        """
        return 0

    @property
    def adequate_qualifier(self) -> int:
        """
        returns the lowest qualifier for an adequate supply
        """
        return round(
            self.required_herb_count
            / constants.CONFIG["clan_resources"]["herbs"]["adequate"]
        )

    @property
    def full_qualifier(self) -> int:
        """
        returns the lowest qualifier for a full supply
        """
        return self.required_herb_count

    @property
    def excess_qualifier(self) -> int:
        """
        returns the lowest qualifier for an adequate supply
        """
        return (
            self.required_herb_count
            * constants.CONFIG["clan_resources"]["herbs"]["excess"]
        )

    def convert_old_save(self, herb_list):
        """
        used to start a new storage dict if the clan had old save file to convert
        """
        for herb, count in herb_list.items():
            if herb in self.base_herb_list:
                self.storage[herb] = [count]

    def set_required_herb_count(self, clan_size):
        """
        takes given clan_size and multiplies it by the required_herbs_per_cat from constants.CONFIG
        """
        self.required_herb_count = (
            clan_size
            * constants.CONFIG["clan_resources"]["herbs"]["required_herbs_per_cat"]
        )

    def start_storage(self, clan_size):
        """
        start's a Clan's storage. Clans begin with a random set of herbs.
        """
        self.set_required_herb_count(clan_size)

        for herb in self.base_herb_list:
            if randint(1, 4) == 1:
                self.add_herb(
                    herb,
                    num_collected=randint(self.adequate_qualifier, self.full_qualifier),
                )

    def handle_moon(self, clan_size: int, clan_cats: list, med_cats: list):
        """
        handle herbs on moon skip: add collected to supply, use herbs where needed, expire old herbs, look for new herbs
        """

        # clear log
        self.log = []

        # set herb count
        self.set_required_herb_count(clan_size)

        # add herbs acquired last moon
        self._add_collection_to_storage(med_cats)

        # look for new herbs
        for med in med_cats:
            self._gather_herbs(med)

        # check if herbs can be used
        severity_ranking = {"severe": [], "major": [], "minor": []}
        cats_to_treat = [
            kitty
            for kitty in clan_cats
            if kitty.is_ill() or kitty.is_injured() or kitty.is_disabled()
        ]
        for kitty in cats_to_treat:
            # if there are no working med cats, then only allow med cats to be treated. the idea being that a med cat
            # could conceivably attempt to care for themselves, but would not be well enough to care for the Clan as
            # a whole. also helps prevent death spiral when med cats aren't able to work.
            if not med_cats and not kitty.status.rank.is_any_medicine_rank():
                break
            severities = []
            conditions = kitty.permanent_condition.copy()
            conditions.update(kitty.injuries)
            conditions.update(kitty.illnesses)
            for con in conditions:
                severities.append(conditions[con]["severity"])
            if "severe" in severities:
                severity_ranking["severe"].append(kitty)
            elif "major" in severities:
                severity_ranking["major"].append(kitty)
            elif "minor" in severities:
                severity_ranking["minor"].append(kitty)

        treatment_cats = (
            severity_ranking["severe"]
            + severity_ranking["major"]
            + severity_ranking["minor"]
        )
        if treatment_cats:
            # collate all the source info for conditions
            source_dict = ILLNESSES.copy()
            source_dict.update(INJURIES)
            source_dict.update(PERMANENT)

            for kitty in treatment_cats:
                self._use_herbs(kitty, source_dict)

        # remove expired herbs
        expired = []
        for herb_name in self.storage.copy():
            # if it's empty, don't check
            if not self.storage[herb_name]:
                continue
            # if last item is a 0, don't expire, just remove it
            if self.storage[herb_name][-1] == 0:
                self.storage[herb_name].pop(-1)
            # now check if list is long enough to expire and remove the expired herbs
            if len(self.storage[herb_name]) > self.herb[herb_name].expiration:
                expired.append(self.herb[herb_name])
                self.storage[herb_name].pop(-1)

        # add log entry to inform player of removal
        if expired:
            self.log.append(
                i18n.t(
                    "screens.med_den.expiration",
                    herbs=adjust_list_text([herb.plural_display for herb in expired]),
                )
            )

        game.herb_events_list.extend(self.log)

    def total_of_herb(self, herb) -> int:
        """
        return total int of given herb in storage and collected
        """
        total = 0
        if herb in self.storage:
            for stock in self.storage[herb]:
                total += stock
        if herb in self.collected:
            total += self.collected[herb]

        return total

    def get_overall_rating(self):
        """
        returns the rating of given supply, aka how "full" the supply is compared to clan size
        """
        if not self.entire_supply:
            return Supply.EMPTY

        lowest_herb = self.sorted_by_lowest[0]
        highest_herb = self.sorted_by_lowest[-1]
        average_count = (
            self.total_of_herb(lowest_herb) + self.total_of_herb(highest_herb)
        ) / 2

        if self.low_qualifier < average_count <= self.adequate_qualifier:
            return Supply.LOW
        if self.adequate_qualifier < average_count <= self.full_qualifier:
            return Supply.ADEQUATE
        if self.full_qualifier < average_count <= self.excess_qualifier:
            return Supply.FULL
        else:
            return Supply.EXCESS

    def get_herb_rating(self, herb):
        """
        returns the rating of given herb, aka how "full" the supply is compared to clan size
        """

        total = self.get_single_herb_total(herb)
        if not total:
            return Supply.EMPTY
        if self.low_qualifier < total <= self.adequate_qualifier:
            return Supply.LOW
        elif self.adequate_qualifier < total <= self.full_qualifier:
            return Supply.ADEQUATE
        elif self.full_qualifier < total <= self.excess_qualifier:
            return Supply.FULL
        elif self.excess_qualifier < total:
            return Supply.EXCESS

    def get_status_message(self, med_cat):
        """
        returns med den message for current herb supply status
        """
        messages: list = MESSAGES["storage_status"][self.get_overall_rating()]
        for message in messages.copy():
            if "lead_name" in message and (
                not game.clan.leader or not game.clan.leader.status.alive_in_player_clan
            ):
                messages.remove(message)
            if "dep_name" in message and (
                not game.clan.deputy or not game.clan.deputy.status.alive_in_player_clan
            ):
                messages.remove(message)

        return event_text_adjust(
            Cat=med_cat, text=choice(messages), main_cat=med_cat, clan=game.clan
        )

    def get_single_herb_total(self, herb: str) -> int:
        """
        returns int total supply of given herb
        """
        return int(
            sum([stock for stock in self.storage.get(herb, [0])])
            + self.collected.get(herb, 0)
        )

    def get_highest_herb_in_group(self, group) -> str:
        """
        returns the herb in group that has the highest supply
        """
        chosen_herb = group[0]
        highest_supply = 0

        for herb in group:
            total = self.get_single_herb_total(herb)
            if total > highest_supply:
                highest_supply = total
                chosen_herb = herb

        return chosen_herb

    def add_herb(self, herb: str, num_collected: int):
        """
        adds herb given to count for that moon
        """
        if self.collected.get(herb, []):
            self.collected[herb] += num_collected
        else:
            self.collected[herb] = num_collected

    def remove_herb(self, herb: str, num_removed: int):
        """
        removes given amount of given herb from the oldest supply first, then collection for that moon
        :param herb: herb to remove
        :param num_removed: POSITIVE number of herbs to remove
        """
        surplus = self._remove_from_storage(herb, int(num_removed))

        if surplus and self.collected.get(herb, []):
            self.collected[herb] -= surplus
            if self.collected[herb] < 0:
                self.collected[herb] = 0

    def handle_focus(self, med_cats: list, assistants: list = None):
        """
        Handles sending med cats to gather extra herbs in accordance to Clan focus
        :param med_cats: a list of medicine cat objects,
        :param assistants: a list of any non-meddies who are assisting the search for herbs
        """

        # get herbs found
        herb_list = []
        list_of_herb_strs = []
        for med in med_cats:
            if assistants:
                list_of_herb_strs, found_herbs = game.clan.herb_supply.get_found_herbs(
                    med,
                    general_amount_bonus=True,
                    specific_quantity_bonus=len(assistants),
                )
            else:
                list_of_herb_strs, found_herbs = game.clan.herb_supply.get_found_herbs(
                    med
                )
            herb_list.extend(found_herbs)

        # remove dupes
        herb_list = list(set(herb_list))
        # get display strings for herbs
        herb_strs = []
        for herb in herb_list:
            herb_strs.append(game.clan.herb_supply.herb[herb].plural_display)

        herb_list = adjust_list_text(herb_strs)

        # finish
        focus_text = i18n.t(
            "hardcoded.focus_herbs", herbs=herb_list, count=len(herb_list)
        )

        if herb_list:
            game.herb_events_list.append(
                i18n.t("screens.med_den.focus", herbs=herb_list)
            )

        return focus_text

    def get_found_herbs(
        self,
        med_cat,
        general_amount_bonus: bool = False,
        specific_quantity_bonus: float = 0,
    ) -> vars():
        """
        Takes a med cat and chooses "random" herbs for them to find. Herbs found are based on cat's skill, how badly
        the herb is needed, and herb rarity
        :param med_cat: cat object for med doing the gathering
        :param general_amount_bonus: set to True if cat should gather a boosted number of herbs
        :param specific_quantity_bonus: a specific float to multiply the gathered herb amount by
        """
        # meds with relevant skills will get a boost to the herbs they find
        # SENSE finds larger amount of herbs
        # CLEVER finds greater quantity of herbs
        primary = med_cat.skills.primary.path
        secondary = None
        if med_cat.skills.secondary:
            secondary = med_cat.skills.secondary.path
        amount_modifier = 1
        quantity_modifier = 1

        if primary == SkillPath.SENSE:
            amount_modifier = constants.CONFIG["clan_resources"]["herbs"][
                "primary_sense"
            ]
        elif primary == SkillPath.CLEVER:
            quantity_modifier = constants.CONFIG["clan_resources"]["herbs"][
                "primary_clever"
            ]

        if secondary == SkillPath.SENSE:
            amount_modifier = constants.CONFIG["clan_resources"]["herbs"][
                "secondary_sense"
            ]
        elif secondary == SkillPath.CLEVER:
            quantity_modifier = constants.CONFIG["clan_resources"]["herbs"][
                "secondary_clever"
            ]

        # list of the herbs, sorted by most need
        herb_list = self.sorted_by_need

        # dict where key is herb name and value is the quantity found of that herb
        found_herbs = {}

        # adjust weighting according to season
        weight = constants.CONFIG["clan_resources"]["herbs"][
            (
                game.clan.biome
                if not game.clan.override_biome
                else game.clan.override_biome
            ).casefold()
        ][game.clan.current_season.casefold()]

        # the amount of herb types the med has found
        amount_of_herbs = (
            choices(population=[1, 2, 3], weights=weight, k=1)[0] + amount_modifier
        )
        if general_amount_bonus:
            amount_of_herbs *= constants.CONFIG["clan_resources"]["herbs"][
                "general_amount_bonus"
            ]

        # adding herb quantity bonus
        if specific_quantity_bonus:
            quantity_modifier *= specific_quantity_bonus

        # now we find what herbs have actually been found and their quantity
        for herb in herb_list:
            if amount_of_herbs == 0:
                break

            # rarity is set to 0 if the herb can't be found in the current season
            if not self.herb[herb].get_rarity(
                game.clan.biome
                if not game.clan.override_biome
                else game.clan.override_biome,
                game.clan.current_season,
            ):
                continue

            # chance to find a herb is based on it's rarity
            if (
                randint(
                    1,
                    self.herb[herb].get_rarity(
                        game.clan.biome
                        if not game.clan.override_biome
                        else game.clan.override_biome,
                        game.clan.current_season,
                    ),
                )
                == 1
            ):
                found_herbs[herb] = int(
                    choices(population=[1, 2, 3], weights=weight, k=1)[0]
                    * quantity_modifier
                )
                amount_of_herbs -= 1

        return self.handle_found_herbs_outcomes(found_herbs)

    def handle_found_herbs_outcomes(self, found_herbs: dict = {}):
        """
        Handles adding herbs to the collection and preparing outcome for patrols
        """
        list_of_herb_strs = []
        if found_herbs:
            for herb, count in found_herbs.items():
                # add it to the collection
                self.add_herb(herb, count)

                # figure out how grammar needs to work in log
                if count > 1:
                    list_of_herb_strs.append(
                        f"{count} {self.herb[herb].plural_display}"
                    )
                else:
                    list_of_herb_strs.append(
                        f"{count} {self.herb[herb].singular_display}"
                    )

        return list_of_herb_strs, found_herbs

    def _add_collection_to_storage(self, med_cats):
        """
        Adds herbs in self.collected to self.storage and clears self.collected dict. If Clan has a CAMP skill med,
        this is where an expiration perk is added.
        """
        # add empty "clump" to all uncollected herb stores
        for herb in [
            x
            for x in self.base_herb_list
            if x not in self.collected and x in self.storage
        ]:
            self.storage.get(herb, []).insert(0, 0)

        for med in med_cats:
            # check if any meds can use a skill to store herbs better (aka, reduce time to expire)
            # we base this modifier on their path points,
            # this means there's skill variation even within cats with matching tiers
            if med.skills.primary.path == SkillPath.CAMP:
                modifier = med.skills.primary.points
            elif med.skills.secondary and med.skills.secondary.path == SkillPath.CAMP:
                modifier = med.skills.secondary.points
            else:
                continue

            better_storage = []
            for herb, count in self.collected.items():
                if not self.storage.get(herb, []):
                    # herbs can't be stored better if there isn't an existing store of that herb
                    continue

                # attempt the better storage
                if randint(1, 35 - modifier) == 1:
                    better_storage.append(herb)
                    self.storage[herb][0] += count
                    continue

            if better_storage:
                # inform player of expiration perk
                self.log.append(
                    i18n.t(
                        "screens.med_den.better_storage",
                        name=med.name,
                        herbs=adjust_list_text(
                            [self.herb[herb].plural_display for herb in better_storage]
                        ),
                    )
                )
                # remove herbs that were stored well from the collection
                for herb in better_storage:
                    self.collected.pop(herb)

        # store if no meds managed to store better
        for herb, count in self.collected.items():
            if herb in self.storage:
                self.storage.get(herb, []).insert(0, count)
            else:
                self.storage[herb] = [count]

        # clear collection dict
        self.collected = {}

    def _use_herbs(self, treatment_cat, source_dict):
        """
        utilize current herb supply on given condition
        :param treatment_cat: the cat object to be treated
        :source_dict: a full dict of all possible conditions
        """
        # collate all cat's conditions
        condition_dict = treatment_cat.injuries.copy()
        condition_dict.update(treatment_cat.illnesses)
        condition_dict.update(treatment_cat.permanent_condition)

        for name, condition in condition_dict.items():
            # get the herbs that the condition allows as treatment
            try:
                required_herbs = []
                for level in source_dict[name]["herbs"].values():
                    required_herbs.extend(level)
            except KeyError:
                print(
                    f"WARNING: {name} does not exist in it's condition dict! That condition may have been removed "
                    f"from the game. If not intentional, check that your condition is in the correct dict or report "
                    f"this as a bug. "
                )
                return

            # if condition has no herbs listed, return
            if not required_herbs:
                return

            self.in_need_of.extend(
                [x for x in required_herbs if x not in self.in_need_of]
            )

            # find the possible effects of herb for the condition
            possible_effects = []

            # effects are weighted mortality most likely, then risks, then duration
            if condition.get("mortality", 0):
                possible_effects.extend(
                    [HerbEffect.MORTALITY, HerbEffect.MORTALITY, HerbEffect.MORTALITY]
                )
            if condition.get("risks", []):
                possible_effects.extend([HerbEffect.RISK, HerbEffect.RISK])
            if condition.get("duration", 0) > 1:
                possible_effects.append(HerbEffect.DURATION)

            if not possible_effects:
                return

            chosen_effect = choice(possible_effects)

            if game.clan.game_mode == "classic":
                # classic always applies basic treatment, regardless of herb supply
                self.__apply_herb_effect(
                    treatment_cat,
                    name,
                    "cobwebs",
                    chosen_effect,
                    amount_used=1,
                    strength=1,
                )
                return

            # find which required herbs the clan currently has
            herbs_available = [
                herb for herb in required_herbs if self.get_single_herb_total(herb) > 0
            ]

            if herbs_available:
                herb_used = self.get_highest_herb_in_group(herbs_available)
                total_herb_amount = self.get_single_herb_total(herb_used)

                amount_used = randint(
                    1, total_herb_amount if total_herb_amount < 4 else 4
                )
                strength = 1
                for level, herb_list in source_dict[name]["herbs"].items():
                    if herb_used in herb_list:
                        strength = int(level)

                self.remove_herb(herb_used, amount_used)

                self.__apply_herb_effect(
                    treatment_cat, name, herb_used, chosen_effect, amount_used, strength
                )

            else:
                self.__apply_lack_of_herb(treatment_cat, name, chosen_effect)

    def _gather_herbs(self, med_cat):
        """
        finds out what herbs an individual med cat gathered during moon skip and adds those herbs to collection
        and log
        """

        list_of_herb_strs, found_herbs = self.get_found_herbs(med_cat)

        if found_herbs:
            # add found herbs to log
            self.log.append(
                i18n.t(
                    "screens.med_den.gather_success",
                    name=med_cat.name,
                    herbs=adjust_list_text(list_of_herb_strs),
                )
            )
        else:
            self.log.append(i18n.t("screens.med_den.gather_fail", name=med_cat.name))

    def _remove_from_storage(self, herb: str, needed_num: int) -> int:
        """
        removes needed_num of given herb from storage until needed_num is met or storage is empty, if storage runs out
        before needed_num is met, returns excess
        """
        while needed_num > 0 and self.storage.get(herb):
            # remove from oldest stock
            self.storage[herb][-1] -= needed_num
            # if that stock runs out, move to next oldest stock
            if self.storage[herb][-1] < 0:
                needed_num = abs(self.storage[herb][-1])
                self.storage[herb].pop(-1)

        return needed_num

    def __apply_herb_effect(
        self,
        treated_cat,
        condition: str,
        herb_used: str,
        effect: str,
        amount_used: int,
        strength: int,
    ):
        """
        applies the given effect to the treated_cat
        """

        # grab the correct condition dict so that we can modify it
        if condition in treated_cat.illnesses:
            con_info = treated_cat.illnesses[condition]
        elif condition in treated_cat.injuries:
            con_info = treated_cat.injuries[condition]
        else:
            con_info = treated_cat.permanent_condition[condition]

        amt_modifier = amount_used

        effect_message = ""
        # apply mortality effect
        if effect == HerbEffect.MORTALITY:
            con_info[effect] += (
                constants.CONFIG["clan_resources"]["herbs"]["base_mortality_effect"]
                * strength
                + amt_modifier
            )
            effect_message = i18n.t("screens.med_den.mortality_down")

        # apply duration effect
        elif effect == HerbEffect.DURATION:
            # duration doesn't get amt_modifier, as that would be far too strong an affect
            con_info[effect] -= (
                constants.CONFIG["clan_resources"]["herbs"]["base_duration_effect"]
                * strength
            )
            if con_info["duration"] < 0:
                con_info["duration"] = 0
            effect_message = i18n.t("screens.med_den.duration_down")

        # apply risk effect
        elif effect == HerbEffect.RISK:
            for risk in con_info[effect]:
                risk["chance"] += (
                    constants.CONFIG["clan_resources"]["herbs"]["base_risk_effect"]
                    * strength
                    + amt_modifier
                )
                effect_message = i18n.t("screens.med_den.risks_down")

        if game.clan.game_mode == "classic":
            # classic doesn't get logs
            return

        # create and append log message
        message = i18n.t(
            "screens.med_den.herb_used",
            herb=(
                self.herb[herb_used].plural_display
                if amount_used > 1
                else str("a ") + self.herb[herb_used].singular_display
            ),
            condition=condition,
            effect=effect_message,
        )

        message = event_text_adjust(
            Cat=treated_cat, text=message, main_cat=treated_cat, clan=game.clan
        )
        self.log.append(message)

    @staticmethod
    def __apply_lack_of_herb(treatment_cat, condition: str, effect):
        """
        if the condition is a perm condition, give some consequence for not treated it
        """
        # TODO: this kinda feels like something that should happen within a theoretical condition class...

        # only perm conditions and redcough can degenerate
        if condition in treatment_cat.illnesses and condition != "redcough":
            return
        elif condition in treatment_cat.injuries:
            return

        # grab the correct condition dict so that we can modify it
        con_info = treatment_cat.permanent_condition[condition]

        if effect == HerbEffect.RISK:
            for risk in con_info[effect]:
                risk["chance"] -= randint(2, 4)
                if risk["chance"] <= 1:
                    risk["chance"] = 2
        elif effect == HerbEffect.MORTALITY:
            con_info[effect] -= randint(2, 4)
            if con_info[effect] <= 1:
                con_info[effect] = 2


MESSAGES = None
message_lang = None


def load_med_den_messages():
    global MESSAGES, message_lang
    if message_lang == i18n.config.get("locale"):
        return
    MESSAGES = load_lang_resource("screens/med_den_messages.json")
    message_lang = i18n.config.get("locale")


load_med_den_messages()
