import unittest

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank, CatAge, CatGroup, CatStanding
from scripts.cat.sprites.load_sprites import sprites
from scripts.cat.status import StatusDict
from scripts.clan import OtherClan, Clan
from scripts.events_module.parameter_dicts import InvolvedCatDict, StandingDict
from scripts.events_module.patrol.create_new_cat import updated_create_new_cat
from scripts.game_structure import game


class TestNewCatCreation(unittest.TestCase):
    # This is just for testing the `updated_new_cat_creation` func
    @classmethod
    def setUpClass(cls):
        # load in the spritesheets
        # we have to do this to prevent a crash, even though we won't be displaying anything
        sprites.load_all()

        game.clan = Clan(save_id="test")
        game.clan.biome = "Forest"
        game.clan.override_biome = False
        game.clan.camp_bg = "camp1"
        game.clan.starting_season = "Newleaf"
        game.clan.game_mode = "classic"
        cls.other_clan = OtherClan()

    def test_status_assignment(self):
        # test various rank assignments
        rank_list = [*CatRank]
        for i, rank in enumerate(rank_list):
            with self.subTest("Testing rank assignments"):
                option_dict = InvolvedCatDict(
                    can_create_new_cat={},
                    status=[rank],
                    past_status=[rank_list[i - 1]] if rank != CatRank.NEWBORN else [],
                )

                cat_list = updated_create_new_cat(
                    option_dict, involved_cats={}, other_clan=self.other_clan
                )
                test_cat = cat_list[0]

                self.assertEqual(
                    test_cat.status.rank,
                    rank,
                    msg=f"{rank} was not assigned correctly as the current rank.",
                )
                if rank != CatRank.NEWBORN:
                    self.assertEqual(
                        list(test_cat.status.all_ranks.keys())[0],
                        rank_list[i - 1],
                        msg=f"{rank_list[i - 1]} was not assigned correctly as a past rank.",
                    )

        # test that group IDs are being given correctly
        group_list = [
            CatGroup.PLAYER_CLAN,
            CatGroup.OTHER_CLAN,
            "no_group",
            "match:m_c",
        ]
        extra_cat = Cat(
            disable_random=True, status_dict=StatusDict(rank=CatRank.WARRIOR)
        )
        for group in group_list:
            with self.subTest("Testing group assignments"):
                option_dict = InvolvedCatDict(
                    can_create_new_cat={},
                    group=[group] if group else None,
                )
                cat_list = updated_create_new_cat(
                    option_dict,
                    involved_cats={
                        "m_c": extra_cat,
                    },
                    other_clan=self.other_clan,
                )

                test_cat = cat_list[0]

                if group == "no_group":
                    self.assertEqual(
                        CatGroup.NONE,
                        test_cat.status.group,
                        msg=f"{group} was not assigned correctly as the current group.",
                    )
                elif group == "match:m_c":
                    self.assertEqual(
                        extra_cat.status.group,
                        test_cat.status.group,
                        msg=f"{group} was not assigned correctly as the current group.",
                    )
                else:
                    self.assertEqual(
                        group,
                        game.used_group_IDs[test_cat.status.group_ID],
                        msg=f"{group} was not assigned correctly as the current group.",
                    )

        # test that past and current standings are applied
        standing_list = [CatStanding.LOST, CatStanding.EXILED, CatStanding.LEFT]
        for standing in standing_list:
            with self.subTest("Testing current standing assignments"):
                option_dict = InvolvedCatDict(
                    can_create_new_cat={},
                    standing=StandingDict(
                        group=[CatGroup.PLAYER_CLAN], currently=[standing]
                    ),
                )

                cat_list = updated_create_new_cat(
                    option_dict,
                    involved_cats={},
                    other_clan=self.other_clan,
                )

                test_cat: Cat = cat_list[0]

                self.assertIn(
                    standing,
                    test_cat.status.get_standing_with_group(CatGroup.PLAYER_CLAN_ID),
                    msg=f"{standing} was not assigned as the current standing with PlayerClan",
                )

            with self.subTest("Testing past standing assignments"):
                option_dict = InvolvedCatDict(
                    can_create_new_cat={},
                    standing=StandingDict(
                        group=[CatGroup.PLAYER_CLAN], past=[standing]
                    ),
                )

                cat_list = updated_create_new_cat(
                    option_dict,
                    involved_cats={},
                    other_clan=self.other_clan,
                )

                test_cat: Cat = cat_list[0]

                self.assertIn(
                    standing,
                    test_cat.status.get_standing_with_group(CatGroup.PLAYER_CLAN_ID),
                    msg=f"{standing} was not assigned as the current standing with PlayerClan",
                )
                self.assertEqual(
                    test_cat.status.get_standing_with_group(CatGroup.PLAYER_CLAN_ID)[
                        -1
                    ],
                    CatStanding.KNOWN,
                    msg=f"{standing} was assigned and was meant to be a past standing, but is the current standing instead.",
                )

        # test what happens if no constraints are given
        with self.subTest(
            "Testing that a 'blank' constraint dictionary will create a random non-playerClan cat."
        ):
            option_dict = InvolvedCatDict(can_create_new_cat={})

            cat_list = updated_create_new_cat(
                option_dict,
                involved_cats={},
                other_clan=self.other_clan,
            )

            test_cat: Cat = cat_list[0]

            self.assertNotEqual(
                test_cat.status.group,
                CatGroup.PLAYER_CLAN,
                msg=f"Fully random new cat was generated as a player_clan cat instead of a no_group or other_clan cat.",
            )

    def test_age_assignment(self):
        # test that age is being assigned
        age_list = [*CatAge]
        for age in age_list:
            with self.subTest("Testing age assignments"):
                option_dict = InvolvedCatDict(
                    can_create_new_cat={},
                    age=[age],
                )

                cat_list = updated_create_new_cat(
                    option_dict, involved_cats={}, other_clan=self.other_clan
                )
                test_cat = cat_list[0]

                self.assertEqual(
                    test_cat.age,
                    age,
                    msg=f"{age} was not assigned correctly as the current age.",
                )

    def test_litter_creation(self):
        # test that multiple cats are made for a litter

        # test that they are all counted as littermates

        # test that they have established relationships

        pass

    def test_gender_assignment(self):
        # test male works

        # test female works

        # test that can_birth works with the toggle

        pass

    def test_mate_assignment(self):
        # test that a single mate can be assigned

        # test that multiple can be assigned

        # test that they have established relationships

        pass

    def test_stat_assignment(self):
        # test that a trait can be chosen

        # test that a skill can be chosen

        # test that both can be chosen

        # test that when both are given but both are not required, that only one is chosen

        pass

    def test_health_assignment(self):
        # test that injury is applied

        # test that illness is applied

        # test that perm condition is applied and can be congenital/not congenital

        # test scar application for missing limbs

        pass

    def test_backstory_assignment(self):
        # test that a category can be used for assignment

        # test that normal names can be used

        # test that various socials get appropriate backstories when no specific backstory was applied

        pass

    def test_name_assignment(self):
        # test that non-clan cats only get a prefix

        # test that clan cats get a full clan name

        pass
