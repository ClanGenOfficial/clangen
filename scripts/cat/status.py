from itertools import groupby
from random import choice
from typing import TypedDict

import ujson

from scripts.cat.enums import CatRank, CatSocial, CatStanding, CatAge, CatGroup
from scripts.game_structure.game_essentials import game


class Status:
    """Holds all status information for a cat (group affiliations, ranks, location relative to others)"""

    def __init__(
            self,
            group_history: list = None,
            standing_history: list = None,
            social: CatSocial = None,
            group: CatGroup = None,
            rank: CatRank = None
    ):
        """
        Saved cats should only be passing their saved group_history and standing into this class.
        Cats that are being newly generated should use function .generate_new_status()
        """
        self.group_history = group_history if group_history else []
        """List of dicts containing the keys group, rank, and moons_as. A new dict is added anytime group or rank are
        changed."""

        self.standing_history = standing_history if standing_history else []
        """List of dicts containing the keys group, standing, and near. Standing is a chronological list of the cat's 
        standings with the group. Near is a bool with True indicating the cat is within interact-able distance of that 
        group."""

        if not self.group_history and (social or group or rank):
            self.generate_new_status(
                social=social,
                group=group,
                rank=rank
            )

    def get_status_dict(self) -> dict:

        return {
            "group_history": self.group_history,
            "standing_history": self.standing_history
        }

    def generate_new_status(
            self,
            age: CatAge = None,
            social: CatSocial = None,
            group: str = None,
            rank: CatRank = None,
    ):
        """
        Starts a group history and standing history for a newly generated cat
        :param age: The age the cat currently is.
        :param social: The social group the cat will be (rogue, clancat, loner, kittypet)
        :param group: The group the cat will be part of, default is None. If social is set to clancat and group is None,
         group will default to player clan.
        :param rank: The rank the cat holds within a group. If they have no group, then this matches their social.
        """
        self._start_group_history(
            age,
            social,
            group,
            rank,
        )

        self._start_standing()

    def _start_group_history(
            self,
            age: CatAge = None,
            social: CatSocial = None,
            group: str = None,
            rank: CatRank = None
    ):
        """
        Generates initial group history for a cat
        You HAVE to include either an age or a rank for this to work correctly
        :param age: The age of the cat.
        :param social: The social standing of the cat (rogue, loner, clancat, ect.)
        :param group: The group this cat belongs to
        :param rank: This cat's rank. If the cat is outside the Clan, this will match it's social.
        """
        new_history = {
            "group": group,
            "rank": rank,
            "moons_as": 0
        }

        if not age and not rank:
            print("WARNING: group history could not be made due to missing age and rank information")
            return

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
                rank = self.get_rank_from_age(age)

        # if not social, then social category is found via the rank
        if not social:
            if rank in CatRank.all_clancat_ranks:
                social = CatSocial.CLANCAT
            else:
                social = choice([CatSocial.ROGUE, CatSocial.LONER, CatSocial.KITTYPET])

        # group assignment via social
        # we assume a clancat is the player's as default
        # otherwise if the cat isn't a clancat, then we assume no group
        if social == CatSocial.CLANCAT and not group:
            new_history["group"] = game.clan.name

        # next, we double-check that the rank is appropriate for the social, this is mostly for loner/rogue/kittypet
        if social != SOCIAL_LOOKUP[rank]:
            # getting ranks according to social category
            possible_ranks = [
                rank for rank in SOCIAL_LOOKUP.keys()
                if SOCIAL_LOOKUP.get(rank) == social
            ]

            new_history["rank"] = choice(possible_ranks)

        self.group_history = [new_history]

    def _start_standing(self):
        """
        Generates basic standing info for a cat. If the cat is part of a group, it creates a "member" dict, else it
        creates an "outsider" standing dict for the player's clan
        """
        if self.group:
            self.standing_history = [
                {
                    "group": self.group,
                    "standing": [CatStanding.MEMBER],
                    "near": True
                }
            ]
        else:
            self.standing_history = [
                {
                    "group": game.clan.name,
                    "standing": [CatStanding.KNOWN],
                    "near": True
                }
            ]

    @property
    def social(self) -> CatSocial:
        """
        Returns the cat's current social category, aka what the cat is considered by other cats within the world
        """
        return self.social_history[-1]

    @property
    def social_history(self) -> list:
        """
        Returns a list of all social classes the cat has been part of or is
        currently part of
        """
        social_history_dupes = [SOCIAL_LOOKUP[record["rank"]] for record in self.group_history]
        return [k for k, g in groupby(social_history_dupes)]

    @property
    def group(self) -> CatGroup:
        """
        Returns the group that a cat is currently affiliated with
        """
        return self.group_history[-1]["group"]

    @property
    def all_groups(self) -> list:
        """
        Returns a list of all groups the cat has been a part of or is currently a part of
        """
        return [record["group"] for record in self.group_history]

    @property
    def rank(self) -> CatRank:
        """
        Returns the rank that a cat currently holds within their group
        """
        rank = [rank for rank in list(CatRank) if rank == self.group_history[-1]["rank"]]
        return rank[0]

    @property
    def rank_history(self) -> dict:
        """
        Returns a dict of past held ranks. Key is rank, value is moons spent as that rank.
        """
        history = {}

        for record in self.group_history:
            if record["rank"] not in history:
                history[record["rank"]] = record["moons_as"]
            else:
                history[record["rank"]] = history[record["rank"]] + record["moons_as"]

        return history

    @staticmethod
    def get_rank_from_age(age) -> CatRank:
        """
        Returns clan rank according to given age
        """
        if age == CatAge.NEWBORN:
            rank = CatRank.NEWBORN
        elif age == CatAge.KITTEN:
            rank = CatRank.KITTEN
        elif age == CatAge.ADOLESCENT:
            rank = choice(
                [CatRank.APPRENTICE, CatRank.MEDIATOR_APPRENTICE, CatRank.MEDICINE_APPRENTICE])
        elif age in [CatAge.YOUNG_ADULT, CatAge.ADULT, CatAge.SENIOR_ADULT]:
            rank = choice([CatRank.WARRIOR, CatRank.MEDICINE_CAT, CatRank.MEDIATOR])
        else:
            rank = CatRank.ELDER

        return rank

    def _modify_group(
            self,
            new_rank,
            standing_with_past_group=None,
            new_group=None
    ):
        """
        Changes group status for a cat. They can be entering, leaving, or switching their group.
        :param new_group: the name of the new group they will be joining, default None
        :param new_rank: Indicate what social category the cat is now part of
        :param standing_with_past_group: Indicate what standing the cat should have with their old group, leave None if
        they didn't have a group
        """
        if standing_with_past_group:
            self.add_standing(standing_with_past_group)

        self.group_history.append(
            {
                "group": new_group,
                "rank": new_rank,
                "moons_as": 0
            }
        )

    def add_standing(self, new_standing):
        """
        Adds given standing to cat's current group
        """
        for record in self.standing_history:
            if record["group"] == self.group:
                record["standing"].append(new_standing)

    def lost_from_group(
            self,
            new_social_status=CatSocial.KITTYPET
    ):
        """
        Removes from previous group and sets standing with that group to Lost.
        :param new_social_status: Indicates what social category the cat now belongs to (i.e. they've been taken by
        Twolegs and are now a kittypet)
        """

        self._modify_group(
            new_social_status,
            standing_with_past_group=CatStanding.LOST
        )

    def exile_from_group(self):
        """
        Removes cat from current group and changes their standing with that group to exiled.
        Cat will become a loner.
        """

        self._modify_group(
            new_rank=CatRank.LONER,
            standing_with_past_group=CatStanding.EXILED)

    def add_to_group(
            self,
            new_group,
            age,
            standing_with_past_group=None
    ):
        """
        Adds the cat to the specified group. If the cat has previously been part of this group, they will take on their
        last held rank within that group (unless it was leader or deputy). Groups are currently assumed to be Clans only,
        so if the cat has held a Clan rank within any Clan in the past, they will attempt to take on that same rank in
        the new group (unless it was leader or deputy). If no past valid past rank is found, they will gain a rank based
        off their age.
        :param new_group: The group the cat will be joining
        :param age: The current age stage of the cat
        :param standing_with_past_group: If leaving a group to join the new one, this should be used to indicate how the
        last group views the cat (exiled, lost, ect.)
        """
        new_rank = None

        # adding a cat who has been in the group in the past, they will take their old rank if possible
        if self.is_former_clancat():
            new_rank = self.find_prior_clan_rank()
            if new_rank in [CatRank.LEADER, CatRank.DEPUTY]:
                new_rank = self.get_rank_from_age(age)

        self._modify_group(
            new_rank=new_rank,
            standing_with_past_group=standing_with_past_group,
            new_group=new_group
        )

    def get_standing_with_group(self, group: CatGroup) -> list[CatStanding]:
        """
        Returns the list of standings a cat has for the given group.
        """
        standing_list = []
        for entry in self.standing_history:
            if entry["group"] == group:
                standing_list = entry
                break

        return standing_list

    def move_to_afterlife(self):
        """
        Changes a cat's group into the appropriate afterlife
        """

        # if we have an outsider who has never been a clancat, they go to the unknown residence
        if self.is_outsider() and not self.is_former_clancat():
            self._modify_group(
                new_rank=self.rank,
                new_group=CatGroup.UNKNOWN_RESIDENCE
            )
            return

        # meanwhile clan cats go wherever their guide points them
        if self.is_former_clancat():
            clan_rank = self.find_prior_clan_rank()
        else:
            clan_rank = self.rank

        self._modify_group(
            new_rank=clan_rank,
            new_group=game.clan.instructor.status.group,
            standing_with_past_group=CatStanding.MEMBER
        )

    def change_rank(self, new_rank):
        """
        Changes the cats rank to the new_rank
        """
        self.group_history.append(
            {
                "group": self.group,
                "rank": new_rank,
                "moons_as": 0
            }
        )

    def _change_outsider_social(self, new_social):
        if self.group:
            self._modify_group(
                new_social,
                standing_with_past_group=CatStanding.LEFT
            )
        else:
            self.group_history.append(
                {
                    "group": None,
                    "rank": new_social,
                    "moons_as": 0
                }
            )

    def find_prior_clan_rank(self, clan=None):
        """
        Finds the last clan rank held of a current outsider
        :param clan: pass the name of a clan to only return the cat's prior rank within that clan. Default is None, if
        None then the last rank within any Clan will be returned.
        """
        if clan:
            past_ranks = [record["rank"] for record in self.group_history if record["group"] == clan]
        else:
            past_ranks = [rank for rank in self.rank_history.keys()
                          if rank not in [CatRank.LONER,
                                          CatRank.KITTYPET,
                                          CatRank.ROGUE]]

        return past_ranks[-1]

    def in_player_clan(self) -> bool:
        """
        Returns True if the cat is currently part of the player clan.
        """
        return True if self.group == CatGroup.PLAYER_CLAN else False

    def is_outsider(self) -> bool:
        """
        Returns True if the cat isn't part of a clan.
        """

        return True if self.social != CatSocial.CLANCAT else False

    def is_clancat(self) -> bool:
        """
        Returns True if the cat is currently a clancat in any clan.
        """
        return True if self.social == CatSocial.CLANCAT else False

    def is_former_clancat(self) -> bool:
        """
        Returns True if the cat has been part of any clan in the past, but is not currently a clancat.
        """

        return True if CatSocial.CLANCAT in self.social_history and self.social != CatSocial.CLANCAT else False

    def is_lost(self) -> bool:
        """
        Returns True if the cat is considered "lost" by a group.
        """
        for entry in self.standing_history:
            if CatStanding.LOST in entry["standing"]:
                return True

        return False

    def is_dead(self) -> bool:
        """
        Returns True if the cat is currently dead
        """
        return True if self.group in [CatGroup.DARK_FOREST,
                                      CatGroup.UNKNOWN_RESIDENCE,
                                      CatGroup.STAR_CLAN] else False

    def is_exiled(self, group):
        """
        Returns True if the cat is currently exiled from the given group.
        """
        standing = self.get_standing_with_group(group)

        if standing[-1] == CatStanding.EXILED:
            return True

        return False


class StatusDict(TypedDict, total=False):
    """
    Dict containing:

    "group_history": list[dict],
    "standing_history": list[dict],
    "social": CatSocialEnum,
    "group": str
    "rank": CatRankEnum

    Dict does not need to contain all keys.
    """
    group_history: list[dict]
    standing_history: list[dict]
    social: CatSocial
    group: str
    rank: CatRank


with open(
        "resources/dicts/social_lookup.json", "r", encoding="utf-8"
) as read_file:
    SOCIAL_LOOKUP = ujson.loads(read_file.read())
