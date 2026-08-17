import os
import unittest

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank, CatGroup
from scripts.cat.factories.test_cat_factory import TestCatFactory
from scripts.cat.factories.typed_dicts import StatusDict
from scripts.cat.skills import SkillPath
from scripts.cat.sprites.load_sprites import sprites
from scripts.clan import Clan, OtherClan
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    JoinDict,
    DeathDict,
    LostDict,
    ConditionDict,
    ReputationChangesDict,
    SupplyDict,
)
from scripts.events_module.patrol.patrol import Patrol
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event import handle_consequences
from scripts.game_structure import game
from scripts.game_structure.game import Switch
from scripts.game_structure.game.switches import switch_set_value

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


class TestPatrolCats(unittest.TestCase):
    def setUp(self):
        game.clan = Clan("test")
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        game.clan.game_mode = "classic"

        self.patrol_class = Patrol()

    def test_all_cats(self):
        patrol_cats = [
            TestCatFactory.create_cat(rank=CatRank.WARRIOR),
            TestCatFactory.create_cat(rank=CatRank.WARRIOR),
        ]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertEqual(patrol_cats, self.patrol_class.involved_cats["patrol_cats"])

    def test_rank(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        war2 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        app = TestCatFactory.create_cat(rank=CatRank.APPRENTICE)
        patrol_cats = [war1, war2, app]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertCountEqual([war2, war1], self.patrol_class.involved_cats["warrior"])

    def test_normal_adult(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        war2 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        app = TestCatFactory.create_cat(rank=CatRank.APPRENTICE, moons=13)
        patrol_cats = [war1, war2, app]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertCountEqual(
            [war2, war1], self.patrol_class.involved_cats["normal adult"]
        )

    def test_all_apprentices(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        war2 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        app = TestCatFactory.create_cat(rank=CatRank.APPRENTICE)
        patrol_cats = [war1, war2, app]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertCountEqual([app], self.patrol_class.involved_cats["all apprentices"])

    def test_healer_cats(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        med_app = TestCatFactory.create_cat(rank=CatRank.MEDICINE_APPRENTICE)
        med = TestCatFactory.create_cat(rank=CatRank.MEDICINE_CAT)
        patrol_cats = [war1, med_app, med]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertCountEqual(
            [med, med_app], self.patrol_class.involved_cats["healer cats"]
        )


class TestInvolvedCats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # load in the spritesheets
        # we have to do this to prevent a crash, even though we won't be displaying anything
        sprites.load_all()

    def setUp(self):
        Cat.all_cats.clear()
        Cat.all_cats_list.clear()

        game.clan = Clan("test")
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        game.clan.game_mode = "classic"

        self.patrol_class = Patrol()
        self.patrol_class.other_clan = OtherClan()

    def test_overall_pl_rc_difference(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR, moons=20, experience=50)
        app1 = TestCatFactory.create_cat(
            rank=CatRank.APPRENTICE, moons=10, experience=1
        )
        app2 = TestCatFactory.create_cat(
            rank=CatRank.APPRENTICE, moons=10, experience=1
        )

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "p_l": InvolvedCatDict(),
                "r_c": InvolvedCatDict(),
            },
            success_outcomes=[{"strings": ["test"]}],
            fail_outcomes=[{"strings": ["test"]}],
        )

        self.patrol_class._add_patrol_cats([war1, app1, app2])
        self.patrol_class._patrol_pass_cat_constraints(patrol)

        self.assertEqual(
            war1,
            self.patrol_class.involved_cats["p_l"],
            msg=f"{war1} should be the patrol leader.",
        )

        self.assertNotEqual(
            war1,
            self.patrol_class.involved_cats["r_c"],
            msg=f"r_c should not be the same as {war1}",
        )

    def test_new_cat_found(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        outsider1 = TestCatFactory.create_cat(rank=CatRank.LONER)

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "n_c:0": InvolvedCatDict(),
                "n_c:1": InvolvedCatDict(can_create_new_cat={}),
            },
            success_outcomes=[{"strings": ["test"]}],
            fail_outcomes=[{"strings": ["test"]}],
        )

        self.patrol_class._add_patrol_cats([war1])
        self.patrol_class._patrol_pass_cat_constraints(patrol)

        self.assertEqual(
            outsider1,
            self.patrol_class.involved_cats["n_c:0"],
            msg=f"{outsider1} should be n_c:0",
        )

        self.assertNotEqual(
            outsider1,
            self.patrol_class.involved_cats["n_c:1"],
            msg=f"n_c:1 should not be {outsider1}",
        )

    def test_pl_persistence(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR, moons=20, experience=50)
        app1 = TestCatFactory.create_cat(
            rank=CatRank.APPRENTICE, moons=10, experience=1
        )
        app2 = TestCatFactory.create_cat(
            rank=CatRank.APPRENTICE, moons=10, experience=1
        )

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "p_l": InvolvedCatDict(),
                "r_c": InvolvedCatDict(),
            },
            success_outcomes=[
                {"involved_cats": {"p_l": InvolvedCatDict(status=["warrior"])}}
            ],
            fail_outcomes=[{"strings": ["test"]}],
        )
        self.patrol_class.patrol_event = patrol
        self.patrol_class._add_patrol_cats([war1, app1, app2])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )

        self.assertEqual(
            self.patrol_class.involved_cats["p_l"],
            self.patrol_class.outcome_cats["success"]["p_l"],
            msg=f"Overall p_l and outcome p_l should match.",
        )

    def test_sc_share_abbr(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        app1 = TestCatFactory.create_cat(rank=CatRank.APPRENTICE)
        app2 = TestCatFactory.create_cat(rank=CatRank.APPRENTICE)

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "p_l": InvolvedCatDict(),
                "r_c": InvolvedCatDict(),
            },
            success_outcomes=[
                {"involved_cats": {"s_c": InvolvedCatDict(prior_abbreviation=["p_l"])}}
            ],
            fail_outcomes=[{"strings": ["test"]}],
        )
        self.patrol_class.patrol_event = patrol
        self.patrol_class._add_patrol_cats([war1, app1, app2])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )

        self.assertEqual(
            self.patrol_class.involved_cats["p_l"],
            self.patrol_class.outcome_cats["success"]["s_c"],
            msg=f"p_l and outcome s_c should match.",
        )

    def test_sc_not_cat(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        app1 = TestCatFactory.create_cat(rank=CatRank.APPRENTICE)
        app2 = TestCatFactory.create_cat(rank=CatRank.APPRENTICE)

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "p_l": InvolvedCatDict(),
                "r_c": InvolvedCatDict(),
            },
            success_outcomes=[
                {"involved_cats": {"s_c": InvolvedCatDict(prior_abbreviation=["-p_l"])}}
            ],
            fail_outcomes=[{"strings": ["test"]}],
        )
        self.patrol_class.patrol_event = patrol
        self.patrol_class._add_patrol_cats([war1, app1, app2])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )

        self.assertNotEqual(
            self.patrol_class.involved_cats["p_l"],
            self.patrol_class.outcome_cats["success"]["s_c"],
            msg=f"p_l and outcome s_c can't match.",
        )


