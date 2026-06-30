import unittest
from itertools import combinations

from scripts.cat.cats import Cat
from scripts.cat.enums import CatRank, CatAge, CatGroup, CatStanding
from scripts.cat.sprites.load_sprites import sprites
from scripts.cat.status import StatusDict
from scripts.clan import OtherClan, Clan
from scripts.clan_package.settings import set_clan_setting
from scripts.events_module.parameter_dicts import (
    InvolvedCatDict,
    StandingDict,
    CanCreateNewCatDict,
)
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
        with self.subTest("Testing litter creation"):
            parent = Cat(
                status_dict=StatusDict(rank=CatRank.LONER), disable_random=True
            )
            adoptive = Cat(
                status_dict=StatusDict(rank=CatRank.LONER), disable_random=True
            )

            option_dict = InvolvedCatDict(
                can_create_new_cat=CanCreateNewCatDict(
                    become_litter=True,
                    assign_blood_parent=["m_c"],
                    assign_adoptive_parent=["r_c"],
                ),
            )

            cat_list = updated_create_new_cat(
                option_dict,
                involved_cats={"m_c": parent, "r_c": adoptive},
                other_clan=self.other_clan,
            )

            # test that they baby
            for c in cat_list:
                self.assertIn(
                    c.age,
                    (CatAge.NEWBORN, CatAge.KITTEN),
                    msg=f"Attempted to generate a litter, but only one kitten was created!",
                )

            # test that multiple cats are made for a litter
            self.assertGreater(
                len(cat_list),
                1,
                msg=f"Attempted to generate a litter, but only one kitten was created!",
            )

            for pair in combinations(cat_list, 2):
                # test that they are all counted as littermates
                self.assertTrue(
                    pair[0].is_littermate(pair[1]),
                    msg="Created a litter, but the kits aren't being considered littermates!",
                )

                # test that they have established relationships
                self.assertGreater(
                    pair[0].relationships[pair[1].ID].total_abs_relationship_value,
                    0,
                    msg="Created a litter, but the kits weren't given appropriate relationships towards each other!",
                )

            for c in cat_list:
                # test that parents were correctly assigned
                self.assertTrue(
                    parent.is_parent(c),
                    msg="Created a litter, but the blood parent isn't considered a parent!",
                )
                self.assertTrue(
                    adoptive.is_parent(c),
                    msg="Created a litter, but the adoptive parent isn't considered a parent!",
                )
                # test that they have established relationships
                self.assertGreater(
                    parent.relationships[c.ID].total_abs_relationship_value,
                    0,
                    msg="Created a litter, but the blood parent doesn't have a relationship toward the kits!",
                )
                self.assertGreater(
                    c.relationships[parent.ID].total_abs_relationship_value,
                    0,
                    msg="Created a litter, but the kit doesn't have a relationship toward the blood parent!",
                )
                self.assertGreater(
                    adoptive.relationships[c.ID].total_abs_relationship_value,
                    0,
                    msg="Created a litter, but the adoptive parent doesn't have a relationship toward the kits!",
                )
                self.assertGreater(
                    c.relationships[parent.ID].total_abs_relationship_value,
                    0,
                    msg="Created a litter, but the kit doesn't have a relationship toward the adoptive parent!",
                )

    def test_gender_assignment(self):
        with self.subTest("Testing gender assignments"):
            # test male works
            option_dict = InvolvedCatDict(
                can_create_new_cat={},
                gender="male",
            )

            cat_list = updated_create_new_cat(
                option_dict, involved_cats={}, other_clan=self.other_clan
            )
            test_cat = cat_list[0]

            self.assertEqual(
                test_cat.gender,
                "male",
                msg=f"male was not assigned correctly as the current gender.",
            )
            # test female works
            option_dict = InvolvedCatDict(
                can_create_new_cat={},
                gender="female",
            )

            cat_list = updated_create_new_cat(
                option_dict, involved_cats={}, other_clan=self.other_clan
            )
            test_cat = cat_list[0]

            self.assertEqual(
                test_cat.gender,
                "female",
                msg=f"female was not assigned correctly as the current gender.",
            )
            # test that can_birth works with the toggle
            set_clan_setting("same sex birth", False)
            option_dict = InvolvedCatDict(
                can_create_new_cat={},
                gender="can_birth",
            )

            cat_list = updated_create_new_cat(
                option_dict, involved_cats={}, other_clan=self.other_clan
            )
            test_cat = cat_list[0]

            self.assertEqual(
                test_cat.gender,
                "female",
                msg=f"female was not assigned correctly as the current gender when birthing cat is requested and same sex birth toggle is off.",
            )

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
