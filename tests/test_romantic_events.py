import os
import unittest
from random import Random

from scripts.cat.factories.test_cat_factory import TestCatFactory

from scripts.cat.enums import CatRank, CatSocial, CatGroup
from scripts.cat.factories.typed_dicts import StatusDict
from scripts.cat.microservices.conditions import get_ill
from scripts.clan import Clan
from scripts.game_structure import game
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

from scripts.cat.cats import Relationship
from scripts.events_module.relationship import romantic_events


cat_factory = TestCatFactory()


class MovingOn(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = cat_factory.create_cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        self.cat1 = cat_factory.create_cat(moons=100)
        self.cat2 = cat_factory.create_cat(moons=100)

        self.cat1.set_mate(self.cat2)

    def test_dead_moon_wait(self):
        """
        Check if a cat will move on too soon from dead mate
        """
        self.cat2.die()
        romantic_events._handle_moving_on(self.cat1)
        self.assertIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should still be a mate of cat1"
        )

    def test_missing_moon_wait(self):
        """
        Check if the cat will move on too soon from missing mate
        """
        self.cat2.status.leave_group(CatSocial.ROGUE)
        romantic_events._handle_moving_on(self.cat1)

        self.assertIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should still be a mate of cat1"
        )

    def test_grief(self):
        """
        Check if the cat will move on while grieving
        """
        self.cat2.die()
        get_ill(cat=self.cat1, illness_name="grief stricken")
        romantic_events._handle_moving_on(self.cat1)

        self.assertIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should still be a mate of cat1"
        )

    def test_dead_move_on(self):
        """
        Check if the mate will move on from dead mate when they are meant to
        """
        self.cat2.die()
        self.cat2.status.change_current_moons_as(4)
        romantic_events._handle_moving_on(self.cat1)

        self.assertNotIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should no longer be a mate of cat1"
        )

    def test_missing_move_on(self):
        """
        Check if the mate will move on from missing mate when they are meant to
        """
        self.cat2.status.leave_group(CatSocial.ROGUE)
        self.cat2.status.change_current_moons_as(4)
        romantic_events._handle_moving_on(self.cat1)

        self.assertNotIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should no longer be a mate of cat1"
        )


class BreakingUp(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = cat_factory.create_cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        self.cat1 = cat_factory.create_cat(moons=100)
        self.cat2 = cat_factory.create_cat(moons=100)

        self.cat1.set_mate(self.cat2)
        romantic_events._rebuild_dicts()

    def test_relation_too_high(self):
        """
        Test that cats don't break up when their relationship is high enough
        """
        self.cat1.relationships[self.cat2.ID] = Relationship(
            cat_from=self.cat1, cat_to=self.cat2, romance=100, like=100
        )

        romantic_events._handle_breakup_events(self.cat1)

        self.assertIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should still be a mate of cat1"
        )

    def test_breakup(self):
        """
        Test that cats will break up when their relationship is below the threshold
        """
        romantic_events._attempt_breakup(self.cat1, self.cat2)
        self.assertNotIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should no longer be a mate of cat1"
        )


