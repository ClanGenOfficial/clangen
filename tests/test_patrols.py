import os
import unittest

from scripts.cat.cats import create_cat
from scripts.cat.enums import CatRank
from scripts.clan import Clan
from scripts.events_module.patrol.patrol import Patrol
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

        self.assertEqual(patrol_cats, self.patrol_class.involved_cats["patrol_cats"])

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

    # test p_l found
    def test_overall_pl(self):
        war1 = create_cat(rank=CatRank.WARRIOR)
        war2 = create_cat(rank=CatRank.WARRIOR)
        app = create_cat(rank=CatRank.APPRENTICE)

    # test r_c found (and is not p_l)

    # test n_c found

    # test outcome p_l is also overall p_l

    # test s_c can be p_l

    # test s_c CANNOT be a certain cat


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
