import os
import unittest

from scripts.cat.enums import CatRank, CatSocial, CatGroup
from scripts.cat.status import StatusDict
from scripts.clan import Clan
from scripts.game_structure import game
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Cat, Relationship
from scripts.events_module.relationship import romantic_events


class MovingOn(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = Cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        self.cat1 = Cat(moons=100, disable_random=True)
        self.cat2 = Cat(moons=100, disable_random=True)

        self.cat1.set_mate(self.cat2)

    def test_dead_moon_wait(self):
        """
        Check if a cat will move on too soon from dead mate
        """
        self.cat2.die()
        romantic_events._handle_moving_on(self.cat1, disable_random=True)
        self.assertIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should still be a mate of cat1"
        )

    def test_missing_moon_wait(self):
        """
        Check if the cat will move on too soon from missing mate
        """
        self.cat2.status.leave_group(CatSocial.ROGUE)
        romantic_events._handle_moving_on(self.cat1, disable_random=True)

        self.assertIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should still be a mate of cat1"
        )

    def test_grief(self):
        """
        Check if the cat will move on while grieving
        """
        self.cat2.die()
        self.cat1.get_ill("grief stricken")
        romantic_events._handle_moving_on(self.cat1, disable_random=True)

        self.assertIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should still be a mate of cat1"
        )

    def test_dead_move_on(self):
        """
        Check if the mate will move on from dead mate when they are meant to
        """
        self.cat2.die()
        self.cat2.status.change_current_moons_as(4)
        romantic_events._handle_moving_on(self.cat1, disable_random=True)

        self.assertNotIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should no longer be a mate of cat1"
        )

    def test_missing_move_on(self):
        """
        Check if the mate will move on from missing mate when they are meant to
        """
        self.cat2.status.leave_group(CatSocial.ROGUE)
        self.cat2.status.change_current_moons_as(4)
        romantic_events._handle_moving_on(self.cat1, disable_random=True)

        self.assertNotIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should no longer be a mate of cat1"
        )


class BreakingUp(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = Cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        self.cat1 = Cat(moons=100, disable_random=True)
        self.cat2 = Cat(moons=100, disable_random=True)

        self.cat1.set_mate(self.cat2)

    def test_breaking_up(self):
        # check breaking up
        pass


class Confessing(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = Cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        self.cat1 = Cat(moons=100, disable_random=True)
        self.cat2 = Cat(moons=100, disable_random=True)

        self.cat1.set_mate(self.cat2)

    def test_confession(self):
        # check confessing
        pass


class MutualLove(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = Cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        self.cat1 = Cat(moons=100, disable_random=True)
        self.cat2 = Cat(moons=100, disable_random=True)

        self.cat1.set_mate(self.cat2)

    def test_mutual_mates(self):
        # check mutual mating
        pass
