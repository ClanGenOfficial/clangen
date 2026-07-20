import os
import unittest

from scripts.cat.cats import create_cat
from scripts.cat.enums import CatRank
from scripts.clan import Clan
from scripts.events_module.parameter_dicts import InvolvedCatDict
from scripts.events_module.patrol.patrol import Patrol
from scripts.events_module.patrol.patrol_event import PatrolEvent
from scripts.events_module.text_pool_event.text_pool_event import TextPoolEvent
from scripts.game_structure import game

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
            create_cat(rank=CatRank.WARRIOR),
            create_cat(rank=CatRank.WARRIOR),
        ]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertEqual(patrol_cats, self.patrol_class.patrol_statuses["patrol_cats"])

    def test_rank(self):
        war1 = create_cat(rank=CatRank.WARRIOR)
        war2 = create_cat(rank=CatRank.WARRIOR)
        app = create_cat(rank=CatRank.APPRENTICE)
        patrol_cats = [war1, war2, app]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertCountEqual(
            [war2, war1], self.patrol_class.patrol_statuses["warrior"]
        )

    def test_normal_adult(self):
        war1 = create_cat(rank=CatRank.WARRIOR)
        war2 = create_cat(rank=CatRank.WARRIOR)
        app = create_cat(rank=CatRank.APPRENTICE, moons=13)
        patrol_cats = [war1, war2, app]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertCountEqual(
            [war2, war1], self.patrol_class.patrol_statuses["normal adult"]
        )

    def test_all_apprentices(self):
        war1 = create_cat(rank=CatRank.WARRIOR)
        war2 = create_cat(rank=CatRank.WARRIOR)
        app = create_cat(rank=CatRank.APPRENTICE)
        patrol_cats = [war1, war2, app]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertCountEqual(
            [app], self.patrol_class.patrol_statuses["all apprentices"]
        )

    def test_healer_cats(self):
        war1 = create_cat(rank=CatRank.WARRIOR)
        med_app = create_cat(rank=CatRank.MEDICINE_APPRENTICE)
        med = create_cat(rank=CatRank.MEDICINE_CAT)
        patrol_cats = [war1, med_app, med]
        self.patrol_class._add_patrol_cats(patrol_cats)

        self.assertCountEqual(
            [med, med_app], self.patrol_class.patrol_statuses["healer cats"]
        )


class TestInvolvedCats(unittest.TestCase):
    def setUp(self):
        game.clan = Clan("test")
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        game.clan.game_mode = "classic"

        self.patrol_class = Patrol()

    def test_overall_pl_rc_difference(self):
        war1 = create_cat(rank=CatRank.WARRIOR)
        app1 = create_cat(rank=CatRank.APPRENTICE)
        app2 = create_cat(rank=CatRank.APPRENTICE)

        patrol = PatrolEvent(
            id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "p_l": InvolvedCatDict(),
                "r_c": InvolvedCatDict(),
            },
            success_outcomes=[TextPoolEvent()],
            fail_outcomes=[TextPoolEvent()],
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
        war1 = create_cat(rank=CatRank.WARRIOR)
        outsider1 = create_cat(rank=CatRank.LONER)

        patrol = PatrolEvent(
            id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "n_c:0": InvolvedCatDict(),
                "n_c:1": InvolvedCatDict(can_create_new_cat={}),
            },
            success_outcomes=[TextPoolEvent()],
            fail_outcomes=[TextPoolEvent()],
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
        war1 = create_cat(rank=CatRank.WARRIOR)
        app1 = create_cat(rank=CatRank.APPRENTICE)
        app2 = create_cat(rank=CatRank.APPRENTICE)

        patrol = PatrolEvent(
            id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "p_l": InvolvedCatDict(),
                "r_c": InvolvedCatDict(),
            },
            success_outcomes=[
                TextPoolEvent(
                    involved_cats={"p_l": InvolvedCatDict(status=["warrior"])}
                )
            ],
            fail_outcomes=[TextPoolEvent()],
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
        war1 = create_cat(rank=CatRank.WARRIOR)
        app1 = create_cat(rank=CatRank.APPRENTICE)
        app2 = create_cat(rank=CatRank.APPRENTICE)

        patrol = PatrolEvent(
            id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "p_l": InvolvedCatDict(),
                "r_c": InvolvedCatDict(),
            },
            success_outcomes=[
                TextPoolEvent(
                    involved_cats={"s_c": InvolvedCatDict(prior_abbreviation=["p_l"])}
                )
            ],
            fail_outcomes=[TextPoolEvent()],
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
        war1 = create_cat(rank=CatRank.WARRIOR)
        app1 = create_cat(rank=CatRank.APPRENTICE)
        app2 = create_cat(rank=CatRank.APPRENTICE)

        patrol = PatrolEvent(
            id="test",
            types=["hunting"],
            intro_text="test",
            decline_text="test",
            involved_cats={
                "p_l": InvolvedCatDict(),
                "r_c": InvolvedCatDict(),
            },
            success_outcomes=[
                TextPoolEvent(
                    involved_cats={"s_c": InvolvedCatDict(prior_abbreviation=["-p_l"])}
                )
            ],
            fail_outcomes=[TextPoolEvent()],
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
        game.clan = Clan("test")
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        game.clan.game_mode = "classic"

        self.patrol_class = Patrol()

    # check joining clan

    # check dying

    # check getting lost

    # check gaining condition

    # check reputation changing

    # check supply changing

    # check exp increasing

    # check mentor app influence applying
