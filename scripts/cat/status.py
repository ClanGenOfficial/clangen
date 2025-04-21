from itertools import groupby
from random import choice

import ujson

from scripts.cat.enums import CatRankEnum, CatSocialEnum, CatStandingEnum
from scripts.game_structure.game_essentials import game


class Status:
    """Holds all status information for a cat (group affiliations, ranks, location relative to others)"""

    def __init__(
            self,
            group_history: list = None,
            standing_history: list = None,
            social: CatSocialEnum = None,
            group: str = None,
            rank: CatRankEnum = None,
    ):
        """
        Saved cats should only be passing their saved group_history and standing into this class.
        Cats that are being newly generated should utilize social/group/rank params to create their information.
        """
        self.group_history = group_history if group_history else []
        self.standing_history = standing_history if standing_history else []

        if not self.group_history:
            self.start_group_history(
                social,
                group,
                rank,
            )

        if not self.standing_history:
            self.start_standing()

    def start_group_history(
            self,
            social: CatSocialEnum = None,
            group: str = None,
            rank: CatRankEnum = None
    ):
        """
        Generates initial group history for a cat
        """
        new_history = {
            "group": group,
            "rank": rank,
            "moons_as": 0
        }

        # if not social, then social category is found via the rank
        if not social:
            if rank in CatRankEnum.all_clancat_ranks:
                social = CatSocialEnum.CLANCAT
            else:
                social = choice([CatSocialEnum.ROGUE, CatSocialEnum.LONER, CatSocialEnum.KITTYPET])

        # group assignment via social
        # we assume a clancat is the player's as default
        # otherwise if the cat isn't a clancat, then we assume no group
        if social == CatSocialEnum.CLANCAT and not group:
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

    def start_standing(self):
        """
        Generates basic standing info for a cat. If the cat is part of a group, it creates a "member" dict, else it
        creates an "outsider" standing dict for the player's clan
        """
        if self.group:
            self.standing_history = [
                {
                    "group": self.group,
                    "standing": [CatStandingEnum.MEMBER],
                    "near": True
                }
            ]
        else:
            self.standing_history = [
                {
                    "group": game.clan.name,
                    "standing": [CatStandingEnum.KNOWN],
                    "near": True
                }
            ]

    @property
    def social(self) -> str:
        """
        Returns the cat's current social category, aka what the cat is considered by other cats within the world
        """
        return self.social_history[-1]

    @property
    def social_history(self) -> list:
        """
        Returns a chronological (first to last/current) list of all social classes the cat has been part of or is
        currently part of
        """
        social_history_dupes = [SOCIAL_LOOKUP[record["rank"]] for record in self.group_history]
        return [k for k, g in groupby(social_history_dupes)]

    @property
    def group(self) -> str:
        """
        Returns the group that a cat is currently affiliated with
        """
        return self.group_history[-1]["group"]

    @property
    def rank(self) -> str:
        """
        Returns the rank that a cat currently holds within their group
        """
        return self.group_history[-1]["rank"]

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

    def _remove_from_group(
            self,
            new_social: CatSocialEnum,
            new_standing: CatStandingEnum
    ):
        """
        Removes a cat from their group and updates that group's standing
        :param new_social: Indicate what social category the cat is now part of
        :param new_standing: Indicate what standing the cat should have with their old group
        """
        for record in self.standing_history:
            if record["group"] == self.group:
                record["standing"].append(new_standing)

        # for now this can't move the cat from one group into another group (like if playerClan kit was stolen by
        # another Clan), we don't really have the full infrastructure for that kind of thing, but it's definitely
        # something we could do in the future
        self.group_history.append(
            {
                "group": None,
                "rank": new_social,
                "moons_as": 0
            }
        )

    def become_lost(
            self,
            new_social_status: CatSocialEnum = CatSocialEnum.KITTYPET
    ):
        """
        Updates a cat's status to lost
        :param new_social_status: Indicates what social category the cat now belongs to (i.e. they've been taken by
        Twolegs and are now a kittypet)
        """

        self._remove_from_group(
            new_social_status,
            new_standing=CatStandingEnum.LOST
        )

    def become_exiled(self):
        """
        updates a cat's status to exiled
        """

        self._remove_from_group(
            CatSocialEnum.LONER,
            new_standing=CatStandingEnum.EXILED)

    def _change_outsider_social(
            self,
            new_social
    ):
        if self.group:
            self._remove_from_group(
                new_social,
                new_standing=CatStandingEnum.LEFT
            )
        else:
            self.group_history.append(
                {
                    "group": None,
                    "rank": new_social,
                    "moons_as": 0
                }
            )

    def become_loner(self):
        """
        Turns a cat into a loner. If they were part of a group, they willingly leave it. If they are being forcibly
        removed, use .become_lost instead
        """

        self._change_outsider_social(CatSocialEnum.LONER)

    def become_rogue(self):
        """
        Turns a cat into a rogue. If they were part of a group, they willingly leave it. If they are being forcibly
        removed, use .become_lost instead
        """

        self._change_outsider_social(CatSocialEnum.ROGUE)

    def become_kittypet(self):
        """
        Turns a cat into a rogue. If they were part of a group, they willingly leave it. If they are being forcibly
        removed, use .become_lost instead
        """

        self._change_outsider_social(CatSocialEnum.ROGUE)

    def change_rank(
            self,
            new_rank
    ):
        """
        Changes the cat's rank within it's group
        :param new_rank: The new rank the cat will become
        """
        pass


with open(
        "resources/dicts/social_lookup.json", "r", encoding="utf-8"
) as read_file:
    SOCIAL_LOOKUP = ujson.loads(read_file.read())