class Confessing(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = cat_factory.create_cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        self.cat1 = cat_factory.create_cat(moons=100)
        self.cat2 = cat_factory.create_cat(moons=100)

        romantic_events._rebuild_dicts()

    def test_confession_reject(self):
        """
        Check that cats will be rejected when they are meant to
        """
        self.cat1.relationships[self.cat2.ID] = Relationship(
            cat_from=self.cat1, cat_to=self.cat2, romance=30, like=15, comfort=10
        )
        self.cat2.relationships[self.cat1.ID] = Relationship(
            cat_from=self.cat2, cat_to=self.cat1
        )
        romantic_events._attempt_confession(self.cat1)

        self.assertNotIn(
            self.cat2.ID,
            self.cat1.mate,
            msg="cat2's relationship shouldn't be high enough to accept",
        )

    def test_confession_accept(self):
        """
        Check that cats will accept when they are meant to
        """
        self.cat1.relationships[self.cat2.ID] = Relationship(
            cat_from=self.cat1, cat_to=self.cat2, romance=30, like=15, comfort=10
        )
        self.cat2.relationships[self.cat1.ID] = Relationship(
            cat_from=self.cat2, cat_to=self.cat1, romance=20, like=15, comfort=10
        )

        romantic_events._attempt_confession(self.cat1)

        self.assertIn(
            self.cat2.ID,
            self.cat1.mate,
            msg="cat2's relationship should be high enough to accept",
        )


class MutualLove(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = cat_factory.create_cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        self.cat1 = cat_factory.create_cat(moons=100)
        self.cat2 = cat_factory.create_cat(moons=100)

        romantic_events._rebuild_dicts()

    def test_no_mutual_interest(self):
        """
        Check that cats will not mate this way without mutual interest
        """
        self.cat1.relationships[self.cat2.ID] = Relationship(
            cat_from=self.cat1, cat_to=self.cat2
        )
        self.cat2.relationships[self.cat1.ID] = Relationship(
            cat_from=self.cat2, cat_to=self.cat1
        )

        romantic_events._attempt_mutual_interest_mates(self.cat1, self.cat2)

        self.assertNotIn(
            self.cat2.ID, self.cat1.mate, msg="Neither cat should qualify to mate"
        )

    def test_one_sided_interest(self):
        """
        Check that cats will not mate this way without mutual interest
        """
        self.cat1.relationships[self.cat2.ID] = Relationship(
            cat_from=self.cat1, cat_to=self.cat2, romance=20, like=30, comfort=20
        )
        self.cat2.relationships[self.cat1.ID] = Relationship(
            cat_from=self.cat2, cat_to=self.cat1
        )

        romantic_events._attempt_mutual_interest_mates(self.cat1, self.cat2)

        self.assertNotIn(
            self.cat2.ID, self.cat1.mate, msg="cat2 should not qualify to mate"
        )

    def test_mutual_interest(self):
        """
        Check that cats will mate with mutual interest
        """
        self.cat1.relationships[self.cat2.ID] = Relationship(
            cat_from=self.cat1, cat_to=self.cat2, romance=20, like=30, comfort=20
        )
        self.cat2.relationships[self.cat1.ID] = Relationship(
            cat_from=self.cat2, cat_to=self.cat1, romance=20, like=30, comfort=20
        )

        romantic_events._attempt_mutual_interest_mates(self.cat1, self.cat2)

        self.assertIn(self.cat2.ID, self.cat1.mate, msg="Cats should have mated")

    def test_friends_to_lovers(self):
        """
        Check that cats will mate with mutual interest
        """
        self.cat1.relationships[self.cat2.ID] = Relationship(
            cat_from=self.cat1, cat_to=self.cat2, romance=0, like=50, comfort=20
        )
        self.cat2.relationships[self.cat1.ID] = Relationship(
            cat_from=self.cat2, cat_to=self.cat1, romance=0, like=50, comfort=20
        )

        romantic_events._attempt_mutual_interest_mates(self.cat1, self.cat2)

        self.assertIn(self.cat2.ID, self.cat1.mate, msg="Cats should have mated")


class TestAgeConstraints(unittest.TestCase):
    def setUp(self):
        game.clan = Clan(save_id="clan")
        game.clan.instructor = cat_factory.create_cat(
            status_dict=StatusDict(rank=CatRank.WARRIOR, group_ID=CatGroup.STARCLAN_ID)
        )
        switch_set_value(Switch.clan_save_id, "clan")

        romantic_events._rebuild_dicts()

    def test_kittens(self):
        cat1 = cat_factory.create_cat(moons=2)
        cat2 = cat_factory.create_cat(moons=2)

        cat1.relationships[cat2.ID] = Relationship(cat_from=cat1, cat_to=cat2)
        cat2.relationships[cat1.ID] = Relationship(cat_from=cat2, cat_to=cat1)

        romantic_events._handle_new_mate_events(cat1)

        self.assertNotIn(cat2.ID, cat1.mate, msg="Neither cat should qualify to mate")

    def test_adolescents(self):
        cat1 = cat_factory.create_cat(moons=8)
        cat2 = cat_factory.create_cat(moons=8)

        cat1.relationships[cat2.ID] = Relationship(cat_from=cat1, cat_to=cat2)
        cat2.relationships[cat1.ID] = Relationship(cat_from=cat2, cat_to=cat1)

        romantic_events._handle_new_mate_events(cat1)

        self.assertNotIn(cat2.ID, cat1.mate, msg="Neither cat should qualify to mate")