class TestOutcomeExecution(unittest.TestCase):
    def setUp(self):
        # load in the spritesheets
        # we have to do this to prevent a crash, even though we won't be displaying anything
        sprites.load_all()
        Cat.all_cats.clear()
        Cat.all_cats_list.clear()

        game.clan = Clan("test", game_mode="expanded")
        game.clan.instructor = TestCatFactory.create_cat(
            status_dict=StatusDict(group_ID=CatGroup.STARCLAN_ID, rank=CatRank.WARRIOR)
        )
        game.clan.instructor.dead = True
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        switch_set_value(Switch.clan_save_id, "test")
        self.patrol_class = Patrol()

    def test_joining_clan(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        outsider1 = TestCatFactory.create_cat(rank=CatRank.LONER)

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "n_c:0": InvolvedCatDict(),
            },
            success_outcomes=[{"strings": [""], "join": [JoinDict(cats=["n_c:0"])]}],
            fail_outcomes=[{"strings": ["test"]}],
        )

        self.patrol_class._add_patrol_cats([war1])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )
        handle_consequences.execute_outcome(
            patrol.success_outcomes[0],
            self.patrol_class.involved_cats,
            other_clan=OtherClan(),
        )

        self.assertTrue(
            outsider1.status.alive_in_player_clan,
            msg=f"{outsider1} should be part of the player_clan, instead {outsider1} is rank: {outsider1.status.rank} with group: {outsider1.status.group}. The patrol's n_c:0 is {self.patrol_class.involved_cats['n_c:0']}",
        )

    def test_dying(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR, moons=20, experience=50)
        app1 = TestCatFactory.create_cat(
            rank=CatRank.APPRENTICE, moons=10, experience=1
        )

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={},
            success_outcomes=[
                {
                    "strings": [""],
                    "death": [DeathDict(cats=["p_l"], body=True, history="test")],
                }
            ],
            fail_outcomes=[{"strings": ["test"]}],
        )

        self.patrol_class._add_patrol_cats([war1, app1])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )
        handle_consequences.execute_outcome(
            patrol.success_outcomes[0],
            self.patrol_class.involved_cats,
            other_clan=OtherClan(),
        )

        self.assertTrue(
            war1.dead,
            msg=f"{war1} should be dead.",
        )
        self.assertEqual(
            war1.history.died_by[0]["text"],
            "test",
            msg=f"{war1.history.died_by[0]['text']} should be 'test'.",
        )

    def test_lost(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR, moons=20, experience=50)
        app1 = TestCatFactory.create_cat(
            rank=CatRank.APPRENTICE, moons=10, experience=1
        )

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={},
            success_outcomes=[
                {
                    "strings": [""],
                    "lost": [LostDict(cats=["p_l"])],
                }
            ],
            fail_outcomes=[{"strings": ["test"]}],
        )

        self.patrol_class._add_patrol_cats([war1, app1])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )
        handle_consequences.execute_outcome(
            patrol.success_outcomes[0],
            self.patrol_class.involved_cats,
            other_clan=OtherClan(),
        )

        self.assertTrue(
            war1.status.is_lost(CatGroup.PLAYER_CLAN_ID),
            msg=f"{war1} should be lost.",
        )

    def test_condition(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        app1 = TestCatFactory.create_cat(rank=CatRank.APPRENTICE)

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={"p_l": InvolvedCatDict(), "r_c": InvolvedCatDict()},
            success_outcomes=[
                {
                    "strings": [""],
                    "condition": [
                        ConditionDict(cats=["p_l", "r_c"], condition=["sore"])
                    ],
                }
            ],
            fail_outcomes=[{"strings": ["test"]}],
        )

        self.patrol_class._add_patrol_cats([war1, app1])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )
        handle_consequences.execute_outcome(
            patrol.success_outcomes[0],
            self.patrol_class.involved_cats,
            other_clan=OtherClan(),
        )

        self.assertTrue(
            "sore" in war1.injuries and "sore" in app1.injuries,
            msg=f"{war1} and {app1} should be sore.",
        )

    def test_rep_change(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        app1 = TestCatFactory.create_cat(rank=CatRank.APPRENTICE)

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={"p_l": InvolvedCatDict(), "r_c": InvolvedCatDict()},
            success_outcomes=[
                {
                    "strings": [""],
                    "reputation_changes": ReputationChangesDict(
                        other_clan=2, outsider=2
                    ),
                }
            ],
            fail_outcomes=[{"strings": ["test"]}],
        )
        other_clan = OtherClan()
        starting_clan_rep = other_clan.relations
        starting_outsider_rep = game.clan.reputation

        self.patrol_class._add_patrol_cats([war1, app1])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )
        handle_consequences.execute_outcome(
            patrol.success_outcomes[0],
            self.patrol_class.involved_cats,
            other_clan=other_clan,
        )

        self.assertTrue(
            starting_clan_rep + 2 == other_clan.relations
            and starting_outsider_rep + 2 == game.clan.reputation,
            msg=f"Clan and outsider reputation should be increased.",
        )

    def test_supply_change(self):
        war1 = TestCatFactory.create_cat(rank=CatRank.WARRIOR)
        war1.skills.primary.path = SkillPath.CLIMBER
        war1.skills.secondary = None

        patrol = PatrolEvent(
            event_id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={"p_l": InvolvedCatDict()},
            success_outcomes=[
                {
                    "strings": [""],
                    "supply": [
                        SupplyDict(type="freshkill", adjust="increase_tiny"),
                        SupplyDict(type="honey", adjust="increase_tiny"),
                        SupplyDict(type="random_herbs", adjust="increase_huge"),
                    ],
                }
            ],
            fail_outcomes=[{"strings": ["test"]}],
        )
        freshkill_count = game.clan.freshkill_pile.total_amount
        honey_count = game.clan.herb_supply.get_single_herb_total("honey")
        total_herb_count = game.clan.herb_supply.total

        self.patrol_class._add_patrol_cats([war1])
        self.patrol_class._patrol_pass_cat_constraints(patrol)
        self.patrol_class._check_outcome_constraints(
            patrol.success_outcomes[0], "success"
        )
        handle_consequences.disable_random = True
        handle_consequences.execute_outcome(
            patrol.success_outcomes[0],
            self.patrol_class.involved_cats,
            other_clan=OtherClan(),
        )

        # check freshkill change
        self.assertTrue(
            freshkill_count + 2 == game.clan.freshkill_pile.total_amount,
            msg=f"{freshkill_count} + 2 should equal {game.clan.freshkill_pile.total_amount}",
        )
        # check single herb change
        self.assertTrue(
            honey_count + 2 == game.clan.herb_supply.get_single_herb_total("honey"),
            msg=f"{honey_count} + 1 should equal {game.clan.herb_supply.get_single_herb_total('honey')}",
        )
        # check random herb change
        self.assertTrue(
            total_herb_count + 10 == game.clan.herb_supply.total,
            msg=f"{total_herb_count} + 9 should equal {game.clan.herb_supply.total}",
        )
