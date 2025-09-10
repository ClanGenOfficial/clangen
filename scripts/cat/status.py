from collections import defaultdict
from itertools import groupby
from random import choice
from typing import TypedDict, Optional, List, Dict

from scripts.cat.enums import CatRank, CatSocial, CatStanding, CatAge, CatGroup
from scripts.game_structure import game


class Status:
    """Holds all status information for a cat (group affiliations, ranks, location relative to others)"""

    social_lookup = {
        CatRank.NEWBORN: CatSocial.CLANCAT,
        CatRank.KITTEN: CatSocial.CLANCAT,
        CatRank.APPRENTICE: CatSocial.CLANCAT,
        CatRank.MEDICINE_APPRENTICE: CatSocial.CLANCAT,
        CatRank.MEDIATOR_APPRENTICE: CatSocial.CLANCAT,
        CatRank.WARRIOR: CatSocial.CLANCAT,
        CatRank.MEDICINE_CAT: CatSocial.CLANCAT,
        CatRank.MEDIATOR: CatSocial.CLANCAT,
        CatRank.DEPUTY: CatSocial.CLANCAT,
        CatRank.LEADER: CatSocial.CLANCAT,
        CatRank.ELDER: CatSocial.CLANCAT,
        CatRank.LONER: CatSocial.LONER,
        CatRank.ROGUE: CatSocial.ROGUE,
        CatRank.KITTYPET: CatSocial.KITTYPET,
    }
    """A dict of ranks and their corresponding social status"""

    def __init__(
        self,
        group_history: list = None,
        standing_history: list = None,
        social: CatSocial = None,
        group_ID: str = None,
        rank: CatRank = None,
        age: CatAge = None,
    ):
        """
        Saved cats should only be passing their saved group_history and standing into this class.
        Cats that are being newly generated will default to the player clan and a rank appropriate for age.  If you'd
        like to have more control, use the social, group, and rank params. If you don't know the rank, include age, or
        vice versa
        """

        self.group_history = group_history if group_history else []
        """List of dicts containing the keys: group, rank, and moons_as. A new dict is added whenever group or rank are
        changed."""

        self.standing_history = standing_history if standing_history else []
        """List of dicts containing the keys: group, standing, and near. Standing is a chronological list of the cat's 
        standings with the group. Near is a bool with True indicating the cat is within interact-able distance of that 
        group."""

        for entry in self.group_history:
            self._convert_old_group_saves(entry)
            # converting strs to enums
            entry["rank"] = CatRank(entry["rank"])

        for entry in self.standing_history:
            self._convert_old_group_saves(entry)
            # converting strs to enums
            standing_copy = entry["standing"].copy()
            entry["standing"].clear()
            for standing in standing_copy:
                entry["standing"].append(CatStanding(standing))

        # just some extra checks in case a str snuck in
        if rank or social:
            rank, social = self.get_enums(rank, social, age)

        # if no group_history was given, we'll see if any other info was given that we can build it with
        if not self.group_history and (rank or age):
            self.generate_new_status(
                social=social, group_ID=group_ID, rank=rank, age=age
            )
        # if we didn't get any information at all, we're gonna default to a warrior
        elif not self.group_history and not rank and not age:
            self.generate_new_status(rank=CatRank.WARRIOR)

        # really we should never be missing a standing_history at this point, but just in case
        if self.group_history and not self.standing_history:
            self._start_standing()

    # SAVE/LOAD
    @staticmethod
    def _convert_old_group_saves(entry):
        # converting older group saves to the new group_IDs
        if not entry["group"]:
            entry["group"] = None
            return
        if not entry["group"].isdigit():
            for ID, group_type in game.used_group_IDs.items():
                if entry["group"] == group_type:
                    entry["group"] = ID
                    break
            # since we actually can't access other_clan IDs until after cats are loaded, we'll extrapolate the *probable* ID based off the old enum.
            # this is close enough, and frankly save conversion accuracy here isn't a priority
            if not entry["group"].isdigit():
                old_enum_number = [x for x in entry["group"] if x.isdigit()][0]
                entry["group"] = str(int(old_enum_number) + 4)

    def get_enums(self, rank=None, social=None, age=None) -> tuple[CatRank, CatSocial]:
        """
        this is mostly to catch the old status strings like exiled and lost
        """
        if rank and not isinstance(rank, CatRank):
            if rank.casefold() in ("exiled", "lost", "former clancat"):
                if age:
                    rank = self.get_rank_from_age(age)
                else:  # god this should never happen, but I'm paranoid
                    rank = CatRank.WARRIOR
            rank = CatRank(rank)
        if social and not isinstance(social, CatSocial):
            if social.casefold() == "former clancat":
                social = CatSocial.CLANCAT
            social = CatSocial(social)
        if rank and not isinstance(rank, CatRank):
            raise TypeError(f"{rank} is not a valid rank")
        if social and not isinstance(social, CatSocial):
            raise TypeError(f"{social} is not a valid social")

        return rank, social

    def get_status_dict(self) -> dict:
        """
        Returns group_history and standing_history bundled together as a dict. This is the format we should use to save
        the status information for a cat.
        """

        return {
            "group_history": self.group_history,
            "standing_history": self.standing_history,
        }

    def generate_new_status(
        self,
        age: CatAge = None,
        social: CatSocial = None,
        group_ID: str = None,
        rank: CatRank = None,
        disable_random=False,
    ):
        """
        Starts a group history and standing history for a newly generated cat. You MUST include either age or rank.
        :param age: The age the cat currently is.
        :param social: The social group the cat will be (rogue, clancat, loner, kittypet)
        :param group_ID: The group_ID for the group the cat will be part of, default is None. If social is set to clancat and group is None,
         group will default to player clan.
        :param rank: The rank the cat holds within a group. If they have no group, then this matches their social.
        :param disable_random: Removes randomness and ensures repeatable results for each age group.
        """
        self._start_group_history(age, social, group_ID, rank, disable_random)

        self._start_standing()

    def _start_group_history(
        self,
        age: CatAge = None,
        social: CatSocial = None,
        group_ID: str = None,
        rank: CatRank = None,
        disable_random=False,
    ):
        """
        Generates initial group history for a cat
        You HAVE to include either an age or a rank for this to work correctly
        :param age: The age of the cat.
        :param social: The social standing of the cat (rogue, loner, clancat, ect.)
        :param group_ID: The group_ID for the group this cat belongs to
        :param rank: This cat's rank. If the cat is outside the Clan, this will match it's social.
        :param disable_random: If true, will provide deterministic outputs
        """
        new_history = {"group": group_ID, "rank": rank, "moons_as": 0}

        if not age and not rank:
            raise ValueError(
                "WARNING: group history could not be made due to missing age and rank information"
            )

        # if no rank, we find rank according to age
        if not rank:
            if social and social != CatSocial.CLANCAT:
                if social == CatSocial.ROGUE:
                    rank = CatRank.ROGUE
                elif social == CatSocial.LONER:
                    rank = CatRank.LONER
                elif social == CatSocial.KITTYPET:
                    rank = CatRank.KITTYPET
            else:
                rank = self.get_rank_from_age(age, disable_random)

            new_history["rank"] = rank

        # if not social, then social category is found via the rank
        if not social:
            if rank and rank.is_any_clancat_rank():
                social = CatSocial.CLANCAT
            else:
                social = CatSocial(rank)

        # group assignment via social
        # we assume a clancat is the player's as default
        # otherwise if the cat isn't a clancat, then we assume no group
        if social == CatSocial.CLANCAT and not group_ID:
            new_history["group"] = CatGroup.PLAYER_CLAN_ID

        # next, we double-check that the rank is appropriate for the social, this is mostly for loner/rogue/kittypet
        if social != self.social_lookup[rank]:
            # getting ranks according to social category
            possible_ranks = [
                rank
                for rank in self.social_lookup.keys()
                if self.social_lookup.get(rank) == social
            ]

            if disable_random and social == CatSocial.CLANCAT:
                new_history["rank"] = CatRank.WARRIOR
            else:
                new_history["rank"] = choice(possible_ranks)

        self.group_history = [new_history]

    def _start_standing(self):
        """
        Generates basic standing info for a cat. If the cat is part of a group, it creates a MEMBER dict, else it
        creates a KNOWN standing dict for the player's clan.
        """
        if self.group_ID:
            self.standing_history = [
                {"group": self.group_ID, "standing": [CatStanding.MEMBER], "near": True}
            ]

        if not self.get_standing_with_group(CatGroup.PLAYER_CLAN_ID):
            self.standing_history = [
                {
                    "group": CatGroup.PLAYER_CLAN_ID,
                    "standing": [CatStanding.KNOWN],
                    "near": True,
                }
            ]

    # PROPERTIES
    @property
    def social(self) -> CatSocial:
        """
        Returns the cat's current social category, aka what the cat is considered by other cats within the world
        """
        return self.all_socials[-1]

    @property
    def all_socials(self) -> list:
        """
        Returns a list of all social classes the cat has been part of or is currently part of.
        """
        social_history_dupes = [
            self.social_lookup[record["rank"]] for record in self.group_history
        ]
        social_groups = [k for k, g in groupby(social_history_dupes)]

        return social_groups

    @property
    def group(self) -> CatGroup:
        """
        Returns the group type that a cat is currently affiliated with.
        """
        group = game.used_group_IDs.get(self.group_ID)
        if not group:
            group = CatGroup.NONE
        return group

    @property
    def group_ID(self) -> str:
        """
        Return the ID of the group this cat belongs to.
        """
        return self.group_history[-1]["group"]

    @property
    def all_groups(self) -> list:
        """
        Returns a list of all groups the cat has been a part of or is currently a part of.
        """
        groups = []
        for record in self.group_history:
            if record["group"] not in groups:
                groups.append(record["group"])

        return groups

    @property
    def rank(self) -> CatRank:
        """
        Returns the rank that a cat currently holds within their group.
        """
        return CatRank(self.group_history[-1]["rank"])

    @property
    def all_ranks(self) -> dict:
        """
        Returns a dict of past held ranks. Key is rank, value is moons spent as that rank.
        """
        history = defaultdict(int)

        for record in self.group_history:
            history[record["rank"]] += record["moons_as"]

        return history

    @property
    def alive_in_player_clan(self) -> bool:
        """
        Returns True if the cat is currently part of the player clan.
        """
        return self.group == CatGroup.PLAYER_CLAN

    @property
    def is_outsider(self) -> bool:
        """
        Returns True if the cat isn't part of a clan.
        """
        return self.social != CatSocial.CLANCAT

    @property
    def is_clancat(self) -> bool:
        """
        Returns True if the cat is currently a clancat in any clan.
        """
        return self.social == CatSocial.CLANCAT

    @property
    def is_former_clancat(self) -> bool:
        """
        Returns True if the cat has been part of any clan in the past, but is not currently a clancat.
        """
        return (
            CatSocial.CLANCAT in self.all_socials and self.social != CatSocial.CLANCAT
        )

    @property
    def is_other_clancat(self) -> bool:
        """
        Returns True if the cat is a clancat but isn't part of the player_clan. If the cat is a dead clancat, returns True if their last living Clan wasn't the player_clan.
        """
        dead_player_clan = (
            self.group
            and self.group.is_afterlife()
            and self.get_last_living_group() == CatGroup.PLAYER_CLAN_ID
        )
        living_player_clan = self.alive_in_player_clan

        return not dead_player_clan and not living_player_clan and self.is_clancat

    @property
    def is_leader(self) -> bool:
        return self.rank == CatRank.LEADER

    @staticmethod
    def get_rank_from_age(age: CatAge, disable_random=False) -> CatRank:
        """
        Returns clan rank according to given age
        :param age: Desired age
        :param disable_random: If true, defaults to apprentice and warrior instead of choices
        """
        if age == CatAge.NEWBORN:
            return CatRank.NEWBORN
        elif age == CatAge.KITTEN:
            return CatRank.KITTEN
        elif age == CatAge.ADOLESCENT:
            return (
                CatRank.APPRENTICE
                if disable_random
                else choice(
                    [
                        CatRank.APPRENTICE,
                        CatRank.MEDIATOR_APPRENTICE,
                        CatRank.MEDICINE_APPRENTICE,
                    ]
                )
            )
        elif age in (CatAge.YOUNG_ADULT, CatAge.ADULT, CatAge.SENIOR_ADULT):
            return (
                CatRank.WARRIOR
                if disable_random
                else choice([CatRank.WARRIOR, CatRank.MEDICINE_CAT, CatRank.MEDIATOR])
            )
        else:
            return CatRank.ELDER

    # MODIFY INFO
    def change_current_moons_as(self, new_moons_as: int):
        """
        Used to adjust the cat's "moons_as" their current rank. This is meant mostly for use in adjusting a newly
        created cat's value to give the illusion that they have existed in the world for longer. If you want to
        increment their current moons_as by 1, use increase_current_moons_as()
        """
        self.group_history[-1].update({"moons_as": new_moons_as})

    def increase_current_moons_as(self):
        """
        Use to increment their current group/rank moons_as by 1
        """
        self.group_history[-1]["moons_as"] += 1

    def _modify_group(
        self,
        new_rank: CatRank,
        standing_with_past_group: CatStanding = None,
        new_group_ID: str = None,
    ):
        """
        Changes group status for a cat. They can be entering, leaving, or switching their group.
        :param new_group_ID: the ID of the new group they will be joining, default None
        :param new_rank: Indicate what rank the cat should take, if they aren't joining a new group then this should
        match their social.
        :param standing_with_past_group: Indicate what standing the cat should have with their old group, leave None if
        they didn't have a group
        """
        if standing_with_past_group:
            self.change_standing(standing_with_past_group)

        self.group_history.append(
            {"group": new_group_ID, "rank": new_rank, "moons_as": 0}
        )

        # add member standing for new group
        self.change_standing(CatStanding.MEMBER)

    def change_standing(self, new_standing: CatStanding, group_ID: str = None):
        """
        Update the given group with the given standing. If no group is given, the new standing will be added to the
        cat's current group.
        """
        # can't change the standing if we have no group to change
        if not group_ID and not self.group:
            return

        if not group_ID:
            group_ID = self.group_ID

        for record in self.standing_history:
            if record["group"] == group_ID:
                duplicates = record["standing"].count(new_standing)
                if duplicates > 1:
                    removed_index = record["standing"].index(new_standing)
                    record["standing"].pop(removed_index)
                record["standing"].append(new_standing)
                return

        self.standing_history.append(
            {"group": group_ID, "standing": [new_standing], "near": True}
        )

    def become_lost(self, new_social_status: CatSocial = CatSocial.KITTYPET):
        """
        Removes from previous group and sets standing with that group to Lost.
        :param new_social_status: Indicates what social category the cat now belongs to (i.e. they've been taken by
        Twolegs and are now a kittypet)
        """
        # find matching rank enum
        rank = CatRank(new_social_status)

        self._modify_group(rank, standing_with_past_group=CatStanding.LOST)

    def exile_from_group(self):
        """
        Removes cat from current group and changes their standing with that group to be exiled.
        Cat will become a loner.
        """

        self._modify_group(
            new_rank=CatRank.LONER, standing_with_past_group=CatStanding.EXILED
        )

    def add_to_group(
        self,
        new_group_ID: str,
        age: CatAge = None,
        standing_with_past_group: CatStanding = CatStanding.KNOWN,
    ):
        """
        Adds the cat to the specified group. If the cat has previously been part of this group, they will take on their
        last held rank within that group (unless it was leader or deputy). Groups are currently assumed to be Clans
        only, so if the cat has held a Clan rank within any Clan in the past, they will attempt to take on that same
        rank in the new group (unless it was leader or deputy). If no past valid past rank is found, they will gain a
        rank based off their age.
        :param new_group_ID: The group_ID for the group the cat will be joining
        :param age: The current age stage of the cat, required if cat is going into a group that will require a rank
        change
        :param standing_with_past_group: If leaving a group to join the new one, this should be used to indicate how the
        last group views the cat (exiled, lost, ect.) Defaults to KNOWN if cat was in a group.
        """
        new_group_type = game.used_group_IDs[new_group_ID]
        # if they weren't in a group, they don't need to update standing
        if not self.group:
            standing_with_past_group = None

        # if we're moving an afterlife cat, they don't change rank
        if self.group.is_afterlife():
            new_rank = self.rank
        # adding a cat who has been in a clan in the past, they will take their old rank if possible
        elif self.is_former_clancat and not self.group.is_afterlife():
            new_rank = self.find_prior_clan_rank()
            # we don't need to change leaders and deps if they're going to an afterlife
            if (
                new_rank in (CatRank.LEADER, CatRank.DEPUTY)
                and not new_group_type.is_afterlife()
            ):
                if age == CatAge.SENIOR:
                    new_rank = CatRank.ELDER
                else:
                    new_rank = CatRank.WARRIOR
        else:
            new_rank = self.rank

        if new_group_type.is_any_clan_group() and not new_rank.is_any_clancat_rank():
            new_rank = self.get_rank_from_age(age)

        self._modify_group(
            new_rank=new_rank,
            standing_with_past_group=standing_with_past_group,
            new_group_ID=new_group_ID,
        )

    def send_to_afterlife(self, target_ID: str = None):
        """
        Changes a cat's group into the appropriate afterlife
        :param target_ID: Use this to specify a certain afterlife, if unused a clancat (or a former clancat) will match
        their guide's afterlife, while an outsider will go to the unknown residence.
        """
        # if we have a specific afterlife to send them to
        if target_ID:
            self.add_to_group(
                new_group_ID=target_ID,
            )
            return

        # if we have an outsider who has never been a clancat, they go to the unknown residence
        if self.is_outsider and (
            self.is_exiled(CatGroup.PLAYER_CLAN_ID) or not self.is_former_clancat
        ):
            self.add_to_group(new_group_ID=CatGroup.UNKNOWN_RESIDENCE_ID)
            return

        # meanwhile clan cats go wherever their guide points them
        if game.clan:
            self.add_to_group(new_group_ID=game.clan.instructor.status.group_ID)
        else:
            self.add_to_group(new_group_ID=CatGroup.STARCLAN_ID)

    def _change_rank(self, new_rank: CatRank):
        """
        Changes the cats rank to the new_rank. Generally you shouldn't use just this to change a cat's rank!
        cat.rank_change() should typically be called instead, since it will handle mentor switches and other complex
        changes.
        """
        saved_group = None
        # checks that we don't add a duplicate group/rank pairing
        if self.group_history:
            last_entry = self.group_history[-1]
            # remove 0 moons history to avoid save bloat
            if len(self.group_history) > 1 and last_entry["moons_as"] == 0:
                if self.group_ID == last_entry["group"]:
                    saved_group = last_entry["group"]
                self.group_history.remove(last_entry)
                last_entry = self.group_history[-1]
            if last_entry["group"] == self.group_ID and last_entry["rank"] == new_rank:
                return
        group_ID = self.group_ID if not saved_group else saved_group
        self.group_history.append({"group": group_ID, "rank": new_rank, "moons_as": 0})

    def change_group_nearness(self, group_ID: str):
        """
        Flips the "near" bool of the given group.
        """
        for entry in self.standing_history:
            if entry.get("group") == group_ID:
                if entry["near"]:
                    entry["near"] = not entry["near"]

    # RETRIEVE INFO
    def get_standing_with_group(self, group_ID: str) -> Optional[list[CatStanding]]:
        """
        Returns the list of standings a cat has for the given group.
        """
        for entry in self.standing_history:
            if entry["group"] == group_ID:
                return entry["standing"]
        return []

    def find_prior_clan_rank(self, clan_ID: str = None) -> CatRank:
        """
        Finds the last held clan rank of a current outsider
        :param clan_ID: pass the ID of a clan to only return the cat's prior rank within that clan. Default is None, if
        None then the last rank within any Clan will be returned.
        """
        if clan_ID:
            past_ranks = [
                record["rank"]
                for record in self.group_history
                if record["group"] == clan_ID
            ]
        else:
            past_ranks = [
                rank
                for rank in self.all_ranks.keys()
                if rank not in [CatRank.LONER, CatRank.KITTYPET, CatRank.ROGUE]
            ]

        return past_ranks[-1]

    def get_last_living_group(self) -> Optional[str]:
        """
        Returns the last group this cat belonged to before death. If the cat had no group before dying, this will return None.
        """
        history = self.group_history.copy()
        history.reverse()

        for entry in history:
            group_type = game.used_group_IDs.get(entry["group"])
            if group_type and not group_type.is_afterlife():
                return entry["group"]

        return None

    def is_lost(self, group_ID: str = None) -> bool:
        """
        Returns True if the cat is considered "lost" by a group.
        :param group_ID: use this to specify a certain group to check lost status against
        """
        for entry in self.standing_history:
            if group_ID and entry["group"] != group_ID:
                continue
            if CatStanding.LOST == entry["standing"][-1]:
                return True

        return False

    def is_exiled(self, group_ID: str = None) -> bool:
        """
        Returns True if cat is exiled from a group.
        :param group_ID: Use to specify the group to check exiled status against. If no group is given, this will return True if the cat is exiled from any group.
        """
        # if no group given
        if not group_ID:
            for entry in self.standing_history:
                if CatStanding.EXILED in entry["standing"]:
                    return True
            return False

        # if group given
        standing = self.get_standing_with_group(group_ID)

        return standing and standing[-1] == CatStanding.EXILED

    def is_near(self, group_ID: str) -> bool:
        """
        Returns True if the cat is near the specified group
        :param group_ID: The group the cat is or is not near
        """
        for entry in self.standing_history:
            if entry.get("group") == group_ID and entry.get("near"):
                return True

        return False


class StatusDict(TypedDict, total=False):
    """
    Dict containing:

    "group_history": list[dict],
    "standing_history": list[dict],
    "social": CatSocial,
    "group": CatGroup
    "rank": CatRank
    "age": CatAge

    Dict does not need to contain all keys. However, if you have no group history, then you must include a rank or age
    """

    group_history: Optional[List[Dict]]
    standing_history: Optional[List[Dict]]
    social: Optional[CatSocial]
    group_ID: Optional[str]
    rank: Optional[CatRank]
    age: Optional[CatAge]
